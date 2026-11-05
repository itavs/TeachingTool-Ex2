# Web-based Teaching Tool

An individual Exercise 2 project for Introduction to Software Engineering
(OOP / OOD): design a practical, simple web application for classroom teaching
and demonstrate its behavior in approximately ten minutes.

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
attendance D-05/D-06, connected comments D-18/D-19 with the D-17 offline gap,
polls D-08 through D-11, video D-12 through D-16, and homework D-20 through
D-22. AI workflows remain design targets; attendance and connected comments now have a Unit B implementation and server checks;
remaining operational parameters and open interpretations are explicit.
The shared website foundation is now implemented under D-23 through D-26;
Unit B implements attendance/XLSX and connected comments under D-27 through D-30. Unit C implements the poll lifecycle with explicit local demo data (D-31 through D-33). Real AI generation is disabled and unverified; video/homework website flows remain unimplemented.

| Capability | Assignment behavior | Design direction and open proposals |
|------------|---------------------|----------------------------------|
| Attendance | Automatic student attendance; lecturer receives an online/offline spreadsheet. | Approved D-05/D-06: lecturer opens a meeting and registration window; an identified student scans a temporary QR displayed in class and rotated during the window. The system validates code validity and meeting association, records attendance and time, and prevents duplicates per student and meeting. Lecturer views an online list and exports a point-in-time XLSX snapshot without synchronization back. |
| Comments and suggestions | Students contribute in real time / offline. | Approved D-18/D-19: identified comment/suggestion requests associated with a meeting, storage/history, student-own visibility, and lecturer access to all meeting requests with new requests appearing without manual refresh. D-17 preserves separate creation/submission/storage; offline meaning and coverage remain unresolved. |
| Polls | Lecturers create automatic, simple polls about current learning material. | Approved D-08 through D-11: lecturer selects comprehension or opinion before real model generation from pasted text. Both have one question and four single-choice options. Comprehension also includes one correct answer and a short explanation; opinion has no correct answer or correctness evaluation. Lecturer reviews/edits before publication only; identified students submit one final response. |
| Video summary | Lecturer obtains an ML summary of a class video. | Approved D-12 through D-16: manually upload an MP4 file from the computer; extract audio, transcribe speech, and summarize through a model in the recording's spoken language without translation. Target Hebrew and English, including a Hebrew lecture with English technical terms. Return a summary paragraph, 3-5 key points, full-transcript viewing, and an explicit notice that unspoken visual information is excluded. All support remains unverified. |
| Homework review | Students and teachers obtain deep LLM reviews including comparison with other students' work. | Approved D-20 through D-22: theoretical Hebrew/English pasted-text assignments, lecturer instructions/criteria, actual LLM feedback and processing of same-assignment peer submissions, student-own review/comparison without peer identities/full works, and lecturer access to all submissions/feedback. No-peer feedback explicitly states that no comparison occurred. |

One course, one lecturer, and one active meeting are proposed simplifications
(P-01), not approved limits. Video numeric duration/file-size limits, separate
demo duration and quality criteria, homework numeric limits, review output
language/peer-selection/revision rules, production access/security parameters,
retention/deletion details, comments' offline meaning, and classroom capacity
remain open. Website identity/access follows D-24; production readiness remains unverified.

For comments, creating content, attempting submission, and confirming storage
are separate responsibilities, so later offline clarification can be reflected
in the design (D-17). This does not approve local persistence, a send queue,
or disconnected synchronization. Online activity after class is not an
approved interpretation of offline, and that part of AS-02 is not yet covered
by an agreed design. The connected scope is now approved under D-18/D-19:
store identified meeting requests with history, student-own and lecturer-meeting
views, and live lecturer updates. Lecturer replies, discussion threads,
attachments, votes, and notifications are excluded.

Homework review uses pasted theoretical work in Hebrew and English against
lecturer-provided instructions/criteria, returning strengths, gaps, and
actionable recommendations (D-20). Comparison actually processes other works
for the same assignment and addresses topic coverage and solution approaches
(D-21). A student can request their own review; the lecturer can request any
submission and see all submissions/feedback for the assignment. The student
view excludes peer identities and full peer works. Without peers, personal
feedback is allowed with an explicit no-comparison notice. Grades, plagiarism
determinations, and submitted-code execution are excluded. The demo uses
sample works only; their count is not a system limit (D-22).

Approved polling scope includes one active poll per meeting, with another
created after the previous poll closes. The lecturer closes polls manually
and sees respondent counts and distributions as counts and percentages during
voting. Students see only aggregate results without respondent identities
after closure; comprehension answers and explanations are also revealed only
then. The scope excludes grades, file uploads, open-ended questions, and
automatic scheduling. Generation failure displays an error and permits retry,
without presenting prepared content as generated from the material. Poll
language is lecturer-selected Hebrew/English and material is limited to 6,000 characters under D-31 (Q-03 resolved); website identification follows D-24 and AI-service constraints remain unresolved. These are project decisions,
not details explicitly prescribed by AS-03.

