# Video Processing Infrastructure

## Current behavior — Unit E

New uploads now continue from real extraction into local GPU transcription, then delete temporary audio and expose the private full transcript. Summarization remains disabled. See [local-transcription.md](local-transcription.md) for current behavior, configuration, seven-day content retention and acceptance evidence. Existing extraction-only jobs retain their original result. The commands below now process transcription for new uploads; the following Unit D record describes the historical extraction-only stage.

# Unit D — Private MP4 Validation and Audio Extraction

Status: implemented extraction infrastructure, not a completed video-summary
capability. The English UI says **Audio extraction completed** only after real
decoding, WAV verification and temporary-audio removal. Transcription and
summarization remain disabled/unverified; no AI request/model download occurred.

## Approved scope and operational limits

- Upload from a meeting as a Lecturer. One MP4 per request, at most **200 MB =
  200,000,000 bytes** and **240 seconds**. These are system-input limits, not
  the separately undecided presentation-segment duration or full-lesson support.
- Check bytes in the multipart upload handler and again while copying chunks.
  Check extension, actual MP4 ftyp/container, video and audio tracks, finite
  container/stream durations, and real decoding. Do not trust MIME/extension alone.
- The worker validates/extracts one video at a time, using a separate decoder
  process. Queue wait does not consume the **600-second processing deadline**,
  which starts when the worker claims a job, before subprocess startup.
- Extract the first audio track into 16-kHz mono 16-bit PCM WAV. Decode video
  frames for integrity/time-bound checks only, without interpreting visual content.
  The later summary remains audio-only; unspoken visual information is excluded.
- Only the uploader may list/view the job, while still an active Lecturer member
  in that course. Other lecturers in the same course are denied direct HTML/JSON
  access. Students, nonmembers and mismatched parent URLs are denied.

## Architecture and persistent state

`VideoJob` stores UUID, meeting/uploader, original display filename, actual byte
count, timestamps, heartbeat, duration/sample measurements, failure stage and
sanitized error code. State is Uploading -> Queued -> Validating -> Extracting ->
Extracted, or Failed. Only real stages are displayed; no invented percentage or
transcription/summarization success appears. The browser polls every 3 seconds
while visible, with an informational elapsed-time clock. It pauses hidden-page
reads and warns on refresh failure; the database remains authoritative.

```mermaid
sequenceDiagram
    participant L as Lecturer browser
    participant D as Django
    participant DB as SQLite
    participant W as Separate worker
    participant P as Isolated media process
    L->>D: CSRF multipart MP4 upload
    D->>DB: Persist owner/meeting and Queued state
    D-->>L: Redirect to task page; other site pages remain usable
    W->>DB: Claim oldest queued job; persist start and heartbeat
    W->>P: Check MP4 and decode/extract under remaining deadline
    P-->>W: Actual stage and verified audio measurements
    W->>W: Remove temporary audio
    W->>DB: Persist Audio extraction completed or failed stage/code
    L->>D: Read own task later
    D-->>L: Persisted state, elapsed time and understandable failure reason
```

Files are private under ignored `.local/videos/<UUID>/input.mp4` and audio.wav;
multipart temporary files use ignored `.local/video-upload-temp/`. There is no
MEDIA_URL, static route, original-file download or raw-audio endpoint. The
original filename is display-only and escaped; all physical names are fixed.
Path resolution validates the UUID/root before any access/deletion. Cleanup
uses individual unlink operations, never recursive deletion or user paths.

The worker holds an OS-exclusive coordinator lock, automatically released on
process exit. A second decoder lock also prevents overlap with an orphan. The
child has its own deadline/parent-death watchdog. The coordinator writes
heartbeats every 2 seconds, terminates its child on timeout/stop and removes WAV
in finally. Independent maintenance and authorized status reads recover stale
heartbeats after 30 seconds; worker restart also recovers formerly active jobs
once it acquires the exclusive lock. Failed tasks retain their actual last stage.
No automatic reprocessing occurs; another upload is explicit.

## Retention and required background services

- Temporary audio is removed before success and after failure; maintenance retries
  locked leftovers. Cleanup failure is not silently reported as successful cleanup.
