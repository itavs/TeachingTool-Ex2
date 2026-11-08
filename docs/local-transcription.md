# Unit E — Local Video Transcription

Implemented 2026-11-08. New meeting MP4 uploads use real local GPU speech recognition; summarization remains disabled. This is a functional integration, not a word-accuracy acceptance pass or completed AS-04 summary capability.

## Existing local runtime (no downloads/installations)

- Python: `.ai-lab/venv/Scripts/python.exe`; separate from website `.venv`.
- Current default for new uploads (D-41): existing `dropbox-dash/faster-whisper-large-v3-turbo`, revision `0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf`, under `.ai-lab/models/faster-whisper-large-v3-turbo`; model.bin 1,617,884,929 bytes. The approved download and independent full-clip comparisons are in static-turbo-quality.md and short-turbo-quality.md. The earlier medium model/results remain historical evidence, not the active default.
- faster-whisper 1.2.1, CTranslate2 4.8.5, PyAV 16.0.0; CUDA float16 on the existing NVIDIA RTX 5050 Laptop GPU. CPU threads 8, workers 1, beam 5, task transcribe, automatic language, VAD off, condition_on_previous_text false. No translation or CPU fallback.
- Existing CUDA12 DLLs: `.ai-lab/ollama/lib/ollama/cuda_v12`, added to the ASR child process only. No driver, global PATH, firewall or network changes.
- Local-files-only model loading and offline/telemetry-disabled environment variables. No API calls, billing or summary engine calls. Missing runtime/model/GPU produces an explicit failure, never prepared text.

## Pipeline and persistence

Upload -> Queued -> Checking video -> Extracting audio -> Loading local transcription model -> Transcribing speech locally -> Transcription completed, or Failed with the actual failed stage and safe reason. Processing stays outside HTTP requests. One coordinator holds an OS lock; an isolated decoder releases its media lock before the ASR child acquires it. The original 600-second deadline, measured from worker claim, covers all stages, startup and loading; queue wait is separate. Model loading is per job, not a resident cache.

The page polls persisted state while visible, displays elapsed time and processed-audio coverage as informational progress, not an invented completion percentage. Completion exposes detected Hebrew/English and a full-transcript link. Silence/empty output, unsupported detected language, GPU/runtime failures, revocation, timeout and interruption do not claim transcription success. Summary remains visibly unavailable; audio-only analysis excludes unspoken visual information.

The worker keeps WAV until transcription returns, then removes it before success. Exceptions also remove WAV/private pending JSON. A child watchdog bounds processing if its parent dies; restart/stale-heartbeat maintenance marks abandoned work failed. The existing recovery tests cover the common worker mechanism; no real GPU hard-crash experiment was performed.

VideoJob stores text, timed segments, language, model/configuration metadata, measured load/transcribe timings and transcript creation/expiry. HTML is escaped and grouped at saved segment/pause boundaries without changing words. Hebrew uses RTL, English LTR, with Latin phrases isolated in bdi elements; reading width is constrained and mobile spacing adapts. Polling JSON excludes transcript words/segments. Only the uploader while still a Lecturer in the associated course can open full text; direct URLs repeat authorization. At exactly creation +7 days, direct access returns HTTP 410 even before maintenance. Maintenance clears text and timed segments and records deletion. Metadata/task history remain. Physical cleanup requires a running machine/maintenance process; this is not a backup-erasure guarantee.

Input limits remain 240 seconds and 200,000,000 bytes, server-enforced. Uploaded MP4 copies retain the existing maximum 24-hour cleanup policy. Pre-existing jobs default to transcription_requested=false and retain Audio extraction completed; only new normal uploads request transcription.

## Initial medium samples — historical evidence

Both originals were read locally, uploaded as two new jobs through the normal upload service, and handled sequentially by actual worker commands. No mock provider was involved. These initial jobs used medium and retain their original text/model metadata; the later default switch does not reprocess them. Owner-authenticated application requests then returned HTTP 200 for detail and full-text pages; the complete escaped stored text was present in each response. This checks server rendering, not an agent-run browser or phone layout.

| Clip | Audio | Detected | Model load | Transcription | Total worker processing |
|---|---:|---|---:|---:|---:|
| SHORT-EXPLAIN.mp4 | 56.750 s | English | 2.837 s | 12.439 s | 26.666 s |
| STATIC-EXPLNATION.mp4 | 235.288 s | Hebrew | 1.578 s | 190.870 s | 195.856 s |

Load timing covers model constructor; transcription includes language detection and segment iteration. Total also includes validation, decoding, interpreter/library startup, shutdown, cleanup and persistence. These are single observed runs, not repeatable cold/warm benchmarks. Both fit 4 minutes/200 MB and the shared 10-minute budget. WAV and pending-result files were absent after each run. No new RAM/VRAM peak measurement was collected; CUDA use follows explicit adapter configuration and successful real inference, not a CPU fallback.

