# Software Requirements Specification

## Teaching Tool - Initial Draft

## 1. Purpose and Status

This document defines the intended behavior of a web-based classroom teaching
tool for Exercise 2. It supports scope decisions, later design, implementation,
and verification. It is a draft, not a fully approved requirements baseline.

The user approved planning for all five capabilities to operate genuinely in
the demo. This coverage target has not been confirmed with the lecturer as the
required implementation coverage. None of the capabilities or acceptance checks
below has been implemented or executed in this stage.

See the [project overview](../README.md), [draft SoW](SoW.md), and
[decisions and assumptions register](decisions-and-assumptions.md).

## 2. Sources and Interpretation

The register defines the source identifiers used here:

- **AS-xx:** assignment requirements or guidance from the two-page handout.
- **D-xx:** user-approved decisions.
- **P-xx:** proposals, including open items and explicitly marked historical
  items superseded or partly resolved by later decisions.
- **Q-xx:** unresolved questions.

Core requirements marked **Assignment requirement** describe stated capability
goals. Detailed candidate behavior marked **Open proposal** is conditional:
it does not become approved merely because it appears beside a requirement.
The same distinction applies to use cases and future acceptance criteria.
Attendance direction D-05 and D-06 is user-approved; its remaining details
and lecturer interpretation are unresolved. Approval is not evidence of
implementation. The university-network option in D-07 remains conditional.
Polling decisions D-08 through D-11 are also user-approved project choices,
not additional requirements stated by the lecturer. Poll language and the
input-length limit remain open (Q-03).

The handout does not prescribe a programming language. Python for the server
and AI processing is approved by the user (D-02); no conflicting language rule
was found in the handout. This is not separate lecturer confirmation.
Frameworks, AI providers, storage, hosting, and the web-interface solution
remain unselected. English project documents and Hebrew user-facing project
discussion follow D-03; the application's interface and processing languages
have not yet been selected.

## 3. Actors and System Boundary

| Actor | Intended responsibilities | Unresolved boundary |
|-------|---------------------------|---------------------|
| Student | Participate in attendance, send comments or suggestions, respond to polls, and obtain homework review. | Identity method, permissions, and peer-data visibility are open. |
| Lecturer | Obtain attendance records, read feedback, create polls, request video summaries, and review homework and comparisons. | Course administration, exact access rules, and review controls are open. |

AI processing supports application behavior; it is not an additional user role.
No integration with Moodle, Zoom, or the university personal-information
system is required by the handout (AS-08). This does not establish how source
recordings or other learning materials will enter the application.

One course, one lecturer, and one active meeting are proposed constraints
(P-01), not approved system limits. Actual class capacity and deployment
conditions remain unresolved (Q-06).

## 4. Functional Requirements

### FR-01 - Automatic Attendance

**Assignment requirement:** AS-01. **Planning coverage:** D-01.

The system shall support automatic student attendance recording for a class
meeting and make the recorded details available for the lecturer's attendance
output (FR-02).

**User-approved design direction:** D-05 replaces the meeting-entry trigger
previously proposed in P-02. The lecturer opens a meeting and a registration
window and displays a temporary QR in class. The QR changes during that window.
The student identifies themselves and scans the QR. The system validates
the code's validity and association with the meeting during the open window,
records attendance and time, and prevents duplicate attendance for the same
student and meeting. Meeting entry alone is not the selected trigger.

The identity method, window duration, rotation frequency, validity interval,
transition behavior between successive codes, and late-arrival handling
remain open (Q-01). No exact timings or grace period are assumed.

The mechanism does not conclusively prove physical presence and does not
prevent real-time sharing of a still-valid code. Lecturer acceptance of this
interpretation of automatically remains unverified. A university-network check
is not required by this direction; see D-07 and Section 6.1.

### FR-02 - Attendance Spreadsheet

**Assignment requirement:** AS-01.

The lecturer shall receive an online/offline spreadsheet containing attendance
details. Lecturer interpretation of online/offline remains unverified (Q-02).

**User-approved design direction:** D-06 resolves the output direction in
P-03: the lecturer views an online attendance list and can export it to XLSX.
The exported file reflects the list at export time. Later changes to the
online records do not update an earlier export; editing the file does not
synchronize changes back into the application.

Exact fields and any online correction behavior remain open. This output
decision does not imply disconnected attendance registration, and has not
been confirmed by the lecturer as satisfying online/offline.

### FR-03 - Student Comments and Suggestions

**Assignment requirement:** AS-02. **Planning coverage:** D-01.

Students shall be able to submit comments and suggestions in real time and
in the mode described by the handout as offline.

