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


class Poll(models.Model):
    class Kind(models.TextChoices):
        COMPREHENSION = 'comprehension', 'Comprehension question'
        OPINION = 'opinion', 'Opinion poll'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'

    class Language(models.TextChoices):
        HEBREW = 'he', 'Hebrew'
        ENGLISH = 'en', 'English'

    meeting = models.ForeignKey(Meeting, on_delete=models.PROTECT, related_name='polls')
    kind = models.CharField(max_length=16, choices=Kind.choices)
    language = models.CharField(max_length=2, choices=Language.choices)
    material = models.TextField(validators=[MaxLengthValidator(6000)])
    question = models.TextField()
    options = models.JSONField()
    correct_index = models.PositiveSmallIntegerField(null=True, blank=True)
    explanation = models.TextField(blank=True)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.DRAFT)
    origin = models.CharField(max_length=4, choices=[('demo', 'Local demo'), ('ai', 'Model output')])
    demo_key = models.CharField(max_length=64, null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField()
    published_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at', '-pk']
        constraints = [
            models.UniqueConstraint(fields=['meeting'], condition=models.Q(status='active'), name='one_active_poll_per_meeting'),
            models.UniqueConstraint(fields=['meeting', 'demo_key'], condition=models.Q(demo_key__isnull=False), name='one_demo_poll_per_key'),
            models.CheckConstraint(condition=models.Q(kind__in=['comprehension', 'opinion']), name='valid_poll_kind'),
            models.CheckConstraint(condition=models.Q(language__in=['he', 'en']), name='valid_poll_language'),
            models.CheckConstraint(condition=models.Q(origin__in=['demo', 'ai']), name='valid_poll_origin'),
            models.CheckConstraint(condition=(
                models.Q(kind='opinion', correct_index__isnull=True, explanation='') |
                (models.Q(kind='comprehension', correct_index__gte=0, correct_index__lte=3, correct_index__isnull=False) & ~models.Q(explanation=''))
            ), name='poll_answer_matches_kind'),
            models.CheckConstraint(condition=(
                models.Q(status='draft', published_at__isnull=True, closed_at__isnull=True) |
                models.Q(status='active', published_at__isnull=False, closed_at__isnull=True) |
                models.Q(status='closed', published_at__isnull=False, closed_at__isnull=False)
            ), name='valid_poll_lifecycle'),
        ]

    @property
    def origin_label(self):
        return 'Demo data — not generated by AI' if self.origin == 'demo' else 'Model-generated draft — lecturer review required'


class PollVote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.PROTECT, related_name='votes')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='poll_votes')
    option_index = models.PositiveSmallIntegerField()
    submitted_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['poll', 'student'], name='one_final_vote_per_student_poll'),
            models.CheckConstraint(condition=models.Q(option_index__gte=0, option_index__lte=3), name='valid_vote_option_index'),
        ]
