"""Only fixed filenames below UUID directories may be accessed or deleted."""
from contextlib import contextmanager
from pathlib import Path
import os
import uuid
from django.conf import settings


def job_path(job_id, filename):
    if filename not in {'input.mp4', 'audio.wav'}:
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


class WorkerBusy(Exception):
    pass


@contextmanager
def exclusive_lock(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as stream:
        if path.stat().st_size == 0:
            stream.write(b'0'); stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise WorkerBusy('Another video process is already running.') from None
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)