**Open proposal:** P-04 would retain meeting-related, identified submissions,
show new submissions to the lecturer without manual page refresh, and allow
later access and submission outside lesson time. Student-to-student visibility
is not proposed. This candidate still needs internet access; it does not
provide disconnected writing and later synchronization. The meaning of
offline must be resolved before the requirement can be baselined (Q-02).

### FR-04 - Automatic Poll Creation

**Assignment requirement:** AS-03. **Planning coverage:** D-01.

Lecturers shall be able to create simple polls automatically about the current
learning materials.

**User-approved design:** D-08 through D-11 resolve the earlier P-05 proposal.
The assignment does not explicitly require an LLM for polls or prescribe the
following types, lifecycle, or visibility rules. These are project decisions.

Before generation the lecturer selects one of two types and supplies pasted
learning text. A real model processes that material and proposes:

| Type | Generated draft | Student feedback after closure |
|------|-----------------|--------------------------------|
| Comprehension question | One question, four single-choice options, one correct option, and a short explanation. | Aggregate results, the lecturer-approved correct answer, and the short explanation. |
| Opinion poll | One question and four single-choice options, without a designated correct answer or correctness evaluation. | Aggregate results without correctness evaluation. |

The lecturer reviews and may edit all generated content before publication,
including the question, options, correct answer, and explanation where
applicable. Publication requires lecturer approval. Content is not editable
after publication.

For both types:

- Each identified student may submit one final, single-choice response per
  poll, with no changes after submission. The identity method remains Q-07.
- Only one poll may be active per meeting. Further polls can be created after
  the previous poll closes; closure is manual, with no automatic scheduling.
- During voting, the lecturer sees the respondent count and the distribution
  of accepted responses as counts and percentages.
- Students see aggregate results only after closure, without respondent
  identities. For comprehension questions, the correct answer and explanation
  are also withheld from student-facing content until closure. An opinion
  poll never has a correct-answer designation or correctness evaluation.
- The basic scope excludes grades, file uploads, and open-ended questions.
- Generation failure produces an error and a retry option; prepared content
  must not be presented as generated from the supplied material.

Poll language and the input-length limit are still open (Q-03). No provider
or framework is selected, and none of this behavior has been implemented
or verified.

### FR-05 - Class Video Summary

**Assignment requirement:** AS-04. **Planning coverage:** D-01.

The lecturer shall be able to obtain an ML-generated summary of a class video.

**Open proposal:** Under P-06, the lecturer would upload a one-to-two-minute
video in one agreed language. Actual processing would extract its audio,
transcribe the speech, and summarize that transcript into main topics,
concepts, and key points. A summary based only on speech can omit silent
slides, diagrams, or board content. Manual upload, short duration, supported
formats, language, and audio-based interpretation remain open (Q-04).

Uploading only a prepared transcript is not equivalent to this proposed
video-input workflow. A prewritten summary is not evidence of ML processing.
The proposed duration is not an approved exclusion of full-length recordings.

### FR-06 - Deep Homework Review

**Assignment requirement:** AS-05. **Planning coverage:** D-01.

Students and lecturers shall be able to obtain a deep LLM review of homework.

**Open proposal:** Under P-07, a lecturer would supply assignment instructions
and review criteria, and the model would inspect a submitted answer against
them. The review would identify strengths, gaps, and actionable improvements
with references to relevant parts of the answer. One assignment with about
three short text submissions of a few hundred words is proposed. Supported
homework types, depth, input limits, and quality criteria are unresolved
(Q-05). Numeric grades, plagiarism judgments, and execution of submitted code
are not proposed for the basic demo; those exclusions remain unapproved.

### FR-07 - Comparison with Other Homework

**Assignment requirement:** AS-05. **Planning coverage:** D-01.

The homework review shall include comparisons with other students' work.
Reviewing an answer in isolation does not meet this part of the requirement.

**Open proposal:** P-07 would compare actual submissions for the same assignment,
identifying differences in topic coverage, missing points, and approaches.
Under P-08, students would see their own review and anonymized comparisons,
while the lecturer would see all reviews. Comparison membership, access rules,
and data-use permission remain open (Q-05, Q-07). The system must not claim a
peer comparison has occurred when no peer submission has been processed;
the exact user-visible behavior for that case needs agreement.

## 5. Main Use Cases

UC-01 incorporates approved attendance direction D-05/D-06, and UC-03 follows
approved polling decisions D-08 through D-11, with remaining details explicit.
UC-02, UC-04, and UC-05 remain candidate workflows for review, not approval of
their detailed steps. Each use case identifies its decisions, proposals, and
unresolved questions.

