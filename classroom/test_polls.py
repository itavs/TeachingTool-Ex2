"""Real server lifecycle tests; fake generators are defined only in this file."""
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from html.parser import HTMLParser
from threading import Barrier
from unittest.mock import patch, Mock
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection, connections, IntegrityError, OperationalError, transaction
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from .models import Poll, PollVote, Membership
from . import poll_services as rules
from .poll_generation import GenerationUnavailable, get_poll_generator
from .local_poll_generator import LocalPollGenerator
from .test_participation import ParticipationFixture


class FakeGenerator:
    """Deterministic test fixture; never selectable by the normal application."""
    def generate(self, material, kind, language):
        result = {'question':'שאלת דוגמה' if language == 'he' else 'Example question', 'options':['A','B','C','D']}
        if kind == 'comprehension':
            result.update(correct_index=1, explanation='PRIVATE_EXPLANATION is supported by the supplied source text.')
        return result


class VoteMarkupParser(HTMLParser):
    """Inspect the actual student response, not a second copy of the template."""
    def __init__(self):
        super().__init__()
        self.inside = False
        self.form = None
        self.radios, self.labels, self.buttons, self.events = [], {}, [], []
        self.label_for = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form' and attrs.get('id') == 'poll-vote-form':
            self.inside = True
            self.form = attrs
        if not self.inside:
            return
        self.events.extend(key for key in attrs if key.startswith('on'))
        if tag == 'input' and attrs.get('type') == 'radio':
            self.radios.append(attrs)
        elif tag == 'label':
            self.label_for = attrs.get('for')
            self.labels[self.label_for] = ''
        elif tag == 'button':
            self.buttons.append(attrs)

    def handle_endtag(self, tag):
        if tag == 'label':
            self.label_for = None
        elif tag == 'form':
            self.inside = False

    def handle_data(self, data):
        if self.inside and self.label_for is not None:
            self.labels[self.label_for] += data


