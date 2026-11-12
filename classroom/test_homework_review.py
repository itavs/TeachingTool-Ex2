"""Injected fixtures test workflow, never claim real-model homework quality."""
from unittest.mock import patch
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from .test_homework import HomeworkFixture
from .models import HomeworkAssignment, SubmissionVersion, Membership, ReviewJob, FeedbackDraft
from .homework_services import submit_version
from .homework_review import request_review, publish, edit_draft, ReviewError, COMPARISON_FAILED, NO_PEERS, NO_DIFFERENCE
from .homework_provider import get_homework_reviewer
from .homework_worker import process_review_job

V1='A stack removes the most recently added item first. A pile of plates is an example.'
V2='A stack removes the most recently added item first, like a pile of plates. A queue removes the earliest added item first, like customers waiting at a service desk.'


class FakeReviewer:
    metadata={'provider':'test-double-only'}
    def __init__(self, personal_fail=False, comparison_fail=False, invalid_quote=False, outcome='compared'):
        self.personal_fail=personal_fail;self.comparison_fail=comparison_fail
        self.invalid_quote=invalid_quote;self.outcome=outcome;self.calls=[]

    def available(self,language):return language in ['en','he']

    def assess_submission(self,instructions,criteria,text,language):
        self.calls.append(('individual',text,language))
        if self.personal_fail:raise RuntimeError('Synthetic failure')
        return {'findings':[{'criterion_index':i,'what_student_wrote':'Synthetic test finding.',
                'quotes':['NOT IN THE SOURCE' if self.invalid_quote else text], 'status':'partial',
                'reasoning':f'PRIVATE DRAFT RATIONALE {i}', 'suggested_correction':'Synthetic test recommendation.'}
                for i in range(len(criteria))]}

    def compare_submissions(self,instructions,criteria,target,peers,language):
        self.calls.append(('comparison',list(peers),language))
        if self.comparison_fail:raise RuntimeError('Synthetic comparison failure')
        return {'outcome':self.outcome,'text':'Reviewed anonymous comparison fixture.',
                'evidence':[{'source':'target','peer_index':0,'quote':target},
                            {'source':'peer','peer_index':0,'quote':peers[0]}]}


