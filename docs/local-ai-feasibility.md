# Local AI Feasibility — 2026-11-05

## Scope and status

User-approved local-only feasibility work before website implementation.
No external inference, payment, driver changes, system-setting changes,
commit or push. This report is experimental evidence, not approval of a
framework, model, provider, or revised project scope.

## Machine and compatibility

- User-reported Intel Core 7 240H, Windows 64-bit, 24GB RAM.
- Observed RAM: 23.64 GiB. NVIDIA-SMI reports RTX 5050 Laptop GPU,
  8151 MiB VRAM, driver 592.82, maximum driver CUDA compatibility 13.1.
  The latter does not establish an installed CUDA Toolkit.
- No Ollama/FFmpeg command was found on PATH; the Python launcher reported
  no registered Python installations. Codex's existing Python 3.12.14 was
  used to create a separate virtual environment. The checked runtime had
  no faster-whisper, CTranslate2, PyAV or psutil installation.
- NVIDIA lists RTX 5050 at compute capability 12.0. Ollama's documented
  NVIDIA requirements are met. The actual server selected CUDA 13 and
  identified the discrete GPU at compute capability 12.0.
- CTranslate2 4.8.5 detected one CUDA device, but detection and supported-type
  enumeration did not guarantee successful inference. See failures below.

