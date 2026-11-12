# Decisions and Assumptions Register

## 1. Purpose and Status

This register distinguishes assignment requirements, approved decisions and open proposals.
D-17 resolves comments timing as during/outside class through normal connected
submission; D-54 closes the attendance interpretation-email wait, with lecture-section review still to do.

The website implements Django/Templates authentication and course-membership roles,
meeting management, attendance/QR/XLSX, connected comments during or outside class,
and the complete poll lifecycle. Local Qwen3 8B generates **English** editable poll
drafts; Hebrew editing/publication/voting remain supported, but Hebrew automatic
generation is unavailable. New MP4 jobs validate/extract audio, transcribe with the
pinned local large-v3-turbo CUDA checkpoint, then summarize with local Qwen3 8B.
A failed summary retains an available saved transcript; legacy completed jobs are
unchanged. Homework assignment/submission and authorized reading are implemented under D-53;
AI review/comparison remains feasibility/planning only, not a website feature. Functional operation does not establish reliable AI accuracy,
phone usability, classroom capacity or a completed in-class demonstration.

Current evidence: [tools](local-ai-feasibility.md#current-tools-and-evidence-index),
[architecture](architecture.md), [tests](testing.md#current-component-to-test-strategy).

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

### Lecturer clarification response and project choices

The user reports receiving the lecturer's reply: requirements 1-5 were detailed
in the lecture, and implementation/design details are ours to decide. The email
wait is closed. This is the lecturer's clarification about **design freedom**,
not an assertion that the lecturer selected or technically validated our methods.
Review the relevant lecture section for requirements 1-5; this update does not
claim that the recording/slides have independently been reviewed.

| Project choice | Actual behavior / limitation | Status |
|---|---|---|
| Rotating QR attendance | A signed-in Student scans a rotating code. After code/session validation a protected automatic POST records attendance and prevents duplicates. A still-valid code can be forwarded in real time, so physical presence is not proven. | Project design under the clarified freedom; no email reply outstanding. |
| Online list and XLSX snapshot | Lecturer sees attendance in the site and exports a point-in-time XLSX file that can be opened without a connection. No edit back-sync or disconnected registration is implied. | Project design; no email reply outstanding. |
| Speech-based video summary | Analyze recorded speech through transcription/summarization and disclose that visual information not spoken is excluded. | Project design; no email reply outstanding. |

D-17 comments during/outside class remains already resolved and unchanged. Real
classroom/phone/quality verification is separate from closing the email wait.

## 3. User-Approved Decisions

| ID | Decision | Boundary |
|----|----------|----------|
| D-01 | Plan a demo with all five capabilities genuinely active. | User-approved planning target; not yet verified with the lecturer as the required implementation coverage. |
| D-02 | Python is the main language for the server and AI processing. Prefer simplicity when choosing the web interface later. | D-23/D-26 now select the initial web/development stack. Local video/English-poll adapters are implemented; homework AI and hosting remain open. |
| D-03 | All project documents are in English; explanations and progress reports to the user are in Hebrew. Code and commit messages are in English. | This supersedes the earlier request for Hebrew documents. |
| D-04 | During the initial requirements-drafting stage, README, draft SoW, draft SRS, and this register were prepared, and AGENTS.md was updated to distinguish documentation and conversation languages. | Historical documentation milestone; application implementation and runtime verification were not part of that stage. It did not approve the open demo reductions. |
| D-05 | The lecturer opens a meeting and an attendance-registration window. An identified student scans a temporary QR displayed in class and rotated during that window. The system validates the code's validity and meeting association, records attendance and time, and prevents duplicate attendance for the same student and meeting. | Implemented in Unit B with server checks; the technique is a project choice under the lecturer's design freedom (D-54), not a lecturer-prescribed method or proof of physical presence. Identity follows D-24; D-27/D-28 resolve timings, transitions and additional-window behavior. The mechanism does not conclusively prove physical presence or prevent real-time sharing of a still-valid code. |
| D-06 | The lecturer views an online attendance list and can export it to XLSX. The exported file is a point-in-time snapshot, with no synchronization of edits back into the application. | Implemented snapshot behavior; D-29 resolves fields and excludes manual corrections. D-54 closes the email wait and leaves implementation details to the project; disconnected attendance registration is not implied. |
| D-07 | A university-network-origin check is only a conditional option subject to a feasibility study. | It is not an approved implementation requirement. The study is deferred, not executed, and does not block other project work; using a network check would require a further decision. It cannot be treated as proof of a person's identity or physical classroom presence. |
| D-08 | Before generation, the lecturer selects a comprehension question or an opinion poll. A real model generates a question and four single-choice options from pasted learning text. For comprehension it also proposes one correct option and a short explanation; opinion polls have neither a designated correct answer nor correctness evaluation. | Approved project design for AS-03; the handout does not prescribe these types or require an LLM for polls. D-31 resolves poll language and input length; D-32 records the historical disabled stage; D-44 enables local English generation. Hebrew generation and general quality remain unaccepted. This early decision did not select a model; D-44 later selects local English generation; D-23 subsequently selects the web framework. |
| D-09 | The lecturer reviews and may edit all generated content before publication only, including the correct answer and explanation for comprehension questions. Each identified student submits one final response per poll with no changes after submission. One poll may be active per meeting; additional polls can be created after the previous poll closes. Closure is manual. | Lifecycle implemented in Unit C and covered with server/test-fixture checks; D-44 adds local English generation; semantic Lecturer review remains required. The initial website student-identification method is D-24; the one-active-poll rule is per meeting, not a global one-meeting limit. |
| D-10 | During voting, the lecturer sees the respondent count and response distribution as counts and percentages. Students see aggregate results only after closure, without respondent identities. For comprehension questions the correct answer and short explanation are also revealed to students only after closure. | Approved visibility rules. No grades are assigned; opinion polls never designate or evaluate a correct answer. Current disclosure implementation has software coverage in testing.md; approval alone is not test evidence. |
| D-11 | The basic polling scope excludes grades, file uploads, open-ended questions, and automatic scheduling. Generation failure produces an error and a retry option, without presenting prepared content as generated from the supplied material. | Approved scope and failure behavior. Generation/error handling and disclosure have software coverage; local English generation has narrow real-model evidence under D-44, not broad semantic acceptance. |
| D-12 | Target support for Hebrew and English recordings, producing each summary in the spoken language of its recording, without translation in the first version. | Hebrew/English local cases were exercised, with remaining Hebrew transcription/summary failures; broad reliable language support is not established. D-15 clarifies Hebrew speech with English technical terms and the limit on sustained language switching. This decision concerns video summaries, not poll language. |
| D-13 | Summarize video through audio extraction, speech transcription, and model-based summarization of that transcript. Analyze audio only and clearly state in the result that visual information not spoken in the recording is not included in the analysis. | Implemented local pipeline under D-38 through D-43, with measured sample evidence and unresolved accuracy limits. No visual analysis is approved. D-54 records speech-only processing as the project choice under design freedom; review the relevant lecture section. D-14 and D-16 now define the input/output direction and the policy for later numeric limits. |
| D-14 | The lecturer manually uploads a file from the computer, with MP4 as the initial supported format. The result contains a summary paragraph and 3-5 key points, alongside an option to view the full transcript. | Implemented layout/upload path under D-34 through D-43; this does not establish reliable summary accuracy. No additional formats, link-import workflow, transcript editing, or transcript export are established by this decision. |
| D-15 | Planned verification includes a Hebrew lecture using English technical terms, in addition to Hebrew and English recordings. The summary remains in the recording's spoken language without a translation stage. | Sustained switching between languages is outside the current commitment. This does not exclude ordinary English technical terminology in a Hebrew lecture or claim that this case has already passed. No automatic rejection/detection policy or numeric switching threshold is chosen. |
| D-16 | Set maximum video duration and file size after measuring processing time and cost. Define the demo-segment duration separately from those system limits. | The measurement-first policy is approved. D-34 now fixes initial limits at 4 minutes/200 MB; demo length remains separate and undecided. No unlimited-length capability, completed benchmark, provider, or budget is implied. |
| D-17 | Resolved following the user's clarification on 2026-11-11: for comments/suggestions, online means during class and offline means outside class. Both use normal website submission to an associated meeting, including a past meeting. Keep creation, submission and confirmed storage distinct. | This supersedes the earlier clarification gate and exclusion of after-class online use as coverage. No local persistence, send queue or disconnected synchronization is required. Stored requests retain student-own and lecturer-meeting visibility, including a later lecturer login. This clarification concerns AS-02 only; attendance online/offline interpretation remains open under Q-02. |
| D-18 | Identified students create meeting-associated requests of type comment or suggestion. A student sees only their own requests; the lecturer sees all requests for the meeting. Store requests and provide history; show new requests to the lecturer without manual refresh. | Implemented connected flow with server checks; the user reported a comment appearing to the lecturer without manual refresh (testing.md). Phone use and other unreported browser scenarios remain unverified. Creation, submission, and storage remain distinct under D-17. The initial identity method is subsequently selected under D-24; retention duration remains open; D-30 resolves length and visible-page update defaults. |
| D-19 | The first comments/suggestions version excludes lecturer replies, discussion threads, attachments, votes, and notifications. D-17 resolves during/outside-class timing through normal connected use. | Approved scope boundary, not a replacement of the offline requirement. Outside-class website submission is the approved offline interpretation; no local persistence, queue or disconnected synchronization is required. |
| D-20 | Support theoretical homework assignments with pasted-text submissions in Hebrew and English. The lecturer supplies instructions and review criteria. A student may request review of their own work; the lecturer may request review of any submission. An LLM processes the work against the supplied instructions/criteria and returns strengths, gaps, and actionable recommendations. | Approved implementation and verification target, not tested language or review support. D-50 now fixes language selection per assignment; real-output language readiness and measured limits and quality acceptance remain open; D-47/D-48 now fix source selection, snapshots and version associations, and D-46 adds publication review. No one-assignment system limit is approved. |
| D-21 | Compare actual other submissions for the same assignment, addressing topic coverage and solution approaches. Students see their own feedback and comparison without peer identities or full peer works; the lecturer sees all submissions and feedback. With no peer submissions, individual review is allowed but must explicitly say that no comparison was performed. | Comparison must actually process peer inputs; general LLM knowledge or canned comparison is not a substitute. D-47/D-48 now fix latest-other-owner selection, source snapshots and immutable version associations; D-49 separates comparison outcomes. No anonymity guarantee beyond the approved student-visible exclusions is claimed. |
| D-22 | The first homework version excludes grades, plagiarism determinations, and execution of submitted code. Use sample works only in the demo; their count is not a system limit. | Approved first-version and demo scope. Actual student homework is not approved as demo input. D-51 fixes synthetic-demo retention through demo/submission checking and intentional cleanup; real-data use/retention, future external AI-processing and spending remain Q-07; no numeric submission-count or text-length cap is set. |
| D-23 | Implement Unit A using Django, Templates and minimal JavaScript as useful, with responsive basic pages. | User-approved implementation stage. No Unit B or new AI trials are included; current pages use CSS without requiring JavaScript. |
| D-24 | Use pre-created individual demo accounts and course-membership roles, with login/logout and server-side access checks, including direct URLs. | Django password/session authentication implements the approved initial identity method. No institutional identity proof, public registration or SSO is approved. |
| D-25 | Prepare courses/memberships in demo data; lecturers may create and edit meetings in their own courses, and students may view only. | Explicitly confirmed during Unit A. No meeting deletion or course/membership management UI is added. |
| D-26 | Use SQLite for initial development and demo fixtures that exercise separation between users/courses. | Classroom load suitability is unverified. Demo counts are fixtures, not system limits. |
| D-27 | Attendance starts with a 5-minute window; QR rotates every 30 seconds and codes last 45 seconds, bounded by closure. Subsequent windows last 2 minutes. Closing invalidates all codes; reopening preserves existing registrations. | User-approved Unit B defaults, not handout-prescribed values. Implemented with signed meeting/window codes, short serialized writes and student/meeting uniqueness. Physical presence is not guaranteed. |
| D-28 | Logged-out scans return to attendance after login with fresh code/membership checks; expired codes require a new scan. Register by CSRF-protected POST only. GET renders a form which JavaScript submits, with a manual button fallback. | Preserve the first timestamp/window/status. Server tests cover login continuation, expiry during login/before POST, and concurrent registration through separate connections. |
| D-29 | Roster/XLSX fields: username, display name, course code/title, meeting title/time, registration status and first-registration time (Asia/Jerusalem). Use Present, Registered in an additional window, or Not registered. No manual corrections. | Current student memberships; XLSX adds export-time metadata and never syncs back. Not registered does not determine absence. No Late label. Lecturer interpretation of online/offline remains unconfirmed. |
| D-30 | Trimmed comments/suggestions contain 1–1000 Unicode code points; lecturer refreshes every 5 seconds while visible. Students see own history only. | Implemented connected flow; refresh pauses hidden and resumes visible. No local persistence, offline queue/sync, replies, threads, files, votes or notifications. D-17 now resolves comments timing; retention and classroom capacity remain open. |
| D-31 | Polls support Hebrew and English with lecturer-selected output language and a 6,000-character learning-material limit enforced on the server. | User-approved Unit C parameters resolve Q-03. Count Unicode code points including whitespace; reject whitespace-only input. Forms/service and synthetic fixtures are tested; English generation has narrow evidence under D-44; Hebrew automatic generation is unavailable under D-45 and general quality remains unaccepted. |
| D-32 | Implement the poll lifecycle with a replaceable AI contract; real generation stays disabled until a real provider is integrated and verified. Fake providers are for automated tests only, with no runtime fake/fallback mode. | Implemented lifecycle: draft edits before publication, one active poll per meeting, one final single-choice response per student, manual close and disclosure-safe aggregate results. This was the initial disabled-provider stage. D-44 now enables installed local English generation while preserving the interface and review/publication lifecycle. Full bilingual/quality AS-03 acceptance remains incomplete. |
| D-33 | Provide a separate local CLI command creating a comprehension example and an opinion example, clearly labeled Demo data — not generated by AI. | seed_demo_polls creates unpublished local fixtures only. Repeated use preserves edits/status; --new-set explicitly creates a new pair. The command does not use a fake or real provider and is not a replacement for required real generation. |
| D-34 | Unit D accepts an MP4 from a meeting, at most 4 minutes and 200 MB; enforce both on the server and verify a valid MP4 with video/audio tracks. | Approved initial numeric limits, 240 seconds and 200,000,000 bytes. Actual validation/extraction is implemented; demo-segment duration remains separate and undecided. Full AS-04 quality/AI acceptance remains incomplete. |
| D-35 | Persist task state and process one video at a time in a separate worker; show actual stage and elapsed time. Limit processing to 10 minutes from worker start, excluding queue wait. | Implemented exclusive coordinator/decoder locks, isolated media decoding, heartbeat/deadline/watchdog recovery and separate maintenance. At the initial Unit D stage, success meant Audio extraction completed. D-38 extends new uploads to local transcription; D-42/D-43 subsequently enable local summarization; the disabled state is historical. |
| D-36 | Associate each task with meeting/uploader; only that uploader may access it while still a Lecturer in the course. Keep files private; remove temporary audio at completion/failure and uploaded MP4 within 24 hours. Future transcripts/summaries have at most 7-day retention. | Implemented ownership/role checks and private fixed UUID paths. Independent maintenance uses early purge and retries; physical deletion requires the machine/maintenance to run. Unit E implements transcript storage and seven-day expiry under D-39. Original user media is unchanged. |
| D-37 | Prepare separate replaceable transcription and summarization interfaces; both engines initially remain disabled (Unit D). D-38 subsequently enables transcription; D-42/D-43 then enable local summaries. Fake providers are permitted only in tests. | Historical Unit D boundary: no AI inference at that stage. Later local adapters make real local inferences without external requests, downloads or billing. Extraction is real, including two existing sample clips; future speech/language/summary quality remains unverified. See video-processing.md and testing.md. |

The project is an individual assignment. The working planning horizon is about
three weeks, as provided by the user; the exact deadline is not confirmed.

### Subsequent approved local-transcription stage — 2026-11-08

| ID | User-approved decision | Implementation / evidence boundary |
|---|---|---|
| D-38 | Connect the existing local Whisper model/environment and working CUDA float16 configuration to normal new MP4 uploads, without downloads or external API requests. Transcribe before deleting temporary audio, within the same 600-second worker-start budget. Summarization is a separate stage. | Real transcription succeeded on both supplied clips. Actual stages, elapsed time, detected language and an owner-only full-transcript link are implemented. Legacy extraction-only jobs retain their original result. See local-transcription.md. |
| D-39 | Permit transcript access only to the uploading user while still a Lecturer in the course. Expire access seven days after transcript creation, including direct links, and purge content in cleanup. Keep mixed Hebrew/English readable. | Server authorization/expiry tests and escaped direction-aware markup are implemented; maintenance clears text and timed segments. Physical purge requires running maintenance, but direct access checks expiry independently. No claim about backups or offline-machine physical deletion. |
| D-40 | Continue technical end-to-end testing of both supplied videos without a manual reference, because the user could not reliably decipher the audio. | Both generated nonempty transcripts and owner full-text responses returned HTTP 200. Word/term accuracy has NOT been verified against manual transcription; no correct/incorrect word examples or WER are claimed. This supersedes the pending request for a manual reference as a prerequisite to functional completion, not the future quality check. |

### Approved default-model switch — 2026-11-08

| ID | User-approved decision | Evidence boundary |
|---|---|---|
| D-41 | Use the already tested local large-v3-turbo checkpoint as the default for new video transcriptions through the existing adapter. Persist actual model identity/revision, preserve all existing transcripts, and fail clearly if turbo is unavailable rather than silently substituting a model. | Pinned repo dropbox-dash/faster-whisper-large-v3-turbo, revision 0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf. Per-file SHA-256 verification and actual-loaded metadata are enforced. Full STATIC/SHORT experiment results are documented separately. Hebrew accuracy remains limited/unverified against manual transcription. At that transcription milestone summaries were disabled; D-42/D-43 later enable them. A new normal upload/worker acceptance and subsequent user-reported browser review are recorded in testing.md. The user approved stage completion: the explanation is understandable, with remaining garbled words/unclear negation and no measured word-by-word accuracy. |

### Approved initial local summarization — 2026-11-08

| ID | User-approved decision | Implemented boundary |
|---|---|---|
| D-42 | Connect installed local Qwen3 8B after saving transcription. Produce a short paragraph and 3–5 points in the recording language. Request actually explained topics, preserved negations/relationship direction, example-scoped code claims and omission of unsupported garbled details. | Replaceable local adapter and pinned installed model, prompt lecture-grounding-v3. Output is Automatic summary with an automatic-transcript/error warning and transcript link. Functional checks do not establish grounded accuracy; STATIC still includes inferred class-access claims. |
| D-43 | Keep the completed transcript accessible when summarization fails; preserve existing permissions, retention and the original overall processing limit. | No new per-stage budget. Transcript survives summary failure; owner/current Lecturer checks remain. Summary expires no later than its source transcript, max seven days; cleanup clears generated text. Unexpected output script is an explicit failure rather than edited output. |

### Approved initial local English poll generation — 2026-11-11

| ID | User-approved decision | Implementation and evidence |
|---|---|---|
| D-44 | Connect installed local Qwen3 8B to the existing poll provider for English comprehension/opinion drafts from up to 6,000 characters. Validate question/four distinct options and type-specific answer/explanation fields. Save as editable unpublished draft; Lecturer publishing stays separate after review. | Real local create/edit/publish/vote checks on stacks/queues. Drafts and active comprehension answers remain hidden from Students until approved states. An initial factual question masquerading as opinion was rejected in semantic review and closed; revised preference output passed the sample review. Automatic checks do not replace meaning review. |
| D-45 | Hebrew automatic generation is currently unavailable, with an explicit English-only message; preserve Hebrew editing/publication/voting. Failed/unavailable/invalid generation retains learning material in the form and saves no placeholder. | Form/service/provider gates and tests enforce the initial limit without changing Hebrew lifecycle validation. This is a current capability boundary, not verified full bilingual generation. No video AI, Gemini, downloads or paid provider changes. |

### Approved UC-05 planning baseline - 2026-11-11

These decisions extend D-20 through D-22; they are user-approved design choices,
not additional lecturer requirements or evidence of implemented homework support.
The review/draft/worker control structures are implemented under D-55, but actual
model generation/comparison remains unavailable. D-53 implements the first
assignment/submission slice, with its own software checks; model quality remains open.
The earlier Qwen trials do not establish either language as available for this
new feedback workflow. That historical planning checkpoint included no implementation
or new model trial; D-53 subsequently authorizes the submission foundation only.

| ID | User-approved decision | Planning / evidence boundary |
|---|---|---|
| D-46 | A Student may request feedback on their own submission; a current course Lecturer may request it for a submission in that course. AI produces a private Lecturer draft. The Lecturer reviews/edits and publishes separately; the Student sees only their own published feedback. | Planned review/publication gate, not an implemented permission or quality claim. Preserve the original generated draft separately from Lecturer edits for audit. Publication is not automatic and does not certify model accuracy. |
| D-47 | Snapshot the latest submitted version of each other Student in the same assignment at request creation. Exclude every version owned by the target submission's owner, including Lecturer-initiated requests. Save actual target/peer version IDs, instructions and criteria used. | Selection uses target owner, not requester. One version per eligible other Student; no fixed three-work cap or silent truncation. Source snapshots remain stable if a peer later resubmits. |
| D-48 | Resubmission creates an immutable new version. Previous feedback remains associated with the version it assessed. Draft edits/publication use concurrency/version checks; changed inputs must not silently relabel old feedback as current. | Planned versioned history and source provenance. Preserve older published feedback with its source version. A changed rubric/source must be flagged before publishing an old draft as current; never replace the original source snapshot. |
| D-49 | Distinguish no other submissions, comparison failure with eligible peers, and completed comparison finding no supported difference. When no peers exist, personal feedback may be published with a clear system-controlled notice. | Peer absence is derived from the saved eligible set, not model prose. Failed comparison is not absence or evidence of similarity. A no-difference claim requires actual peer processing and evidence review. D-52 resolves failed-comparison publication: a successful personal draft may be explicitly reviewed/published with its failure notice; personal generation failure has no publishable draft. |
| D-50 | Select feedback language at assignment level. Hebrew and English are test targets; expose a language for generation only after actual output in that language has been checked for this workflow. Determine length/workload limits after measurement. | Neither language is currently accepted as available for this planned workflow. Earlier outputs were actually reviewed but failed quality expectations. Record per-language outcome and remaining errors; valid JSON or language detection alone is insufficient. |
| D-51 | Use synthetic submissions only for the demo. Keep versions and feedback through completion of the demo and submission-related checking, then support explicit cleanup. | Planned intentional cleanup, not automatic seven-day expiry. Real student-work retention/consent/deletion policy requires separate discussion. No destructive cleanup runs in this documentation stage. |

### Approved partial-feedback publication - 2026-11-11

| ID | User-approved decision | Planning / evidence boundary |
|---|---|---|
| D-52 | When personal feedback succeeds but comparison with eligible submissions fails, the Lecturer may review it and explicitly publish individual feedback only. If personal feedback generation itself fails, there is no draft to publish. | Keep the draft private before publication; publish its personal content with comparison status failed and the exact system-controlled notice below. Do not relabel failed comparison as no peers or no supported difference. A later generated comparison remains a private new feedback revision until separate Lecturer review and explicit publication; it never silently replaces the currently published content. D-55 now implements this state/publication behavior with test-only provider coverage, not real-model quality evidence. |

Required Student-facing notice after individual-only publication with failed
comparison: **"Your lecturer published your individual feedback. The comparison with other submissions could not be completed."**

The no-other-submissions notice and completed-no-supported-difference result
remain distinct. D-52 resolves the former open publication policy in Q-05; all
source/version/privacy rules in D-46 through D-51 remain in force.

### Approved UC-05 submission implementation slice

| ID | User-approved stage | Actual boundary |
|---|---|---|
| D-53 | Implement meeting assignment creation with instructions/criteria, enrolled-Student text submission, immutable resubmission versions, and current-course Lecturer/owner reading. Show save confirmation, version number and Submitted status. | HomeworkAssignment and SubmissionVersion, forms, short transactional writes and scoped HTML routes are implemented. D-55 subsequently implements request/draft/publication mechanics and assignment language selection; real generation/comparison and cleanup remain deferred. No AI calls, new model downloads or paid service. Assignment edit/delete is not exposed. Tests distinguish source preservation/server privacy from later model quality. |

### Lecturer clarification and retained project choices

| ID | Source / decision | Boundary |
|---|---|---|
| D-54 | User-reported lecturer reply: requirements 1-5 are detailed in the lecture; implementation and design details are ours to decide. Retain the project's rotating authenticated QR with validated automatic registration/deduplication, online attendance with offline-readable XLSX snapshot, and recorded-speech video summary with unspoken-visual exclusion. | Attribute design freedom to the lecturer and the three technical choices to the project. Close the email wait; review the relevant lecture section without claiming it was reviewed here. Valid QR forwarding remains possible. This is not proof of physical presence, classroom/phone readiness or AI accuracy. D-17 remains resolved. |

### Approved UC-05 workflow mechanics with no active provider

| ID | User-approved stage | Actual evidence boundary |
|---|---|---|
| D-55 | Implement version-bound feedback request, private Lecturer draft editing and separate publication after closing the failed Qwen3 experiment round. Use fake providers in tests only. Before creating a request in the normal site, show that the selected language has no active provider. Keep real-model individual feedback/comparison as open requirements. | Software models, snapshots, processor, guarded routes and publication controls are implemented. Normal factory is DisabledHomeworkReviewer for English/Hebrew and creates no waiting request. Alex v1-request/v2-resubmission/v1-publication is tested with an injected provider only; no live draft is seeded. Actual inference quality/availability and measured runtime/input limits remain open; implementation is separate from experiment commit bb9cc58; real-model feedback/comparison acceptance remains open. |

## 4. Proposal Register

P-02 and P-03 retain the history of the earlier attendance proposals and their
resolution by D-05 and D-06. P-05 records the polling proposal resolved by
D-08 through D-11. P-06 is partly resolved by D-12 through D-16 and D-34; initial numeric limits are now approved, while real-model quality and demo duration remain open. P-04 is resolved for the
connected workflow by D-18/D-19, with D-17 resolving the during/outside-class interpretation. P-07 and
P-08 are resolved for the approved homework scope by D-20 through D-22, with
D-46 through D-51 resolving review/version/language/demo-retention planning and the remaining limits/quality/policy questions explicit. Other open rows do not
approve an implementation requirement or scope reduction.

| ID | Proposal and current status | Effect and unresolved boundary |
|----|---------------|--------------------------------|
| P-01 | One course, one lecturer, and one active meeting at a time. | Reduces administration; actual class size and concurrency remain unknown. |
| P-02 | Superseded by D-05: the earlier proposal used identified meeting entry as the attendance trigger. | The approved trigger is now a valid, meeting-bound rotating QR during an open registration window; meeting entry alone is not the selected trigger. Identity follows D-24; D-27/D-28 resolve timing and additional-window registration. |
| P-03 | Partly resolved by D-06: online list and XLSX snapshot export without synchronization back are approved. | D-29 resolves fields and excludes manual corrections; D-54 closes the email wait: the XLSX snapshot is the project choice under design freedom; review the relevant lecture section. |
| P-04 | Resolved by D-17/D-18/D-19: identified meeting requests, stored history, student-own and lecturer-meeting visibility, live updates and exclusions remain approved. | Online means during class and offline outside class; both use the same connected website flow, including past meetings. No local persistence, send queue or disconnected synchronization is required. Retention and classroom capacity remain open. |
| P-05 | Resolved by D-08 through D-11: model-generated comprehension questions and opinion polls from pasted learning text, four single-choice options, pre-publication lecturer review/editing, final responses, and one active poll per meeting. | Poll types, lifecycle, results visibility, exclusions, and failure/retry behavior are approved. Language and input-length limit are resolved by D-31; this row is historical, not a pending vote on the approved workflow. |
| P-06 | Partly resolved by D-12 through D-16: Hebrew/English targets, audio-only processing/disclosure, manual computer-file upload with initial MP4 support, a summary paragraph plus 3-5 key points, and full-transcript viewing are approved targets. Planned cases include Hebrew speech with English technical terms. | Sustained language switching is outside the commitment. D-34 resolves initial limits at 4 minutes/200 MB after earlier measurements; demo duration remains separate and undecided. Quality criteria remain open (Q-04); D-54 closes the email wait and retains the lecture-section review action. No fixed one-to-two-minute cap, full-lesson exclusion, or unlimited-length claim is approved. |
| P-07 | Resolved in scope by D-20 through D-22: theoretical Hebrew/English pasted-text assignments, lecturer criteria, real LLM review, and actual same-assignment peer comparison are approved. | The earlier one-assignment/three-short-submission proposal is not a system constraint. D-46 through D-51 now resolve selection/snapshots, revisions, publication gate and assignment-level language. Numeric limits and quality acceptance remain open; grades, plagiarism determinations, and code execution are excluded. |
| P-08 | Resolved in visibility/demo scope by D-21/D-22: student-own review with comparison excluding peer identities/full works, lecturer access to all submissions/feedback, and sample works only for the demo. | D-46 specifies planned access/publication and D-51 synthetic-demo retention/explicit cleanup. Real-data policies, external processing and budget remain Q-07. No real student homework is approved for the demo, and the number of demo samples is not a system cap. |
| P-09 | Prepare demo inputs in advance and aim to show actual processing within ten minutes. Label any previously processed output explicitly. | Runtime is unmeasured. Previously processed results are not a substitute for a live-processing requirement without approval; simulated output cannot establish capability completion. |
| P-10 | Optionally check whether a registration request comes through the university network, subject to feasibility (D-07). | No network restriction is approved. Address ranges, actual request path, VPN/shared-address effects, IPv4/IPv6 behavior, and handling of unavailable evidence require investigation and a later decision (Q-10). |

## 5. Questions Requiring Decisions

| ID | Question | Related items | Resolution needed |
|----|----------|---------------|-------------------|
| Q-01 | Closed email clarification under D-54: lecturer leaves implementation/design to the project and refers to requirements 1-5 in the lecture. | AS-01, D-05, D-06, D-54 | Rotating authenticated QR and online list/offline-readable XLSX snapshot are project choices. Review the relevant lecture section; functional/classroom testing remains separate. |
| Q-02 | Closed email clarification under D-54: lecturer leaves implementation/design to the project and refers to requirements 1-5 in the lecture. | AS-01, D-05, D-06, D-54 | Rotating authenticated QR and online list/offline-readable XLSX snapshot are project choices. Review the relevant lecture section; functional/classroom testing remains separate. |
| Q-03 | Resolved by D-31: lecturer-selected Hebrew/English output, 6,000 Unicode characters of learning material, server-validated. | AS-03, D-08 through D-11, P-05 | These parameters are approved under D-31. English generation has narrow real-model evidence under D-44; Hebrew generation is unavailable. Poll types, four options, lecturer review/editing, voting, closure, visibility, exclusions, and failure/retry behavior are decided; shared identity, capacity, and AI-service constraints remain Q-06/Q-07. |
| Q-04 | Initial numeric limits are resolved by D-34. What separate demo duration and summary/transcription quality criteria are appropriate, with the speech-only project choice recorded under D-54? | AS-04, D-12 through D-16, P-06 | Language, audio processing/disclosure, manual MP4 upload, output layout, full-transcript viewing, terminology test coverage, and measurement-first limits policy are decided. D-34 fixes initial system limits. Demo duration and real-model quality remain open; the email interpretation wait is closed under D-54. Sustained language switching is outside the current commitment. Reply received: D-54 closes the email wait and records project design freedom. Review the relevant lecture section. |
| Q-05 | D-46 through D-52 resolve review/publication, peer/latest-version snapshots, revisions, assignment-level language and synthetic-demo retention. What measured limits, per-language quality threshold and processing/retry limits should apply? | AS-05, D-20 through D-22, D-46 through D-52 | D-52 resolves personal-only publication after comparison failure and requires separate review/publication of any later comparison. Length/workload and runtime bounds require measurement; Hebrew/English generation availability requires successful real-output review. D-55 implements request/draft/publication control flow with test-only provider evidence; real-model feedback/comparison and accepted quality remain open. |
| Q-06 | How many classroom users, devices, and simultaneous actions must be supported, and where must the demo be accessible? | AS-06, AS-07, P-01 | Actual class conditions, network availability, and measurable usability/capacity targets. |
| Q-07 | With initial website identity/access implemented under D-24, which production safeguards, data-use, consent, retention/deletion, external-AI-processing and spending boundaries should apply? | D-02, D-10, D-18, D-21, D-22, P-02, P-04, P-08 | Poll, comments, and homework visibility rules are decided; Unit A enforces membership-scoped website access; production safeguards and data lifecycle/resources remain open. Homework demo inputs are sample works only. No budget or external-service permission is inferred. |
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

## 8. Video-Summary Decisions and Initial Limits

These are user-approved project targets, not additional handout requirements
or claims of tested capabilities:

| Topic | Approved target | Decision boundary |
|-------|---------------------|-------------------|
| Video delivery | Lecturer manually uploads a file from the computer (D-14). | Link import is not part of the selected workflow. |
| Input format | MP4 is the initial supported format (D-14). | Unit D checks/extracts real MP4 audio; local transcription/summaries are implemented; source fidelity and broad quality remain unaccepted. Other formats are not committed. |
| Summary layout | A summary paragraph followed by 3-5 key points (D-14). | No additional numeric text-length constraint is selected. |
| Transcript display | Lecturer can view the full transcript alongside the summary (D-14). | Transcript editing or export is not added by this decision. |
| Language verification | Hebrew, English, and a Hebrew lecture with English technical terms (D-12/D-15). | No translation stage; sustained language switching is outside the current commitment. Local experimental cases have been run with quality limitations; narrow website route checks exist; they do not establish full language/quality acceptance. |

**Approved limits policy (D-16):** determine maximum recording duration and
file size after processing-time and cost measurements. Choose demo-segment
duration separately. A short demo sample does not define the system's maximum
input. D-34 now approves initial limits of 4 minutes/200 MB; demo duration remains undecided, and the earlier one-to-two-minute suggestion never became a system limit. Unlimited processing or
full-lesson support has not been established.

**Historical measurement plan, partly executed:** the trials linked below informed
the approved initial caps. Future broader measurements should record processing time and cost for permitted Hebrew and English
samples of different durations and file sizes, including Hebrew speech with
English technical terms. Record input duration, language, file size, extraction,
transcription and summarization times, total turnaround, observed quality,
failures, and cost. Label estimated cost separately from actual usage charges;
if charges are unavailable, record that gap rather than a zero cost. Use the
evidence to propose maximum recording duration and file size, with a separate
demo-segment duration, for user approval. The plan itself establishes no provider, budget or result. Actual small-sample
measurements are recorded in local-ai-feasibility.md and informed the subsequently approved D-34 initial limits. Unit D extraction measurements are in video-processing.md; they do not establish AI quality. The web framework is subsequently selected under D-23. Sustained language
switching remains outside the commitment rather than silently adding
translation or an unapproved automatic rejection policy.

## 9. Open Decisions and Technical-Design Readiness

The distinctions below are planning recommendations, not additional user
decisions or blanket blockers. Conceptual component/use-case design can
proceed from the approved scope. Do not silently assume answers when fixing
an affected interface, architecture, or acceptance claim.

### Decisions needed before committing to affected technical choices

| Decision | Why it matters | Related items |
|----------|----------------|---------------|
| Shared student/lecturer identification and access method — resolved for Unit A by D-24 | Session login and membership-scoped access are implemented; future feature permissions and production safeguards still need their own checks. | D-24, Q-07 |
| First-version course/meeting organization, expected users/concurrency, and classroom access/network conditions | Determines context boundaries and the deployment/capacity assumptions; the current foundation supports multiple courses/roles/meetings; no one-course cap is approved. | P-01, Q-06 |
| Permitted external AI/data processing, budget, and data-lifecycle expectations | Needed before any new external/paid service or unresolved persistence policy; current video/English-poll adapters are local and video retention is approved. Sample-only homework demo scope does not itself approve external processing or paid use. | Q-07, D-22 |
| Eligible peer set and submission revisions - resolved for planned UC-05 by D-47/D-48 | Latest other-owner versions at request time, immutable sources and version-bound feedback; implementation and quality checks remain pending. | D-47/D-48, Q-05 |

The former comments clarification gate is closed under D-17: during/outside-class website submission covers the clarified timing interpretation. No disconnected mechanism is needed. Lecturer interpretation of
attendance and audio-only summaries also remains unconfirmed (Q-01/Q-04);
record any scope impact rather than inventing confirmation.

### Details that can be resolved during later design or feasibility work

- Poll language/input length is resolved by D-31. D-50 now fixes homework language selection per assignment, with language-specific real-output acceptance still pending. Interface language remains open;
  do not assume the video-language decision applies to them (Q-03/Q-05/Q-06).
- Attendance timing, additional-window handling, export fields/no manual corrections and comment length/update defaults are resolved by D-27 through D-30. Classroom capacity and remaining retention policies stay open; D-54 closes Q-01/Q-02 email waiting and retains a lecture-section review action.
- Initial video duration/file-size limits now follow D-34; later revisions still require evidence under D-16. Homework text/workload bounds and AI quality/latency criteria need
  evidence and agreement, not an invented cap from the demo dataset.
- Video retention and current local no-auto-retry behavior are decided; remaining
  homework/comments retention, future retry details and presentation layout can be refined after the high-level lifecycle/access decisions and
  before implementation or verification of the affected behavior.
- Exact deadline/submission instructions and live-demo completion expectations
  are needed soon for the schedule and rehearsal, but do not prevent initial
  conceptual design (Q-08/Q-09).

The university-network study remains deferred, conditional, and non-blocking
(D-07/Q-10). The historical readiness review did not itself approve technology. Later
D-23 through D-26 approve Unit A; its design and verification are recorded in
architecture.md and testing.md.
