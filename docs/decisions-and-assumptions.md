# Decisions and Assumptions Register

## 1. Purpose and Status

This register is the shared source of decision status for the initial
requirements drafts. It does not approve the proposed demo reductions.
No application behavior, AI experiment, or runtime test has been implemented
or verified in this stage.

Use the following labels throughout the project:

- **Assignment requirement:** explicitly stated in the Exercise 2 handout.
- **User-approved decision:** explicitly approved by the project owner.
- **Open proposal:** suggested behavior or scope, awaiting approval.
- **Open question:** missing information or an unresolved interpretation.

An approved planning target is not automatically a lecturer-confirmed
interpretation. Draft acceptance criteria describe future checks, not results.

## 2. Assignment Sources

Source: `I2SE_Exe2.docx.pdf`, reviewed in full (two pages). The handout is
currently a local, untracked reference; cloning the repository alone does not
provide it. The rows below are paraphrases, not additional lecturer instructions.

| ID | Page | Assignment requirement or guidance |
|----|------|------------------------------------|
| AS-01 | 1 | Automatic student attendance and an online/offline spreadsheet of details for the lecturer. |
| AS-02 | 1 | Student comments and suggestions in real time / offline. |
| AS-03 | 1 | Lecturers can create automatic, simple polls about current learning materials. |
| AS-04 | 1 | Lecturers can obtain an ML summary of a class video, such as a recording from Zoom, Meet, or Google Classroom. |
| AS-05 | 1 | Students and teachers can obtain a deep LLM homework review, including comparisons with other students' work. |
| AS-06 | 1 | The system should work in the actual class. |
| AS-07 | 1 | Students use a simple smartphone web application (KISS). |
| AS-08 | 1 | Design must be implementable; design is the focus, implementation is secondary, reuse is preferred, and integration with Moodle, Zoom, or the university personal-information system is not required. |
| AS-09 | 1 | Compose a web application and demonstrate it in class in approximately ten minutes. |
| AS-10 | 2 | Create a repository and define the problem and scope in README. |
| AS-11 | 2 | Produce a technical tools report and actually try every suggested tool. |
| AS-12 | 2 | Define SoW, SRS, and the main use cases / client stories. |
| AS-13 | 2 | Define main components, low-level class and sequence diagrams, and a testing strategy addressing the classes. |
| AS-14 | 2 | Implement or compose a simple web demo, demonstrate it, and write a short account of the results. |

The handout does not prescribe a programming language. Its references to OOP,
OOD, classes, and composing an application do not specify Java or another
language. No conflict with the approved Python choice was found in the handout;
this is a document inspection, not separate confirmation from the lecturer.

## 3. User-Approved Decisions

| ID | Decision | Boundary |
|----|----------|----------|
| D-01 | Plan a demo with all five capabilities genuinely active. | User-approved planning target; not yet verified with the lecturer as the required implementation coverage. |
| D-02 | Python is the main language for the server and AI processing. Prefer simplicity when choosing the web interface later. | No framework, AI provider, storage system, hosting platform, or frontend solution has been selected. |
| D-03 | All project documents are in English; explanations and progress reports to the user are in Hebrew. Code and commit messages are in English. | This supersedes the earlier request for Hebrew documents. |
| D-04 | During the initial requirements-drafting stage, README, draft SoW, draft SRS, and this register were prepared, and AGENTS.md was updated to distinguish documentation and conversation languages. | Historical documentation milestone; application implementation and runtime verification were not part of that stage. It did not approve the open demo reductions. |

The project is an individual assignment. The working planning horizon is about
three weeks, as provided by the user; the exact deadline is not confirmed.

## 4. Open Demo Proposals

None of the following rows is an approved limitation. Requirements and use cases
that depend on a row remain conditional until it is resolved.

