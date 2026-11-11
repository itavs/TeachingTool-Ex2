"""Submission foundation: real form routes, source preservation and course privacy."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, OperationalError, connections, transaction
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from .models import Course, HomeworkAssignment, Meeting, Membership, SubmissionVersion
from .homework_services import submit_version


class HomeworkFixture:
    @classmethod
    def prepare(cls):
        users = get_user_model()
        cls.teacher = users.objects.create_user("hw_teacher")
        cls.student = users.objects.create_user("hw_student")
        cls.other = users.objects.create_user("hw_other")
        cls.outsider = users.objects.create_user("hw_outsider", is_staff=True, is_superuser=True)
        cls.course = Course.objects.create(code="HW1", title="Homework course")
        cls.foreign = Course.objects.create(code="HW2", title="Foreign course")
        for user, role in [(cls.teacher, "lecturer"), (cls.student, "student"), (cls.other, "student")]:
            Membership.objects.create(user=user, course=cls.course, role=role)
        Membership.objects.create(user=cls.teacher, course=cls.foreign, role="student")
        cls.meeting = Meeting.objects.create(course=cls.course, title="Homework meeting", starts_at=timezone.now())
        cls.foreign_meeting = Meeting.objects.create(course=cls.foreign, title="Foreign meeting", starts_at=timezone.now())
        cls.assignment = HomeworkAssignment.objects.create(meeting=cls.meeting, created_by=cls.teacher,
            title="Transactions", instructions="Explain transactions.", criteria=["Explain rollback", "Protect capacity"])

    def url(self, name, assignment=None, submission=None, meeting=None, course=None):
        args = [(course or self.course).pk, (meeting or self.meeting).pk]
        if assignment is not None:
            args.append(assignment.pk)
        if submission is not None:
            args.append(submission.pk)
        return reverse(name, args=args)


class HomeworkTests(HomeworkFixture, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.prepare()

    def test_lecturer_creates_assignment_and_student_reads_instructions_and_criteria(self):
        self.client.force_login(self.teacher)
        response = self.client.post(self.url("homework-create"), {
            "title": "New work", "instructions": "  Explain atomicity.\nPreserve this line.  ",
            "criteria": "Rollback\n\n Capacity protection ", "meeting": self.foreign_meeting.pk,
            "created_by": self.student.pk})
        saved = HomeworkAssignment.objects.get(title="New work")
        self.assertEqual(saved.meeting, self.meeting)
        self.assertEqual(saved.created_by, self.teacher)
        self.assertEqual(saved.criteria, ["Rollback", "Capacity protection"])
        self.assertEqual(saved.instructions, "  Explain atomicity.\nPreserve this line.  ")
        self.assertRedirects(response, self.url("homework-detail", saved))
        self.client.force_login(self.student)
        response = self.client.get(self.url("homework-detail", saved))
        self.assertContains(response, "Explain atomicity.")
        self.assertContains(response, "Rollback")
        self.assertNotContains(self.client.get(self.url("homework-list")), "New assignment")

    def test_normal_submission_confirmed_with_version_and_resubmission_preserves_exact_sources(self):
        self.client.force_login(self.student)
        first = "  מקור ראשון עם New Car\nrollback restores changes.  "
        second = "A distinct second version\nwith corrected cache handling."
        for number, text in enumerate([first, second], 1):
            response = self.client.post(self.url("homework-detail", self.assignment), {
                "text": text, "student": self.other.pk, "version_number": 99,
                "assignment": 999, "status": "reviewed"}, follow=True)
            self.assertContains(response, f"Your work was saved. Version {number}")
            self.assertContains(response, f"Submitted work · Version {number}")
            self.assertContains(response, "Status: Submitted")
            self.assertNotContains(response, "Request feedback")
        versions = list(self.assignment.submissions.filter(student=self.student).order_by("version_number"))
        self.assertEqual([(v.version_number, v.text) for v in versions], [(1, first), (2, second)])
        history = self.client.get(self.url("homework-detail", self.assignment))
        for version in versions:
            self.assertContains(history, self.url("homework-submission", self.assignment, version))
            self.assertEqual(self.client.get(self.url("homework-submission", self.assignment, version)).status_code, 200)
        self.client.force_login(self.teacher)
        for version in versions:
            response = self.client.get(self.url("homework-submission", self.assignment, version))
            self.assertContains(response, f"Version {version.version_number}")
            self.assertContains(response, self.student.username)
            self.assertEqual(response.context["submission"].text, version.text)

    def test_other_student_cannot_read_source_or_discover_its_link(self):
        submission = submit_version(self.meeting, self.assignment.pk, self.student, "PRIVATE CONTENT")
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get(self.url("homework-detail", self.assignment)),
                               self.url("homework-submission", self.assignment, submission))
        response = self.client.get(self.url("homework-submission", self.assignment, submission))
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, "PRIVATE CONTENT", status_code=404)

    def test_other_lecturer_in_course_can_read_but_foreign_lecturer_cannot(self):
        submission = submit_version(self.meeting, self.assignment.pk, self.student, "course private source")
        for course, expected in [(self.course, 200), (self.foreign, 404)]:
            user = get_user_model().objects.create_user("lecturer_" + course.code)
            Membership.objects.create(user=user, course=course, role="lecturer")
            self.client.force_login(user)
            response = self.client.get(self.url("homework-submission", self.assignment, submission))
            self.assertEqual(response.status_code, expected)
            if expected == 200:
                self.assertContains(response, "course private source")

    def test_nonmember_and_global_admin_flags_do_not_bypass_access(self):
        submission = submit_version(self.meeting, self.assignment.pk, self.student, "PRIVATE CONTENT")
        self.client.force_login(self.outsider)
        for name, a, v in [("homework-list", None, None), ("homework-create", None, None),
                           ("homework-detail", self.assignment, None), ("homework-submission", self.assignment, submission)]:
            self.assertEqual(self.client.get(self.url(name, a, v)).status_code, 404)
            self.assertEqual(self.client.post(self.url(name, a, v), {"text": "forged"}).status_code, 405 if name in ["homework-list", "homework-submission"] else 404)

    def test_parent_meeting_assignment_and_submission_substitution_are_rejected(self):
        submission = submit_version(self.meeting, self.assignment.pk, self.student, "private")
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(self.url("homework-list", course=self.foreign)).status_code, 404)
        self.assertEqual(self.client.get(self.url("homework-detail", self.assignment, meeting=self.foreign_meeting,
                                                  course=self.foreign)).status_code, 404)
        second = HomeworkAssignment.objects.create(meeting=self.meeting, created_by=self.teacher,
            title="Other", instructions="Explain.", criteria=["Correctness"])
        self.assertEqual(self.client.get(self.url("homework-submission", second, submission)).status_code, 404)

    def test_roles_are_per_course_and_student_cannot_create_or_lecturer_submit(self):
        self.client.force_login(self.student)
        for method in [self.client.get, self.client.post]:
            self.assertEqual(method(self.url("homework-create")).status_code, 403)
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.post(self.url("homework-detail", self.assignment), {"text": "forged"}).status_code, 403)
        self.assertEqual(self.client.get(self.url("homework-create", meeting=self.foreign_meeting,
                                                  course=self.foreign)).status_code, 403)
        self.assertEqual(SubmissionVersion.objects.count(), 0)

    def test_current_membership_rechecked_on_direct_read_and_stale_form_post(self):
        submission = submit_version(self.meeting, self.assignment.pk, self.student, "private")
        self.client.force_login(self.teacher)
        Membership.objects.filter(user=self.teacher, course=self.course).update(role="student")
        self.assertEqual(self.client.get(self.url("homework-submission", self.assignment, submission)).status_code, 404)
        self.assertEqual(self.client.post(self.url("homework-create"), {"title": "x", "instructions": "x", "criteria": "x"}).status_code, 403)
        self.client.force_login(self.student)
        Membership.objects.filter(user=self.student, course=self.course).delete()
        self.assertEqual(self.client.get(self.url("homework-submission", self.assignment, submission)).status_code, 404)
        self.assertEqual(self.client.post(self.url("homework-detail", self.assignment), {"text": "new"}).status_code, 404)

    def test_anonymous_routes_require_login_and_read_only_routes_reject_post(self):
        submission = submit_version(self.meeting, self.assignment.pk, self.student, "private")
        for name, a, v in [("homework-list", None, None), ("homework-create", None, None),
                           ("homework-detail", self.assignment, None), ("homework-submission", self.assignment, submission)]:
            response = self.client.get(self.url(name, a, v))
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(reverse("login")))
        self.client.force_login(self.student)
        self.assertEqual(self.client.post(self.url("homework-submission", self.assignment, submission), {"text": "edit"}).status_code, 405)
        self.assertEqual(self.client.post(self.url("homework-list")).status_code, 405)

    def test_csrf_enforced_for_both_writes(self):
        client = Client(enforce_csrf_checks=True)
        for user, url, data in [(self.teacher, self.url("homework-create"), {"title": "CSRF", "instructions": "x", "criteria": "x"}),
                                (self.student, self.url("homework-detail", self.assignment), {"text": "CSRF source"})]:
            client.force_login(user)
            self.assertEqual(client.post(url, data).status_code, 403)
            client.get(url)
            self.assertEqual(client.post(url, {**data, "csrfmiddlewaretoken": client.cookies["csrftoken"].value}).status_code, 302)

    def test_invalid_forms_do_not_save_and_preserve_bound_input(self):
        self.client.force_login(self.teacher)
        for field in ["title", "instructions", "criteria"]:
            data = {"title": "Title", "instructions": "Instructions", "criteria": "Criterion"}
            data[field] = " \n "
            self.assertEqual(self.client.post(self.url("homework-create"), data).status_code, 200)
        self.assertEqual(HomeworkAssignment.objects.count(), 1)
        self.client.force_login(self.student)
        response = self.client.post(self.url("homework-detail", self.assignment), {"text": " \n "})
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(response.context["form"].data["text"], " \n ")
        self.assertEqual(SubmissionVersion.objects.count(), 0)

    def test_text_is_escaped_and_never_rendered_as_html(self):
        submission = submit_version(self.meeting, self.assignment.pk, self.student, "<script>alert('private')</script>\nעברית New Car")
        self.client.force_login(self.teacher)
        response = self.client.get(self.url("homework-submission", self.assignment, submission))
        self.assertNotContains(response, "<script>alert")
        self.assertContains(response, "&lt;script&gt;")
        self.assertContains(response, 'class="submission-text" dir="auto"')

    def test_failed_save_does_not_confirm_success(self):
        self.client.force_login(self.student)
        with patch("classroom.homework_services.submit_version", side_effect=OperationalError("busy")):
            response = self.client.post(self.url("homework-detail", self.assignment), {"text": "source"})
        self.assertEqual(response.status_code, 503)
        self.assertNotContains(response, "Your work was saved", status_code=503)
        self.assertEqual(SubmissionVersion.objects.count(), 0)

    def test_saved_versions_cannot_be_edited_and_database_rejects_invalid_numbering(self):
        submission = submit_version(self.meeting, self.assignment.pk, self.student, "original")
        submission.text = "replacement"
        with self.assertRaises(ValidationError):
            submission.save()
        submission.refresh_from_db()
        self.assertEqual(submission.text, "original")
        for version in [0, 1]:
            with self.assertRaises(IntegrityError), transaction.atomic():
                SubmissionVersion.objects.create(assignment=self.assignment, student=self.student,
                                                 version_number=version, text="invalid")


class HomeworkConcurrencyTests(HomeworkFixture, TransactionTestCase):
    def setUp(self):
        self.prepare()

    def test_parallel_submissions_get_distinct_versions_and_preserve_both_texts(self):
        barrier = Barrier(2)
        def save(text):
            connections.close_all()
            try:
                barrier.wait(timeout=10)
                return submit_version(self.meeting, self.assignment.pk, self.student, text).version_number
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            numbers = list(pool.map(save, ["first concurrent source", "second concurrent source"]))
        self.assertEqual(sorted(numbers), [1, 2])
        self.assertEqual(set(self.assignment.submissions.values_list("text", flat=True)),
                         {"first concurrent source", "second concurrent source"})
