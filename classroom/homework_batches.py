"""Lecturer-confirmed small groups; no inference in request/preview handlers."""
from datetime import timedelta
import hashlib
import json
import uuid

from django.core import signing
from django.db import IntegrityError, transaction
from django.utils import timezone

from .attendance import CourseAccessError, lock_and_authorize, authorize
from .homework_contract import capacity_error, PROCESS_SECONDS
from .homework_review import availability
from .models import HomeworkAssignment, Membership, ReviewBatch, ReviewJob, SubmissionVersion

PREVIEW_SECONDS = 600
QUEUE_SECONDS = 900
SALT = 'homework-demo-group-v1'
SCOPE_NOTICE = 'This feedback compares your submission with a selected demonstration group, not the whole class.'


class BatchError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


class SourcesChanged(BatchError):
    def __init__(self, fields, owner_ids):
        self.owner_ids = owner_ids
        super().__init__('Changed since preview: ' + ', '.join(fields) + '. Review a new preview and confirm again.', 409)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


def latest_sources(assignment):
    eligible = Membership.objects.filter(course_id=assignment.meeting.course_id, role='student', user__is_active=True).values('user_id')
    versions = assignment.submissions.filter(student_id__in=eligible).select_related('student').order_by('student_id', '-version_number')
    result = {}
    for version in versions:
        if version.student_id not in result:
            result[version.student_id] = version
    return result


def _snapshot(meeting, assignment_id, user, owner_ids):
    authorize(meeting.pk, user, Membership.Role.LECTURER)
    try:
        owners = [int(value) for value in owner_ids]
    except (ValueError, TypeError):
        raise BatchError('Choose 2–4 different students with submitted work.') from None
    if not 2 <= len(owners) <= 4 or len(set(owners)) != len(owners):
        raise BatchError('Choose 2–4 different students with submitted work.')
    assignment = HomeworkAssignment.objects.select_related('meeting').filter(pk=assignment_id, meeting=meeting).first()
    if assignment is None:
        raise CourseAccessError(404)
    latest = latest_sources(assignment)
    if any(owner not in latest for owner in owners):
        raise BatchError('A selected student or submission is no longer available. Review the selection.', 409)
    sources = [{'id':latest[owner].pk, 'student_id':owner, 'version':latest[owner].version_number,
                'text':latest[owner].text, 'username':latest[owner].student.username} for owner in sorted(owners)]
    return assignment, {'sources':sources, 'instructions':assignment.instructions, 'criteria':assignment.criteria,
                        'rubric':assignment.professional_rubric, 'language':assignment.feedback_language}


def _validate(assignment, snapshot):
    enabled, reason = availability(assignment)
    if not enabled:
        raise BatchError(reason, 409)
    sources = snapshot['sources']
    for source in sources:
        error = capacity_error(snapshot['instructions'], snapshot['criteria'], snapshot['rubric'], source['text'],
                               [peer['text'] for peer in sources if peer['student_id'] != source['student_id']])
        if error:
            raise BatchError(error + ' No group or requests were created.')


def prepare_preview(meeting, assignment_id, user, owner_ids):
    assignment, snapshot = _snapshot(meeting, assignment_id, user, owner_ids)
    _validate(assignment, snapshot)
    # The signed client token contains hashes/IDs, never the private source texts.
    claims = {'assignment':assignment.pk, 'requester':user.pk,
              'owners':[s['student_id'] for s in snapshot['sources']], 'key':str(uuid.uuid4()),
              'digest':digest(snapshot), 'parts':{key:digest(value) for key,value in snapshot.items()}}
    return snapshot, signing.dumps(claims, salt=SALT, compress=True)


def expire_batch_jobs(*, submission_ids=None, batch_id=None):
    jobs = ReviewJob.objects.filter(batch__isnull=False)
    if submission_ids is not None:
        jobs = jobs.filter(submission_id__in=submission_ids)
    if batch_id is not None:
        jobs = jobs.filter(batch_id=batch_id)
    now = timezone.now()
    queued = jobs.filter(status='queued', batch__queue_expires_at__lte=now).update(
        status='failed', error_code='queue_timeout', waiting_for_resource=False, finished_at=now)
    running = jobs.filter(status='running', started_at__lte=now-timedelta(seconds=PROCESS_SECONDS)).update(
        status='failed', error_code='processing_timeout', waiting_for_resource=False, finished_at=now)
    return queued + running


