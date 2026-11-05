"""Decode a user-supplied video to a private 16-kHz mono WAV using PyAV."""
import argparse
import json
from pathlib import Path
import time
import wave
import av

parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
start = time.perf_counter()
samples = 0
with av.open(str(args.input)) as source, wave.open(str(args.output), "wb") as output:
    output.setnchannels(1)
    output.setsampwidth(2)
    output.setframerate(16000)
    resampler = av.AudioResampler(format="s16", layout="mono", rate=16000)
    for frame in source.decode(audio=0):
        for converted in resampler.resample(frame):
            output.writeframes(converted.to_ndarray().tobytes())
            samples += converted.samples
    for converted in resampler.resample(None):
        output.writeframes(converted.to_ndarray().tobytes())
        samples += converted.samples
print(json.dumps({"duration_s": samples / 16000, "extraction_wall_s": time.perf_counter() - start}))
