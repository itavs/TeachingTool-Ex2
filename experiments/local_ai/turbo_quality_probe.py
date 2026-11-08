"""Local full-recording turbo experiments, separate from website settings.

Run using .ai-lab/venv/Scripts/python.exe from the project root. Downloads only
the public CTranslate2 model; inference is then forced offline. Raw results,
model files and audio copies remain in ignored .ai-lab directories.
"""
from datetime import datetime, timezone
import hashlib
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import wave

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / '.ai-lab'
REPO = 'dropbox-dash/faster-whisper-large-v3-turbo'
os.environ.update(HF_HOME=str(LAB/'hf-cache'), HF_HUB_DISABLE_TELEMETRY='1', HF_HUB_DISABLE_XET='1')
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--clip', choices=['static', 'short'], default='static')
    parser.add_argument('--local-only', action='store_true', help='Verify/reuse the downloaded checkpoint without network access.')
    args = parser.parse_args()
    from classroom.process_lock import exclusive_lock
    run = LAB/f'results/{args.clip}-turbo'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run.mkdir(parents=True)
    model_dir = LAB/'models/faster-whisper-large-v3-turbo'
    names = ['config.json', 'model.bin', 'tokenizer.json', 'vocabulary.json', 'preprocessor_config.json']
    started = time.perf_counter()
    if args.local_only:
        for key in ['HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE']:
            os.environ[key] = '1'
        previous = sorted((LAB/'results/static-turbo').glob('*/model-source.json'))[-1]
        manifest = json.loads(previous.read_text(encoding='utf-8'))
        for name in names:
            with (model_dir/name).open('rb') as source_file:
                if hashlib.file_digest(source_file, 'sha256').hexdigest() != manifest['sha256'][name]:
                    raise ValueError('Local model file does not match the previously downloaded revision')
        manifest = {**manifest, 'local_reuse': True, 'verification_seconds': time.perf_counter()-started}
        print(json.dumps({'verified_local_revision': manifest['revision']}), flush=True)
    else:
        from huggingface_hub import HfApi, snapshot_download
        info = HfApi().model_info(REPO, files_metadata=True, token=False)
        manifest = {'repo': REPO, 'revision': info.sha, 'files': [
            {'name': f.rfilename, 'bytes': f.size} for f in info.siblings if f.rfilename in names]}
        print(json.dumps({'download': manifest}), flush=True)
        snapshot_download(REPO, revision=info.sha, token=False, allow_patterns=names, local_dir=model_dir)
        manifest['download_seconds'] = time.perf_counter()-started
        manifest['sha256'] = {}
        for name in names:
            with (model_dir/name).open('rb') as source_file:
                manifest['sha256'][name] = hashlib.file_digest(source_file, 'sha256').hexdigest()
    (run/'model-source.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    for key in ['HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE']:
        os.environ[key] = '1'
    import av
    import psutil
    source = Path.home()/'Downloads'/('SHORT-EXPLAIN.mp4' if args.clip=='short' else 'STATIC-EXPLNATION.mp4')
    audio = run/f'{args.clip}-full.wav'
    samples = 0
    with av.open(str(source), format='mov', options={'protocol_whitelist': 'file'}) as media, wave.open(str(audio), 'wb') as target:
        target.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
        resampler = av.AudioResampler(format='s16', layout='mono', rate=16000)
        for frame in media.decode(audio=0):
            for converted in resampler.resample(frame):
                target.writeframes(bytes(converted.planes[0])[:converted.samples*2])
                samples += converted.samples
        for converted in resampler.resample(None):
            target.writeframes(bytes(converted.planes[0])[:converted.samples*2])
            samples += converted.samples
    handle = os.add_dll_directory(str(LAB/'ollama/lib/ollama/cuda_v12'))
    from faster_whisper import WhisperModel
    observations = []
    stopping = threading.Event()
    process = psutil.Process()
    def monitor():
        while not stopping.is_set():
            record = {'elapsed': time.perf_counter()-measurement_start, 'rss_bytes': process.memory_info().rss}
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu',
                    '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=3,
                    creationflags=subprocess.CREATE_NO_WINDOW)
                record['gpu'] = [int(v.strip()) for v in result.stdout.strip().split(',')]
            except Exception as error:
                record['gpu_sample_error'] = type(error).__name__
            observations.append(record)
            stopping.wait(1)
    with exclusive_lock(ROOT/'.local/videos/.decoder.lock'):
        measurement_start = time.perf_counter()
        watcher = threading.Thread(target=monitor, daemon=True)
        watcher.start()
        output = {'repo': REPO, 'revision': manifest['revision'], 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'audio_sha256': hashlib.sha256(audio.read_bytes()).hexdigest(), 'audio_seconds': samples/16000,
            'versions': {name: importlib.metadata.version(name) for name in ['faster-whisper', 'ctranslate2', 'av']},
            'device': 'cuda', 'compute_type': 'float16', 'cpu_threads': 8, 'num_workers': 1,
            'task': 'transcribe', 'language': None, 'beam_size': 5, 'vad_filter': False,
            'condition_on_previous_text': False, 'human_reference': None}
        try:
            started = time.perf_counter()
            model = WhisperModel(str(model_dir), device='cuda', compute_type='float16',
                local_files_only=True, cpu_threads=8, num_workers=1)
            output['model_load_seconds'] = time.perf_counter()-started
            print(json.dumps({'stage': 'transcribing', 'load_seconds': output['model_load_seconds']}), flush=True)
            started = time.perf_counter()
            iterator, detection = model.transcribe(str(audio), language=None, task='transcribe', beam_size=5,
                vad_filter=False, condition_on_previous_text=False)
            segments = []
            for segment in iterator:
                segments.append({'start': segment.start, 'end': segment.end, 'text': segment.text})
            output.update(success=True, segments=segments, transcript=' '.join(s['text'].strip() for s in segments),
                detected_language=detection.language, language_probability=detection.language_probability,
                transcription_seconds=time.perf_counter()-started)
        except Exception as error:
            output.update(success=False, exception_type=type(error).__name__)
        finally:
            stopping.set(); watcher.join(timeout=4)
            output['model_and_inference_seconds'] = time.perf_counter()-measurement_start
            output['resource_samples'] = observations
            output['rss_peak_sampled_bytes'] = max((s['rss_bytes'] for s in observations), default=None)
            output['gpu_total_used_peak_sampled_mib'] = max((s['gpu'][0] for s in observations if 'gpu' in s), default=None)
            (run/'turbo-full.json').write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
            handle.close()
        print(json.dumps({'run': str(run), 'success': output['success'],
            'seconds': output.get('transcription_seconds'), 'gpu_peak_mib': output['gpu_total_used_peak_sampled_mib']}), flush=True)


if __name__ == '__main__':
    main()