### UC-01 - Scan a Rotating QR and Obtain Attendance Details

- **Actors:** Student and lecturer.
- **Trigger/preconditions:** The lecturer opens a meeting and a registration
  window and displays its rotating temporary QR. The student identifies
  themselves through a method that remains to be selected.
- **Approved direction:** The student scans the QR; the system checks validity,
  meeting association, and the open window, records attendance and time, and
  prevents duplicate attendance for that student and meeting. The lecturer
  views the online list and exports a point-in-time XLSX snapshot as needed.
- **Expected outcome:** One attendance record for the identified student and
  meeting, with the recorded time, reflected in the online list and any export
  taken after that record. File edits do not synchronize back.
- **Failure/alternative:** An invalid, expired, wrong-meeting code or a closed
  registration window must not create a successful registration through this
  path. Failed identification or recording must not be presented as saved.
  Code-transition timing and the separate treatment of late arrivals remain
  open. Valid-code sharing in real time is not prevented, and the flow does
  not conclusively prove physical presence.
- **Dependencies:** FR-01, FR-02; D-05, D-06; Q-01, Q-02, Q-07.
  P-02 and P-03 are historical references, not pending approval of this direction.
  D-07 does not add a university-network prerequisite.

### UC-02 - Send a Comment or Suggestion

- **Actors:** Student and lecturer.
- **Trigger/preconditions:** A student has a meeting-related comment or
  suggestion; access and visibility rules are resolved.
- **Candidate steps:** The student submits text; the application stores it;
  the lecturer's open view displays it without manual refresh. The student
  can submit or the lecturer can read later, outside lesson time.
- **Expected outcome:** The content is associated with the intended meeting
  and remains available according to the agreed retention policy.
- **Failure/alternative:** An unsuccessful save is not shown as completed.
  Network loss under P-04 does not establish offline support; a disconnected
  mode would require a separately approved workflow.
- **Dependencies:** FR-03; P-04; Q-02, Q-06, Q-07.

### UC-03 - Generate, Publish, and Answer a Poll

- **Actors:** Lecturer and students.
- **Trigger/preconditions:** The lecturer has learning text for a meeting and
  selects comprehension or opinion before requesting generation. A previous
  poll for that meeting is closed; for the first poll, none is active. Poll
  language and input limits still require a decision.
- **Approved steps:** The lecturer pastes the material; the model proposes a
  question and four options, plus one correct answer and short explanation
  only for comprehension. The lecturer reviews and can edit all applicable
  content, then approves publication. Identified students each submit one
  final choice. The lecturer sees updated respondent counts and distribution
  as counts and percentages during voting, and closes the poll manually.
- **Expected outcome:** Published content reflects the approved draft and
  becomes uneditable. Submitted choices cannot be changed; further responses
  are not accepted after closure. Students then see aggregate results without
  identities and, for comprehension only, the correct answer and explanation.
  No grades are assigned, and opinion responses are not evaluated for
  correctness. Another poll can be created for the meeting after closure.
- **Failure/alternative:** Generation failure displays an error with retry and
  never substitutes prepared content as if generated. Duplicate responses,
  attempts to change a submitted choice, post-publication content edits, and
  responses after closure must not change the accepted poll content or votes.
  Missing input, unusable model output, and shared identity/access details
  require validation during later design; no framework or provider is chosen.
- **Dependencies:** FR-04; D-08 through D-11; Q-03, Q-06, Q-07.
  P-05 is resolved proposal history, not pending approval of this workflow.

### UC-04 - Summarize a Recorded Class Segment

- **Actor:** Lecturer.
- **Trigger/preconditions:** An agreed video input is available and permitted
  for the selected processing path; the language and input limits are resolved.
- **Candidate steps:** The lecturer uploads the video and requests a summary;
  the system processes its audio, transcribes speech, generates a summary,
  and displays the resulting topics, concepts, and key points.
- **Expected outcome:** The result comes from actual processing of the uploaded
  recording; it is identified as audio-based if P-06 is approved.
- **Failure/alternative:** Unsupported input, absent intelligible speech, failed
  transcription, or failed summarization is reported without a false success.
  A previously processed result, if permitted for presentation, is labeled
  rather than attributed to the current request.
- **Dependencies:** FR-05; P-06, P-09; Q-04, Q-07, Q-09.

### UC-05 - Review Homework and Compare Submissions

- **Actors:** Student and lecturer.
- **Trigger/preconditions:** Assignment instructions, proposed review criteria,
  and permitted submissions for the same assignment are available; the agreed
  role is allowed to request the review and comparison.
