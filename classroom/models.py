from django.conf import settings
from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.exceptions import ValidationError
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


class HomeworkAssignment(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.PROTECT, related_name="homework_assignments")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField(max_length=160)
    instructions = models.TextField()
    criteria = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]


class SubmissionVersion(models.Model):
    assignment = models.ForeignKey(HomeworkAssignment, on_delete=models.PROTECT, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="homework_versions")
    version_number = models.PositiveIntegerField()
    text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["student__username", "-version_number"]
        constraints = [
            models.UniqueConstraint(fields=["assignment", "student", "version_number"], name="unique_homework_owner_version"),
            models.CheckConstraint(condition=models.Q(version_number__gte=1), name="positive_homework_version"),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("Submitted versions cannot be edited. Submit a new version instead.")
        return super().save(*args, **kwargs)

    @property
    def status_label(self):
        return "Submitted"


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


class VideoJob(models.Model):
    class Status(models.TextChoices):
        UPLOADING = 'uploading', 'Saving upload'
        QUEUED = 'queued', 'Waiting for worker'
        VALIDATING = 'validating', 'Checking video'
        EXTRACTING = 'extracting', 'Extracting audio'
        LOADING_ASR = 'loading_asr', 'Loading local transcription model'
        TRANSCRIBING = 'transcribing', 'Transcribing speech locally'
        TRANSCRIBED = 'transcribed', 'Transcription completed'
        LOADING_SUM = 'loading_sum', 'Loading local summary model'
        SUMMARIZING = 'summarizing', 'Summarizing transcript locally'
        SUMMARIZED = 'summarized', 'Summary completed'
        EXTRACTED = 'extracted', 'Audio extraction completed'
        FAILED = 'failed', 'Processing failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.PROTECT, related_name='video_jobs')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='video_jobs')
    original_name = models.CharField(max_length=255)
    file_size = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.UPLOADING)
    created_at = models.DateTimeField()
    queued_at = models.DateTimeField(null=True)
    started_at = models.DateTimeField(null=True)
    heartbeat_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    source_expires_at = models.DateTimeField()
    source_deleted_at = models.DateTimeField(null=True)
    failed_stage = models.CharField(max_length=12, blank=True)
    error_code = models.CharField(max_length=32, blank=True)
    processing_seconds = models.FloatField(default=0)
    video_seconds = models.FloatField(null=True)
    audio_seconds = models.FloatField(null=True)
    audio_samples = models.PositiveIntegerField(null=True)
    transcription_requested = models.BooleanField(default=False)
    transcript = models.TextField(blank=True)
    transcript_segments = models.JSONField(default=list, blank=True)
    detected_language = models.CharField(max_length=8, blank=True)
    transcript_created_at = models.DateTimeField(null=True)
    transcript_expires_at = models.DateTimeField(null=True)
    transcript_deleted_at = models.DateTimeField(null=True)
    transcribed_until = models.FloatField(default=0)
    model_load_seconds = models.FloatField(null=True)
    transcription_seconds = models.FloatField(null=True)
    asr_metadata = models.JSONField(default=dict, blank=True)
    audio_removed_at = models.DateTimeField(null=True)
    summary_requested = models.BooleanField(default=False)
    summary_paragraph = models.TextField(blank=True)
    summary_points = models.JSONField(default=list, blank=True)
    summary_metadata = models.JSONField(default=dict, blank=True)
    summary_created_at = models.DateTimeField(null=True)
    summary_expires_at = models.DateTimeField(null=True)
    summary_deleted_at = models.DateTimeField(null=True)
    summary_seconds = models.FloatField(null=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [models.CheckConstraint(condition=models.Q(status__in=['uploading','queued','validating','extracting','extracted','loading_asr','transcribing','transcribed','loading_sum','summarizing','summarized','failed']), name='valid_video_job_status')]
