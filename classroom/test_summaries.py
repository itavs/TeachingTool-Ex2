"""Summary integration uses test-only injected engines, never a real model."""
from datetime import timedelta
from io import StringIO
import json
from pathlib import Path
import time
from unittest.mock import Mock, patch
from django.test import TransactionTestCase, SimpleTestCase, override_settings
from django.utils import timezone
from .test_participation import ParticipationFixture
from . import test_transcription as transcription_fixture
from .models import VideoJob, Membership
from .video_jobs import transcript_available, summary_available, cleanup_video_files, payload
from .video_storage import job_path
from .video_worker import process_job, claim_job
from .local_summarizer import LocalQwenSummarizer, SummaryFailure, validate_result
from .summary_contract import MODEL, WEIGHTS, MANIFEST_SHA256, PROMPT_VERSION, summary_prompt, validate_summary


def result():
    return {'paragraph':'לכל אובייקט משתנים נפרדים. משתנה static משותף בדוגמה.',
            'key_points':['משתנים נפרדים לכל אובייקט.','בדוגמה משתנה משותף.','אין ניתוח חזותי.'],
            'metadata':{'model':MODEL,'weights_digest':WEIGHTS,'manifest_sha256':MANIFEST_SHA256,'prompt_version':PROMPT_VERSION},
            'summary_seconds':.2}