- **Candidate steps:** The lecturer supplies instructions and criteria; students
  submit answers; a student requests review of their answer or the lecturer
  requests review of an answer; the LLM processes the answer and the actual
  peer comparison inputs; the requester receives the permitted review view.
- **Expected outcome:** Feedback addresses the actual answer and criteria,
  and comparison observations reflect the selected peer submissions. Under
  P-08, the student view does not disclose peer identities or full answers.
- **Failure/alternative:** Missing instructions, no peer submissions, invalid
  inputs, unavailable processing, or unauthorized access is made explicit;
  a partial review is not described as a completed peer comparison.
- **Dependencies:** FR-06, FR-07; P-07, P-08; Q-05, Q-07, Q-09.

## 6. Quality Requirements and Constraints

| ID | Status and source | Requirement or candidate target | Still to define |
|----|-------------------|---------------------------------|-----------------|
| NFR-01 | Assignment requirement: AS-07 | Provide a simple smartphone web application suitable for student participation. | Supported devices/browsers, interface language, and observable usability criteria; Q-06. |
| NFR-02 | Assignment requirement: AS-06 | Work in the actual class rather than only as a disconnected mockup. | Class size, concurrent activity, connectivity, deployment/access, and acceptable response times; Q-06. |
| NFR-03 | Assignment guidance AS-08; approved D-02 | Keep design implementable, consider reuse, and use Python as the main server/AI language. | Frameworks, providers, frontend, storage, hosting, and evidence from later real tool trials. No choices are made here. |
| NFR-04 | Approved attendance duplicate prevention D-05 and polling controls D-09/D-11; other error-handling details remain proposals under P-04 and P-06 through P-08 | Distinguish pending, successful, partial, and failed operations; avoid duplicate records or false success after errors. Attendance deduplication, final poll responses, and generation-error/retry behavior follow the approved decisions. | General persistence and failure rules still need refinement; attendance identity, timings, and late-arrival handling remain Q-01. No provider-specific retry policy is selected. |
| NFR-05 | Approved poll visibility D-10; other role/data boundaries remain open under P-08 and Q-07 | Students see poll aggregates only after closure without respondent identities; comprehension answers/explanations are withheld until closure. Enforce approved role/data boundaries and disclose what information is processed externally. | Identity, authorization, consent, retention/deletion, and actual student-data policy. No service or paid use is authorized here. |
| NFR-06 | Approved planning target D-01; assignment AS-09; open P-09 | Plan a roughly ten-minute demo with actual functioning capabilities; disclose sample inputs, earlier results, limitations, and failures. | Live-completion expectations, acceptable AI latency/quality, and any approved use of earlier outputs; Q-09. |

Short input samples and earlier processed results cannot by themselves prove
actual-class capacity or performance. No numeric concurrency, latency,
accuracy, or availability threshold has been approved or measured.

### 6.1. Conditional University-Network Option

D-07 and P-10 record an option to investigate university-network origin; this
is not an approved implementation requirement, additional attendance condition,
or claim of a completed experiment. Q-10 remains open. The proposed information
request, local decision-table review, and short campus observation are in
Section 7 of the [register](decisions-and-assumptions.md).

Even if feasible, network origin would not uniquely identify a student or
prove presence in a particular classroom. Unknown VPN and routing behavior
must be investigated rather than assumed. No network filtering behavior,
framework, or deployment solution is selected here. The study is deferred and
does not block any other project work.

## 7. Future Acceptance Checks and Traceability

All checks below are **planned and not executed**. AC-01 follows approved
attendance direction D-05/D-06, and AC-03 follows polling decisions D-08 through
D-11; their remaining unresolved parameters are explicit. Other proposed
detailed criteria remain conditional on approval of the associated P-xx items.
The checks make
the intended evidence concrete without claiming the open interpretations meet
the lecturer's expectations.

