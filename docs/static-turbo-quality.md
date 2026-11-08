# Full STATIC: medium vs large-v3-turbo — 2026-11-08

## Approved isolated experiment

Downloaded public CTranslate2 model [dropbox-dash/faster-whisper-large-v3-turbo](https://huggingface.co/dropbox-dash/faster-whisper-large-v3-turbo/tree/main), derived from OpenAI Whisper large-v3-turbo. No hosted inference, payment, application-provider switch, website transcription or medium rerun occurred. Full source audio was processed, not the previous crop. Original Downloads media and the saved website medium transcript remain unchanged. Model/audio/raw outputs remain under ignored .ai-lab; Gemini experiment files remain untouched.

Exact revision: `0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf`. Downloaded 1,621,665,983 bytes in 29.500 s (includes metadata/download, not inference); model.bin 1,617,884,929 bytes. SHA-256 for each model/config/tokenizer file is recorded in the ignored model-source.json.

Reproduction: run `.ai-lab/venv/Scripts/python.exe experiments/local_ai/turbo_quality_probe.py` from project root. This downloads/reuses the pinned-by-resolved-revision public checkpoint, then sets offline flags and local_files_only. Runtime remains faster-whisper 1.2.1, CTranslate2 4.8.5, PyAV 16.0.0, CUDA float16, threads 8, workers 1, task transcribe, language=None, beam 5, VAD false, condition_on_previous_text false. These match the existing full-medium job. No initial prompt/glossary, translation, correction or summarization. The source copy is resampled to 16-kHz mono PCM exactly as in production. Sequential ASR is protected by the shared exclusive lock; no CPU fallback exists.

## Measurements (single runs, not controlled speed benchmark)

| Measurement | Existing full medium | New full turbo |
|---|---:|---:|
| Audio duration | 235.288 s | 235.288 s |
| Model load | 1.578 s | 1.822 s |
| Transcription | 190.870 s | 54.893 s |
| Detected language | he | he |
| Processing including load/extraction | 195.856 s website worker | Not directly comparable: isolated experiment |

Turbo model-load/inference observation window: 56.754 s (includes monitoring teardown). Peak sampled process RSS: 1,397,211,136 bytes (1.301 GiB). Peak sampled total GPU memory: 2,723 MiB, out of 8,151 MiB. Samples roughly once/second plus nvidia-smi overhead; these are sampled maxima, not allocation-profiler peaks. GPU memory is device-wide including display/other processes, not exclusive model VRAM. RAM covers the experiment process, not whole-system usage; model download/hash and extraction precede monitoring. GPU use is supported by explicit CUDA-only loading, successful inference and utilization samples.

## Comparison window: original 00:55–01:35

The ASR timestamps refer to the full original video. Segment boundaries differ between models. Each side includes all segments intersecting [55,95); edge segments extend slightly outside the requested interval. No word-level clipping, invented alignment or text rewriting was applied. Bold marks segments intersecting the requested listening window 01:17.560–01:22.160, not an assertion that their individual words are aligned exactly.

Raw side-by-side transcript outputs are retained only in ignored local experiment artifacts and are excluded from the published repository.

## Meaning and code-term review — not source-accuracy acceptance

Turbo is more readable around separate variables created for each object and removes the medium's dishwasher, replacement characters and unrelated foreign fragments in this window. It includes Object in Latin characters here; the full output also contains new car, year, name, color, static, public, int, minimum car price and mycar. This does not prove exact identifier spelling/casing/spacing or preservation of words actually spoken.

At 53.46–57.46 turbo says the variables belong to the object; at 58.02–61.74 it says "אם לא שלחים למשהו, אם שלחים ל-Object", which is unclear and contains a negation. Medium's corresponding region has corruption rather than a usable statement. Neither provides a reliable basis to verify whether the speaker said belongs or does not belong there. Do not silently repair שלחים to שייכים or remove לא.

Later turbo text distinguishes per-object variables from a proposed shared variable and explicitly retains "לא שייך לאובייקט". Medium's later text also retains that distinction in places. These are internal coherence observations against the programming topic, not human-verified transcription fidelity. The localized unclear negation remains material: disappearance of a nonsensical token alone is not an accuracy pass. Listening/reference verification is required especially at 00:58–01:02 and 01:17.560–01:22.160. No WER or correctness percentage is available.

The exact 4.6-second listening copy focus-77.560-82.160.wav and full turbo JSON are private ignored experiment artifacts. Review the target sentence with surrounding context if the narrow clip cuts speech. Recommendation: review turbo with the user before changing the website model; current active website medium remains unchanged, and summarization has not started.
