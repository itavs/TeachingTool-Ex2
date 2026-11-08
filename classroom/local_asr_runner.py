"""Local-only CLI for the existing ASR Python, not the website interpreter.

Stdout contains protocol events only; transcript text goes to a private file.
No model downloads, HTTP client, summarization, or CPU fallback is provided.
"""
import argparse
import gc
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import threading
import time

def emit(**event):
    print(json.dumps(event,ensure_ascii=True),flush=True)


def main():
    parser=argparse.ArgumentParser()
    for name in ['audio','output','model','cuda-dll']:parser.add_argument('--'+name,required=True)
    parser.add_argument('--deadline',type=float,required=True)
    parser.add_argument('--parent-pid',type=int,required=True)
    args=parser.parse_args()
    for key in ['HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE','HF_HUB_DISABLE_TELEMETRY']:
        os.environ[key]='1'
    stage='loading_asr';dll_handle=None;model=None
    try:
        import psutil
        parent=psutil.Process(args.parent_pid)
        def watchdog():
            while True:
                if time.monotonic()>=args.deadline or not parent.is_running():os._exit(3)
                time.sleep(.25)
        threading.Thread(target=watchdog,daemon=True).start()
        sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
        from classroom.process_lock import exclusive_lock
        from classroom.asr_checkpoint import REPO, REVISION, verify_checkpoint
        with exclusive_lock(Path(args.audio).parent.parent/'.decoder.lock'):
            emit(stage=stage)
            required={'faster-whisper':'1.2.1','ctranslate2':'4.8.5','av':'16.0.0'}
            if any(importlib.metadata.version(name)!=version for name,version in required.items()):
                emit(result='failed',stage=stage,code='asr_versions');return 1
            model_path=Path(args.model)
            try:
                verify_checkpoint(model_path)
            except (OSError, ValueError):
                emit(result='failed',stage=stage,code='asr_model_missing');return 1
            if os.name=='nt':dll_handle=os.add_dll_directory(args.cuda_dll)
            import ctranslate2
            if ctranslate2.get_cuda_device_count()<1:
                emit(result='failed',stage=stage,code='asr_gpu');return 1
            from faster_whisper import WhisperModel
            started=time.perf_counter()
            model=WhisperModel(str(model_path),device='cuda',compute_type='float16',local_files_only=True,cpu_threads=8,num_workers=1)
            load_s=time.perf_counter()-started
            metadata={'repo':REPO,'revision':REVISION,'sha256_verified':True,**required,
                'device':'cuda','compute_type':'float16','beam_size':5,'task':'transcribe',
                'vad_filter':False,'condition_on_previous_text':False,'language':'auto'}
            stage='transcribing';emit(stage=stage,model_load_seconds=load_s,model_loaded=metadata)
            started=time.perf_counter()
            iterator,info=model.transcribe(args.audio,language=None,task='transcribe',beam_size=5,
                vad_filter=False,condition_on_previous_text=False)
            segments=[]
            for segment in iterator:
                segments.append({'start':segment.start,'end':segment.end,'text':segment.text})
                emit(progress_seconds=segment.end)
            elapsed=time.perf_counter()-started
            text=' '.join(s['text'].strip() for s in segments).strip()
            if not text:
                emit(result='failed',stage=stage,code='asr_empty');return 1
            if info.language not in ['he','en']:
                emit(result='failed',stage=stage,code='asr_language');return 1
            result={'text':text,'segments':segments,'language':info.language,
                'model_load_seconds':load_s,'transcription_seconds':elapsed,
                'metadata':metadata}
            encoded=json.dumps(result,ensure_ascii=False).encode('utf-8')
            if len(encoded)>2_000_000:
                emit(result='failed',stage=stage,code='asr_output');return 1
            with Path(args.output).open('xb') as output:output.write(encoded)
            emit(result='ok');return 0
    except Exception as error:
        emit(result='failed',stage=stage,code='asr_gpu' if stage=='loading_asr' else 'asr_failed',error_class=type(error).__name__)
        return 1
    finally:
        if model is not None:del model;gc.collect()
        if dll_handle is not None:dll_handle.close()


if __name__=='__main__':raise SystemExit(main())
