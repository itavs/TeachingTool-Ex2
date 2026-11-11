# Software Requirements Specification

## Teaching Tool - Initial Draft

## 1. Purpose and Status

The user has sent the lecturer three interpretation questions: rotating-QR
attendance, online attendance list with XLSX snapshot, and speech-only video
summary. All three await replies; implemented behavior is not lecturer acceptance.
D-17 comments during/outside class is already resolved. See the
[clarification register](decisions-and-assumptions.md#lecturer-clarification-requests---sent-awaiting-reply).

This document defines the intended behavior of a web-based classroom teaching
tool for Exercise 2. It supports scope decisions, later design, implementation,
and verification. It is a draft, not a fully approved requirements baseline.

The website implements Django/Templates authentication and course-membership roles,
meeting management, attendance/QR/XLSX, connected comments during or outside class,
and the complete poll lifecycle. Local Qwen3 8B generates **English** editable poll
drafts; Hebrew editing/publication/voting remain supported, but Hebrew automatic
generation is unavailable. New MP4 jobs validate/extract audio, transcribe with the
pinned local large-v3-turbo CUDA checkpoint, then summarize with local Qwen3 8B.
A failed summary retains an available saved transcript; legacy completed jobs are
unchanged. Homework review/comparison has an approved **planning baseline** (D-46 through
D-52). The assignment/submission foundation is implemented under D-53;
AI feedback/comparison remains feasibility/planning only, not a website feature. Functional operation does not establish reliable AI accuracy,
phone usability, classroom capacity or a completed in-class demonstration.

The five-capability target is user-approved, not lecturer-confirmed. Full AC-01
through AC-07 acceptance is not established; see [test evidence](testing.md).

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
follow D-24/D-27 through D-29; lecturer interpretation remains pending. Approval is not evidence of
implementation. The university-network option in D-07 remains conditional.
Polling decisions D-08 through D-11 are also user-approved project choices,
not additional requirements stated by the lecturer. D-31 resolves Q-03: Hebrew/English with lecturer-selected output language and a 6,000-character material ceiling.
Video decisions D-12 through D-16 define unverified language, audio-processing,
input/output, terminology-test, and limit-setting targets. P-06 retains pending
real-model quality questions; D-34 now fixes initial numeric input limits, while its input/output choices remain approved.
D-18/D-19 approve the comments scope. D-17 now clarifies online/offline as during/outside class through the same connected website flow, retaining separate creation/submission/storage.
D-20 through D-22 approve the first-version homework scope. These are project
choices, not additional requirements explicitly prescribed by the handout.

The handout does not prescribe a programming language. Python for the server
and AI processing is approved by the user (D-02); no conflicting language rule
was found in the handout. This is not separate lecturer confirmation.
D-23/D-26 select Django/Templates and SQLite for initial development.
Local turbo/Qwen adapters serve video and English polls; homework engine selection, hosting and classroom readiness remain open. English project documents and Hebrew user-facing project
discussion follow D-03. Video-summary language targets follow D-12: Hebrew
and English, with output in the recording's spoken language and no translation.
Hebrew lectures with English technical terms are included in planned checks;
sustained language switching is outside the current commitment (D-15).
Homework pasted-input targets are also Hebrew and English (D-20), without
claiming tested support. Application-interface language remains open; D-50 fixes feedback language per assignment, with real-output language availability unaccepted. Poll output language is lecturer-selected Hebrew/English under D-31; tested fixtures do not establish real-model language quality.

## 3. Actors and System Boundary

| Actor | Intended responsibilities | Unresolved boundary |
|-------|---------------------------|---------------------|
| Student | Participate in attendance, send meeting comments/suggestions, respond to polls, and request/view review of their own homework. | Visibility follows D-10/D-18/D-21; initial identity/access follows D-24; feature-specific checks, resources and operational parameters remain open. |
| Lecturer | Obtain attendance, view all meeting requests, create polls, request video summaries, and request review of any assignment submission while viewing all submissions/feedback. | Course/membership data is prepared under D-25; current website features enforce course access; homework review operations remain open; approved visibility/request rights are not reopened. |

AI processing supports application behavior; it is not an additional user role.
No integration with Moodle, Zoom, or the university personal-information
system is required by the handout (AS-08). This does not establish how source
recordings or other learning materials will enter the application.

P-01 is historical simplification advice, not a system limit: the implemented
foundation supports multiple courses, memberships and meetings. Actual class capacity and deployment
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

Identity follows D-24. D-27 fixes the initial window at 5 minutes, rotation at 30 seconds and validity at 45 seconds (15 seconds overlap, bounded by closure). Later windows last 2 minutes; closing invalidates all their codes. D-28 requires login continuation with fresh validation, and registration by CSRF-protected POST only. Preserve the first registration without duplicates; label a first registration in a later window Registered in an additional window, never Late.

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

D-29 fixes roster/export fields: username, display name, course code/title, meeting title/time, registration status and first-registration time (Asia/Jerusalem). Include current student memberships, using Not registered without declaring absence. Export metadata records snapshot time. No manual correction is included. This output
decision does not imply disconnected attendance registration, and has not
been confirmed by the lecturer as satisfying online/offline.

### FR-03 - Student Comments and Suggestions

**Assignment requirement:** AS-02. **Planning coverage:** D-01.

Students shall be able to submit comments and suggestions in real time and
in the mode described by the handout as offline.

**Clarified interpretation (D-17, user report on 2026-11-11):** online means during class and offline means outside class. Both use normal website submission by an identified student to an associated meeting. A past meeting remains eligible, independently of attendance windows or whether the lecturer is currently signed in. No local storage, send queue or disconnected synchronization is required.

Keep creation, submission and storage separate:

| Responsibility | Meaning in the design | What it does not establish |
|----------------|-----------------------|----------------------------|
| Create | Compose a comment or suggestion before submission. | Creation alone is not submission or confirmed storage, and does not imply a persistent local draft. |
| Submit | Request delivery of the created content for acceptance by the system. | A submission attempt is not confirmed storage; no automatic send queue or later replay is approved. |
| Store | Record accepted requests and provide history under D-18; retention/deletion parameters remain to be decided. | No local persistence or disconnected synchronization mechanism is selected or approved. |

D-17 requires no disconnected functionality. Outside-class requests use the same server-side persistence and private history as during-class requests; the lecturer can read them on a later login.

**User-approved connected scope (D-18/D-19):** identified students create
requests of type comment or suggestion associated with a meeting. Students
see only their own requests; the lecturer sees all requests for that meeting.
Requests are stored with history, and new requests appear to the lecturer
without manual refresh. The first version excludes lecturer replies,
discussion threads, attachments, votes, and notifications.

Initial identity follows D-24. D-30 fixes trimmed request length at 1–1000 Unicode code points and lecturer refresh at 5 seconds while visible. No editing/deletion UI is included. Retention/deletion policy and classroom capacity remain open. D-17 resolves both timing modes through connected submission and stored history. P-04 records this scope; comments timing is no longer an open part of Q-02.

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
  poll, with no changes after submission. The initial identity method is D-24; later feature permissions still need checks.
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

D-31 sets the approved Hebrew/English output target and 6,000-character material
limit. Current generation uses local Qwen3 8B in English only (D-44/D-45), with
validated editable drafts and separate Lecturer publication. Hebrew lifecycle
support remains, but automatic Hebrew generation is unavailable. D-32 is the
historical disabled-provider stage; test fakes and D-33 labeled demo data are
separate paths. Real English samples do not establish broad semantic quality or
full AS-03/AC-03 acceptance; see local-poll-generation.md and testing.md.

### FR-05 - Class Video Summary

**Assignment requirement:** AS-04. **Planning coverage:** D-01.

The lecturer shall be able to obtain an ML-generated summary of a class video.

**User-approved design direction:** D-12 targets Hebrew and English recordings,
with the summary in the spoken language of the recording and no translation
in the first version. Both languages have been exercised locally; reliable accuracy in both has not
been established, and the uploaded STATIC summary failed language validation. Under D-15, planned verification also
includes a Hebrew lecture with English technical terms; its summary remains
in Hebrew without a translation stage. Sustained switching between languages
is outside the current commitment. No automatic rejection/detection policy
or numeric switching threshold is assumed.

D-13 requires actual audio extraction from the video, speech transcription,
and model-based summarization of that transcript. Analysis is audio-only.
The result must clearly explain that visual information not spoken in the
recording is not included in the analysis. Silent slides, formulas, diagrams,
and board content are therefore not analyzed; speech-recognition errors can
affect the summary. Lecturer acceptance of this interpretation remains
unconfirmed; the handout does not explicitly prescribe an audio-only approach.

**User-approved input/output (D-14):** the lecturer manually uploads a video
file from the computer. MP4 is the initial supported format. The result
includes a summary paragraph and 3-5 key points, with an option to view the
full transcript. Other input formats, link import, and transcript editing or
export are not established by this decision. Unit D now implements MP4 validation/audio extraction; Unit E adds local Hebrew/English detection and full-transcript display; local summaries are implemented under D-42/D-43, with source accuracy and broad quality still unaccepted.

D-34 approves initial limits of 240 seconds and 200,000,000 bytes, enforced server-side. D-35 limits worker processing to 600 seconds from claim, excluding queue wait. These limits follow the earlier D-16 measurement-first policy; demo duration remains separate and undecided. This does not establish full-lesson support or real AI quality. See video-processing.md and the decisions register.

Providing only a prepared transcript is not equivalent to the approved
video-to-audio-to-summary processing direction. A prewritten summary does
not demonstrate model processing of the supplied video.

### FR-06 - Deep Homework Review

**Assignment requirement:** AS-05 requires deep LLM review for Students and
Lecturers. **Approved project design:** D-20/D-22 and D-46 through D-51.

A theoretical assignment accepts pasted Hebrew/English text and has Lecturer
instructions, criteria and an assignment-level feedback language. A Student may
request review of their own version; a Lecturer may request review of a submission
in their course. Model output is an unpublished Lecturer draft: identify what the
Student wrote for each criterion, quote the target where relevant, distinguish
correct/partial/missing/incorrect coverage, and explain strengths, actual errors
and actionable recommendations. Exact quotes must be checked against the right
source version; their presence does not certify the conclusion.

Only a separate Lecturer review/edit/publication action makes feedback visible
to its owner. Generated content and edited/published content remain distinguishable.
Resubmission creates an immutable version; older feedback stays bound to its
original version. Snapshot instructions, criteria, requested language and source
versions at request creation. Never silently treat old feedback as feedback for
new text. Source/rubric changes and stale edits must be detected before publication.

The **assignment/submission foundation is implemented** (D-53): meeting-linked
assignment creation, instructions/criteria, exact-text versions and authorized
reading. Review/comparison/publication below remain **planned**, not website features. Hebrew and English remain quality-test
targets: a language becomes available only after actual output for this workflow
has been reviewed successfully. Existing failed trials do not enable either.
Length/workload and processing bounds require measurement, not a cap inferred
from three demo works. No grades, plagiarism determinations or code execution.
Only synthetic works are approved for the demo. Keep versions/feedback through
the demo and submission checking, then provide intentional cleanup; do not reuse
the video's seven-day policy. Real student-work policy is separate.

### FR-07 - Comparison with Other Homework

**Assignment requirement:** AS-05 includes comparison with other Students' work.
**Approved design:** D-21 and D-47 through D-49. An isolated review is insufficient.

At request creation select the latest submitted version of each **other owner**
in the same assignment. Exclude all versions of the target owner even when the
requester is a Lecturer. Persist the exact selected IDs plus instructions/criteria
snapshots; later resubmissions do not mutate this job's sources. Actual peer texts
must be processed. Output addresses topic coverage and solution approaches, not
ranking or majority-as-correctness. Student presentation contains no peer identities,
stable identifying labels or full peer works. Lecturer access may include the
source evidence needed to check the draft. Internal peer IDs are not Student output.

| Planned comparison outcome | Required behavior |
|---|---|
| No eligible other submissions | System derives this from the saved empty set and adds a clear no-other-submissions notice. Personal feedback may be reviewed/published; no comparison is claimed. |
| Eligible peers, comparison failed | Show a separate failed-comparison state/reason and retain any completed personal draft. Do not label it no peers, completed comparison or no supported difference. D-52 permits publication of successful personal feedback only after explicit Lecturer review and individual-only publication, with the required failed-comparison notice. A failed personal stage has no draft to publish. |
| Actual comparison, no supported difference | Explicitly say no supported difference was found in the processed snapshot. This is a substantive result requiring source review, not a fallback for errors or empty inputs. |
| Actual comparison with supported differences | Describe concrete coverage/approach differences grounded in the selected works, with private evidence for Lecturer review and an anonymous Student-facing account. |

The UI/publication gate must distinguish these outcomes. Similarity is not a
plagiarism judgment. Comparison quality and privacy remain unverified; no new
comparison experiment or implementation is claimed by this planning baseline.

## 5. Main Use Cases

UC-01 incorporates approved attendance direction D-05/D-06, and UC-03 follows
approved polling decisions D-08 through D-11, with remaining details explicit.
UC-04 incorporates video decisions D-12 through D-16 while retaining pending
numeric limits and quality criteria. UC-02 follows D-18/D-19 while preserving
the resolved D-17 during/outside-class interpretation; UC-05 follows D-20 through D-22 and the approved planning baseline D-46 through D-51.
Each use case retains its unresolved parameters and distinguishes approved
direction from implementation or completed checks.

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
- **Trigger/preconditions:** An identified student has a comment or suggestion
  for a meeting. The shared website identity mechanism is implemented under D-24.
- **Approved steps:** Create the typed request, submit it, and store accepted
  content as distinct responsibilities. The student sees their own requests
  and history; the lecturer sees all meeting requests, with new ones appearing
  without manual refresh. Accepted requests persist in SQLite through MeetingRequest;
  the comments retention/deletion duration remains open.
- **Expected outcome:** A successfully stored request is available in the
  permitted history views. Students cannot see another student's requests.
  Lecturer replies, threads, attachments, votes, and notifications are excluded.
  Under D-17 this applies during or outside class, including a past meeting, with later lecturer access to stored requests.
- **Failure/alternative:** An unsuccessful or uncertain submission/save must
  not be described as confirmed storage. Recovery behavior is undecided;
  no persistent local draft, automatic queue, disconnected synchronization,
  or automatic replay is required. Outside-class connected submission is an approved D-17 acceptance case.
- **Dependencies:** FR-03; D-17 through D-19; P-04 history and Q-06/Q-07 for capacity and operational/data policy; D-17 resolves comments timing.

### UC-03 - Generate, Publish, and Answer a Poll

- **Actors/preconditions:** A current course Lecturer selects comprehension or
  opinion and pastes 1-6,000 Unicode characters. The approved language target is
  Hebrew/English; current automatic generation is **English only** (D-44).
  Existing Hebrew drafts remain editable, publishable and answerable. The
  single-active-poll check applies to publication, not model execution.
- **Current steps:** The CSRF POST calls `create_generated_draft` and the local
  `PollGenerator` adapter outside a database transaction. Validate the question,
  four distinct options and type-specific fields; recheck membership before
  saving an unpublished draft. Comprehension includes one answer index and an
  explanation; opinion has neither. The Lecturer reviews meaning, edits/saves,
  then separately publishes. Students cannot access drafts.
- **Participation/result:** One final vote per Student; Lecturer counts and
  percentages during voting; manual close; Student aggregates only afterward.
  Correct answer/explanation are withheld from Student HTML/JSON until closure
  for comprehension, and never exist for opinion. No grades/respondent identities.
  Published content cannot be edited or reopened. Another poll may be published
  after closing the active one.
- **Failures:** Unavailable/busy/timed-out/invalid generation retains the material
  in the form and saves no prepared fallback. Hebrew generation explains the
  English-only restriction before inference. Explicit retry is a user action,
  not an automatic loop. Rejected stale edit/publication, duplicate vote or a
  race with close leaves accepted data consistent. Structural checks cannot
  certify correctness or that an opinion question truly asks for a preference.
- **Evidence/dependencies:** FR-04, D-08 through D-11, D-31/D-44;
  [real-model checks](local-poll-generation.md#actual-local-validation-on-a-new-topic),
  [software strategy](testing.md#current-component-to-test-strategy). Q-03 parameters
  are resolved; Hebrew generation quality, broader quality and classroom Q-06
  remain unaccepted. P-05 is proposal history.

### UC-04 - Summarize the Speech in a Class Video

- **Actor/preconditions:** The uploader is a current Lecturer in the meeting's
  course. Manually provide a permitted MP4 with video and audio, at most
  **240 seconds and 200,000,000 bytes**, enforced by the server. Hebrew/English
  speech and Hebrew with English technical terms are intended; sustained
  language switching is outside the commitment.
- **Current processing:** Persist the private upload and queued `VideoJob`;
  a separate single worker claims it, validates/decodes media, extracts WAV and
  runs pinned local large-v3-turbo CUDA transcription. Remove WAV and persist
  transcript, timed segments, detected language, actual model metadata and
  seven-day expiry before calling local Qwen3 8B for a short paragraph and 3-5
  points in the detected recording language. There is no translation or visual
  content analysis. The website remains usable while the job runs.
- **Progress/result:** Show actual stage, separate queue/processing elapsed
  times, automatic-result warnings and an owner-only full-transcript link.
  One 600-second budget starts when the worker claims the job and includes
  decoding, loading, transcription and summarization; it excludes queue wait.
- **Partial failure:** If summarization fails after transcript persistence,
  show the failed stage/reason and retain the full transcript for authorized
  access until expiry. Do not display a rejected summary or claim summary
  success. Transcription failure has no completed transcript to expose. Stopped
  workers/deadlines are recovered explicitly; there is no silent model fallback.
- **Access/retention:** Require uploader identity and current course Lecturer
  membership on direct task/transcript URLs. Transcript expires seven days
  after creation; summary never outlives it. Direct access is blocked at expiry,
  and maintenance clears content. Uploaded MP4 expires within 24 hours while
  maintenance operates; physical deletion cannot run on a powered-off machine.
  Old extraction/transcription-only jobs keep their original outcomes.
- **Evidence/dependencies:** FR-05, D-12 through D-16 and D-34 through D-43;
  [sequence](architecture.md#video-sequence), [actual results](local-summaries.md#actual-full-route-acceptance).
  Functional success is not speech-reference accuracy: Hebrew wording/negation
  and summary grounding remain limited. Separate demo duration, acceptable
  quality, audio-only lecturer interpretation and live-demo expectations remain
  Q-04/Q-09. Transcript editing/export and link import are not approved.

### UC-05 - Submit Homework, Review a Draft, and Publish Feedback

**Status:** user-approved planning baseline D-46 through D-52; assignment/submission components are implemented under D-53, while all review/
comparison/publication components are planned and model conclusion quality remains open.

1. A course Lecturer defines an assignment under a meeting, with instructions,
   criteria and requested Hebrew/English feedback language. Generation is enabled
   only for a language with recorded successful real-output review; neither is
   currently accepted for this planned workflow. Current creation implements
   title/instructions/criteria only; feedback-language configuration is deferred.
2. A Student pastes a synthetic work and submits it as a new immutable version.
   This is implemented: show save confirmation, numbered history and Submitted
   status, not a pending/generated review claim. Steps 3-8 remain planned.
3. The owner requests review, or the course Lecturer requests review for that
   version. Check current membership/role and target ownership. Atomically save
   target/version, instructions/criteria/language and latest-other-owner peer
   selection as a stable request snapshot. A Lecturer's own identity must not
   replace the target owner's identity in the exclusion rule.
4. A proposed background worker evaluates the target by criterion first, verifies
   quote presence, then compares actual eligible peer texts when present. Preserve
   real failures, original generated output, model identity and processing evidence.
   Do not feed the independent test coverage map to the model.
5. The Lecturer opens a private draft with target evidence, explanations,
   recommendations and comparison evidence. Edit findings and anonymous comparison,
   reviewing both meaning and privacy. Exact quoting/structural checks cannot
   establish correctness. Students cannot read drafts in HTML, lists or JSON.
6. A separate CSRF-protected Publish action rechecks current Lecturer membership,
   draft version and source/rubric status. It publishes an immutable feedback
   revision associated with the assessed version, without silently relabeling an
   older draft as current. A fresh version needs its own feedback/publication.
7. The Student sees only their own published feedback and anonymous comparison,
   with version attribution. The Lecturer sees course submissions/feedback.
   No-peer personal publication includes a system-generated notice. Comparison
   failure and completed/no-supported-difference are separate states (FR-07).
8. Retain synthetic versions/feedback through the demo and submission checking;
   afterward offer intentional cleanup. No timed seven-day homework deletion or
   real-student-work policy is approved.

**Alternatives/failures:** An unavailable model, invalid evidence/output,
permission revocation or worker failure must not become published feedback.
Preserve submitted versions and report the affected stage. When peers exist but
comparison fails, keep that failure visible separately from any personal draft;
D-52 permits explicit Lecturer publication of successful personal feedback only,
with comparison status still failed and the notice below. A failed personal stage
has no publishable draft.
Later peer submissions do not silently update an already generated/published
comparison. No grades, attachments, plagiarism determinations or code execution.

**Partial publication and later comparison (D-52):** Before publication the
successful personal draft remains Lecturer-private despite comparison failure.
The Lecturer reviews it and explicitly chooses individual-only publication. The
Student then sees that published personal feedback with comparison status failed
and this exact system-controlled notice:

> Your lecturer published your individual feedback. The comparison with other submissions could not be completed.

If the personal stage itself fails, no draft or publication action is available.
A later successful comparison is stored as a new unpublished feedback revision,
linked to the assessed submission version and its own recorded peer sources. The
currently published personal feedback/failure notice remains until the Lecturer
reviews and explicitly publishes the new revision. Publication then exposes the
reviewed comparison outcome, without silently rewriting earlier publication history.

**Traceability:** FR-06/FR-07, D-20 through D-22, D-46 through D-52;
[planned components/diagrams](architecture.md#planned-uc-05-components),
[planned acceptance strategy](testing.md#planned-uc-05-acceptance-strategy).
Q-05/Q-07/Q-09 retain quality/measurement, real-data and demo
questions; peer selection/revisions/language placement/demo retention are decided.

## 6. Quality Requirements and Constraints

| ID | Status and source | Requirement or candidate target | Still to define |
|----|-------------------|---------------------------------|-----------------|
| NFR-01 | Assignment requirement: AS-07 | Provide a simple smartphone web application suitable for student participation. | Supported devices/browsers, interface language, and observable usability criteria; Q-06. |
| NFR-02 | Assignment requirement: AS-06 | Work in the actual class rather than only as a disconnected mockup. | Class size, concurrent activity, connectivity, deployment/access, and acceptable response times; Q-06. |
| NFR-03 | Assignment guidance AS-08; approved D-02 | Keep design implementable, consider reuse, and use Python as the main server/AI language. | Django/Templates and development SQLite follow D-23/D-26; Local video/English-poll adapters are selected; homework AI, production hosting and classroom suitability remain open. |
| NFR-04 | Approved attendance/poll controls D-05/D-09/D-11, separate comments stages D-17/D-18, and truthful no-peer behavior D-21 | Distinguish pending, successful, partial, and failed operations; avoid duplicate records or false success after errors. Attendance deduplication, final poll responses, and poll generation-error/retry behavior follow approved decisions. Creation/submission is not confirmed storage; individual homework feedback is not peer comparison. | Detailed persistence/recovery policies remain open. Attendance timing and additional-window behavior follow D-27/D-28; current local video/poll adapters have no automatic generation retry; broader recovery policies remain open. |
| NFR-05 | Approved visibility D-10/D-18/D-21 and sample-only homework demo D-22; enforcement/lifecycle remain Q-07 | Preserve poll disclosure rules, student-own comments, lecturer-meeting comments, student-own homework feedback/comparison without peer identities/full works, and lecturer access to all assignment submissions/feedback. Disclose external data processing. | Initial identity/access follows D-24; consent, retention/deletion, production safeguards and permitted integrated AI processing remain open. No external service, paid use, or real-homework demo data is authorized by visibility approval. |
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

The table describes acceptance targets, not a blanket pass. Unit B server checks cover parts of AC-01/AC-02; executed evidence and browser/phone gaps are recorded separately in testing.md. AC-01 follows attendance
D-05/D-06, AC-02 follows connected comments D-18/D-19 with the D-17 separation
and clarified during/outside-class timing, AC-03 follows polls D-08 through D-11, AC-04 follows video
D-12 through D-16, and AC-05 follows homework D-20 through D-22. Remaining
parameters are explicit. AC-02 includes outside-class connected submission under D-17. The table is not evidence of a completed test or confirmation of unrelated unresolved assignment interpretations.

| Check | Source | Requirement / use case | Planned evidence and expected result | Open dependencies |
|-------|--------|------------------------|--------------------------------------|-------------------|
| AC-01 | AS-01, D-01, D-05, D-06 | FR-01, FR-02; UC-01 | Using D-24 and D-27 through D-29, use two identified students and a rotating temporary QR in an open meeting window. Check valid registrations and recorded times; reject an expired code, a wrong-meeting code, and normal registration after window closure. Verify the displayed QR changes and apply the agreed validity rule across rotation boundaries, without assuming an unapproved grace period. Repeated scans by the same student produce one record for that meeting; the second student's valid scan produces a separate record. Export XLSX, open it and compare it with the online list at export time. Add a later valid attendance record and confirm the earlier file remains a snapshot; editing a copy does not change online records. These checks do not establish physical presence or prevent real-time sharing of valid codes. | D-27 through D-29 fix identity continuation, timings, additional windows, fields and no manual correction. Q-01/Q-02 lecturer interpretation and Q-07 production safeguards remain open. D-07 is not a required network gate. |
| AC-02 | AS-02, D-01, D-17 through D-19 | FR-03; UC-02 | Submit identified comment and suggestion samples through normal website POST during and outside class, including a meeting dated in the past. Verify the selected meeting and submitting student are persisted, personal history survives a fresh login, and a lecturer signing in later sees the stored requests in that meeting. Another student must not see them through the meeting page or access the lecturer feed. Retain checks for failed-save reporting, boundaries, duplicate submission, escaping and live lecturer updates. No local persistence, queues or disconnected synchronization is required. | D-17 resolves timing. D-30 fixes request length and visible-page refresh. Executed server evidence is in testing.md; browser/phone/classroom capacity and retention remain separate questions under Q-06/Q-07. |
| AC-03 | AS-03, D-01, D-08 through D-11 | FR-04; UC-03 | Exercise both lecturer-selected types using real generation from known pasted material. Inspect relevance, four options, and, for comprehension, one correct option plus a short explanation. Edit all applicable draft fields and verify publication uses the approved version; reject later content edits. Cast known votes from two identified students and verify live lecturer counts/percentages, one final response each, no vote changes, and no second active poll in that meeting. Before closure, verify student-facing content exposes neither aggregates nor the comprehension answer/explanation. Close manually; reject later votes and show student aggregates without identities, plus the correct answer/explanation only for comprehension. Confirm opinion polls never designate or evaluate correctness and neither type assigns grades. Create a further poll after closure. Exercise generation failure and retry without a prepared-content substitution. Verify the basic flow has no file upload, open-ended response, or automatic scheduling. | D-31 resolves poll language/input length. Lifecycle evidence uses test fixtures and explicitly labeled demo data under D-32/D-33, not real generation. Q-06/Q-07 retain capacity and integrated-AI/data questions. Approved workflow is not conditional on P-05 approval. |
| AC-04 | AS-04, D-01, D-12 through D-16 | FR-05; UC-04 | Manually upload permitted MP4 files for three planned cases: Hebrew speech, English speech, and a Hebrew lecture with English technical terms. Using agreed quality criteria, verify genuine audio extraction/transcription/model summarization, inspect known spoken facts and the intended meaning of technical terms, and confirm output is in the spoken language without translation (Hebrew for the terminology case). Verify a summary paragraph, 3-5 key points, and an option that exposes the full transcript rather than a partial excerpt. Compare the transcript and summary with the actual speech. Check each result clearly states that unspoken visual content is excluded. Check the candidate failed/unsupported-input path without false success after its details are agreed. Measure time and cost for samples of different durations/file sizes before proposing maximum duration and file size; choose demo duration separately. After numeric limits are agreed and implemented, add boundary checks at and above each limit without inventing thresholds now. | D-34 through D-37 cover initial limits and extraction infrastructure; Q-04 retains demo duration, real-model quality and lecturer interpretation; Q-07/Q-09 for resources and demo expectations. All three language cases are planned, not passed; sustained language switching is outside the commitment. Extraction-only measurements/limits are recorded separately; no end-to-end AI quality pass is assumed. |
| AC-05 | AS-05, D-01, D-20 through D-22, D-46 through D-52 | FR-06, FR-07; UC-05 | Planned software and actual-model quality checks are separated in the UC-05 strategy. Verify owner/Lecturer requests, private drafts and separate publication; latest-other-owner snapshots including Lecturer initiation; immutable revisions; no-peers versus comparison failure versus no supported difference; system-controlled no-peer notice. For successful personal feedback plus failed comparison, assert private draft before explicit Lecturer individual-only publication and own published feedback plus the exact failed-comparison notice afterward. Personal failure yields no publishable draft. A later comparison stays hidden until separately reviewed/published. Assess real conclusions against source/criteria, A capacity coverage, B rollback and cache-only controlled correction, C actual gaps, and a grounded coverage/approach difference. | D-53 assignment/submission/read checks have software evidence in testing.md; AI review/comparison/publication and full AC-05 remain pending. Q-05 retains quality/language readiness, measured limits; D-52 resolves failure-publication; Q-07 real-data policy; Q-09 live demo. No existing trial constitutes a pass. |
| AC-06 | AS-06, AS-07 | NFR-01, NFR-02; UC-01 through UC-05 | Exercise the relevant student flows on the agreed smartphone/browser set and all flows in the intended classroom environment at the agreed load; record devices, network conditions, observed durations, and failures. | Q-06; P-01. |
| AC-07 | AS-09, D-01 | NFR-06; UC-01 through UC-05 | Rehearse the approximately ten-minute presentation and record what ran live, actual processing times, any earlier outputs, and any failures. Confirm all five capabilities have genuine execution evidence; label sample data and any separately approved presentation shortcuts. | Q-09; P-09. |

The [current testing strategy](testing.md#current-component-to-test-strategy) maps
these checks to actual components/classes and unit/integration evidence (AS-13). These draft criteria are not a substitute for that strategy,
actual tool experiments (AS-11), or recorded test and demo outcomes (AS-14).

## 8. Baseline Decisions Still Needed

The register remains authoritative for open items. In particular, resolve:

1. Lecturer acceptance of automatically (Q-01); D-24 and D-27/D-28 now resolve initial identity, timings, code transitions and additional-window registration.
2. Lecturer acceptance of the attendance online/offline interpretation (Q-02) remains open; D-06 approves the list/XLSX snapshot. Comments timing is separately resolved by D-17: online means during class and offline outside class, using the same website submission/history flow. Creation, submission and storage remain separate. D-18/D-19/D-30 scope and defaults are unchanged; capacity/data lifecycle remain Q-06/Q-07.
3. Local English poll generation is implemented under D-44. Hebrew automatic generation and broad semantic/language acceptance remain open. Q-03 parameters are resolved; D-32 is historical disabled-provider behavior and D-33 remains a separate labeled demo path. No external-provider approval or paid fallback is implied.
4. Separate video demo duration, real-model quality,
   and lecturer interpretation (Q-04). Manual MP4 upload, a summary paragraph
   with 3-5 key points and full-transcript viewing, Hebrew/English targets
   including Hebrew with English technical terms, same-language output without
   translation, and audio-only processing/disclosure are approved (D-12 through
   D-16). Sustained language switching is outside the commitment. D-34 through D-43 fix current limits, worker/privacy/retention and local video engines; disabled engines describe the historical infrastructure stage.
5. Homework numeric/runtime limits, per-language quality readiness and
   processing/retry controls (Q-05); D-52 resolves personal-only publication after
   comparison failure and explicit publication of a later comparison. Theoretical
   Hebrew/English pasted work, lecturer criteria, review/comparison behavior,
   visibility, no-peer handling, exclusions, and sample-only demo are approved
   (D-20 through D-22). D-46 through D-51 additionally resolve Lecturer publication,
   peer/version snapshots, assignment language and synthetic retention/cleanup;
   sample count does not define a system cap.
6. Classroom access, capacity, devices, network, and usability targets (Q-06).
7. Production access safeguards, consent, retention, external processing, and spending
   permission (Q-07).
8. Submission/deadline expectations and live-demo completion rules (Q-08, Q-09).
9. Feasibility and possible later adoption of a university-network-origin
   check (Q-10); it is conditional, not a requirement under D-07.

Resolving these questions may change candidate workflows and acceptance
criteria. Such changes require coordinated updates to the SoW, README, and
register; they must not be silently represented as already approved.

For the recommended distinction between decisions needed before fixing
affected technical choices and details that can be settled later, see
Section 9 of the [register](decisions-and-assumptions.md). This readiness
classification does not select a framework or approve new scope.

## 9. Shared Foundation — Unit A

**User-approved project decisions:** D-23 through D-26, not additional handout
requirements. This infrastructure supports future feature flows without
claiming they have been implemented.

| ID | Implemented behavior | Verification |
|---|---|---|
| FND-01 | Individual username/password login and POST logout using Django sessions; credentials are stored as hashes in the local database. | Valid/invalid/inactive login, session invalidation, CSRF and external-next rejection. |
| FND-02 | Every course/meeting request checks the current membership; role is per course. Missing/unavailable courses return generic 404; students receive 403 for meeting-management actions in their course. | Foreign direct GET/POST, mismatched parent course, removed membership, demotion, forged role/course, and no global staff bypass. |
| FND-03 | Members list their courses, view course meetings and meeting details; lecturers create/edit meetings only in their lecturer courses. No deletion or course/membership UI. | Form validation, persistence, timezone awareness, HTML escaping and permission checks. |
| FND-04 | Sample data spans two courses, six users and mixed roles, with generated local credentials. Counts are not limits. | Repeatable seeding, preserved password hashes and refusal to overwrite unrelated accounts. |

Automated server evidence is in [testing.md](testing.md). Responsive CSS is
implemented but browser/phone rendering was not verified because browser
permission for localhost was declined. These foundation tests are separate
from the future AC-01 through AC-07 checks and do not establish classroom load
or comments timing behavior (which has separate D-17 regression coverage). The current English UI is a reversible
implementation choice, not an approved final language restriction.

## 10. Unit B Implementation and Verification Boundary

D-27 through D-30 are user-approved implementation decisions, separate from
AS-01/AS-02. Attendance and connected requests are implemented. Video AI and
English poll generation were added in later stages; homework remains experimental. The 5-minute/30-second/45-second and subsequent
2-minute timing rules are server-enforced, including 15-second overlap bounded
by closure. Login continuation and POST both revalidate code and course role.
GET must never persist attendance. Duplicate and additional-window registration
preserve the original record, timestamp and status. The UI/XLSX label is
Registered in an additional window, without inferring lateness.

Acceptance extensions to AC-01: test expiry during login and between GET/POST,
closure before POST, malformed and wrong-meeting codes, CSRF rejection,
reopening invalidation, simultaneous identical/different student registrations,
and immutable first registration. Verify XLSX text safety and snapshot semantics.
AC-02 adds trimmed 1/1000/1001-character boundaries, duplicate-submit protection,
server privacy and role revalidation, escaped text and failed-save reporting.

Executed server/JavaScript logic results are recorded in testing.md; they do
not prove native camera scanning, visual layout, browser polling behavior,
classroom capacity or physical presence; clarified comments timing has separate server regression coverage. The manual phone
plan is in phone-testing.md and has not been executed.

## 11. Current Implementation and Historical Milestones

The website implements Django/Templates authentication and course-membership roles,
meeting management, attendance/QR/XLSX, connected comments during or outside class,
and the complete poll lifecycle. Local Qwen3 8B generates **English** editable poll
drafts; Hebrew editing/publication/voting remain supported, but Hebrew automatic
generation is unavailable. New MP4 jobs validate/extract audio, transcribe with the
pinned local large-v3-turbo CUDA checkpoint, then summarize with local Qwen3 8B.
A failed summary retains an available saved transcript; legacy completed jobs are
unchanged. Homework review/comparison has an approved **planning baseline** (D-46 through
D-52). The assignment/submission foundation is implemented under D-53;
AI feedback/comparison remains feasibility/planning only, not a website feature. Functional operation does not establish reliable AI accuracy,
phone usability, classroom capacity or a completed in-class demonstration.

Unit A supplied the shared foundation; Unit B added attendance/comments; the
initial Unit C used disabled generation plus labeled demo fixtures; Unit D
initially stopped after extraction; Unit E added transcription. These are
historical milestones. D-38 enables local transcription, D-39 defines private access/expiry and D-40
records functional acceptance without a manual reference. D-41 selects turbo for
new uploads, D-42/D-43 add local
summaries and D-44 adds English poll generation. Previously completed jobs are
not retroactively processed. Disabled/test providers are not normal runtime
alternatives and never establish automatic-generation acceptance.

AC-01 through AC-07 remain acceptance targets. Software checks, real-model
samples, user-reported interface checks and open phone/classroom/quality gaps
are separated in the [testing strategy](testing.md#current-component-to-test-strategy).
See [current components and diagrams](architecture.md) and the
[tools report](local-ai-feasibility.md#current-tools-and-evidence-index).

## UC-05 implemented submission slice

The UC-05 submission foundation is implemented: Lecturers create meeting-linked
assignments with instructions and one criterion per line; enrolled Students submit
text as append-only numbered versions. Owners see their history; current course
Lecturers can read all submitted versions. The status is **Submitted**, not reviewed
or published. AI review requests, comparison, feedback drafts/publication, feedback
language configuration and cleanup remain planned. No model is called by this stage.

Normal CSRF-protected form POSTs create assignments and submitted versions. Fresh
course membership and server-selected assignment/owner prevent posted IDs/roles
from changing scope. Direct URLs resolve course -> meeting -> assignment ->
version; Students are filtered to their own versions and Lecturers require current
course membership. Read-only version URLs reject POST. Invalid or failed saves
never confirm success. Blank work/instructions/criteria are rejected; no numeric
homework text/workload limit is introduced here beyond existing HTTP transport
limits. Title metadata uses the existing site's 160-character convention.

Resubmission computes the next owner/assignment version under a short SQLite
IMMEDIATE transaction; uniqueness prevents duplicate numbering. Submitted text
is kept exactly, including leading/trailing whitespace and line breaks. The model
save path rejects editing an existing version; no edit/delete endpoint exists.
This is application immutability, not a claim that privileged direct SQL cannot
alter data. Demo data remains synthetic; no automatic cleanup is implemented.
