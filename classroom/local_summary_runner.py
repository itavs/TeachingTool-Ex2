"""Isolated offline Qwen child. Owns a private loopback Ollama service per job."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import urllib.request


def emit(**event):
    print(json.dumps(event), flush=True)


def main():
    parser = argparse.ArgumentParser()
    for key in ['input', 'output', 'ollama', 'models']:
        parser.add_argument('--'+key, required=True)
    parser.add_argument('--deadline', type=float, required=True)
    parser.add_argument('--parent-pid', type=int, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import psutil
    from classroom.process_lock import exclusive_lock
    from classroom.summary_contract import MODEL, SCHEMA, summary_prompt, validate_summary, verify_local_model, SummaryLanguageError
    parent = psutil.Process(args.parent_pid)
    server = None
    cleaning = threading.Lock()

    def stop_server():
        with cleaning:
            if server is not None:
                try:
                    process = psutil.Process(server.pid)
                    children = process.children(recursive=True)
                    for child in reversed(children):
                        try: child.kill()
                        except psutil.Error: pass
                    try: process.kill()
                    except psutil.Error: pass
                    psutil.wait_procs(children+[process], timeout=2)
                except psutil.Error:
                    pass

    def watchdog():
        while True:
            if time.monotonic() >= args.deadline or not parent.is_running():
                stop_server()
                os._exit(3)
            time.sleep(.25)
    threading.Thread(target=watchdog, daemon=True).start()
    stage = 'loading_sum'
    try:
        emit(stage=stage)
        metadata = verify_local_model(args.models)
        if not Path(args.ollama).is_file():
            emit(result='failed', code='summary_runtime'); return 1
        source = json.loads(Path(args.input).read_text(encoding='utf-8'))
        prompt = summary_prompt(source['text'], source['language'])
        with exclusive_lock(Path(args.input).parent.parent/'.decoder.lock'):
            # Never reuse a desktop/cloud-enabled Ollama service or accept a URL.
            with socket.socket() as reservation:
                reservation.bind(('127.0.0.1', 0))
                port = reservation.getsockname()[1]
            host = f'127.0.0.1:{port}'
            env = {**os.environ, 'OLLAMA_HOST': host, 'OLLAMA_MODELS': args.models,
                   'OLLAMA_NO_CLOUD': '1', 'OLLAMA_NUM_PARALLEL': '1',
                   'OLLAMA_MAX_LOADED_MODELS': '1', 'OLLAMA_CONTEXT_LENGTH': '8192'}
            server = subprocess.Popen([args.ollama, 'serve'], env=env,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            http = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            base = 'http://'+host
            while True:
                if server.poll() is not None:
                    emit(result='failed', code='summary_runtime'); return 1
                try:
                    with http.open(base+'/api/version', timeout=1) as response:
                        version = json.load(response)['version']
                    break
                except (OSError, ValueError): time.sleep(.1)
            if version != '0.40.14':
                emit(result='failed', code='summary_runtime'); return 1
            metadata.update(ollama_version=version, thinking=False, temperature=.1, seed=42,
                            num_ctx=8192, num_predict=768)
            request = urllib.request.Request(base+'/api/generate', data=json.dumps({
                'model': MODEL, 'prompt': prompt, 'think': False, 'format': SCHEMA,
                'stream': True, 'keep_alive': 0, 'options': {'temperature': .1, 'seed': 42,
                    'num_ctx': 8192, 'num_predict': 768}}).encode('utf-8'),
                headers={'Content-Type': 'application/json'})
            started = time.perf_counter()
            fragments = []
            final = None
            with http.open(request, timeout=max(.1, args.deadline-time.monotonic())) as response:
                for raw in response:
                    event = json.loads(raw.decode('utf-8'))
                    if event.get('error'):
                        emit(result='failed', code='summary_failed'); return 1
                    if stage == 'loading_sum':
                        stage = 'summarizing'; emit(stage=stage, model_loaded=metadata)
                    fragments.append(event.get('response', ''))
                    if sum(map(len, fragments)) > 12000:
                        emit(result='failed', code='summary_output'); return 1
                    if event.get('done'): final = event
            if not final or final.get('done_reason') != 'stop':
                emit(result='failed', code='summary_output'); return 1
            value = validate_summary(json.loads(''.join(fragments)), source['language'])
            metadata.update(load_seconds=final.get('load_duration', 0)/1e9,
                            generation_seconds=final.get('eval_duration', 0)/1e9)
            result = {**value, 'metadata': metadata, 'summary_seconds': time.perf_counter()-started}
            Path(args.output).write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
            emit(result='ok'); return 0
    except SummaryLanguageError:
        emit(result='failed', code='summary_language'); return 1
    except (FileNotFoundError, ValueError, KeyError) as error:
        emit(result='failed', code='summary_model' if stage=='loading_sum' else 'summary_output', error_class=type(error).__name__)
        return 1
    except Exception as error:
        emit(result='failed', code='summary_failed', error_class=type(error).__name__)
        return 1
    finally:
        stop_server()


if __name__ == '__main__':
    raise SystemExit(main())
