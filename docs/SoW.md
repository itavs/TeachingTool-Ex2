# Statement of Work
## Web-Based Teaching Tool - Draft

## 1. Purpose

This document defines the intended work, deliverables, boundaries, and review
points for Exercise 2 in Introduction to Software Engineering (OOP / OOD).
The project addresses the need for simpler classroom tools that support
learning and make practical use of AI.

The assignment emphasizes implementable design and reuse over writing code
from scratch. It nevertheless requires a working web demonstration and a
class presentation of approximately ten minutes (AS-08, AS-09, AS-14).

Requirement sources, approval status, and unresolved interpretations are
maintained in the
[Decisions and Assumptions Register](decisions-and-assumptions.md).
Detailed behavior and proposed acceptance checks belong in the
[SRS](SRS.md); the project overview belongs in [README](../README.md).

## 2. Sources and Approved Direction

| Basis | Meaning for this work |
|-------|-----------------------|
| Assignment requirements | AS-01 through AS-14 identify the handout requirements and guidance. |
| D-01 | The user approved planning for all five capabilities to be genuinely active in the demo. This coverage is not yet a lecturer-confirmed interpretation of the required implementation scope. |
| D-02 | Python is the main language for the server and AI processing; the future web interface should favor simplicity. |
| D-03 | All project documents are in English; explanations and progress summaries to the user are in Hebrew. |
| D-05 | Attendance uses student identification and a temporary QR displayed in class and rotated during the lecturer's open registration window; validate the code and meeting, record attendance and time, and prevent duplicates. Identity follows D-24; timings, transitions and additional-window registration follow D-27/D-28. |
| D-06 | Lecturer receives an online attendance list and XLSX snapshot export, without synchronization of file edits back to the application. Lecturer interpretation of online/offline remains unverified. |
| D-07 | University-network-origin checking is conditional on feasibility and a later decision; it is not an approved implementation requirement or a completed experiment. |
| D-08 through D-11 | Approved polling design: lecturer-selected comprehension or opinion, real model generation from pasted text, four options, lecturer review/editing before publication only, final student responses, manual closure, role-specific results, and defined exclusions/error handling. D-31 resolves language and input length; D-32 is the historical disabled stage; D-44 implements local English generation, with Hebrew generation unavailable and semantic review still required. |
| D-12 through D-16 | Target Hebrew and English video recordings, including Hebrew with English technical terms, through manual computer-file upload with initial MP4 support. Use audio extraction/transcription/model summarization, same-language output without translation, and an explicit unspoken-visual-content notice. Return a summary paragraph, 3-5 key points, and full-transcript viewing. Sustained language switching is outside the commitment. Set maximum duration/file size after time/cost measurements; demo duration is separate. Unit D implements validation/audio extraction; local transcription is implemented under Unit E; word accuracy and summary quality remain unverified. |
| D-17 | Clarified by the user on 2026-11-11: online means during class; offline means outside class. Both use normal website submission to a meeting, including a past meeting. Creation, submission and storage remain distinct; no local persistence, send queue or disconnected synchronization is required. |
| D-18/D-19 | Identified meeting comments/suggestions, storage/history, student-own and lecturer-meeting views, and live lecturer updates. No lecturer replies, threads, attachments, votes, or notifications. D-17 resolves during/outside-class use through the same connected workflow. |
| D-20 through D-22 | Theoretical Hebrew/English pasted homework, lecturer criteria, real LLM review and same-assignment comparison, student-own feedback without peer identities/full works, lecturer access to all assignment submissions/feedback, and explicit no-peer comparison notice. No grades, plagiarism determinations, or code execution. Demo uses sample works only; sample count is not a system limit. |

The reviewed handout does not specify a programming language. No conflict with
Python was found; this finding does not select a framework or AI service.
D-23 through D-26 subsequently approve Django/Templates, initial SQLite,
individual demo accounts, course-membership roles and lecturer meeting
management. Local turbo/Qwen adapters are selected for video and English polls; homework AI and production hosting remain open.

## 3. Planned Capability Coverage

The baseline covers approved first-version directions for all five capabilities:
attendance D-05/D-06, comments D-18/D-19 with the resolved D-17 timing interpretation,
polls D-08 through D-11, video D-12 through D-16, and homework D-20 through
D-22. Open parameters and lecturer interpretations remain explicit. Approval
is not implementation evidence or lecturer confirmation. Changing or dropping
a capability requires a user decision.

