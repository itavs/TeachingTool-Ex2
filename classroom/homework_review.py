"""Version-bound requests, private drafts and explicit immutable publication."""
from django.db import transaction
from django.utils import timezone
from .attendance import authorize, lock_and_authorize, CourseAccessError
from .models import Membership, HomeworkAssignment, SubmissionVersion, ReviewJob, FeedbackDraft
from .homework_provider import get_homework_reviewer

NO_PEERS = 'No other submissions are available for comparison yet.'
COMPARISON_FAILED = 'Your lecturer published your individual feedback. The comparison with other submissions could not be completed.'
NO_DIFFERENCE = 'The comparison was completed. No supported difference was found in the reviewed submissions.'


class ReviewError(Exception):
    pass


def availability(assignment):
    language = assignment.get_feedback_language_display()
    enabled = get_homework_reviewer().available(assignment.feedback_language)
    return enabled, '' if enabled else f'Automatic feedback generation is unavailable for {language}. No request will be created.'


def check_requester(submission, user):
    meeting, membership = authorize(submission.assignment.meeting_id, user)
    if membership.role == Membership.Role.STUDENT and submission.student_id != user.pk:
        raise CourseAccessError(404)
    return meeting, membership


@transaction.atomic
def request_review(submission, user):
    meeting, membership = check_requester(submission, user)
    lock_and_authorize(meeting.pk, user, membership.role)
    assignment = HomeworkAssignment.objects.get(pk=submission.assignment_id)
    enabled, reason = availability(assignment)
    if not enabled:
        raise ReviewError(reason)
    if not Membership.objects.filter(course_id=meeting.course_id, user=submission.student, role='student').exists():
        raise ReviewError('The submission owner is no longer a Student in this course.')
    active = submission.review_jobs.filter(status__in=['queued','running']).first()
    if active:
        return active
    peers, owners = [], set()
    versions = SubmissionVersion.objects.filter(assignment=assignment).exclude(student_id=submission.student_id).order_by('student_id','-version_number')
    for version in versions:
        if version.student_id not in owners:
            peers.append({'id':version.pk, 'student_id':version.student_id, 'version':version.version_number, 'text':version.text})
            owners.add(version.student_id)
    return ReviewJob.objects.create(submission=submission, requester=user, instructions_snapshot=assignment.instructions,
        criteria_snapshot=assignment.criteria, target_text=submission.text, peer_snapshots=peers, language=assignment.feedback_language)


def owned_job(meeting, job_id, user):
    authorize(meeting.pk, user, Membership.Role.LECTURER)
    job = ReviewJob.objects.select_related('submission__assignment','submission__student').filter(pk=job_id, submission__assignment__meeting=meeting).first()
    if job is None:
        raise CourseAccessError(404)
    return job


def ensure_editable(draft, version):
    if draft.published_at is not None:
        raise ReviewError('Published feedback is immutable. A new review requires separate publication.')
    if draft.version != version:
        raise ReviewError('This draft changed. Reload and review it before continuing.')


@transaction.atomic
def edit_draft(meeting, job_id, user, data):
    lock_and_authorize(meeting.pk, user, Membership.Role.LECTURER)
    job = owned_job(meeting, job_id, user)
    draft = FeedbackDraft.objects.select_for_update().filter(job=job).first()
    if draft is None or job.status != 'ready':
        raise ReviewError('No successful individual draft is available.')
    ensure_editable(draft, data['version'])
    draft.individual_text = data['individual_text']
    draft.comparison_text = data['comparison_text'] if job.comparison_status in ['compared','no_difference'] else ''
    draft.version += 1
    draft.save()
    return draft


@transaction.atomic
def publish(meeting, job_id, user, version, mode):
    lock_and_authorize(meeting.pk, user, Membership.Role.LECTURER)
    job = owned_job(meeting, job_id, user)
    draft = FeedbackDraft.objects.select_for_update().filter(job=job).first()
    if draft is None or job.status != 'ready':
        raise ReviewError('No successful individual draft is available to publish.')
    ensure_editable(draft, version)
    expected = 'individual_only' if job.comparison_status == 'failed' else 'complete'
    if mode != expected or job.comparison_status not in ['failed','no_peers','compared','no_difference']:
        raise ReviewError('Explicitly choose the publication action appropriate to the comparison state.')
    if not draft.individual_text.strip():
        raise ReviewError('Individual feedback cannot be empty.')
    if job.comparison_status in ['compared','no_difference'] and not draft.comparison_text.strip():
        raise ReviewError('Review and complete the anonymous comparison before publication.')
    # Every publication is tied to this immutable source, including older versions.
    # It never becomes feedback for a later submission simply because that exists.
    draft.published_individual = draft.individual_text
    draft.published_comparison = draft.comparison_text if job.comparison_status in ['compared','no_difference'] else ''
    draft.published_comparison_status = job.comparison_status
    draft.published_at = timezone.now()
    draft.published_by = user
    draft.version += 1
    draft.save()
    return draft


def published_feedback(submission):
    # Never serialize job snapshots or mutable draft fields to Student responses.
    result = []
    for draft in FeedbackDraft.objects.filter(job__submission=submission, published_at__isnull=False).order_by('-published_at','-pk'):
        result.append({'individual':draft.published_individual, 'comparison':draft.published_comparison,
            'notice':{'no_peers':NO_PEERS,'failed':COMPARISON_FAILED,'no_difference':NO_DIFFERENCE}.get(draft.published_comparison_status,''),
            'comparison_status':draft.published_comparison_status, 'published_at':draft.published_at,
            'requested_at':draft.job.created_at})
    return result
