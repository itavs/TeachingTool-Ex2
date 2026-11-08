"""Isolated CPU media decoding. No Django model import or AI inference."""
import math
import multiprocessing as mp
import os
from pathlib import Path
import threading
import time
import wave
import av


class MediaFailure(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def inspect_mp4(path, max_seconds=240):
    with Path(path).open('rb') as stream:
        header = stream.read(4096)
    # MP4 requires an ftyp box; forcing the MOV/MP4 demuxer avoids playlists.
    offset = 0
    brands = []
    while offset + 16 <= len(header):
        size = int.from_bytes(header[offset:offset+4], 'big')
        if size < 8 or offset + size > len(header): break
        if header[offset+4:offset+8] == b'ftyp':
            brands = [header[offset+8:offset+12]] + [header[i:i+4] for i in range(offset+16, offset+size, 4)]
            break
        offset += size
    if not any(b in {b'isom', b'iso2', b'iso3', b'iso4', b'iso5', b'iso6', b'mp41', b'mp42', b'avc1', b'M4V ', b'dash'} for b in brands):
        raise MediaFailure('invalid_mp4')
    options = {'protocol_whitelist':'file', 'enable_drefs':'0', 'use_absolute_path':'0', 'err_detect':'explode'}
    try:
        with av.open(str(path), format='mov', options=options) as source:
            if not source.streams.video: raise MediaFailure('no_video')
            if not source.streams.audio: raise MediaFailure('no_audio')
            durations = [float(source.duration / av.time_base)] if source.duration is not None else []
            for stream in source.streams:
                if stream.duration is not None and stream.time_base:
                    durations.append(float(stream.duration * stream.time_base))
            if not durations or any(not math.isfinite(x) or x <= 0 for x in durations):
                raise MediaFailure('unknown_duration')
            seconds = max(durations)
            if seconds > max_seconds: raise MediaFailure('too_long')
            return {'video_seconds':seconds, 'audio_streams':len(source.streams.audio), 'video_streams':len(source.streams.video)}
    except av.FFmpegError:
        raise MediaFailure('invalid_mp4') from None


def extract_audio(path, output, max_seconds=240):
    """Decode video too for integrity, never analyze visual content; first audio track."""
    samples, video_frames = 0, 0
    options = {'protocol_whitelist':'file', 'enable_drefs':'0', 'use_absolute_path':'0', 'err_detect':'explode'}
    try:
        with av.open(str(path), format='mov', options=options) as source, wave.open(str(output), 'wb') as target:
            target.setnchannels(1); target.setsampwidth(2); target.setframerate(16000)
            resampler = av.AudioResampler(format='s16', layout='mono', rate=16000)
            audio_stream = source.streams.audio[0]
            streams = [*source.streams.video, audio_stream]
            def save(converted):
                nonlocal samples
                samples += converted.samples
                if samples > max_seconds * 16000: raise MediaFailure('too_long')
                target.writeframes(bytes(converted.planes[0])[:converted.samples*2])
            for packet in source.demux(streams):
                if packet.is_corrupt: raise MediaFailure('decode_failed')
                for frame in packet.decode():
                    if frame.time is not None and frame.time > max_seconds:
                        raise MediaFailure('too_long')
                    if isinstance(frame, av.AudioFrame):
                        for converted in resampler.resample(frame): save(converted)
                    else:
                        video_frames += 1
            for converted in resampler.resample(None): save(converted)
        if samples == 0: raise MediaFailure('empty_audio')
        if video_frames == 0: raise MediaFailure('decode_failed')
        with wave.open(str(output), 'rb') as result:
            if result.getnframes() != samples: raise MediaFailure('decode_failed')
        return {'audio_seconds':samples/16000, 'audio_samples':samples, 'video_frames_checked':video_frames}
    except av.FFmpegError:
        raise MediaFailure('decode_failed') from None


def media_child(sender, source, output, max_seconds, deadline):
    # Avoid an orphan decoder after a hard-killed worker; parent also enforces deadline.
    def watchdog():
        parent = mp.parent_process()
        while True:
            if time.monotonic() >= deadline or (parent is not None and not parent.is_alive()):
                os._exit(3)
            time.sleep(.25)
    threading.Thread(target=watchdog, daemon=True).start()
    stage = 'validating'
    try:
        # Secondary OS lock also prevents overlapping orphan/new decoders.
        from .video_storage import exclusive_lock
        with exclusive_lock(Path(source).parent.parent / '.decoder.lock'):
            metadata = inspect_mp4(source, max_seconds)
            stage = 'extracting'
            sender.send({'stage':stage, **metadata})
            result = extract_audio(source, output, max_seconds)
            sender.send({'result':'ok', **metadata, **result})
    except MediaFailure as error:
        sender.send({'result':'failed', 'stage':stage, 'code':error.code})
    except Exception:
        sender.send({'result':'failed', 'stage':stage, 'code':'processing_error'})
    finally:
        sender.close()
