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
D-22. These are design targets, not implemented or verified capabilities;
remaining operational parameters and open interpretations are explicit.

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
language/peer-selection/revision rules, shared identity/access mechanisms,
retention/deletion details, comments' offline meaning, and classroom capacity
remain open. Approved visibility rules do not choose their enforcement method.

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
language and the input-length limit remain open (Q-03); shared identification
and AI-service constraints remain unresolved. These are project decisions,
not details explicitly prescribed by AS-03.

Video input/output direction is approved: manual file upload, initial MP4
support, a summary paragraph and 3-5 key points, with an option to view the
full transcript (D-14). Planned verification includes Hebrew, English, and a
Hebrew lecture using English technical terms (D-15); sustained language
switching is outside the current commitment. These are unverified targets.
Maximum recording duration and file size will be set after processing-time
and cost measurements (D-16). Demo duration is separate; no numeric cap or
demo duration is fixed, and unlimited-length or full-lesson support is not
claimed. No such measurement has been performed. See
Section 8 of the [register](docs/decisions-and-assumptions.md).

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

Section 9 of the [register](docs/decisions-and-assumptions.md) consolidates
remaining decisions: identity/access, teaching context/capacity, AI/data/budget
boundaries, and eligible-peer/revision policy affect technical choices;
numeric limits and other details can be refined during later design or trials.
Offline clarification gates that part of comments coverage, not unrelated
planning. The university-network study remains deferred and non-blocking.

## Project Status

Initial README, SoW, SRS, and decisions-register drafts have been prepared
(D-04). First-version design targets for all five capabilities are recorded,
with the offline comments gap and other open parameters retained. Review has
covered document consistency only; no application, AI workflow, network
experiment, or runtime verification has been implemented. Build/run
instructions and application test results are not yet
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
