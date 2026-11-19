"""Group workflow/locking tests with injected providers, never model-quality claims."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier
from unittest.mock import patch, MagicMock
import json
import time

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connections, connection
from django.test import TestCase, TransactionTestCase, SimpleTestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone

from . import test_homework as fixtures
from . import test_homework_review as review_fixtures
from .attendance import CourseAccessError
from .homework_batches import prepare_preview, confirm_group, BatchError, SourcesChanged, batch_state, expire_batch_jobs
from .homework_review import request_review, ReviewError, publish
from .homework_services import submit_version
from .homework_worker import process_review_job
from .models import ReviewBatch, ReviewJob, FeedbackDraft, Membership
from .process_lock import WorkerBusy


class GroupProvider(review_fixtures.FakeReviewer):
    busy = False
    reservations = 0

    @contextmanager
    def reserve_resource(self):
        if self.busy:
            raise WorkerBusy('Synthetic busy resource')
        self.reservations += 1
        yield


class BatchFixture(fixtures.HomeworkFixture):
    def seed_group(self):
        self.prepare()
        self.assignment.professional_rubric = 'Accept correct explanations and different approaches.'
        self.assignment.save()
        self.v1 = submit_version(self.meeting, self.assignment.pk, self.student, 'Rollback restores changes in a transaction.')
        self.v2 = submit_version(self.meeting, self.assignment.pk, self.other, 'A lock protects shared capacity.')
        self.fake = GroupProvider()

    def preview(self, owners=None, user=None):
        with patch('classroom.homework_review.get_homework_reviewer', return_value=self.fake):
            return prepare_preview(self.meeting, self.assignment.pk, user or self.teacher,
                                   owners or [self.student.pk, self.other.pk])

    def confirm(self, token=None):
        token = token or self.preview()[1]
        with patch('classroom.homework_review.get_homework_reviewer', return_value=self.fake):
            return confirm_group(self.meeting, self.assignment.pk, self.teacher, token)

    def burl(self, name, batch=None):
        args = [self.course.pk, self.meeting.pk, self.assignment.pk]
        if batch:
            args.append(batch.pk)
        return reverse(name, args=args)


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class HomeworkBatchTests(BatchFixture, TestCase):
    def setUp(self):
        self.seed_group()

    def test_preview_does_not_enqueue_and_confirm_is_atomic_frozen_and_idempotent(self):
        snapshot, token = self.preview()
        self.assertEqual(ReviewJob.objects.count(), 0)
        batch = self.confirm(token)
        self.assertEqual(self.confirm(token).pk, batch.pk)
        self.assertEqual((ReviewBatch.objects.count(), ReviewJob.objects.count()), (1, 2))
        for job in batch.jobs.all():
            self.assertEqual(job.rubric_snapshot, snapshot['rubric'])
            self.assertEqual(len(job.peer_snapshots), 1)
            self.assertNotIn(job.submission.student_id, [p['student_id'] for p in job.peer_snapshots])
        newer = submit_version(self.meeting, self.assignment.pk, self.student, 'A new version after group confirmation.')
        self.assignment.professional_rubric = 'Changed afterwards'; self.assignment.save()
        self.assertEqual(self.confirm(token).pk, batch.pk)
        self.assertNotIn(newer.pk, [s['id'] for s in batch.sources_snapshot])
        self.assertTrue(all(j.rubric_snapshot == snapshot['rubric'] for j in batch.jobs.all()))

    def test_mid_creation_failure_rolls_back_group_and_every_child(self):
        token = self.preview()[1]
        create = ReviewJob.objects.create
        calls = []
        def fail_second(**values):
            calls.append(values)
            if len(calls) == 2:
                raise RuntimeError('Synthetic persistence failure')
            return create(**values)
        with patch.object(ReviewJob.objects, 'create', side_effect=fail_second), self.assertRaises(RuntimeError):
            self.confirm(token)
        self.assertFalse(ReviewBatch.objects.exists())
        self.assertFalse(ReviewJob.objects.exists())

    def test_every_changed_preview_component_requires_reconfirmation(self):
        for field, value, label in [('instructions','Changed instructions','instructions'),
                                    ('criteria',['Changed criterion'],'criteria'),
                                    ('professional_rubric','Changed professional rubric','professional rubric'),
                                    ('feedback_language','he','feedback language')]:
            with self.subTest(field=field):
                self.assignment.refresh_from_db()
                original = getattr(self.assignment, field)
                token = self.preview()[1]
                setattr(self.assignment, field, value); self.assignment.save()
                with self.assertRaisesMessage(SourcesChanged, label): self.confirm(token)
                self.assertFalse(ReviewBatch.objects.exists())
                setattr(self.assignment, field, original); self.assignment.save()
        token = self.preview()[1]
        submit_version(self.meeting, self.assignment.pk, self.student, 'New work before confirmation.')
        with self.assertRaisesMessage(SourcesChanged, 'submitted versions'): self.confirm(token)
        self.assertEqual(self.confirm().jobs.count(), 2)

    def test_sources_changed_view_preserves_selection_and_requires_new_preview(self):
        self.client.force_login(self.teacher)
        token = self.preview()[1]
        self.assignment.instructions = 'Changed instructions'; self.assignment.save()
        page = self.client.post(self.burl('homework-batch-create'), {'action':'confirm','preview_token':token})
        self.assertContains(page, 'Changed since preview: instructions', status_code=409)
        self.assertNotContains(page, 'Confirm and queue all drafts', status_code=409)
        self.assertFalse(ReviewBatch.objects.exists())

    def test_group_excludes_unselected_owner_and_all_self_versions(self):
        third = get_user_model().objects.create_user('unselected')
        Membership.objects.create(user=third, course=self.course, role='student')
        submit_version(self.meeting, self.assignment.pk, third, 'Unselected source text.')
        newer = submit_version(self.meeting, self.assignment.pk, self.student, 'Selected latest owner version.')
        batch = self.confirm()
        self.assertEqual({s['id'] for s in batch.sources_snapshot}, {newer.pk, self.v2.pk})
        for job in batch.jobs.select_related('submission'):
            self.assertTrue(all(p['student_id'] != job.submission.student_id for p in job.peer_snapshots))
            self.assertTrue(all(p['student_id'] != third.pk for p in job.peer_snapshots))

    def test_group_and_input_limits_reject_whole_request(self):
        for owners in [[self.student.pk], [self.student.pk, self.student.pk], [self.student.pk, self.outsider.pk]]:
            with self.subTest(owners=owners), self.assertRaises(BatchError): self.preview(owners)
        submit_version(self.meeting, self.assignment.pk, self.student, 'x'*4001)
        with self.assertRaisesMessage(BatchError, '4,000'): self.preview()
        self.assertFalse(ReviewBatch.objects.exists()); self.assertFalse(ReviewJob.objects.exists())

    def test_four_selected_owners_work_but_five_or_combined_overflow_do_not(self):
        owners = [self.student.pk,self.other.pk]
        for i in range(3):
            user=get_user_model().objects.create_user('selected'+str(i))
            Membership.objects.create(user=user,course=self.course,role='student')
            submit_version(self.meeting,self.assignment.pk,user,'A synthetic alternative.')
            owners.append(user.pk)
        with self.assertRaises(BatchError): self.preview(owners)
        token=self.preview(owners[:4])[1]
        batch=self.confirm(token)
        self.assertEqual(batch.jobs.count(),4)
        self.assertTrue(all(len(job.peer_snapshots)==3 for job in batch.jobs.all()))
        submit_version(self.meeting,self.assignment.pk,self.student,'x'*4000)
        submit_version(self.meeting,self.assignment.pk,self.other,'y'*4000)
        with self.assertRaisesMessage(BatchError,'8,000'): self.preview(owners[:4])

    def test_expired_preview_and_other_lecturer_token_cannot_enqueue(self):
        with patch('django.core.signing.time.time',return_value=1000): token=self.preview()[1]
        with patch('django.core.signing.time.time',return_value=1601),self.assertRaises(BatchError): self.confirm(token)
        token=self.preview()[1]
        teacher=get_user_model().objects.create_user('another_lecturer')
        Membership.objects.create(user=teacher,course=self.course,role='lecturer')
        with self.assertRaisesMessage(BatchError,'does not belong'):
            confirm_group(self.meeting,self.assignment.pk,teacher,token)
        self.assertFalse(ReviewBatch.objects.exists())

    def test_conflict_with_single_request_does_not_create_partial_group(self):
        token = self.preview()[1]
        with patch('classroom.homework_review.get_homework_reviewer', return_value=self.fake):
            existing = request_review(self.v1, self.student)
        with self.assertRaisesMessage(BatchError, 'active review'): self.confirm(token)
        self.assertFalse(ReviewBatch.objects.exists())
        self.assertEqual(list(ReviewJob.objects.values_list('pk', flat=True)), [existing.pk])

    def test_single_overflow_explains_all_peers_and_suggests_group(self):
        for i in range(3):
            user = get_user_model().objects.create_user('extra'+str(i))
            Membership.objects.create(user=user, course=self.course, role='student')
            submit_version(self.meeting, self.assignment.pk, user, 'Another eligible source.')
        with patch('classroom.homework_review.get_homework_reviewer', return_value=self.fake):
            with self.assertRaisesMessage(ReviewError, 'all eligible other students'):
                request_review(self.v1, self.teacher)
        self.assertEqual(self.confirm().jobs.count(), 2)

    def test_busy_waits_without_inference_then_processes_once_when_free(self):
        batch = self.confirm(); job = batch.jobs.first()
        self.fake.busy = True
        self.assertEqual(process_review_job(job.pk, reviewer=self.fake), 'waiting')
        job.refresh_from_db()
        self.assertEqual(job.status, 'queued'); self.assertTrue(job.waiting_for_resource)
        self.assertIsNone(job.started_at); self.assertEqual(self.fake.calls, [])
        self.assertIn('Waiting for shared AI resource', next(row['label'] for row in batch_state(batch)['rows'] if row['id']==job.pk))
        self.fake.busy = False
        process_review_job(job.pk, reviewer=self.fake); process_review_job(job.pk, reviewer=self.fake)
        job.refresh_from_db(); self.assertEqual(job.status, 'ready')
        self.assertFalse(job.waiting_for_resource)
        self.assertEqual([call[0] for call in self.fake.calls], ['individual','comparison'])

    def test_wait_expires_without_worker_and_releases_active_version(self):
        batch = self.confirm(); job = batch.jobs.first()
        batch.queue_expires_at = timezone.now()-timedelta(seconds=1); batch.save()
        job = ReviewJob.objects.select_related('batch').get(pk=job.pk)
        self.assertEqual(job.display_status, 'Queue wait expired')
        self.assertFalse(batch_state(batch)['pending'])
        self.client.force_login(self.teacher)
        state = self.client.get(self.burl('homework-batch-state', batch)).json()
        self.assertEqual((state['failed'],state['pending']), (2,False))
        process_review_job(job.pk, reviewer=self.fake)
        self.assertEqual(self.fake.calls, [])
        self.assertEqual(self.confirm().jobs.count(), 2)

    def test_expiry_rechecked_after_reservation_before_generation(self):
        batch = self.confirm(); job = batch.jobs.first()
        @contextmanager
        def late_reservation():
            ReviewBatch.objects.filter(pk=batch.pk).update(queue_expires_at=timezone.now()-timedelta(seconds=1))
            yield
        with patch.object(self.fake, 'reserve_resource', late_reservation):
            process_review_job(job.pk, reviewer=self.fake)
        job.refresh_from_db(); self.assertEqual(job.error_code, 'queue_timeout')
        self.assertEqual(self.fake.calls, [])

    def test_interrupted_processing_cannot_remain_active_forever_without_worker(self):
        batch=self.confirm(); job=batch.jobs.first()
        ReviewJob.objects.filter(pk=job.pk).update(status='running',started_at=timezone.now()-timedelta(seconds=181))
        self.client.force_login(self.teacher)
        state=self.client.get(self.burl('homework-batch-state',batch)).json()
        job.refresh_from_db()
        self.assertEqual(job.error_code,'processing_timeout')
        self.assertEqual(state['failed'],1)
        self.assertFalse(FeedbackDraft.objects.filter(job=job).exists())

    def test_queue_deadline_does_not_replace_processing_deadline(self):
        batch=self.confirm(); job=batch.jobs.first()
        ReviewBatch.objects.filter(pk=batch.pk).update(queue_expires_at=timezone.now()-timedelta(seconds=1))
        ReviewJob.objects.filter(pk=job.pk).update(status='running',started_at=timezone.now()-timedelta(seconds=1))
        expire_batch_jobs(batch_id=batch.pk)
        job.refresh_from_db(); self.assertEqual(job.status,'running')

    def test_late_result_does_not_save_a_draft_after_processing_deadline(self):
        batch=self.confirm();job=batch.jobs.first()
        original=self.fake.assess_submission
        def late(*args):
            value=original(*args)
            ReviewJob.objects.filter(pk=job.pk).update(started_at=timezone.now()-timedelta(seconds=181))
            return value
        self.fake.assess_submission=late
        process_review_job(job.pk,reviewer=self.fake)
        job.refresh_from_db();self.assertEqual(job.error_code,'processing_timeout')
        self.assertFalse(FeedbackDraft.objects.filter(job=job).exists())

    def test_unavailable_provider_fails_without_reservation_or_inference(self):
        batch=self.confirm();job=batch.jobs.first()
        with patch.object(self.fake,'available',return_value=False),patch.object(self.fake,'reserve_resource') as reserve:
            process_review_job(job.pk,reviewer=self.fake)
        reserve.assert_not_called();self.assertEqual(self.fake.calls,[])
        job.refresh_from_db();self.assertEqual(job.error_code,'provider_unavailable')

    def test_partial_failure_private_drafts_and_separate_publication(self):
        batch = self.confirm(); jobs = list(batch.jobs.order_by('pk'))
        process_review_job(jobs[0].pk, reviewer=GroupProvider(comparison_fail=True))
        process_review_job(jobs[1].pk, reviewer=GroupProvider())
        state = batch_state(batch)
        self.assertEqual((state['ready'],state['partial'],state['failed']), (2,1,0))
        self.client.force_login(self.student)
        page = self.client.get(self.url('homework-submission',self.assignment,self.v1))
        self.assertNotContains(page, 'PRIVATE DRAFT RATIONALE')
        with self.assertRaises(ReviewError): publish(self.meeting,jobs[0].pk,self.teacher,1,'complete')
        publish(self.meeting,jobs[0].pk,self.teacher,1,'individual_only')
        page = self.client.get(self.url('homework-submission',self.assignment,self.v1))
        self.assertContains(page, 'selected demonstration group, not the whole class')
        self.assertContains(page, 'comparison with other submissions could not be completed')
        self.assertFalse(FeedbackDraft.objects.get(job=jobs[1]).published_at)
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get(self.url('homework-submission',self.assignment,self.v2)), 'PRIVATE DRAFT RATIONALE')

    def test_individual_failure_does_not_cancel_other_work(self):
        batch = self.confirm(); jobs = list(batch.jobs.order_by('pk'))
        process_review_job(jobs[0].pk, reviewer=GroupProvider(personal_fail=True))
        process_review_job(jobs[1].pk, reviewer=self.fake)
        self.assertEqual((batch_state(batch)['failed'],batch_state(batch)['ready']), (1,1))
        self.assertFalse(FeedbackDraft.objects.filter(job=jobs[0]).exists())

    def test_permissions_preview_binding_csrf_and_no_snapshot_in_state(self):
        batch = self.confirm(); token = self.preview()[1]
        for user in [self.student,self.other,self.outsider]:
            self.client.force_login(user)
            for name in ['homework-batch-detail','homework-batch-state']:
                self.assertIn(self.client.get(self.burl(name,batch)).status_code,[403,404])
            self.assertIn(self.client.post(self.burl('homework-batch-create'), {'action':'confirm','preview_token':token}).status_code,[403,404])
        self.client.logout(); self.assertEqual(self.client.get(self.burl('homework-batch-detail',batch)).status_code,302)
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.post(self.burl('homework-batch-create'), {'action':'confirm','preview_token':token+'x'}).status_code,400)
        page = self.client.get(self.burl('homework-batch-state',batch))
        self.assertNotContains(page,self.v1.text); self.assertNotContains(page,'rubric_snapshot')
        csrf = Client(enforce_csrf_checks=True); csrf.force_login(self.teacher)
        self.assertEqual(csrf.post(self.burl('homework-batch-create'), {'action':'confirm','preview_token':token}).status_code,403)
        foreign = reverse('homework-batch-detail',args=[self.foreign.pk,self.foreign_meeting.pk,self.assignment.pk,batch.pk])
        self.assertEqual(self.client.get(foreign).status_code,403)

    def test_restart_preserves_queue_deadline_and_fails_only_interrupted_work(self):
        batch = self.confirm(); jobs = list(batch.jobs.order_by('pk'))
        ReviewJob.objects.filter(pk=jobs[0].pk).update(status='running',started_at=timezone.now())
        original_deadline = batch.queue_expires_at
        self.fake.busy = True
        with TemporaryDirectory() as root, override_settings(LOCAL_DIR=Path(root)), patch('classroom.homework_worker.get_homework_reviewer',return_value=self.fake):
            call_command('run_homework_worker',once=True)
        jobs[0].refresh_from_db(); jobs[1].refresh_from_db(); batch.refresh_from_db()
        self.assertEqual((jobs[0].status,jobs[0].error_code),('failed','interrupted'))
        self.assertEqual(jobs[1].status,'queued'); self.assertIsNone(jobs[1].started_at)
        self.assertEqual(batch.queue_expires_at,original_deadline)
        self.assertEqual(self.fake.calls,[])

    def test_revocation_before_processing_does_not_invoke_provider(self):
        batch = self.confirm(); job = batch.jobs.first()
        Membership.objects.filter(course=self.course,user=self.other).delete()
        process_review_job(job.pk,reviewer=self.fake)
        job.refresh_from_db(); self.assertEqual(job.error_code,'access_changed')
        self.assertEqual(self.fake.calls,[])


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class BatchConcurrencyTests(BatchFixture, TransactionTestCase):
    def setUp(self):
        if 'memory' in connection.settings_dict['NAME']:
            self.skipTest('Use the existing file-backed test database setting for connection races.')
        self.seed_group()

    def race(self,tokens):
        barrier = Barrier(2,timeout=15)
        def worker(token):
            connections.close_all()
            try:
                teacher=get_user_model().objects.get(pk=self.teacher.pk)
                barrier.wait()
                try:
                    return confirm_group(self.meeting,self.assignment.pk,teacher,token).pk
                except BatchError:
                    return None
            finally:
                connections.close_all()
        with patch('classroom.homework_review.get_homework_reviewer',return_value=self.fake), ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(worker,tokens))

    def test_parallel_double_confirmation_creates_one_complete_group(self):
        token = self.preview()[1]
        result = self.race([token,token])
        self.assertEqual(result[0],result[1])
        self.assertIsNotNone(result[0])
        self.assertEqual((ReviewBatch.objects.count(),ReviewJob.objects.count()),(1,2))


    def test_different_parallel_groups_cannot_share_active_versions(self):
        result = self.race([self.preview()[1],self.preview()[1]])
        self.assertEqual(sum(value is not None for value in result),1)
        self.assertEqual((ReviewBatch.objects.count(),ReviewJob.objects.count()),(1,2))


class GroupReservationTests(SimpleTestCase):
    def test_parent_reservation_spans_both_child_calls_and_single_route_keeps_its_lock(self):
        from .local_homework_reviewer import LocalHomeworkReviewer
        from .summary_contract import MODEL, WEIGHTS, MANIFEST_SHA256
        provider=LocalHomeworkReviewer();provider.deadline=time.monotonic()+20
        commands=[]
        process=MagicMock();process.pid=123;process.returncode=0;process.poll.return_value=0
        process.communicate.return_value=('{"result":"ok"}\n','')
        def spawn(command,**kwargs):
            commands.append(command)
            output=Path(command[command.index('--output')+1])
            output.write_text(json.dumps({'draft':{'fixture':'test-only'},'metadata':{
                'model':MODEL,'weights_digest':WEIGHTS,'manifest_sha256':MANIFEST_SHA256,'generation_seconds':.01}}),encoding='utf-8')
            return process
        with TemporaryDirectory() as root,override_settings(BASE_DIR=Path(root),LOCAL_DIR=Path(root)),\
                patch('classroom.local_homework_reviewer.ProcessTree'),\
                patch('classroom.local_homework_reviewer.subprocess.Popen',side_effect=spawn):
            with provider.reserve_resource():
                provider.assess_submission('instructions',['criterion'],'target','en')
                with self.assertRaises(WorkerBusy):
                    with LocalHomeworkReviewer().reserve_resource(): pass
                provider.compare_submissions('instructions',['criterion'],'target',['peer'],'en')
                self.assertTrue(all('--resource-reserved' in command for command in commands))
            self.assertFalse(provider.resource_reserved)
            provider.assess_submission('instructions',['criterion'],'target','en')
            self.assertNotIn('--resource-reserved',commands[-1])
