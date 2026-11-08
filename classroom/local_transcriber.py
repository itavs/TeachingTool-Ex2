"""Supervise the existing local ASR environment without adding website packages."""
import json
import math
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
from django.conf import settings
from .asr_checkpoint import is_expected_metadata


class TranscriptionFailure(Exception):
    def __init__(self,code):
        super().__init__(code);self.code=code


def validate_result(result):
    if not isinstance(result,dict) or not isinstance(result.get('text'),str) or not result['text'].strip():
        raise TranscriptionFailure('asr_output')
    if result.get('language') not in ['he','en'] or not isinstance(result.get('segments'),list):
        raise TranscriptionFailure('asr_output')
    if not is_expected_metadata(result.get('metadata')) or result['metadata'].get('device')!='cuda' or result['metadata'].get('compute_type')!='float16':
        raise TranscriptionFailure('asr_output')
    for key in ['model_load_seconds','transcription_seconds']:
        value=result.get(key)
        if not isinstance(value,(float,int)) or not math.isfinite(value) or value<0:raise TranscriptionFailure('asr_output')
    for segment in result['segments']:
        if not isinstance(segment,dict) or not isinstance(segment.get('text'),str):raise TranscriptionFailure('asr_output')
        start,end=segment.get('start'),segment.get('end')
        if any(type(value) not in (float,int) or not math.isfinite(value) for value in [start,end]) or not 0<=start<=end<=270:
            raise TranscriptionFailure('asr_output')
    return result


class LocalWhisperTranscriber:
    def transcribe(self,audio_path,*,deadline,on_event,on_tick):
        audio=Path(audio_path)
        output=audio.with_name('transcript.pending.json')
        runtime=Path(settings.LOCAL_ASR_PYTHON)
        if not runtime.is_file():raise TranscriptionFailure('asr_runtime')
        if not Path(settings.LOCAL_ASR_MODEL).is_dir():raise TranscriptionFailure('asr_model_missing')
        command=[str(runtime),'-u',str(settings.BASE_DIR/'classroom/local_asr_runner.py'),
            '--audio',str(audio),'--output',str(output),'--model',str(settings.LOCAL_ASR_MODEL),
            '--cuda-dll',str(settings.LOCAL_ASR_CUDA_DLL),'--deadline',str(deadline),'--parent-pid',str(os.getpid())]
        env={**os.environ,'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_HUB_DISABLE_TELEMETRY':'1','PYTHONUTF8':'1'}
        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
        process=None
        try:
            output.unlink(missing_ok=True)
            process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding='utf-8',
                env=env,creationflags=creationflags)
            events=queue.Queue(maxsize=2048)
            def read_events():
                try:
                    for line in process.stdout:
                        if len(line)>8192:break
                        events.put(line)
                finally:events.put(None)
            reader=threading.Thread(target=read_events,daemon=True);reader.start()
            success=False
            while True:
                on_tick()
                if time.monotonic()>=deadline:raise TranscriptionFailure('timeout')
                try:line=events.get(timeout=.2)
                except queue.Empty:continue
                if line is None:break
                event=json.loads(line)
                if event.get('result')=='failed':raise TranscriptionFailure(event.get('code','asr_failed'))
                if event.get('result')=='ok':success=True
                else:on_event(event)
            process.wait(timeout=max(.1,deadline-time.monotonic()))
            if process.returncode!=0 or not success:
                raise TranscriptionFailure('timeout' if time.monotonic()>=deadline else 'asr_failed')
            if not output.is_file() or output.stat().st_size>2_000_000:raise TranscriptionFailure('asr_output')
            return validate_result(json.loads(output.read_text(encoding='utf-8')))
        finally:
            if process is not None:
                if process.poll() is None:process.kill()
                process.wait(timeout=3)
                process.stdout.close()
            output.unlink(missing_ok=True)
