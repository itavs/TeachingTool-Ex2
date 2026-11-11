"""Generated draft validation and UI failures; real-model evidence is separate."""
import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch,Mock
from django.test import SimpleTestCase,TestCase,override_settings
from . import test_polls as fixtures
from .models import Poll
from .poll_contract import validate_generated
from .poll_generation import GenerationUnavailable
from .local_poll_generator import LocalPollGenerator
from .summary_contract import MODEL,WEIGHTS,MANIFEST_SHA256


def generated():
    return {'question':'Which item does a stack remove first?',
        'options':['The newest item','The oldest item','Every item','No items'],
        'correct_index':0,'explanation':'A stack removes the newest item because its order is last in, first out.'}


class GeneratedContractTests(SimpleTestCase):
    def test_valid_comprehension_and_opinion_are_not_rewritten(self):
        value=generated();self.assertEqual(validate_generated('comprehension',value),value)
        opinion={'question':'Which practice method do you prefer?','options':['Diagrams','Coding','Discussion','Worked examples']}
        self.assertEqual(validate_generated('opinion',opinion),opinion)

    def test_bad_fields_script_duplicates_answer_and_incomplete_explanation_rejected(self):
        for change in [{'options':['Same',' same.','Other','Third']},
                       {'question':'English 混入'}, {'correct_index':True}, {'correct_index':4},
                       {'options':['Only one']}, {'explanation':'The text defines atomicity as'},
                       {'explanation':'This has enough words but no ending punctuation'}]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                validate_generated('comprehension',{**generated(),**change})
        with self.assertRaises(ValueError):validate_generated('opinion',generated())

    def test_adapter_protocol_is_local_only_and_removes_private_material(self):
        with TemporaryDirectory() as directory:
            root=Path(directory);binary=root/'ollama.exe';binary.write_bytes(b'fixture')
            process=Mock(stdout=StringIO('{"result":"ok"}\n'),returncode=0);process.poll.return_value=0
            def spawn(command,**kwargs):
                self.assertNotIn('http',str(command))
                source=Path(command[command.index('--input')+1]);self.assertIn('source',source.read_text())
                output=Path(command[command.index('--output')+1])
                output.write_text(json.dumps({'draft':generated(),'metadata':{'model':MODEL,'weights_digest':WEIGHTS,'manifest_sha256':MANIFEST_SHA256}}))
                return process
            from django.conf import settings
            with override_settings(LOCAL_DIR=root,LOCAL_SUMMARY_OLLAMA=binary),patch('classroom.local_poll_generator.ProcessTree'),patch('classroom.local_poll_generator.subprocess.Popen',side_effect=spawn):
                self.assertEqual(LocalPollGenerator().generate('source','comprehension','en'),generated())
            self.assertEqual(list((root/'poll-generation').iterdir()),[])


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class GenerationViewTests(fixtures.PollFixture,TestCase):
    def setUp(self):self.prepare_polls();self.client.force_login(self.teacher)

    def test_unavailable_real_adapter_preserves_form_without_creating_poll(self):
        with override_settings(LOCAL_ASR_PYTHON=Path('missing-local-runtime.exe')),patch('classroom.local_poll_generator.subprocess.Popen') as spawn:
            response=self.client.post(self.purl('poll-create'),{'kind':'comprehension','language':'en','material':'Source retained for explicit retry.'})
            self.assertContains(response,'local model is unavailable',status_code=503)
            self.assertEqual(response.context['form']['material'].value(),'Source retained for explicit retry.')
            spawn.assert_not_called()
        self.assertEqual(Poll.objects.count(),2)

    def test_invalid_output_preserves_material_and_does_not_save(self):
        bad={**generated(),'explanation':'The source defines it as'}
        provider=Mock();provider.generate.return_value=bad
        with patch('classroom.poll_services.get_poll_generator',return_value=provider):
            response=self.client.post(self.purl('poll-create'),{'kind':'comprehension','language':'en','material':'Source retained for invalid output.'})
        self.assertEqual(response.status_code,400)
        self.assertEqual(response.context['form']['material'].value(),'Source retained for invalid output.')
        self.assertContains(response,'No usable draft was saved',status_code=400)
        self.assertEqual(Poll.objects.count(),2)

    def test_generated_poll_is_draft_hidden_from_student_before_separate_publish(self):
        provider=Mock();provider.generate.return_value=generated()
        with patch('classroom.poll_services.get_poll_generator',return_value=provider):
            response=self.client.post(self.purl('poll-create'),{'kind':'comprehension','language':'en','material':'A stack is last in, first out.'})
        self.assertEqual(response.status_code,302);poll=Poll.objects.latest('pk')
        self.assertEqual((poll.origin,poll.status,poll.language),('ai','draft','en'))
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.purl('poll-detail',poll)).status_code,404)
        self.assertEqual(self.client.get(self.purl('poll-state',poll)).status_code,404)

    def test_hebrew_existing_draft_edit_publish_and_vote_remain_supported(self):
        data=self.draft_data(question='איזו אפשרות מתאימה?',option_0='ראשונה',option_1='שנייה',option_2='שלישית',option_3='רביעית',explanation='זהו הסבר לדוגמה בעברית.')
        self.assertEqual(self.client.post(self.purl('poll-edit'),data).status_code,302)
        self.comp.refresh_from_db()
        self.assertEqual(self.client.post(self.purl('poll-publish'),{'version':self.comp.version}).status_code,302)
        self.client.force_login(self.student)
        self.assertContains(self.client.get(self.purl('poll-detail')),'איזו אפשרות מתאימה?')
        self.assertEqual(self.client.post(self.purl('poll-vote'),{'option_index':1}).status_code,302)