class FakeSummarizer:
    def summarize(self,text,language,*,work_dir,deadline,on_event,on_tick):
        job=VideoJob.objects.get(pk=Path(work_dir).name)
        assert job.transcript==text and transcript_available(job)
        assert not (Path(work_dir)/'audio.wav').exists()
        assert time.monotonic()<deadline
        on_event({'stage':'summarizing','model_loaded':result()['metadata']})
        on_tick()
        return result()


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class SummaryTests(ParticipationFixture,TransactionTestCase):
    setUp=transcription_fixture.TranscriptionTests.setUp
    tearDown=transcription_fixture.TranscriptionTests.tearDown
    url=transcription_fixture.TranscriptionTests.url

    def new_job(self):
        job=transcription_fixture.TranscriptionTests.new_job(self)
        VideoJob.objects.filter(pk=job.pk).update(summary_requested=True)
        job.refresh_from_db();return job

    def finish(self,engine=None):
        self.new_job();job=claim_job()
        process_job(job,transcriber=transcription_fixture.FakeTranscriber(),summarizer=engine or FakeSummarizer())
        job.refresh_from_db();return job

    def test_full_lifecycle_stores_transcript_first_then_summary_with_shared_expiry(self):
        job=self.finish()
        self.assertEqual(job.status,'summarized')
        self.assertEqual(job.summary_paragraph,result()['paragraph'])
        self.assertEqual(job.summary_points,result()['key_points'])
        self.assertEqual(job.summary_expires_at,job.transcript_expires_at)
        self.assertTrue(transcript_available(job));self.assertTrue(summary_available(job))
        self.assertFalse(job_path(job.pk,'summary.input.json').exists())
        self.assertFalse(job_path(job.pk,'summary.pending.json').exists())

    def test_owner_summary_page_escapes_content_and_excludes_text_from_status_json(self):
        job=self.finish();self.client.force_login(self.teacher)
        VideoJob.objects.filter(pk=job.pk).update(summary_paragraph='<script>unsafe</script> תוצאה')
        page=self.client.get(self.url('video-detail',job))
        self.assertContains(page,'Automatic summary');self.assertContains(page,'&lt;script&gt;')
        self.assertContains(page,'This summary is based on an automatic transcript and may contain errors.')
        self.assertContains(page,'Open full transcript')
        state=self.client.get(self.url('video-state',job)).json()
        self.assertTrue(state['summary_available']);self.assertNotIn('summary_paragraph',state)
        Membership.objects.create(user=self.outsider,course=self.course,role='lecturer')
        self.client.force_login(self.outsider)
        self.assertEqual(self.client.get(self.url('video-detail',job)).status_code,404)
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.url('video-state',job)).status_code,403)
        Membership.objects.filter(user=self.teacher,course=self.course).update(role='student')
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(self.url('video-detail',job)).status_code,403)

    def test_summary_failure_keeps_saved_transcript_accessible(self):
        engine=Mock();engine.summarize.side_effect=SummaryFailure('summary_model')
        job=self.finish(engine)
        self.assertEqual((job.status,job.failed_stage,job.error_code),('failed','loading_sum','summary_model'))
        self.assertTrue(transcript_available(job));self.assertFalse(summary_available(job))
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(self.url('video-transcript',job)).status_code,200)
        self.assertContains(self.client.get(self.url('video-detail',job)),'Qwen3 8B')

    def test_unexpected_summary_error_has_summary_reason_and_preserves_text(self):
        engine=Mock();engine.summarize.side_effect=RuntimeError('private implementation detail')
        job=self.finish(engine)
        self.assertEqual(job.error_code,'summary_failed')
        self.assertTrue(transcript_available(job))
        self.client.force_login(self.teacher)
        response=self.client.get(self.url('video-detail',job))
        self.assertContains(response,'Local summarization failed')
        self.assertNotContains(response,'private implementation detail')

    def test_interruption_and_timeout_during_summary_retain_transcript_and_budget(self):
        for code in ['timeout','interrupted']:
            engine=Mock()
            def fail(text,language,**kwargs):
                self.assertLess(kwargs['deadline']-time.monotonic(),600)
                kwargs['on_event']({'stage':'summarizing'})
                raise SummaryFailure(code)
            engine.summarize.side_effect=fail
            job=self.finish(engine)
            self.assertEqual((job.failed_stage,job.error_code),('summarizing',code))
            self.assertTrue(transcript_available(job));self.assertEqual(job.summary_paragraph,'')

    def test_expiry_hides_summary_on_direct_job_url_and_cleanup_clears_both(self):
        job=self.finish();self.client.force_login(self.teacher)
        with patch('classroom.video_jobs.timezone.now',return_value=job.summary_expires_at):
            response=self.client.get(self.url('video-detail',job))
            self.assertNotContains(response,result()['paragraph'])
            self.assertContains(response,'summary has expired')
        cleanup_video_files(job.summary_expires_at)
        job.refresh_from_db()
        self.assertEqual((job.transcript,job.transcript_segments,job.summary_paragraph,job.summary_points),('',[],'',[]))
        self.assertIsNotNone(job.summary_deleted_at)

    def test_legacy_transcribed_task_does_not_call_summary_engine(self):
        job=self.new_job();VideoJob.objects.filter(pk=job.pk).update(summary_requested=False)
        job=claim_job()
        with patch('classroom.video_worker.get_summarizer',side_effect=AssertionError('Old task must not summarize')):
            process_job(job,transcriber=transcription_fixture.FakeTranscriber())
        job.refresh_from_db();self.assertEqual(job.status,'transcribed')
        self.assertEqual(job.summary_paragraph,'')

    def test_invalid_summary_and_revoked_permission_cannot_store_result(self):
        bad=Mock();bad.summarize.return_value={'paragraph':'invalid'}
        job=self.finish(bad);self.assertEqual(job.error_code,'summary_output')
        class Revoke(FakeSummarizer):
            def summarize(inner,*args,**kwargs):
                value=super().summarize(*args,**kwargs)
                Membership.objects.filter(user=self.teacher,course=self.course).delete()
                return value
        second=self.finish(Revoke());self.assertEqual(second.error_code,'permission_revoked')
        self.assertEqual(second.summary_paragraph,'');self.assertTrue(second.transcript)

    def test_adapter_missing_runtime_does_not_spawn_and_protocol_cleans_ipc(self):
        adapter=LocalQwenSummarizer()
        with override_settings(LOCAL_SUMMARY_OLLAMA=self.root/'absent.exe'),patch('classroom.local_summarizer.subprocess.Popen') as spawn:
            with self.assertRaises(SummaryFailure):adapter.summarize('text','en',work_dir=self.root,deadline=time.monotonic()+10,on_event=lambda x:None,on_tick=lambda:None)
            spawn.assert_not_called()
        runtime=self.root/'ollama.exe';runtime.write_bytes(b'fixture')
        process=Mock(stdout=StringIO('{"stage":"loading_sum"}\n{"result":"ok"}\n'),returncode=0)
        process.poll.return_value=0
        def spawn(*args,**kwargs):
            (self.root/'summary.pending.json').write_text(json.dumps(result()),encoding='utf-8')
            return process
        with override_settings(LOCAL_SUMMARY_OLLAMA=runtime),patch('classroom.local_summarizer.ProcessTree'),patch('classroom.local_summarizer.subprocess.Popen',side_effect=spawn):
            self.assertEqual(adapter.summarize('טקסט','he',work_dir=self.root,deadline=time.monotonic()+10,on_event=lambda x:None,on_tick=lambda:None)['paragraph'],result()['paragraph'])
        self.assertFalse((self.root/'summary.input.json').exists());self.assertFalse((self.root/'summary.pending.json').exists())


