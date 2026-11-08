"""One coordinator per storage root, isolated decoder, persisted heartbeats."""
from datetime import timedelta
import multiprocessing as mp
from pathlib import Path
import time
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import VideoJob
from .video_jobs import ACTIVE, fail_job, recover_jobs, cleanup_video_files, lecturer_still_allowed
from .video_media import media_child
from .video_storage import job_path, remove_file, exclusive_lock
from .video_engines import get_transcriber, get_summarizer, FUTURE_TEXT_RETENTION_DAYS
from .local_transcriber import TranscriptionFailure,validate_result
from .asr_checkpoint import is_expected_metadata
from .local_summarizer import SummaryFailure, validate_result as validate_summary_result


@transaction.atomic
def claim_job():
    job = VideoJob.objects.select_for_update().filter(status='queued').order_by('queued_at','created_at').first()
    if job is None: return None
    now = timezone.now()
    if job.source_deleted_at or job.source_expires_at <= now+timedelta(seconds=settings.VIDEO_PROCESS_SECONDS+300):
        fail_job(job.pk,'expired'); return job
    if not lecturer_still_allowed(job):
        fail_job(job.pk,'permission_revoked'); return job
    job.status='validating'; job.started_at=now; job.heartbeat_at=now; job.save()
    return job


def process_job(job, stop_requested=lambda:False, *, timeout_seconds=None, child_target=media_child,transcriber=None,summarizer=None):
    """Must run under coordinator lock. Test injection never comes from user input."""
    if job.status not in ACTIVE: return
    source, output = job_path(job.pk,'input.mp4'),job_path(job.pk,'audio.wav')
    limit = settings.VIDEO_PROCESS_SECONDS if timeout_seconds is None else timeout_seconds
    # Deadline is relative to the persisted worker start, not queue or child start.
    remaining = max(0,limit-(timezone.now()-job.started_at).total_seconds())
    deadline = time.monotonic()+remaining
    context = mp.get_context('spawn')
    receiver,sender=context.Pipe(duplex=False)
    child=context.Process(target=child_target,args=(sender,str(source),str(output),settings.VIDEO_MAX_SECONDS,deadline))
    last_heartbeat=0
    def check_control():
        nonlocal last_heartbeat
        if stop_requested():raise TranscriptionFailure('interrupted')
        if time.monotonic()>=deadline:raise TranscriptionFailure('timeout')
        if time.monotonic()-last_heartbeat>=2:
            current=VideoJob.objects.get(pk=job.pk)
            if current.status not in ACTIVE:raise TranscriptionFailure(current.error_code or 'interrupted')
            if not lecturer_still_allowed(current):raise TranscriptionFailure('permission_revoked')
            VideoJob.objects.filter(pk=job.pk,status__in=ACTIVE).update(heartbeat_at=timezone.now())
            last_heartbeat=time.monotonic()
    def asr_event(event):
        updates={}
        if event.get('stage') in ['loading_asr','transcribing']:updates['status']=event['stage']
        if 'model_load_seconds' in event:updates['model_load_seconds']=event['model_load_seconds']
        if 'model_loaded' in event:
            if not is_expected_metadata(event['model_loaded']):raise TranscriptionFailure('asr_output')
            updates['asr_metadata']=event['model_loaded']
        if 'progress_seconds' in event:updates['transcribed_until']=max(0,min(float(event['progress_seconds']),settings.VIDEO_MAX_SECONDS))
        if updates:VideoJob.objects.filter(pk=job.pk,status__in=ACTIVE).update(**updates)
    def summary_event(event):
        updates={}
        if event.get('stage') in ['loading_sum','summarizing']:updates['status']=event['stage']
        if 'model_loaded' in event:updates['summary_metadata']=event['model_loaded']
        if updates:VideoJob.objects.filter(pk=job.pk,status__in=ACTIVE).update(**updates)
    summary_started=False
    try:
        child.start();sender.close()
        result=None
        while True:
            if stop_requested(): fail_job(job.pk,'interrupted');break
            if time.monotonic()>=deadline: fail_job(job.pk,'timeout');break
            if time.monotonic()-last_heartbeat>=2:
                current=VideoJob.objects.get(pk=job.pk)
                if current.status not in ACTIVE: break
                if not lecturer_still_allowed(current): fail_job(job.pk,'permission_revoked');break
                VideoJob.objects.filter(pk=job.pk,status__in=ACTIVE).update(heartbeat_at=timezone.now())
                last_heartbeat=time.monotonic()
            if receiver.poll(.2):
                try: event=receiver.recv()
                except EOFError: fail_job(job.pk,'interrupted');break
                if event.get('result'):
                    result=event;break
                if event.get('stage')=='extracting':
                    VideoJob.objects.filter(pk=job.pk,status__in=ACTIVE).update(status='extracting',video_seconds=event['video_seconds'],heartbeat_at=timezone.now())
        if result:
            if result['result']=='ok':
                VideoJob.objects.filter(pk=job.pk,status__in=ACTIVE).update(video_seconds=result['video_seconds'],
                    audio_seconds=result['audio_seconds'],audio_samples=result['audio_samples'])
                transcript=None
                if job.transcription_requested:
                    # Release the decoder and its lock before the ASR process starts.
                    child.join(timeout=2)
                    if child.is_alive():child.terminate();child.join(timeout=2)
                    check_control()
                    asr_event({'stage':'loading_asr'})
                    engine=transcriber if transcriber is not None else get_transcriber()
                    transcript=validate_result(engine.transcribe(str(output),deadline=deadline,on_event=asr_event,on_tick=check_control))
                    check_control()
                if not remove_file(job.pk,'audio.wav'):
                    fail_job(job.pk,'cleanup_failed','extracting')
                else:
                    now=timezone.now()
                    updates={}
                    if transcript:
                        updates={'transcript':transcript['text'],'transcript_segments':transcript['segments'],
                            'detected_language':transcript['language'],'transcript_created_at':now,
                            'transcript_expires_at':now+timedelta(days=FUTURE_TEXT_RETENTION_DAYS),
                            'model_load_seconds':transcript['model_load_seconds'],
                            'transcription_seconds':transcript['transcription_seconds'],'asr_metadata':transcript['metadata']}
                    # Commit content only if the owner still has permission and the
                    # task has not been failed by maintenance during processing.
                    with transaction.atomic():
                        current=VideoJob.objects.select_for_update().get(pk=job.pk)
                        if not lecturer_still_allowed(current):raise TranscriptionFailure('permission_revoked')
                        check_control()
                        pending_summary=bool(transcript and job.summary_requested)
                        VideoJob.objects.filter(pk=job.pk,status__in=ACTIVE).update(status='loading_sum' if pending_summary else ('transcribed' if transcript else 'extracted'),finished_at=None if pending_summary else now,
                        heartbeat_at=now,processing_seconds=max(0,(now-job.started_at).total_seconds()),
                        video_seconds=result['video_seconds'],audio_seconds=result['audio_seconds'],audio_samples=result['audio_samples'],
                        audio_removed_at=now,**updates)
                    if pending_summary:
                        summary_started=True
                        check_control()
                        engine=summarizer if summarizer is not None else get_summarizer()
                        generated=validate_summary_result(engine.summarize(transcript['text'],transcript['language'],
                            work_dir=output.parent,deadline=deadline,on_event=summary_event,on_tick=check_control),transcript['language'])
                        check_control()
                        with transaction.atomic():
                            current=VideoJob.objects.select_for_update().get(pk=job.pk)
                            if not lecturer_still_allowed(current):raise SummaryFailure('permission_revoked')
                            check_control()
                            now=timezone.now()
                            if now>=current.transcript_expires_at:raise SummaryFailure('expired')
                            VideoJob.objects.filter(pk=job.pk,status__in=ACTIVE).update(status='summarized',
                                summary_paragraph=generated['paragraph'],summary_points=generated['key_points'],
                                summary_metadata=generated['metadata'],summary_seconds=generated['summary_seconds'],
                                summary_created_at=now,summary_expires_at=min(now+timedelta(days=FUTURE_TEXT_RETENTION_DAYS),current.transcript_expires_at),
                                finished_at=now,heartbeat_at=now,processing_seconds=max(0,(now-job.started_at).total_seconds()))
            else:
                fail_job(job.pk,result.get('code','processing_error'),result.get('stage'))
    except (TranscriptionFailure, SummaryFailure) as error:
        fail_job(job.pk,error.code)
    except Exception:
        fail_job(job.pk,'summary_failed' if summary_started else 'processing_error')
    finally:
        if child.is_alive(): child.terminate()
        if child.pid is not None: child.join(timeout=3)
        receiver.close();sender.close()
        if remove_file(job.pk,'audio.wav'):
            VideoJob.objects.filter(pk=job.pk).update(audio_removed_at=timezone.now())
        remove_file(job.pk,'transcript.pending.json')
        remove_file(job.pk,'summary.input.json')
        remove_file(job.pk,'summary.pending.json')


def run_worker(*,once=False,stop_requested=lambda:False,child_target=media_child):
    with exclusive_lock(Path(settings.VIDEO_STORAGE_ROOT)/'.worker.lock'):
        # Owning the OS lock proves there is no previous coordinator alive.
        recover_jobs(force_active=True)
        while not stop_requested():
            cleanup_video_files()
            job=claim_job()
            if job: process_job(job,stop_requested,child_target=child_target)
            if once: return
            if job is None: time.sleep(1)
