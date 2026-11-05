from datetime import timedelta
from io import StringIO
import json
import secrets
from pathlib import Path
from tempfile import TemporaryDirectory
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from .models import Course, Meeting, Membership


class ClassroomAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model()
        cls.test_password = secrets.token_urlsafe(24)
        cls.student = users.objects.create_user("student", password=cls.test_password)
        cls.lecturer = users.objects.create_user("lecturer", password=cls.test_password)
        cls.outsider = users.objects.create_user("outsider", password=cls.test_password)
        cls.alpha = Course.objects.create(code="A", title="Private alpha course")
        cls.beta = Course.objects.create(code="B", title="Private beta course")
        cls.student_membership = Membership.objects.create(user=cls.student, course=cls.alpha, role="student")
        Membership.objects.create(user=cls.lecturer, course=cls.alpha, role="lecturer")
        Membership.objects.create(user=cls.lecturer, course=cls.beta, role="student")
        cls.alpha_meeting = Meeting.objects.create(course=cls.alpha, title="Alpha meeting", starts_at=timezone.now())
        cls.beta_meeting = Meeting.objects.create(course=cls.beta, title="Beta private meeting", starts_at=timezone.now())

    def url(self, name, course=None, meeting=None):
        args = []
        if course is not None:
            args.append(course.pk)
        if meeting is not None:
            args.append(meeting.pk)
        return reverse(name, args=args)

    def valid_data(self):
        return {"title": "A new meeting", "starts_at": "2026-11-10T14:30", "description": "Meeting notes."}

    def test_anonymous_get_and_post_redirect_to_login(self):
        urls = [reverse("course-list"), self.url("course-detail", self.alpha),
                self.url("meeting-detail", self.alpha, self.alpha_meeting),
                self.url("meeting-create", self.alpha), self.url("meeting-edit", self.alpha, self.alpha_meeting)]
        for url in urls:
            for method in ["get", "post"]:
                with self.subTest(url=url, method=method):
                    self.assertRedirects(getattr(self.client, method)(url), reverse("login") + "?next=" + url)

    def test_login_error_and_success(self):
        self.assertContains(self.client.post(reverse("login"), {"username": "student", "password": "wrong"}), "Please enter a correct")
        response = self.client.post(reverse("login"), {"username": "student", "password": self.test_password})
        self.assertRedirects(response, reverse("course-list"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.student.pk)

    def test_login_does_not_allow_external_next(self):
        response = self.client.post(reverse("login"), {"username": "student", "password": self.test_password, "next": "https://example.org/"})
        self.assertRedirects(response, reverse("course-list"))

    def test_logout_is_post_only_and_invalidates_session(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("logout")), reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(self.client.get(reverse("course-list")).status_code, 302)

    def test_inactive_user_cannot_login(self):
        self.student.is_active = False
        self.student.save()
        response = self.client.post(reverse("login"), {"username": "student", "password": self.test_password})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_course_list_does_not_leak_other_courses(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("course-list"))
        self.assertContains(response, self.alpha.title)
        self.assertNotContains(response, self.beta.title)

    def test_direct_other_course_and_meeting_urls_return_generic_404(self):
        self.client.force_login(self.student)
        urls = [self.url("course-detail", self.beta), self.url("meeting-detail", self.beta, self.beta_meeting),
                self.url("meeting-create", self.beta), self.url("meeting-edit", self.beta, self.beta_meeting)]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "We couldn't open that page.", status_code=404)
                self.assertNotContains(response, self.beta.title, status_code=404)
                self.assertNotContains(response, self.beta_meeting.title, status_code=404)

    def test_wrong_parent_course_cannot_expose_or_modify_meeting(self):
        self.client.force_login(self.lecturer)
        for route in ["meeting-detail", "meeting-edit"]:
            url = self.url(route, self.alpha, self.beta_meeting)
            self.assertEqual(self.client.get(url).status_code, 404)
            if route == "meeting-edit":
                self.assertEqual(self.client.post(url, self.valid_data()).status_code, 404)
        self.beta_meeting.refresh_from_db()
        self.assertEqual(self.beta_meeting.title, "Beta private meeting")

    def test_student_can_view_but_cannot_create_or_edit_even_with_forged_role(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.url("course-detail", self.alpha)).status_code, 200)
        self.assertEqual(self.client.get(self.url("meeting-detail", self.alpha, self.alpha_meeting)).status_code, 200)
        count = Meeting.objects.count()
        for route in ["meeting-create", "meeting-edit"]:
            url = self.url(route, self.alpha, self.alpha_meeting if route == "meeting-edit" else None)
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url, {**self.valid_data(), "role": "lecturer", "user": self.lecturer.pk}).status_code, 403)
        self.assertEqual(Meeting.objects.count(), count)
        self.alpha_meeting.refresh_from_db()
        self.assertEqual(self.alpha_meeting.title, "Alpha meeting")

    def test_role_is_per_course_and_not_global(self):
        self.client.force_login(self.lecturer)
        self.assertEqual(self.client.get(self.url("meeting-create", self.alpha)).status_code, 200)
        self.assertEqual(self.client.get(self.url("meeting-create", self.beta)).status_code, 403)
        self.assertEqual(self.client.post(self.url("meeting-create", self.beta), self.valid_data()).status_code, 403)

    def test_staff_and_superuser_flags_do_not_bypass_course_membership(self):
        self.outsider.is_staff = True
        self.outsider.is_superuser = True
        self.outsider.save()
        self.client.force_login(self.outsider)
        self.assertEqual(self.client.get(self.url("course-detail", self.alpha)).status_code, 404)
        self.assertEqual(self.client.post(self.url("meeting-create", self.alpha), self.valid_data()).status_code, 404)

    def test_removed_membership_is_checked_again_on_next_request(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.url("course-detail", self.alpha)).status_code, 200)
        Membership.objects.filter(pk=self.student_membership.pk).delete()
        self.assertEqual(self.client.get(self.url("course-detail", self.alpha)).status_code, 404)

    def test_demoted_lecturer_cannot_submit_a_stale_edit_form(self):
        self.client.force_login(self.lecturer)
        url = self.url("meeting-edit", self.alpha, self.alpha_meeting)
        self.assertEqual(self.client.get(url).status_code, 200)
        Membership.objects.filter(user=self.lecturer, course=self.alpha).update(role="student")
        self.assertEqual(self.client.post(url, self.valid_data()).status_code, 403)

    def test_empty_membership_state(self):
        self.client.force_login(self.outsider)
        self.assertContains(self.client.get(reverse("course-list")), "No courses yet")

    def test_multiple_courses_and_course_specific_buttons(self):
        self.client.force_login(self.lecturer)
        response = self.client.get(reverse("course-list"))
        self.assertContains(response, self.alpha.title)
        self.assertContains(response, self.beta.title)
        self.assertContains(self.client.get(self.url("course-detail", self.alpha)), "New meeting")
        self.assertNotContains(self.client.get(self.url("course-detail", self.beta)), "New meeting")

    def test_lecturer_creates_meeting_without_trusting_posted_course(self):
        self.client.force_login(self.lecturer)
        response = self.client.post(self.url("meeting-create", self.alpha), {**self.valid_data(), "course": self.beta.pk})
        meeting = Meeting.objects.get(title="A new meeting")
        self.assertEqual(meeting.course, self.alpha)
        self.assertTrue(timezone.is_aware(meeting.starts_at))
        self.assertRedirects(response, self.url("meeting-detail", self.alpha, meeting))

    def test_lecturer_edits_meeting_and_cannot_move_it_to_another_course(self):
        self.client.force_login(self.lecturer)
        response = self.client.post(self.url("meeting-edit", self.alpha, self.alpha_meeting), {**self.valid_data(), "course": self.beta.pk})
        self.alpha_meeting.refresh_from_db()
        self.assertEqual(self.alpha_meeting.title, "A new meeting")
        self.assertEqual(self.alpha_meeting.course, self.alpha)
        self.assertRedirects(response, self.url("meeting-detail", self.alpha, self.alpha_meeting))

    def test_invalid_title_or_date_does_not_save(self):
        self.client.force_login(self.lecturer)
        for values in [{"title": "   "}, {"starts_at": "not-a-date"}, {"title": "x" * 161}]:
            response = self.client.post(self.url("meeting-edit", self.alpha, self.alpha_meeting), {**self.valid_data(), **values})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
            self.alpha_meeting.refresh_from_db()
            self.assertEqual(self.alpha_meeting.title, "Alpha meeting")

    def test_text_is_html_escaped(self):
        self.alpha_meeting.description = '<script>alert("unsafe")</script>'
        self.alpha_meeting.save()
        self.client.force_login(self.student)
        response = self.client.get(self.url("meeting-detail", self.alpha, self.alpha_meeting))
        self.assertNotContains(response, '<script>alert(')
        self.assertContains(response, "&lt;script&gt;")

    def test_csrf_required_for_login_logout_and_meeting_write(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(reverse("login"), self.valid_data()).status_code, 403)
        client.force_login(self.lecturer)
        self.assertEqual(client.post(reverse("logout")).status_code, 403)
        self.assertEqual(client.post(self.url("meeting-create", self.alpha), self.valid_data()).status_code, 403)
        self.assertEqual(client.post(self.url("meeting-edit", self.alpha, self.alpha_meeting), self.valid_data()).status_code, 403)
        client.get(self.url("meeting-create", self.alpha))
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(self.url("meeting-create", self.alpha), {**self.valid_data(), "csrfmiddlewaretoken": token}).status_code, 302)

    def test_missing_resource_and_read_only_method_handling(self):
        self.client.force_login(self.lecturer)
        self.assertEqual(self.client.get(reverse("course-detail", args=[999999])).status_code, 404)
        self.assertEqual(self.client.get(reverse("meeting-detail", args=[self.alpha.pk, 999999])).status_code, 404)
        self.assertEqual(self.client.post(self.url("course-detail", self.alpha)).status_code, 405)
        self.assertEqual(self.client.post(self.url("meeting-detail", self.alpha, self.alpha_meeting)).status_code, 405)

    def test_membership_constraints(self):
        for values in [dict(user=self.student, course=self.alpha, role="student"),
                       dict(user=self.outsider, course=self.alpha, role="administrator")]:
            with self.subTest(values=values), self.assertRaises(IntegrityError), transaction.atomic():
                Membership.objects.create(**values)