class HomeworkReviewTests(HomeworkFixture,TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.prepare()
        cls.student.username='student_alex';cls.student.save()
        cls.teacher.username='lecturer_alpha';cls.teacher.save()
        cls.assignment.title='Stacks and queues'
        cls.assignment.instructions='Explain how a stack and a queue remove items. Give one everyday example of each.'
        cls.assignment.criteria=['Explain stack LIFO','Explain queue FIFO','Give one example of each']
        cls.assignment.save()

    def setUp(self):
        self.v1=submit_version(self.meeting,self.assignment.pk,self.student,V1)

    def job_url(self,name,job):
        return reverse(name,args=[self.course.pk,self.meeting.pk,job.pk])

    def request_url(self,submission=None):
        return self.url('homework-review-request',self.assignment,submission or self.v1)

    def make_job(self,fake=None,user=None,submission=None):
        with patch('classroom.homework_review.get_homework_reviewer',return_value=fake or FakeReviewer()):
            return request_review(submission or self.v1,user or self.student)

    def ready(self,fake=None,peer=False):
        if peer:submit_version(self.meeting,self.assignment.pk,self.other,'Private peer source')
        fake=fake or FakeReviewer();job=self.make_job(fake)
        process_review_job(job.pk,reviewer=fake);job.refresh_from_db();return job

    def test_alex_requests_v1_resubmits_v2_then_lecturer_reviews_and_publishes_v1_only(self):
        student=Client(enforce_csrf_checks=True);student.force_login(self.student)
        v1url=self.url('homework-submission',self.assignment,self.v1)
        response=student.get(v1url)
        self.assertContains(response,'Automatic feedback generation is unavailable for English')
        token=student.cookies['csrftoken'].value if 'csrftoken' in student.cookies else None
        # The disabled page has no write form; obtain CSRF from normal assignment form.
        student.get(self.url('homework-detail',self.assignment));token=student.cookies['csrftoken'].value
        fake=FakeReviewer()
        with patch('classroom.homework_review.get_homework_reviewer',return_value=fake):
            response=student.post(self.request_url(),{'csrfmiddlewaretoken':token})
        self.assertEqual(response.status_code,302)
        job=ReviewJob.objects.get();self.assertEqual(job.status,'queued')
        response=student.post(self.url('homework-detail',self.assignment),{'text':V2,'csrfmiddlewaretoken':token})
        self.assertEqual(response.status_code,302)
        v2=self.assignment.submissions.get(student=self.student,version_number=2)
        process_review_job(job.pk,reviewer=fake)
        job.refresh_from_db();self.assertEqual(job.submission_id,self.v1.pk)
        self.assertEqual(job.target_text,V1);self.assertEqual(fake.calls,[('individual',V1,'en')])
        self.assertEqual(job.comparison_status,'no_peers')
        self.assertNotContains(student.get(v1url),'PRIVATE DRAFT RATIONALE')
        self.assertEqual(student.get(self.job_url('homework-review',job)).status_code,403)
        teacher=Client(enforce_csrf_checks=True);teacher.force_login(self.teacher)
        url=self.job_url('homework-review',job);response=teacher.get(url)
        self.assertContains(response,'Lecturer review · Version 1')
        self.assertContains(response,'A newer submitted version exists')
        self.assertContains(response,'PRIVATE DRAFT RATIONALE')
        self.assertNotContains(response,V2)
        csrf=teacher.cookies['csrftoken'].value
        response=teacher.post(url,{'version':job.draft.version,'individual_text':'Lecturer-approved V1 feedback.',
                                  'comparison_text':'','csrfmiddlewaretoken':csrf})
        self.assertEqual(response.status_code,302)
        job.draft.refresh_from_db()
        response=teacher.post(self.job_url('homework-review-publish',job),{'version':job.draft.version,'mode':'complete','csrfmiddlewaretoken':csrf})
        self.assertEqual(response.status_code,302)
        self.assertContains(student.get(v1url),'Lecturer-approved V1 feedback.')
        self.assertContains(student.get(v1url),NO_PEERS)
        self.assertNotContains(student.get(self.url('homework-submission',self.assignment,v2)),'Lecturer-approved V1 feedback.')
        self.assertNotContains(student.get(v1url),'PRIVATE DRAFT RATIONALE')
        self.assertEqual(self.v1.text,V1)

    def test_disabled_language_preflight_and_forged_posts_create_no_request(self):
        for lang,name in [('en','English'),('he','Hebrew')]:
            self.assignment.feedback_language=lang;self.assignment.save()
            for user in [self.student,self.teacher]:
                self.client.force_login(user)
                page=self.client.get(self.url('homework-submission',self.assignment,self.v1))
                self.assertContains(page,f'Automatic feedback generation is unavailable for {name}')
                self.assertNotContains(page,'type="submit">Request feedback')
                response=self.client.post(self.request_url(),follow=True)
                self.assertContains(response,'No request will be created.')
        self.assertEqual(ReviewJob.objects.count(),0)
        with override_settings(HOMEWORK_FAKE_PROVIDER=True):
            self.assertFalse(get_homework_reviewer().available('en'))

    def test_assignment_form_persists_language_but_does_not_enable_generation(self):
        self.client.force_login(self.teacher)
        response=self.client.post(self.url('homework-create'),{'title':'Hebrew target','instructions':'Synthetic instructions',
                                 'criteria':'One criterion','feedback_language':'he'})
        self.assertEqual(response.status_code,302)
        assignment=HomeworkAssignment.objects.get(title='Hebrew target')
        self.assertEqual(assignment.feedback_language,'he')
        self.assertFalse(get_homework_reviewer().available(assignment.feedback_language))
        response=self.client.post(self.url('homework-create'),{'title':'Unsupported','instructions':'x','criteria':'x','feedback_language':'xx'})
        self.assertEqual(response.status_code,200);self.assertFalse(HomeworkAssignment.objects.filter(title='Unsupported').exists())

    def test_lecturer_request_excludes_all_target_owner_versions_and_freezes_latest_peers(self):
        v2=submit_version(self.meeting,self.assignment.pk,self.student,V2)
        submit_version(self.meeting,self.assignment.pk,self.other,'peer old')
        latest=submit_version(self.meeting,self.assignment.pk,self.other,'peer latest')
        foreign=HomeworkAssignment.objects.create(meeting=self.foreign_meeting,created_by=self.teacher,title='Foreign',instructions='x',criteria=['x'])
        SubmissionVersion.objects.create(assignment=foreign,student=self.other,version_number=1,text='foreign source')
        job=self.make_job(user=self.teacher)
        self.assertEqual(job.requester,self.teacher);self.assertEqual(job.submission,self.v1)
        self.assertEqual([p['id'] for p in job.peer_snapshots],[latest.pk])
        self.assertNotIn(v2.pk,[p['id'] for p in job.peer_snapshots])
        submit_version(self.meeting,self.assignment.pk,self.other,'peer future')
        self.assignment.instructions='Changed later';self.assignment.criteria=['changed'];self.assignment.save()
        job.refresh_from_db();self.assertEqual(job.peer_snapshots[0]['text'],'peer latest')
        self.assertNotEqual(job.instructions_snapshot,'Changed later')
        self.assertEqual(len(job.criteria_snapshot),3)

    def test_partial_comparison_failure_requires_explicit_mode_and_correct_student_notice(self):
        job=self.ready(FakeReviewer(comparison_fail=True),peer=True)
        self.assertEqual(job.status,'ready');self.assertEqual(job.comparison_status,'failed')
        self.client.force_login(self.student)
        page=self.client.get(self.url('homework-submission',self.assignment,self.v1))
        self.assertNotContains(page,'PRIVATE DRAFT RATIONALE');self.assertNotContains(page,COMPARISON_FAILED)
        with self.assertRaises(ReviewError):publish(self.meeting,job.pk,self.teacher,job.draft.version,'complete')
        publish(self.meeting,job.pk,self.teacher,job.draft.version,'individual_only')
        page=self.client.get(self.url('homework-submission',self.assignment,self.v1))
        self.assertContains(page,COMPARISON_FAILED)
        self.assertNotContains(page,NO_PEERS);self.assertNotContains(page,NO_DIFFERENCE)
        self.assertNotContains(page,'Private peer source')

    def test_personal_failure_and_invalid_quotes_have_no_publishable_draft(self):
        for fake in [FakeReviewer(personal_fail=True),FakeReviewer(invalid_quote=True)]:
            job=self.make_job(fake);process_review_job(job.pk,reviewer=fake);job.refresh_from_db()
            self.assertEqual(job.status,'failed');self.assertFalse(FeedbackDraft.objects.filter(job=job).exists())
            with self.assertRaises(ReviewError):publish(self.meeting,job.pk,self.teacher,1,'complete')
            self.client.force_login(self.teacher)
            page=self.client.get(self.job_url('homework-review',job))
            self.assertNotContains(page,'name="mode"');self.assertContains(page,'No successful individual draft')

    def test_later_comparison_is_private_until_new_explicit_publication(self):
        job=self.ready(FakeReviewer(comparison_fail=True),peer=True)
        publish(self.meeting,job.pk,self.teacher,job.draft.version,'individual_only')
        later=self.make_job();process_review_job(later.pk,reviewer=FakeReviewer())
        self.client.force_login(self.student);url=self.url('homework-submission',self.assignment,self.v1)
        self.assertContains(self.client.get(url),COMPARISON_FAILED)
        self.assertNotContains(self.client.get(url),'Reviewed anonymous comparison fixture.')
        later.refresh_from_db();publish(self.meeting,later.pk,self.teacher,later.draft.version,'complete')
        self.assertContains(self.client.get(url),'Reviewed anonymous comparison fixture.')
        job.draft.refresh_from_db();self.assertEqual(job.draft.published_comparison_status,'failed')

    def test_no_supported_difference_is_completed_not_failed_or_absent(self):
        job=self.ready(FakeReviewer(outcome='no_difference'),peer=True)
        self.assertEqual(job.comparison_status,'no_difference')
        publish(self.meeting,job.pk,self.teacher,job.draft.version,'complete')
        self.client.force_login(self.student)
        page=self.client.get(self.url('homework-submission',self.assignment,self.v1))
        self.assertContains(page,NO_DIFFERENCE);self.assertNotContains(page,NO_PEERS)
        self.assertNotContains(page,COMPARISON_FAILED)

    def test_stale_edit_and_published_edit_rejected_and_original_model_output_retained(self):
        job=self.ready();version=job.draft.version
        edit_draft(self.meeting,job.pk,self.teacher,{'version':version,'individual_text':'Edited feedback','comparison_text':''})
        with self.assertRaises(ReviewError):edit_draft(self.meeting,job.pk,self.teacher,{'version':version,'individual_text':'stale','comparison_text':''})
        with self.assertRaises(ReviewError):publish(self.meeting,job.pk,self.teacher,version,'complete')
        job.draft.refresh_from_db();publish(self.meeting,job.pk,self.teacher,job.draft.version,'complete')
        job.refresh_from_db();self.assertIn('PRIVATE DRAFT RATIONALE',str(job.generated_individual))
        with self.assertRaises(ReviewError):edit_draft(self.meeting,job.pk,self.teacher,{'version':job.draft.version,'individual_text':'replace','comparison_text':''})

    def test_direct_other_student_nonmember_foreign_course_and_wrong_parent_denied(self):
        job=self.ready()
        for user,status in [(self.other,403),(self.outsider,404)]:
            self.client.force_login(user)
            self.assertEqual(self.client.get(self.job_url('homework-review',job)).status_code,status)
            self.assertIn(self.client.post(self.request_url()).status_code,[404])
            self.assertEqual(self.client.post(self.job_url('homework-review-publish',job),{'version':1,'mode':'complete'}).status_code,status)
        self.client.force_login(self.teacher)
        wrong=reverse('homework-review',args=[self.foreign.pk,self.foreign_meeting.pk,job.pk])
        self.assertEqual(self.client.get(wrong).status_code,403)
        wrong=reverse('homework-review',args=[self.course.pk,self.foreign_meeting.pk,job.pk])
        self.assertEqual(self.client.get(wrong).status_code,404)

    def test_revocation_before_processing_and_publication_cannot_expose_draft(self):
        job=self.make_job()
        Membership.objects.filter(user=self.student,course=self.course).delete()
        process_review_job(job.pk,reviewer=FakeReviewer());job.refresh_from_db()
        self.assertEqual(job.status,'failed');self.assertFalse(FeedbackDraft.objects.filter(job=job).exists())
        Membership.objects.create(user=self.student,course=self.course,role='student')
        job=self.ready();Membership.objects.filter(user=self.teacher,course=self.course).update(role='student')
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.post(self.job_url('homework-review-publish',job),{'version':1,'mode':'complete'}).status_code,403)

    def test_duplicate_active_request_reuses_snapshot_and_no_fake_runtime_setting(self):
        job=self.make_job();again=self.make_job(user=self.teacher)
        self.assertEqual(job.pk,again.pk);self.assertEqual(ReviewJob.objects.count(),1)
        process_review_job(job.pk)  # Normal factory is disabled, not a synthetic fallback.
        job.refresh_from_db();self.assertEqual(job.status,'failed')
        self.assertFalse(FeedbackDraft.objects.filter(job=job).exists())

    def test_published_html_is_escaped_and_contains_no_peer_snapshot_fields(self):
        job=self.ready(peer=True)
        edit_draft(self.meeting,job.pk,self.teacher,{'version':1,'individual_text':'<script>alert(1)</script>','comparison_text':'Anonymous comparison'})
        publish(self.meeting,job.pk,self.teacher,2,'complete')
        self.client.force_login(self.student)
        page=self.client.get(self.url('homework-submission',self.assignment,self.v1))
        self.assertContains(page,'&lt;script&gt;');self.assertNotContains(page,'<script>alert')
        for private in ['Private peer source','peer_snapshots','generated_individual','test-double-only']:
            self.assertNotContains(page,private)

    def test_request_and_publish_require_post_login_and_csrf(self):
        job=self.ready();url=self.job_url('homework-review-publish',job)
        self.assertEqual(self.client.get(url).status_code,302)
        self.client.force_login(self.teacher);self.assertEqual(self.client.get(url).status_code,405)
        client=Client(enforce_csrf_checks=True);client.force_login(self.teacher)
        self.assertEqual(client.post(url,{'version':1,'mode':'complete'}).status_code,403)
        self.assertEqual(client.post(self.request_url()).status_code,403)

    def test_worker_restart_marks_interrupted_job_failed_without_creating_draft(self):
        job=self.make_job();job.status='running';job.save()
        call_command('run_homework_worker',once=True)
        job.refresh_from_db();self.assertEqual(job.status,'failed');self.assertEqual(job.error_code,'interrupted')
        self.assertFalse(FeedbackDraft.objects.filter(job=job).exists())

    def test_invalid_comparison_evidence_keeps_individual_draft_but_not_bad_comparison(self):
        fake=FakeReviewer()
        original=fake.compare_submissions
        def invalid(*args):
            result=original(*args);result['evidence'][1]['quote']='fabricated peer quote';return result
        fake.compare_submissions=invalid
        job=self.ready(fake,peer=True)
        self.assertEqual(job.comparison_status,'failed');self.assertEqual(job.generated_comparison,{})
        self.assertTrue(job.draft.individual_text);self.assertEqual(job.draft.comparison_text,'')
