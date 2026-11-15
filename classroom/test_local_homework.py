"""Software invariants with injected output; real-model findings are documented separately."""
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.urls import reverse
from .test_homework import HomeworkFixture
from .test_homework_review import FakeReviewer
from .homework_review import request_review, edit_draft, publish, ReviewError
from .homework_worker import process_review_job
from .homework_services import submit_version
from .homework_evidence import annotated_evidence
from .local_homework_reviewer import LocalHomeworkReviewer
from .homework_provider import ReviewUnavailable
import subprocess
import time
from unittest.mock import MagicMock


class LocalHomeworkTests(HomeworkFixture,TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.prepare()
        cls.assignment.professional_rubric='Accept valid alternative approaches. Check source meaning.'
        cls.assignment.save()

    def setUp(self):
        self.v1=submit_version(self.meeting,self.assignment.pk,self.student,'Original own work about transactions.')
        self.fake=FakeReviewer()

    def job(self,peer=False):
        if peer:submit_version(self.meeting,self.assignment.pk,self.other,'Private peer source with a distinct valid approach.')
        with patch('classroom.homework_review.get_homework_reviewer',return_value=self.fake):
            return request_review(self.v1,self.student)

    def url(self,name,job):
        return reverse(name,args=[self.course.pk,self.meeting.pk,job.pk])

    def test_unmatched_quote_remains_private_and_blocks_publish_until_removed_via_form(self):
        self.fake.invalid_quote=True
        job=self.job();process_review_job(job.pk,reviewer=self.fake);job.refresh_from_db()
        self.assertEqual(job.status,'ready')
        self.assertTrue(all(not x['verified'] for x in annotated_evidence(job,job.draft.evidence)))
        with self.assertRaisesMessage(ReviewError,'Unverified evidence'):publish(self.meeting,job.pk,self.teacher,1,'complete')
        self.client.force_login(self.teacher)
        page=self.client.get(self.url('homework-review',job))
        self.assertContains(page,'Unverified — correct or remove')
        payload={'version':1,'individual_text':'Corrected lecturer feedback.','comparison_text':'',
                 'evidence-TOTAL_FORMS':len(job.draft.evidence),'evidence-INITIAL_FORMS':len(job.draft.evidence)}
        for i in range(len(job.draft.evidence)):
            payload.update({f'evidence-{i}-quote':'NOT IN THE SOURCE',f'evidence-{i}-removed':'on'})
        self.assertEqual(self.client.post(self.url('homework-review',job),payload).status_code,302)
        job.draft.refresh_from_db();publish(self.meeting,job.pk,self.teacher,job.draft.version,'complete')
        self.client.force_login(self.student)
        page=self.client.get(self.url_submission())
        self.assertContains(page,'Corrected lecturer feedback.');self.assertNotContains(page,'NOT IN THE SOURCE')

    def url_submission(self):
        return reverse('homework-submission',args=[self.course.pk,self.meeting.pk,self.assignment.pk,self.v1.pk])

    def test_correct_quote_against_frozen_source_not_new_version(self):
        self.fake.invalid_quote=True;job=self.job();process_review_job(job.pk,reviewer=self.fake)
        submit_version(self.meeting,self.assignment.pk,self.student,'New version text')
        draft=job.draft
        edits=[{'quote':'New version text','removed':False} for _ in draft.evidence]
        edit_draft(self.meeting,job.pk,self.teacher,{'version':1,'individual_text':'Reviewed','comparison_text':'','evidence_edits':edits})
        with self.assertRaises(ReviewError):publish(self.meeting,job.pk,self.teacher,2,'complete')
        edits=[{'quote':'Original own work','removed':False} for _ in draft.evidence]
        edit_draft(self.meeting,job.pk,self.teacher,{'version':2,'individual_text':'Reviewed','comparison_text':'','evidence_edits':edits})
        publish(self.meeting,job.pk,self.teacher,3,'complete')

    def test_peer_quote_checked_against_referenced_peer_not_target(self):
        job=self.job(peer=True)
        original=self.fake.compare_submissions
        def bad(*args):
            data=original(*args);data['evidence'][1]['quote']=self.v1.text;return data
        self.fake.compare_submissions=bad
        process_review_job(job.pk,reviewer=self.fake);job.refresh_from_db()
        self.assertEqual(job.comparison_status,'compared')
        self.assertFalse(annotated_evidence(job,job.draft.evidence)[-1]['verified'])
        with self.assertRaises(ReviewError):publish(self.meeting,job.pk,self.teacher,1,'complete')

    def test_privacy_guard_blocks_peer_passage_and_identity_even_after_lecturer_edit(self):
        job=self.job(peer=True);process_review_job(job.pk,reviewer=self.fake)
        for text in [self.other.username,'Private peer source with a distinct valid approach.']:
            draft=job.draft;draft.refresh_from_db()
            edit_draft(self.meeting,job.pk,self.teacher,{'version':draft.version,'individual_text':'Personal', 'comparison_text':text})
            draft.refresh_from_db()
            with self.assertRaises(ReviewError):publish(self.meeting,job.pk,self.teacher,draft.version,'complete')

    def test_rubric_edit_frozen_in_existing_job_and_course_authorized(self):
        job=self.job();old=job.rubric_snapshot
        url=reverse('homework-detail',args=[self.course.pk,self.meeting.pk,self.assignment.pk])
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.post(url,{'action':'rubric','professional_rubric':'Updated rubric'}).status_code,302)
        self.assignment.refresh_from_db();job.refresh_from_db()
        self.assertEqual(self.assignment.professional_rubric,'Updated rubric');self.assertEqual(job.rubric_snapshot,old)
        response=self.client.post(url,{'action':'rubric','professional_rubric':'x'*4001})
        self.assertEqual(response.status_code,200)
        self.assignment.refresh_from_db();self.assertEqual(self.assignment.professional_rubric,'Updated rubric')
        self.client.force_login(self.other)
        self.client.post(url,{'action':'rubric','professional_rubric':'Student mutation'})
        self.assignment.refresh_from_db();self.assertEqual(self.assignment.professional_rubric,'Updated rubric')

    def test_capacity_overflow_rejects_request_without_silent_peer_sampling(self):
        submit_version(self.meeting,self.assignment.pk,self.other,'x'*4001)
        with self.assertRaisesMessage(ReviewError,'capacity'):self.job()
        self.assertEqual(self.v1.review_jobs.count(),0)

    def test_missing_rubric_prevents_waiting_request(self):
        self.assignment.professional_rubric='';self.assignment.save()
        with self.assertRaisesMessage(ReviewError,'rubric'):self.job()

    def test_missing_runtime_and_hebrew_are_not_available(self):
        provider=LocalHomeworkReviewer()
        self.assertFalse(provider.available('he'))
        with override_settings(LOCAL_SUMMARY_MODELS='missing-model'):
            self.assertFalse(provider.available('en'))

    def test_lecturer_can_correct_false_no_difference_outcome_without_rewriting_raw_result(self):
        self.fake.outcome='no_difference';job=self.job(peer=True);process_review_job(job.pk,reviewer=self.fake)
        edit_draft(self.meeting,job.pk,self.teacher,{'version':1,'individual_text':'Reviewed personal',
            'comparison_text':'Your solution uses a different valid approach.','comparison_outcome':'compared'})
        publish(self.meeting,job.pk,self.teacher,2,'complete')
        job.refresh_from_db();job.draft.refresh_from_db()
        self.assertEqual(job.generated_comparison['outcome'],'no_difference')
        self.assertEqual(job.draft.published_comparison_status,'compared')
        self.client.force_login(self.student)
        self.assertNotContains(self.client.get(self.url_submission()),'No supported difference was found')

    def test_provider_timeout_terminates_owned_tree_and_removes_private_ipc(self):
        provider=LocalHomeworkReviewer();provider.deadline=time.monotonic()+1
        fake_process=MagicMock();fake_process.communicate.side_effect=[subprocess.TimeoutExpired('local',1),('','')]
        fake_process.poll.return_value=None
        with patch('classroom.local_homework_reviewer.ProcessTree') as tree,patch('classroom.local_homework_reviewer.subprocess.Popen',return_value=fake_process):
            with self.assertRaises(ReviewUnavailable):provider.assess_submission('x',['x'],'x','en')
            tree.return_value.close.assert_called_once();fake_process.kill.assert_called_once()
