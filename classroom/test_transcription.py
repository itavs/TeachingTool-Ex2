"""Integration/privacy/expiry with injected ASR fixtures, never real inference."""
from datetime import timedelta
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import time
from unittest.mock import patch,Mock
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TransactionTestCase,SimpleTestCase,override_settings
from django.urls import reverse
from django.utils import timezone
from .models import VideoJob,Membership
from .asr_checkpoint import REPO,REVISION,verify_checkpoint
from .test_participation import ParticipationFixture
from .test_videos import make_mp4
from .video_jobs import save_upload,cleanup_video_files,payload
from .video_storage import job_path
from .video_worker import claim_job,process_job
from .local_transcriber import LocalWhisperTranscriber,TranscriptionFailure,validate_result


TEXT='זהו משתנה static במחלקה Car. English term: minimumCarPrice. <script>not executable</script>'


def fixture_result():
    return {'text':TEXT,'segments':[{'start':0.0,'end':.5,'text':TEXT}],'language':'he',
        'model_load_seconds':.1,'transcription_seconds':.5,
        'metadata':{'repo':REPO,'revision':REVISION,'sha256_verified':True,'device':'cuda','compute_type':'float16'}}


class FakeTranscriber:
    """Test only. The normal factory cannot select this class."""
    def transcribe(self,audio_path,*,deadline,on_event,on_tick):
        assert Path(audio_path).is_file(), 'Audio must exist until transcription finishes.'
        assert deadline>time.monotonic()
        on_event({'stage':'loading_asr'})
        on_tick()
        on_event({'stage':'transcribing','model_load_seconds':.1,'model_loaded':fixture_result()['metadata']})
        on_event({'progress_seconds':.5})
        return fixture_result()


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class TranscriptionTests(ParticipationFixture,TransactionTestCase):
    def setUp(self):
        self.prepare()
        self.temp=TemporaryDirectory();self.root=Path(self.temp.name)
        (self.root/'multipart').mkdir()
        self.override=override_settings(VIDEO_STORAGE_ROOT=self.root/'private',FILE_UPLOAD_TEMP_DIR=self.root/'multipart')
        self.override.enable()
        self.media=make_mp4(self.root/'test.mp4')

    def tearDown(self):
        self.override.disable();self.temp.cleanup()

    def new_job(self):
        return save_upload(self.meeting.pk,self.teacher,SimpleUploadedFile('test.mp4',self.media))

    def finish(self):
        job=self.new_job();job=claim_job()
        process_job(job,transcriber=FakeTranscriber())
        job.refresh_from_db();return job

    def url(self,name,job):
        return reverse(name,args=[self.course.pk,self.meeting.pk,job.pk])

    def test_normal_upload_requests_transcription_and_stores_full_result_before_cleanup(self):
        job=self.finish()
        self.assertTrue(job.transcription_requested)
        self.assertEqual(job.asr_metadata['repo'],REPO)
        self.assertEqual(job.asr_metadata['revision'],REVISION)
        self.assertEqual((job.status,job.transcript,job.detected_language),('transcribed',TEXT,'he'))
        self.assertEqual(job.transcript_segments,fixture_result()['segments'])
        self.assertEqual((job.transcript_expires_at-job.transcript_created_at).total_seconds(),7*86400)
        self.assertIsNotNone(job.audio_removed_at)
        self.assertFalse(job_path(job.pk,'audio.wav').exists())
        self.assertFalse(job_path(job.pk,'transcript.pending.json').exists())

    def test_full_transcript_is_private_escaped_and_mixed_language_readable_markup(self):
        job=self.finish();self.client.force_login(self.teacher)
        response=self.client.get(self.url('video-transcript',job))
        self.assertContains(response,'minimumCarPrice')
        self.assertContains(response,'<h1>Automatic transcript</h1>',html=True)
        self.assertContains(response,'Some words and code terms may be transcribed incorrectly.')
        self.assertContains(response,'lang="he" dir="rtl"')
        self.assertContains(response,'&lt;')
        self.assertContains(response,'&gt;')
        self.assertNotContains(response,'<script>not executable</script>')
        self.assertContains(response,'Content shown only on screen is not included.')
        self.assertNotContains(response,'GPU:')
        state=self.client.get(self.url('video-state',job)).json()
        self.assertTrue(state['transcript_available'])
        self.assertNotIn(TEXT,json.dumps(state,ensure_ascii=False))
        Membership.objects.create(user=self.outsider,course=self.course,role='lecturer')
        self.client.force_login(self.outsider)
        self.assertEqual(self.client.get(self.url('video-transcript',job)).status_code,404)
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.url('video-transcript',job)).status_code,403)
        self.client.logout()
        self.assertEqual(self.client.get(self.url('video-transcript',job)).status_code,302)

    def test_demotion_revocation_and_mismatched_parent_block_saved_link(self):
        job=self.finish();self.client.force_login(self.teacher)
        wrong=reverse('video-transcript',args=[self.foreign.pk,self.meeting.pk,job.pk])
        self.assertEqual(self.client.get(wrong).status_code,404)
        Membership.objects.filter(user=self.teacher,course=self.course).update(role='student')
        self.assertEqual(self.client.get(self.url('video-transcript',job)).status_code,403)
        Membership.objects.filter(user=self.teacher,course=self.course).delete()
        self.assertEqual(self.client.get(self.url('video-transcript',job)).status_code,404)

    def test_expiry_blocks_at_exact_deadline_even_before_cleanup(self):
        job=self.finish();self.client.force_login(self.teacher)
        with patch('classroom.video_views.timezone.now',return_value=job.transcript_expires_at-timedelta(microseconds=1)):
            self.assertEqual(self.client.get(self.url('video-transcript',job)).status_code,200)
        with patch('classroom.video_views.timezone.now',return_value=job.transcript_expires_at):
            response=self.client.get(self.url('video-transcript',job))
            self.assertEqual(response.status_code,410)
            self.assertNotIn(TEXT,response.content.decode())
        job.refresh_from_db()
        self.assertEqual((job.transcript,job.transcript_segments),('',[]))
        self.assertIsNotNone(job.transcript_deleted_at)

    def test_maintenance_purges_text_but_keeps_task_and_language_metadata(self):
        job=self.finish()
        cleanup_video_files(job.transcript_expires_at)
        job.refresh_from_db()
        self.assertEqual((job.transcript,job.transcript_segments),('',[]))
        self.assertEqual((job.status,job.detected_language),('transcribed','he'))
        self.assertFalse(payload(job)['transcript_available'])

    def test_legacy_extraction_keeps_original_result_and_no_transcript(self):
        job=self.new_job()
        VideoJob.objects.filter(pk=job.pk).update(transcription_requested=False)
        job=claim_job()
        with patch('classroom.video_worker.get_transcriber',side_effect=AssertionError('No legacy ASR')):
            process_job(job)
        job.refresh_from_db();self.assertEqual((job.status,job.transcript),('extracted',''))
        self.client.force_login(self.teacher)
        self.assertContains(self.client.get(self.url('video-detail',job)),'Audio extraction completed')
        self.assertEqual(self.client.get(self.url('video-transcript',job)).status_code,409)

    def test_unavailable_turbo_fails_clearly_without_fallback(self):
        job=self.new_job()
        self.assertEqual(job.asr_metadata,{'requested_model':{'repo':REPO,'revision':REVISION}})
        job=claim_job()
        with override_settings(LOCAL_ASR_MODEL=self.root/'unavailable-turbo'),patch('classroom.local_transcriber.subprocess.Popen') as spawn:
            process_job(job)
            spawn.assert_not_called()
        job.refresh_from_db()
        self.assertEqual((job.status,job.error_code,job.transcript),('failed','asr_model_missing',''))
        self.client.force_login(self.teacher)
        self.assertContains(self.client.get(self.url('video-detail',job)),'large-v3-turbo')
        self.assertContains(self.client.get(self.url('video-detail',job)),'No other model was used.')

    def test_loaded_model_identity_is_retained_if_inference_fails(self):
        self.new_job();job=claim_job()
        engine=Mock()
        def fail(*args,**kwargs):
            kwargs['on_event']({'stage':'transcribing','model_loaded':fixture_result()['metadata']})
            raise TranscriptionFailure('asr_failed')
        engine.transcribe.side_effect=fail
        process_job(job,transcriber=engine)
        job.refresh_from_db()
        self.assertEqual(job.error_code,'asr_failed')
        self.assertEqual(job.asr_metadata['repo'],REPO)
        self.assertEqual(job.asr_metadata['revision'],REVISION)
        self.assertEqual(job.transcript,'')

    def test_model_failure_cleans_audio_and_never_claims_full_transcript(self):
        job=self.new_job();job=claim_job()
        engine=Mock()
        def fail(*args,**kwargs):
            kwargs['on_event']({'stage':'transcribing'})
            raise TranscriptionFailure('asr_gpu')
        engine.transcribe.side_effect=fail
        process_job(job,transcriber=engine)
        job.refresh_from_db()
        self.assertEqual((job.status,job.failed_stage,job.error_code,job.transcript),('failed','transcribing','asr_gpu',''))
        self.assertFalse(job_path(job.pk,'audio.wav').exists())

    def test_total_deadline_is_not_reset_at_transcription_start(self):
        self.new_job();job=claim_job();seen=[]
        class DeadlineEngine(FakeTranscriber):
            def transcribe(self,audio_path,**kwargs):
                seen.append(kwargs['deadline']-time.monotonic())
                self_outer.assertLess(seen[0],599.5)
                raise TranscriptionFailure('timeout')
        self_outer=self
        # Persist a start one second earlier; ASR must inherit that consumed time.
        VideoJob.objects.filter(pk=job.pk).update(started_at=job.started_at-timedelta(seconds=1))
        job.refresh_from_db()
        process_job(job,transcriber=DeadlineEngine())
        self.assertTrue(seen)
        job.refresh_from_db();self.assertEqual(job.error_code,'timeout')

    def test_invalid_result_not_saved_and_revoked_role_after_asr_cannot_publish_text(self):
        self.new_job();job=claim_job()
        bad=Mock();bad.transcribe.return_value={'text':'unfinished'}
        process_job(job,transcriber=bad)
        job.refresh_from_db();self.assertEqual(job.error_code,'asr_output')
        self.new_job();second=claim_job()
        class RevokeEngine(FakeTranscriber):
            def transcribe(inner,*args,**kwargs):
                result=super().transcribe(*args,**kwargs)
                Membership.objects.filter(user=self.teacher,course=self.course).delete()
                return result
        process_job(second,transcriber=RevokeEngine())
        second.refresh_from_db()
        self.assertEqual(second.transcript,'')
        self.assertEqual(second.error_code,'permission_revoked')

    def test_adapter_missing_runtime_does_not_download_or_spawn(self):
        with override_settings(LOCAL_ASR_PYTHON=self.root/'absent.exe'),patch('classroom.local_transcriber.subprocess.Popen') as spawn:
            with self.assertRaises(TranscriptionFailure):
                LocalWhisperTranscriber().transcribe(self.root/'audio.wav',deadline=time.monotonic()+10,on_event=lambda x:None,on_tick=lambda:None)
            spawn.assert_not_called()

    def test_adapter_protocol_keeps_text_off_stdout_and_forces_offline_environment(self):
        runtime=self.root/'python.exe';runtime.write_bytes(b'test-only')
        model=self.root/'model';model.mkdir()
        audio=self.root/'audio.wav';audio.write_bytes(b'test-only')
        output=audio.with_name('transcript.pending.json')
        process=Mock(stdout=StringIO('{"stage":"loading_asr"}\n{"stage":"transcribing"}\n{"result":"ok"}\n'),returncode=0)
        process.poll.return_value=0
        def spawn(*args,**kwargs):
            output.write_text(json.dumps(fixture_result(),ensure_ascii=False),encoding='utf-8')
            self.assertEqual(kwargs['env']['HF_HUB_OFFLINE'],'1')
            self.assertNotIn('http',str(args))
            return process
        with override_settings(LOCAL_ASR_PYTHON=runtime,LOCAL_ASR_MODEL=model),patch('classroom.local_transcriber.subprocess.Popen',side_effect=spawn):
            result=LocalWhisperTranscriber().transcribe(audio,deadline=time.monotonic()+10,on_event=lambda x:None,on_tick=lambda:None)
        self.assertEqual(result['text'],TEXT)
        self.assertFalse(output.exists())

    def test_invalid_language_empty_text_or_nan_timing_rejected(self):
        for changes in [{'text':''},{'language':'fr'},{'model_load_seconds':float('nan')},{'segments':[{'start':2,'end':1,'text':'x'}]}]:
            with self.assertRaises(TranscriptionFailure):validate_result({**fixture_result(),**changes})