| ID | Open proposal | Effect and unresolved boundary |
|----|---------------|--------------------------------|
| P-01 | One course, one lecturer, and one active meeting at a time. | Reduces administration; actual class size and concurrency remain unknown. |
| P-02 | Entering a meeting as an identified student automatically records identity and arrival time, with duplicate prevention. | Does not establish physical presence; identity and attendance trigger need approval. |
| P-03 | Lecturer sees a live attendance table and downloads a spreadsheet with name, identifier, and arrival time. | Whether a table plus a downloadable file satisfies online/offline spreadsheet requirements, and the file format and fields, remain open. |
| P-04 | Offline comments mean asynchronous access outside lesson time, with an internet connection. Retain comments; show identified comments only to the lecturer. | Does not provide disconnected operation or later synchronization; interpretation and visibility require approval. |
| P-05 | Generate one single-choice poll from a short pasted lesson text using a real model; lecturer reviews before publication; one response per student and one active poll. | Generation method, input bounds, question format, editing, and voting rules are proposals. |
| P-06 | Manually upload a one-to-two-minute video in one agreed language; extract audio, transcribe it, and summarize the transcript using actual model processing. | Does not interpret silent slides or board content, process full lessons, or import recordings automatically. The video-to-summary pipeline must actually run if approved. |
| P-07 | One homework assignment, about three short text submissions of a few hundred words, lecturer-provided instructions and criteria, and real LLM review and cross-submission comparison. | Text-only input, workload, review rubric, and depth require approval; numeric grading, plagiarism judgments, and code execution are not proposed for the basic demo. |
| P-08 | Students see their own review and anonymized comparisons; the lecturer sees all reviews. Use clearly identified sample inputs for the demo. | Access controls, consent, use of actual student work, retention, deletion, and what may be sent for AI processing are unresolved. |
| P-09 | Prepare demo inputs in advance and aim to show actual processing within ten minutes. Label any previously processed output explicitly. | Runtime is unmeasured. Previously processed results are not a substitute for a live-processing requirement without approval; simulated output cannot establish capability completion. |

## 5. Questions Requiring Decisions

| ID | Question | Related items | Resolution needed |
|----|----------|---------------|-------------------|
| Q-01 | What counts as automatic attendance, and what identity or physical-presence evidence is needed? | AS-01, P-02 | User scope decision; lecturer clarification if assignment interpretation remains uncertain. |
| Q-02 | Does offline mean asynchronous online access or operation without a network? What spreadsheet behavior is expected? | AS-01, AS-02, P-03, P-04 | Resolve separately for attendance export and student comments before implementing these paths. |
| Q-03 | Is model-generated single-choice polling from pasted text sufficient, and which response/publication rules apply? | AS-03, P-05 | User approval of proposed workflow and input bounds. |
| Q-04 | Is an audio-based summary of a short uploaded video sufficient? Which language, duration, formats, and quality criteria apply? | AS-04, P-06 | User scope decision and any necessary lecturer clarification. |
| Q-05 | Which homework types, comparison population, review criteria, and depth are required? | AS-05, P-07, P-08 | User approval before fixing inputs, review behavior, and acceptance fixtures. |
| Q-06 | How many classroom users, devices, and simultaneous actions must be supported, and where must the demo be accessible? | AS-06, AS-07, P-01 | Actual class conditions, network availability, and measurable usability/capacity targets. |
| Q-07 | What identity, access, data-use, consent, retention, deletion, and AI-spending boundaries apply? | P-02, P-04, P-08, D-02 | User approval before external processing, paid use, or actual student-data use; no budget is assumed. |
| Q-08 | What are the exact deadline, submission format, templates, and assessment criteria? | AS-10 through AS-14 | User or lecturer information; do not invent submission rules. |
| Q-09 | Must every AI output finish live during the presentation, and what is the acceptable duration and quality of each result? | AS-09, D-01, P-09 | User decision plus later measured feasibility; disclose any approved use of earlier results. |

## 6. Reference Style and Change Control

The Exercise 1 README and relevant documentation were consulted as references
for concise sections, responsibility tables, requirement identifiers, explicit
limits, and separation of plans from observed results. The repository reference is
[Plane-Projection-of-3D-volume](https://github.com/itavs/Plane-Projection-of-3D-volume).
Its application requirements, Java choices, algorithms, measurements, and test
results are not Exercise 2 decisions or evidence.

The primary agent maintains this register. When the user resolves an item,
record the actual decision, update its status and dependent documents, and
preserve the distinction between user approval and lecturer confirmation.
Do not silently promote a proposal into a requirement or a verified result.
