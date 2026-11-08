"""Pure subprocess fixtures; importing them performs no media/AI processing."""
import time
from pathlib import Path


def waiting_child(sender,source,output,max_seconds,deadline):
    time.sleep(30)


def watchdog_child(sender,source,output,max_seconds,deadline):
    from unittest.mock import patch
    from classroom.video_media import media_child
    def wait(*args):
        Path(output).write_bytes(b'test-only partial audio')
        time.sleep(30)
    with patch('classroom.video_media.inspect_mp4',return_value={'video_seconds':1}),patch('classroom.video_media.extract_audio',side_effect=wait):
        media_child(sender,source,output,max_seconds,deadline)


def test_worker_process(database,storage,temp):
    import os
    os.environ['DJANGO_SETTINGS_MODULE']='teachingtool.settings'
    import django
    django.setup()
    from django.conf import settings
    from django.db import connections
    settings.VIDEO_STORAGE_ROOT=Path(storage)
    settings.FILE_UPLOAD_TEMP_DIR=Path(temp)
    connections.close_all()
    connections['default'].settings_dict['NAME']=database
    from classroom.video_worker import run_worker
    run_worker(once=True,child_target=watchdog_child)
