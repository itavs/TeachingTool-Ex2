# Full SHORT-EXPLAIN: medium vs turbo — 2026-11-08

## Isolated offline comparison

Used the already downloaded dropbox-dash/faster-whisper-large-v3-turbo CTranslate2 model, revision 0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf. Every local model/config/tokenizer file SHA-256 was verified against the prior download manifest before loading. No network/model download or hosted inference occurred. Original SHORT-EXPLAIN.mp4 was read only; a full audio copy and raw model output are separately stored under ignored .ai-lab/results/short-turbo with a unique run directory. The baseline is the saved website medium transcript, not a new medium run.

Reproduction using existing environment/model:

```powershell
.\.ai-lab\venv\Scripts\python.exe experiments/local_ai/turbo_quality_probe.py --clip short --local-only
```

Settings match full-medium baseline: faster-whisper 1.2.1, CTranslate2 4.8.5, PyAV 16.0.0, CUDA float16, CPU threads 8, one worker, language=None, task transcribe, beam 5, VAD off, condition_on_previous_text false. No prompt/glossary, translation, post-editing or summarization. Full audio is 56.74956 seconds, 16-kHz mono PCM. Both detected English. Explicit CUDA-only construction, successful inference and sampled GPU utilization support GPU execution; no CPU fallback exists.

| Measurement | Existing medium | New turbo |
|---|---:|---:|
| Model loading | 2.837 s | 1.749 s |
| Full transcription | 12.439 s | 4.824 s |

Turbo sampled maximum process RSS: 1,487,618,048 bytes (1.385 GiB); maximum sampled total GPU-used memory 2,715 MiB / 8,151 MiB. Sampling roughly once per second is not an exact peak; GPU memory includes display/other users, and RAM is process-only. These are single runs at different times, not controlled hardware benchmarks. Medium's total website-worker time (26.666 s) includes validation/extraction/startup/cleanup and is not compared with isolated turbo inference time.

## Inheritance comparison window

Requested comparison window approximately 00:29–00:45. Include complete overlapping model segments, not invented word timestamps: medium 00:28.720–00:45.680; turbo 00:28.240–00:45.580. Differences at the excerpt's beginning are segment-boundary differences; compare within full-output context.

Raw side-by-side transcript outputs are retained only in ignored local experiment artifacts and are excluded from the published repository.

Both describe a boat class inheriting vehicle functions/data while having its own methods. The terms inheritance, class, boat and vehicle are retained in both excerpts. Elsewhere both contain object and its own instance. Turbo says "drop an anchor" where medium says "drop and anchor"; this is a plausible readability improvement, not a human-verified correction. Both retain "build and year" in the earlier attributes example; no unverified alternative is substituted. Punctuation and segment timestamps vary, and overall the English outputs are very similar. This is a text-to-text coherence comparison only: no manual reference or independent source listening was available, so word accuracy/omissions and code-term fidelity remain unverified. No WER or accuracy percentage is claimed.

The active website model remains medium; saved baseline text/segments were hash/structure verified unchanged. The 13 outstanding Gemini files were also hash verified unchanged. No commit/push or website feature change. Isolated experiment execution succeeded and the Python script compiled; website regression tests were not rerun for this experiment-only change. Review both Hebrew and English results before deciding whether to switch the website model.
