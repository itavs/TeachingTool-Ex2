"""Rendered markup regressions; no browser rendering or real AI calls."""
from collections import Counter
from html.parser import HTMLParser
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from . import test_homework as fixtures
from . import test_homework_review as review_fixtures
from .homework_review import request_review
from .homework_services import submit_version
from .homework_worker import process_review_job


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.references = []
        self.inputs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for name in ['aria-describedby', 'aria-labelledby']:
            self.references.extend(attrs.get(name, '').split())
        if tag == 'label' and attrs.get('for'):
            self.references.append(attrs['for'])
        if tag == 'input':
            self.inputs.append(attrs)


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class PageIntegrityTests(fixtures.HomeworkFixture, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.prepare()
        cls.assignment.professional_rubric = 'Explain rollback and capacity protection.'
        cls.assignment.save()

    def assert_markup(self, response):
        self.assertEqual(response.status_code, 200)
        parsed = Markup()
        parsed.feed(response.content.decode('utf-8', errors='strict'))
        self.assertFalse([key for key, count in Counter(parsed.ids).items() if count > 1])
        self.assertFalse(set(parsed.references) - set(parsed.ids))
        return parsed

    def test_assignment_help_links_resolve_on_blank_and_invalid_forms(self):
        self.client.force_login(self.teacher)
        url = self.url('homework-create')
        for response in [self.client.get(url), self.client.post(url, {})]:
            with self.subTest(bound=response.context['form'].is_bound):
                markup = self.assert_markup(response)
                self.assertIn('id_criteria_helptext', markup.ids)
                self.assertIn('id_feedback_language_helptext', markup.ids)
                self.assertIn('id_professional_rubric_helptext', markup.ids)

    def test_submission_help_links_resolve_after_validation_error(self):
        self.client.force_login(self.student)
        url = self.url('homework-detail', self.assignment)
        for response in [self.client.get(url), self.client.post(url, {'text': ' '})]:
            self.assertIn('id_text_helptext', self.assert_markup(response).ids)

    def test_review_has_unique_version_ids_help_and_unchanged_publication_payload(self):
        target = submit_version(self.meeting, self.assignment.pk, self.student, 'Rollback restores changes.')
        submit_version(self.meeting, self.assignment.pk, self.other, 'A different synthetic work.')
        fake = review_fixtures.FakeReviewer()
        with patch('classroom.homework_review.get_homework_reviewer', return_value=fake):
            job = request_review(target, self.student)
        process_review_job(job.pk, reviewer=fake)
        job.refresh_from_db()
        self.client.force_login(self.teacher)
        url = reverse('homework-review', args=[self.course.pk, self.meeting.pk, job.pk])
        response = self.client.get(url)
        parsed = self.assert_markup(response)
        versions = [item for item in parsed.inputs if item.get('name') == 'version']
        self.assertEqual({item['id'] for item in versions}, {'id_version', 'publish_version'})
        self.assertEqual([item['value'] for item in versions], ['1', '1'])
        self.assertIn('id_comparison_outcome_helptext', parsed.ids)
        self.assertContains(response, 'Review the generated outcome as well as the comparison text.')
        invalid = self.client.post(url, {'version': 1, 'individual_text': '',
            'comparison_outcome': 'compared', 'evidence-TOTAL_FORMS': 0, 'evidence-INITIAL_FORMS': 0})
        self.assert_markup(invalid)
        publish = reverse('homework-review-publish', args=[self.course.pk, self.meeting.pk, job.pk])
        self.assertEqual(self.client.post(publish, {'version': 1, 'mode': 'complete'}).status_code, 302)
        self.client.force_login(self.student)
        student_page = self.client.get(self.url('homework-submission', self.assignment, target))
        self.assertContains(student_page, 'Current published feedback')
        self.assertNotContains(student_page, 'Private feedback draft')

    def test_poll_index_describes_english_drafts_without_invoking_model(self):
        url = reverse('poll-list', args=[self.course.pk, self.meeting.pk])
        with patch('classroom.local_poll_generator.LocalPollGenerator.generate') as generate:
            self.client.force_login(self.teacher)
            page = self.client.get(url)
            self.assert_markup(page)
            self.assertContains(page, 'Create AI draft')
            self.assertContains(page, 'available in English only')
            self.assertContains(page, 'Review and edit each draft before publishing')
            self.assertNotContains(page, 'not active or verified')
            self.assertNotContains(page, 'Create with AI (not active)')
            self.client.force_login(self.student)
            self.assertNotContains(self.client.get(url), 'Create AI draft')
            generate.assert_not_called()