**Word/term accuracy remains unverified against a manually transcribed reference.** Initially requested listening-only windows were SHORT 00:05.000–00:40.000 and STATIC 00:30.000–01:10.000, with the latter's English-term coverage unverified. The user reported difficulty deciphering the source and approved continuing functional checks without references. No WER, verified correct/incorrect terms or quality pass is claimed. Full AS-04 still needs summary implementation and source-grounded quality review.

## Run and manual check

From the project directory, use the existing website and separate processes:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload
.\.venv\Scripts\python.exe manage.py run_video_worker
.\.venv\Scripts\python.exe manage.py run_video_maintenance
```

Each command occupies its own terminal. Keep maintenance running independently of the worker. No dependency/model installation is needed with the current local files. Stop with Ctrl+C; restart services after reboot. Start only one worker/maintenance instance; a second is refused by its lock.

Sign in as lecturer_alpha, open the relevant DEMO-CS101 meeting -> Video processing -> upload a new MP4. Other pages remain usable. Return via My uploads, wait for Transcription completed, then select Open full transcript. The two new real sample tasks are already present in that meeting. Confirm detected language and mixed Hebrew/English reading visually; that visual check and independent word accuracy are not yet reported as verified. Old extraction-only tasks do not gain a transcript automatically. Other users must not open copied transcript links.

Automated checks and their evidence boundaries are in [testing.md](testing.md). Summary and external AI remain outside this stage; the 13 outstanding Gemini experiment changes were not modified.

## Reading layout and recognized-text anomalies

The same saved tasks now render short reading paragraphs on every view; no retranscription or database text rewrite is needed. The teacher-facing explanation is: "The transcript is based on speech in the recording. Content shown only on screen is not included." Hardware/processing details remain in this document rather than the full-text page.

The STATIC audit found four U+FFFD characters and one dishwasher already present in persisted direct model segments, identical in full database text and UTF-8 rendered response. No application encoding fault was found. The original transient result JSON was deleted by policy, so the persisted segment strings are the earliest retained artifact for this run. No words were guessed/repaired. Dishwasher remains a source-audio accuracy-review finding, not a verified spoken word or proven wrong replacement. Exact segment times, test results and browser-verification limitations are in testing.md.

## Approved turbo default — D-41

New uploads now request the tested local large-v3-turbo revision through the existing adapter. At creation, asr_metadata records requested_model (repo/revision); this is an intent record, not a claim that a model ran. Before loading, the offline ASR subprocess verifies SHA-256 of all five model/config/tokenizer files against the approved checkpoint manifest. Missing, altered or different files fail with a clear turbo-unavailable reason; there is no medium/CPU/online fallback or download. Hash verification shares the existing 600-second deadline.

After successful CUDA model loading, the child emits actual repo/revision, sha256_verified, library versions and inference configuration. The worker stores this immediately, so an inference failure still retains the identity actually loaded. Successful text stores the same actual metadata. Failed-before-load jobs retain requested identity only. Metadata is private server-side and does not expand transcript permissions or appear as hardware details on the reading page. Historic transcripts and their original metadata are unchanged.

The full-recording experiments measured STATIC turbo 54.893 s ASR / 1.822 s loading versus medium 190.870 s / 1.578 s, and SHORT turbo 4.824 s / 1.749 s versus medium 12.439 s / 2.837 s. These single isolated runs are not predicted website latency. Hebrew improved in readability but still includes unclear wording/negation near 00:58–01:02. Neither Hebrew word accuracy nor code-identifier fidelity is verified against a manual source reference. Summarization remains disabled and separate. Website upload acceptance and exact task details are recorded in testing.md; The subsequent user browser review is recorded below.

Normal-route STATIC acceptance for D-41: new job 489f75a2-bca3-4c0a-a9fc-3cc602636ce5 in DEMO-CS101 / Test Meeting, uploaded by lecturer_alpha. Verified turbo revision/CUDA metadata, 1.574 s model loading, 54.555 s transcription, 60.549 s total worker processing, detected he, owner HTTP 200 full text, and WAV/pending-result deletion. This exercised the real multipart POST handler and worker through an in-process client, not a browser. The subsequent user browser review is recorded below. All six prior task transcripts/segments/model metadata were preserved unchanged. See testing.md for the 113-test run and limitations.

## User-reviewed stage completion

The user reported opening the STATIC full transcript in the website and understanding the object-variable versus shared-static-variable explanation. Garbled words remain, and part of a negated sentence was unclear even on source listening. No word-by-word accuracy was measured. This is user-reported understandability evidence, not verified verbatim accuracy or phone acceptance. The user approved completing local transcription with turbo as the new-upload default; summaries remain disabled and separate.

The reading page is titled Automatic transcript, with the concise warning Some words and code terms may be transcribed incorrectly. The speech-only notice is retained. Model/worker details remain in technical documentation. Published reports contain measurements and assessments; raw transcript outputs stay in ignored local storage.

## Subsequent summary integration

New uploads now continue to local automatic Qwen3 8B summarization after the transcript is saved. The transcript survives a summary failure; existing completed tasks remain unchanged. Statements above that summaries were disabled describe the earlier transcription-only stage. See [local-summaries.md](local-summaries.md) for current behavior and quality limitations.