| Check | Source | Requirement / use case | Planned evidence and expected result | Open dependencies |
|-------|--------|------------------------|--------------------------------------|-------------------|
| AC-01 | AS-01, D-01, D-05, D-06 | FR-01, FR-02; UC-01 | After timing and identity details are agreed, use two identified students and a rotating temporary QR in an open meeting window. Check valid registrations and recorded times; reject an expired code, a wrong-meeting code, and normal registration after window closure. Verify the displayed QR changes and apply the agreed validity rule across rotation boundaries, without assuming an unapproved grace period. Repeated scans by the same student produce one record for that meeting; the second student's valid scan produces a separate record. Export XLSX, open it and compare it with the online list at export time. Add a later valid attendance record and confirm the earlier file remains a snapshot; editing a copy does not change online records. These checks do not establish physical presence or prevent real-time sharing of valid codes. | Q-01, Q-02, Q-07 for identity, timings, late arrivals, fields, and permissions; lecturer interpretation remains unverified. D-07 is not a required network gate. |
| AC-02 | AS-02, D-01 | FR-03; UC-02 | Submit a known comment while the lecturer view is open; confirm its content appears and remains accessible under the agreed retention rules. Separately exercise the approved offline meaning. Under P-04 this is later online submission, not a network-disconnected test. | Q-02, Q-06, Q-07; P-04. |
| AC-03 | AS-03, D-01, D-08 through D-11 | FR-04; UC-03 | Exercise both lecturer-selected types using real generation from known pasted material. Inspect relevance, four options, and, for comprehension, one correct option plus a short explanation. Edit all applicable draft fields and verify publication uses the approved version; reject later content edits. Cast known votes from two identified students and verify live lecturer counts/percentages, one final response each, no vote changes, and no second active poll in that meeting. Before closure, verify student-facing content exposes neither aggregates nor the comprehension answer/explanation. Close manually; reject later votes and show student aggregates without identities, plus the correct answer/explanation only for comprehension. Confirm opinion polls never designate or evaluate correctness and neither type assigns grades. Create a further poll after closure. Exercise generation failure and retry without a prepared-content substitution. Verify the basic flow has no file upload, open-ended response, or automatic scheduling. | Q-03 for poll language/input length; Q-06/Q-07 for capacity, identity, access, and AI constraints. Approved workflow is not conditional on P-05 approval. |
| AC-04 | AS-04, D-01 | FR-05; UC-04 | Process an actual video containing identifiable spoken facts. Inspect the produced transcript and summary against those facts using agreed quality criteria. Try a failed/unsupported input and verify no successful summary is claimed. Under P-06, disclose omission of unspoken visual content. | Q-04, Q-07, Q-09; P-06, P-09. |
| AC-05 | AS-05, D-01 | FR-06, FR-07; UC-05 | Supply answers with deliberately different coverage and known strengths/gaps. Inspect a real LLM review and cross-answer comparison against the answers and agreed criteria. Check the no-peer case and, if P-08 is approved, separate student and lecturer visibility. Do not require identical wording from repeated model outputs. | Q-05, Q-07, Q-09; P-07, P-08. |
| AC-06 | AS-06, AS-07 | NFR-01, NFR-02; UC-01 through UC-05 | Exercise the relevant student flows on the agreed smartphone/browser set and all flows in the intended classroom environment at the agreed load; record devices, network conditions, observed durations, and failures. | Q-06; P-01. |
| AC-07 | AS-09, D-01 | NFR-06; UC-01 through UC-05 | Rehearse the approximately ten-minute presentation and record what ran live, actual processing times, any earlier outputs, and any failures. Confirm all five capabilities have genuine execution evidence; label sample data and any separately approved presentation shortcuts. | Q-09; P-09. |

The later testing strategy must expand these checks into component and
integration cases, including checks for the classes identified in subsequent
design work (AS-13). These draft criteria are not a substitute for that strategy,
actual tool experiments (AS-11), or recorded test and demo outcomes (AS-14).

## 8. Baseline Decisions Still Needed

The register remains authoritative for open items. In particular, resolve:

1. Attendance identity method, registration-window and QR timings, code
   transitions, late-arrival handling, and lecturer acceptance of automatically
   (Q-01). The rotating-QR direction itself is approved (D-05).
2. Attendance export fields, any online correction behavior, and lecturer
   acceptance of online/offline, separately from offline comments (Q-02).
   Online list and XLSX snapshot without back-sync are approved (D-06).
3. Poll language and input-length limit (Q-03). Types, generation from pasted
   text, review/editing, publication, responses, manual closure, visibility,
   exclusions, and failure/retry behavior are approved (D-08 through D-11).
4. Video language, duration, format, summary quality, and audio-only boundary
   (Q-04).
5. Homework formats, scope/depth, comparison group, and review criteria (Q-05).
6. Classroom access, capacity, devices, network, and usability targets (Q-06).
7. Identity, access, consent, retention, external processing, and spending
   permission (Q-07).
8. Submission/deadline expectations and live-demo completion rules (Q-08, Q-09).
9. Feasibility and possible later adoption of a university-network-origin
   check (Q-10); it is conditional, not a requirement under D-07.

Resolving these questions may change candidate workflows and acceptance
criteria. Such changes require coordinated updates to the SoW, README, and
register; they must not be silently represented as already approved.
