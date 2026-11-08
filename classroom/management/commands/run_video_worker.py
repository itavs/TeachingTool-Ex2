import signal
from django.core.management.base import BaseCommand, CommandError
from classroom.video_worker import run_worker
from classroom.video_storage import WorkerBusy


class Command(BaseCommand):
    help='Process video uploads sequentially. AI engines are not used. Ctrl+C stops safely.'

    def add_arguments(self,parser):
        parser.add_argument('--once',action='store_true',help='Handle at most one queued task, then exit.')

    def handle(self,*args,**options):
        stopped=False
        def stop(signum,frame):
            nonlocal stopped
            stopped=True
        old={s:signal.signal(s,stop) for s in [signal.SIGINT,signal.SIGTERM]}
        try:
            self.stdout.write('Video worker running: one video at a time; real media extraction only, no AI.')
            run_worker(once=options['once'],stop_requested=lambda:stopped)
        except WorkerBusy as error:
            raise CommandError(str(error)) from None
        finally:
            for signum,handler in old.items():signal.signal(signum,handler)
