from django.conf import settings
from django.db import models


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
