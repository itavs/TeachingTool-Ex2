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
- **P-xx:** open proposals that require approval.
- **Q-xx:** unresolved questions.

Core requirements marked **Assignment requirement** describe stated capability
goals. Detailed candidate behavior marked **Open proposal** is conditional:
it does not become approved merely because it appears beside a requirement.
The same distinction applies to use cases and future acceptance criteria.

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

**Open proposal:** Under P-02, entering a meeting as an identified student would
create an attendance record with identity and arrival time. Repeated entry
would not create duplicate attendance rows. Neither the identity mechanism
nor this trigger is approved. Entry through a link does not demonstrate
physical presence in the room (Q-01).

### FR-02 - Attendance Spreadsheet

**Assignment requirement:** AS-01.

The lecturer shall receive an online/offline spreadsheet containing attendance
details. The precise interpretation of online/offline, required fields, and
file format are unresolved (Q-02).

**Open proposal:** P-03 would provide a live attendance table and a downloadable
spreadsheet containing name, identifier, and arrival time. Whether this meets
the stated spreadsheet requirement needs approval. It is not an approved
replacement for an editable online spreadsheet or another expected behavior.

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

**Open proposal:** Under P-05, a model would generate one single-choice question
and answer options from short pasted lesson text. The lecturer would review
or edit it before publication; students would submit one response each and
the lecturer would see response counts and their distribution. One active
poll at a time is proposed. Model-based generation, input limits, question
format, publication, vote changes, and result visibility require approval
(Q-03); the handout does not explicitly require an LLM for poll creation.

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

These are candidate workflows for review, not approval of their detailed
steps. Each depends on the cited proposals and unresolved questions.

### UC-01 - Attend a Meeting and Obtain Attendance Details

- **Actors:** Student and lecturer.
- **Trigger/preconditions:** The lecturer makes a meeting available; the student
  has an identity recognized by the yet-to-be-agreed identity mechanism.
- **Candidate steps:** The student enters the meeting; the system records
  attendance automatically; the lecturer views the table and downloads the
  attendance spreadsheet.
- **Expected outcome:** The lecturer receives details matching actual recorded
  attendance events. Under P-02, re-entry does not add another row.
- **Failure/alternative:** If identity or recording fails, the candidate behavior
  is to report the failure without claiming attendance was saved. Physical
  presence cannot be inferred from this workflow alone.
- **Dependencies:** FR-01, FR-02; P-02, P-03; Q-01, Q-02, Q-07.

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
- **Trigger/preconditions:** The lecturer has current learning material and
  requests a poll; the proposed generation method is approved and available.
- **Candidate steps:** The lecturer pastes text; generation produces a question
  and options; the lecturer reviews or edits them and publishes the poll;
  students respond; the lecturer views the distribution.
- **Expected outcome:** The generated poll concerns the supplied material and
  the displayed results match accepted responses.
- **Failure/alternative:** Failed generation does not publish a canned question
  as if generated. Missing material, invalid options, repeat responses, and
  submission after closure need explicit handling once rules are approved.
- **Dependencies:** FR-04; P-05; Q-03, Q-06, Q-07.

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
| NFR-04 | Open proposal: P-02 through P-08 | Distinguish pending, successful, partial, and failed operations; avoid duplicate records or false success after errors. | Exact retry, deduplication, persistence, and failure rules for each approved workflow. |
| NFR-05 | Open proposal: P-08; Q-07 | Enforce approved role/data boundaries and disclose what information is processed externally. | Identity, authorization, consent, retention/deletion, and actual student-data policy. No service or paid use is authorized here. |
| NFR-06 | Approved planning target D-01; assignment AS-09; open P-09 | Plan a roughly ten-minute demo with actual functioning capabilities; disclose sample inputs, earlier results, limitations, and failures. | Live-completion expectations, acceptable AI latency/quality, and any approved use of earlier outputs; Q-09. |

Short input samples and earlier processed results cannot by themselves prove
actual-class capacity or performance. No numeric concurrency, latency,
accuracy, or availability threshold has been approved or measured.

## 7. Future Acceptance Checks and Traceability

All checks below are **planned and not executed**. Proposed detailed criteria
remain conditional on approval of the associated P-xx items. The checks make
the intended evidence concrete without claiming the open interpretations meet
the lecturer's expectations.

| Check | Source | Requirement / use case | Planned evidence and expected result | Open dependencies |
|-------|--------|------------------------|--------------------------------------|-------------------|
| AC-01 | AS-01, D-01 | FR-01, FR-02; UC-01 | Use at least two distinguishable student identities and the approved attendance trigger. Compare recorded events with the lecturer output. If P-02/P-03 are approved, re-entry creates no duplicate row and the downloaded spreadsheet opens with the same records and agreed fields. | Q-01, Q-02; P-02, P-03. |
| AC-02 | AS-02, D-01 | FR-03; UC-02 | Submit a known comment while the lecturer view is open; confirm its content appears and remains accessible under the agreed retention rules. Separately exercise the approved offline meaning. Under P-04 this is later online submission, not a network-disconnected test. | Q-02, Q-06, Q-07; P-04. |
| AC-03 | AS-03, D-01 | FR-04; UC-03 | Generate a new poll from known current material and inspect relevance. If P-05 is approved, review/publish it, cast known votes, and check response counts/distribution and the agreed repeat-vote rule. Record a real generation failure as failure rather than inserting a canned result. | Q-03, Q-07; P-05. |
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

1. Attendance identity/trigger and physical-presence expectations (Q-01).
2. Offline meaning for comments and the exact attendance spreadsheet behavior
   independently (Q-02).
3. Poll inputs, generation, publication, and response rules (Q-03).
4. Video language, duration, format, summary quality, and audio-only boundary
   (Q-04).
5. Homework formats, scope/depth, comparison group, and review criteria (Q-05).
6. Classroom access, capacity, devices, network, and usability targets (Q-06).
7. Identity, access, consent, retention, external processing, and spending
   permission (Q-07).
8. Submission/deadline expectations and live-demo completion rules (Q-08, Q-09).

Resolving these questions may change candidate workflows and acceptance
criteria. Such changes require coordinated updates to the SoW, README, and
register; they must not be silently represented as already approved.
