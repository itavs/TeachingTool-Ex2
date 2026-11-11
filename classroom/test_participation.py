"""Unit B behavior, access boundaries, time edges and real-connection races."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from io import BytesIO
import secrets
from threading import Barrier
from unittest.mock import patch
import uuid
from django.contrib.auth import get_user_model
from django.db import connections, connection, OperationalError
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from openpyxl import load_workbook
from . import attendance as rules
from .models import AttendanceRecord, AttendanceWindow, Course, Meeting, MeetingRequest, Membership


class ParticipationFixture:
    def prepare(self):
        users = get_user_model()
        self.password = secrets.token_urlsafe(24)
        self.teacher = users.objects.create_user("teacher", password=self.password)
        self.student = users.objects.create_user("student", password=self.password)
        self.other = users.objects.create_user("other", password=self.password)
        self.outsider = users.objects.create_user("outsider", password=self.password)
        self.course = Course.objects.create(code="ONE", title="Course one")
        self.foreign = Course.objects.create(code="TWO", title="Course two")
        for user, role in [(self.teacher, "lecturer"), (self.student, "student"), (self.other, "student")]:
            Membership.objects.create(user=user, course=self.course, role=role)
        Membership.objects.create(user=self.teacher, course=self.foreign, role="student")
        self.meeting = Meeting.objects.create(course=self.course, title="Meeting one", starts_at=timezone.now())
        self.foreign_meeting = Meeting.objects.create(course=self.foreign, title="Foreign meeting", starts_at=timezone.now())
        self.now = timezone.now()

    def url(self, name, token=None, course=None, meeting=None):
        return reverse(name, args=[(course or self.course).pk, (meeting or self.meeting).pk] + ([token] if token else []))

    def opened(self):
        with patch("classroom.attendance.timezone.now", return_value=self.now):
            window = rules.open_window(self.meeting.pk, self.teacher)
        return window, rules.token_for(window, self.now)

    def post_request(self, text="A useful suggestion", kind="suggestion", nonce=None):
        return self.client.post(self.url("meeting-requests"), {"text": text, "kind": kind, "submission_id": nonce or uuid.uuid4()})


class ParticipationTests(ParticipationFixture, TestCase):
    def setUp(self):
        self.prepare()

    def test_initial_additional_duration_and_active_open_idempotency(self):
        window, _ = self.opened()
        self.assertEqual((window.closes_at-window.opened_at).total_seconds(), 300)
        self.assertEqual(rules.open_window(self.meeting.pk, self.teacher).pk, window.pk)
        rules.close_window(self.meeting.pk, self.teacher)
        another = rules.open_window(self.meeting.pk, self.teacher)
        self.assertTrue(another.additional)
        self.assertEqual((another.closes_at-another.opened_at).total_seconds(), 120)

    def test_expired_window_can_reopen_without_explicit_close(self):
        first, _ = self.opened()
        with patch("classroom.attendance.timezone.now", return_value=self.now+timedelta(seconds=300)):
            second = rules.open_window(self.meeting.pk, self.teacher)
        first.refresh_from_db()
        self.assertIsNotNone(first.closed_at)
        self.assertTrue(second.additional)

    def test_rotation_overlap_expiry_and_window_end(self):
        window, token = self.opened()
        self.assertEqual(token, rules.token_for(window, self.now+timedelta(seconds=29)))
        self.assertNotEqual(token, rules.token_for(window, self.now+timedelta(seconds=30)))
        rules.validate_token(self.meeting.pk, token, self.now+timedelta(seconds=44, microseconds=999999))
        for seconds in [-1, 45, 300]:
            with self.subTest(seconds=seconds), self.assertRaises(rules.AttendanceError):
                rules.validate_token(self.meeting.pk, token, self.now+timedelta(seconds=seconds))
        final = rules.token_for(window, self.now+timedelta(seconds=299))
        rules.validate_token(self.meeting.pk, final, self.now+timedelta(seconds=299))
        with self.assertRaises(rules.AttendanceError):
            rules.validate_token(self.meeting.pk, final, self.now+timedelta(seconds=300))

    def test_close_invalidates_every_code_even_after_reopen(self):
        window, token = self.opened()
        rules.close_window(self.meeting.pk, self.teacher)
        rules.open_window(self.meeting.pk, self.teacher)
        with self.assertRaises(rules.AttendanceError):
            rules.validate_token(self.meeting.pk, token, self.now)

    def test_bad_signature_wrong_meeting_and_malformed_payload(self):
        window, token = self.opened()
        bad_tokens = [token+"x", rules.SIGNER.sign_object({"window": "bad", "meeting": self.meeting.pk, "step": 0}),
            rules.SIGNER.sign_object({"window": str(window.public_id), "meeting": self.meeting.pk, "step": True}),
            rules.SIGNER.sign_object([1, 2]), "a"*1025]
        for bad in bad_tokens:
            with self.subTest(token_length=len(bad)), self.assertRaises(rules.AttendanceError):
                rules.validate_token(self.meeting.pk, bad, self.now)
        with self.assertRaises(rules.AttendanceError):
            rules.validate_token(self.foreign_meeting.pk, token, self.now)

    def test_scan_get_and_head_do_not_record_attendance(self):
        _, token = self.opened()
        self.client.force_login(self.student)
        response = self.client.get(self.url("attendance-scan", token))
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertEqual(self.client.head(self.url("attendance-scan", token)).status_code, 405)
        self.assertEqual(AttendanceRecord.objects.count(), 0)
        self.assertEqual(self.client.post(self.url("attendance-scan", token)).status_code, 302)
        self.assertEqual(AttendanceRecord.objects.count(), 1)

    def test_login_continuation_preserves_scan_then_requires_post(self):
        _, token = self.opened()
        url = self.url("attendance-scan", token)
        self.assertRedirects(self.client.get(url), reverse("login")+"?next="+url)
        response = self.client.post(reverse("login"), {"username": self.student.username, "password": self.password, "next": url})
        self.assertRedirects(response, url)
        self.assertEqual(AttendanceRecord.objects.count(), 0)
        self.assertEqual(self.client.post(url).status_code, 302)

    def test_code_expires_during_login_get_and_post_require_rescan(self):
        _, token = self.opened()
        url = self.url("attendance-scan", token)
        self.client.get(url)
        with patch("classroom.attendance.timezone.now", return_value=self.now+timedelta(seconds=45)):
            self.client.post(reverse("login"), {"username": self.student.username, "password": self.password, "next": url})
            for method in [self.client.get, self.client.post]:
                self.assertContains(method(url), "Scan the current QR again", status_code=410)
        self.assertFalse(AttendanceRecord.objects.exists())

    def test_membership_rechecked_after_login_and_between_get_post(self):
        _, token = self.opened()
        self.client.force_login(self.student)
        url = self.url("attendance-scan", token)
        self.assertEqual(self.client.get(url).status_code, 200)
        Membership.objects.filter(user=self.student).delete()
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url).status_code, 404)
        self.assertFalse(AttendanceRecord.objects.exists())

    def test_window_closed_after_get_rejects_post_and_next_scan_requires_new_code(self):
        _, token = self.opened()
        self.client.force_login(self.student)
        url = self.url("attendance-scan", token)
        self.assertEqual(self.client.get(url).status_code, 200)
        rules.close_window(self.meeting.pk, self.teacher)
        self.assertEqual(self.client.post(url).status_code, 410)
        window = rules.open_window(self.meeting.pk, self.teacher)
        self.assertEqual(self.client.post(self.url("attendance-scan", rules.token_for(window))).status_code, 302)
        record = AttendanceRecord.objects.get()
        self.assertTrue(record.additional)

    def test_feature_pages_render_and_expired_code_rechecks_at_post(self):
        _, token = self.opened()
        self.client.force_login(self.teacher)
        self.assertContains(self.client.get(self.url("attendance")), "Export XLSX snapshot")
        self.assertContains(self.client.get(self.url("meeting-requests")), "All requests")
        self.client.force_login(self.student)
        self.assertContains(self.client.get(self.url("meeting-requests")), "Send a request")
        url = self.url("attendance-scan", token)
        self.assertEqual(self.client.get(url).status_code, 200)
        with patch("classroom.attendance.timezone.now", return_value=self.now+timedelta(seconds=45)):
            self.assertEqual(self.client.post(url).status_code, 410)
        self.assertFalse(AttendanceRecord.objects.exists())

    def test_registration_preserves_first_timestamp_window_and_label(self):
        _, token = self.opened()
        original, created = rules.register(self.meeting.pk, self.student, token)
        self.assertTrue(created)
        rules.close_window(self.meeting.pk, self.teacher)
        second = rules.open_window(self.meeting.pk, self.teacher)
        again, created = rules.register(self.meeting.pk, self.student, rules.token_for(second))
        self.assertFalse(created)
        self.assertEqual((original.pk, original.registered_at, original.window_id, original.additional),
            (again.pk, again.registered_at, again.window_id, again.additional))
        new, _ = rules.register(self.meeting.pk, self.other, rules.token_for(second))
        self.assertEqual(new.registration_label, "Registered in an additional window")
        self.assertEqual(original.registration_label, "Present")

    def test_attendance_roster_and_export_are_lecturer_only_course_scoped(self):
        for user, expected in [(self.student, 403), (self.outsider, 404)]:
            self.client.force_login(user)
            for name in ["attendance", "attendance-state", "attendance-export"]:
                with self.subTest(user=user.username, name=name):
                    self.assertEqual(self.client.get(self.url(name)).status_code, expected)
            for name in ["attendance-open", "attendance-close"]:
                self.assertEqual(self.client.post(self.url(name)).status_code, expected)
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(self.url("attendance", course=self.foreign)).status_code, 404)
        self.assertEqual(self.client.get(self.url("attendance", course=self.foreign, meeting=self.foreign_meeting)).status_code, 403)
        _, token = self.opened()
        self.assertEqual(self.client.post(self.url("attendance-scan", token)).status_code, 403)

    def test_state_svg_roster_no_get_writes_and_cache_disabled(self):
        self.opened()
        self.client.force_login(self.teacher)
        response = self.client.get(self.url("attendance-state"))
        data = response.json()
        self.assertTrue(data["window"]["qr_image"].startswith("data:image/svg+xml;base64,"))
        self.assertEqual({r[0] for r in data["rows"]}, {"student", "other"})
        self.assertEqual({r[6] for r in data["rows"]}, {"Not registered"})
        self.assertIn("no-store", response.headers["Cache-Control"])
        self.assertFalse(AttendanceRecord.objects.exists())
        self.assertEqual(AttendanceWindow.objects.count(), 1)

    def test_export_snapshot_formula_safety_and_additional_label(self):
        self.opened()
        rules.close_window(self.meeting.pk, self.teacher)
        window = rules.open_window(self.meeting.pk, self.teacher)
        rules.register(self.meeting.pk, self.student, rules.token_for(window))
        self.student.first_name = "=HYPERLINK(\"https://example.invalid\")"
        self.student.save()
        self.client.force_login(self.teacher)
        response = self.client.get(self.url("attendance-export"))
        self.assertEqual(response.status_code, 200)
        sheet = load_workbook(BytesIO(response.content))["Attendance"]
        rows = list(sheet.values)
        self.assertEqual(list(rows[0]), rules.HEADERS)
        row_number = next(i for i, row in enumerate(rows, 1) if row[0] == "student")
        self.assertEqual(sheet.cell(row_number, 7).value, "Registered in an additional window")
        self.assertEqual(sheet.cell(row_number, 2).data_type, "s")
        self.assertTrue(sheet.cell(row_number, 2).value.startswith("="))
        rules.register(self.meeting.pk, self.other, rules.token_for(window))
        self.assertEqual(next(r for r in rows if r[0] == "other")[6], "Not registered")
        sheet.cell(row_number, 7).value = "Edited offline"
        self.assertEqual(AttendanceRecord.objects.get(student=self.student).registration_label, "Registered in an additional window")

    def test_all_attendance_writes_require_post_and_csrf(self):
        self.client.force_login(self.teacher)
        for name in ["attendance-open", "attendance-close"]:
            self.assertEqual(self.client.get(self.url(name)).status_code, 405)
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.teacher)
        for name in ["attendance-open", "attendance-close"]:
            self.assertEqual(strict.post(self.url(name)).status_code, 403)
        _, token = self.opened()
        strict.force_login(self.student)
        url = self.url("attendance-scan", token)
        self.assertEqual(strict.post(url).status_code, 403)
        strict.get(url)
        csrf = strict.cookies["csrftoken"].value
        self.assertEqual(strict.post(url, {"csrfmiddlewaretoken": csrf}).status_code, 302)

    def test_requests_bounds_trimmed_unicode_and_idempotent_submission(self):
        self.client.force_login(self.student)
        for text in ["", "   \n", "x"*1001]:
            self.assertEqual(self.post_request(text).status_code, 400)
        for text in [" א ", "🙂"*1000, "Hebrew עברית"]:
            self.assertEqual(self.post_request(text).status_code, 302)
        self.assertEqual(MeetingRequest.objects.count(), 3)
        self.assertTrue(MeetingRequest.objects.filter(text="א").exists())
        nonce = uuid.uuid4()
        self.post_request("Original", nonce=nonce)
        self.post_request("Changed", nonce=nonce)
        self.assertEqual(MeetingRequest.objects.filter(submission_id=nonce).get().text, "Original")

    def test_outside_class_requests_for_past_meeting_persist_for_later_lecturer(self):
        submitted_at=self.now
        self.meeting.starts_at=submitted_at-timedelta(days=7)
        self.meeting.save(update_fields=['starts_at'])
        self.assertFalse(self.meeting.attendance_windows.exists())
        url=self.url('meeting-requests')
        student=Client(enforce_csrf_checks=True)
        student.force_login(self.student)
        form=student.get(url)
        self.assertContains(form,'You can send comments and suggestions during or outside class.')
        texts={'comment':'After-class comment for this past meeting',
               'suggestion':'After-class suggestion for this past meeting'}
        for kind,text in texts.items():
            with self.subTest(kind=kind),patch('classroom.participation_views.timezone.now',return_value=submitted_at):
                nonce=uuid.uuid4()
                response=student.post(url,{'kind':kind,'text':text,'submission_id':nonce,
                    'csrfmiddlewaretoken':student.cookies['csrftoken'].value})
                self.assertRedirects(response,url)
                stored=MeetingRequest.objects.get(submission_id=nonce)
                self.assertEqual((stored.meeting_id,stored.student_id,stored.text,stored.kind,stored.created_at),
                                 (self.meeting.pk,self.student.pk,text,kind,submitted_at))
        student.logout()
        history=Client();history.force_login(self.student)
        for text in texts.values():self.assertContains(history.get(url),text)
        another=Meeting.objects.create(course=self.course,title='Another meeting',starts_at=submitted_at)
        for text in texts.values():self.assertNotContains(history.get(self.url('meeting-requests',meeting=another)),text)
        later=submitted_at+timedelta(days=2)
        with patch('classroom.participation_views.timezone.now',return_value=later):
            lecturer=Client();lecturer.force_login(self.teacher)
            page=lecturer.get(url)
            for text in texts.values():self.assertContains(page,text)
            rows=lecturer.get(self.url('requests-feed')).json()['rows']
            self.assertEqual({row['text'] for row in rows},set(texts.values()))
        other=Client();other.force_login(self.other)
        for text in texts.values():self.assertNotContains(other.get(url),text)
        self.assertEqual(other.get(self.url('requests-feed')).status_code,403)
        self.assertEqual(MeetingRequest.objects.filter(meeting=self.meeting,student=self.student).count(),2)

    def test_requests_history_is_private_feed_is_lecturer_only(self):
        self.client.force_login(self.student)
        self.post_request("Student private")
        self.client.force_login(self.other)
        self.post_request("Other private", kind="comment")
        response = self.client.get(self.url("meeting-requests"))
        self.assertContains(response, "Other private")
        self.assertNotContains(response, "Student private")
        self.assertEqual(self.client.get(self.url("requests-feed")).status_code, 403)
        self.client.force_login(self.teacher)
        self.assertEqual(len(self.client.get(self.url("requests-feed")).json()["rows"]), 2)
        self.assertEqual(self.post_request().status_code, 403)
        self.client.force_login(self.outsider)
        for name in ["meeting-requests", "requests-feed"]:
            self.assertEqual(self.client.get(self.url(name)).status_code, 404)
        self.assertEqual(self.post_request().status_code, 404)

    def test_request_membership_and_role_are_rechecked_each_time(self):
        self.client.force_login(self.student)
        member = Membership.objects.get(user=self.student, course=self.course)
        member.role = "lecturer"
        member.save()
        self.assertEqual(self.post_request().status_code, 403)
        self.assertEqual(self.client.get(self.url("requests-feed")).status_code, 200)
        member.delete()
        self.assertEqual(self.client.get(self.url("requests-feed")).status_code, 404)
        self.assertEqual(self.post_request().status_code, 404)

    def test_requests_csrf_invalid_kind_xss_and_persistence(self):
        self.client.force_login(self.student)
        self.assertEqual(self.post_request(kind="reply").status_code, 400)
        self.assertEqual(self.post_request(text='<script>alert("x")</script>').status_code, 302)
        response = self.client.get(self.url("meeting-requests"))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, '<script>alert("x")</script>')
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.student)
        self.assertEqual(strict.post(self.url("meeting-requests"), {"text": "test", "kind": "comment", "submission_id": uuid.uuid4()}).status_code, 403)

    def test_database_failure_does_not_claim_attendance_or_request_saved(self):
        _, token = self.opened()
        self.client.force_login(self.student)
        with patch("classroom.participation_views.rules.register", side_effect=OperationalError("locked")):
            self.assertContains(self.client.post(self.url("attendance-scan", token)), "could not be confirmed", status_code=503)
        with patch("classroom.participation_views.MeetingRequest.objects.get_or_create", side_effect=OperationalError("locked")):
            self.assertContains(self.post_request(), "could not be confirmed", status_code=503)
        self.assertFalse(AttendanceRecord.objects.exists())
        self.assertFalse(MeetingRequest.objects.exists())


class ParticipationConcurrencyTests(ParticipationFixture, TransactionTestCase):
    def setUp(self):
        if "memory" in connection.settings_dict["NAME"]:
            self.skipTest("Use DJANGO_TEST_SQLITE_NAME with a file-backed SQLite test database for real connection races.")
        self.prepare()

    def race(self, users, name, token=None):
        barrier = Barrier(2, timeout=15)
        url = self.url(name, token)
        def worker(user_id):
            connections.close_all()
            try:
                client = Client()
                client.force_login(get_user_model().objects.get(pk=user_id))
                barrier.wait()
                return client.post(url).status_code
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(worker, [u.pk for u in users]))

    def test_simultaneous_same_student_posts_create_one_record(self):
        _, token = self.opened()
        self.assertEqual(self.race([self.student, self.student], "attendance-scan", token), [302, 302])
        self.assertEqual(AttendanceRecord.objects.count(), 1)

    def test_simultaneous_different_students_both_register(self):
        _, token = self.opened()
        self.assertEqual(self.race([self.student, self.other], "attendance-scan", token), [302, 302])
        self.assertEqual(AttendanceRecord.objects.count(), 2)

    def test_simultaneous_open_posts_keep_one_window(self):
        self.assertEqual(self.race([self.teacher, self.teacher], "attendance-open"), [302, 302])
        self.assertEqual(AttendanceWindow.objects.count(), 1)
