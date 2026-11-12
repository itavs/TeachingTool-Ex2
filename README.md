# Web-based Teaching Tool

An individual Exercise 2 project for Introduction to Software Engineering
(OOP / OOD): design a practical, simple web application for classroom teaching
and demonstrate its behavior in approximately ten minutes.

## Problem and Scope

The sections below distinguish assignment capabilities from approved design choices.

## Problem Definition

The assignment asks for simpler, LLM-ready teaching tools that support classroom
participation and learning. The proposed application brings attendance,
comments, polls, class-video summaries, and homework review into one coherent
lecturer/student workflow accessible through a smartphone web interface.

Design quality and implementability are central. Implementation is secondary,
and composing existing code or tools is preferred where appropriate.

## Planning Scope

The user approved planning a demo in which **all five capabilities actually
work** (D-01). This is our working target; the lecturer has not confirmed that
all five must be implemented for the demo. User-approved directions now cover
attendance D-05/D-06, comments D-18/D-19 with the D-17 during/outside-class clarification,
polls D-08 through D-11, video D-12 through D-16, and homework D-20 through
D-22. Homework remains a planning/quality target; implemented video/English-poll AI and participation evidence are described below;
remaining operational parameters and open interpretations are explicit.
The shared website foundation is now implemented under D-23 through D-26;
Unit B implements attendance/XLSX and connected comments under D-27 through D-30. Unit C implements the poll lifecycle with explicit local demo data (D-31 through D-33). Local English poll-draft generation is now available under D-44; Unit D implements private MP4 validation/audio extraction; Unit E now transcribes new video uploads locally and exposes private full transcripts; new uploads now include local Qwen3 automatic summaries; real homework AI remains unavailable; its version-bound request/draft/publication mechanics are implemented with test-only provider evidence.

| Capability | Assignment behavior | Design direction and open proposals |
|------------|---------------------|----------------------------------|
| Attendance | Automatic student attendance; lecturer receives an online/offline spreadsheet. | Approved D-05/D-06: lecturer opens a meeting and registration window; an identified student scans a temporary QR displayed in class and rotated during the window. The system validates code validity and meeting association, records attendance and time, and prevents duplicates per student and meeting. Lecturer views an online list and exports a point-in-time XLSX snapshot without synchronization back. |
| Comments and suggestions | Students contribute in real time / offline. | Approved D-18/D-19: identified comment/suggestion requests associated with a meeting, storage/history, student-own visibility, and lecturer access to all meeting requests with new requests appearing without manual refresh. D-17 resolves online as during class and offline as outside class: both use normal website submission to the same meeting, with no disconnected storage or synchronization. |
| Polls | Lecturers create automatic, simple polls about current learning material. | Approved D-08 through D-11: lecturer selects comprehension or opinion before real model generation from pasted text. Both have one question and four single-choice options. Comprehension also includes one correct answer and a short explanation; opinion has no correct answer or correctness evaluation. Lecturer reviews/edits before publication only; identified students submit one final response. |
| Video summary | Lecturer obtains an ML summary of a class video. | Approved D-12 through D-16: manually upload an MP4 file from the computer; extract audio, transcribe speech, and summarize through a model in the recording's spoken language without translation. Target Hebrew and English, including a Hebrew lecture with English technical terms. Return a summary paragraph, 3-5 key points, full-transcript viewing, and an explicit notice that unspoken visual information is excluded. Validation/audio extraction is implemented under Unit D; Unit E adds real local transcription and full-transcript viewing. Word and summary accuracy remain unverified; new uploads include local automatic summaries. |
| Homework review | Students and teachers obtain deep LLM reviews including comparison with other students' work. | Approved D-20 through D-22: theoretical Hebrew/English pasted-text assignments, lecturer instructions/criteria, actual LLM feedback and processing of same-assignment peer submissions, student-own review/comparison without peer identities/full works, and lecturer access to all submissions/feedback. No-peer feedback explicitly states that no comparison occurred. |

