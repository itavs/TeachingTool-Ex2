# Decisions and Assumptions Register

## 1. Purpose and Status

This register is the shared source of decision status for the requirements
drafts. It records approved attendance and polling decisions separately from
the remaining open demo proposals.
No application behavior, AI experiment, or runtime test has been implemented
or verified in this stage.

Use the following labels throughout the project:

- **Assignment requirement:** explicitly stated in the Exercise 2 handout.
- **User-approved decision:** explicitly approved by the project owner.
- **Open proposal:** suggested behavior or scope, awaiting approval. Superseded
  or partly resolved proposals are retained with their current status.
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
| D-05 | The lecturer opens a meeting and an attendance-registration window. An identified student scans a temporary QR displayed in class and rotated during that window. The system validates the code's validity and meeting association, records attendance and time, and prevents duplicate attendance for the same student and meeting. | Approved design direction, not implemented or lecturer-confirmed. Identity method, window/rotation/validity timings, transition rules, and late-arrival handling remain open. The mechanism does not conclusively prove physical presence or prevent real-time sharing of a still-valid code. |
| D-06 | The lecturer views an online attendance list and can export it to XLSX. The exported file is a point-in-time snapshot, with no synchronization of edits back into the application. | Approved output behavior. Exact fields and any online correction behavior remain open. Acceptance of this interpretation of online/offline by the lecturer is unverified; disconnected attendance registration is not implied. |
| D-07 | A university-network-origin check is only a conditional option subject to a feasibility study. | It is not an approved implementation requirement. The study is deferred, not executed, and does not block other project work; using a network check would require a further decision. It cannot be treated as proof of a person's identity or physical classroom presence. |
| D-08 | Before generation, the lecturer selects a comprehension question or an opinion poll. A real model generates a question and four single-choice options from pasted learning text. For comprehension it also proposes one correct option and a short explanation; opinion polls have neither a designated correct answer nor correctness evaluation. | Approved project design for AS-03; the handout does not prescribe these types or require an LLM for polls. Poll language and input-length limit remain open (Q-03). No model/provider or framework is selected. |
| D-09 | The lecturer reviews and may edit all generated content before publication only, including the correct answer and explanation for comprehension questions. Each identified student submits one final response per poll with no changes after submission. One poll may be active per meeting; additional polls can be created after the previous poll closes. Closure is manual. | Approved workflow, not implemented. The shared student-identification method remains unresolved (Q-07); the one-active-poll rule is per meeting, not a global one-meeting limit. |
| D-10 | During voting, the lecturer sees the respondent count and response distribution as counts and percentages. Students see aggregate results only after closure, without respondent identities. For comprehension questions the correct answer and short explanation are also revealed to students only after closure. | Approved visibility rules. No grades are assigned; opinion polls never designate or evaluate a correct answer. Approval does not establish implementation or verification. |
| D-11 | The basic polling scope excludes grades, file uploads, open-ended questions, and automatic scheduling. Generation failure produces an error and a retry option, without presenting prepared content as generated from the supplied material. | Approved scope and failure behavior. Actual generation, error recovery, and result visibility still require later implementation and verification. |

The project is an individual assignment. The working planning horizon is about
three weeks, as provided by the user; the exact deadline is not confirmed.

## 4. Proposal Register

P-02 and P-03 retain the history of the earlier attendance proposals and their
resolution by D-05 and D-06. P-05 records the polling proposal resolved by
D-08 through D-11. Other rows remain open proposals; their inclusion does not
approve an implementation requirement or scope reduction.