class TranscriptDisplayTests(SimpleTestCase):
    def test_pause_boundaries_preserve_words_and_isolate_new_car(self):
        from .transcript_display import reading_paragraphs
        segments = [
            {'start':0,'end':3,'text':'עכשיו יוצרים New Car בתוך המחלקה.'},
            {'start':4,'end':7,'text':'המשך ההסבר המקורי.'},
        ]
        text = ' '.join(s['text'] for s in segments)
        paragraphs = reading_paragraphs(text, segments)
        self.assertEqual(len(paragraphs), 2)
        self.assertEqual(' '.join(''.join(r['text'] for r in p) for p in paragraphs),text)
        self.assertIn({'text':'New Car','latin':True},paragraphs[0])

    def test_unmatched_legacy_segments_do_not_replace_text(self):
        from .transcript_display import reading_paragraphs
        original = 'Original <text> dishwasher \ufffd'
        paragraphs = reading_paragraphs(original, [])
        self.assertEqual(''.join(r['text'] for r in paragraphs[0]), original)

    def test_long_speech_is_grouped_at_segment_boundaries(self):
        from .transcript_display import reading_paragraphs
        segments=[{'start':i*10,'end':(i+1)*10,'text':'Original words.'} for i in range(9)]
        text=' '.join(s['text'] for s in segments)
        paragraphs=reading_paragraphs(text,segments)
        self.assertGreater(len(paragraphs),1)
        self.assertEqual(' '.join(''.join(r['text'] for r in p) for p in paragraphs),text)


class CheckpointIdentityTests(SimpleTestCase):
    def test_checkpoint_verification_rejects_missing_or_changed_files(self):
        import hashlib
        with TemporaryDirectory() as directory:
            file=Path(directory)/'model.bin'
            expected={'model.bin':hashlib.sha256(b'approved-test-checkpoint').hexdigest()}
            with patch('classroom.asr_checkpoint.FILE_SHA256',expected):
                with self.assertRaises(OSError):verify_checkpoint(directory)
                file.write_bytes(b'approved-test-checkpoint')
                verify_checkpoint(directory)
                file.write_bytes(b'other-model')
                with self.assertRaises(ValueError):verify_checkpoint(directory)

    def test_result_from_another_model_or_revision_is_rejected(self):
        for change in [{'repo':'Systran/faster-whisper-medium'},{'revision':'other'},{'sha256_verified':False}]:
            result=fixture_result()
            result['metadata']={**result['metadata'],**change}
            with self.assertRaises(TranscriptionFailure):validate_result(result)
