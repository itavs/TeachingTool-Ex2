"""Attendance rules. GET token generation is stateless; only POST calls writes."""
from datetime import timedelta
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import AttendanceRecord, AttendanceWindow, Meeting, Membership

INITIAL_SECONDS = 300
ADDITIONAL_SECONDS = 120
ROTATION_SECONDS = 30
VALIDITY_SECONDS = 45
SIGNER = signing.Signer(salt="classroom.attendance.v1")


class AttendanceError(Exception):
    pass


class CourseAccessError(Exception):
    def __init__(self, status):
        self.status = status


def authorize(meeting_id, user, role=None):
    meeting = Meeting.objects.select_related("course").filter(pk=meeting_id).first()
    if meeting is None:
        raise CourseAccessError(404)
    membership = Membership.objects.filter(user=user, course_id=meeting.course_id).first()
    if membership is None:
        raise CourseAccessError(404)
    if role is not None and membership.role != role:
        raise CourseAccessError(403)
    return meeting, membership


def lock_and_authorize(meeting_id, user, role):
    # Row lock is useful on a future PostgreSQL backend; SQLite uses BEGIN IMMEDIATE.
    if not Meeting.objects.select_for_update().filter(pk=meeting_id).exists():
        raise CourseAccessError(404)
    return authorize(meeting_id, user, role)


def current_window(meeting_id, now=None):
    now = now or timezone.now()
    return AttendanceWindow.objects.filter(meeting_id=meeting_id, closed_at__isnull=True, closes_at__gt=now).first()


@transaction.atomic
def open_window(meeting_id, user):
    lock_and_authorize(meeting_id, user, Membership.Role.LECTURER)
    now = timezone.now()
    existing = current_window(meeting_id, now)
    if existing:
        return existing
    additional = AttendanceWindow.objects.filter(meeting_id=meeting_id).exists()
    AttendanceWindow.objects.filter(meeting_id=meeting_id, closed_at__isnull=True).update(closed_at=now)
    return AttendanceWindow.objects.create(meeting_id=meeting_id, opened_at=now,
        closes_at=now + timedelta(seconds=ADDITIONAL_SECONDS if additional else INITIAL_SECONDS), additional=additional)


@transaction.atomic
def close_window(meeting_id, user):
    lock_and_authorize(meeting_id, user, Membership.Role.LECTURER)
    AttendanceWindow.objects.filter(meeting_id=meeting_id, closed_at__isnull=True).update(closed_at=timezone.now())


def token_for(window, now=None):
    now = now or timezone.now()
    step = int((now - window.opened_at).total_seconds() // ROTATION_SECONDS)
    return SIGNER.sign_object({"window": str(window.public_id), "meeting": window.meeting_id, "step": step})


def validate_token(meeting_id, token, now=None):
    now = now or timezone.now()
    try:
        if len(token) > 1024:
            raise ValueError
        payload = SIGNER.unsign_object(token)
        if set(payload) != {"window", "meeting", "step"} or type(payload["step"]) is not int or type(payload["meeting"]) is not int:
            raise ValueError
        if payload["meeting"] != meeting_id or payload["step"] < 0:
            raise ValueError
        window = AttendanceWindow.objects.get(public_id=payload["window"], meeting_id=meeting_id)
        issued = window.opened_at + timedelta(seconds=payload["step"] * ROTATION_SECONDS)
        if window.closed_at is not None or now < issued or now >= min(window.closes_at, issued + timedelta(seconds=VALIDITY_SECONDS)):
            raise ValueError
        return window
    except (signing.BadSignature, ValidationError, ValueError, TypeError, KeyError, AttendanceWindow.DoesNotExist, OverflowError):
        raise AttendanceError("This code is invalid, expired, or its registration window is closed. Scan the current QR again.") from None


@transaction.atomic
def register(meeting_id, user, token):
    lock_and_authorize(meeting_id, user, Membership.Role.STUDENT)
    now = timezone.now()  # Validate after any lock wait, not at HTTP arrival time.
    window = validate_token(meeting_id, token, now)
    return AttendanceRecord.objects.get_or_create(meeting_id=meeting_id, student=user,
        defaults={"window": window, "registered_at": now, "additional": window.additional})


HEADERS = ["Username", "Display name", "Course code", "Course title", "Meeting",
           "Meeting time (Asia/Jerusalem)", "Registration status", "First registration (Asia/Jerusalem)"]


def display_time(value):
    return timezone.localtime(value).strftime("%Y-%m-%d %H:%M:%S") if value else ""


def roster(meeting):
    members = Membership.objects.filter(course_id=meeting.course_id, role=Membership.Role.STUDENT).select_related("user").order_by("user__username")
    records = {r.student_id: r for r in meeting.attendance_records.all()}
    rows = []
    for membership in members:
        record = records.get(membership.user_id)
        rows.append([membership.user.username, membership.user.get_full_name() or membership.user.username,
            meeting.course.code, meeting.course.title, meeting.title, display_time(meeting.starts_at),
            record.registration_label if record else "Not registered", display_time(record.registered_at) if record else ""])
    return rows