def confirm_group(meeting, assignment_id, user, token):
    try:
        claims = signing.loads(token, salt=SALT, max_age=PREVIEW_SECONDS)
        if claims['assignment'] != assignment_id or claims['requester'] != user.pk:
            raise BatchError('Preview does not belong to this assignment and lecturer.', 400)
        uuid.UUID(claims['key'])
    except (signing.BadSignature, KeyError, ValueError, TypeError):
        raise BatchError('The preview is invalid or expired. Select the group and preview again.') from None
    try:
        with transaction.atomic():
            lock_and_authorize(meeting.pk, user, Membership.Role.LECTURER)
            previous = ReviewBatch.objects.filter(request_key=claims['key']).first()
            if previous:
                if previous.requester_id != user.pk or previous.assignment_id != assignment_id or previous.preview_digest != claims['digest']:
                    raise BatchError('Conflicting group confirmation.', 409)
                return previous
            assignment, snapshot = _snapshot(meeting, assignment_id, user, claims['owners'])
            if digest(snapshot) != claims['digest']:
                labels = {'sources':'submitted versions', 'instructions':'instructions', 'criteria':'criteria',
                          'rubric':'professional rubric', 'language':'feedback language'}
                raise SourcesChanged([label for key,label in labels.items() if digest(snapshot[key]) != claims['parts'][key]], claims['owners'])
            _validate(assignment, snapshot)
            ids = [s['id'] for s in snapshot['sources']]
            expire_batch_jobs(submission_ids=ids)
            if ReviewJob.objects.filter(submission_id__in=ids, status__in=['queued','running']).exists():
                raise BatchError('A selected version already has an active review request. Open its submission to check it; no group was created.', 409)
            now = timezone.now()
            batch = ReviewBatch.objects.create(assignment=assignment, requester=user, request_key=claims['key'],
                preview_digest=claims['digest'], sources_snapshot=snapshot['sources'],
                instructions_snapshot=snapshot['instructions'], criteria_snapshot=snapshot['criteria'],
                rubric_snapshot=snapshot['rubric'], language=snapshot['language'], created_at=now,
                queue_expires_at=now + timedelta(seconds=QUEUE_SECONDS))
            for source in snapshot['sources']:
                peers = [{k:p[k] for k in ['id','student_id','version','text']} for p in snapshot['sources'] if p['student_id'] != source['student_id']]
                ReviewJob.objects.create(batch=batch, submission_id=source['id'], requester=user,
                    instructions_snapshot=batch.instructions_snapshot, criteria_snapshot=batch.criteria_snapshot,
                    rubric_snapshot=batch.rubric_snapshot, language=batch.language, target_text=source['text'], peer_snapshots=peers)
            return batch
    except IntegrityError:
        # The transaction has rolled back, including a partially inserted group.
        previous = ReviewBatch.objects.filter(request_key=claims['key'], requester=user, assignment_id=assignment_id,
                                             preview_digest=claims['digest']).first()
        if previous:
            return previous
        raise BatchError('A selected version acquired another active request. Review current requests before confirming again.', 409) from None


ERRORS = {
    'queue_timeout':'The 15-minute queue limit expired before generation started. No draft was generated.',
    'processing_timeout':'The 180-second processing limit expired. No draft was published or retried automatically.',
    'interrupted':'Processing was interrupted. No automatic retry was made.',
    'provider_unavailable':'The configured English feedback provider is unavailable.',
    'individual_failed':'Individual generation or validation failed. There is no draft to publish.',
    'comparison_failed':'Individual feedback is ready; comparison failed. Review and publish individually if appropriate.',
    'access_changed':'Course access changed before processing. No new draft was generated.',
}


def batch_state(batch):
    expire_batch_jobs(batch_id=batch.pk)
    jobs = list(batch.jobs.select_related('submission__student','draft','batch').order_by('pk'))
    rows = [{'id':job.pk, 'student':job.submission.student.username, 'version':job.submission.version_number,
             'status':job.status, 'label':job.display_status, 'comparison':job.get_comparison_status_display(),
             'reason':ERRORS.get(job.error_code,''),
             'elapsed':round(max(0, ((job.finished_at or timezone.now())-job.started_at).total_seconds()),1) if job.started_at else 0}
            for job in jobs]
    return {'rows':rows, 'total':len(rows), 'finished':sum(j.status in ['ready','failed'] for j in jobs),
            'ready':sum(j.status=='ready' for j in jobs), 'partial':sum(j.status=='ready' and j.comparison_status=='failed' for j in jobs),
            'failed':sum(j.status=='failed' for j in jobs), 'pending':any(j.status in ['queued','running'] for j in jobs)}