Official references: [NVIDIA GPUs](https://developer.nvidia.com/cuda/gpus),
[Ollama hardware](https://docs.ollama.com/gpu),
[Ollama Windows portable runtime](https://docs.ollama.com/windows),
[CTranslate2 releases](https://github.com/OpenNMT/CTranslate2/releases),
[faster-whisper](https://github.com/SYSTRAN/faster-whisper).

## Runtime, downloads and configuration

- Portable Ollama 0.40.14; archive 1,601,954,968 bytes from the official
  GitHub release. SHA256 verified against the published checksum:
  `65d68cade6cf6375f398b518224f8c8a15e062387f38cf477abfc848de7e7e29`.
- Qwen3 4B Q4_K_M, approximately 2.5GB; actual digest/configuration in
  `experiments/local_ai/results/environment.json`.
- One escalation in model size after quality failure: Qwen3 8B Q4_K_M,
  approximately 5.2GB; configuration/digest in the `qwen3-8b` results.
  Both sizes and the extra download were announced before downloading.
- SYSTRAN faster-whisper-medium weights: 1,527,906,378 bytes, plus tokenizer,
  configuration and vocabulary; revision
  `08e178d48790749d25932bbc082711ddcfdfbc4f`.
- faster-whisper 1.2.1, CTranslate2 4.8.5, psutil 7.2.2, PyAV initially
  19.0.2, corrected to 16.0.0. Full versions are locked in experiment files.
- LLM settings: context 8192, output limit 1800 tokens, thinking disabled,
  temperature 0, seed 42, JSON schema. These are experiment parameters,
  not approved system input/output limits. One inference request at a time.
- Actual download total is approximately 10.9GB plus Python wheels and
  metadata, including the second LLM; extracted runtime uses extra disk.
- User-video outputs remain in ignored `.ai-lab/results`; synthetic results
  remain reviewable under `experiments/local_ai/results`.

Official models: [Qwen3 4B](https://ollama.com/library/qwen3:4b),
[Qwen3 8B](https://ollama.com/library/qwen3:8b),
[SYSTRAN medium](https://huggingface.co/Systran/faster-whisper-medium).

## Text experiments and measured results

Each model generated comprehension and opinion polls in Hebrew and English,
reviewed each of three actual synthetic theoretical submissions using the
other two as peers, and processed a no-peer review case. Sources, prompts,
full responses and measurements are retained. These are eight single runs
per model, not a statistically representative evaluation.

| Model | First comprehension call: load / prompt / generation | Warm poll model totals | Peer-review model totals | Sampled device VRAM |
|---|---|---|---|---|
| Qwen3 4B | 27.12 / 24.30 / 3.63 seconds | 1.46–1.94 seconds | 3.60–11.15 seconds | About 4108 MiB |
| Qwen3 8B | 5.29 / 1.11 / 10.70 seconds | 2.26–2.63 seconds | 6.70–8.84 seconds | About 6423 MiB |

8B sampled combined process RSS reached about 1594 MiB. Initial 4B RAM
accounting missed its worker, so it is not a usable total-RAM measurement.
Both LLMs were GPU-resident according to Ollama's running-model API. Load
times are affected by disk/driver caches and cannot establish 8B loads faster.

Manual quality findings:

- English comprehension questions were relevant and selected a correct
  source-supported answer, with four options and an explanation.
- Hebrew questions had awkward wording and occasional unrelated-script
  characters. Larger size did not resolve this reliably.
- Opinion outputs lacked correctness fields, but often remained factual
  questions with a best answer. Structural compliance did not satisfy the
  intended opinion-poll meaning.
- The 4B review praised unsafe cache-only confirmation as a benefit and
  repeatedly attributed another answer's omissions to the target.
- The 8B review improved some concurrency discussion, but falsely claimed
  the complete answer lacked failure/rollback handling. Peer comparisons
  also misstated which works discussed rollback or locking.
- Both models received actual peer texts; this establishes that inputs were
  processed, not that comparisons were accurate. No ablation study was run.
- The no-peer flag/notice was emitted. The 8B review also incorrectly treated
  that output-format requirement as a gap in the student's theoretical work.

Result: hardware feasibility is promising; the tested prompts/models do not
yet establish reliable bilingual deep feedback or valid opinion generation.

## Audio experiment and failures

The user supplied `sharper_video.mp4` (199,055,342 bytes). Container duration
is 350.94 seconds and the audio stream is tagged English; a stream tag alone
does not prove language. Original file left unchanged. PyAV extracted
350.90 seconds of 16-kHz mono audio in 0.94 seconds. This sample duration is
not a system duration limit. Media and derivatives are excluded from Git.

Observed setup/inference failures, retained here rather than called passes:

1. Checksum reader initially mishandled PowerShell byte content and `./`
   filenames; corrected before running the verified archive.
2. ASR download initially omitted `vocabulary.txt`; corrected from the same
   pinned official model revision.
3. faster-whisper 1.2.1 failed with PyAV 19.0.2 (`metadata_errors` argument);
   pinning PyAV 16.0.0 resolved this decoding incompatibility.
4. GPU int8_float16 model loading succeeded, but actual transcription failed
   with `CUBLAS_STATUS_NOT_SUPPORTED`. The failure occurred after 9.80 seconds;
   successful loading and CUDA detection were insufficient compatibility evidence.
5. The float16 GPU retry completed: model load 2.51 seconds, transcription
   128.31 seconds for 350.90 seconds of audio (real-time factor 0.366),
   sampled process RSS 613 MiB and total device memory 3241 MiB. CPU is used
   for decoding/orchestration; this was CUDA inference, not a CPU fallback.
   Bundled CUDA 12 cuBLAS DLLs were exposed to this process only; no system
   CUDA Toolkit or cuDNN installation or PATH change was performed.

The user subsequently confirmed that the source is a song mainly in Hebrew.
The model automatically selected English and emitted English text despite
`task="transcribe"`. This is an observed language-detection and language-
preservation failure on this musical input. The resulting English summary
also fails the approved same-language/no-translation target. The precise
accuracy of the English rendering has not been independently assessed; it
must not be described as a verified translation. The English container tag
was not ground truth. Neither Hebrew nor English lecture ASR passed here.

Qwen3 8B summarized the actual generated transcript, returning a paragraph
and five key points. Summary model time was 6.88 seconds: load 3.15, prompt
0.35, generation 3.37; wall time 7.70 seconds. Sampled summary RSS reached
1377 MiB and total device VRAM 6574 MiB. The summary reflected the transcript's
personal-growth theme, but no claim of fidelity to the original recording or
lecture-summary quality is justified. End-to-end measured component times
sum to about 139 seconds including extraction and both loads; this is one
file, not a system performance guarantee.

Initially no lecture speech clips were supplied; that availability gap is
superseded by the follow-up below. No manually verified reference transcript
or WER assessment is available for any recording.

## Speech follow-up — user-supplied clips

The user supplied two MP4 files and confirmed their languages:
`SHORT-EXPLAIN.mp4` is English-only speech; `STATIC-EXPLNATION.mp4` is Hebrew
speech with English technical terms. Both were processed in full and left
unchanged. No additional downloads or external inference were used. PyAV's
bundled FFmpeg libraries decoded the audio; no FFmpeg executable was installed.

Whisper medium used CUDA float16, automatic language detection, transcribe
mode, beam_size=5, no VAD and no preceding-text conditioning. ASR loaded once
in 3.16 seconds. ASR was unloaded before Qwen3 8B summarized the transcripts.

| Case | Audio duration | Extraction | ASR wall time | Language | Summary model time (load / prompt / generation) |
|---|---|---|---|---|---|
| SHORT-EXPLAIN | 56.75 s | 0.22 s | 10.97 s | English, matches user | 6.27 s (2.62 / 0.25 / 3.40) |
| STATIC-EXPLNATION | 235.29 s | 0.52 s | 171.00 s | Hebrew, matches user | 6.56 s (0.01 / 0.35 / 6.16) |

Summary wall times including HTTP/monitoring were 7.03 and 7.39 seconds.
Sampled ASR RSS peaks were 465/477 MiB; device-wide memory was 2428/3104 MiB.
Summary RSS peaks were 1348/1418 MiB; device-wide memory was 6433/6437 MiB.
CPU handles decoding/orchestration; ASR and LLM inference used GPU. Measurements
include cache effects and are not independent cold-start benchmarks. Resource
measurement limitations are described in the experiment README.

Manual inspection of generated text, not independent listening-based scoring:

- English transcription was coherent about OOP, classes, objects, inheritance
  and mutable state. Its English summary retained central transcript points
  and returned a paragraph plus four bullets. Exact speech accuracy is unscored.
- Hebrew transcription retained static-versus-instance variables, a Car
  example and a minimum-price example, but included unrelated-script fragments,
  malformed Hebrew and corrupted code terminology. Technical identifiers were
  not reliably transcribed on this sample.
- The Hebrew summary stayed Hebrew and returned a paragraph plus four bullets.
  It captured the shared-variable idea, but used a wrong expression equivalent
  to "does not translate again" instead of clearly discussing per-instance
  creation/allocation. It is not accepted as an accurate teaching summary.
- Language detection and output structure passed narrow checks; source speech
  fidelity and reliable summary quality did not thereby pass. Summaries were
  checked against machine transcripts only, so ASR errors can propagate.
- English speech and Hebrew speech with English terms were exercised. A
  separate Hebrew-only speech case, repeated runs, longer recordings and
  reference-based accuracy remain untested. No visual information was analyzed;
  unspoken slide/code content is outside the approved audio-only approach.

Private full transcripts, segments, summaries and resource samples are in
`.ai-lab/results/speech-followup/`; sanitized metrics are in
`experiments/local_ai/results/audio_speech_metrics.json`. Original song
results and failures were preserved.

## Limits and next decision

The local route is not yet accepted as sufficient for the full demo. Retain
the measured hardware evidence and investigate a bounded prompt correction
or one explicitly chosen alternative only in a later approved stage.
Reference-based speech accuracy, Hebrew technical-term fidelity, grounded
feedback, factual comparison, opinion-poll semantics and end-to-end summary
quality still need evidence. English speech is promising on one sample;
Hebrew speech is degraded and is not accepted for a reliable demo. No website,
classroom test, offline implementation, maximum input limit, or paid fallback
has been approved by this experiment. Do not change the existing scope to
hide these gaps.
