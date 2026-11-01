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
all five must be implemented for the demo. Attendance direction D-05/D-06 and
polling decisions D-08 through D-11 are user-approved; remaining parameters
and other candidate limits below are open.

| Capability | Assignment behavior | Design direction and open proposals |
|------------|---------------------|----------------------------------|
| Attendance | Automatic student attendance; lecturer receives an online/offline spreadsheet. | Approved D-05/D-06: lecturer opens a meeting and registration window; an identified student scans a temporary QR displayed in class and rotated during the window. The system validates code validity and meeting association, records attendance and time, and prevents duplicates per student and meeting. Lecturer views an online list and exports a point-in-time XLSX snapshot without synchronization back. |
| Comments and suggestions | Students contribute in real time / offline. | Retained, identified comments visible to the lecturer, with live updates and asynchronous online access (P-04). This does not support disconnected operation. |
| Polls | Lecturers create automatic, simple polls about current learning material. | Approved D-08 through D-11: lecturer selects comprehension or opinion before real model generation from pasted text. Both have one question and four single-choice options. Comprehension also includes one correct answer and a short explanation; opinion has no correct answer or correctness evaluation. Lecturer reviews/edits before publication only; identified students submit one final response. |
| Video summary | Lecturer obtains an ML summary of a class video. | A short uploaded video is actually processed through audio extraction, transcription, and summarization (P-06). This omits silent visual content and full-length lessons. |
| Homework review | Students and teachers obtain deep LLM reviews including comparison with other students' work. | Real review of short text submissions against task criteria and actual peer submissions; proposed role-specific and anonymized views (P-07, P-08). |

One course, one lecturer, and one active meeting are proposed simplifications
(P-01), not approved limits. Video length/language, homework formats and volume,
identity, access rules, comments' offline meaning, and classroom capacity
remain open.

Approved polling scope includes one active poll per meeting, with another
created after the previous poll closes. The lecturer closes polls manually
and sees respondent counts and distributions as counts and percentages during
voting. Students see only aggregate results without respondent identities
after closure; comprehension answers and explanations are also revealed only
then. The scope excludes grades, file uploads, open-ended questions, and
automatic scheduling. Generation failure displays an error and permits retry,
without presenting prepared content as generated from the material. Poll
language and the input-length limit remain open (Q-03); shared identification
and AI-service constraints remain unresolved. These are project decisions,
not details explicitly prescribed by AS-03.

Attendance identity method, QR rotation/validity and registration-window
timings, transition rules, late-arrival handling, export fields, and any
online correction behavior remain open (Q-01, Q-02). The QR mechanism does not
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

- **Python** is the user-approved main language for the server and AI
  processing (D-02).
- The assignment handout does not restrict the implementation language;
  inspection found no conflict with Python.
- The web interface should favor simplicity, but no frontend solution,
  framework, AI provider, database, or deployment platform has been selected.
- Project documentation is written in English (D-03).

The assignment does not require integration with Moodle, Zoom, or the
university personal-information system. This does not remove the requirement
to process a class video or the other required inputs.

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

## Project Status

Initial README, SoW, SRS, and decisions-register drafts have been prepared
(D-04). Attendance direction D-05/D-06 and polling decisions D-08 through D-11
are approved; remaining proposal details are still open. Review has covered
document consistency only; no application,
AI workflow, network experiment, or runtime verification has been
implemented. Build/run instructions and application test results are not yet
available; AI quality, processing time, and classroom-scale behavior remain
unmeasured.

## Source and Reference Material

The two-page Exercise 2 handout, `I2SE_Exe2.docx.pdf`, is a local untracked
reference and is not included in the repository. Its requirements are
paraphrased with page references in the decisions register.

The local Exercise 1 README and relevant `docs` files were consulted read-only
for documentation style and structure. They are not sources of Exercise 2
requirements or technology decisions. See
[Plane-Projection-of-3D-volume](https://github.com/itavs/Plane-Projection-of-3D-volume).
