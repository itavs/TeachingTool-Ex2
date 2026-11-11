# Verification Record — Units A, B, C, D and E

## Current component-to-test strategy

This section addresses To Do 8 and the real names in the
[class/interface diagrams](architecture.md#class-and-interface-diagrams).
It is a current strategy/index over existing tests, not a new execution record.
Dated results below retain provenance. **No software tests or AI trials were run
in this documentation round.** The previous poll-stage closure recorded 136 server
and 12 JavaScript tests passing; the later personal-review helper records two
standalone audit tests, outside that website count.

Use software tests for deterministic contracts, state/permission/retention and
process-control assertions; use bounded real-model samples for inference wiring
and content review; require separately reported browser/phone/classroom evidence
for those environments. A fake engine may verify failure handling or disclosure,
never speech/feedback/summary correctness. Exact-source quote checking does not
prove that the quote supports the assessment.

| Diagram component / responsibility | Risk or invariant | Existing software evidence (named tests) | Real-model / open boundary |
|---|---|---|---|
| User, Course, Membership, Meeting, MeetingForm | Cross-course access, forged role/parent and invalid writes | [Foundation suite](../classroom/tests.py); [class-aware assertions](#class-aware-coverage) | User browser checks are separate; production identities/phone/load open. |
| AttendanceWindow, AttendanceRecord and attendance module | QR expiry/login continuation/duplicate registration; one record per student/meeting | [Participation suite](../classroom/test_participation.py): test_close_invalidates_every_code_even_after_reopen, test_window_closed_after_get_rejects_post_and_next_scan_requires_new_code; concurrent registration cases in same suite | User QR report is not a phone/classroom acceptance or physical-presence proof. Lecturer interpretation pending. |
| MeetingRequest and request form/views | Outside-class persistence and Student-own/Lecturer visibility | [Participation suite](../classroom/test_participation.py): test_outside_class_requests_for_past_meeting_persist_for_later_lecturer | User reported live appearance of a comment; D-17 resolved. Broader load/retention open. |
| Poll/PollVote, poll_services.edit_draft/publish/vote/close | Stale edits; second Active poll; concurrent duplicate vote; vote/close ordering | [Poll suite](../classroom/test_polls.py): test_draft_edit_all_content_and_optimistic_version, test_same_student_parallel_votes_are_final_and_unique, test_parallel_publications_only_one_active_poll, test_vote_racing_close_has_one_consistent_order | Real local generated drafts exercised lifecycle; not classroom load. |
| poll_services.public_payload and Poll views | Draft/answer privacy; review notice only Lecturer/Draft | [Poll suite](../classroom/test_polls.py): test_student_cannot_see_drafts_in_list_detail_or_state, test_ai_review_notice_is_lecturer_draft_only_in_list_detail_and_state | User opinion-results checks reported separately; browser/phone matrix incomplete. |
| PollGenerator / LocalPollGenerator / poll_contract | Invalid or unavailable engine must save no draft and retain material; Hebrew lifecycle unaffected | [Generation tests](../classroom/test_poll_generation.py): test_valid_comprehension_and_opinion_are_not_rewritten, test_bad_fields_script_duplicates_answer_and_incomplete_explanation_rejected, test_adapter_protocol_is_local_only_and_removes_private_material, test_unavailable_real_adapter_preserves_form_without_creating_poll, test_invalid_output_preserves_material_and_does_not_save, test_generated_poll_is_draft_hidden_from_student_before_separate_publish, test_hebrew_existing_draft_edit_publish_and_vote_remain_supported | Actual English stacks/queues route in local-poll-generation.md; factual opinion defect caught in review. Hebrew generation unavailable; max-input semantic/latency quality unproven. |
| BoundedUploadHandler / VideoUploadForm / video_jobs.save_upload | Oversized/corrupt/no-audio input and unauthorized upload | [Video tests](../classroom/test_videos.py): test_size_handler_boundary_and_real_http_abort, test_duration_limit_is_server_enforced_with_real_media, test_corrupt_no_audio_and_audio_only_are_failed_by_worker, test_authorization_owner_lecturer_and_parent_scoping | Both supplied clips extracted; input-limit checks do not prove ASR accuracy. |
| VideoJob / video_worker.claim_job/process_job / media_child | One worker; queue wait separate; timeout/stop/stale recovery; remove temporary audio | [Video tests](../classroom/test_videos.py): test_single_worker_lock_and_fifo, test_queue_wait_does_not_consume_processing_budget, test_timeout_terminates_actual_subprocess_and_removes_audio, test_hard_stopped_worker_is_recovered_and_decoder_does_not_orphan | Real uploads/workers exercised; full GPU hard-crash testing not claimed. |
| Transcriber / LocalWhisperTranscriber / checkpoint helper | No fallback/download; valid metadata/text; one deadline; failure cleanup | [Transcription tests](../classroom/test_transcription.py): test_unavailable_turbo_fails_clearly_without_fallback, test_loaded_model_identity_is_retained_if_inference_fails, test_total_deadline_is_not_reset_at_transcription_start, test_adapter_protocol_keeps_text_off_stdout_and_forces_offline_environment, test_checkpoint_verification_rejects_missing_or_changed_files | Real medium/turbo on full SHORT/STATIC and new turbo uploads. No human-reference word accuracy; Hebrew code terms/negation remain uncertain. |
| Summarizer / LocalQwenSummarizer / summary contract | Save transcript first; invalid language/model/format; failed summary preserves transcript | [Summary tests](../classroom/test_summaries.py): test_full_lifecycle_stores_transcript_first_then_summary_with_shared_expiry, test_summary_failure_keeps_saved_transcript_accessible, test_hebrew_summary_accepts_english_code_terms_without_rewriting, test_format_language_and_wrong_model_are_rejected | SHORT real upload success; STATIC saved-input success but uploaded summary_language failure. Structural tests cannot certify source grounding. |
| video_jobs.owned_job/transcript_available/summary_available/purge_expired_transcripts | Owner/current role on direct URL; exact expiry; summary never outlives transcript | [Transcription tests](../classroom/test_transcription.py): test_demotion_revocation_and_mismatched_parent_block_saved_link, test_expiry_blocks_at_exact_deadline_even_before_cleanup; [summary tests](../classroom/test_summaries.py): test_expiry_hides_summary_on_direct_job_url_and_cleanup_clears_both | Actual owner pages opened; seven-day passage is tested with controlled time, not a seven-day live wait. Physical cleanup requires running maintenance. |
| ProcessTree / exclusive_lock | Orphan compute and competing video/poll AI | [Summary tests](../classroom/test_summaries.py): test_windows_process_tree_close_terminates_owned_descendant; [video tests](../classroom/test_videos.py): test_single_worker_lock_and_fifo; generation adapter protocol test above | Owned-descendant test uses ordinary Python, not a real GPU hard-crash. Real sample services exited; classroom contention unmeasured. |
| transcript_display.reading_paragraphs / Templates / browser scripts | Reordering/rewriting, RTL-LTR, escaping, hidden-page polling and double reload | [Display tests](../classroom/test_transcription.py): test_pause_boundaries_preserve_words_and_isolate_new_car, test_unmatched_legacy_segments_do_not_replace_text; [JS video tests](../tests_js/videos.test.cjs), [poll tests](../tests_js/polls.test.cjs), [participation tests](../tests_js/participation.test.cjs) | User opened STATIC transcript and SHORT summary/link. Actual-phone layout and full keyboard/browser matrix remain open. |
| Personal-review audit helper (experiment only, not website class) | Fabricated quote versus unsupported conclusion | **Local only / unpublished:** experiments/local_ai/test_personal_review_probe.py (two reported audit tests); excluded from this documentation commit | **Local only / unpublished:** docs/homework-personal-review-feasibility.md reports 15/15 exact quotes, but technical false positives/negatives persist. No homework acceptance. |

### Evidence boundaries and outstanding acceptance

- **Software:** request/database/rendering/contracts and bounded process tests
  above; test doubles and controlled clocks are disclosed in dated records.
- **Real model:** measured local ASR, summary, English poll and synthetic homework
  trials are indexed by the [tools report](local-ai-feasibility.md#current-tools-and-evidence-index).
  The independent homework coverage map was not supplied to the model. Gemini
  has no substantive task-quality result; user-reported direct HTTP 503 is a failure.
- **Manual interface:** user reports are labeled as such below. They do not
  establish unreported phone, audio-reference accuracy or classroom-load tests.
- **Open:** lecturer acceptance of QR/list-XLSX/speech-only interpretations (the
  user has sent the questions; replies pending), phone/network/load conditions,
  broad AI quality and the actual ten-minute class demo/final conclusion.
  D-17 comments timing is resolved; no disconnected queue is required.
- **Reproducibility:** repository links above point to tracked files included in a clean clone.
  New homework probes/reports/audit tests and later Gemini updates remain
  unpublished local files, as labeled. Models, supplied media/raw transcripts
  and independent experiment maps also remain local-only.

### Documentation publication verification - 2026-11-11

The documentation review checks the prospective staged tree rather than mere
working-directory existence: repository links must resolve to tracked files and
headings after commit; excluded homework/Gemini artifacts are explicitly labeled
local-only/unpublished without repository links. README maps the eleven populated
To Do items in page-2 order. The two previous homework experiment execution records
remain unstaged; their outcomes are summarized in the tools index without
publishing those experiments.

All four current architecture Mermaid blocks and the historical video-processing
sequence were parsed and rendered with
Mermaid 11.12.0 in headless Chrome and their PNGs visually inspected. Rendering
exposed sequence-message semicolons interpreted as statement separators; those
labels were corrected to commas. No application behavior changed. The render
helper/library/SVG/PNG outputs are local-only under ignored .local/doc-review,
not submission dependencies or committed artifacts. This is documentation QA,
not a new model, website, phone or classroom test.

## UC-05 submission foundation

Implemented under D-53; this section supersedes the planned status only for
assignment creation, submitted versions and authorized reading. Review jobs,
AI, comparison and feedback publication remain unimplemented and untested.
The two previous uncommitted model experiment records below are unchanged.

**Executed:** the full website suite passed **151 tests in 55.674 seconds**, using
a separate file-backed SQLite test database, no skips. This includes **15 new
homework tests** in [test_homework.py](../classroom/test_homework.py). An earlier
focused run of the first 14 tests passed before the additional Lecturer-access
case was added; the complete run includes that case. **12 JavaScript tests passed**.
System check, migration-drift check and dependency check passed. Migration
0007_homework_submissions was applied to the ignored local development database.
No model inference or external-provider request occurred.

| Actual component | Executed assertions |
|---|---|
| AssignmentForm / homework_services.create_assignment / HomeworkAssignment | Lecturer normal-form creation; server-selected meeting/creator despite forged fields; required title/instructions/ordered criteria; Student can read instructions. Student/foreign-course creation denied. |
| SubmissionForm / homework_services.submit_version / SubmissionVersion | Normal POST save confirmation and Submitted/version display; second submission preserves both exact sources including whitespace/line breaks and Hebrew/English terms. Posted owner/assignment/version/status ignored. Concurrent real-connection submissions receive numbers 1/2 and retain both texts. |
| assignment_for / submission_for / scoped guard | Owner sees both version URLs/history; current course Lecturer and a second Lecturer in that course can read; another Student cannot discover/open versions; a foreign Lecturer/nonmember and global staff flags do not bypass scope. Wrong course/meeting/assignment substitutions fail. Fresh membership removal/demotion applies to direct reads and stale-form writes. |
| CSRF, read-only endpoints and source integrity | CSRF rejection and successful token-bearing creation/submission; anonymous login redirects; POST to read-only version/list routes rejected; model save rejects editing saved versions; DB rejects duplicate/zero numbering. Blank work is not saved and failed-save HTTP 503 cannot display success. |
| Templates / source display | Escaped source HTML, dir=auto and pre-wrap reading style; explicit Student/version/time/Submitted fields. No review-request action is offered. These are server markup assertions, not phone/browser visual acceptance. |

These checks establish website control flow and source persistence, **not feedback
quality**. Application save paths are append-only; no database trigger blocks
privileged bulk/SQL administration. SQLite two-request success is not classroom
capacity acceptance. No numeric homework-content/workload limit is established;
existing Django request-memory limits still apply. Criteria are stored as ordered
text, one line per criterion; feedback-language/rubric-version configuration is
not part of this slice. Assignment editing/deletion and intentional demo cleanup
remain deferred.

Manual browser steps for lecturer_alpha/student_alex are in the
[README](../README.md#uc-05-submission-foundation---local-browser-check).
### User-reported Lecturer version check - 2026-11-11

The user reported opening both **Version 1** and **Version 2**, submitted by
**student_alex**, in the browser as a Lecturer after resubmission. Each version
showed its corresponding text. This is a user-reported manual Lecturer reading
and version-preservation check, not agent-operated browser evidence. It does not
establish Student submission UI, phone layout, other users' access restrictions
or model quality; server authorization/source checks above are separate evidence.

The agent separately verified the active loopback server's authenticated HTTP
navigation from DEMO-CS101 / Test Meeting through Assignments and submissions to
New assignment (all HTTP 200). The old --noreload process initially served the
previous template; restarting that development server exposed the existing new
link without a template correction. This was HTTP/form inspection, not browser
visual acceptance or a newly created assignment. No phone/network binding changed.

Before the submission-stage commit, all 15 focused homework tests passed again
in 0.465 seconds on a separate file-backed SQLite test database, with no skips.
System and migration-drift checks passed. This documentation-only manual-report
addition did not change application code or require a new AI trial.
Gemini/homework experiment changes remain separate from this submission stage.

## Planned UC-05 acceptance strategy

**Full review acceptance is not executed.** D-46 through D-52 define the review
planning baseline; D-53 foundation checks are executed separately above. This section does not modify the historical homework experiment records
below. The assignment/submission subset is now implemented under D-53 (see the
[executed foundation checks](#uc-05-submission-foundation)). All feedback/review/
comparison/publication additions in the diagrams remain planned. Separate deterministic website acceptance from
actual-model conclusion quality. Test fixtures can validate control flow, not
claim real feedback generation or an accepted language.

### Planned website correctness checks

| Planned responsibility | Risk / acceptance check | Evidence status |
|---|---|---|
| HomeworkReviewService + existing Membership | Student requests only own work, course Lecturer may request a course submission. Reject forged owner/course/version, direct cross-user/cross-course HTML/JSON and revoked membership at request/save/publication/read. | Planned tests, no implementation. |
| SubmissionVersion | Resubmission preserves exact earlier text and version; old published feedback stays associated with that version. Concurrent submissions cannot overwrite a version. | Source/version/concurrency checks implemented under D-53 in test_homework.py; feedback association remains planned. |
| ReviewJob source selection | Save latest version per other owner in the same assignment at request creation; exclude all target-owner versions, not merely requester versions. **Lecturer initiates review of A, where A has multiple versions: none of A's versions may appear as a peer.** Include latest B/C only, exclude foreign assignments, and preserve the chosen snapshots after later resubmission. | Planned transactional/source-selection tests. |
| ReviewJob provenance | Save actual target/peer IDs, instructions, criteria, assignment revision/language, actual model identity and failure stage. Editing source/rubric/language does not rewrite prior request inputs. | Planned persistence tests. |
| FeedbackDraft + review service | Student cannot discover draft text/evidence via list/detail/JSON. Lecturer can review/edit; only separate CSRF Publish exposes version-bound public content. Original generated text is distinguishable from edits. Stale or concurrent edit/publication and changed-source-as-current attempts are rejected or explicitly flagged, never silently relabeled. | Planned disclosure/concurrency tests. |
| Student output projection | Only own published feedback; no peer identities, IDs, stable labels, full works or private comparison quotes/evidence. Lecturer can inspect permitted sources. Test accidental provider identity fields and escaping. | Planned privacy/rendering tests. |
| Comparison state | Empty eligible set produces system-controlled no-other-submissions notice and permits personal publication. Nonempty set plus failure retains personal draft with a separate comparison-failed state, never no peers or no difference. Completed no-supported-difference is distinct from completed differences. D-52 permits personal-only publication only after successful personal generation, Lecturer review and explicit selection; keep comparison failed. Personal generation failure has no draft/publication. | Planned state/publication tests, policy resolved by D-52. |
| Language gate | Assignment stores selected language; unsupported/unaccepted language fails before inference. A generation language can be enabled only with recorded reviewed real output for this workflow. Existing failed Hebrew/English probes do not enable either language. | Planned gate tests plus separate real-output evidence below. |
| Worker / HomeworkReviewer / validator | Unavailable/invalid/timeout/interrupt/busy reports a real failure without prepared fallback or automatic publication. Verify shared-compute integration without changing video processing. Numeric control bounds/retries require a later measured decision. | Planned injected-provider/process tests, not real model quality. |
| Explicit synthetic-data cleanup | Keep versions/feedback through demo and submission checking. Then an intentional authorized cleanup removes linked demo content consistently without deleting unrelated course data. No inherited seven-day expiry or automatic deletion; real-work policy remains separate. | Planned lifecycle tests, no cleanup executed. |

### Planned partial-publication regression (D-52)

**Not executed.** Arrange eligible peers, successful personal feedback and failed
comparison. Assert that the Student cannot read the private draft through list,
detail or JSON. The Lecturer sees the successful personal draft and separate
comparison failure, reviews/edits and explicitly chooses individual-only
publication. After publication the owner sees the published personal content and
comparison status failed, with this exact system-controlled notice:

> Your lecturer published your individual feedback. The comparison with other submissions could not be completed.

Assert that no-peer and completed-no-supported-difference messages are absent,
no peer identities/private evidence are exposed, and another Student cannot read
that feedback. Revoked/wrong-role users cannot publish. A personal-generation
failure creates no publishable draft and exposes no publication action.

Then produce a fixture for a later successful comparison: keep the previous
publication and failure notice unchanged while the new feedback revision is
private. Only a second explicit Lecturer review/publication exposes the new
comparison and updates the visible comparison state. Retain source snapshots and
publication history. An injected provider proves these state/privacy controls,
not the quality of a real comparison; model quality is evaluated separately below.

### Planned model quality checks

Use only synthetic work and an independent criterion/coverage map prepared before
generation and kept outside the prompt. Retain exact inputs, original outputs,
model/configuration and timings locally. A reviewer checks each claim against its
referenced source and criterion, not merely fluent wording or valid JSON.

| Quality target | Required source-based evaluation |
|---|---|
| Quote presence versus entailment | Mechanically verify each quote against the correct frozen target/peer version. Separately check relevance, surrounding context and whether the conclusion follows; an exact quote cannot certify technical correctness or absence of a topic. |
| Missing / partial / incorrect | Missing means relevant explanation is absent, partial means meaningful correct coverage is incomplete, incorrect means an explicit wrong explanation. Correctly credit explicit coverage rather than demand unapproved SQL/code detail. |
| Original A/B/C | A must receive credit for the conditional seat update. B must receive credit for explicit rollback while its wrong UNIQUE/last-seat and cache-only approval claims are identified. C must receive credit for locking/recheck while its actual failure/rollback and duplicate-protection gaps are recognized. |
| Controlled B cache correction | Change only the cache-authorization sentence. The cache criticism must disappear or become an appropriate acknowledgment; the unchanged UNIQUE/last-seat error must still be identified, and unchanged rollback/atomicity coverage must not improve or worsen without source justification. Check actual findings, not identical wording or score strings. |
| Real comparison | Actually process saved other-owner submissions and identify a concrete supported coverage/approach difference, such as A's conditional update versus C's locking/recheck. Check the private evidence against each source; no invented omissions, majority-as-correctness or cross-assignment comparisons. |
| Similar works | Use deliberately similar synthetic works. A completed comparison may correctly state no supported difference; verify actual processing and review the basis. This must not substitute for empty peers or failed inference. |
| Hebrew / English readiness | Test real complete feedback and comparison output in each assignment-selected language. Assess readable language, technical claims and privacy as well as structure. Record each language separately; no accepted generation language is claimed now. Numerical acceptance thresholds/repeatability and measured input/workload limits remain open. |

Prior homework trials are **failed quality evidence**, not a pass for this design.
The latest personal probe matched 15/15 supplied quotes but missed genuine errors
and invented gaps. Lecturer review is a safety/control step, not proof that the
engine meets quality targets. No new model run, website test or acceptance result
was produced while adding this strategy. See [tools summary](local-ai-feasibility.md#current-tools-and-evidence-index)
for repository versus local-only evidence availability.

## Historical execution records

Entries below are dated stage evidence. Statements that an engine was disabled
or a workflow unimplemented describe that historical stage, not today's runtime.
Use the current architecture and strategy above for the implemented boundary.

## Unit E — Local Transcription — 2026-11-08

- **106 website tests passed**, file-backed SQLite, 48.750 s, no skips; 32 focused video/transcription checks passed in 15.381 s. Tests inject ASR fixtures only; actual GPU evidence is separate below.
- **10 JavaScript tests passed**, fake DOM, not a browser. New cases cover real-stage labels, audio deletion state, successful transcript link visibility and expiry hiding.
- Tests cover normal transcription-before-WAV-cleanup, private escaped full text, mixed-language markup, no text in polling JSON, same-course other Lecturer/student/anonymous denial, revoked/demoted owner, mismatched parent URLs, exact seven-day expiry/HTTP 410 and content purge, cleanup, model failure, invalid output, missing runtime/no download, original shared deadline and legacy extraction-only behavior. Existing timeout/stop/watchdog tests cover shared worker recovery; no real GPU hard-kill test is claimed.
- Two **new actual sample uploads**, real offline CUDA float16 medium inference: SHORT detected en, load 2.837 s, ASR 12.439 s, total 26.666 s; STATIC detected he, load 1.578 s, ASR 190.870 s, total 195.856 s. WAV/pending JSON absent after both. Both owner-authenticated detail/full-text responses returned HTTP 200 and included the complete escaped text. This used the upload service, real separate worker and in-process Django requests, not browser automation or a new browser-upload report.
- The user reported difficulty preparing a reliable listening-only reference and approved continuing functional checks. **Word accuracy and English programming-term accuracy have not been verified against manual transcription.** No verified word examples or WER are claimed. Mixed-language visual layout still needs user/browser inspection.
- Summary remains disabled. No API calls, model downloads, installations or billing occurred in this stage. The 13 pre-existing Gemini experiment changes remain separate/unchanged. See [local-transcription.md](local-transcription.md) for exact local versions, privacy/expiry, timing boundaries and manual steps.

## Unit D — Video Infrastructure — 2026-11-08

Implemented boundary: private upload, queued persistent state, real MP4 checks
and audio extraction. No transcription/summarization/model request, download,
billing or agent-run browser test occurred. Gemini experiment files were left unchanged.

| Executed check | Observed result |
|---|---|
| Focused video suite, file-backed SQLite | **20 passed**, 5.343 s, no skips |
| Full website suite, file-backed SQLite | **94 passed**, 44.669 s, no skips: previous 74 plus 20 video tests |
| `node --test tests_js/*.test.cjs` | **8 passed**, including 3 video polling/state tests; fake DOM, not a browser |
| Dependency installation | Only PyAV 16.0.0 added to the website .venv; 32.3 MB official wheel; no model/driver/system change |
| Migration 0004 / dependency / schema checks | Local migration applied; no broken requirements or pending migration changes |
| Actual existing MP4 clips | Both within 240 s and 200,000,000 bytes; real extraction completed via local queued jobs and separate worker commands; temporary WAV absent after each |

Sample evidence (not an AI benchmark): SHORT-EXPLAIN.mp4, 14,645,300 bytes,
56.74957 s video, 56.74956 s extracted audio, 4.43773 s worker elapsed;
STATIC-EXPLNATION.mp4, 10,477,365 bytes, 235.28780 s video, 235.28781 s extracted
audio, 2.919206 s worker elapsed. Elapsed times include startup and integrity
decoding; neither predicts AI latency/quality. Originals were opened read-only;
private uploaded copies and run metadata are ignored by Git.

### Actual assertions

- Real generated MP4 audio/video data, streaming save, queued POST redirect and
  use of another site page; actual worker extraction; verified 16-kHz mono PCM
  WAV samples and deletion before success.
- Corrupt bytes, no-audio video and audio-only container rejected by worker with
  persisted Checking video failure stage/code. Extension and multi-file forms
  rejected; MIME/extension alone never establish successful decoding.
- Size is 200,000,000 bytes. Declared 200,000,001 rejects before saving; actual
  multipart/copy byte boundaries are exercised with lowered test limits rather
  than allocating a 200-MB fixture. Both existing real clips pass the actual cap.
- Duration enforcement uses real media under lowered test limits; exact measured
  duration accepted, just-above boundary rejected. Both supplied clips pass the
  production 240-second cap; no full 241-second fixture was generated.
- Owner-only HTML/JSON including same-course second Lecturer denial, students,
  foreign/mismatched paths, anonymous login, CSRF, demotion and removed membership.
  Queued role revocation prevents decoding. Private paths do not appear in pages.
- Queue wait is distinct from processing time; one-hour-old queue entry still
  gets a fresh worker-start budget. Single-worker OS lock and FIFO are checked.
- Actual subprocess termination under a shortened test timeout, plus persisted
  started-at >600-second recovery; no 10-minute wall-clock wait is claimed.
- Graceful stop and stale heartbeat recovery; actual hard termination of a test
  coordinator, parent-death watchdog/decoder-lock release, failed persisted state
  and partial-WAV removal. Test subprocess helpers are test-only, not runtime modes.
- Independent maintenance command, expired queued-source cleanup, orphan WAV and
  old multipart cleanup, fixed-path/traversal protection and unrelated-file safety.
- Separate disabled transcription/summary contracts, neither invoked by extraction.
  No synthetic text is presented as actual AI processing.

The local worker and separate maintenance process were started for current demo
use; the web server remains 127.0.0.1:8000. They must be restarted after a machine
restart. Maintenance is required independently of the worker for 24-hour cleanup;
offline/stopped services cannot guarantee physical deletion on schedule. See
[video-processing.md](video-processing.md) for commands and the early-purge margin.

Agent-run browser interactions, phone upload/layout, class load, pathological
codecs and real AI quality are not verified here. The previously denied browser-
origin gate was not bypassed. The later user-reported manual result below is
separate evidence for its reported path only. Full AS-04/AC-04 remains incomplete;
this stage establishes extraction infrastructure.

### Unit D pre-commit verification

After recording the user report, the full suite passed **94 tests**, 45.239 s,
on isolated file-backed SQLite, with no skips. All **8 JavaScript logic tests**
passed. Django check, migration drift, dependency consistency and diff whitespace
checks passed. No AI request or billing action was part of this verification.

### User-reported manual video check — 2026-11-08

The user reported testing SHORT-EXPLAIN.mp4 in the browser. After starting the
worker, the already queued task changed to **Audio extraction completed**.
The UI displayed **118.2 seconds waiting**, **4.5 seconds processing**, and
**56.75 seconds of audio**. The site reported that temporary audio had been
deleted. These are user-reported browser observations, not actions directly
performed or observed by the agent; the UI deletion notice is not a separate
user inspection of files on disk.

This report does not establish other media cases, phone layout, permissions,
recovery, timeouts, 24-hour expiry or AI quality; their specific automated evidence
and remaining limitations are recorded separately. **Transcription and summaries
remain disabled and unverified.** No additional AI request is implied by this check.

Date: 2026-11-05. Environment: Windows 64-bit, Python 3.12.14, Django 5.2.19,
SQLite. The historical Unit A section below covers the shared foundation; the Unit B section records later attendance/comments checks. It does not
mark any five-capability acceptance check AC-01 through AC-07 as passed.

## Executed checks

| Check | Observed result |
|---|---|
| Install website dependencies in separate `.venv` | Django 5.2.19, asgiref 3.13.0, sqlparse 0.6.1, tzdata 2026.6 installed |
| `python manage.py check` | No issues |
| `python manage.py migrate` | Django/auth/session and classroom initial migrations applied to local SQLite |
| `python manage.py seed_demo` | Two courses, six random-password accounts, seven memberships, four initial meetings created; no passwords printed |
| `python manage.py test --verbosity 2` | **24 tests passed**, 8.434 seconds; isolated in-memory SQLite test database |
| Pre-commit test rerun after replacing literal test credentials with runtime-generated values | **24 tests passed**, 8.261 seconds; system check passed and no migration drift |
| `python manage.py makemigrations --check --dry-run` | No changes detected |
| `python -m pip check` / `findstatic css/site.css` | No dependency conflicts; stylesheet discovered |
| Documentation consistency | 60 unique register IDs, 27 local links; original assignment-source rows and AC-01 through AC-07 unchanged |
| Runtime fixture counts and Git hygiene | Six users, two courses, seven memberships, four meetings; no generated demo/signing/API secret found in Git-visible files; runtime directories ignored |

The tests use Django's request client, not a browser. CSRF rejection is
explicitly tested using `Client(enforce_csrf_checks=True)`; default client
behavior alone would not establish CSRF coverage.

## Class-aware coverage

| Component | Actual assertions |
|---|---|
| Django auth views and middleware | Valid/invalid/inactive login; safe handling of external `next`; POST-only logout clears the session; anonymous requests redirect; CSRF enforced for login/logout/writes |
| Course/Membership | Lists expose only memberships; multiple courses supported; one account can be lecturer in one course and student in another; no global staff/superuser bypass; uniqueness and role database constraints |
| Current-membership lookup | Foreign direct URLs denied; membership deletion takes effect on next request; demotion prevents submission of a previously accessible edit form |
| Meeting lookup and view | Meeting ID must match authorized parent course; missing IDs return 404; read routes reject POST; cross-course edit does not modify the row |
| MeetingForm / management view | Authorized create/edit persists; posted course cannot change ownership; student GET/POST denied even with forged role/user fields; invalid date, blank/overlong title do not save; timezone-aware date stored |
| Templates | Forbidden data absent from denied responses; student management buttons absent; description HTML escaped; empty membership state displayed |
| seed_demo command | Rerun preserves password hashes and initial fixture counts; mixed-role/no-membership cases created; generated passwords are not printed; unrelated existing account is not overwritten |

Test fixtures generate synthetic passwords at runtime; no usable test password
is embedded in source. Actual
generated demo passwords, signing keys and the existing Gemini key are not
source fixtures and remain ignored local files.

## User-reported manual browser checks

On 2026-11-05, the user reported performing these checks manually in a browser:

| Check reported by the user | Reported result |
|---|---|
| Sign in and view courses and course roles | Worked |
| Create a meeting | Worked |
| Edit a meeting description and refresh the page | Saved description persisted after refresh |
| View the site with a Student role | Creation/edit buttons were absent |

These are **user-reported results**, not browser actions performed or directly
observed by the agent. Browser/device/version and viewport were not specified.
They do not establish a phone test, responsive-layout acceptance, or rejection
of unauthorized direct GET/POST requests. Hidden buttons are not an access
control: the separate automated server permission tests above provide that
evidence.

## Remaining UI verification limitation

An attempt to open `http://127.0.0.1:8000` with browser automation was rejected
by the browser origin approval gate. No alternative browser, raw browser
automation or indirect workaround was used. No agent-run browser interaction
or screenshot check passed. The later user-reported functional browser checks
are recorded separately above. **Viewport-specific rendering and real-phone
usability remain unverified.** This limitation does not invalidate the
executed in-process server permission tests.

Additional manual browser checklist, not reported as completed:

1. At desktop and approximately 375-pixel widths, sign in and check for overflow,
   keyboard focus, readable labels, button reachability and date input behavior.
2. As student_alex, see DEMO-CS101 only; confirm direct beta URLs are denied.
3. As lecturer_alpha, create/edit a CS101 meeting; view SE201 as Student and
   verify its management buttons/routes are denied.
4. As student_casey, see both courses; as observer, see the empty state.
5. Sign out and verify protected pages require sign-in again.

## Unverified and deferred

- Actual classroom user count and SQLite capacity. Unit B verifies only two simultaneous requests, not classroom load.
- Hosting/HTTPS/phone access; current server listens only on loopback.
- Production hardening, login throttling, retention/deletion and real identities.
- Browser/phone attendance scanning, XLSX UI/download and live-update usability; the server paths are covered under Unit B below. Polls, video summaries and homework feedback remain unimplemented website features.
- Offline interpretation and university-network checks.
- AI providers/adapters and AI correctness. Existing feasibility reports remain
  separate evidence; no new AI request occurred during this unit.

The foundation is a meaningful commit unit, with user-reported manual checks
and remaining UI limitations explicitly separated from server test evidence.

## Unit B — Executed Attendance and Connected-Request Checks

Date: 2026-11-05. Same Windows/Python/Django environment, with qrcode 8.2 and
openpyxl 3.1.5. Tests use generated synthetic users/data and credentials;
the development database, real passwords, media and AI keys are not test inputs.

| Check | Observed result |
|---|---|
| Full Django suite with file-backed SQLite test DB | **48 passed**, 38.411 seconds, no skips. Includes 24 Unit A tests, 21 Unit B functional tests and 3 concurrency tests. |
| `node --test tests_js/participation.test.cjs` | **3 passed**: visible-page polling pause/resume and 5-second schedule; safe text rendering and QR boundary refresh; scan form submission. Logic-only fake DOM/timers, no browser. |
| Pre-commit rerun after shortening the request notice | **48 passed**, 39.928 seconds on file-backed SQLite; **3 JavaScript logic tests passed**. |
| `manage.py check` | No issues |
| `manage.py makemigrations --check --dry-run` | No changes detected |
| `python -m pip check` | No broken requirements |
| Local migration 0002 | Applied successfully to ignored development SQLite; demo seeding was not rerun. |

The first test run found missing course context in the forbidden-response
template. That caused 500 errors instead of the intended 403; it was fixed
and the full suite rerun successfully. No failed run is treated as a pass.

### Actual assertions

- Initial 300-second and subsequent 120-second windows; active-open idempotency;
  automatic-expiry reopening and invalidation of all explicitly closed codes.
- Stable QR tokens within 30-second buckets, rotation at the boundary, valid
  overlap through 44.999999 seconds, rejection at 45 seconds and at window end;
  future/tampered/malformed/wrong-meeting codes are rejected.
- GET scan does not register; CSRF-protected POST does. Login preserves the
  attendance continuation. Expiry during login, between GET and POST, or closure
  after GET requires a new scan. Membership/role is freshly checked.
- Student/meeting uniqueness, preserved first timestamp/window/status, and exact
  Registered in an additional window label. Two requests from the same student
  create one record; two different students create two. Concurrent opens create
  one window. These tests use a barrier, threads and separate database connections.
- Lecturer-only roster/state/export/window actions; students denied management;
  nonmembers/mismatched parent courses denied; per-course roles and removed or
  changed memberships enforced. HTML/JSON are not substitutes for server checks.
- Real XLSX bytes loaded with openpyxl: expected fields/current-student roster,
  additional-window label, unchanged old snapshot after new registration, no
  write-back on editing, and leading '=' in a display name stored as text.
- Comment/suggestion history persistence and own-only student access; lecturer
  all-meeting feed; 1/1000-character Unicode boundaries after trim, blank/1001
  rejection, invalid type rejection, escaped script text and duplicate-form
  submission deduplication. CSRF rejection and database-failure reporting tested.

### Reproduce without touching the development database

```powershell
$env:DJANGO_TEST_SQLITE_NAME = Join-Path (Get-Location) ('.local/unit-b-test-' + [guid]::NewGuid().ToString('N') + '.sqlite3')
.\.venv\Scripts\python.exe manage.py test --noinput
Remove-Item Env:DJANGO_TEST_SQLITE_NAME
node --test tests_js/participation.test.cjs
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pip check
```

The generated path is an isolated temporary test database managed by Django.
Without the environment variable, regular tests use in-memory SQLite and the
three real-connection concurrency tests explicitly skip; that run cannot be
reported as equivalent concurrency evidence. The file-backed suite above ran
all three. Two-request success does not establish classroom capacity.

### User-reported Unit B manual checks

The user reported the following checks; they were not performed or directly
observed by the agent:

| Reported action | Reported result |
|---|---|
| Manual QR check | The user reported checking the QR. Device, exact steps and successful attendance registration were not specified; no additional QR scenario is inferred. |
| Submit a comment as student_alex and view it as lecturer_alpha in the same meeting | The comment appeared to the lecturer without a manual refresh. |

These reports do not establish a successful phone test, an exact five-second
latency, login continuation, expiry handling, additional windows, duplicate
prevention, XLSX correctness, server authorization or classroom load. Server
checks above remain separate evidence for their specific assertions.

No agent-run Unit B browser, real-phone, native-camera scan or responsive
screenshot check passed. JavaScript logic tests are not browser tests. The prior
browser origin rejection was not bypassed. Existing Unit A user-reported checks
above remain separate historical evidence.

Use [phone-testing.md](phone-testing.md) for desktop/two-account and future
private-LAN phone instructions. Current binding and ALLOWED_HOSTS remain
loopback-only; no firewall/network changes were made. Offline meaning, lecturer
acceptance of attendance automatically/online-offline, university-network
feasibility, retention, production security and classroom load remain open.
No AI experiment or AI website feature was started in Unit B.

## Unit C — Executed Poll Lifecycle Checks

Date: 2026-11-05. Existing Windows/Python/Django environment, no new dependency
or AI request. Real generation is disabled/unverified; tests use synthetic data
and a fake generator defined only in the test module. Local demo fixtures are
separate approved non-AI data, not evidence of generation or model quality.

| Check | Observed result |
|---|---|
| First complete website suite after lifecycle implementation | 72 tests passed, 37.926 s, isolated file-backed SQLite |
| Final complete suite after adding failed-vote save reporting | **73 tests passed**, 38.362 s, no skips; 48 earlier foundation/participation tests plus 25 poll tests |
| Targeted rerun after a small active-poll message adjustment | 2 disclosure/lifecycle tests passed, 0.107 s; no new provider calls |
| Poll test breakdown | 21 functional/server/command tests, 4 real separate-connection concurrency tests |
| `node --test tests_js/*.test.cjs` | **5 passed**: 3 participation tests plus 2 poll tests for safe live results, visibility pause/resume and stale-action handling |
| Django check / migration drift / dependency consistency | No issues, no migration changes, no broken requirements |
| Local migration 0003 | Applied successfully to ignored development SQLite |
| `seed_demo_polls --language he` | Created Draft poll 1 (comprehension) and Draft poll 2 (opinion), meeting 5 in DEMO-CS101; explicitly not generated by AI; no account reseeding, publication or votes |

### Actual server assertions

- Disabled normal generation reports unavailable and creates no placeholder.
  The only real runtime factory returns DisabledPollGenerator. Explicit test
  injection exercises valid Hebrew/English responses for both types, malformed
  output, provider exceptions, and revoked lecturer membership after generation.
  These tests are not real generation/language-quality evidence.
- Material lengths 1/6000 accepted at the input-validation boundary, 6001
  rejected on the server, including Unicode and whitespace-only cases. A valid
  request still returns 503 because generation is disabled, not a saved draft.
- Draft-only edits to question, four distinct options, comprehension key and
  explanation; invalid/duplicate/blank content rejected. Stale versions reject
  lost edits and publication of content not reviewed by that page. Opinion
  drafts reject forged answer/explanation fields.
- Drafts invisible to students; course/membership/role enforcement for direct
  HTML and JSON routes, mismatched parents, role changes/revocation, lecturer
  voting rejection, anonymous login redirects, CSRF and POST-only transitions.
- Active student HTML/JSON excludes the comprehension key/explanation and all
  counts/distributions. Closed comprehension reveals approved key/explanation;
  opinion results never designate/evaluate correctness. Student payloads contain
  no respondent identities; demo provenance and escaping are tested.
- One active poll per meeting, manual close, idempotent repeated close, no
  reopening or published-content editing, and another poll after closure.
  One final vote per student with invalid/multi-value choices and changes
  rejected. DB uniqueness/check constraints are exercised directly.
- Zero-safe counts/percentages and a known two-vote 50/50 result. Database-busy
  vote failure reports unconfirmed save without persisting a vote or leaking key.
- Separate-connection SQLite races: same student/different options yields one
  accepted vote and one conflict; two students both count; two simultaneous
  publications yield one active poll; voting competing with closure either
  commits before closure or is rejected. Further votes after close are rejected.
  This is two-request correctness evidence, not a classroom capacity benchmark.
- Demo command labels, two types/languages, repeat-run preservation of edited
  content and active status, explicit new-set behavior, and missing-target error.
  The command never calls a fake/real model or publishes its drafts.

### Reproduction and manual boundary

Use the file-backed test database command shown under Unit B above, followed
by `node --test tests_js/*.test.cjs`; this runs all current website tests.
Ordinary in-memory test runs explicitly skip real-connection races and must
not be reported as the complete concurrency run.

The updated development server is loopback-only. Agent-run browser/native-camera,
phone layout and live visible-tab interactions for polls were **not** performed;
the prior browser-origin gate was not bypassed. Subsequent user-reported manual poll results are recorded below; unreported scenarios remain unverified. JS tests use fake DOM/timers and do not establish browser
rendering or timing. See [poll manual checks](poll-implementation-plan.md) for
lecturer_alpha/student_alex steps. Existing Unit A/B user reports are preserved
separately and are not repurposed as Unit C evidence.

Full AS-03/AC-03 acceptance remains incomplete until real generation, quality,
browser/phone and intended classroom evidence exists. No AI experiment, billing or network/firewall change occurred during implementation.

### Poll radio-selection follow-up — 2026-11-05

**User-reported defect:** as student_alex on an active poll, clicking an answer
showed no visual selection. The agent did not reproduce a browser click or
observe the original screen, so the report is not assigned a proven sole cause.

Read-only inspection of the actual Django-rendered VoteForm showed four native
radios sharing option_index, unique IDs and correctly linked labels. No student
poll script or automatic submission handler was present. The widget's group
CSS class poll-choices was also propagated to each radio, unintentionally applying
grid/margins to the control. There was no explicit selected-card style. These
are observed markup/style defects, not evidence of a broken label/POST link.

Fix: render a semantic fieldset/legend with four explicit input/label pairs;
separate group, native radio and label classes. Checked state styles the adjacent
label with border/background and a Selected text marker; focus-visible outlines
the option card. Native radio appearance and accent color are explicit, with a
forced-colors fallback. No click handler or automatic POST was added. Guidance
states that choosing is provisional until Submit final response is pressed.

Executed verification: **26 poll tests passed**, 1.140 s, with file-backed SQLite
and no skips, including the existing four concurrency tests. A new regression
parses the real student HTML and verifies unique for/id linkage, four same-name
radio values, no initial selection, no group class on inputs, a separate submit
button, no inline event handlers and no student polling script. GET saves no vote;
POST of a rendered option stores its index and later changes remain rejected.
Django check and diff whitespace check passed. This was a focused poll-suite run,
not a rerun of the entire 73-test prior suite; the new total is not claimed passed.

**Browser limitation:** the previously denied localhost browser origin and Chrome
automation approval were not bypassed or treated as granted. No agent browser,
pointer interaction, computed-style, screenshot, keyboard interaction or phone
check was completed. Parser/server checks establish wiring and persistence, not
actual native selection, focus appearance or visual correctness in the browser.

Additional manual coverage checklist (the limited later user report does not verify every step): hard-refresh an active, unvoted student poll; click
both the radio and the option text. Expect exactly one checked control and one
Selected card; choose another and confirm the marker moves without submitting.
Use Tab, arrow keys and Space to check visible focus/native group behavior.
Before pressing Submit final response, no response should be counted. After
submission the chosen value should count once and cannot be changed.


### User-reported poll manual results — before Unit C commit

The user reported these successful manual checks. They were not performed or
directly observed by the agent; browser/device/viewport details were not supplied.

| Reported check | User-reported result |
|---|---|
| Answer selection after the radio/selection fix | Selection is displayed correctly. |
| Active opinion poll, lecturer versus student visibility | Lecturer sees results before closure; student does not. |
| Opinion poll after closure | Both see the response distribution, without a correct-answer designation or grade. |

This report does not verify keyboard focus/navigation, separate radio versus
label click behavior, phone layout, comprehension-answer disclosure, concurrent
writes, every permission boundary or real AI generation. Server test evidence
for specific assertions remains separate. General visual-design improvements
are deferred to later work. Real AI generation remains disabled and unverified.


### Unit C pre-commit verification

After the selection fix and the user-reported opinion-poll checks were documented,
the complete website suite passed **74 tests**, 39.409 s, on isolated file-backed
SQLite with no skips. All **5 JavaScript logic tests** passed. Django check,
migration drift, dependency consistency and diff whitespace checks passed.
Real AI generation remains disabled/unverified; no AI request was sent. General
visual redesign is deferred. User manual observations and unverified keyboard,
phone and other scenarios remain distinguished above.

## Transcript readability correction — 2026-11-08

User feedback on the existing STATIC task prompted a presentation-only correction. Stored words/order are unchanged. Paragraphs use saved segment boundaries, >=0.8-second gaps, roughly 25-second groups or a 360-character target (individual segments stay intact). The renderer falls back to exact stored text if segment reconstruction differs. A constrained reading width, mobile padding, explicit Hebrew RTL/English LTR and isolated Latin phrases keep mixed text such as New Car in its original order. The teacher-facing explanation is now one sentence in the English UI; GPU/loading/worker details remain in technical documentation.

Executed: **15 focused transcription/display tests passed**, 3.711 s. Existing authorization/expiry/cleanup tests remained green. Actual saved tasks returned owner-authenticated HTTP 200: STATIC now has 13 reading paragraphs; SHORT has 4. HTML text extraction (with paragraph separators) matched every original word and punctuation in order; database text hashes remained unchanged. The existing STATIC New Car phrase is enclosed in a left-to-right bdi element inside RTL text. UTF-8 response decoding was strict and the document declares UTF-8. These are server-response/markup checks, not visual browser/phone verification; the previously denied browser gate was not bypassed.

Encoding/content audit: the saved direct model segment text, the full database transcript and the HTML text all contain the same **four U+FFFD replacement characters** and **one dishwasher**. The segment 57.72–64.60 seconds starts with two replacement characters; others occur in 82.16–86.52 and 86.52–89.48. Dishwasher occurs in 77.56–82.16. The affected segment strings match the full stored text and response text exactly. The worker constructs full text by joining original model segments; JSON file IO uses explicit UTF-8 and strict decoding. No replacement-character decoding is performed by the application. Thus no application transport/render encoding fault was found, and no guessed replacement or word rewrite was applied.

Evidence limitation: the original temporary model-result JSON from these jobs was intentionally deleted. This comparison uses the original model segment strings persisted losslessly in VideoJob, not an independent retained pre-database file. The earlier independent local-experiment raw STATIC result also contains U+FFFD, but it is a different run and contains no dishwasher; it is not evidence that the current sentence was identical across runs. Word/term accuracy (including dishwasher) remains pending comparison with the source audio. No new inference/API request was performed for this correction.

## Focused STATIC quality probe — 2026-11-08

Executed two genuine local CUDA medium transcriptions of the same 00:55–01:35 audio copy: automatic language (detected he), then fixed he, task transcribe unchanged. Roughly 34.7/34.5 s, one shared model load. Outputs differ slightly; both omit the prior dishwasher/U+FFFD artifacts on this cropped context but still contain suspicious words/unclear meaning. Human-reference accuracy/code terminology remain unverified; cropping prevents attributing improvements over the full-video run to the language argument. The existing task text was not replaced. No other local ASR model was found in inspected model/cache locations. A roughly 1.63-GB turbo download is proposed, not performed. Experiment findings and limits: [static-asr-quality.md](static-asr-quality.md). No application code changed in this probe; no website regression run is claimed for it.

## Full STATIC turbo comparison — 2026-11-08

Following explicit download approval, downloaded 1,621,665,983 bytes of public CTranslate2 checkpoint/config/tokenizer files from dropbox-dash/faster-whisper-large-v3-turbo, pinned revision 0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf. Actual full-recording CUDA float16 transcribe succeeded offline with automatic Hebrew detection, using the same ASR arguments as the existing full-medium job. Model load 1.822 s; transcription 54.893 s versus existing medium 190.870 s. Sampled maximum process RSS 1.301 GiB, total GPU-used memory 2,723 MiB; roughly one-second sampling is not an exact peak, GPU value includes other device users. No API/paid inference or application provider change.

Raw full output/model manifest/audio are stored separately under ignored .ai-lab/results/static-turbo; existing website transcript/segments and active medium setting were asserted unchanged. The source-timestamp comparison for 00:55–01:35 is described in [static-turbo-quality.md](static-turbo-quality.md), with the 01:17.560–01:22.160 listening window identified. Turbo is more readable but still has an unclear negation around 00:58–01:02. Human-source accuracy, code-identifier fidelity and the belongs/does-not-belong distinction in that unclear region remain unverified. No WER/quality pass is claimed. The 13 outstanding Gemini files were unchanged. Website regression tests were not rerun because only isolated experiment code/documentation changed in this step.

## Full SHORT-EXPLAIN turbo comparison — 2026-11-08

Actual full-English turbo transcription completed locally on CUDA float16 using the existing verified model, no download/network request. Same arguments as full medium, automatic en detection. Turbo load 1.749 s / transcription 4.824 s versus saved medium 2.837 s / 12.439 s. Sampled maximum process RSS 1.385 GiB and total GPU-used memory 2,715 MiB (sampling and shared-device limitations apply). Both inheritance excerpts retain class/boat/vehicle/inheritance and coherent high-level meaning. Turbo's drop an anchor differs from medium's drop and anchor; this is not verified against human listening. Full outputs are very similar, with no reference-based accuracy/WER claim. Existing website transcript/segments/medium setting and Gemini files remained unchanged. Raw results are ignored local artifacts; comparison findings and reproducibility are in [short-turbo-quality.md](short-turbo-quality.md). No website regression suite was run for this isolated experiment.

## Approved turbo default and normal STATIC upload — 2026-11-08

Executed **113 website tests passed**, file-backed SQLite, 52.562 s, no skips. New checks reject missing/modified checkpoint files, reject another model/revision or unverified result, assert requested/actual identity persistence, exercise unavailable-turbo failure with no fallback/subprocess, and retain loaded identity on later inference failure. Existing privacy/expiry/cleanup/legacy/display tests remain green. The earlier focused set had 37 passed before the final two failure/provenance tests; the full 113-test run includes both additions.

Actual new STATIC upload used the normal authenticated CSRF-enforced multipart POST view/form/upload middleware and real separate background worker, not the standalone experiment or a fake ASR. Upload returned 302 to a queued task. This was an in-process Django client request, not agent-operated browser automation. User manual browser acceptance is pending.

- Course DEMO-CS101, meeting **Test Meeting** (meeting 5), owner lecturer_alpha.
- Job **489f75a2-bca3-4c0a-a9fc-3cc602636ce5**.
- Actual persisted model dropbox-dash/faster-whisper-large-v3-turbo, revision 0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf, sha256_verified=true, CUDA float16.
- Model load **1.574 s**, transcription **54.555 s**, total worker processing **60.549 s**; automatic detected language he. Model-file hashing/decoder/startup/cleanup share the total budget, so total exceeds load + ASR.
- Owner full-transcript page returned **HTTP 200**; parsed reading text matched all stored words/punctuation in order. Actual audio.wav and transcript.pending.json were absent and audio removal was recorded. The page uses the existing paragraph/RTL/Latin-isolation rendering.
- All six pre-existing tasks retained identical transcript hashes, timed segments and asr_metadata. No retranscription or metadata backfill was applied to old jobs. Gemini-file hashes remained unchanged.

Task page: /courses/1/meetings/5/videos/489f75a2-bca3-4c0a-a9fc-3cc602636ce5/ ; full text: append transcript/ . The loopback server and single worker were restarted with current settings; independent maintenance remains running. No new model downloads, API calls, payment, commit or push occurred in this switch stage. Hebrew readability is improved, but meaning/negation, word accuracy and exact technical identifiers remain unverified against a manual source reference (see static-turbo-quality.md); no quality acceptance or summary capability is claimed. The subsequent user-reported browser review is recorded below.

## User-reported STATIC browser review and stage completion — 2026-11-08

**Provenance: reported by the user, not an agent-executed browser test.** The user opened the full STATIC transcript on the website. The explanation of variables belonging to an object versus a shared static variable was understandable. Some words remained garbled, and part of a sentence containing a negation remained unclear even when listening to the recording. No word-by-word accuracy measurement was performed.

This supports usability/understandability of that reviewed result, not verbatim fidelity, exact code-identifier accuracy, a quantified accuracy score or a phone/layout acceptance pass. The user approved completing the local transcription stage with large-v3-turbo as the new-upload default. Summary generation remains a separate, disabled stage. Existing transcripts remain unchanged.

The reading page now uses the heading **Automatic transcript** and the warning **Some words and code terms may be transcribed incorrectly.** It retains the short speech-only explanation. Server template assertions cover the heading, warning and speech-only notice; raw transcript outputs remain local/ignored and are not published in the quality reports.

Final pre-commit verification for this completed stage: **113 server tests passed** in 49.785 s using file-backed SQLite; **10 JavaScript tests passed** in the fake-DOM harness. Migration drift check reported no changes; dependency check reported no broken requirements. These checks include the final Automatic transcript heading and warning. Documentation links and the explicit publication file list were checked; raw transcript tables were removed from published quality reports while the original local artifacts remain unchanged.

## Local summary feasibility on saved turbo transcripts — 2026-11-08

Executed two real local Qwen3 8B (Q4_K_M, Ollama 0.40.14) CLI generations from saved full STATIC/SHORT turbo transcripts; no retranscription/download/external-provider request. Thinking off, JSON paragraph + 3–5 points, source-only/negation/inheritance/omit-unclear instructions, one call each/no retries. Both format checks passed: STATIC 4 points, SHORT 3. Wall times 10.098 s and 2.863 s; first model load 4.919 s versus 0.004 s warm reuse. Output-generation durations 4.182/2.510 s. Context/CUDA use confirmed in local logs; no new peak-memory measurement is claimed.

Claim-by-claim review against ASR input found the per-object versus shared-static distinction and boat-inherits-vehicle direction preserved. STATIC nevertheless overstates coverage of static functions and adds class-ownership/only-once inferences beyond explicit wording. SHORT claims were supported by its transcript. This is not recording-reference accuracy verification. Raw outputs and inputs remain ignored/local; full review and a proposed controlled draft integration are in [local-summary-feasibility.md](local-summary-feasibility.md). Website summarization remains disabled; no feature implementation or website regression run occurred. Gemini experiment files remain separate/unchanged. No commit/push.

## Initial automatic local summaries — 2026-11-08

Implemented the approved initial local Qwen3 8B stage (D-42/D-43). **126 server tests passed** in 52.922 s on file-backed SQLite, no skips; **12 JavaScript tests passed**. Migration 0006 applied; schema drift check passed. Tests use injected engines, except an ordinary-Python owned-process-tree test; real-model evidence is separate below.

Automated coverage includes transcript persistence before summary invocation, WAV removal before summary, shared original deadline, summary failure/timeout/interruption preserving transcript access, invalid output and wrong-language/script rejection, safe unexpected-error messages, legacy task preservation, actual model metadata, owner-only escaped summary HTML and direct URLs/status, current membership/revocation, exact expiry and cleanup of both text products, private IPC removal, and Windows owned-grandchild termination on process-tree close. JavaScript covers one reload for ready server-rendered summary, terminal polling stop and a retained transcript link on failure. An initial reload test exposed a double reload and passed after a one-shot guard. No real GPU hard-crash or browser/phone run is claimed.

Real saved-input prompt checks used unchanged full turbo transcripts and the installed model through the production adapter. Initial lecture-grounding-v2 still falsely attributed static-function instruction and reconstructed an uncertain identifier. A bounded v3 refinement generated valid paragraph/point structures in Hebrew/English: STATIC 10.382 s wall, 7.607 s model request; SHORT 8.719 s wall, 5.943 s model request. These cold per-job services include loading, unlike the earlier warm CLI experiment. In v3, STATIC did NOT claim static functions were explained; SHORT retained boat inheriting from vehicle. STATIC still inferred class ownership/access through the class, and not all points were example-scoped. No semantic accuracy pass is claimed despite the prompt. Raw outputs/prompts remain ignored local artifacts and are displayed to the user without editing.

Real full-route uploads (in-process authenticated CSRF multipart request, actual separate worker):

| Clip / job | Observed result |
|---|---|
| STATIC / 03b0bfec-f199-4aa1-9dfc-0e26eb2225f9 | ASR 57.276 s; model-summary request 7.745 s; total 77.416 s. Unexpected Korean word in summary prompted a new language validation rule. The initially accepted invalid output was snapshotted locally then explicitly invalidated on this new development acceptance task; task now shows summary_language failure, with the completed transcript retained. No silent correction/retranslation occurred. |
| SHORT / dd68e11b-2d34-40ae-9fb5-9bca05e14c7b | ASR 4.835 s; model-summary request 5.972 s; total 21.985 s. Summary completed; generated English output matches the v3 saved-input check and preserves inheritance direction. |

An additional SHORT upload was necessary after the STATIC failure to verify the successful full path. Both belong to lecturer_alpha, DEMO-CS101 / Test Meeting. Owner task/full-transcript requests returned HTTP 200; successful summary paragraph/points were present as escaped text, and rejected STATIC summary was absent with a clear reason. Actual WAV and transcript/summary pending/input files were absent. No per-job Ollama/model process remained afterward. Seven old task transcripts/segments/asr_metadata were verified unchanged; all Gemini file hashes stayed unchanged. The existing summary fixture language tests and direct-page privacy tests are not replaced by this owner-only real sample check.

The original ten-minute worker-start limit covers all phases; queue wait stays separate. Summaries expire no later than their source transcript (max seven days), with direct access hiding content at expiry and maintenance clearing it. This does not guarantee physical deletion when the machine/maintenance is stopped. User browser review and recording-grounded word/summary fidelity remain open. Full behavior/setup/limitations: [local-summaries.md](local-summaries.md).

One intermediate test invocation encountered a Windows lock because a preceding test run still owned its SQLite test file. After the previous run completed, the final suite used a separate file and passed; no production database was deleted. No new dependencies/models, external-provider inference, billing, commit or push occurred in this stage.

## User-reported SHORT summary interface review — 2026-11-08

**Provenance: a manual interface check reported by the user, not agent-executed browser automation.** Signed in as lecturer_alpha, the user reviewed SHORT task dd68e11b-2d34-40ae-9fb5-9bca05e14c7b. The summary paragraph and key points were readable, and the link opened the full transcript of the same video. This verifies the reported display/navigation path only; it does not establish phone layout, other users' permissions, source-audio accuracy, or a quantified summary-quality score.

STATIC evidence remains distinct: the saved-transcript v3 summary check succeeded structurally and did not attribute static-function coverage, with grounding limitations recorded above. The normal MP4-upload run produced an invalid-language summary and was marked summary_language failure; its full transcript remained accessible. The SHORT interface report does not convert that STATIC upload into a successful summary run.

Language regression coverage explicitly accepts a Hebrew paragraph and points containing English code terms **static** and **Car**, with exact generated strings retained. The unexpected-script rejection check remains separate, so rejecting the Korean-script case does not require rejecting ordinary Hebrew/English technical mixtures.

Final pre-commit verification after the user report and mixed-language regression addition: **127 server tests passed** in 53.362 s using file-backed SQLite, no skips; **12 JavaScript tests passed**. The new acceptance test covers a Hebrew summary paragraph and points with static and Car without rewriting, alongside rejection of unexpected script. Schema drift/system/dependency checks passed. Publication review covered only stage code/tests/documentation; Gemini files and ignored raw/media/model/database/secret artifacts were excluded.

## Clarified comments timing (D-17) — 2026-11-11

The user reported the resolved assignment interpretation: online means during class and offline means outside class. Both use normal connected website submission to an associated meeting. Local persistence, a send queue and disconnected synchronization are not required. This clarification applies to comments/suggestions only; attendance interpretation remains separate.

Code inspection found no meeting-time, attendance-window or simultaneous-lecturer-login gate in the existing request submission/history paths. Runtime submission/storage/authorization logic was unchanged. The student-facing notice now reads: You can send comments and suggestions during or outside class.

**Executed automated server checks: 25 participation tests passed in 31.285 s**, file-backed SQLite, no skips; system check reported no issues. The added regression exercises both comment and suggestion through the normal form/view/middleware path with CSRF enforcement:

- Set the meeting date seven days before submission; no attendance window exists.
- Submit each type using a fresh submission ID and a valid CSRF token. Verify the redirect and persisted meeting ID, student ID, kind, exact text and submission timestamp.
- Log the student out, use a fresh authenticated client, and verify both requests in personal history. Verify neither appears under a different meeting.
- Create a fresh Lecturer client with the clock advanced two days, and verify stored requests on the meeting page and lecturer feed. This is a mocked later timestamp, not a real two-day wait.
- Use another student account in the same course: neither private request is present in its page, and the lecturer feed returns HTTP 403.

This is automated request/database/rendering evidence, not a manual browser/phone or classroom-capacity test. Existing participation tests also cover identity/role revalidation, failed-save reporting, escaping, duplicate submission and input boundaries. README, SoW, SRS and the decision register now consistently record the resolved comments timing; the former unresolved-offline statements in older dated test records describe historical decisions and are superseded by this entry. No disconnected feature, database migration, AI request, commit or push was introduced.

## Local Qwen3 8B poll-draft probe — 2026-11-11

Four real local generations only: Hebrew/English comprehension and opinion, short synthetic transaction/rollback learning text. Installed Qwen3 8B Q4_K_M/Ollama 0.40.14, temperature 0.1, seed 42, thinking off, JSON schema, no generation retries. Wall times: he comprehension 8.730 s, en comprehension 2.432 s, he opinion 2.006 s, en opinion 1.330 s. First load 5.395 s; subsequent calls reused the model. An initial three-second local readiness check timed out before any generation; a 30-second readiness timeout resolved that startup-probe issue.

All four passed existing input/content structural validation without saving a poll. English comprehension uniquely selected rollback undoing all changes, including earlier successful operations, with a supported explanation. English opinion correctly asked for a preference among four reasonable practice methods, without an answer key; its topic reference is generic. Hebrew comprehension contained unexpected CJK script, weak/ambiguous distractors and an incomplete explanation despite normal model stop. Hebrew opinion had four reasonable choices/no correct answer but a grammatically and semantically corrupted question with weak personal-preference framing. Neither Hebrew result was publication-ready. Exact raw outputs were retained locally and presented unedited; source-grounding and readability review is recorded in [local-poll-feasibility.md](local-poll-feasibility.md).

The probe executed, and the standalone script compiled; no website implementation/database mutation, website regression suite, Gemini call, external-provider inference, download, billing, commit or push occurred. Generation on the website remains disabled pending a separately approved integration. Proposed publishing remains a Lecturer action after review/editing. Gemini hashes were verified unchanged.

## Local English poll generation integration — 2026-11-11

**135 server tests passed** in 52.445 s with file-backed SQLite, no skips; **33 focused poll/provider tests passed**, and **12 JavaScript tests passed**. System/schema checks passed with no migration needed. Unit tests use injected fixtures/mocked subprocesses; actual model evidence is separate below. No website authorization/disclosure test was replaced with a model-quality claim.

New coverage rejects generated duplicate/case-equivalent options, malformed fields, an invalid answer index, unexpected script and incomplete explanations. Real-adapter missing-runtime and invalid-provider-output tests verify no new Poll row and exact material retained in the bound form. Provider protocol tests verify private IPC cleanup and pinned model identity. English creation saves ai/draft, hidden from Student HTML/JSON. A Hebrew fixture still supports editing/publishing/voting; Hebrew generation is rejected before the provider is called. Existing tests cover 6,000/6,001-character limits, role revalidation after generation, separate publication, single active poll, voting races and pre-close answer privacy.

Real normal authenticated CSRF multipart-free form POSTs used installed Qwen3 8B on a new topic: stacks/queues, LIFO/FIFO and practice methods. The provider was the production local adapter, not an injected fake. These were in-process Django clients, not agent-operated browser automation.

- DEMO-CS101, new meeting **Local AI polls: stacks and queues** (6).
- Comprehension **3**: generation 9.652 s; four options, Stack at index 1 and a complete source-supported LIFO explanation. Saved as unpublished draft; Student detail/state returned 404 and the list omitted it. Edited the question with the topic prefix, separately published, and submitted a Student vote. Correct index/answer/explanation were absent from active Student HTML/JSON, then visible only after closing. Final status closed.
- Initial opinion **4**: generation 8.114 s; structurally valid but a required LIFO scheduler scenario made Stack the technical answer. The mechanical lifecycle test had already published it before semantic review. Review caught the defect and the new test poll was explicitly closed, without deleting or silently rewriting it. This demonstrates why structural validation cannot certify a genuine opinion question.
- Bounded prompt revision poll-en-v2 forbids functional constraints that determine the engineering answer and prefers learning-activity preferences. Revised opinion **5**, generation 9.520 s, asks for preferred practice: diagrams, sandbox coding, group discussion or step tracing. All four are legitimate positions; no correctness metadata exists. Semantically reviewed before editing/publishing, hidden from Students while draft, then visible/votable after explicit publication. Final status active.

Original generated text is retained only in ignored local evidence and shown to the user without edits. The demonstration edit added a Stacks and queues prefix; no generated answer was silently corrected. Comprehension list/tree distractors introduce terms not defined in the short material, which remains a Lecturer-review consideration. No broad semantic/language/classroom-performance acceptance is claimed. Maximum-input actual-model latency, browser/phone review and busy-server load remain unverified.

The UI defaults to English and explains the Hebrew generation limitation while preserving Hebrew lifecycle support. Failure/busy/invalid messages retain the input; no prepared fallback or automatic retry exists. Video transcription/summary code and experiments were left unchanged, and Gemini hashes remained unchanged. No download/external-provider call/billing, staging, commit or push occurred. Setup and manual steps: [local-poll-generation.md](local-poll-generation.md).

## Poll origin notice regression — 2026-11-11

The model-generated draft/review-required notice is now selected by viewer role and poll state in both the list context and detail/state payload. It is shown only to a Lecturer reviewing an unpublished AI draft (including the draft editor). Active/closed AI polls use the neutral Model-generated poll label for both roles. The existing Demo data — not generated by AI provenance label is preserved.

**34 focused poll/provider tests passed** in 1.253 s using file-backed SQLite, no skips. The new regression verifies Lecturer list/detail/edit/state visibility during draft, then absence of the review-required notice from Lecturer and Student list/detail/state after publication and closure. Existing poll privacy/lifecycle tests remain green. No AI generation, data migration or poll-content mutation was needed. This is server rendering/payload evidence, not agent-operated browser verification. No commit or push.

## English poll stage closure verification — 2026-11-11

At the user's request, the complete website suite passed: **136 server tests**, 88.304 s, file-backed SQLite, no skips. **12 JavaScript tests passed**. System, schema-drift and dependency checks passed. This includes English real-provider integration regressions, preserved Hebrew lifecycle behavior, pre-publication privacy and Lecturer-only draft-review labels in list/detail/state. The explicit publication scope contains poll code/tests/documentation only; Gemini files, PDF, media, models, raw outputs, local databases and secrets remain excluded. No new model generations were needed for these automated checks.