class SummaryContractTests(SimpleTestCase):
    def test_prompt_requires_explained_topics_negation_direction_and_example_scope(self):
        prompt=summary_prompt('source text','en')
        for required in ['actually explained','merely announced','Preserve negations','which class inherits from which','THAT example','Omit unclear']:
            self.assertIn(required,prompt)
        self.assertIn('source text',prompt)

    def test_hebrew_summary_accepts_english_code_terms_without_rewriting(self):
        value=result()
        value['paragraph']='בדוגמה לכל אובייקט Car משתנים נפרדים ומשתנה static משותף.'
        value['key_points']=['אובייקט Car מופיע בדוגמה.','משתנה static משותף בדוגמה.','התוכן מבוסס על התמלול.']
        self.assertEqual(validate_summary({'paragraph':value['paragraph'],'key_points':value['key_points']},'he'),
                         {'paragraph':value['paragraph'],'key_points':value['key_points']})
        self.assertEqual(validate_result(value,'he'),value)

    def test_unexpected_script_is_a_language_failure_not_a_successful_summary(self):
        bad=result();bad['paragraph']+=' 공용'
        with self.assertRaises(SummaryFailure) as caught:validate_result(bad,'he')
        self.assertEqual(caught.exception.code,'summary_language')

    def test_format_language_and_wrong_model_are_rejected(self):
        for change in [{'key_points':['one']},{'paragraph':''},{'metadata':{}},{'summary_seconds':float('nan')}]:
            with self.assertRaises(SummaryFailure):validate_result({**result(),**change},'he')
        with self.assertRaises(ValueError):validate_summary({'paragraph':'Only English','key_points':['a','b','c']},'he')


    def test_windows_process_tree_close_terminates_owned_descendant(self):
        import ctypes,sys,subprocess,time
        from ctypes import wintypes
        from tempfile import TemporaryDirectory
        from .process_tree import ProcessTree
        tree=ProcessTree()
        with TemporaryDirectory() as directory:
            marker=Path(directory)/'child.pid'
            code="import subprocess,sys,time,pathlib;time.sleep(.3);child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']);pathlib.Path(sys.argv[1]).write_text(str(child.pid));time.sleep(30)"
            process=subprocess.Popen([sys.executable,'-c',code,str(marker)],creationflags=subprocess.CREATE_NO_WINDOW)
            handle=None
            try:
                tree.attach(process.pid)
                deadline=time.monotonic()+5
                while not marker.exists() and time.monotonic()<deadline:time.sleep(.05)
                self.assertTrue(marker.exists())
                handle=tree.kernel.OpenProcess(0x100000,False,int(marker.read_text()))
                self.assertTrue(handle)
                tree.close();process.wait(timeout=3)
                wait=tree.kernel.WaitForSingleObject;wait.argtypes=[wintypes.HANDLE,wintypes.DWORD];wait.restype=wintypes.DWORD
                self.assertEqual(wait(handle,3000),0)
            finally:
                tree.close()
                if process.poll() is None:process.kill()
                process.wait(timeout=3)
                if handle:tree.kernel.CloseHandle(handle)
