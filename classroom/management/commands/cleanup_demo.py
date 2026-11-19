"""Preview-first intentional cleanup of explicitly named seeded demo courses."""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from classroom import models as m


class Command(BaseCommand):
    help='Preview demo course data cleanup. No deletion without --apply and explicit --course-code.'

    def add_arguments(self,parser):
        parser.add_argument('--course-code',action='append',choices=['DEMO-CS101','DEMO-SE201'])
        parser.add_argument('--apply',action='store_true')

    def handle(self,*args,**options):
        if options['apply'] and not options['course_code']:
            raise CommandError('Deletion requires explicit --course-code; preview with no arguments first.')
        codes=options['course_code'] or ['DEMO-CS101','DEMO-SE201']
        with transaction.atomic():
            courses=m.Course.objects.filter(code__in=codes)
            meetings=m.Meeting.objects.filter(course__in=courses)
            assignments=m.HomeworkAssignment.objects.filter(meeting__in=meetings)
            versions=m.SubmissionVersion.objects.filter(assignment__in=assignments)
            jobs=m.ReviewJob.objects.filter(submission__in=versions)
            polls=m.Poll.objects.filter(meeting__in=meetings)
            videos=m.VideoJob.objects.filter(meeting__in=meetings)
            groups=[m.FeedbackDraft.objects.filter(job__in=jobs),jobs,
                m.ReviewBatch.objects.filter(assignment__in=assignments),versions,assignments,
                m.PollVote.objects.filter(poll__in=polls),polls,
                m.AttendanceRecord.objects.filter(meeting__in=meetings),
                m.AttendanceWindow.objects.filter(meeting__in=meetings),
                m.MeetingRequest.objects.filter(meeting__in=meetings),videos,meetings,
                m.Membership.objects.filter(course__in=courses),courses]
            for queryset in groups:
                self.stdout.write(f'{queryset.model.__name__}: {queryset.count()}')
            if not options['apply']:
                self.stdout.write('PREVIEW ONLY. No data/files deleted. User accounts and credentials are retained.')
                return
            if jobs.filter(status__in=['queued','running']).exists() or videos.exclude(status__in=['extracted','transcribed','summarized','failed']).exists():
                raise CommandError('Active work exists. Stop workers and resolve active jobs before intentional cleanup.')
            for queryset in groups:queryset.delete()
        self.stdout.write('Named demo course records deleted. Accounts/credentials retained. No files deleted; private video orphan cleanup is separate maintenance.')
