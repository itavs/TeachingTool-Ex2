"""Offline paired medium ASR probe; writes only to ignored .ai-lab results.

Uses an experimental audio copy, never updates website data or model settings.
Run with the existing .ai-lab/venv Python from the project root.
"""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import time
import wave
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
for key in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY'):
    os.environ[key] = '1'
sys.path.insert(0, str(ROOT))
from classroom.process_lock import exclusive_lock


def main():
    import av
    source = Path.home() / 'Downloads' / 'STATIC-EXPLNATION.mp4'
    start, end = 55, 95
    run = ROOT / '.ai-lab/results/static-quality' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run.mkdir(parents=True)
    audio = run / 'static-0055-0135.wav'
    # Match production decoding/resampling, then crop exact sample indices.
    pcm = bytearray()
    with av.open(str(source), format='mov', options={'protocol_whitelist': 'file'}) as media:
        resampler = av.AudioResampler(format='s16', layout='mono', rate=16000)
        for frame in media.decode(audio=0):
            for converted in resampler.resample(frame):
                pcm.extend(bytes(converted.planes[0])[:converted.samples * 2])
        for converted in resampler.resample(None):
            pcm.extend(bytes(converted.planes[0])[:converted.samples * 2])
    with wave.open(str(audio), 'wb') as target:
        target.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
        target.writeframes(pcm[start * 32000:end * 32000])
    del pcm
    versions = {name: importlib.metadata.version(name) for name in ['faster-whisper', 'ctranslate2', 'av']}
    handle = os.add_dll_directory(str(ROOT / '.ai-lab/ollama/lib/ollama/cuda_v12'))
    from faster_whisper import WhisperModel
    with exclusive_lock(ROOT / '.local/videos/.decoder.lock'):
        loading = time.perf_counter()
        model = WhisperModel(str(ROOT / '.ai-lab/models/faster-whisper-medium'), device='cuda',
                             compute_type='float16', local_files_only=True, cpu_threads=8, num_workers=1)
        load_seconds = time.perf_counter() - loading
        for name, language in [('auto', None), ('forced-he', 'he')]:
            started = time.perf_counter()
            result = {'model': 'Systran/faster-whisper-medium',
                      'revision': '08e178d48790749d25932bbc082711ddcfdfbc4f',
                      'source_start_seconds': start, 'source_end_seconds': end,
                      'audio_sha256': hashlib.sha256(audio.read_bytes()).hexdigest(),
                      'versions': versions, 'device': 'cuda', 'compute_type': 'float16',
                      'language_argument': language, 'task': 'transcribe', 'beam_size': 5,
                      'vad_filter': False, 'condition_on_previous_text': False,
                      'model_load_seconds': load_seconds, 'manual_reference': None}
            try:
                iterator, info = model.transcribe(str(audio), language=language, task='transcribe',
                    beam_size=5, vad_filter=False, condition_on_previous_text=False)
                result['segments'] = [{'start': s.start, 'end': s.end, 'text': s.text} for s in iterator]
                result['transcript'] = ' '.join(s['text'].strip() for s in result['segments']).strip()
                result['detected_language'] = info.language
                result['language_probability'] = info.language_probability
                result['success'] = True
            except Exception as error:
                result.update(success=False, exception_type=type(error).__name__)
            result['processing_seconds'] = time.perf_counter() - started
            (run / f'{name}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps({'run': str(run), 'case': name, 'success': result['success'],
                              'seconds': result['processing_seconds']}), flush=True)
    handle.close()


if __name__ == '__main__':
    main()