Video input/output direction is approved: manual file upload, initial MP4
support, a summary paragraph and 3-5 key points, with an option to view the
full transcript (D-14). Planned verification includes Hebrew, English, and a
Hebrew lecture using English technical terms (D-15); sustained language
switching is outside the current commitment. These are unverified targets.
Maximum recording duration and file size will be set after processing-time
and cost measurements (D-16). Demo duration is separate; no numeric cap or
demo duration is fixed, and unlimited-length or full-lesson support is not
claimed. Small experimental measurements exist, but approved numeric system limits do not. See
Section 8 of the [register](docs/decisions-and-assumptions.md).

Attendance uses D-24 identity and the approved D-27 through D-29 timing, login-continuation and export rules. There are no manual corrections in this version (Q-01/Q-02 still track lecturer interpretation). The QR mechanism does not
conclusively prove physical presence or prevent real-time sharing of a
still-valid code. Lecturer acceptance of automatically and online/offline
has not been verified. XLSX export does not imply disconnected registration.

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

## Confirmed Decisions and Unselected Technology

- Python remains the main server/AI language (D-02).
- The approved Unit A implementation uses Django 5.2 LTS (installed 5.2.19),
  server-rendered Templates and CSS, and SQLite for initial development
  (D-23/D-26). Unit B adds small scripts for CSRF-protected scan submission and visible-page polling.
- Individual pre-created demo accounts use Django password hashing and sessions.
  Roles belong to course memberships, not global account flags (D-24).
- Lecturers create/edit meetings in their courses; students view only (D-25).
- AI provider, production database, hosting and classroom capacity are unresolved.
  Experiments do not establish a selected or integrated AI backend.
- Documents are English. Current UI copy is English as a reversible implementation
  choice; the final interface language remains open (Q-06).

The assignment requires no Moodle, Zoom or university information-system
integration. This does not remove any of the five feature requirements.

## Assignment Deliverables

The full project includes:

- A repository and README defining the problem and project scope.
- A technical tools evaluation report based on actual trials of every
  suggested tool.
- SoW, SRS, and the main use cases / client stories.
- Main software components, low-level class diagrams, and sequence diagrams.
- A testing strategy addressing the classes, with actual verification
  outcomes recorded separately from planned checks.
- An implemented or composed web demo, an approximately ten-minute in-class
  demonstration, and a short results conclusion.

The working horizon is about three weeks for an individual assignment.
The exact deadline, submission rules, actual class conditions, spending
limits, and live-processing expectations still need confirmation.

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
boundaries, and eligible-peer/revision policy affect technical choices;
numeric limits and other details can be refined during later design or trials.
Offline clarification gates that part of comments coverage, not unrelated
planning. The university-network study remains deferred and non-blocking.

## Project Status

Unit A is implemented: sign-in/out, course-scoped permissions, course/meeting
pages, lecturer meeting creation/editing, and isolated demo data. Unit B implements attendance, rotating QR windows, XLSX snapshots and connected private comments/history with lecturer polling. The poll lifecycle is implemented with labeled local demo drafts; real AI generation remains disabled and unverified. Video/homework website flows remain unimplemented.
See [architecture](docs/architecture.md) and [verification](docs/testing.md).

Local AI experiments produced measurable but mixed-quality results; Gemini
was a partial connectivity experiment with no task-quality result. See
[local AI feasibility](docs/local-ai-feasibility.md) and
[Gemini feasibility](docs/gemini-free-feasibility.md). These are separate from
website acceptance. No new AI experiment was run during Units A or B.

The foundation has automated server-side checks. The user reported successful
manual browser checks for login, courses/roles, meeting creation, description
persistence after refresh and absent student management buttons. These are
separate from the server permission tests. Agent browser access was denied;
viewport-specific visual and real-phone verification remain open.
SQLite development success does not establish classroom load readiness.

## Local Setup and Run

### Unit C — poll lifecycle and separate local demo fixtures

The website now supports draft review/editing, publication, one final response
per student, lecturer live counts/percentages, manual closure and post-close
student results. One poll may be active per meeting. Comprehension answers and
explanations are absent from student HTML/JSON until closure; opinion polls
have no correct answer or correctness evaluation. Poll material accepts at most
6,000 Unicode characters on the server; output-language choices are Hebrew and
English. This does not establish genuine AI language/generation quality.

Real generation is **disabled and unverified**. The generation form makes no
provider request and reports unavailable, without saving canned content. Fake
providers exist only in automated tests. For manual lifecycle checks, use the
separate local command after migrations:

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
and JavaScript logic tests; real AI generation is not a completed capability.

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
5-second visible-page polling. No offline storage, send queue or synchronization
is implemented. Connected use does not establish offline coverage.

See [executed checks and limitations](docs/testing.md) and the
[manual/private-LAN phone plan](docs/phone-testing.md). Phone access requires a
separately authorized temporary LAN binding and exact allowed host; no network
or firewall setting was changed during implementation. All website AI flows
remain unimplemented.

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