class DemoSeedTests(TestCase):
    def test_seed_is_repeatable_preserves_passwords_and_creates_isolation_cases(self):
        with TemporaryDirectory() as directory, override_settings(LOCAL_DIR=Path(directory)):
            output = StringIO()
            call_command("seed_demo", stdout=output)
            credentials = json.loads((Path(directory) / "demo-credentials.json").read_text(encoding="utf-8"))
            hashes = dict(get_user_model().objects.values_list("username", "password"))
            call_command("seed_demo", stdout=output)
            self.assertEqual(get_user_model().objects.count(), 6)
            self.assertEqual(Course.objects.count(), 2)
            self.assertEqual(Membership.objects.count(), 7)
            self.assertEqual(Meeting.objects.count(), 4)
            self.assertEqual(dict(get_user_model().objects.values_list("username", "password")), hashes)
            self.assertFalse(Membership.objects.filter(user__username="observer").exists())
            self.assertEqual(set(Membership.objects.filter(user__username="lecturer_alpha").values_list("role", flat=True)), {"student", "lecturer"})
            for username, password in credentials.items():
                self.assertTrue(get_user_model().objects.get(username=username).check_password(password))
                self.assertNotIn(password, output.getvalue())

    def test_seed_refuses_to_take_over_existing_account(self):
        unrelated_password = secrets.token_urlsafe(24)
        existing = get_user_model().objects.create_user("student_alex", password=unrelated_password)
        with TemporaryDirectory() as directory, override_settings(LOCAL_DIR=Path(directory)):
            with self.assertRaises(CommandError):
                call_command("seed_demo", stdout=StringIO())
            self.assertFalse((Path(directory) / "demo-credentials.json").exists())
        existing.refresh_from_db()
        self.assertTrue(existing.check_password(unrelated_password))
        self.assertEqual(Course.objects.count(), 0)
