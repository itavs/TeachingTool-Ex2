"""Version-bound experimental local processing; fake providers are test injection only."""
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .homework_contract import PROCESS_SECONDS
from .attendance import CourseAccessError
from .models import ReviewJob, FeedbackDraft, Membership
from .homework_review import check_requester
from .homework_provider import get_homework_reviewer


def validate_individual(data, job):
    if not isinstance(data, dict) or set(data) != {'findings'}:
        raise ValueError('Invalid individual output')
    rows = data['findings']
    if not isinstance(rows,list) or len(rows) != len(job.criteria_snapshot):
        raise ValueError('Wrong criterion count')
    seen, text = set(), []
    for row in rows:
        required={'criterion_index','what_student_wrote','quotes','status','reasoning','suggested_correction'}
        if not isinstance(row,dict) or set(row) != required:
            raise ValueError('Invalid criterion fields')
        i=row['criterion_index']
        if type(i) is not int or i in seen or not 0 <= i < len(job.criteria_snapshot):
            raise ValueError('Invalid criterion reference')
        seen.add(i)
        if row['status'] not in ['correct','partial','missing','incorrect']:
            raise ValueError('Invalid status')
        if any(not isinstance(row[k],str) for k in ['what_student_wrote','reasoning','suggested_correction']) or not row['reasoning'].strip():
            raise ValueError('Invalid explanation')
        if not isinstance(row['quotes'],list) or len(row['quotes'])>2 or any(not isinstance(q,str) or not q for q in row['quotes']):
            raise ValueError('Invalid quote structure')
        text.append((i, '\n'.join([job.criteria_snapshot[i], row['status'].capitalize(), row['what_student_wrote'],
                     row['reasoning'], row['suggested_correction']]).strip()))
    return '\n\n'.join(t for _,t in sorted(text))


def validate_comparison(data, job):
    if not isinstance(data,dict) or set(data) != {'outcome','text','evidence'}:
        raise ValueError('Invalid comparison')
    if data['outcome'] not in ['compared','no_difference'] or not isinstance(data['text'],str) or not data['text'].strip():
        raise ValueError('Invalid comparison outcome')
    if not isinstance(data['evidence'],list) or not data['evidence']:
        raise ValueError('No comparison evidence')
    sources=set()
    for item in data['evidence']:
        if not isinstance(item,dict) or set(item) != {'source','peer_index','quote'}:
            raise ValueError('Invalid evidence')
        if item['source']=='target':
            source=job.target_text
        elif item['source']=='peer' and type(item['peer_index']) is int and 0<=item['peer_index']<len(job.peer_snapshots):
            source=job.peer_snapshots[item['peer_index']]['text']
        else:
            raise ValueError('Wrong comparison source')
        if not isinstance(item['quote'],str) or not item['quote']:
            raise ValueError('Invalid comparison quote structure')
        sources.add(item['source'])
    if sources != {'target','peer'}:
        raise ValueError('Evidence must reference target and peers')
    return data['outcome'], data['text']


def access_valid(job):
    if not job.requester.is_active or not job.submission.student.is_active:
        raise CourseAccessError(403)
    check_requester(job.submission,job.requester)
    if not Membership.objects.filter(user_id=job.submission.student_id,course_id=job.submission.assignment.meeting.course_id,role='student').exists():
        raise CourseAccessError(403)
    if job.batch_id:
        for source in job.batch.sources_snapshot:
            if not Membership.objects.filter(user_id=source['student_id'], user__is_active=True,
                    course_id=job.submission.assignment.meeting.course_id, role='student').exists():
                raise CourseAccessError(403)


def process_review_job(job_id, *, reviewer=None):
    if ReviewJob.objects.filter(pk=job_id, batch__isnull=False).exists():
        return process_batch_job(job_id, reviewer=reviewer)
    return _process_review_job(job_id, reviewer=reviewer)


