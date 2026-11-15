"""Bounded adapter for the pinned, already installed local model. No remote fallback."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from django.conf import settings
from django.utils import timezone
from .homework_provider import ReviewUnavailable
from .homework_contract import PROCESS_SECONDS, capacity_error
from .process_tree import ProcessTree
from .summary_contract import MODEL, WEIGHTS, MANIFEST_SHA256, verify_local_model


class LocalHomeworkReviewer:
    def __init__(self):
        self.rubric = ''
        self.deadline = None
        self.metadata = {'provider': 'experimental-local-qwen', 'stages': {}}

    def available(self, language):
        if language != 'en':
            return False
        try:
            verify_local_model(settings.LOCAL_SUMMARY_MODELS)
            return Path(settings.LOCAL_SUMMARY_OLLAMA).is_file() and Path(settings.LOCAL_ASR_PYTHON).is_file()
        except (OSError, ValueError):
            return False

    def configure(self, job):
        self.rubric = job.rubric_snapshot
        elapsed = (timezone.now()-job.started_at).total_seconds() if job.started_at else 0
        self.deadline = time.monotonic() + max(0,PROCESS_SECONDS-elapsed)
        error = capacity_error(job.instructions_snapshot,job.criteria_snapshot,self.rubric,
                               job.target_text,[p['text'] for p in job.peer_snapshots])
        if error:
            raise ReviewUnavailable(error)

    def assess_submission(self,instructions,criteria,submission,language):
        return self._run('individual',instructions,criteria,submission,[],language)

    def compare_submissions(self,instructions,criteria,target,peers,language):
        return self._run('comparison',instructions,criteria,target,peers,language)

    def _run(self,stage,instructions,criteria,target,peers,language):
        if language != 'en' or self.deadline is None:
            raise ReviewUnavailable('English configured review required')
        root = settings.LOCAL_DIR/'homework-processing'; root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as folder:
            source = Path(folder)/'input.json'; output = Path(folder)/'output.json'
            source.write_text(json.dumps({'stage':stage,'instructions':instructions,'criteria':criteria,
                'rubric':self.rubric,'target':target,'peers':peers},ensure_ascii=False),encoding='utf-8')
            tree = ProcessTree(); process = None
            started = time.monotonic()
            try:
                command = [str(settings.LOCAL_ASR_PYTHON),'-u',str(settings.BASE_DIR/'classroom/local_homework_runner.py'),
                    '--input',str(source),'--output',str(output),'--ollama',str(settings.LOCAL_SUMMARY_OLLAMA),
                    '--models',str(settings.LOCAL_SUMMARY_MODELS),'--deadline',str(self.deadline),
                    '--parent-pid',str(os.getpid())]
                process = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                    text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
                tree.attach(process.pid)
                stdout,_ = process.communicate(timeout=max(.1,self.deadline-time.monotonic()))
                if process.returncode or not output.is_file() or output.stat().st_size > 100000:
                    events=[json.loads(line) for line in stdout.splitlines()]
                    self.metadata['failure_code']=next((e.get('code') for e in events if e.get('result')=='failed'),'process_failed')
                    raise ReviewUnavailable('Local processing failed, was busy, or reached the 180-second limit.')
                if not any(json.loads(line).get('result')=='ok' for line in stdout.splitlines()):
                    raise ReviewUnavailable('Local processing failed.')
                result = json.loads(output.read_text(encoding='utf-8'))
                metadata = result['metadata']
                if (metadata.get('model'),metadata.get('weights_digest'),metadata.get('manifest_sha256')) != (MODEL,WEIGHTS,MANIFEST_SHA256):
                    raise ReviewUnavailable('Unexpected model identity')
                self.metadata['stages'][stage] = metadata
                self.metadata['wall_seconds'] = sum(x['generation_seconds'] for x in self.metadata['stages'].values())
                return result['draft']
            except subprocess.TimeoutExpired:
                raise ReviewUnavailable('Local processing reached the 180-second limit.') from None
            finally:
                self.metadata['last_stage_wall_seconds'] = time.monotonic()-started
                tree.close()
                if process is not None:
                    if process.poll() is None: process.kill()
                    process.communicate(timeout=3)
