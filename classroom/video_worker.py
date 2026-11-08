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


def process_job(job, stop_requested=lambda:False, *, timeout_seconds=None, child_target=media_child):
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
                if not remove_file(job.pk,'audio.wav'):
                    fail_job(job.pk,'cleanup_failed','extracting')
                else:
                    now=timezone.now()
                    VideoJob.objects.filter(pk=job.pk,status__in=ACTIVE).update(status='extracted',finished_at=now,
                        heartbeat_at=now,processing_seconds=max(0,(now-job.started_at).total_seconds()),
                        video_seconds=result['video_seconds'],audio_seconds=result['audio_seconds'],audio_samples=result['audio_samples'])
            else:
                fail_job(job.pk,result.get('code','processing_error'),result.get('stage'))
    except Exception:
        fail_job(job.pk,'processing_error')
    finally:
        if child.is_alive(): child.terminate()
        if child.pid is not None: child.join(timeout=3)
        receiver.close();sender.close()
        remove_file(job.pk,'audio.wav')


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
