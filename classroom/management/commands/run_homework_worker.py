"""Separate single task runner for bounded experimental local homework reviews."""
import time
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from classroom.models import ReviewJob
from classroom.homework_worker import process_review_job
from classroom.process_lock import exclusive_lock
from classroom.homework_batches import expire_batch_jobs


class Command(BaseCommand):
    help='Process queued English homework reviews using the installed local Qwen model.'

    def add_arguments(self,parser):
        parser.add_argument('--once',action='store_true')

    def handle(self,*args,**options):
        with exclusive_lock(Path(settings.LOCAL_DIR)/'.homework-worker.lock'):
            # Owning the single-worker lock proves any previous runner has exited.
            # No automatic retry or fabricated success for interrupted work.
            ReviewJob.objects.filter(status='running').update(status='failed',error_code='interrupted',waiting_for_resource=False,finished_at=timezone.now())
            expire_batch_jobs()
            try:
                while True:
                    expire_batch_jobs()
                    job=ReviewJob.objects.filter(status='queued').order_by('created_at','pk').first()
                    result=process_review_job(job.pk) if job else None
                    if options['once']:return
                    if job is None:time.sleep(1)
                    elif result=='waiting':time.sleep(2)
            except KeyboardInterrupt:
                return
