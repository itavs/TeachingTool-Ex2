# Website Architecture

## Current implemented boundary

The website implements authentication/course roles, meetings, attendance/XLSX,
connected comments during/outside class (resolved D-17), poll lifecycle with local
English draft generation, and background MP4 extraction/transcription/summarization.
Homework remains feasibility experiments only: no homework models, views or
review service are implemented. See [requirements/use cases](SRS.md#5-main-use-cases),
[tools and observed evidence](local-ai-feasibility.md#current-tools-and-evidence-index),
and [component-to-test strategy](testing.md#current-component-to-test-strategy).

The QR, online-list/XLSX snapshot and speech-only video-summary interpretations
are implemented choices. The user reports sending all three clarification
questions to the lecturer; acceptance is **pending a reply**, not confirmed.
D-17 comments timing is resolved and is not part of that pending set.

## Current components

| Source component | Actual responsibility and boundary |
|---|---|
| `teachingtool/settings.py`, Django middleware/auth, `classroom/views.py` | Django 5.2.19 Templates/session/CSRF and meeting management; fresh course-membership authorization, SQLite development database. No public account/course administration. |
| `models.py` | Course/Membership/Meeting, AttendanceWindow/AttendanceRecord/MeetingRequest, Poll/PollVote and VideoJob persistence/constraints. |
| `attendance.py`, `participation_views.py`, `request_forms.py` | Rotating signed QR, POST registration/deduplication, XLSX snapshot, private comments/history and visible-page updates. |
| `poll_views.py`, `poll_forms.py`, `poll_services.py` | Generation form, draft edit/version checks, publication, final vote, close and disclosure-safe payload. No inference inside a database write transaction. |
| `poll_generation.py`, `local_poll_generator.py`, `poll_contract.py`, `local_poll_runner.py` | Replaceable PollGenerator contract, local Qwen3 8B English adapter, generated-output validation and isolated runtime. Fake providers are test-only; seed_demo_polls is a separate labeled local fixture command. |
| `video_uploads.py`, `video_forms.py`, `video_views.py`, `video_jobs.py` | Bound uploaded bytes, private persistence, uploader/current-role access, state payloads, failure/recovery and retention. |
| `video_worker.py`, `video_media.py`, `video_storage.py` | One persistent queue/worker; isolated CPU media validation and WAV extraction, locks, deadline/heartbeat and private file handling. |
| `video_engines.py`, `local_transcriber.py`, `local_asr_runner.py`, `asr_checkpoint.py` | Transcriber contract/factory, pinned local large-v3-turbo, CUDA float16, offline checkpoint validation, supervised events and validated transcript results. |
| `local_summarizer.py`, `local_summary_runner.py`, `summary_contract.py` | Summarizer implementation, pinned Qwen3 8B/structured paragraph plus 3-5 points, language/identity checks; no semantic-accuracy guarantee. |
| `process_tree.py`, `process_lock.py` | Owned Windows process-tree lifetime and exclusive local compute access. Poll generation and video AI do not overlap on the shared compute lock. |
| `transcript_display.py`, Templates, `static/js` | Word-preserving paragraphs/RTL-LTR isolation, escaped server-rendered results, visible-page polling and form interactions. |

`get_transcriber()`, `get_summarizer()` and `get_poll_generator()` return the local
implementations. Disabled classes still exist in code but are not current factory
results. No normal runtime fake provider, external inference or paid fallback is
selected. Models/runtimes/private data remain outside Git.

## Class and interface diagrams

These diagrams name real classes/interfaces and selected real operations. Boxes
marked **module** describe function-based modules, not invented Python classes.
Fields/operations are selected for responsibilities, not a complete ORM listing.
The strategy table uses the same names and links to executable test methods.

```mermaid
classDiagram
    class User {
        username
        is_active
    }
    class Course {
        code
        title
    }
    class Membership {
        role
    }
    class Meeting {
        title
        starts_at
    }
    class AttendanceWindow {
        public_id
        opened_at
        closes_at
        closed_at
        additional
    }
    class AttendanceRecord {
        registered_at
        additional
    }
    class MeetingRequest {
        kind
        text
        submission_id
        created_at
    }
    class Poll {
        kind
        language
        question
        options
        correct_index
        explanation
        status
        version
        origin
    }
    class PollVote {
        option_index
        submitted_at
    }
    class VideoJob {
        status
        heartbeat_at
        failed_stage
        error_code
        transcript
        transcript_segments
        detected_language
        asr_metadata
        transcript_expires_at
        summary_paragraph
        summary_points
        summary_metadata
        summary_expires_at
    }
    User "1" --> "0..*" Membership
    Course "1" --> "0..*" Membership
    Course "1" --> "0..*" Meeting
    Meeting "1" --> "0..*" AttendanceWindow
    Meeting "1" --> "0..*" AttendanceRecord
    AttendanceWindow "1" --> "0..*" AttendanceRecord
    User "1" --> "0..*" AttendanceRecord
    Meeting "1" --> "0..*" MeetingRequest
    User "1" --> "0..*" MeetingRequest
    Meeting "1" --> "0..*" Poll
    Poll "1" --> "0..*" PollVote
    User "1" --> "0..*" PollVote
    Meeting "1" --> "0..*" VideoJob
    User "1" --> "0..*" VideoJob : uploader
```

Membership is unique per user/course, so roles can differ across courses. Attendance
is unique per meeting/student; additional windows preserve first registration.
Poll votes are unique per poll/student and a conditional database constraint allows
only one Active poll per meeting. VideoJob stores actual model provenance separately
from requested identity and preserves historical completed jobs.

```mermaid
classDiagram
    class Transcriber {
        <<interface>>
        transcribe(audio_path, deadline, on_event, on_tick)
    }
    class LocalWhisperTranscriber {
        transcribe(audio_path, deadline, on_event, on_tick)
    }
    class Summarizer {
        <<interface>>
        summarize(transcript, language, work_dir, deadline, on_event, on_tick)
    }
    class LocalQwenSummarizer {
        summarize(transcript, language, work_dir, deadline, on_event, on_tick)
    }
    class PollGenerator {
        <<interface>>
        generate(material, kind, language)
    }
    class LocalPollGenerator {
        generate(material, kind, language)
    }
    class ProcessTree {
        attach(pid)
        close()
    }
    class VideoUploadForm {
        clean_video()
    }
    class BoundedUploadHandler {
        receive_data_chunk(raw_data, start)
        file_complete(file_size)
    }
    class video_worker {
        <<module>>
        run_worker()
        claim_job()
        process_job(job)
    }
    class video_jobs {
        <<module>>
        save_upload(meeting_id, user, upload)
        owned_job(meeting_id, job_id, user)
        fail_job(job_id, code, stage)
        recover_jobs()
        purge_expired_transcripts()
        cleanup_video_files()
    }
    class poll_services {
        <<module>>
        create_generated_draft(meeting_id, user, kind, language, material)
        edit_draft(meeting_id, poll_id, user, version, data)
        publish(meeting_id, poll_id, user, version)
        vote(meeting_id, poll_id, user, option_index)
        close(meeting_id, poll_id, user)
        public_payload(poll, membership, user)
    }
    Transcriber <|.. LocalWhisperTranscriber : structural protocol
    Summarizer <|.. LocalQwenSummarizer : structural protocol
    PollGenerator <|.. LocalPollGenerator : structural protocol
    video_worker ..> Transcriber
    video_worker ..> Summarizer
    video_worker ..> video_jobs
    video_jobs ..> VideoJob
    poll_services ..> PollGenerator
    poll_services ..> Poll
    LocalQwenSummarizer ..> ProcessTree
    LocalPollGenerator ..> ProcessTree
```

Python Protocols use structural conformance; adapters do not inherit them explicitly.
Function argument lists above omit optional/test-only parameters; the code is the
source of exact signatures. ASR subprocess supervision is in LocalWhisperTranscriber;
ProcessTree ownership is used for the Qwen subprocess/service descendants.

## Video sequence

```mermaid
sequenceDiagram
    actor L as Lecturer
    participant V as video_views
    participant J as video_jobs
    participant DB as VideoJob / SQLite
    participant W as video_worker
    participant M as video_media.media_child
    participant T as LocalWhisperTranscriber
    participant S as LocalQwenSummarizer
    participant C as maintenance
    L->>V: CSRF POST MP4 in meeting
    V->>V: BoundedUploadHandler + VideoUploadForm
    V->>J: save_upload(meeting_id, user, upload)
    J->>DB: Authorize Lecturer, private file, queued job
    V-->>L: Redirect, website remains usable
    W->>J: recover_jobs / cleanup_video_files
    W->>DB: claim_job(), recheck role, start 600s budget
    W->>M: Validate MP4/audio/video, extract WAV
    M-->>W: Measurements or actual failed stage/code
    alt Media failure
        W->>J: fail_job(), remove temporary files
    else Media valid
        W->>T: transcribe(audio_path, same deadline, events/ticks)
        T-->>W: Verified identity/stages, text result or failure
        alt Transcription failure
            W->>J: fail_job(), remove WAV and pending files
        else Valid transcript
            W->>W: Remove WAV, require successful cleanup
            W->>DB: Recheck role/state, persist transcript and 7-day expiry
            W->>S: summarize(text, language, same deadline, events/ticks)
            alt Summary valid and role still allowed
                S-->>W: Validated paragraph, points, actual metadata
                W->>DB: summarized, expiry no later than transcript
            else Summary unavailable/invalid/timeout/interrupted
                W->>J: fail_job() with stage/reason
                Note over J,DB: Saved transcript remains, no false summary success
            end
        end
    end
    L->>V: GET task / full transcript later
    V->>J: owned_job(), current Lecturer + uploader, availability
    V-->>L: Result or failure, transcript only while unexpired
    C->>J: recover_jobs(), cleanup_video_files()
    J->>DB: purge_expired_transcripts(), clear expired summary/text
    Note over V,DB: Direct access blocked at expiry before physical cleanup
```

A WAV cleanup failure also routes to fail_job before saving a transcript or
starting summary; the diagram abbreviates this guard. Actual states are queued,
validating, extracting, loading_asr, transcribing, loading_sum, summarizing and
terminal extracted/transcribed/summarized/failed (plus uploading during persistence).
The persisted start governs a single 600-second processing deadline; queue wait
is separate. Heartbeats/recovery and the worker lock prevent indefinitely active
jobs or concurrent workers. Owner and fresh Lecturer role are checked on direct
URLs and before saving outputs. WAV/IPC files are removed on normal/failure cleanup.

Sources are private UUID paths, capped at 240 seconds/200,000,000 bytes, and expire
within 24 hours while maintenance operates. Transcript access ends seven days after
creation; summaries never outlive it. Maintenance clears content, not the job's
history. Physical deletion cannot occur while the computer/maintenance is stopped.
No public MEDIA_URL, original-file download or raw-audio endpoint exists.

## Poll generation and publication sequence

```mermaid
sequenceDiagram
    actor L as Lecturer
    participant V as poll_views
    participant P as poll_services
    participant G as LocalPollGenerator
    participant R as local_poll_runner / Qwen3 8B
    participant DB as Poll / SQLite
    actor S as Student
    L->>V: CSRF POST English/type/material (1-6000 characters)
    V->>P: create_generated_draft()
    P->>P: validate_input(), authorize Lecturer
    alt Invalid input or Hebrew generation
        P-->>V: Reject before inference
        V-->>L: Preserve material, explain English-only generation
    else Valid English request
    P->>G: generate(material, kind, language) outside DB transaction
    G->>R: Private IPC, pinned local model, bounded shared compute
    R-->>G: Structured result or explicit failure
    alt Unavailable/busy/invalid/timeout
        P-->>V: Explicit error, no Poll saved
        V-->>L: Bound form retains material, no prepared fallback
    else Valid English output
        G-->>P: Validated draft content
        P->>DB: Recheck membership under lock, create ai/Draft
        V-->>L: Editable unpublished draft, review required
        S->>V: GET unpublished draft
        V-->>S: 404, omit from list
        L->>V: POST edit/save draft + version + CSRF
        V->>P: edit_draft(), validate_content(), increment version
        L->>V: Separate POST Publish + version + CSRF
        V->>P: publish()
        P->>DB: Lock meeting/poll, require_draft, one Active, publish
        S->>V: POST one final choice
        V->>P: vote(), current Student role, Active, unique vote
        L->>V: Read live counts, POST manual close
        V->>P: close() under same locking order
        S->>V: GET closed results
        V-->>S: Aggregates, comprehension-only answer/explanation
    end
    end
```

Validation occurs at adapter/service boundaries; a failed provider call does not
continue through the success messages shown above. The runner's compute lock
serializes against video AI; busy is an explicit error. Generation has a 120-second
startup/generation limit and no automatic retry. Publication checks the current
draft version; voting/closing serialize under short SQLite IMMEDIATE transactions.
Active Student HTML/JSON contain no answer/explanation or aggregates. Opinion polls
never have correctness fields. The review-required notice is Lecturer/Draft-only.

## Shared participation and authorization

All feature routes require current course membership, not just hidden controls.
Cross-course or mismatched parent IDs yield generic 404; wrong-role access gives
403. Student histories filter by owner; Lecturer feeds/exports recheck role. Staff
flags do not bypass course membership. Login preserves a safe next URL, logout
requires CSRF POST, and templates escape text. MeetingForm binds allowed fields
and the server assigns the course. Past meetings remain usable.

Attendance opens a five-minute initial window, rotates signed QR every 30 seconds
and accepts a code for 45 seconds bounded by closure. Later windows last two
minutes. GET/login continuation revalidates; only CSRF POST registers, preserving
one meeting/student record. A valid code can be forwarded: physical presence is
not proven. XLSX is a snapshot, without back-sync or manual corrections.

Comments accept 1-1000 trimmed characters and retain private history; a visible
Lecturer page polls every five seconds. D-17 is resolved as during/outside class,
including past meetings and later Lecturer login, using the same connected path.
No disconnected queue/local persistence/synchronization is required.

## Historical milestones and remaining boundaries

Unit A was foundation-only; Unit B added participation; initial Unit C used a
disabled generator and local demo drafts; Unit D initially stopped at extraction;
Unit E added ASR. D-41/D-42/D-43/D-44 supersede those old disabled boundaries for
new uploads/English drafts. Historical records remain in testing and experiment
reports and must not be read as current factories or full acceptance.

The website is loopback development with DEBUG/SQLite, not a production/classroom
deployment. Phone access, classroom load, HTTPS/hardening and the ten-minute demo
remain unverified. Homework comparison/review has failed quality expectations in
local feasibility work; no corresponding website classes or sequence are invented
here. Optional campus-network checks remain deferred and nonblocking.
