"""Course-authorized assignment creation and append-only submitted versions."""
from django.db import transaction
from django.db.models import Max
from .attendance import CourseAccessError, lock_and_authorize
from .models import HomeworkAssignment, Membership, SubmissionVersion


def assignment_for(meeting, assignment_id):
    assignment = HomeworkAssignment.objects.filter(pk=assignment_id, meeting=meeting).first()
    if assignment is None:
        raise CourseAccessError(404)
    return assignment


@transaction.atomic
def create_assignment(meeting, user, data):
    lock_and_authorize(meeting.pk, user, Membership.Role.LECTURER)
    return HomeworkAssignment.objects.create(meeting=meeting, created_by=user, **data)


@transaction.atomic
def submit_version(meeting, assignment_id, user, text):
    # SQLite IMMEDIATE acquires the write reservation before reading the maximum.
    # The meeting lock also expresses the locking order for a future row-lock DB.
    lock_and_authorize(meeting.pk, user, Membership.Role.STUDENT)
    assignment = assignment_for(meeting, assignment_id)
    previous = assignment.submissions.filter(student=user).aggregate(last=Max("version_number"))["last"] or 0
    return SubmissionVersion.objects.create(assignment=assignment, student=user,
                                             version_number=previous + 1, text=text)


def submission_for(assignment, submission_id, user, membership):
    versions = assignment.submissions.select_related("student")
    if membership.role == Membership.Role.STUDENT:
        versions = versions.filter(student=user)
    submission = versions.filter(pk=submission_id).first()
    if submission is None:
        raise CourseAccessError(404)
    return submission
