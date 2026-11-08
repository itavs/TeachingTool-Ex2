"""Only fixed filenames below UUID directories may be accessed or deleted."""
from pathlib import Path
import uuid
from django.conf import settings
from .process_lock import exclusive_lock, WorkerBusy


def job_path(job_id, filename):
    if filename not in {'input.mp4', 'audio.wav', 'transcript.pending.json', 'summary.input.json', 'summary.pending.json'}:
        raise ValueError('Unapproved private filename.')
    root = Path(settings.VIDEO_STORAGE_ROOT).resolve()
    directory = root / str(uuid.UUID(str(job_id)))
    if directory.resolve().parent != root:
        raise ValueError('Private job directory escaped storage root.')
    path = (directory / filename).resolve()
    if path.parent != directory:
        raise ValueError('Private file escaped its job directory.')
    return path


def remove_file(job_id, filename):
    try:
        job_path(job_id, filename).unlink(missing_ok=True)
        return True
    except (OSError, ValueError):
        return False  # Maintenance retries locked files without exposing paths.
