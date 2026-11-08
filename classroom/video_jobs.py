"""Private upload lifecycle and independent recovery/retention maintenance."""
from datetime import timedelta
from pathlib import Path
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .attendance import authorize, CourseAccessError
from .models import VideoJob, Membership
from .video_storage import job_path, remove_file

ACTIVE = ['validating', 'extracting']
TERMINAL = ['extracted', 'failed']
HEARTBEAT_GRACE_SECONDS = 30
ERRORS = {
    'invalid_mp4':'The file is not a supported valid MP4 video.',
    'no_audio':'The MP4 has no audio track.',
    'no_video':'The file has no video track.',
    'unknown_duration':'The video duration could not be verified safely.',
    'too_long':'The video exceeds the 4-minute limit.',
    'too_large':'The upload exceeds the 200 MB limit.',
    'empty_audio':'No decodable audio was found.',
    'decode_failed':'The video or audio is damaged or cannot be decoded.',
    'timeout':'Processing reached the 10-minute limit. Queue time is not included.',
    'interrupted':'The worker stopped or stopped reporting progress. Processing was not completed.',
    'expired':'The source is no longer available within its retention window. Upload it again to continue.',
    'upload_failed':'The upload could not be saved completely. Please upload the file again.',
    'permission_revoked':'The uploader is no longer a lecturer in this course.',
    'processing_error':'Media processing could not be completed. No audio-extraction success is confirmed.',
    'cleanup_failed':'Audio was extracted but temporary-file cleanup failed. Maintenance will retry cleanup.',
}


def lecturer_still_allowed(job):
    return Membership.objects.filter(course_id=job.meeting.course_id, user_id=job.owner_id, role='lecturer', user__is_active=True).exists()


def save_upload(meeting_id, user, upload):
    authorize(meeting_id, user, Membership.Role.LECTURER)
    name = upload.name.replace('\\','/').rsplit('/',1)[-1]
    if not name.lower().endswith('.mp4'):
        raise ValidationError('Upload an MP4 file.')
    if upload.size > settings.VIDEO_MAX_BYTES:
        raise ValidationError('The upload exceeds 200 MB.')
    now = timezone.now()
    job = VideoJob.objects.create(meeting_id=meeting_id, owner=user, original_name=name[:255],
        created_at=now, source_expires_at=now+timedelta(hours=24))
    try:
        target = job_path(job.pk,'input.mp4')
        target.parent.mkdir(parents=True,exist_ok=True)
        count = 0
        with target.open('xb') as output:
            for chunk in upload.chunks():
                count += len(chunk)
                if count > settings.VIDEO_MAX_BYTES:
                    raise ValidationError('The upload exceeds 200 MB.')
                output.write(chunk)
        if count == 0:
            raise ValidationError('The upload is empty.')
        with transaction.atomic():
            authorize(meeting_id,user,Membership.Role.LECTURER)
            VideoJob.objects.filter(pk=job.pk,status='uploading').update(status='queued',queued_at=timezone.now(),file_size=count)
        job.refresh_from_db()
        return job
    except Exception:
        VideoJob.objects.filter(pk=job.pk).update(status='failed',failed_stage='uploading',error_code='upload_failed',finished_at=timezone.now())
        if remove_file(job.pk,'input.mp4'):
            VideoJob.objects.filter(pk=job.pk).update(source_deleted_at=timezone.now())
        raise


def fail_job(job_id, code, stage=None):
    with transaction.atomic():
        job = VideoJob.objects.select_for_update().get(pk=job_id)
        if job.status in TERMINAL:
            return job
        now = timezone.now()
        job.failed_stage = stage or job.status
        job.status = 'failed'; job.error_code = code; job.finished_at = now
        if job.started_at:
            job.processing_seconds = max(0,(now-job.started_at).total_seconds())
        job.save()
    remove_file(job.pk,'audio.wav')
    return job