| ID | Proposal and current status | Effect and unresolved boundary |
|----|---------------|--------------------------------|
| P-01 | One course, one lecturer, and one active meeting at a time. | Reduces administration; actual class size and concurrency remain unknown. |
| P-02 | Superseded by D-05: the earlier proposal used identified meeting entry as the attendance trigger. | The approved trigger is now a valid, meeting-bound rotating QR during an open registration window; meeting entry alone is not the selected trigger. Identity, timing, and late-arrival details remain open. |
| P-03 | Partly resolved by D-06: online list and XLSX snapshot export without synchronization back are approved. | Exact fields and online corrections remain open; lecturer confirmation of the online/offline interpretation is still needed. |
| P-04 | Offline comments mean asynchronous access outside lesson time, with an internet connection. Retain comments; show identified comments only to the lecturer. | Does not provide disconnected operation or later synchronization; interpretation and visibility require approval. |
| P-05 | Resolved by D-08 through D-11: model-generated comprehension questions and opinion polls from pasted learning text, four single-choice options, pre-publication lecturer review/editing, final responses, and one active poll per meeting. | Poll types, lifecycle, results visibility, exclusions, and failure/retry behavior are approved. Language and input-length limit remain open under Q-03; this row is historical, not a pending vote on the approved workflow. |
| P-06 | Manually upload a one-to-two-minute video in one agreed language; extract audio, transcribe it, and summarize the transcript using actual model processing. | Does not interpret silent slides or board content, process full lessons, or import recordings automatically. The video-to-summary pipeline must actually run if approved. |
| P-07 | One homework assignment, about three short text submissions of a few hundred words, lecturer-provided instructions and criteria, and real LLM review and cross-submission comparison. | Text-only input, workload, review rubric, and depth require approval; numeric grading, plagiarism judgments, and code execution are not proposed for the basic demo. |
| P-08 | Students see their own review and anonymized comparisons; the lecturer sees all reviews. Use clearly identified sample inputs for the demo. | Access controls, consent, use of actual student work, retention, deletion, and what may be sent for AI processing are unresolved. |
| P-09 | Prepare demo inputs in advance and aim to show actual processing within ten minutes. Label any previously processed output explicitly. | Runtime is unmeasured. Previously processed results are not a substitute for a live-processing requirement without approval; simulated output cannot establish capability completion. |
| P-10 | Optionally check whether a registration request comes through the university network, subject to feasibility (D-07). | No network restriction is approved. Address ranges, actual request path, VPN/shared-address effects, IPv4/IPv6 behavior, and handling of unavailable evidence require investigation and a later decision (Q-10). |

## 5. Questions Requiring Decisions

| ID | Question | Related items | Resolution needed |
|----|----------|---------------|-------------------|
| Q-01 | Which identity method, registration-window duration, QR rotation/validity timings, transition rules, and late-arrival handling should accompany D-05? Does the lecturer accept this mechanism as automatically recording attendance? | AS-01, D-05, P-02 | Direction approved; these details remain open. Physical presence is not guaranteed, and real-time sharing of valid codes is not prevented. Lecturer interpretation remains unverified. |
| Q-02 | Does the lecturer accept the D-06 online list and XLSX snapshot as online/offline? Which fields and online corrections are needed? Separately, what does offline mean for comments? | AS-01, AS-02, D-06, P-03, P-04 | Attendance output format and no-back-sync behavior are decided; fields, corrections, lecturer interpretation, and the unrelated comments interpretation remain open. |
| Q-03 | Which poll language and input-length limit should be supported? | AS-03, D-08 through D-11, P-05 | These two parameters remain open. Poll types, four options, lecturer review/editing, voting, closure, visibility, exclusions, and failure/retry behavior are decided; shared identity, capacity, and AI-service constraints remain Q-06/Q-07. |
| Q-04 | Is an audio-based summary of a short uploaded video sufficient? Which language, duration, formats, and quality criteria apply? | AS-04, P-06 | User scope decision and any necessary lecturer clarification. |
| Q-05 | Which homework types, comparison population, review criteria, and depth are required? | AS-05, P-07, P-08 | User approval before fixing inputs, review behavior, and acceptance fixtures. |
| Q-06 | How many classroom users, devices, and simultaneous actions must be supported, and where must the demo be accessible? | AS-06, AS-07, P-01 | Actual class conditions, network availability, and measurable usability/capacity targets. |
| Q-07 | What identity, access, data-use, consent, retention, deletion, and AI-spending boundaries apply? | P-02, P-04, P-08, D-02 | User approval before external processing, paid use, or actual student-data use; no budget is assumed. |
| Q-08 | What are the exact deadline, submission format, templates, and assessment criteria? | AS-10 through AS-14 | User or lecturer information; do not invent submission rules. |
| Q-09 | Must every AI output finish live during the presentation, and what is the acceptable duration and quality of each result? | AS-09, D-01, P-09 | User decision plus later measured feasibility; disclose any approved use of earlier results. |
| Q-10 | Can the intended deployment reliably distinguish university-network requests from other traffic, and is that signal useful enough to adopt? | D-07, P-10 | Obtain network information, perform the proposed local review and campus observations below, document uncertainty, and seek a separate decision. No implementation requirement or successful experiment is assumed. |

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

