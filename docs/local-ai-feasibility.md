# Technical Tools Report and Local AI Evidence

## Current tools and evidence index

This is the short entry point for To Do 2. The table distinguishes adopted runtime
tools, historical candidates and deferred options; a mention is not an untested
recommendation. It links actual trials, including negative results, rather than
claiming that installation or valid JSON proves quality. Current design is in
[architecture](architecture.md); software/real-model/open checks are separated in
[testing](testing.md#current-component-to-test-strategy).

Evidence availability: **repository evidence** means a tracked file available in
a clean clone after this documentation commit. **Local only / unpublished** means
an ignored or untracked artifact, or an unstaged update excluded from this commit;
its filename is shown as plain text rather than a repository link. This index
summarizes reported outcomes without publishing the independent experiment
implementations or raw outputs. The homework probe code, synthetic fixtures and focused results are now published
with this experiment closure. The 13 Gemini changes remain excluded. No AI tool was rerun for this review.

| Tool / status | Purpose considered | What actually ran | Observed result and limit | Evidence and availability |
|---|---|---|---|---|
| Python 3.12.14 / adopted | Server, experiment scripts, isolated runners | Separate website and AI virtual environments; scripts and Django requests/tests | Workstation runtime used successfully; a fresh clone needs setup, not the Windows Store alias | [Setup](../README.md#local-setup-and-run), [locked AI dependencies](../experiments/local_ai/requirements-lock.txt); environments local only |
| Git / adopted | Repository and versioned deliverables | Prior scoped commits/pushes; status/diff inspection | Repository exists; outstanding experiment/document changes are not published evidence | Git history and README To Do map; PDF is local/untracked |
| Django 5.2.19, Templates, auth/ORM / adopted | Simple server-rendered site, roles/forms/CSRF | Course/meeting, participation, poll and video request paths; user browser checks | Functionality/permissions have software evidence; not production/phone/classroom-load acceptance | [Class-aware strategy/results](testing.md#current-component-to-test-strategy), [requirements](../requirements.txt); DB/credentials local only |
| SQLite / adopted for development | Persistent state and short serialized writes | File-backed tests, parallel votes/publications/close and participation writes | Two-request races exercised; classroom capacity unknown | [Poll concurrency tests](../classroom/test_polls.py), [participation tests](../classroom/test_participation.py); development DB local only |
| HTML/CSS and small JavaScript; Node test runner / adopted | Responsive pages, selection, visible-page polling | Server rendering, JS tests, user-reported selection/live-update checks | Last recorded closure: 136 server and 12 JS tests passed; no full phone visual acceptance | [Testing record](testing.md#english-poll-stage-closure-verification--2026-11-11), [JS tests](../tests_js/polls.test.cjs) and adjacent tests; source in repository |
| qrcode 8.2 / adopted | SVG rotating QR | Signed QR/render/scan path and user-reported QR check | Operational QR flow; not physical-presence proof or confirmed classroom-phone acceptance | [Participation assertions](testing.md#unit-b--executed-attendance-and-connected-request-checks), [attendance](../classroom/attendance.py) |
| openpyxl 3.1.5, et_xmlfile / adopted | XLSX snapshot export | Export checks include fields, snapshot and safe string cells | Working export; no back-sync, no lecturer-confirmed interpretation yet | Same participation record and [participation tests](../classroom/test_participation.py) |
| PyAV 16.0.0 / adopted | Validate MP4; extract 16-kHz mono WAV | Real supplied clips and generated valid/corrupt/no-audio test media | CPU extraction works; PyAV 19.0.2 initially incompatible with faster-whisper and was replaced | [Initial speech evidence](#speech-follow-up--user-supplied-clips), [video record](video-processing.md#actual-sample-results--2026-11-08), [video tests](../classroom/test_videos.py); original media local only |
| FFmpeg CLI / not selected | Possible media extraction executable | No CLI installation or standalone CLI trial | PyAV bundled FFmpeg libraries provided the tested extraction; standalone CLI is not a project recommendation | [Historical audio experiment](#audio-experiment-and-failures) |
| faster-whisper 1.2.1, CTranslate2 4.8.5, NVIDIA CUDA / adopted | Local speech transcription on 8-GB GPU | RTX 5050 Laptop CUDA float16 inference; isolated DLL configuration | int8_float16 failed CUBLAS_STATUS_NOT_SUPPORTED; float16 worked. No driver/system configuration change; accurate words not established | [Local transcription](local-transcription.md), [initial failures](#audio-experiment-and-failures); model/DLLs local only |
| SYSTRAN Whisper medium / historical baseline | Initial local multilingual ASR | Full SHORT/STATIC plus language-forcing quality comparison | English coherent; Hebrew corrupted; baseline preserved, not current fallback | [Focused quality report](static-asr-quality.md), [initial speech evidence](#speech-follow-up--user-supplied-clips); full text local only |
| faster-whisper large-v3-turbo / adopted | Faster/better new-upload ASR | Both full clips and normal website uploads on GPU; checkpoint provenance checked | Isolated STATIC ASR 54.893 s vs medium 190.870 s; SHORT 4.824 s vs 12.439 s. Hebrew understandability improved, word/negation accuracy unverified | [STATIC comparison](static-turbo-quality.md), [SHORT comparison](short-turbo-quality.md), [pinned identity](local-transcription.md#approved-turbo-default--d-41); weights/raw transcripts local only |
| Ollama 0.40.14 / adopted | Run pinned local Qwen weights | Local GPU text experiments and supervised isolated website services | Local generation works; cold load and warm reuse differ. No external endpoint or paid fallback | [Runtime](local-summaries.md#model-and-isolated-runtime), [AI lock](../experiments/local_ai/requirements-lock.txt); executable/models local only |
| Qwen3 4B Q4_K_M / rejected baseline | Smaller local text model | Four bilingual poll and four homework cases | Unsafe/inaccurate feedback and weak Hebrew/opinion quality; not website engine | [Historical text trials](#text-experiments-and-measured-results), [synthetic results](../experiments/local_ai/results/); models local only |
| Qwen3 8B Q4_K_M / adopted selectively | Summaries and English poll drafts; candidate homework reviewer | Saved-transcript and MP4 summary paths, bilingual poll probes and real English generation route | SHORT summary succeeds; STATIC uploaded summary fails language check with transcript retained. English drafts need Lecturer semantic review; Hebrew generation unavailable | [Summary results](local-summaries.md#actual-full-route-acceptance), [poll generation](local-poll-generation.md#actual-local-validation-on-a-new-topic), [poll quality](local-poll-feasibility.md); real raw/video-derived output local only |
| Qwen3 8B homework probes / experiment round closed, not accepted | Criteria-grounded feedback and comparison | Prior joint reviews plus one-criterion-per-call English review of Alex v1/v2 and B before/after cache correction (14 calls) | Per-criterion review succeeded for both Alex versions but failed controlled B. 26/26 exact quotes matched source; meaning review still found false conclusions and unrelated criterion changes. Neither language is enabled as a real homework provider. | [Closure report](homework-criterion-review-feasibility.md), [personal report](homework-personal-review-feasibility.md), [comparison report](homework-review-feasibility.md), [reproduction instructions](../experiments/local_ai/README.md#focused-homework-probes---reproduction), [synthetic inputs/maps](../experiments/local_ai/homework_fixtures/), [recorded outputs](../experiments/local_ai/results/homework-focused/). Runtime/models remain local-only. |
| psutil 7.2.2, NVIDIA-SMI / measurement tools | Sample process RAM/device VRAM and GPU use | Initial local trials sampled memory and device data | Device-wide VRAM is not model-only; early 4B RAM missed worker. Latest personal probe has no new RAM/VRAM sample | [Measured results](#text-experiments-and-measured-results), [sanitized metrics](../experiments/local_ai/results/audio_speech_metrics.json) |
| Gemini API via Python urllib/PowerShell / external candidate, paused | Check free text/audio alternative | Authenticated inventory/trivial smoke; task timeouts; bounded poll attempt; user-reported direct HTTP 503 | Connectivity partial, no substantive task-quality result. Direct failure does not establish original root cause; no basis to enable billing | [Committed initial Gemini report](gemini-free-feasibility.md) covers the original partial trial. **Local only / unpublished:** later report updates and experiments/gemini_free/results/poll-probe-20261105T141004-fa5b8f3a.json; direct 503 is user-reported, not independently reproduced here. Key/inventory and private data local only |
| University-network origin gate / deferred option, not adopted tool | Possible attendance signal | No campus feasibility trial or runtime gate | Not required/approved; not a physical-presence guarantee; does not block other work | [Conditional study](decisions-and-assumptions.md#7-proposed-university-network-feasibility-study) |

Versions and digests specific to experiments remain in their detailed reports;
the Python requirement files describe the two separate environments, not a single
combined installation. No external service is needed by current website AI.
Local media/weights/runtimes/credentials/databases/raw transcripts remain excluded
from Git. The focused homework probes now use published synthetic fixtures and independent
maps. The runner never passes expected judgments into model prompts. Recorded
synthetic input/prompt/output/timing evidence is in results/homework-focused;
private service logs, token-context arrays, binaries and weights are excluded.
A clone can audit those results without a database or running model. New inference
still needs the explicitly documented installed local runtime/checkpoint, and is
not bit-for-bit reproducible across different hardware/runtime conditions.

## Historical initial local feasibility report

The following dated record preserves the original trials and their failures.
Statements such as no website implementation or no selected provider describe
that earlier stage. They are superseded for current video/English polls by the
index above and current architecture; the observations themselves are unchanged.

### Initial report — 2026-11-05

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