class PollFixture(ParticipationFixture):
    def prepare_polls(self):
        self.prepare()
        self.comp = self.make_poll()
        self.opinion = self.make_poll('opinion')

    def make_poll(self, kind='comprehension', language='he', meeting=None):
        return Poll.objects.create(meeting=meeting or self.meeting,kind=kind,language=language,
            material='PRIVATE_MATERIAL',question='Example question',options=['A','B','C','D'],
            correct_index=1 if kind == 'comprehension' else None,
            explanation='PRIVATE_EXPLANATION' if kind == 'comprehension' else '',origin='demo',created_at=timezone.now())

    def purl(self, name, poll=None, course=None, meeting=None):
        args = [(course or self.course).pk,(meeting or self.meeting).pk]
        if name not in ['poll-list','poll-create']:
            args.append((poll or self.comp).pk)
        return reverse(name,args=args)

    def publish(self,poll=None):
        poll = poll or self.comp
        poll.refresh_from_db()
        return rules.publish(poll.meeting_id,poll.pk,self.teacher,poll.version)

    def draft_data(self, poll=None, **extra):
        poll = poll or self.comp
        data = {'version':poll.version,'question':'Updated question',**{f'option_{i}':x for i,x in enumerate(['One','Two','Three','Four'])}}
        if poll.kind == 'comprehension':
            data.update(correct_index=2,explanation='UPDATED_PRIVATE_EXPLANATION')
        return {**data,**extra}


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class PollTests(PollFixture,TestCase):
    def setUp(self):
        self.prepare_polls()

    def test_hebrew_generation_is_blocked_without_calling_provider(self):
        self.assertIsInstance(get_poll_generator(),LocalPollGenerator)
        self.client.force_login(self.teacher)
        with patch('classroom.poll_services.get_poll_generator') as provider:
            for kind in ['comprehension','opinion']:
                response=self.client.post(self.purl('poll-create'),{'kind':kind,'language':'he','material':'Test material'})
                self.assertContains(response,'English only',status_code=400)
                self.assertContains(response,'Test material',status_code=400)
            provider.assert_not_called()
        self.assertEqual(Poll.objects.count(),2)

    def test_ai_review_notice_is_lecturer_draft_only_in_list_detail_and_state(self):
        notice='Model-generated draft — lecturer review required'
        self.comp.origin='ai';self.comp.save(update_fields=['origin'])
        self.client.force_login(self.teacher)
        for name in ['poll-list','poll-detail','poll-edit']:
            with self.subTest(role='lecturer',state='draft',view=name):
                self.assertContains(self.client.get(self.purl(name)),notice)
        self.assertEqual(self.client.get(self.purl('poll-state')).json()['origin_label'],notice)
        self.publish()
        for state in ['active','closed']:
            if state=='closed':rules.close(self.meeting.pk,self.comp.pk,self.teacher)
            for user in [self.teacher,self.student]:
                self.client.force_login(user)
                for name in ['poll-list','poll-detail']:
                    with self.subTest(role=user.username,state=state,view=name):
                        response=self.client.get(self.purl(name))
                        self.assertNotContains(response,notice)
                        self.assertContains(response,'Model-generated poll')
                self.assertEqual(self.client.get(self.purl('poll-state')).json()['origin_label'],'Model-generated poll')

    def test_student_radio_labels_group_and_explicit_submission(self):
        self.publish();self.client.force_login(self.student)
        response = self.client.get(self.purl('poll-detail'))
        markup = VoteMarkupParser();markup.feed(response.content.decode())
        self.assertEqual(markup.form['method'],'post')
        self.assertEqual(markup.form['action'],self.purl('poll-vote'))
        self.assertEqual(len(markup.radios),4)
        self.assertEqual({r['name'] for r in markup.radios},{'option_index'})
        self.assertEqual({r['value'] for r in markup.radios},{'0','1','2','3'})
        ids = [r['id'] for r in markup.radios]
        self.assertEqual(len(set(ids)),4)
        self.assertEqual(set(ids),set(markup.labels))
        for radio in markup.radios:
            self.assertIn(self.comp.options[int(radio['value'])],markup.labels[radio['id']])
            self.assertNotIn('checked',radio)
            self.assertNotIn('poll-choices',radio.get('class','').split())
            self.assertIn('required',radio)
        self.assertEqual(len(markup.buttons),1)
        self.assertEqual(markup.buttons[0]['type'],'submit')
        self.assertEqual(markup.events,[])
        self.assertNotContains(response,'js/polls.js')
        self.assertContains(response,'Selecting an option does not submit it.')
        self.assertFalse(PollVote.objects.exists())
        # Submit one value from the actual rendered group; the server stores it
        # only at the explicit POST boundary, and later changes remain rejected.
        selected = markup.radios[2]
        self.assertEqual(self.client.post(markup.form['action'],{selected['name']:selected['value']}).status_code,302)
        self.assertEqual(PollVote.objects.get().option_index,2)
        self.assertEqual(self.client.post(markup.form['action'],{'option_index':0}).status_code,409)
        self.assertEqual(PollVote.objects.get().option_index,2)

    def test_generation_input_boundaries_and_languages_checked_before_provider(self):
        self.client.force_login(self.teacher)
        with patch('classroom.poll_services.get_poll_generator') as unavailable:
            unavailable.return_value.generate.side_effect=GenerationUnavailable('Local model unavailable')
            for material,status in [('x',503),('א'*6000,503),('🙂'*6000,503),('x'*6001,400),(' '*10,400),('x'*6000+' ',400)]:
                with self.subTest(length=len(material)):
                    self.assertEqual(self.client.post(self.purl('poll-create'),{'kind':'opinion','language':'en','material':material}).status_code,status)
        for kind,language in [('bad','he'),('opinion','fr')]:
            self.assertEqual(self.client.post(self.purl('poll-create'),{'kind':kind,'language':language,'material':'text'}).status_code,400)
        with patch('classroom.poll_services.get_poll_generator') as provider:
            for material in ['', ' '*3, 'x'*6001]:
                with self.assertRaises(ValidationError):
                    rules.create_generated_draft(self.meeting.pk,self.teacher,'opinion','he',material)
            provider.assert_not_called()

    def test_fake_provider_supports_both_types_only_when_injected_in_test(self):
        self.client.force_login(self.teacher)
        with patch('classroom.poll_services.get_poll_generator',return_value=FakeGenerator()):
            for kind in ['comprehension','opinion']:
                for language in ['en']:
                    response=self.client.post(self.purl('poll-create'),{'kind':kind,'language':language,'material':'Test data'})
                    self.assertEqual(response.status_code,302)
                    poll=Poll.objects.latest('pk')
                    self.assertEqual((poll.kind,poll.language,poll.status),(kind,language,'draft'))
                    self.assertEqual(poll.correct_index,1 if kind=='comprehension' else None)
        self.assertIsInstance(get_poll_generator(),LocalPollGenerator)

    def test_provider_failure_and_invalid_output_never_save_placeholder(self):
        self.client.force_login(self.teacher)
        provider=Mock()
        with patch('classroom.poll_services.get_poll_generator',return_value=provider):
            for payload in [{'question':'Bad','options':['A']}, {'question':'Bad','options':['A','B','C','D'],'correct_index':0}]:
                provider.generate.return_value=payload
                self.assertEqual(self.client.post(self.purl('poll-create'),{'kind':'opinion','language':'en','material':'source'}).status_code,400)
            provider.generate.side_effect=TimeoutError('PRIVATE_PROVIDER_ERROR')
            response=self.client.post(self.purl('poll-create'),{'kind':'opinion','language':'en','material':'source'})
            self.assertContains(response,'Generation failed',status_code=503)
            self.assertNotContains(response,'PRIVATE_PROVIDER_ERROR',status_code=503)
        self.assertEqual(Poll.objects.count(),2)

    def test_membership_rechecked_after_generator_before_save(self):
        def revoke(*args):
            Membership.objects.filter(user=self.teacher,course=self.course).delete()
            return FakeGenerator().generate(*args)
        provider=Mock();provider.generate.side_effect=revoke
        self.client.force_login(self.teacher)
        with patch('classroom.poll_services.get_poll_generator',return_value=provider):
            self.assertEqual(self.client.post(self.purl('poll-create'),{'kind':'opinion','language':'en','material':'source'}).status_code,404)
        self.assertEqual(Poll.objects.count(),2)

    def test_draft_edit_all_content_and_optimistic_version(self):
        self.client.force_login(self.teacher)
        data=self.draft_data()
        self.assertEqual(self.client.post(self.purl('poll-edit'),data).status_code,302)
        self.comp.refresh_from_db()
        self.assertEqual((self.comp.question,self.comp.options,self.comp.correct_index,self.comp.explanation),('Updated question',['One','Two','Three','Four'],2,'UPDATED_PRIVATE_EXPLANATION'))
        self.assertEqual(self.client.post(self.purl('poll-edit'),{**data,'question':'Stale overwrite'}).status_code,409)
        self.assertEqual(self.client.post(self.purl('poll-publish'),{'version':data['version']}).status_code,409)
        self.comp.refresh_from_db();self.assertEqual(self.comp.question,'Updated question')

    def test_duplicate_empty_options_and_answer_validation(self):
        self.client.force_login(self.teacher)
        for extra in [{'option_0':'Two'},{'option_0':' '},{'correct_index':4},{'explanation':' '},{'question':''}]:
            self.assertEqual(self.client.post(self.purl('poll-edit'),self.draft_data(**extra)).status_code,400)
        self.assertEqual(self.client.post(self.purl('poll-edit',self.opinion),self.draft_data(self.opinion,correct_index=0)).status_code,400)
        self.assertEqual(self.client.post(self.purl('poll-edit',self.opinion),self.draft_data(self.opinion)).status_code,302)

    def test_student_cannot_see_drafts_in_list_detail_or_state(self):
        self.client.force_login(self.student)
        self.assertNotContains(self.client.get(self.purl('poll-list')),'Example question')
        for name in ['poll-detail','poll-state']:
            self.assertEqual(self.client.get(self.purl(name)).status_code,404)
        self.assertEqual(self.client.post(self.purl('poll-vote'),{'option_index':0}).status_code,404)

    def test_complete_comprehension_lifecycle_and_strict_disclosure(self):
        self.publish()
        self.client.force_login(self.student)
        data=self.client.get(self.purl('poll-state')).json()
        for key in ['correct_index','correct_answer','explanation','material','respondent_count','results']:
            self.assertNotIn(key,data)
        response=self.client.get(self.purl('poll-detail'))
        self.assertNotContains(response,'PRIVATE_EXPLANATION')
        self.assertNotContains(response,'PRIVATE_MATERIAL')
        self.assertNotContains(response,'name="correct_index"')
        self.assertEqual(self.client.post(self.purl('poll-vote'),{'option_index':1}).status_code,302)
        self.assertEqual(self.client.post(self.purl('poll-vote'),{'option_index':2}).status_code,409)
        self.assertEqual(PollVote.objects.get().option_index,1)
        rules.vote(self.meeting.pk,self.comp.pk,self.other,0)
        self.client.force_login(self.teacher)
        data=self.client.get(self.purl('poll-state')).json()
        self.assertEqual(data['respondent_count'],2)
        self.assertEqual([r['percent'] for r in data['results']],[50,50,0,0])
        self.assertEqual(data['explanation'],'PRIVATE_EXPLANATION')
        self.assertEqual(self.client.post(self.purl('poll-close')).status_code,302)
        self.client.force_login(self.student)
        data=self.client.get(self.purl('poll-state')).json()
        self.assertEqual(data['correct_index'],1)
        self.assertEqual(data['respondent_count'],2)
        self.assertNotIn('student',str(data))
        self.assertNotIn('other',str(data))
        self.assertEqual(self.client.post(self.purl('poll-vote'),{'option_index':0}).status_code,409)

    def test_opinion_never_has_answer_or_correctness_evaluation(self):
        self.publish(self.opinion)
        self.client.force_login(self.teacher)
        for phase in ['active','closed']:
            if phase=='closed': rules.close(self.meeting.pk,self.opinion.pk,self.teacher)
            for user in [self.teacher,self.student]:
                self.client.force_login(user)
                data=self.client.get(self.purl('poll-state',self.opinion)).json()
                self.assertFalse(data['show_answer'])
                for key in ['correct_index','correct_answer','explanation','grade','is_correct']:
                    self.assertNotIn(key,data)

    def test_zero_votes_and_new_poll_after_close(self):
        self.publish();self.client.force_login(self.teacher)
        data=self.client.get(self.purl('poll-state')).json()
        self.assertEqual(data['respondent_count'],0)
        self.assertEqual([row['percent'] for row in data['results']],[0]*4)
        self.assertEqual(self.client.post(self.purl('poll-publish',self.opinion),{'version':1}).status_code,409)
        rules.close(self.meeting.pk,self.comp.pk,self.teacher)
        self.assertEqual(self.client.post(self.purl('poll-publish',self.opinion),{'version':1}).status_code,302)
        self.assertEqual(Poll.objects.filter(status='active').count(),1)

    def test_invalid_transitions_and_no_edits_after_publication(self):
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.post(self.purl('poll-close')).status_code,409)
        self.publish()
        for name in ['poll-edit','poll-publish']:
            self.assertEqual(self.client.post(self.purl(name),self.draft_data()).status_code,409)
        rules.close(self.meeting.pk,self.comp.pk,self.teacher)
        self.assertEqual(self.client.post(self.purl('poll-publish'),{'version':3}).status_code,409)
        self.assertEqual(self.client.post(self.purl('poll-close')).status_code,302)

    def test_wrong_roles_foreign_courses_and_direct_urls(self):
        self.client.force_login(self.student)
        for name in ['poll-create','poll-edit']:
            self.assertEqual(self.client.get(self.purl(name)).status_code,403)
            self.assertEqual(self.client.post(self.purl(name)).status_code,403)
        for name in ['poll-publish','poll-close']:
            self.assertEqual(self.client.post(self.purl(name),{'version':1}).status_code,403)
        self.client.force_login(self.outsider)
        for name in ['poll-list','poll-detail','poll-state','poll-edit','poll-create']:
            self.assertEqual(self.client.get(self.purl(name)).status_code,404)
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(self.purl('poll-detail',course=self.foreign)).status_code,404)
        self.publish()
        self.assertEqual(self.client.post(self.purl('poll-vote'),{'option_index':0}).status_code,403)

    def test_revoked_membership_demotion_and_per_course_roles(self):
        self.publish();self.client.force_login(self.teacher)
        foreign=self.make_poll(meeting=self.foreign_meeting)
        self.assertEqual(self.client.post(self.purl('poll-publish',foreign,course=self.foreign,meeting=self.foreign_meeting),{'version':1}).status_code,403)
        member=Membership.objects.get(user=self.teacher,course=self.course)
        member.role='student';member.save()
        self.assertEqual(self.client.post(self.purl('poll-close')).status_code,403)
        member.delete()
        self.assertEqual(self.client.get(self.purl('poll-state')).status_code,404)
        Membership.objects.filter(user=self.student,course=self.course).delete()
        self.client.force_login(self.student)
        self.assertEqual(self.client.post(self.purl('poll-vote'),{'option_index':0}).status_code,404)

    def test_invalid_multiple_or_foreign_vote_values_are_rejected(self):
        self.publish();self.client.force_login(self.student)
        for value in ['bad',4,-1,'1.5',['0','1']]:
            self.assertEqual(self.client.post(self.purl('poll-vote'),{'option_index':value}).status_code,400)
        self.assertEqual(self.client.post(self.purl('poll-vote',meeting=self.foreign_meeting),{'option_index':0}).status_code,404)
        self.assertFalse(PollVote.objects.exists())

    def test_csrf_and_post_only_transitions(self):
        strict=Client(enforce_csrf_checks=True);strict.force_login(self.teacher)
        for name in ['poll-create','poll-edit','poll-publish','poll-close']:
            self.assertEqual(strict.post(self.purl(name),self.draft_data()).status_code,403)
        self.client.force_login(self.teacher)
        for name in ['poll-publish','poll-close']:
            self.assertEqual(self.client.get(self.purl(name)).status_code,405)
        strict.get(self.purl('poll-detail'))
        csrf=strict.cookies['csrftoken'].value
        self.assertEqual(strict.post(self.purl('poll-publish'),{'version':1,'csrfmiddlewaretoken':csrf}).status_code,302)
        strict.force_login(self.student)
        self.assertEqual(strict.post(self.purl('poll-vote'),{'option_index':0}).status_code,403)
        strict.get(self.purl('poll-detail'));csrf=strict.cookies['csrftoken'].value
        self.assertEqual(strict.post(self.purl('poll-vote'),{'option_index':0,'csrfmiddlewaretoken':csrf}).status_code,302)

    def test_anonymous_routes_redirect_to_login_and_get_does_not_mutate(self):
        for name in ['poll-list','poll-create','poll-detail','poll-state','poll-edit']:
            self.assertEqual(self.client.get(self.purl(name)).status_code,302)
        self.client.force_login(self.teacher)
        for name in ['poll-list','poll-create','poll-detail','poll-state','poll-edit']:
            self.assertEqual(self.client.get(self.purl(name)).status_code,200)
        self.assertFalse(PollVote.objects.exists())
        self.comp.refresh_from_db();self.assertEqual(self.comp.status,'draft')

    def test_template_escaping_demo_label_and_english_draft(self):
        self.comp.question='<script>bad()</script>';self.comp.save()
        self.client.force_login(self.teacher)
        response=self.client.get(self.purl('poll-detail'))
        self.assertContains(response,'&lt;script&gt;')
        self.assertContains(response,'not generated by AI')
        self.assertNotContains(response,'<script>bad()</script>')
        self.assertContains(self.client.get(self.purl('poll-edit')),'PRIVATE_EXPLANATION')
        english=self.make_poll(language='en')
        self.assertContains(self.client.get(self.purl('poll-detail',english)),'English')

    def test_database_constraints_reject_duplicate_vote_and_second_active(self):
        self.publish();rules.vote(self.meeting.pk,self.comp.pk,self.student,0)
        with self.assertRaises(IntegrityError),transaction.atomic():
            PollVote.objects.create(poll=self.comp,student=self.student,option_index=2,submitted_at=timezone.now())
        with self.assertRaises(IntegrityError),transaction.atomic():
            Poll.objects.filter(pk=self.opinion.pk).update(status='active',published_at=timezone.now())
        with self.assertRaises(IntegrityError),transaction.atomic():
            Poll.objects.filter(pk=self.opinion.pk).update(correct_index=0)

    def test_database_failure_does_not_claim_vote_saved_or_leak_answer(self):
        self.publish();self.client.force_login(self.student)
        with patch('classroom.poll_views.rules.vote',side_effect=OperationalError('locked')):
            response=self.client.post(self.purl('poll-vote'),{'option_index':0})
        self.assertContains(response,'could not be confirmed',status_code=503)
        self.assertNotContains(response,'PRIVATE_EXPLANATION',status_code=503)
        self.assertFalse(PollVote.objects.exists())

    def test_local_demo_command_is_labeled_idempotent_and_preserves_edits_status(self):
        output=StringIO()
        call_command('seed_demo_polls',meeting_id=self.meeting.pk,stdout=output)
        demo=self.meeting.polls.filter(demo_key__isnull=False)
        self.assertEqual(demo.count(),2)
        self.assertEqual(set(demo.values_list('kind',flat=True)),{'comprehension','opinion'})
        poll=demo.first();poll.question='Preserve my edited demo';poll.save();self.publish(poll)
        call_command('seed_demo_polls',meeting_id=self.meeting.pk,stdout=output)
        poll.refresh_from_db();self.assertEqual((poll.question,poll.status),('Preserve my edited demo','active'))
        self.assertIn('Not generated by AI',output.getvalue())
        call_command('seed_demo_polls',meeting_id=self.meeting.pk,language='en',stdout=output)
        self.assertEqual(demo.count(),4)
        call_command('seed_demo_polls',meeting_id=self.meeting.pk,new_set=True,stdout=output)
        self.assertEqual(demo.count(),6)
        self.assertEqual(demo.filter(status='active').count(),1)
        with self.assertRaises(CommandError): call_command('seed_demo_polls',meeting_id=999999,stdout=StringIO())


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class PollConcurrencyTests(PollFixture,TransactionTestCase):
    def setUp(self):
        if 'memory' in connection.settings_dict['NAME']:
            self.skipTest('Use a file-backed DJANGO_TEST_SQLITE_NAME for real connection races.')
        self.prepare_polls()

    def race(self,entries):
        barrier=Barrier(2,timeout=15)
        def worker(entry):
            user_id,url,data=entry
            connections.close_all()
            try:
                client=Client();client.force_login(get_user_model().objects.get(pk=user_id))
                barrier.wait()
                return client.post(url,data).status_code
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(worker,entries))

    def test_same_student_parallel_votes_are_final_and_unique(self):
        self.publish()
        statuses=self.race([(self.student.pk,self.purl('poll-vote'),{'option_index':i}) for i in [0,1]])
        self.assertEqual(sorted(statuses),[302,409])
        self.assertEqual(PollVote.objects.count(),1)
        self.assertEqual(PollVote.objects.get().option_index,0 if statuses[0]==302 else 1)

    def test_two_students_parallel_votes_both_count(self):
        self.publish()
        self.assertEqual(self.race([(u.pk,self.purl('poll-vote'),{'option_index':i}) for i,u in enumerate([self.student,self.other])]),[302,302])
        self.assertEqual(PollVote.objects.count(),2)

    def test_parallel_publications_only_one_active_poll(self):
        statuses=self.race([(self.teacher.pk,self.purl('poll-publish',p),{'version':1}) for p in [self.comp,self.opinion]])
        self.assertEqual(sorted(statuses),[302,409])
        self.assertEqual(Poll.objects.filter(status='active').count(),1)

    def test_vote_racing_close_has_one_consistent_order(self):
        self.publish()
        statuses=self.race([(self.student.pk,self.purl('poll-vote'),{'option_index':0}),
            (self.teacher.pk,self.purl('poll-close'),{})])
        self.assertEqual(statuses[1],302)
        self.assertIn(statuses[0],[302,409])
        self.comp.refresh_from_db();self.assertEqual(self.comp.status,'closed')
        self.assertEqual(PollVote.objects.count(),1 if statuses[0]==302 else 0)
        if statuses[0]==302:
            self.assertLessEqual(PollVote.objects.get().submitted_at,self.comp.closed_at)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(self.purl('poll-vote'),{'option_index':1}).status_code,409)