| Capability and source | Required planning outcome | Approved direction or open proposal | Remaining boundaries |
|-----------------------|---------------------------|--------------------------|--------------------------------------|
| Attendance (AS-01) | Automatic attendance and lecturer access to an online/offline spreadsheet of student details. | Approved D-05/D-06: lecturer opens a meeting and a registration window; identified student scans a temporary QR displayed in class and rotated during the window. Validate code validity and meeting association, record attendance and time, prevent duplicates per student and meeting, and provide an online list and XLSX snapshot without synchronization back. | Identity follows D-24; code/window rules and additional-window registration follow D-27/D-28; fields/no manual corrections follow D-29. Lecturer interpretation remains Q-01/Q-02. Physical presence is not proven conclusively and real-time sharing of a valid code is not prevented. Lecturer acceptance of automatically and online/offline is unverified. |
| Comments and suggestions (AS-02) | Student comments and suggestions in real time / offline. | D-17 clarifies online as during class and offline as outside class, both through normal connected website submission to an associated meeting, including a past meeting. D-18/D-19 retain identified comment/suggestion requests, stored history, student-own visibility, lecturer access and live lecturer updates. | No local persistence, send queue or disconnected synchronization is required. Lecturer replies, threads, attachments, votes and notifications remain excluded. Identity follows D-24; retention and classroom capacity remain open. |
| Automatic polls (AS-03) | Lecturers can create simple polls automatically about current learning material. | Approved D-08 through D-11: lecturer selects comprehension or opinion before real model generation from pasted text. Both types have one question and four single-choice options; comprehension adds one correct answer and short explanation, while opinion has no correct answer or correctness evaluation. All generated content can be reviewed/edited before publication only. Each identified student submits one final response; one active poll per meeting, with further creation after manual closure. Lecturer sees live counts/percentages; students see aggregates without identities only after closure, plus comprehension answer/explanation then. | D-31 fixes lecturer-selected Hebrew/English output and 6,000 material characters; shared identity/capacity/AI constraints remain Q-06/Q-07. These detailed rules are project choices, not explicit handout requirements. No grades, file uploads, open-ended questions, or automatic scheduling. Generation failure provides an error and retry without prepared-content substitution. |
| Class-video summary (AS-04) | The lecturer receives an ML-generated summary derived from a class video. | Approved D-12 through D-16: manually upload an MP4 from the computer; extract audio, transcribe speech, and summarize through a model in the recording's spoken language without translation. Target Hebrew, English, and Hebrew with English technical terms. Display a summary paragraph, 3-5 key points, an option to view the full transcript, and a notice that unspoken visual information is excluded. | Targets are unverified. Sustained language switching is outside the commitment. D-34 fixes initial system limits at 4 minutes/200 MB. Separate demo duration, model quality and lecturer interpretation remain open (P-06/Q-04). Unit D validates/extracts audio; Unit E adds full-transcript viewing, with word accuracy unverified and summaries disabled. |
| Homework review and comparison (AS-05) | Students and teachers receive deep LLM reviews, including comparison with other students' work. | D-20 through D-22 approve theoretical Hebrew/English pasted submissions, lecturer instructions/criteria, strengths/gaps/actionable recommendations, and actual same-assignment peer comparison of topic coverage and solution approaches. Student requests/views own feedback/comparison without peer identities/full works; lecturer may review any submission and sees all submissions/feedback. No-peer feedback explicitly says no comparison occurred. | No grades, plagiarism determinations, or code execution. Demo uses sample works only; sample count is not a system cap. Peer selection/revisions, output language, numeric workload/input limits, quality, and data/resource details remain Q-05/Q-07. No capability has been verified. |

The proposed administrative boundary is one course, one lecturer, and one active
meeting (P-01). Neither the actual class size nor a concurrency limit has been
approved. AS-06 requires actual classroom operation, and AS-07 requires a simple
smartphone web experience; a small presentation dataset alone cannot establish
that these requirements have been met (Q-06).

Moodle, Zoom, and university personal-information-system integrations are not
required by the handout (AS-08). Their absence does not remove the requirement
to process a video or perform any other capability.

For comments, keep creation, submission and storage distinct (D-17). Creation alone is not delivery, and a submission attempt is not confirmed storage. The user has resolved online/offline as during/outside class; both use the connected website and keep the request associated with the selected meeting. Past meetings remain eligible. No disconnected mechanism is needed.

Homework demo works are samples only (D-22). Their number does not define a
submission limit or restrict the system to one assignment. The approved
review and comparison must process actual work and peer inputs; sample data
does not authorize canned feedback or fabricated comparisons.

