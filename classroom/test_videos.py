"""Video pipeline tests: generated real media, private isolated storage, no AI."""
from datetime import timedelta
from fractions import Fraction
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import multiprocessing as mp
import os
import time
import uuid
import wave
import av
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import StopUpload
from django.core.management import call_command
from django.db import connection
from django.test import Client,TransactionTestCase,override_settings
from django.urls import reverse
from django.utils import timezone
from .models import VideoJob,Membership
from .test_participation import ParticipationFixture
from .video_jobs import save_upload,cleanup_video_files,recover_jobs,payload,fail_job
from .video_media import inspect_mp4,extract_audio,MediaFailure
from .video_storage import job_path,exclusive_lock,WorkerBusy,remove_file
from .video_uploads import BoundedUploadHandler
from .video_worker import claim_job,process_job,run_worker
from .video_engines import get_transcriber,get_summarizer,EngineUnavailable
from tests_support.video_children import waiting_child,test_worker_process


def make_mp4(path, *, audio=True, video=True):
    with av.open(str(path),'w',format='mp4') as out:
        v=out.add_stream('mpeg4',rate=5) if video else None
        a=out.add_stream('aac',rate=16000) if audio else None
        if v:
            v.width=64;v.height=48;v.pix_fmt='yuv420p'
        if a: a.layout='mono'
        if v:
            for i in range(3):
                frame=av.VideoFrame(64,48,'yuv420p');frame.pts=i;frame.time_base=Fraction(1,5)
                for plane in frame.planes:plane.update(bytes(plane.buffer_size))
                for packet in v.encode(frame):out.mux(packet)
            for packet in v.encode(None):out.mux(packet)
        if a:
            for i in range(10):
                frame=av.AudioFrame(format='fltp',layout='mono',samples=1024)
                frame.sample_rate=16000;frame.pts=i*1024;frame.time_base=Fraction(1,16000)
                for plane in frame.planes:plane.update(bytes(plane.buffer_size))
                for packet in a.encode(frame):out.mux(packet)
            for packet in a.encode(None):out.mux(packet)
    return Path(path).read_bytes()


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class VideoTests(ParticipationFixture,TransactionTestCase):
    def setUp(self):
        self.prepare()
        self.directory=TemporaryDirectory()
        self.root=Path(self.directory.name)
        self.override=override_settings(VIDEO_STORAGE_ROOT=self.root/'private',FILE_UPLOAD_TEMP_DIR=self.root/'multipart')
        self.override.enable()
        (self.root/'multipart').mkdir()
        self.valid=make_mp4(self.root/'fixture.mp4')

    def tearDown(self):
        self.override.disable();self.directory.cleanup()

    def vurl(self,name,job=None,course=None,meeting=None):
        args=[(course or self.course).pk,(meeting or self.meeting).pk]
        if name!='video-list':args.append((job.pk if job else uuid.uuid4()))
        return reverse(name,args=args)

    def upload(self,data=None,name='example.mp4'):
        return SimpleUploadedFile(name,self.valid if data is None else data,content_type='video/mp4')

    def queued(self,data=None):
        return save_upload(self.meeting.pk,self.teacher,self.upload(data))

    def test_upload_returns_queued_task_with_private_streamed_file(self):
        self.client.force_login(self.teacher)
        response=self.client.post(self.vurl('video-list'),{'video':self.upload()})
        self.assertEqual(response.status_code,302)
        job=VideoJob.objects.get()
        self.assertEqual(job.status,'queued');self.assertIsNone(job.started_at)
        self.assertEqual(job.owner,self.teacher)
        self.assertEqual(job_path(job.pk,'input.mp4').read_bytes(),self.valid)
        self.assertEqual((job.source_expires_at-job.created_at).total_seconds(),86400)
        self.assertContains(self.client.get(self.vurl('video-list')),'4 minutes')
        self.assertContains(self.client.get(self.vurl('video-list')),'200 MB')
        self.assertContains(self.client.get(self.vurl('video-detail',job)),'Waiting for worker')
        self.assertNotContains(self.client.get(self.vurl('video-detail',job)),str(settings.VIDEO_STORAGE_ROOT))
        self.assertEqual(self.client.get(reverse('course-list')).status_code,200)

    def test_real_decode_extract_and_cleanup_through_worker(self):
        self.queued()
        run_worker(once=True)
        job=VideoJob.objects.get()
        self.assertEqual((job.status,job.error_code),('extracted',''))
        self.assertGreater(job.audio_samples,0);self.assertGreater(job.audio_seconds,0)
        self.assertIsNotNone(job.started_at);self.assertIsNotNone(job.finished_at)
        self.assertFalse(job_path(job.pk,'audio.wav').exists())
        self.assertTrue(job_path(job.pk,'input.mp4').exists())
        self.client.force_login(self.teacher)
        self.assertContains(self.client.get(self.vurl('video-detail',job)),'Audio extraction completed')

    def test_direct_extraction_creates_verified_16khz_mono_wav(self):
        source=self.root/'fixture.mp4';output=self.root/'real.wav'
        metadata=inspect_mp4(source)
        result=extract_audio(source,output)
        with wave.open(str(output)) as audio:
            self.assertEqual((audio.getnchannels(),audio.getsampwidth(),audio.getframerate()),(1,2,16000))
            self.assertEqual(audio.getnframes(),result['audio_samples'])
        self.assertGreater(metadata['video_seconds'],0)

    def test_corrupt_no_audio_and_audio_only_are_failed_by_worker(self):
        cases=[(b'not mp4','invalid_mp4'),(make_mp4(self.root/'silent.mp4',audio=False),'no_audio'),
            (make_mp4(self.root/'audio-only.mp4',video=False),'no_video')]
        for data,code in cases:
            job=self.queued(data);run_worker(once=True);job.refresh_from_db()
            self.assertEqual((job.status,job.failed_stage,job.error_code),('failed','validating',code))
            self.assertFalse(job_path(job.pk,'audio.wav').exists())

    def test_duration_limit_is_server_enforced_with_real_media(self):
        job=self.queued()
        with override_settings(VIDEO_MAX_SECONDS=.2):run_worker(once=True)
        job.refresh_from_db();self.assertEqual(job.error_code,'too_long')
        actual=inspect_mp4(self.root/'fixture.mp4')['video_seconds']
        self.assertEqual(inspect_mp4(self.root/'fixture.mp4',actual)['video_seconds'],actual)
        with self.assertRaises(MediaFailure):inspect_mp4(self.root/'fixture.mp4',actual-.001)

    def test_size_handler_boundary_and_real_http_abort(self):
        self.assertEqual(settings.VIDEO_MAX_BYTES,200_000_000)
        request=SimpleNamespace();handler=BoundedUploadHandler(request)
        with override_settings(VIDEO_MAX_BYTES=4):
            self.assertEqual(handler.receive_data_chunk(b'1234',0),b'1234')
            with self.assertRaises(StopUpload):handler.receive_data_chunk(b'5',4)
        self.assertIn('200 MB',request.video_upload_error)
        self.client.force_login(self.teacher)
        with override_settings(VIDEO_MAX_BYTES=len(self.valid)-1):
            self.assertEqual(self.client.post(self.vurl('video-list'),{'video':self.upload()}).status_code,413)
        self.assertFalse(VideoJob.objects.exists())

    def test_declared_and_actual_upload_sizes_are_both_checked(self):
        fake=SimpleNamespace(name='x.mp4',size=200_000_001,chunks=lambda:iter([b'x']))
        with self.assertRaises(ValidationError):save_upload(self.meeting.pk,self.teacher,fake)
        self.assertFalse(VideoJob.objects.exists())
        fake=SimpleNamespace(name='x.mp4',size=1,chunks=lambda:iter([b'1234',b'5']))
        with override_settings(VIDEO_MAX_BYTES=4),self.assertRaises(ValidationError):
            save_upload(self.meeting.pk,self.teacher,fake)
        job=VideoJob.objects.get();self.assertEqual(job.status,'failed')
        self.assertFalse(job_path(job.pk,'input.mp4').exists())

    def test_authorization_owner_lecturer_and_parent_scoping(self):
        job=self.queued()
        Membership.objects.create(user=self.outsider,course=self.course,role='lecturer')
        self.client.force_login(self.outsider)
        for name in ['video-detail','video-state']:
            self.assertEqual(self.client.get(self.vurl(name,job)).status_code,404)
        self.assertNotContains(self.client.get(self.vurl('video-list')),job.original_name)
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.vurl('video-detail',job)).status_code,403)
        self.assertEqual(self.client.post(self.vurl('video-list'),{'video':self.upload()}).status_code,403)
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(self.vurl('video-state',job,course=self.foreign)).status_code,404)
        Membership.objects.filter(user=self.teacher,course=self.course).update(role='student')
        self.assertEqual(self.client.get(self.vurl('video-state',job)).status_code,403)
        Membership.objects.filter(user=self.teacher,course=self.course).delete()
        self.assertEqual(self.client.get(self.vurl('video-detail',job)).status_code,404)

    def test_queued_role_revocation_prevents_decoding(self):
        job=self.queued();Membership.objects.filter(user=self.teacher,course=self.course).delete()
        run_worker(once=True);job.refresh_from_db()
        self.assertEqual(job.error_code,'permission_revoked')

    def test_csrf_login_bad_extension_and_multiple_files(self):
        self.assertEqual(self.client.get(self.vurl('video-list')).status_code,302)
        strict=Client(enforce_csrf_checks=True);strict.force_login(self.teacher)
        self.assertEqual(strict.post(self.vurl('video-list'),{'video':self.upload()}).status_code,403)
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.post(self.vurl('video-list'),{'video':self.upload(name='x.mov')}).status_code,400)
        self.assertEqual(self.client.post(self.vurl('video-list'),{'video':[self.upload(),self.upload()]}).status_code,400)

    def test_queue_wait_does_not_consume_processing_budget(self):
        job=self.queued()
        VideoJob.objects.filter(pk=job.pk).update(created_at=timezone.now()-timedelta(hours=1),queued_at=timezone.now()-timedelta(hours=1))
        job=claim_job()
        self.assertEqual(job.status,'validating')
        self.assertGreater(payload(job)['waiting_seconds'],3590)
        self.assertLess(payload(job)['processing_seconds'],2)
        process_job(job)
        job.refresh_from_db();self.assertEqual(job.status,'extracted')

    def test_timeout_terminates_actual_subprocess_and_removes_audio(self):
        self.queued();job=claim_job()
        job_path(job.pk,'audio.wav').write_bytes(b'partial')
        process_job(job,timeout_seconds=.15,child_target=waiting_child)
        job.refresh_from_db();self.assertEqual(job.error_code,'timeout')
        self.assertFalse(job_path(job.pk,'audio.wav').exists())

    def test_graceful_stop_and_stale_heartbeat_are_not_stuck_active(self):
        self.queued();job=claim_job()
        process_job(job,stop_requested=lambda:True)
        job.refresh_from_db();self.assertEqual(job.error_code,'interrupted')
        another=self.queued();another=claim_job()
        VideoJob.objects.filter(pk=another.pk).update(heartbeat_at=timezone.now()-timedelta(seconds=31))
        job_path(another.pk,'audio.wav').write_bytes(b'partial')
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(self.vurl('video-state',another)).json()['status'],'failed')
        self.assertFalse(job_path(another.pk,'audio.wav').exists())

    def test_persisted_ten_minute_deadline_and_restart_recovery(self):
        self.queued();job=claim_job()
        VideoJob.objects.filter(pk=job.pk).update(started_at=timezone.now()-timedelta(seconds=601))
        recover_jobs();job.refresh_from_db();self.assertEqual(job.error_code,'timeout')
        another=self.queued();claim_job()
        run_worker(once=True) # Fresh OS lock proves prior coordinator is absent.
        another.refresh_from_db();self.assertEqual(another.error_code,'interrupted')

    def test_single_worker_lock_and_fifo(self):
        a=self.queued();b=self.queued()
        lock=Path(settings.VIDEO_STORAGE_ROOT)/'.worker.lock'
        with exclusive_lock(lock),self.assertRaises(WorkerBusy):run_worker(once=True)
        run_worker(once=True);a.refresh_from_db();b.refresh_from_db()
        self.assertEqual((a.status,b.status),('extracted','queued'))

    def test_expired_sources_and_orphan_temp_cleanup(self):
        job=self.queued();now=timezone.now()
        VideoJob.objects.filter(pk=job.pk).update(source_expires_at=now+timedelta(minutes=4))
        cleanup_video_files(now);job.refresh_from_db()
        self.assertEqual((job.status,job.error_code),('failed','expired'))
        self.assertIsNotNone(job.source_deleted_at)
        self.assertFalse(job_path(job.pk,'input.mp4').exists())
        unknown=uuid.uuid4();path=job_path(unknown,'audio.wav');path.parent.mkdir();path.write_bytes(b'orphan')
        os.utime(path.parent,(now.timestamp()-200,now.timestamp()-200))
        temp=Path(settings.FILE_UPLOAD_TEMP_DIR)/'test.upload.mp4';temp.write_bytes(b'temp')
        os.utime(temp,(now.timestamp()-86400,now.timestamp()-86400))
        cleanup_video_files(now)
        self.assertFalse(path.exists());self.assertFalse(temp.exists())

    def test_paths_do_not_allow_traversal_or_delete_unrelated_files(self):
        with self.assertRaises(ValueError):job_path('../escape','input.mp4')
        with self.assertRaises(ValueError):job_path(uuid.uuid4(),'../outside')
        unrelated=Path(settings.VIDEO_STORAGE_ROOT)/'unrelated.txt'
        unrelated.parent.mkdir(exist_ok=True);unrelated.write_text('keep')
        cleanup_video_files();self.assertTrue(unrelated.exists())

    def test_ai_contracts_disabled_and_not_called_on_success(self):
        with self.assertRaises(EngineUnavailable):get_transcriber().transcribe('unused')
        with self.assertRaises(EngineUnavailable):get_summarizer().summarize('unused','he')
        self.queued()
        with patch('classroom.video_engines.get_transcriber',side_effect=AssertionError('AI forbidden')),patch('classroom.video_engines.get_summarizer',side_effect=AssertionError('AI forbidden')):
            run_worker(once=True)
        self.assertEqual(VideoJob.objects.get().status,'extracted')

    def test_maintenance_command_runs_independently(self):
        job=self.queued()
        VideoJob.objects.filter(pk=job.pk).update(source_expires_at=timezone.now())
        call_command('run_video_maintenance',once=True,stdout=StringIO())
        job.refresh_from_db();self.assertIsNotNone(job.source_deleted_at)

    def test_hard_stopped_worker_is_recovered_and_decoder_does_not_orphan(self):
        if 'memory' in connection.settings_dict['NAME']:
            self.skipTest('Hard-stop recovery needs the file-backed test database.')
        job=self.queued()
        context=mp.get_context('spawn')
        process=context.Process(target=test_worker_process,args=(str(connection.settings_dict['NAME']),str(settings.VIDEO_STORAGE_ROOT),str(settings.FILE_UPLOAD_TEMP_DIR)))
        process.start()
        try:
            deadline=time.monotonic()+15
            while time.monotonic()<deadline:
                job.refresh_from_db()
                if job.status=='extracting' and job_path(job.pk,'audio.wav').exists():break
                time.sleep(.05)
            self.assertEqual(job.status,'extracting')
            process.terminate();process.join(3)
            # The decoder's own parent watchdog releases its OS lock after hard kill.
            released=False
            for _ in range(80):
                try:
                    with exclusive_lock(Path(settings.VIDEO_STORAGE_ROOT)/'.decoder.lock'):released=True
                    break
                except WorkerBusy:time.sleep(.05)
            self.assertTrue(released)
            VideoJob.objects.filter(pk=job.pk).update(heartbeat_at=timezone.now()-timedelta(seconds=31))
            cleanup_video_files();job.refresh_from_db()
            self.assertEqual((job.status,job.error_code),('failed','interrupted'))
            self.assertFalse(job_path(job.pk,'audio.wav').exists())
        finally:
            if process.is_alive():process.terminate()
            process.join(3)
