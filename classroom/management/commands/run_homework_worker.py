"""Separate task runner; no runtime test provider or accepted model is configured."""
import time
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from classroom.models import ReviewJob
from classroom.homework_worker import process_review_job
from classroom.process_lock import exclusive_lock


class Command(BaseCommand):
    help='Process queued homework reviews (generation is currently disabled in the normal site).'

    def add_arguments(self,parser):
        parser.add_argument('--once',action='store_true')

    def handle(self,*args,**options):
        with exclusive_lock(Path(settings.LOCAL_DIR)/'.homework-worker.lock'):
            # Owning the single-worker lock proves any previous runner has exited.
            # No automatic retry or fabricated success for interrupted work.
            ReviewJob.objects.filter(status='running').update(status='failed',error_code='interrupted',finished_at=timezone.now())
            try:
                while True:
                    job=ReviewJob.objects.filter(status='queued').order_by('created_at','pk').first()
                    if job:process_review_job(job.pk)
                    if options['once']:return
                    if job is None:time.sleep(1)
            except KeyboardInterrupt:
                return