For video summaries, manual computer-file upload with initial MP4 support, a
summary paragraph with 3-5 key points, and full-transcript viewing are approved
implementation targets (D-14). Planned verification includes Hebrew, English,
and Hebrew speech with English technical terms (D-15). Sustained language
switching is outside the current commitment. Actual Hebrew/English samples were
processed, but word accuracy and broad summary quality remain unaccepted.
Audio-only processing does not analyze unspoken slides, formulas, or board
content; lecturer acceptance of this interpretation of the video requirement
is not confirmed. A transcript supplied on its own does not demonstrate the
approved extraction/transcription/summarization pipeline.

D-34 now approves 4 minutes and 200 MB as initial system limits. Demo duration remains separate/undecided, not an unlimited-length claim. Unit D implements validation and real audio extraction; local transcription is implemented under Unit E, with word accuracy unverified; local Qwen3 summaries are implemented with known grounding/language failures. The earlier D-16 measurement-first policy informed these limits; see video-processing.md for current measurements and operational boundaries.

University-network origin is only a conditional option (D-07, P-10, Q-10), not
an additional attendance requirement. The proposed feasibility study in
Section 7 of the [register](decisions-and-assumptions.md) separates local review
from observations requiring campus access. No network experiment or measurement
has been completed, and no university address ranges are assumed.
The study is deferred and is not a dependency that blocks other project work.

## 4. Project Deliverables

The full assignment includes the deliverables below. Completion evidence must
reflect the actual implementation and verification, rather than the presence
of a plan alone.

| Deliverable | Assignment basis | Completion evidence to produce later |
|-------------|------------------|--------------------------------------|
| Repository and README problem/scope definition | AS-10 | A repository with a README that describes the problem, scope, documentation, and actual project status. |
| SoW, SRS, and main use cases | AS-12 | Documents updated as questions are resolved and implementation clarifies behavior. |
| Technical tools report | AS-11 | Actual trials of every suggested tool, with observed suitability, failures, and limits separated from plans. |
| Main software components | AS-13 | Documented responsibilities and interfaces consistent with the selected design. |
| Low-level class diagrams and sequence diagrams | AS-13 | Diagrams aligned with the implemented responsibilities and principal workflows. |
| Testing strategy addressing the classes | AS-13 | Planned class-level and integration checks tied to requirements; later execution evidence reported separately. |
| Implemented or composed web demo | AS-09, AS-14, D-01 | All five capabilities operating genuinely within the approved scope. |
| In-class demonstration | AS-06, AS-07, AS-09, AS-14 | Observed classroom use and an approximately ten-minute presentation, with disclosed limitations. |
| Short conclusion and results account | AS-14 | What worked, what was actually checked, failures, limitations, and remaining gaps. |

No specific submission packaging, templates, or assessment rubric is assumed;
these remain questions for the user or lecturer (Q-08).

## 5. Student Responsibilities

This is an individual assignment. The student is responsible for:

- **Planning and design:** interpreting the assignment, resolving scope
  questions, evaluating tools, and maintaining requirements, component
  responsibilities, class diagrams, and sequence diagrams.
- **Implementation and integration:** implementing or composing the web
  application so that the five capabilities operate within the agreed scope.
- **Verification:** defining the testing strategy, checking components and
  integrated workflows, evaluating actual classroom and smartphone behavior,
  and recording observed results, failures, and limitations.
- **Presentation and submission:** preparing and rehearsing the demonstration,
  keeping documents consistent with the delivered behavior, and submitting
  the required artifacts and short conclusion according to confirmed rules.

AI assistance and reused tools may be documented separately where required.
Their use does not transfer responsibility for the design, correctness,
verification, or submission away from the student.

## 6. Indicative Milestones

The user describes an individual assignment with about three weeks available.
The exact deadline is unconfirmed. The sequence below is an indicative project
plan, not a confirmed calendar.

1. **Requirements and scope:** prepare and refine README, SoW, SRS, and the
   decisions register, retaining unresolved scope explicitly.
2. **Scope resolution and feasibility:** obtain material decisions, trial
   candidate tools, and choose an implementable design. Resolve cost and
   data-use constraints before paid or external processing.
3. **Incremental implementation and documentation:** implement approved paths,
   update components and diagrams, and check each capability as it becomes
   available.
4. **Integration, classroom checks, and rehearsal:** verify the combined
   workflow under agreed conditions, measure actual AI processing times,
   rehearse the presentation, and address routine defects.
5. **Submission preparation and conclusion:** align documents with observed
   behavior, record results and limitations, and package according to confirmed
   submission instructions.

The remaining time must cover design and written deliverables as well as the
demo. If feasibility conflicts with the five-capability target or approved
scope, the student records the conflict for an explicit scope decision rather
than silently reducing the deliverables.