One course, one lecturer, and one active meeting are proposed simplifications
(P-01), not approved limits. Separate video demo duration and quality criteria, homework measured limits/quality,
production access/security parameters, real-work retention and classroom capacity
remain open. Website identity/access follows D-24; production readiness remains unverified.

For comments, D-17 was clarified by the user on 2026-11-11: online means during class and offline means outside class. In both cases, identified students submit normally through the website to an associated meeting, including one that has already taken place. Creating content, submitting it and confirming storage remain separate responsibilities. Local persistence, a send queue and disconnected synchronization are not required. D-18/D-19 retain stored history, student-own visibility, lecturer access to meeting requests and live updates. Lecturer replies, discussion threads, attachments, votes and notifications remain excluded.

Homework feedback/comparison remains **planned / feasibility only**, under D-20 through D-22
and the approved UC-05 baseline D-46 through D-51. A Student may request feedback
on their version; a course Lecturer may request a submission review. AI prepares
a private Lecturer draft, which the Lecturer edits/reviews and publishes separately
before the Student sees it. The same assignment's latest version per other owner
is frozen at request time, excluding all target-owner versions even for Lecturer
requests. Instructions/criteria/source versions are recorded. Resubmission creates
a new immutable version and never reassigns old feedback to new text.

No peers permits personal publication with a system-controlled notice. D-52 also
permits explicitly reviewed/published personal feedback after comparison failure,
with the fixed failure notice in UC-05; personal generation failure has no draft.
Any later comparison requires separate Lecturer review and explicit publication. Eligible
peers with failed comparison and completed comparison with no supported difference
are distinct states. Feedback language is chosen per assignment; Hebrew/English
are test targets, neither yet accepted for this planned workflow. Keep synthetic
demo versions/feedback through the demo and submission checking, then support
intentional cleanup; real-student-work policy is separate. No grades, plagiarism
determinations or code execution. See [UC-05](docs/SRS.md#uc-05---submit-homework-review-a-draft-and-publish-feedback),
[planned design](docs/architecture.md#planned-uc-05-components) and
[planned acceptance](docs/testing.md#planned-uc-05-acceptance-strategy).

Approved polling scope includes one active poll per meeting, with another
created after the previous poll closes. The lecturer closes polls manually
and sees respondent counts and distributions as counts and percentages during
voting. Students see only aggregate results without respondent identities
after closure; comprehension answers and explanations are also revealed only
then. The scope excludes grades, file uploads, open-ended questions, and
automatic scheduling. Generation failure displays an error and permits retry,
without presenting prepared content as generated from the material. Poll
language is lecturer-selected Hebrew/English and material is limited to 6,000 characters under D-31 (Q-03 resolved); website identification follows D-24; local English generation is implemented and Hebrew generation remains unavailable. These are project decisions,
not details explicitly prescribed by AS-03.

Video input/output direction is approved: manual file upload, initial MP4
support, a summary paragraph and 3-5 key points, with an option to view the
full transcript (D-14). Planned verification includes Hebrew, English, and a
Hebrew lecture using English technical terms (D-15); sustained language
switching is outside the current commitment. Word accuracy and summary quality remain unverified targets.
D-34 now approves initial system limits of 4 minutes and 200 MB after the earlier measurements. Demo duration remains separate and undecided; unlimited-length/full-lesson support is not claimed. Actual checking/extraction is implemented under D-34 through D-37, while speech/summary quality remains unverified. See
Section 8 of the [register](docs/decisions-and-assumptions.md).

Attendance uses D-24 identity and the approved D-27 through D-29 timing, login-continuation and export rules. There are no manual corrections in this version (Q-01/Q-02 email clarifications are closed under D-54). The QR mechanism does not
conclusively prove physical presence or prevent real-time sharing of a
still-valid code. The email clarification is closed under D-54; QR/list/XLSX are project choices. XLSX export does not imply disconnected registration.

A university-network-origin check is a conditional feasibility option only,
not an approved implementation requirement (D-07, P-10, Q-10). The proposed
information request, local review, and campus observation are recorded in
Section 7 of the [decisions register](docs/decisions-and-assumptions.md);
no network experiment has been performed.
The study is deferred and does not block other project work.

Simulation, canned AI responses, or a transcript uploaded instead of a video
must not silently stand in for a required action. Demo input examples may be
prepared and clearly labeled. Any use of previously computed results needs
explicit disclosure and agreement on what must complete live (P-09).

## Confirmed Decisions and Remaining Technology Boundaries

- Python remains the main server/AI language (D-02).
- The approved Unit A implementation uses Django 5.2 LTS (installed 5.2.19),
  server-rendered Templates and CSS, and SQLite for initial development
  (D-23/D-26). Unit B adds small scripts for CSRF-protected scan submission and visible-page polling.
- Individual pre-created demo accounts use Django password hashing and sessions.
  Roles belong to course memberships, not global account flags (D-24).
- Lecturers create/edit meetings in their courses; students view only (D-25).
- Local turbo transcription and Qwen3 8B summary/English poll adapters are integrated.
  Homework engine selection, production database/hosting and classroom capacity remain open.
- Documents are English. Current UI copy is English as a reversible implementation
  choice; the final interface language remains open (Q-06).

The assignment requires no Moodle, Zoom or university information-system
integration. This does not remove any of the five feature requirements.

## Assignment Deliverables

The numbering below reproduces the eleven populated To Do items on page 2 of
the local assignment PDF (not included in Git). Read the scope here, then the
linked sections; detailed historical evidence is separate from current status.

| To Do | Required deliverable | Short reading route | Current status |
|---|---|---|---|
| 1 | Repository; problem and scope in README | [Problem and scope](#problem-and-scope) | Repository and scope exist; five-feature demo remains a user-approved target, not lecturer-confirmed coverage. |
| 2 | Technical tools report, with actual trials of suggested tools | [Tools and evidence index](docs/local-ai-feasibility.md#current-tools-and-evidence-index) | Trials and failures documented; homework quality insufficient, Gemini partial; some evidence local-only/uncommitted. |
| 3 | SoW document | [Scope and deliverables](docs/SoW.md#3-planned-capability-coverage) | Draft maintained against implemented boundaries and open interpretations. |
| 4 | SRS document | [Functional requirements](docs/SRS.md#4-functional-requirements) | FR/NFR and acceptance targets defined; full acceptance not claimed. |
| 5 | Main use cases / client stories | [UC-01 through UC-05](docs/SRS.md#5-main-use-cases) | Five main flows documented; UC-05 planning baseline approved, quality/limits still open. |
| 6 | Main software components | [Current components](docs/architecture.md#current-components) | Implemented responsibilities mapped; planned UC-05 additions are separate from existing code. |
| 7 | Low-level class and sequence diagrams | [Class interfaces](docs/architecture.md#class-and-interface-diagrams), [video](docs/architecture.md#video-sequence), [poll generation](docs/architecture.md#poll-generation-and-publication-sequence), [planned homework](docs/architecture.md#planned-uc-05-components) | Current video/poll paths covered; homework assignment/version classes are implemented; review/comparison remains planned. |
| 8 | Testing strategy addressing the classes in item 7 | [Component-to-test strategy](docs/testing.md#current-component-to-test-strategy) | Software checks mapped separately from real-model evidence and open acceptance. |
| 9 | Implement or compose a KISS web demo | [Current status](#current-implementation-status), [local run](#local-setup-and-run) | Foundation/participation/polls/video implemented; homework submissions implemented; AI feedback/comparison missing. |
| 10 | Perform a demo in class | [Classroom/demo acceptance](docs/SRS.md#7-future-acceptance-checks-and-traceability) | Not recorded as performed; phone, network, load and ten-minute rehearsal outstanding. |
| 11 | Conclude; write a short account of results | [Interim results](#interim-results-and-final-conclusion-status) | Interim findings available; final conclusion awaits remaining work and actual class demo. |

The exact deadline, submission packaging and live-processing expectations remain
unconfirmed. No specific report filename/template is prescribed by the handout.

## Documentation

| Document | Purpose |
|----------|---------|
| [Statement of Work](docs/SoW.md) | Draft scope, deliverables, boundaries, milestones, and completion criteria. |
| [Software Requirements Specification](docs/SRS.md) | Draft requirements, main use cases, traceability, and future acceptance checks. |
| [Decisions and Assumptions Register](docs/decisions-and-assumptions.md) | Assignment-source IDs, approved decisions, open proposals, and unresolved questions. |
| [Project Working Guidelines](AGENTS.md) | Collaboration and repository working rules. |

The register distinguishes assignment requirements (`AS-*`), user-approved
decisions (`D-*`), open proposals and proposal history (`P-*`), and open
questions (`Q-*`). A draft
requirement or planned acceptance check is not evidence of implementation.

Section 9 of the [register](docs/decisions-and-assumptions.md) consolidates
remaining decisions: production access, teaching context/capacity, AI/data/budget
boundaries and homework quality/limits remain open; D-47/D-48 resolve planned
peer/version selection, and D-50/D-51 resolve assignment language/demo retention; video caps and participation defaults are already decided.
The D-17 comments timing interpretation is resolved; it does not change attendance interpretations. The university-network study remains deferred and non-blocking.

## Current Implementation Status

The user reports the lecturer replied: requirements 1-5 are detailed in the
lecture, and implementation/design details are ours to decide. Email waiting is
closed. Rotating QR, online attendance plus offline-readable XLSX snapshot, and
speech-only video summaries are **project choices**, not technical prescriptions
attributed to the lecturer. Review the relevant lecture section; it has not been
independently reviewed in this update.
D-17 comments during/outside class is already resolved. See the
[clarification register](docs/decisions-and-assumptions.md#lecturer-clarification-response-and-project-choices).

The website implements Django/Templates authentication and course-membership roles,
meeting management, attendance/QR/XLSX, connected comments during or outside class,
and the complete poll lifecycle. Local Qwen3 8B generates **English** editable poll
drafts; Hebrew editing/publication/voting remain supported, but Hebrew automatic
generation is unavailable. New MP4 jobs validate/extract audio, transcribe with the
pinned local large-v3-turbo CUDA checkpoint, then summarize with local Qwen3 8B.
A failed summary retains an available saved transcript; legacy completed jobs are
unchanged. Homework review/comparison has an approved **planning baseline** (D-46 through
D-51) with an implemented assignment/submission foundation; real AI feedback/comparison is unavailable; its mechanical request/draft/publication workflow is implemented but has test-only provider evidence. Functional operation does not establish reliable AI accuracy,
phone usability, classroom capacity or a completed in-class demonstration.

Detailed component/test evidence: [architecture](docs/architecture.md),
[testing strategy](docs/testing.md#current-component-to-test-strategy),
[tools report](docs/local-ai-feasibility.md#current-tools-and-evidence-index).

## Local Setup and Run

### Units D/E — MP4 checks, extraction and local transcription

From a meeting choose **Video processing** as its Lecturer. Upload an MP4 of at
most **4 minutes and 200 MB**; both limits and actual video/audio structure are
checked by the server. After upload, keep using the site and return to the task
to see persistent stage, separate queue/processing elapsed times and failure
reasons. New successful tasks say **Summary completed**, with detected language, an automatic summary and a private full-transcript link. If summary processing fails after transcription, the transcript remains accessible until expiry. Legacy extraction-only jobs retain **Audio extraction completed**. Word accuracy remains unverified against manual transcription; new uploads include local automatic summaries and no external-provider request occurs.

Run the separate services from the project root in two PowerShell windows:

```powershell
.\.venv\Scripts\python.exe manage.py run_video_worker
.\.venv\Scripts\python.exe manage.py run_video_maintenance
```

Each command stays running: use separate windows, not sequential execution in
one window. Stop with Ctrl+C. Only one worker is allowed; maintenance must stay
running independently for recovery and expiry. Requirements add PyAV 16.0.0;
apply migrations before starting. For one task/pass, add `--once`.

Only the uploader, while still a Lecturer in the course, can view each task.
Private uploaded copies expire within 24 hours while maintenance is running;
temporary audio is removed after processing. An offline computer cannot perform
physical deletion; cleanup resumes on startup. Saved transcripts expire seven days after creation; summaries expire no later
than their source transcript. Access is blocked at expiry and maintenance clears content. Source files in Downloads are untouched.

Both existing clips meet the limits and passed actual extraction. Use
SHORT-EXPLAIN.mp4 for a quick local browser check. See [video processing](docs/video-processing.md)
for measurements, commands, retention, architecture and manual steps, and
[testing](docs/testing.md) for executed checks versus browser/phone limitations.

### Unit C — poll lifecycle and separate local demo fixtures

The website now supports draft review/editing, publication, one final response
per student, lecturer live counts/percentages, manual closure and post-close
student results. One poll may be active per meeting. Comprehension answers and
explanations are absent from student HTML/JSON until closure; opinion polls
have no correct answer or correctness evaluation. Poll material accepts at most
6,000 Unicode characters on the server; output-language choices are Hebrew and
English. This does not establish genuine AI language/generation quality.

English draft generation now uses installed local Qwen3 8B through the provider interface. Choose English/type and paste up to 6,000 characters; a valid result opens an unpublished editable draft. Publication is a separate Lecturer action. Automatic checks do not establish meaning/correctness. Hebrew generation is currently unavailable, while editing/publishing/voting in existing Hebrew polls remains supported. On failure the material remains in the form, with no saved placeholder. See [local-poll-generation.md](docs/local-poll-generation.md).

The separate local command below remains available for clearly labeled manual lifecycle fixtures after migrations:

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo_polls --language he
```

This creates two unpublished drafts in the first DEMO-CS101 meeting and prints
their IDs: a comprehension question and an opinion poll. Both display **Demo
data — not generated by AI**, including to students after publication. Use
`--meeting-id <id>` to target another meeting, `--language en` for English, or
`--new-set` to explicitly create another pair. Repeating the basic command
preserves existing edits/status and does not republish or reset anything.

Open that meeting's Polls page as lecturer_alpha; review/edit/publish one draft.
In a separate browser/private session as student_alex, vote once. Observe live
counts on the visible lecturer page, close manually, then reload the student
page to reveal aggregates and, for comprehension only, answer/explanation.
Close the first poll before publishing the second. Current credentials remain
in the ignored local demo credential file. No signup or network setup changed.

See [poll design and manual checks](docs/poll-implementation-plan.md),
[architecture](docs/architecture.md), and [executed evidence](docs/testing.md).
Real browser/phone acceptance and classroom capacity are separate from server
and JavaScript logic tests. Local English generation has narrow real-model evidence; broader language/meaning quality remains unverified.

### Unit B quick check

After applying migrations and restarting any `--noreload` development server,
sign in as lecturer_alpha, open a DEMO-CS101 meeting and choose Attendance and
QR. Open window starts 5 minutes; Close window invalidates every code; the next
window lasts 2 minutes. QR rotates every 30 seconds and is valid for 45 seconds,
bounded by closure. Use a separate private browser as student_alex to open a
copied scan link: login returns to the scan and the page submits a CSRF-protected
POST. Expiry requires a new scan. Without JavaScript press Register attendance.
The lecturer roster and XLSX preserve first-registration time and use Registered
in an additional window for a student's first registration in a later window.
No manual corrections or spreadsheet synchronization are included.

Comments and suggestions accepts 1–1000 trimmed Unicode characters; students
see their own stored history and lecturers see all meeting requests, with
5-second visible-page polling. D-17 defines online/offline as during/outside class; both use the normal connected website flow, including past meetings. No local disconnected storage, send queue or synchronization is required or implemented.

See [executed checks and limitations](docs/testing.md) and the
[manual/private-LAN phone plan](docs/phone-testing.md). Phone access requires a
separately authorized temporary LAN binding and exact allowed host; no network
or firewall setting was changed during implementation. Local video AI and English poll generation are implemented; homework submission is available, while feedback remains experimental.

Run PowerShell from the repository root. A separate `.venv` is already prepared
on the current workstation. On a fresh checkout, use an installed Python 3.12
interpreter to create it first: `python -m venv .venv`. The Windows `python`
Store alias is not an interpreter; select the real interpreter if needed.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). If a development server
is already running on port 8000, use it or stop that server before starting
another. Stop a foreground development server with Ctrl+C.

`seed_demo` generates individual random demo passwords in
`.local/demo-credentials.json`. Open that **local file** to sign in; passwords
are not printed or committed. Rerunning the command preserves passwords and
existing meeting edits, but may restore a renamed initial sample meeting as a
new sample. Do not use this sample-data command as a real-data management tool.
It refuses to take over unrelated accounts with matching usernames.
The SQLite database and generated signing key also stay in ignored `.local/`.
No personal password, Gemini key, media or AI model is needed to run the site.

| Account | DEMO-CS101 | DEMO-SE201 |
|---|---|---|
| lecturer_alpha | Lecturer | Student |
| lecturer_beta | No access | Lecturer |
| student_alex | Student | No access |
| student_blair | No access | Student |
| student_casey | Student | Student |
| observer | No access | No access |

Users see only their courses and meetings. A lecturer creates/edits meetings
only in the course where their membership is Lecturer. Course/membership
administration is prepared through demo data; no public signup, admin UI,
meeting deletion is included. Attendance and comments are available from each meeting under Unit B.
Meeting times are entered and displayed in Asia/Jerusalem.

```powershell
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

This is loopback-only development with DEBUG enabled, not a production or
phone-accessible deployment. Hosting, HTTPS, login throttling, retention and
classroom concurrency need later work. No deployment claim is made.

## Source and Reference Material

The two-page Exercise 2 handout, `I2SE_Exe2.docx.pdf`, is a local untracked
reference and is not included in the repository. Its requirements are
paraphrased with page references in the decisions register.

The local Exercise 1 README and relevant `docs` files were consulted read-only
for documentation style and structure. They are not sources of Exercise 2
requirements or technology decisions. See
[Plane-Projection-of-3D-volume](https://github.com/itavs/Plane-Projection-of-3D-volume).

## Local video transcription — Unit E

New MP4 uploads now run extraction and real offline CUDA speech transcription in the separate worker. The uploader can open full text with detected Hebrew/English; direct access requires current Lecturer membership and expires seven days after transcription creation. Old extraction-only results remain unchanged. Word accuracy is not verified against a manual reference; summaries are automatic drafts with known grounding limitations. See [local-transcription.md](docs/local-transcription.md) for run commands, actual sample timings and manual checks.

D-41 makes the verified local large-v3-turbo checkpoint the default for new video uploads; existing transcripts keep their original text/model provenance. Each task records the actual loaded model revision. Missing/mismatched turbo fails explicitly with no fallback. Hebrew transcription still needs accuracy review; improved readability is not proof of faithful meaning. New uploads now include initial local automatic summaries. See [local-transcription.md](docs/local-transcription.md) and [testing.md](docs/testing.md) for measured results and current manual-review status.

## Local automatic video summaries — subsequent approved stage

New MP4 uploads now use the existing local Qwen3 8B adapter after the full turbo transcript is saved. Output is an automatic paragraph plus 3–5 points in the detected recording language, owner-only with a transcript link and an error warning. Failed summaries retain the completed transcript. The same overall 600-second processing budget, course-membership/uploader authorization and at-most-seven-day text retention apply; summaries never outlive their source. Existing completed tasks remain unchanged. No external provider, model download or canned fallback is used. Current implementation, setup, measured checks and unresolved Hebrew grounding errors are in [local-summaries.md](docs/local-summaries.md). Historical extraction/transcription-only jobs retain their original outcomes; this pipeline applies to new uploads.

## Interim Results and Final Conclusion Status

The implemented website has server-side authorization/lifecycle checks and
user-reported browser checks, recorded separately in [testing](docs/testing.md).
SHORT completed the real video-to-summary route and the user opened its summary
and transcript. STATIC transcription is understandable with remaining errors;
its uploaded summary failed language validation while the transcript stayed
available. English poll generation has narrow real-model evidence and requires
Lecturer review; Hebrew automatic generation is unavailable. Homework probes
missed real errors and invented gaps, so no homework website acceptance is claimed.
Gemini produced no substantive task-quality result. See the [tools report](docs/local-ai-feasibility.md#current-tools-and-evidence-index).

No in-class presentation, full phone acceptance, classroom load result or final
assignment conclusion is recorded. This is an interim results account for To Do
11, to be completed with observed demo results, limitations and remaining gaps.

## UC-05 submission foundation - local browser check

The UC-05 submission foundation is implemented: Lecturers create meeting-linked
assignments with instructions and one criterion per line; enrolled Students submit
text as append-only numbered versions. Owners see their history; current course
Lecturers can read all submitted versions. The status is **Submitted**, not reviewed
or published. Feedback request/draft/publication control flow and assignment language selection
are implemented, but the normal provider is disabled in both languages. No review
request is created when unavailable. Real-model individual feedback/comparison
and explicit demo-data cleanup remain incomplete. No model is called by this stage.

The local database migration `0007_homework_submissions` has been applied. On a
fresh checkout run `python manage.py migrate` in the website environment. Restart
an existing development server if it runs without autoreload; no AI worker is
needed for homework submission.

1. Sign in as **lecturer_alpha**, open **DEMO-CS101**, choose a meeting, then
   **Assignments and submissions -> New assignment**. Enter a title, instructions
   and one criterion per line, and create the assignment.
2. In a separate browser/private session, sign in as **student_alex**, open the
   same meeting/assignment, paste synthetic text and **Submit new version**.
   Check the save confirmation and **Version 1 / Submitted** reading page.
3. Return to the assignment and submit changed text. Check **Version 2** and open
   both saved links to confirm the original text is unchanged.
4. As lecturer_alpha, open the same assignment and either version. The page shows
   student, version number, submission time and exact escaped text.
5. Optional privacy check: as **student_casey** (another CS101 member), the other
   Student's links are absent; directly opening Alex's version URL returns 404.

Each submitted version now explains feedback-provider availability. No request
button or queue is offered while the selected language has no accepted provider. Assignment
editing/deletion is not included in this slice. Automated evidence and remaining
browser/phone limits are in [testing](docs/testing.md#uc-05-submission-foundation).

## UC-05 feedback workflow - current availability

The site stores a target feedback language (English/Hebrew) per assignment. **No
real homework provider is active in either language.** Opening a submitted version
shows that limitation before a request can be created. A forged/direct POST is
also rejected without a ReviewJob or fake result. Choosing a language is not
an AI-quality acceptance claim. There is no runtime demo/fake-provider setting.

The version-bound request, source/peer snapshots, task processing, private Lecturer
draft editing and separate publication are implemented as control flow. The full
Alex Version 1 request -> Version 2 submission -> Lecturer V1 draft -> separate
publication -> Student V1-only feedback route is verified with an injected
**test-only** provider. It is not a completed real-model feature or a normal-site
demo that a user can reproduce by clicking Generate today.

For a future accepted provider, queued work is processed separately with
`python manage.py run_homework_worker` (`--once` for one pass). With the current
factory the site creates no queue, so this worker is not needed for browser
checks. It cannot select a fake provider. Real-model adapters, per-language quality,
measured runtime/length/workload bounds and standalone demo-data cleanup remain.
See [executed workflow evidence](docs/testing.md#uc-05-feedback-workflow-controls)
and [current components](docs/architecture.md#uc-05-feedback-control-flow).

What can be checked now: as lecturer_alpha create an assignment with a chosen
language, then as student_alex submit/read its versions and observe the provider-
unavailable notice. No wait is started. Editing/publishing a generated draft can
currently be tested only by the automated test-only provider scenarios; no
prepared feedback is inserted into the live database.
