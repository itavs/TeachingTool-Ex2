"""Review task processor; production provider remains disabled, fakes are test injection only."""
from pathlib import Path
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .attendance import CourseAccessError
from .models import ReviewJob, FeedbackDraft, Membership
from .homework_review import check_requester
from .homework_provider import get_homework_reviewer
from .process_lock import exclusive_lock


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
        if not isinstance(row['quotes'],list) or any(not isinstance(q,str) or not q or q not in job.target_text for q in row['quotes']):
            raise ValueError('Unsupported quote')
        text.append((i, '\n'.join([job.criteria_snapshot[i], row['status'].capitalize(), row['what_student_wrote'],
                     *['"'+q+'"' for q in row['quotes']], row['reasoning'], row['suggested_correction']]).strip()))
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
        if not isinstance(item['quote'],str) or not item['quote'] or item['quote'] not in source:
            raise ValueError('Unsupported comparison quote')
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


def process_review_job(job_id, *, reviewer=None):
    with transaction.atomic():
        job=ReviewJob.objects.select_for_update().select_related('submission__assignment__meeting','submission__student','requester').get(pk=job_id)
        if job.status != 'queued':
            return
        job.status='running';job.save(update_fields=['status'])
    stage='individual_failed'
    try:
        access_valid(job)
        provider=reviewer if reviewer is not None else get_homework_reviewer()
        if not provider.available(job.language):
            stage='provider_unavailable'
            raise ValueError('Provider unavailable')
        # No inference under a database transaction; no real provider is enabled.
        with exclusive_lock(Path(settings.VIDEO_STORAGE_ROOT)/'.decoder.lock'):
            individual=provider.assess_submission(job.instructions_snapshot,job.criteria_snapshot,job.target_text,job.language)
            individual_text=validate_individual(individual,job)
            comparison,comparison_text={},''
            comparison_state='no_peers'
            if job.peer_snapshots:
                try:
                    comparison=provider.compare_submissions(job.instructions_snapshot,job.criteria_snapshot,job.target_text,
                                                          [p['text'] for p in job.peer_snapshots],job.language)
                    comparison_state,comparison_text=validate_comparison(comparison,job)
                except Exception:
                    comparison_state='failed';comparison={};comparison_text=''
            with transaction.atomic():
                # Refresh access before persisting any draft after processing.
                job=ReviewJob.objects.select_for_update().select_related('submission__assignment__meeting','submission__student','requester').get(pk=job_id)
                access_valid(job)
                FeedbackDraft.objects.create(job=job,individual_text=individual_text,comparison_text=comparison_text)
                job.generated_individual=individual;job.generated_comparison=comparison
                job.comparison_status=comparison_state
                job.model_metadata=getattr(provider,'metadata',{})
                job.error_code='comparison_failed' if comparison_state=='failed' else ''
                job.status='ready';job.finished_at=timezone.now();job.save()
    except Exception:
        ReviewJob.objects.filter(pk=job_id).update(status='failed',error_code=stage,finished_at=timezone.now())
