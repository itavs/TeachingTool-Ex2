import time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path
from classroom.video_jobs import cleanup_video_files
from classroom.video_storage import exclusive_lock, WorkerBusy


class Command(BaseCommand):
    help='Independent recovery/cleanup loop, including when the decoder worker stops. Ctrl+C exits.'

    def add_arguments(self,parser):
        parser.add_argument('--once',action='store_true')

    def handle(self,*args,**options):
        try:
            with exclusive_lock(Path(settings.VIDEO_STORAGE_ROOT)/'.maintenance.lock'):
                while True:
                    count=cleanup_video_files()
                    if options['once']:
                        self.stdout.write(f'Cleanup completed; {count} expired sources removed.');return
                    time.sleep(10)  # Recovery <=30s grace +10s; purge has a 5-minute margin.
        except KeyboardInterrupt:
            self.stdout.write('Maintenance stopped.')
        except WorkerBusy as error:
            raise CommandError(str(error)) from None
