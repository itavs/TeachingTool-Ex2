from django.conf import settings
from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator
import uuid


class Course(models.Model):
    code = models.CharField(max_length=32, unique=True)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.title}"


class Membership(models.Model):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        LECTURER = "lecturer", "Lecturer"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=16, choices=Role.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="one_membership_per_user_course"),
            models.CheckConstraint(condition=models.Q(role__in=["student", "lecturer"]), name="valid_course_role"),
        ]


class Meeting(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="meetings")
    title = models.CharField(max_length=160)
    starts_at = models.DateTimeField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["starts_at", "pk"]

    def __str__(self):
        return self.title


class AttendanceWindow(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.PROTECT, related_name="attendance_windows")
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    opened_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    additional = models.BooleanField(default=False)

    class Meta:
        ordering = ["opened_at", "pk"]
        constraints = [
            models.UniqueConstraint(fields=["meeting"], condition=models.Q(closed_at__isnull=True), name="one_unclosed_attendance_window"),
            models.CheckConstraint(condition=models.Q(closes_at__gt=models.F("opened_at")), name="positive_attendance_window"),
        ]


class AttendanceRecord(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.PROTECT, related_name="attendance_records")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="attendance_records")
    window = models.ForeignKey(AttendanceWindow, on_delete=models.PROTECT)
    registered_at = models.DateTimeField()
    additional = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "meeting"], name="one_attendance_per_student_meeting")]

    @property
    def registration_label(self):
        return "Registered in an additional window" if self.additional else "Present"


class MeetingRequest(models.Model):
    class Kind(models.TextChoices):
        COMMENT = "comment", "Comment"
        SUGGESTION = "suggestion", "Suggestion"

    meeting = models.ForeignKey(Meeting, on_delete=models.PROTECT, related_name="requests")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="meeting_requests")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    text = models.TextField(validators=[MinLengthValidator(1), MaxLengthValidator(1000)])
    created_at = models.DateTimeField()
    submission_id = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        ordering = ["-created_at", "-pk"]
        constraints = [
            models.UniqueConstraint(fields=["student", "meeting", "submission_id"], name="one_request_per_submission"),
            models.CheckConstraint(condition=models.Q(kind__in=["comment", "suggestion"]), name="valid_meeting_request_kind"),
        ]