def process_batch_job(job_id, *, reviewer=None):
    from .homework_batches import expire_batch_jobs
    from .process_lock import WorkerBusy
    job = ReviewJob.objects.select_related('batch','submission__assignment__meeting','submission__student','requester').get(pk=job_id)
    expire_batch_jobs(batch_id=job.batch_id)
    job.refresh_from_db()
    if job.status != 'queued':
        return
    try:
        access_valid(job)
        provider = reviewer if reviewer is not None else get_homework_reviewer()
        if not provider.available(job.language) or not hasattr(provider, 'reserve_resource'):
            ReviewJob.objects.filter(pk=job_id, status='queued').update(status='failed', error_code='provider_unavailable',
                waiting_for_resource=False, finished_at=timezone.now())
            return
        # No model server/inference or DB writer lock is held while waiting.
        with provider.reserve_resource():
            return _process_review_job(job_id, reviewer=provider)
    except WorkerBusy:
        expire_batch_jobs(batch_id=job.batch_id)
        ReviewJob.objects.filter(pk=job_id, status='queued').update(waiting_for_resource=True)
        return 'waiting'
    except Exception as error:
        ReviewJob.objects.filter(pk=job_id, status='queued').update(status='failed',
            error_code='access_changed' if isinstance(error, CourseAccessError) else 'provider_unavailable',
            waiting_for_resource=False, finished_at=timezone.now())


def _process_review_job(job_id, *, reviewer=None):
    with transaction.atomic():
        job=ReviewJob.objects.select_for_update().select_related('batch','submission__assignment__meeting','submission__student','requester').get(pk=job_id)
        if job.status != 'queued':
            return
        if job.batch_id and timezone.now() >= job.batch.queue_expires_at:
            job.status='failed';job.error_code='queue_timeout';job.finished_at=timezone.now()
            job.waiting_for_resource=False
            job.save(update_fields=['status','error_code','finished_at','waiting_for_resource'])
            return
        job.status='running';job.started_at=timezone.now();job.waiting_for_resource=False
        job.save(update_fields=['status','started_at','waiting_for_resource'])
    stage='individual_failed'
    try:
        access_valid(job)
        provider=reviewer if reviewer is not None else get_homework_reviewer()
        if not provider.available(job.language):
            stage='provider_unavailable'
            raise ValueError('Provider unavailable')
        if hasattr(provider,'configure'): provider.configure(job)
        # Owned isolated runners acquire the shared GPU lock; no inference transaction.
        individual=provider.assess_submission(job.instructions_snapshot,job.criteria_snapshot,job.target_text,job.language)
        # Retain private output for diagnosis even if structural validation fails.
        ReviewJob.objects.filter(pk=job_id).update(generated_individual=individual,
            model_metadata=getattr(provider,'metadata',{}))
        individual_text=validate_individual(individual,job)
        comparison,comparison_text={},''
        comparison_original={}
        comparison_state='no_peers'
        if job.peer_snapshots:
            try:
                comparison=provider.compare_submissions(job.instructions_snapshot,job.criteria_snapshot,job.target_text,
                                                      [p['text'] for p in job.peer_snapshots],job.language)
                comparison_original=comparison
                comparison_state,comparison_text=validate_comparison(comparison,job)
                from .homework_evidence import privacy_error
                if privacy_error(job,comparison_text): raise ValueError('Unsafe public comparison')
            except Exception:
                comparison_state='failed';comparison={};comparison_text=''
        with transaction.atomic():
            # Refresh access before persisting any draft after processing.
            job=ReviewJob.objects.select_for_update().select_related('submission__assignment__meeting','submission__student','requester').get(pk=job_id)
            if job.batch_id and (job.status != 'running' or timezone.now() >= job.started_at + timedelta(seconds=PROCESS_SECONDS)):
                raise ValueError('Group processing deadline expired before saving a draft')
            access_valid(job)
            from .homework_evidence import collect_evidence
            FeedbackDraft.objects.create(job=job,individual_text=individual_text,comparison_text=comparison_text,
                evidence=collect_evidence(individual,comparison))
            job.generated_individual=individual;job.generated_comparison=comparison_original
            job.comparison_status=comparison_state
            job.model_metadata=getattr(provider,'metadata',{})
            job.error_code='comparison_failed' if comparison_state=='failed' else ''
            job.status='ready';job.finished_at=timezone.now();job.save()
    except Exception as error:
        metadata = dict(getattr(locals().get('provider'),'metadata',{}))
        metadata['failure_type'] = type(error).__name__
        if isinstance(error,ValueError): metadata['validation_error'] = str(error)[:100]
        target = ReviewJob.objects.filter(pk=job_id)
        if job.batch_id:
            target = target.filter(status='running')
            if timezone.now() >= job.started_at + timedelta(seconds=PROCESS_SECONDS):
                stage = 'processing_timeout'
            elif isinstance(error, CourseAccessError):
                stage = 'access_changed'
        target.update(status='failed',error_code=stage,model_metadata=metadata,finished_at=timezone.now())
