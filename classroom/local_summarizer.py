"""Supervised local-only summarizer. Plaintext IPC is private and short-lived."""
import json
import math
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
from django.conf import settings
from .summary_contract import MODEL, WEIGHTS, MANIFEST_SHA256, PROMPT_VERSION, validate_summary, SummaryLanguageError
from .process_tree import ProcessTree


class SummaryFailure(Exception):
    def __init__(self, code):
        super().__init__(code); self.code = code


def validate_result(result, language):
    try:
        validate_summary({'paragraph':result['paragraph'], 'key_points':result['key_points']}, language)
        meta = result['metadata']
        if (meta.get('model') != MODEL or meta.get('weights_digest') != WEIGHTS
                or meta.get('manifest_sha256') != MANIFEST_SHA256 or meta.get('prompt_version') != PROMPT_VERSION):
            raise ValueError('Unexpected model')
        seconds = result['summary_seconds']
        if type(seconds) not in (float, int) or not math.isfinite(seconds) or seconds < 0:
            raise ValueError('Invalid timing')
        return result
    except SummaryLanguageError:
        raise SummaryFailure('summary_language') from None
    except (KeyError, TypeError, ValueError):
        raise SummaryFailure('summary_output') from None


class LocalQwenSummarizer:
    def summarize(self, transcript, language, *, work_dir, deadline, on_event, on_tick):
        runtime = Path(settings.LOCAL_ASR_PYTHON)
        binary = Path(settings.LOCAL_SUMMARY_OLLAMA)
        if not runtime.is_file() or not binary.is_file(): raise SummaryFailure('summary_runtime')
        source = Path(work_dir)/'summary.input.json'
        target = Path(work_dir)/'summary.pending.json'
        command = [str(runtime), '-u', str(settings.BASE_DIR/'classroom/local_summary_runner.py'),
            '--input', str(source), '--output', str(target), '--ollama', str(binary),
            '--models', str(settings.LOCAL_SUMMARY_MODELS), '--deadline', str(deadline), '--parent-pid', str(os.getpid())]
        process = None
        tree = None
        try:
            target.unlink(missing_ok=True)
            source.write_text(json.dumps({'text':transcript, 'language':language}, ensure_ascii=False), encoding='utf-8')
            tree = ProcessTree()
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            tree.attach(process.pid)
            events = queue.Queue(maxsize=2048)
            def read_events():
                try:
                    for line in process.stdout:
                        if len(line)>8192: break
                        events.put(line)
                finally: events.put(None)
            threading.Thread(target=read_events, daemon=True).start()
            success = False
            while True:
                on_tick()
                if time.monotonic() >= deadline: raise SummaryFailure('timeout')
                try: line = events.get(timeout=.2)
                except queue.Empty: continue
                if line is None: break
                event = json.loads(line)
                if event.get('result') == 'failed': raise SummaryFailure(event.get('code', 'summary_failed'))
                if event.get('result') == 'ok': success = True
                else: on_event(event)
            process.wait(timeout=max(.1, deadline-time.monotonic()))
            if not success or process.returncode:
                raise SummaryFailure('timeout' if time.monotonic()>=deadline else 'summary_failed')
            if not target.is_file() or target.stat().st_size > 20000: raise SummaryFailure('summary_output')
            return validate_result(json.loads(target.read_text(encoding='utf-8')), language)
        finally:
            if tree is not None: tree.close()
            if process is not None:
                if process.poll() is None: process.kill()
                process.wait(timeout=3); process.stdout.close()
            source.unlink(missing_ok=True); target.unlink(missing_ok=True)