def recover_jobs(now=None, force_active=False):
    now = now or timezone.now()
    for job in VideoJob.objects.filter(status__in=ACTIVE):
        # Recheck under the write lock so a fresh heartbeat cannot race recovery.
        with transaction.atomic():
            current = VideoJob.objects.select_for_update().get(pk=job.pk)
            if current.status not in ACTIVE: continue
            if current.started_at and (now-current.started_at).total_seconds() >= settings.VIDEO_PROCESS_SECONDS:
                fail_job(current.pk,'timeout')
            elif force_active or current.heartbeat_at is None or (now-current.heartbeat_at).total_seconds()>HEARTBEAT_GRACE_SECONDS:
                fail_job(current.pk,'interrupted')
    for job in VideoJob.objects.filter(status='uploading',created_at__lt=now-timedelta(minutes=2)):
        fail_job(job.pk,'upload_failed')
        if remove_file(job.pk,'input.mp4'):
            VideoJob.objects.filter(pk=job.pk).update(source_deleted_at=now)


def cleanup_video_files(now=None):
    now = now or timezone.now()
    # Five-minute margin + 30-second maintenance cycle: physical purge before 24h
    # while services/machine run. Offline machines cannot execute a timer.
    recover_jobs(now)
    removed = 0
    for job in VideoJob.objects.all():
        if job.status in TERMINAL:
            remove_file(job.pk,'audio.wav')
        if job.source_expires_at <= now+timedelta(minutes=5) and job.source_deleted_at is None:
            if job.status not in TERMINAL:
                fail_job(job.pk,'expired')
            if remove_file(job.pk,'input.mp4'):
                VideoJob.objects.filter(pk=job.pk).update(source_deleted_at=now)
                removed += 1
    # Recover crash leftovers without recursive deletion or user-controlled paths.
    root = Path(settings.VIDEO_STORAGE_ROOT).resolve()
    if root.exists():
        known = {str(pk) for pk in VideoJob.objects.values_list('pk',flat=True)}
        for directory in root.iterdir():
            if directory.is_symlink() or not directory.is_dir(): continue
            try: parsed = str(uuid.UUID(directory.name))
            except ValueError: continue
            if directory.resolve().parent != root: continue
            if parsed not in known and directory.stat().st_mtime <= now.timestamp()-120:
                for name in ['audio.wav','input.mp4']:
                    remove_file(parsed,name)
    temp = Path(settings.FILE_UPLOAD_TEMP_DIR).resolve()
    if temp.is_dir():
        for path in temp.glob('*.upload*'):
            if path.is_symlink() or not path.is_file() or path.resolve().parent != temp: continue
            if path.stat().st_mtime <= now.timestamp()-(24*3600-300):
                try: path.unlink()
                except OSError: pass
    return removed


def owned_job(meeting_id, job_id, user):
    authorize(meeting_id,user,Membership.Role.LECTURER)
    job = VideoJob.objects.filter(pk=job_id,meeting_id=meeting_id,owner=user).first()
    if job is None: raise CourseAccessError(404)
    recover_jobs()
    job.refresh_from_db()
    return job


def payload(job, now=None):
    now = now or timezone.now()
    elapsed = max(0,(now-job.started_at).total_seconds()) if job.started_at and job.status in ACTIVE else job.processing_seconds
    queue_end = job.started_at or job.finished_at or now
    return {'id':str(job.pk),'filename':job.original_name,'status':job.status,'stage_label':job.get_status_display(),
        'processing_seconds':round(elapsed,1),'waiting_seconds':round(max(0,(queue_end-(job.queued_at or job.created_at)).total_seconds()),1),
        'failed_stage':dict(VideoJob.Status.choices).get(job.failed_stage,job.failed_stage),
        'error':ERRORS.get(job.error_code,'') if job.error_code else '',
        'video_seconds':job.video_seconds,'audio_seconds':job.audio_seconds,
        'source_removed':job.source_deleted_at is not None}