- Uploaded MP4s expire 24 hours after upload creation. Maintenance sweeps every
  10 seconds with a 5-minute early-purge margin. Jobs too close to source expiry
  to fit a full processing budget are not started. Expired queued jobs fail.
- Orphan UUID files and interrupted saves are cleaned, with path/symlink guards.
  Old Django multipart temporary files are included in the private cleanup scope.
- **Keep maintenance running independently of the worker.** Stopping the worker
  must not stop source expiry/recovery. Neither an offline computer nor stopped
  maintenance can physically delete files on time: cleanup resumes on startup.
  This is an operational limitation, not a claim of guaranteed deletion while off.
- Task metadata remains for viewing. No transcripts/summaries are stored now;
  their approved future maximum retention is 7 days, recorded by the separate
  disabled-engine contract. This does not claim future text cleanup is implemented.
- Original Downloads files and experiment media are never modified or cleaned
  by this application; only uploaded private copies are in this retention scope.

## Run locally

Use the existing website `.venv`; requirements now add only **av==16.0.0**, the
previously exercised PyAV version (32.3 MB wheel). No FFmpeg executable, NumPy,
ASR/LLM model, driver or system configuration change is required.

From the project root, after installing requirements and applying migrations,
keep these commands running in **separate PowerShell windows**:

```powershell
.\.venv\Scripts\python.exe manage.py run_video_worker
```

```powershell
.\.venv\Scripts\python.exe manage.py run_video_maintenance
```

Use Ctrl+C for a graceful stop. A second coordinator/maintenance instance refuses
its OS lock. `--once` handles at most one queued video, or one maintenance pass,
for diagnosis. For legacy extraction-only jobs these commands do not invoke transcription. New uploads now invoke the local transcription engine under Unit E; summarization remains disabled.
No OS scheduler or firewall/network settings were changed.

## Actual sample results — 2026-11-08

The two existing clips were read locally, copied through the upload service,
processed by separate `run_video_worker --once` invocations and left unchanged
at their original paths. File-size/duration checks passed for both:

| Clip | Actual bytes | Video duration | Worker elapsed | Result |
|---|---:|---:|---:|---|
| SHORT-EXPLAIN.mp4 | 14,645,300 | 56.74957 s | 4.43773 s | Audio extraction completed; 56.74956 s audio; temporary WAV absent |
| STATIC-EXPLNATION.mp4 | 10,477,365 | 235.28780 s | 2.919206 s | Audio extraction completed; 235.28781 s audio; temporary WAV absent |

These elapsed times include subprocess startup, validation/decoding and result
handling; they are not independent cold-start benchmarks or AI timings. Their
difference does not establish a duration/performance law. No speech content,
language fidelity or summary quality was evaluated in this stage.

## Manual browser checklist — not executed by the agent

The user later reported the SHORT-EXPLAIN queued-job success path, including
118.2 s waiting, 4.5 s processing and 56.75 s audio. Details and attribution
are in testing.md. This does not mark every checklist item below as verified.

1. Start the website, worker and maintenance. Sign in as lecturer_alpha, open a
   DEMO-CS101 meeting and choose Video processing. The two limits and the current
   validation/extraction-only capability must be visible before upload.
2. Upload SHORT-EXPLAIN.mp4 from Downloads. Leave the task page and use another
   site page, then return via My uploads. Expect Audio extraction completed or
   an actual failed stage/reason. No transcript/summary should be claimed.
3. In a separate account, try the copied task URL. Student access is forbidden;
   another Lecturer is not the owner and receives 404. Demotion/revocation also
   removes the uploader's access. These server paths have automated evidence.
4. Try a damaged file or MP4 without audio: the asynchronous task should fail
   during checking. An over-size upload is refused; over-duration files fail
   server-side validation. No success is inferred from a filename or MIME type.
5. Stopping the worker leaves queued tasks waiting, not processing. An active
   stopped task must become failed by recovery rather than remain active forever.
   Keep independent maintenance running for retention. Browser/phone and actual
   classroom load remain unverified; see testing.md for executed evidence.

Official references: [PyAV containers](https://pyav.org/docs/stable/api/container.html)
and [Django file uploads](https://docs.djangoproject.com/en/5.2/topics/http/file-uploads/).