## 7. Proposed University-Network Feasibility Study

**Status: proposed only; no network experiment, endpoint implementation, or
campus measurement has been performed.** This investigates P-10 and Q-10;
it is not an attendance prerequisite under D-05. The study is deferred and
does not block attendance, polling, or any other project work (D-07).

### Information needed

- Confirm what university network means: the classroom student Wi-Fi, all
  campus networks, or another defined network. Ask university IT for the
  relevant approved IPv4/IPv6 source ranges at the intended endpoint: public
  egress ranges for an externally hosted endpoint, or the appropriate internal
  ranges if the endpoint is on campus. Ask whether VPN access from outside
  campus can appear in those ranges. Do not infer an allowlist merely
  from university ownership of an address or from a single observed address.
- Identify the intended request path: direct access, hosting/reverse proxies,
  or another path. No hosting or framework choice is made here. Establish
  which component could reliably observe the client-side source address.
- Confirm access to the classroom network, suitable devices, an authorized
  observation endpoint or existing trusted request logs, and permission to
  record minimal test evidence. Agree what to do with unavailable or ambiguous
  evidence before considering a restriction.

### Local review, without campus access

Review a decision table using hypothetical in-range, out-of-range, boundary,
missing, malformed, IPv4, and IPv6 addresses. Include two distinct students
sharing an address; address equality must not be used as student identity or
as the attendance duplicate key. This can be reviewed manually now; executable
checks would belong to a later implementation stage.

Review any available deployment documentation for trusted proxies. A
client-supplied address or forwarding header must not be accepted as evidence
without a verified proxy trust boundary. Local examples cannot establish
the university's real egress ranges or connectivity. No such review result
or executable network check is claimed here.

### Short campus observation, proposed for later

After the required information and observation endpoint are available, target
about 20-30 minutes of observations, excluding setup and IT response time:

| Condition | Observation to collect | What it can establish |
|-----------|------------------------|-----------------------|
| Two devices on the intended classroom Wi-Fi | Reachability, timestamp, server-observed address/family, and any verified proxy path. Repeat after reconnecting. | Whether the intended path is reachable and observed addresses fit the supplied ranges; whether devices share an egress address. |
| A device on cellular data or another non-university connection | The same observations at the same endpoint. | Whether this tested outside connection differs; one sample does not establish every outside path. |
| An off-campus device using university VPN, if available and permitted | The same observations, noting VPN state. | Whether an off-campus user can appear to originate from the university network. If unavailable, retain this limitation explicitly. |

Use non-personal test labels and retain only the minimal observations needed;
do not collect passwords, tokens, or student homework. Record actual outcomes,
missing cases, and uncertainty, without marking untested cases as passed.
The result is a feasibility recommendation for a later decision, not proof of
physical classroom presence. Inconclusive evidence leaves P-10 conditional;
it does not silently add an IP restriction to attendance.

### Technical basis

Forwarded client addresses require a verified proxy trust boundary; the
header itself may be changed by a client or intermediary
([RFC 7239, Section 8.1](https://www.rfc-editor.org/rfc/rfc7239.html#section-8.1)).
Shared IP addresses do not uniquely identify a user
([RFC 6269, Section 13.2](https://www.rfc-editor.org/rfc/rfc6269.html#section-13.2)).
Whether campus routing or VPN behavior defeats a university-origin heuristic
is a hypothesis for this study, not an observed property of this university.