## 7. Dependencies and Risks

| Dependency or risk | Required handling |
|--------------------|-------------------|
| Remaining scope parameters and lecturer interpretations | Approved targets cover all five capabilities. D-17 resolves comments timing; Q-01 through Q-07 track unresolved identity, operating parameters, capacity, resources, quality, and lecturer interpretation. Do not reopen approved comments/homework behavior or silently invent numeric caps. |
| Conditional university-network option | Investigate the proposed P-10 study and Q-10 before any separate adoption decision. Do not treat university-origin traffic as proof of identity or physical classroom presence (D-07). |
| Actual class conditions and smartphone access | Confirm devices, user count, connectivity, and access location; do not equate a small local demo with classroom readiness (Q-06). |
| Identity, authorization, and student-data exposure | Enforce approved visibility from D-10/D-18/D-21. Initial identity/access is D-24; production safeguards, permitted integrated AI inputs, consent, retention/deletion and budget remain Q-07. Homework demo inputs are sample works only under D-22. |
| AI availability, output quality, cost, and processing time | Trial proposed tools later, use actual inputs, record observed results, and seek approval for payment. No budget or performance guarantee is assumed. |
| Ten-minute presentation feasibility | Measure actual video and review processing time and rehearse before claiming the presentation fits (P-09, Q-09). |
| Unknown deadline and submission rules | Confirm Q-08 and adjust the plan explicitly if needed. |

Section 9 of the [register](decisions-and-assumptions.md) distinguishes decisions
needed before fixing affected technical choices from details that can be
refined later. Shared identity, teaching context/capacity, data/AI/budget
boundaries, and peer-selection/revision policy affect architecture. D-17 resolves the comments timing interpretation without requiring disconnected functionality. Initial video limits are fixed by D-34 at 4 minutes/200 MB; demo duration remains open, and the university-network study remains deferred.

## 8. Demo and Assignment Acceptance

Future acceptance requires genuine operation of the approved first-version
workflows across all five capabilities, with evidence of actual classroom and
smartphone suitability. The clarified D-17 timing scenarios must be verified through the normal comments workflow; this does not establish phone or classroom-capacity acceptance. Detailed
checks are drafted in SRS.md, with unresolved parameters explicit; they are
not completed tests or final acceptance thresholds.

Prepared inputs may support a demo if their nature is disclosed. A prerecorded
screen, canned AI answer, or simulated action cannot establish that a required
capability works. Previously processed output must be labeled, and cannot
replace a requirement for live completion without approval (P-09, Q-09).
Failures and partial processing must not be presented as successful outcomes.

## 9. Project Status

The user has sent the lecturer three interpretation questions: rotating-QR
attendance, online attendance list with XLSX snapshot, and speech-only video
summary. All three await replies; implemented behavior is not lecturer acceptance.
D-17 comments during/outside class is already resolved. See the
[clarification register](decisions-and-assumptions.md#lecturer-clarification-requests---sent-awaiting-reply).

The website implements Django/Templates authentication and course-membership roles,
meeting management, attendance/QR/XLSX, connected comments during or outside class,
and the complete poll lifecycle. Local Qwen3 8B generates **English** editable poll
drafts; Hebrew editing/publication/voting remain supported, but Hebrew automatic
generation is unavailable. New MP4 jobs validate/extract audio, transcribe with the
pinned local large-v3-turbo CUDA checkpoint, then summarize with local Qwen3 8B.
A failed summary retains an available saved transcript; legacy completed jobs are
unchanged. Homework review/comparison remains **feasibility experiments only**, not
a website feature. Functional operation does not establish reliable AI accuracy,
phone usability, classroom capacity or a completed in-class demonstration.

The original Unit C disabled-provider and Unit D extraction-only milestones are
historical, not current capability descriptions. D-34 fixes 240 seconds and
200,000,000 bytes; D-38 through D-43 cover current video transcription/summary,
privacy, deadline and retention. D-44 covers English poll generation. D-17 is
resolved for comments only; attendance interpretations remain Q-01/Q-02.

Evidence and limitations: [tools report](local-ai-feasibility.md#current-tools-and-evidence-index),
[current architecture](architecture.md), [class-aware strategy and results](testing.md#current-component-to-test-strategy).
The full assignment still requires homework planning/integration if the unchanged
five-capability target is retained, actual classroom/phone verification, an
approximately ten-minute demonstration and a final results conclusion. No such
class demonstration or final conclusion has been recorded. These are remaining
deliverables, not permission to begin them.
