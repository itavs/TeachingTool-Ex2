"""Explicit isolated validation runtime; never points at the demonstration DB."""
import os
from pathlib import Path
from .settings import *
if not os.environ.get('TEACHINGTOOL_VALIDATION_DIR'):
    raise RuntimeError('Set TEACHINGTOOL_VALIDATION_DIR to an isolated directory.')
LOCAL_DIR = Path(os.environ['TEACHINGTOOL_VALIDATION_DIR']).resolve()
LOCAL_DIR.mkdir(parents=True, exist_ok=True)
DATABASES['default']['NAME'] = LOCAL_DIR / 'validation.sqlite3'
DATABASES['default']['TEST'] = {'NAME':str(LOCAL_DIR / 'tests.sqlite3')}
VIDEO_STORAGE_ROOT = LOCAL_DIR / 'videos'
FILE_UPLOAD_TEMP_DIR = LOCAL_DIR / 'upload-temp'
FILE_UPLOAD_TEMP_DIR.mkdir(exist_ok=True)
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
ALLOWED_HOSTS = ['localhost','127.0.0.1','testserver']
