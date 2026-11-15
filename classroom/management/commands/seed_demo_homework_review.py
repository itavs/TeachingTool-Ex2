"""Create explicitly synthetic, unpublished homework sources; never fabricate AI feedback."""
import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from classroom.models import Course, Meeting, Membership, HomeworkAssignment
from classroom.homework_services import create_assignment, submit_version


class Command(BaseCommand):
    help='Create a synthetic English review assignment with two valid different approaches. No inference/publication.'

    @transaction.atomic
    def handle(self,*args,**options):
        data=json.loads((settings.BASE_DIR/'classroom/demo_homework.json').read_text(encoding='utf-8'))
        try:
            course=Course.objects.get(code='DEMO-CS101')
            teacher=get_user_model().objects.get(username='lecturer_alpha')
            users=[get_user_model().objects.get(username=w['username']) for w in data['works']]
        except (Course.DoesNotExist,get_user_model().DoesNotExist):
            raise CommandError('Prepare existing demo accounts/courses with seed_demo first; no passwords are changed here.')
        for user,role in [(teacher,'lecturer')]+[(u,'student') for u in users]:
            if not Membership.objects.filter(course=course,user=user,role=role).exists():
                raise CommandError('Required demo course membership is missing.')
        meeting,_=Meeting.objects.get_or_create(course=course,title='Homework AI review demo',defaults={
            'starts_at':timezone.now(),'description':'Synthetic local AI review demonstration only.'})
        assignment=HomeworkAssignment.objects.filter(meeting=meeting,title=data['title']).first()
        if assignment is None:
            assignment=create_assignment(meeting,teacher,{k:data[k] for k in ['title','instructions','criteria','professional_rubric']})
            for user,work in zip(users,data['works']):submit_version(meeting,assignment.pk,user,work['text'])
        self.stdout.write(f'Synthetic assignment {assignment.pk}; meeting {meeting.pk}. No feedback generated or published.')
