# Verification Record — Units A, B, C, D and E

## Current component-to-test strategy

This section addresses To Do 8 and the real names in the
[class/interface diagrams](architecture.md#class-and-interface-diagrams).
It is a current strategy/index over existing tests, not a new execution record.
Dated results below retain provenance. The original documentation-only round
ran no software tests or AI; subsequent runtime verification is recorded below.
Latest full workflow verification is 177 server and 12 JavaScript logic tests,
with 26 focused workflow/provider checks after routine corrections; these are
separate from standalone experiment quote audits and device/browser evidence.

Use software tests for deterministic contracts, state/permission/retention and
process-control assertions; use bounded real-model samples for inference wiring
and content review; require separately reported browser/phone/classroom evidence
for those environments. A fake engine may verify failure handling or disclosure,
never speech/feedback/summary correctness. Exact-source quote checking does not
prove that the quote supports the assessment.

| Diagram component / responsibility | Risk or invariant | Existing software evidence (named tests) | Real-model / open boundary |
|---|---|---|---|
| User, Course, Membership, Meeting, MeetingForm | Cross-course access, forged role/parent and invalid writes | [Foundation suite](../classroom/tests.py); [class-aware assertions](#class-aware-coverage) | User browser checks are separate; production identities/phone/load open. |
| AttendanceWindow, AttendanceRecord and attendance module | QR expiry/login continuation/duplicate registration; one record per student/meeting | [Participation suite](../classroom/test_participation.py): test_close_invalidates_every_code_even_after_reopen, test_window_closed_after_get_rejects_post_and_next_scan_requires_new_code; concurrent registration cases in same suite | Earlier QR report was not phone evidence; the later iPhone/Safari report below verifies the stated happy path only. Classroom use and physical-presence proof are not established. Email wait closed by D-54. |
| MeetingRequest and request form/views | Outside-class persistence and Student-own/Lecturer visibility | [Participation suite](../classroom/test_participation.py): test_outside_class_requests_for_past_meeting_persist_for_later_lecturer | User reported live appearance of a comment; D-17 resolved. Broader load/retention open. |
| Poll/PollVote, poll_services.edit_draft/publish/vote/close | Stale edits; second Active poll; concurrent duplicate vote; vote/close ordering | [Poll suite](../classroom/test_polls.py): test_draft_edit_all_content_and_optimistic_version, test_same_student_parallel_votes_are_final_and_unique, test_parallel_publications_only_one_active_poll, test_vote_racing_close_has_one_consistent_order | Real local generated drafts exercised lifecycle; not classroom load. |
| poll_services.public_payload and Poll views | Draft/answer privacy; review notice only Lecturer/Draft | [Poll suite](../classroom/test_polls.py): test_student_cannot_see_drafts_in_list_detail_or_state, test_ai_review_notice_is_lecturer_draft_only_in_list_detail_and_state | User opinion-results checks reported separately; browser/phone matrix incomplete. |
| PollGenerator / LocalPollGenerator / poll_contract | Invalid or unavailable engine must save no draft and retain material; Hebrew lifecycle unaffected | [Generation tests](../classroom/test_poll_generation.py): test_valid_comprehension_and_opinion_are_not_rewritten, test_bad_fields_script_duplicates_answer_and_incomplete_explanation_rejected, test_adapter_protocol_is_local_only_and_removes_private_material, test_unavailable_real_adapter_preserves_form_without_creating_poll, test_invalid_output_preserves_material_and_does_not_save, test_generated_poll_is_draft_hidden_from_student_before_separate_publish, test_hebrew_existing_draft_edit_publish_and_vote_remain_supported | Actual English stacks/queues route in local-poll-generation.md; factual opinion defect caught in review. Hebrew generation unavailable; max-input semantic/latency quality unproven. |
| BoundedUploadHandler / VideoUploadForm / video_jobs.save_upload | Oversized/corrupt/no-audio input and unauthorized upload | [Video tests](../classroom/test_videos.py): test_size_handler_boundary_and_real_http_abort, test_duration_limit_is_server_enforced_with_real_media, test_corrupt_no_audio_and_audio_only_are_failed_by_worker, test_authorization_owner_lecturer_and_parent_scoping | Both supplied clips extracted; input-limit checks do not prove ASR accuracy. |
| VideoJob / video_worker.claim_job/process_job / media_child | One worker; queue wait separate; timeout/stop/stale recovery; remove temporary audio | [Video tests](../classroom/test_videos.py): test_single_worker_lock_and_fifo, test_queue_wait_does_not_consume_processing_budget, test_timeout_terminates_actual_subprocess_and_removes_audio, test_hard_stopped_worker_is_recovered_and_decoder_does_not_orphan | Real uploads/workers exercised; full GPU hard-crash testing not claimed. |
| Transcriber / LocalWhisperTranscriber / checkpoint helper | No fallback/download; valid metadata/text; one deadline; failure cleanup | [Transcription tests](../classroom/test_transcription.py): test_unavailable_turbo_fails_clearly_without_fallback, test_loaded_model_identity_is_retained_if_inference_fails, test_total_deadline_is_not_reset_at_transcription_start, test_adapter_protocol_keeps_text_off_stdout_and_forces_offline_environment, test_checkpoint_verification_rejects_missing_or_changed_files | Real medium/turbo on full SHORT/STATIC and new turbo uploads. No human-reference word accuracy; Hebrew code terms/negation remain uncertain. |
| Summarizer / LocalQwenSummarizer / summary contract | Save transcript first; invalid language/model/format; failed summary preserves transcript | [Summary tests](../classroom/test_summaries.py): test_full_lifecycle_stores_transcript_first_then_summary_with_shared_expiry, test_summary_failure_keeps_saved_transcript_accessible, test_hebrew_summary_accepts_english_code_terms_without_rewriting, test_format_language_and_wrong_model_are_rejected | SHORT real upload success; STATIC saved-input success but uploaded summary_language failure. Structural tests cannot certify source grounding. |
| video_jobs.owned_job/transcript_available/summary_available/purge_expired_transcripts | Owner/current role on direct URL; exact expiry; summary never outlives transcript | [Transcription tests](../classroom/test_transcription.py): test_demotion_revocation_and_mismatched_parent_block_saved_link, test_expiry_blocks_at_exact_deadline_even_before_cleanup; [summary tests](../classroom/test_summaries.py): test_expiry_hides_summary_on_direct_job_url_and_cleanup_clears_both | Actual owner pages opened; seven-day passage is tested with controlled time, not a seven-day live wait. Physical cleanup requires running maintenance. |
| ProcessTree / exclusive_lock | Orphan compute and competing video/poll/homework AI | [Summary tests](../classroom/test_summaries.py): test_windows_process_tree_close_terminates_owned_descendant; [video tests](../classroom/test_videos.py): test_single_worker_lock_and_fifo; generation adapter protocol test above | Owned-descendant test uses ordinary Python, not a real GPU hard-crash. Real sample services exited; classroom contention unmeasured. |
| transcript_display.reading_paragraphs / Templates / browser scripts | Reordering/rewriting, RTL-LTR, escaping, hidden-page polling and double reload | [Display tests](../classroom/test_transcription.py): test_pause_boundaries_preserve_words_and_isolate_new_car, test_unmatched_legacy_segments_do_not_replace_text; [JS video tests](../tests_js/videos.test.cjs), [poll tests](../tests_js/polls.test.cjs), [participation tests](../tests_js/participation.test.cjs) | User opened STATIC transcript and SHORT summary/link. Actual-phone layout and full keyboard/browser matrix remain open. |
| HomeworkAssignment / ReviewJob / homework_review | Frozen rubric/target/latest-other-owner versions, roles, private drafts and immutable version-bound publication | [Workflow tests](../classroom/test_homework_review.py): test_lecturer_request_excludes_all_target_owner_versions_and_freezes_latest_peers; [local integration tests](../classroom/test_local_homework.py): test_rubric_edit_frozen_in_existing_job_and_course_authorized, test_lecturer_can_correct_false_no_difference_outcome_without_rewriting_raw_result | Real English and user-reported guided publication are recorded below; automatic comparison still made substantive errors. |
| LocalHomeworkReviewer / homework_evidence / FeedbackDraft | Owned deadline cleanup, quote matched to correct source, unmatched evidence blocks publish, peer text privacy | [Local integration tests](../classroom/test_local_homework.py): test_provider_timeout_terminates_owned_tree_and_removes_private_ipc, test_peer_quote_checked_against_referenced_peer_not_target, test_privacy_guard_blocks_peer_passage_and_identity_even_after_lecturer_edit | No test guarantees semantic entailment or indirect anonymity. Real workflow success is separate from model content accuracy. |
| Personal-review audit helper (experiment only, not website class) | Fabricated quote versus unsupported conclusion | [Quote-audit tests](../experiments/local_ai/test_personal_review_probe.py), now published with synthetic fixtures | [Personal probe](homework-personal-review-feasibility.md) reports 15/15 exact quotes, but technical false positives/negatives persist. No homework acceptance. |

### Evidence boundaries and outstanding acceptance

- **Software:** request/database/rendering/contracts and bounded process tests
  above; test doubles and controlled clocks are disclosed in dated records.
- **Real model:** measured local ASR, summary, English poll and synthetic homework
  trials are indexed by the [tools report](local-ai-feasibility.md#current-tools-and-evidence-index).
  The independent homework coverage map was not supplied to the model. Gemini
  has no substantive task-quality result; user-reported direct HTTP 503 is a failure.
- **Manual interface:** user reports are labeled as such below. They do not
  establish unreported phone, audio-reference accuracy or classroom-load tests.
- **Open:** review the relevant lecture section under D-54, phone/network/load conditions,
  broad AI quality and assignment acceptance beyond the observed workflows. The written results account is in [README](../README.md#results-summary).
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

## UC-05 feedback workflow controls

**Executed 2026-11-12:** all **167 server tests passed in 54.969 seconds**, no skips,
using a separate file-backed SQLite test database. This includes **16 new workflow
tests** in [test_homework_review.py](../classroom/test_homework_review.py), plus the
15 submission-foundation tests. **12 JavaScript tests passed**. System/schema-
drift checks passed and migration 0008_homework_review_workflow was applied to
the ignored local development database. There was no real-model generation.

The central CSRF-enforced authenticated form route used test actors student_alex
and lecturer_alpha. Alex requests feedback on v1 with a fake provider available
only through test injection, submits v2 before processing, then the processor
receives the exact v1 source. The Lecturer page identifies Version 1, warns that
a newer version exists, and shows only the frozen v1 source. The Lecturer edits
and separately publishes it; Alex sees published feedback only on v1, not v2.
Before publication the draft is absent from Student HTML and the Lecturer route
returns 403 to the Student. This is in-process HTTP/database/rendering evidence,
not browser interaction or a real model-quality result.

| Actual component | Executed control assertions |
|---|---|
| AssignmentForm / DisabledHomeworkReviewer / request_review | English/Hebrew assignment language stored; unsupported choice rejected. Normal factory refuses both languages, including a fictitious settings flag; preflight explains unavailability and forged POST creates no ReviewJob. |
| ReviewJob snapshot selection | Lecturer-triggered request excludes every target-owner version, includes only latest other-owner versions for the same assignment, and freezes sources/criteria against later submissions or rubric changes. Repeated active requests reuse the original job. |
| homework_worker / validation | Historical D-55 checks: invalid individual shape/quotes failed and the normal factory was disabled. D-56 supersedes availability and quote handling: source mismatches remain private/unverified and publication-blocking; invalid shape/source indexes fail the affected stage. Worker-restart behavior is retained. |
| Draft edit / publish / public projection | Separate publication, stale edit/version rejection and immutable published snapshots; other Student/nonmember/wrong-course/direct parent routes denied; role revocation before processing/publication blocked. HTML escaped and private peer snapshots/model metadata absent from Student output. Login, POST-only and CSRF checks included. |
| D-52 partial success and later comparison | Private draft before publication. Explicit individual_only action publishes personal content with the exact comparison-failed notice; complete publication in that state is rejected. No peers, failed comparison and completed no_difference remain distinct. Later comparison stays hidden until another explicit publication, preserving prior publication history. |

**Live normal-site HTTP check (no fake):** Lecturer assignment creation form exposes
the target-language selector with its limitation. Student Alex's existing v1 page
at /courses/1/meetings/5/homework/1/versions/1/ shows English generation unavailable
and no request button. An authenticated CSRF POST to the request route returns the
same reason and leaves the development ReviewJob count exactly zero. No test
feedback or prepared draft was seeded into the live database. This is direct
HTTP/form inspection, not agent browser/phone visual acceptance.

Pre-commit verification after the user display report: **31 focused homework
submission/workflow tests passed in 0.787 seconds**, with a separate file-backed
SQLite database, no skips. System and migration-drift checks passed. Application
code was unchanged since the full 167-test run above; this rerun verifies the stage
before publication without another real model call.

### User-reported Version 1 display check - 2026-11-12

The user reported opening student_alex's Version 1 page in the browser. It showed
Submitted status, the original submitted text, a clear notice that English
feedback generation is unavailable and no request would be created, and a notice
that no feedback had yet been published for that version. This is a manual
**display** check reported by the user; the account/role was not specified in this
report. It does not claim that the user submitted a feedback request or exercised
draft editing/publication. The draft-edit/publication lifecycle, including v1
request followed by v2 resubmission, is verified by automated injected-provider
tests only. No real-model feedback/comparison or phone test is established.

**Not established:** actual personal-feedback/comparison quality, accepted real
providers for either language, semantic anonymity/technical correctness, real
inference deadline/cancellation/hard-crash behavior, measured workload/input caps,
classroom load or intentional demo-data cleanup. Fixtures test the lifecycle,
never fulfill the real-model requirement. Lecturer semantic/privacy review remains
necessary even when field/quote checks pass. No application commit/push is made
by this verification record; the separate experiment commit is bb9cc58.

The lecturer clarification update is documentation-only: the user reports design
freedom and a reference to requirements 1-5 in the lecture. The QR/list-XLSX/speech-
summary choices are project-owned; email waiting is closed, and lecture-section
review is still an action. No independent lecture review is claimed.

## Planned UC-05 acceptance strategy

**Full model-quality acceptance is not established.** D-53/D-55 source/version
and review/publication software controls are implemented. D-56 adds real local
English generation plus rubric snapshots/evidence/outcome editing, with software,
actual-model and [user-reported guided evidence](#user-reported-guided-rehearsal---2026-11-17)
kept separate. D-57 keeps automatic Hebrew a future nonblocking demo target.
The retained section anchor describes acceptance responsibilities, not a claim
that these components are still unimplemented. Historical experiments below
remain unchanged; exact quotes and successful publication do not certify meaning.

### Planned website correctness checks

| Planned responsibility | Risk / acceptance check | Evidence status |
|---|---|---|
| homework_review module + existing Membership | Student requests only own work, course Lecturer may request a course submission. Reject forged owner/course/version, direct cross-user/cross-course HTML/JSON and revoked membership at request/save/publication/read. | Workflow controls tested under D-55 with test-only provider; no real-model acceptance. |
| SubmissionVersion | Resubmission preserves exact earlier text and version; old published feedback stays associated with that version. Concurrent submissions cannot overwrite a version. | Source/version/concurrency checks implemented under D-53 in test_homework.py; D-55/D-56 tests and user-reported publication checks verify version-specific feedback association. |
| ReviewJob source selection | Save latest version per other owner in the same assignment at request creation; exclude all target-owner versions, not merely requester versions. **Lecturer initiates review of A, where A has multiple versions: none of A's versions may appear as a peer.** Include latest B/C only, exclude foreign assignments, and preserve the chosen snapshots after later resubmission. | D-55 snapshot and Lecturer-request tests passed. |
| ReviewJob provenance | Save actual target/peer IDs, instructions, criteria, assignment revision/language, rubric text, actual model identity and failure stage. Editing source/rubric/language does not rewrite prior request inputs. | D-55 frozen-source tests passed. |
| FeedbackDraft + review service | Student cannot discover draft text/evidence via list/detail/JSON. Lecturer can review/edit; only separate CSRF Publish exposes version-bound public content. Original generated text is distinguishable from edits. Stale or concurrent edit/publication and changed-source-as-current attempts are rejected or explicitly flagged, never silently relabeled. | D-55 draft privacy/stale version/publication tests passed; classroom concurrency remains unmeasured. |
| Student output projection | Only own published feedback; no peer identities, IDs, stable labels, full works or private comparison quotes/evidence. Lecturer can inspect permitted sources. Test accidental provider identity fields and escaping. | D-55 direct-access/rendering tests passed; semantic text privacy still needs Lecturer review. |
| Comparison state | Empty eligible set produces system-controlled no-other-submissions notice and permits personal publication. Nonempty set plus failure retains personal draft with a separate comparison-failed state, never no peers or no difference. Completed no-supported-difference is distinct from completed differences. D-52 permits personal-only publication only after successful personal generation, Lecturer review and explicit selection; keep comparison failed. Personal generation failure has no draft/publication. | D-55 test-only partial/no-peer/no-difference/publication cases passed; policy resolved by D-52. |
| Language gate | Assignment stores selected language; unsupported/unaccepted language fails before inference. A generation language can be enabled only with recorded reviewed real output for this workflow. D-56 enables English experimentally after later real-output review; D-57 keeps automatic Hebrew unavailable and outside this demo. | Existing preflight tests and real English route are recorded separately; neither establishes general feedback quality. |
| Worker / HomeworkReviewer / validator | Unavailable/invalid/timeout/interrupt/busy reports a real failure without prepared fallback or automatic publication. Verify shared-compute integration without changing video processing. D-56 sets initial source/peer limits and a 180-second deadline, with no automatic retries. | test_local_homework.py covers source matching, snapshot privacy and owned timeout cleanup; normal English inference is recorded separately, not model-quality acceptance. |
| Explicit synthetic-data cleanup | Keep versions/feedback through demo and submission checking. Then an intentional authorized cleanup removes linked demo content consistently without deleting unrelated course data. No inherited seven-day expiry or automatic deletion; real-work policy remains separate. | Planned lifecycle tests, no cleanup executed. |

### Planned partial-publication regression (D-52)

**Executed with injected fixtures under D-55, not a real model.** Arrange eligible peers, successful personal feedback and failed
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

## Local homework review/comparison probe — 2026-11-11

Prepared an independent source/rubric coverage map before generation (not passed to the model), then ran installed Qwen3 8B on each of three existing synthetic works with the other two as anonymous peer text, plus A alone. Four local generations, no retries, no download/external provider/Gemini call. Wall times A 14.859 s, B 7.363 s, C 10.427 s, A alone 7.929 s; first load 2.690 s, later warm loads ~0.003–0.004 s. All stopped normally with four criterion findings; flags matched actual peer availability.

Quality review FAILED key expectations: A received invented capacity-condition gaps despite explicit coverage; B's rollback sentence was correctly quoted (no false absence claim), but its wrong UNIQUE/capacity and cache-only approval were not adequately corrected; C's real rollback/duplicate omissions were found, alongside unsupported recommendations and misaligned evidence. Comparison identified some actual coverage differences but confused approaches and invented ordinal peer labels. No source IDs/names/full peer works were emitted. 15/16 exact target-quote checks passed, showing that quotation presence alone does not prove the right assessment.

The no-peer case provided personal feedback and comparison_performed=false, but its text only said אין תובנות משותפות, not that no other submissions are available; the explicit notice check therefore failed. Hebrew language corruption/readability problems remain. These are experiment findings, not homework capability acceptance. See [homework-review-feasibility.md](homework-review-feasibility.md). No homework website implementation or further commit/push was performed. The English poll stage was committed/pushed before this experiment; its previously recorded full suite is separate evidence.


## Isolated personal criterion review — 2026-11-11

Ran four real, local Qwen3 8B Q4_K_M/Ollama 0.40.14 requests: unchanged synthetic A/B/C separately, then B changing only its cache-authorization sentence. The independently timestamped coverage map and expected judgments were kept out of model input; no peers were supplied. Wall times: A 13.994 s (2.985 s initial load), B 11.232 s, C 11.888 s, cache-fixed B 9.047 s. All stopped normally; no retry or external provider was used.

Mechanical audits passed 15/15 supplied exact source quotes and all four criterion-index sets. Two standalone quote-audit tests passed; they deliberately do not certify whether quotes support conclusions. Substantive source review FAILED key expectations: A's explicit capacity condition was recognized but a duplicate/capacity distinction gap was invented; B's rollback was explicitly recognized but initially penalized via confusion with concurrency, its wrong UNIQUE/last-seat claim was accepted in both versions, and unsafe cache approval was softened to partial coverage. After fixing only cache authorization, the cache criticism disappeared, but the unchanged capacity-protection criterion incorrectly improved to correct. C's explicit locking/recheck was labeled missing and its acknowledged duplicate-protection omission was missed. No incorrect status appeared despite explicit B errors. Hebrew wording also remained corrupted in places.

Full verbatim B before/after feedback and evidence review: [homework-personal-review-feasibility.md](homework-personal-review-feasibility.md). Recommendation: improve isolated personal assessment before a separately approved comparison experiment; no homework website integration. Original samples and Gemini experiment files were left unchanged. No website test result, download, cloud call, billing, commit or push is claimed for this probe. Raw prompts/outputs/maps remain in ignored local experiment storage.


## Closed per-criterion Qwen3 feedback probe - 2026-11-12

Four synthetic works, 14 local GPU requests (one criterion each): Alex v1/v2
conclusions matched expected LIFO/plates/FIFO/queue additions. B failed the
controlled cache-edit test: all four statuses changed partial -> correct, with
false approval of the unchanged UNIQUE/last-seat guarantee. All 26/26 supplied
quotes were exact source substrings; separate meaning review still found false
conclusions and irrelevant evidence. Times per work: 11.917, 7.197, 17.506 and
12.854 seconds; first work includes 4.860 seconds loading. One run per case,
no statistical acceptance. The experiment round is closed, not accepted as a
real homework provider in either language. No further inference was run for
publication. Fixtures, recorded outputs and [reproduction instructions](../experiments/local_ai/README.md#focused-homework-probes---reproduction)
are now reviewable from the repository; model/runtime assets remain local-only.
Full findings: [criterion probe](homework-criterion-review-feasibility.md).


## Experimental local homework integration

2026-11-15, D-56. English Qwen3 8B Q4_K_M with the professional rubric is
connected to the ordinary UC-05 request/worker/private draft/edit/publication
routes. Synthetic fixture only. No model download, external request, Gemini,
billing, staging, commit or push. Earlier disabled-provider and failed-readiness
sections above are historical measurements, not the current availability state.

### Software checks versus actual inference

The full file-backed SQLite suite initially passed 175 server tests in 54.843 s.
The final full file-backed SQLite suite passed **177 server tests in 65.398 s**,
including two further regressions for correction of a false no-difference outcome
and timeout termination/private IPC cleanup. After routine invalid-rubric-form,
original-failed-output retention and deadline-start corrections, **26 focused
workflow/provider tests passed**. No concurrency test was skipped. All 12 JavaScript tests passed;
system, migration-drift and dependency checks passed.

The first focused test invocation used shared in-memory SQLite: 30 passed and
one existing multi-connection submission test failed with `database table is locked`.
The same 39 focused tests passed with file-backed SQLite, matching the development
DB mode. This was not concealed by skipping the concurrency test.

| Component / responsibility | Risk | Existing exercised test |
|---|---|---|
| request_review and rubric snapshots | Changed rubric/new submission silently changes request | test_rubric_edit_frozen_in_existing_job_and_course_authorized; existing latest-other-owner snapshot/Lecturer-initiation tests |
| Source-bound evidence | Another version/peer quote incorrectly accepted; unsupported quote published | test_correct_quote_against_frozen_source_not_new_version; test_peer_quote_checked_against_referenced_peer_not_target; test_unmatched_quote_remains_private_and_blocks_publish_until_removed_via_form |
| edit_draft / publish | Wrong outcome survives Lecturer correction; original result lost | test_lecturer_can_correct_false_no_difference_outcome_without_rewriting_raw_result; stale-edit/publication regressions |
| Public projection and privacy guard | Student reads draft, peer text/identity or another owner's feedback | Existing direct-URL/HTML privacy/role revocation tests; test_privacy_guard_blocks_peer_passage_and_identity_even_after_lecturer_edit |
| Capacity / preflight | Silent source sampling, queue for unavailable language/assets/rubric | test_capacity_overflow_rejects_request_without_silent_peer_sampling; test_missing_rubric_prevents_waiting_request; test_missing_runtime_and_hebrew_are_not_available |
| LocalHomeworkReviewer subprocess | Timed-out process keeps GPU/IPC; hidden provider fallback | test_provider_timeout_terminates_owned_tree_and_removes_private_ipc; installed-model identity checks and separate actual inference |
| Partial/no-peer/no-difference states | Failure becomes no peers or automatic publication | Existing comparison-failure individual-only, personal failure, no-difference and later-publication tests |

Fixtures/test doubles prove workflow invariants only, not generated feedback
quality. No fake provider is selectable in the normal site.

### Real local provider route and measurements

Authenticated Django clients with CSRF enforcement used normal HTTP view/form
routes and the actual `run_homework_worker --once`, normal provider factory and
isolated installed model. This is an agent-operated integration check, not a
user-reported browser/phone check. Initial synthetic sources were prepared by
seed_demo_homework_review through the authorized submission services. Alex then
submitted a second version through the normal submission POST before completion
of the first version's review. Exact source and rubric snapshots remained bound
to Version 1. The peer group for a later Casey request correctly used Alex's
latest Version 2, not both Alex versions and not Casey's own work.

| Run | Result | Request POST to ready/failure | Model request wall, excluding runner startup/teardown |
|---|---|---:|---:|
| student_alex, job 1 | ready, private draft; generated no_difference | 35.345 s | 26.513 s |
| student_casey, job 3 | ready, private draft; generated no_difference | 35.216 s | 25.984 s |
| First Casey attempt, job 2 | individual_failed; no draft, no publication | 33.465 s worker interval | Not retained |
| Alex Version 2, job 4, manual-review sample | ready/private; generated no_difference | 41.446 s | 33.243 s |

The failed first Casey attempt predates added private failure diagnostics/output
retention; its exact structural/runtime cause and output are unavailable. Do not
attribute it to timeout, GPU load or model quality without evidence. An explicit
new request succeeded with unchanged prompt/settings. No automatic retry ran.
Future individual failures retain available original structured output, safe
failure type/code and stage metadata; structural failure still creates no draft.

The later Alex job records all 6,194,766,806 model-resident bytes in GPU memory
for both individual and comparison stages through /api/ps. This establishes GPU
residency, not peak total device usage/RAM. Metadata retains pinned model hashes,
Ollama 0.40.14, prompt homework-rubric-en-v1, temperature .1, seed 42,
8192 context/2304 maximum output tokens, think=false, no retries, per-call wall,
load and generation times. The first call in each owned service includes loading.

### Content findings and actual publication

The two different approaches are (a) positive-capacity conditional update and
(b) exclusive shared-row lock with recheck. Both works cover the four criteria.
All four individual statuses were correct in each successful integration run.
The Casey capacity rationale loosely conflates atomicity/rollback with the
capacity mechanism and should be sharpened to describe the lock and recheck.
Repeated full-work descriptions also need shortening. Source-exact quotations
are not semantic acceptance.

All three successful comparison drafts wrongly concluded no supported difference,
despite the real approach difference. Casey's comparison also referred to the
peer's second version rather than focusing on the technical difference. This is
a substantive model error, not proof of absent differences. Lecturer must change
the comparison text AND the reviewed outcome to compared when correcting it.
No prompt tuning was performed after these results to hide this failure.

Alex V1 job 1's original comparison included:

> No supported difference exists in topic coverage or approach.

The agent acting through the Lecturer's normal CSRF form corrected it to:

> Your submission reserves capacity using a conditional positive-count update. Another submission holds an exclusive lock on the shared capacity row and rechecks availability before writing. Both are valid approaches described in these works. Both distinguish duplicate enrollment from shared capacity and use database-authoritative enrollment rather than cached availability. The solution approaches differ even though topic coverage is similar.

The outcome was changed from no_difference to compared, saved, then published in
a separate POST. Save/publication/Student verification requests took 0.063 seconds,
excluding the intervening analysis/edit preparation time; no human editing time was measured. Student Alex V1 showed the corrected publication and no false
system no-difference notice. V2 did not show V1's feedback. Another student's
source URL returned 404; Student draft URLs returned 403. Neither private evidence,
peer sources, model JSON nor rubric appeared in Student responses. The original
model no_difference result remains recorded privately.

Job 1 had 14/14 exact evidence matches; Casey job 3 also had 14/14. Before the
user's subsequent manual review, the Alex V2 draft (job 4) had 13/14: evidence item 13 was an exact quote from the PEER's
cache explanation, but the model labels it as TARGET. Correct matching-source
validation flags it unverified. A real publication POST returned 409 and left the
draft private. For manual review, remove item 13 or replace it with an exact
relevant target quote; then correct the false comparison and outcome and save
before a separate Publish. This demonstrates why both attribution and source
presence are checked. Do not silently fix or discard the original evidence.

### Review links, artifacts and limits

The local site was started on 127.0.0.1:8000 without network/firewall changes.
An authenticated request to the active HTTP server verified the experimental
warning, unverified-evidence indicator and editable outcome field on job 4.
This is HTTP integration, not visual/mobile browser validation.

- Meeting: Homework AI review demo, DEMO-CS101; synthetic assignment 2.
- Alex V2 review record (subsequently edited/published by the user): http://127.0.0.1:8000/courses/1/meetings/7/homework/reviews/4/
- Alex V2 page: http://127.0.0.1:8000/courses/1/meetings/7/homework/2/versions/5/
- Reviewed/published Alex V1: http://127.0.0.1:8000/courses/1/meetings/7/homework/2/versions/3/

IDs are local database examples, not portable repository fixtures. The saved
local-only .local/homework-model-acceptance.json contains unchanged generated
outputs, timings and audit records; .local scripts/logs/database remain excluded
from Git. The reproducible synthetic sources are classroom/demo_homework.json.
Fresh checkouts use the seed command and their own generated IDs.

English draft integration is useful for supervised editing, not reliable grading
or automatic publication. Comparison is particularly unreliable in this sample;
quote correctness does not repair its conclusion. Hebrew, largest allowed peer
sets, throughput under classroom load, adversarial anonymity, human editing time,
phone behavior and intentional post-demo data cleanup remain unverified/open.
[Operating limits and manual steps](local-homework-review.md).

### User-reported manual review and version-specific publication

The user reported completing the following browser checks:

- Edited the comparison in the Version 2 draft, removed Evidence 13, saved the
  draft and separately published it.
- As Alex, saw the individual feedback and the manually corrected comparison
  on Version 2.
- Opened Version 1 and confirmed that its previous feedback retained its
  original publication time and comparison, unchanged by Version 2 publication.

This is user-reported manual interface evidence for editing/removing evidence,
separate publication, Student visibility and preservation of historical
version-specific publication. The comparison was corrected manually; this is
**not** evidence that the model generated the comparison correctly. It does not
establish word-by-word feedback accuracy, phone behavior, additional permission
scenarios or classroom capacity. Automated server authorization checks and
actual-model content findings remain separate above. No model inference or
application-code change was performed while recording this report.


## Phone evidence and focused demo test gaps

### User-reported manual device results

The user reported the following tests in Safari on a real iPhone connected to
the home Wi-Fi network:

| Reported path | Reported result | Evidence limit |
|---|---|---|
| Login using the LAN website | Successful login | No reported device/OS version, login error, logout or session-expiry scenario. |
| Scan QR and register attendance | Registration appeared to the Lecturer. A later user report also confirms a scan led to login, an expired-code message appeared, and a new scan registered attendance. | Do not infer an exact delay/expiry boundary, automatic return details, window closure, duplicate or concurrent scan checks on the phone. |
| Submit a comment | Comment appeared to the Lecturer | No reported refresh behavior/timing, suggestion-type check, other-student privacy or boundary-input test on the phone. |
| Vote in a poll and view results after closure | Voting and post-close results worked. In the later comprehension-poll report, correct answer, explanation and results were hidden before closure and all appeared after closure plus reload in Safari on iPhone. | UI observations only; do not infer exact timing, additional screens, voter-identity inspection or server-payload inspection from the report. |

These are user-reported manual checks, not tests executed/observed by the agent.
No screenshots or inferred screen coverage are claimed. The phone round has ended for now. No video upload/transcript/summary, homework, Lecturer editing/publication,
XLSX, landscape, accessibility, long-text or all-screen phone acceptance follows
from these four results. See [phone record and remaining plan](phone-testing.md).

### Separate test layers and existing infrastructure

| Layer | Existing infrastructure / evidence | What it does not establish |
|---|---|---|
| Server | Django TestCase/TransactionTestCase, authenticated Client with CSRF checks, file-backed SQLite concurrency. Last full run: 177 tests; subsequent focused corrections: 26 passed. Login/course authorization in classroom/tests.py; QR/comment checks in test_participation.py; poll checks in test_polls.py; video and homework suites separate. | Actual browser event handling, CSS/layout, native camera, Safari/network/session behavior. Django Client is not a browser. |
| JavaScript logic | 12 node:test tests in tests_js; vm with hand-built fake document/fetch/timers. Lecturer polling/visibility, QR rotation rendering, scan POST form submission and result refresh/state transitions. | Real DOM rendering, radio hit areas, browser networking, WebKit or a mobile viewport. These are not browser tests or phone emulation. |
| Browser with phone emulation | No committed Playwright/Selenium/Cypress/Puppeteer config, package manifest or browser suite found. Playwright/Selenium are not installed in the website environment. No new browser/emulation run occurred in this review. | No emulated-device pass is claimed. Environment tooling for interactive browser control, if used later, is separate from a maintained repository suite. |
| Real device | The four user-reported Safari/iPhone happy paths above. | No general cross-device/browser acceptance or classroom-network result. |

Server coverage already checks login continuation and code expiry at POST,
closing a QR window, tampering/wrong meeting, duplicate/concurrent registration,
Lecturer-only roster/export, comment bounds/persistence/outside-class submission,
Student-own history and course authorization. Poll tests cover associated labels
and single explicit submission, final/duplicate votes and close races, hidden
drafts, pre-close answer/result privacy in HTML/state responses, and post-close
results. Do not duplicate these as a second broad browser authorization suite.

### Focused completion proposal, not executed

Before the demo, prioritize one timed rehearsal on the intended demonstration
network using the existing desktop browser and accounts. Cover all five approved
capabilities in presentation order, actual waiting time, worker readiness and
Lecturer corrections/publication of homework; distinguish live operations from
any explicitly approved earlier results. Home Wi-Fi success does not establish
classroom Wi-Fi reachability. Repeat only a short connectivity/login/QR smoke
check if the demonstration network or server address changes.

The formerly pending narrow comprehension disclosure UI check is now covered
by the subsequent user-reported Safari/iPhone observation below. The later user report
now supplies real-device evidence for a QR scan leading to login, an expired-code
message and successful registration after a new scan; exact timing/redirect details
are not inferred. Server tests already cover both paths. Reuse
existing accounts and browser sessions when resuming testing; do not add another
server test package or install a browser framework for this documentation round.
They are proposed targeted checks, not reported phone passes or a reason to
resume the paused phone round without the user.

Optional later work: a thin reproducible browser smoke with a mobile viewport,
additional iPhone/Android models, landscape/long-text/accessibility review and
classroom-load measurement. A viewport check would still not replace a physical
phone/camera test. No large E2E framework, duplicate suite, application code,
new AI experiment, network/firewall change, software-test rerun, commit or push
was performed during this review.


## Focused comprehension-browser check - blocked, not executed

The agent attempted to observe the existing local website through the available
Computer Use browser tool. A saved user permission/browser security policy denied
access to the localhost origin. No alternate browser surface, raw browser protocol,
injected session or other workaround was used. No poll was created, voted or closed
by this attempted browser check, and no browser/phone-emulation pass is claimed.
Existing server HTML/state disclosure tests remain separate evidence.

The manual replacement check is now completed as a user report below. These
were the proposed instructions, not agent-executed actions; do not infer that
the user used the suggested seed command or every optional assertion:

1. Prepare an English comprehension draft with a known correct answer and
   explanation. To avoid another AI call, use the existing explicitly labeled
   demo command below and choose only the comprehension draft. This creates
   synthetic lifecycle fixtures, not AI-generation evidence.
2. Lecturer: review and publish the comprehension draft. Student in a separate
   browser/private session: open it, verify no designated correct answer,
   explanation or vote distribution is visible. Options themselves remain visible.
3. Student: select one option and Submit final response. Before Lecturer closure,
   verify the page still hides the designated answer, explanation and aggregate
   counts/percentages, including after reload.
4. Lecturer: Close voting. Student: reload and verify the correct answer and
   explanation plus aggregate counts/percentages appear, with no voter identities.
   Record the observed result; do not infer a pass from the server tests.

From the project root, replacing MEETING_ID with an authorized meeting ID:

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo_polls --meeting-id MEETING_ID --language en --new-set
```

The command also prepares an unused opinion draft; do not publish it for this
single test. Do not close/overwrite unrelated polls; select an appropriate meeting
with no active poll. [Ten-minute demo plan and frozen AI backup](demo-runbook.md).


### User-reported comprehension disclosure check - completed

The user reported Safari on an iPhone: before the comprehension poll closed,
the correct answer, explanation and results were hidden. After closure and
reloading the page, all three appeared correctly. This is user-reported real-
device browser/UI evidence; the agent's browser attempt above remains blocked.
No browser automation or phone emulation pass is claimed. No extra assertion
about counts, voter identities, payloads, timing or other screens is inferred.

The user also reported seeing a “model busy” message, without identifying its
exact stage or cause. The shared nonblocking decoder lock can reject competing
video, poll and homework inference. This is a scheduling risk, not evidence of
a missing model, VRAM exhaustion or a confirmed provider-specific cause.
[Updated rehearsal plan](demo-runbook.md) serializes model stages and avoids
repeated requests while busy. No new AI call or software test was run for this
documentation closure.


## Rehearsal preparation - 2026-11-17

Actual preparation, not timed rehearsal/classroom evidence: existing servers and
single video/homework workers started; shared decoder lock checked free. Existing
demo credentials used for real HTTP login, CSRF form meeting/assignment creation,
synthetic submissions and regular multipart SHORT-EXPLAIN upload. No browser
check or new phone pass is claimed. First upload failed asr_failed; local
same-model diagnostic identified cublas64_12.dll loading failure. Restarting only
the video worker with the existing CUDA directory in process-local PATH enabled
a fresh upload to complete: 33.400 seconds processing, 4.650 transcription,
9.536 summary, English, turbo + Qwen. No driver, system PATH, code, checkpoint or
processing-limit changes. The failed first task remains a failure. Lecturer HTTP
summary/full-transcript pages returned 200, Student requests returned 403,
transcript/summary availability and ordinary expiry were checked; temporary WAV
was absent. These are access/pipeline results, not word-level/summary-quality
acceptance or a classroom result.

A real English AI comprehension draft (7.634 s) and a real private homework draft
(33.172 s) were prepared sequentially after video completion. They remain
unpublished. Student poll access returned 404 and Student own feedback page
exposed no unpublished draft. The homework comparison falsely reports no
supported difference despite different valid approaches; exact quotes do not
validate that conclusion. Lecturer review/correction remains mandatory. Main
meeting has no attendance/comment/active-poll prefilled success. Model decoder
lock was free and no review remained queued/running after preparation.

[Preparation inventory, links, setup detail and limits](demo-runbook.md#preparation-executed---2026-11-17-not-a-timed-rehearsal).
No full software suite, timed rehearsal, AI research round, browser workaround,
new capability, commit or push was performed in this preparation stage.


## User-reported guided rehearsal - 2026-11-17

**Source:** the user's manual report, not checks performed or observed by the
agent. This was a guided walkthrough with pauses, **not** an uninterrupted
ten-minute run and **not** an in-class demonstration. No total/segment times
were supplied. Preparation measurements above must not be used as rehearsal times.

| Capability / step | User-reported observation | What this establishes and does not establish |
|---|---|---|
| Versioned submission / request | A new version was submitted and feedback requested. | Reported use of the version-bound request flow; no new automatic correctness or timing claim. |
| Attendance and comments | Attendance was registered using QR; a comment was sent and appeared to the Lecturer. | Reported functional paths, not physical-presence proof or new expiry/concurrency/permission coverage. |
| Comprehension poll | A comprehension question was generated, a vote was cast from the phone, and results were shown after closure. | Reported generation/voting/results path; the earlier Safari disclosure check remains separate evidence. No new device/browser details or general poll-content accuracy are inferred. |
| Lecturer-reviewed feedback | The draft was edited and published; Alex saw feedback on the relevant submission version. The comparison was manually corrected from no_difference to the distinction between conditional update and locking with recheck. | Reported review/edit/separate-publication/version association. **The comparison correction was human work, not successful automatic comparison.** It does not establish general feedback quality. |
| Video | The video uploaded during the walkthrough completed processing; its summary and full transcript were opened. | Reported upload-to-text viewing path; not word-level transcription verification, summary-accuracy acceptance or proof of ten-minute completion. |

The five approved demo paths now have a user-reported guided walkthrough record.
Experimental English scope, mandatory Lecturer review and known comparison errors
remain unchanged. This record does not establish uninterrupted ten-minute or
classroom evidence. The written results account now summarizes the observed work
in [README](../README.md#results-summary), without relabeling this walkthrough. No additional implementation, software/browser testing,
AI experiment, commit or push was performed by the agent while documenting this
report. [Runbook and preparation history](demo-runbook.md).


## Final documentation review - 2026-11-17

Current SRS, tools index, source/use-case status, homework class/sequence diagrams
and component-test responsibility names were aligned with the existing code.
Disabled-provider milestones are historical; D-56 English integration and D-57
demo scope are current. The class/member names and sequence controls were checked
against source; no application change or AI run was made. A new visual Mermaid
render was not performed: no existing project/bundled Mermaid renderer was found,
and no renderer/browser-test infrastructure was installed. Do not treat source
review as a new visual-render or browser pass. Guided-walkthrough evidence remains
a user report, not uninterrupted ten-minute/classroom evidence. Known comparison
errors, local-only artifacts and the incomplete intentional cleanup/real-data
policy remain explicit. Submission deadline/packaging (Q-08) and classroom live-
processing expectations/acceptable quality (Q-09) are not invented by this review.


## Final visual diagram review and written results

The seven architecture Mermaid blocks were rendered locally with Mermaid CLI
12.2.0 / Mermaid 12.3.0 using the existing Chrome executable in an isolated
headless profile. This is offline document rendering, not application/browser
workflow testing. One actual sequence parse failure was corrected: the semicolon
in `publication blocked; correct/remove and save` was replaced with a comma so
Mermaid does not treat the message tail as a separate statement. No application
behavior changed. Participant columns were widened in render configuration to
avoid splitting long component names mid-word. The resulting diagrams were
inspected as overview images and detailed PNG regions for labels, clipping,
branch frames and arrow readability. [SVG gallery and render provenance](diagrams/README.md).

The earlier source-only review remains a historical record; this review supplies
the previously missing visual rendering evidence. The [written results summary](../README.md#results-summary)
is complete for existing implementation, experiments and user-reported guided
observations. It explicitly preserves the false automatic-comparison finding and
manual Lecturer correction. No application tests, AI experiments, implementation
changes, commit or push were performed in this documentation/rendering round.

## Shared UI and meeting navigation review - 2026-11-17

Stage 1 changes shared CSS typography, spacing, buttons, text fields, status
badges and keyboard-focus styling. The meeting page groups the existing tools
into responsive navigation cards, with breadcrumbs and clearer meeting metadata.
Lecturers retain five tool links; students retain comments, polls and homework
links plus QR registration guidance. Lecturer-only attendance management, video
processing and meeting editing remain hidden from students. No view, permission,
AI provider, URL, form submission or workflow logic changed. Feature-specific
poll, video and feedback templates were not redesigned.

Verification performed:

- Django system check passed. The existing `classroom.tests`,
  `classroom.test_homework`, `classroom.test_participation` and
  `classroom.test_polls` suites passed: **91 tests**, 42.269 seconds.
- Authenticated HTTP checks against the active server confirmed the updated
  meeting template and stylesheet, five lecturer tool cards and three student
  links, with no student edit/video links. All rendered `aria-labelledby`
  references resolved. The existing web server processes were restarted at their
  previous loopback/LAN addresses to clear cached templates; network settings,
  firewall and workers were unchanged.
- Calculated palette contrast ratios: body text/background 12.57:1, secondary
  text/white 6.13:1, primary button text/background 6.27:1, field border/white
  3.52:1 and focus outline/white 6.72:1. This is a color calculation, not a full
  accessibility audit. Existing field labels are retained.
- `git diff --check` passed for the UI files.

The saved browser-access policy blocks automation of the local site. No browser
workaround was attempted, so no before/after screenshots or visual browser pass
were produced. CSS includes desktop, two-column and narrow single-column meeting
layouts, but actual wrapping, keyboard focus and touch behavior still require
manual review. Earlier iPhone reports do not verify this new styling. Review the
meeting page as both roles at desktop width and about 390px wide; use Tab to check
focus and confirm each tool link opens its existing destination. Refresh cached
styles before comparing. UI changes remain uncommitted for user review.

## Shared light/dark appearance and meeting cards - 2026-11-17

This follow-up supersedes the stage-1 palette. Shared surfaces, text, links,
buttons, inputs/selects/file controls, tables, notices, errors, status labels,
selected poll choices and keyboard outlines use semantic CSS variables. Meeting
cards have consistent decorative inline SVG icons and restrained feature accents.
Their destinations and role conditions are unchanged. Poll, video and feedback
templates retain their existing structure. QR images always have a white
background and white border, including in dark mode.

The labelled native Appearance selector offers System (default), Light and Dark.
`static/js/theme.js` runs before the stylesheet, applies a saved preference from
`localStorage`, tracks system appearance when System is selected, and synchronizes
changes between tabs. Storage failures do not prevent in-page selection. CSS
also follows the system without JavaScript; the manual selector requires it.
This reduces initial light-theme flashing but is not a browser-verified guarantee.

Checks performed in this round:

- **111 existing Django tests passed** in 47.504 seconds: foundation, homework,
  participation, polls and videos. Django system check passed.
- **17 JavaScript tests passed**, including five new appearance tests covering
  early system selection/OS changes, explicit selection and reload, blocked
  storage, invalid stored values and cross-tab synchronization. These run in the
  existing Node VM harness, not a real browser.
- Authenticated HTTP checks passed for **16 page responses**: meeting, poll list
  and detail, homework list and assignment for both roles, plus lecturer video
  list/detail, attendance, feedback review and both roles' submission-version
  pages. The selector and early script were present; meeting icon/link counts,
  unique IDs and `aria-labelledby` targets were checked. The theme asset returned
  HTTP 200. Existing web servers were restarted at the same addresses to clear
  cached templates; no network/firewall/worker settings changed.
- Palette calculations passed: tested text pairs were at least 4.94:1 in light
  mode and 7.18:1 in dark mode; field borders against surfaces were 3.56:1 / 4.95:1.
  Feature icon foreground/background pairs also passed 4.5:1. No undefined CSS
  variable references were found. This is not a visual/accessibility audit.

The saved local-site browser permission remains blocked; it was not bypassed.
No new visual, screenshot, real-keyboard or phone pass is claimed. Existing phone
evidence applies to the previous presentation. Manual review still required on
desktop and phone: select Light/Dark, refresh and follow a link to confirm saved
appearance; select System and change OS appearance; inspect meeting cards and
navigation wrapping; Tab through the selector and links; inspect poll selection,
tables, video/feedback text, form controls and QR white background in both modes.
No AI request or business/permission change was made. Changes remain uncommitted
for review.

## Charcoal learning-activity presentation - 2026-11-17

The current palette supersedes the green-brand appearance above: dark mode uses
charcoal page/card surfaces, white primary actions with dark text, and transparent
secondary actions with light text. Hover, keyboard focus and disabled states have
distinct styling. Light mode remains available; Appearance behavior is unchanged.
Green is retained for the shared informational notice treatment rather than the
brand. Meeting activities now precede secondary metadata. Five decorative local
SVG scenes use consistent strokes and sky/lilac/peach accents; they are hidden
from assistive technology and do not represent real progress, scores or outcomes.
Each existing role-appropriate destination retains a full-card link and a short
description. Student QR guidance remains noninteractive; video management remains
lecturer-only. The actual QR image retains its white background/border.

Verification: **111 existing Django tests passed** (48.174 seconds), including the
system check; **17 existing JavaScript tests passed**, including Appearance logic.
Authenticated HTTP checks passed for the same 16 meeting/poll/video/homework and
feedback page responses described above. Checks confirmed role-specific links,
decorative SVG counts, accessible label targets and activities before metadata.
All five rendered SVG variants parsed as XML. CSS variable references resolved.
Calculated primary-button text contrast is 14.57:1 (dark) and 12.25:1 (light);
hover is 11.23:1 / 17.03:1, and disabled text is 5.02:1 / 4.78:1. Tested text
pairs meet 4.5:1 and field borders meet 3:1. An initially weaker light disabled
color was corrected before the final calculation. Protected Gemini/PDF file hashes
were unchanged. Diff whitespace checks passed.

Browser automation remains blocked by the saved local-site permission. These
checks do **not** establish visual quality, keyboard usability or phone layout.
Manual review remains necessary in Light and Dark: inspect illustration sizing,
full-card focus/hover, title hierarchy, metadata, white primary/outlined secondary
buttons and wrapping at phone width. No browser workaround, screenshot, AI run,
business/permission change, commit or push was performed in this round.

## Meeting action-arrow encoding correction - 2026-11-17

The meeting template contained actual mojibake in five arrow strings and four
middle-dot separators. It still decoded as valid UTF-8: the corrupt characters
had already been saved as text. Earlier UI-edit scripts used implicit text-file
encoding; the local default is cp1255. Only the identified broken strings were
corrected, with explicit UTF-8 reads/writes. No whole-project conversion or Hebrew
content rewrite was performed. CSS had no generated `content` declaration causing
the issue. Five text arrows were replaced by the shared local
`templates/classroom/action_arrow.html` SVG, with `aria-hidden="true"`,
`focusable="false"` and `stroke="currentColor"`. Link labels, destinations and
keyboard focus rules remain unchanged. The arrow inherits the action text color
in both themes, without a separate fixed-color background.

All seven prior UI/doc/test files scanned decoded strictly as UTF-8; no remaining
replacement characters or inspected mojibake signatures were found. The valid
middle dot in the base footer was preserved. **24 foundation tests passed**
(8.267 seconds). Authenticated HTTP responses declared UTF-8 and contained five
SVG action arrows for the lecturer and three for the student, with no corrupt
template strings and with accessible link-label references retained. Diff
whitespace checks passed. Browser access remains blocked: currentColor/focus
source checks are not a visual Light/Dark or real-keyboard verification. No
commit or push was performed.

Following user review, the decorative Open-link arrows were removed from all five
activity cards, together with their unused SVG partial and CSS rule. Link text,
full-card destinations and keyboard-focus styling remain intact. The encoding
corrections above remain; the current design has no action arrow.

## Site markup audit and three corrections - 2026-11-17

The read-only site audit found stale disabled-provider wording on the poll index,
missing help-text targets in assignment/submission/review forms, and duplicate
`id_version` values in the lecturer's separate edit/publication forms. The poll
index now describes local English draft generation and explicit lecturer review.
Manually rendered help text has the IDs referenced by Django's `aria-describedby`.
The publication form uses `auto_id='publish_%s'`, preserving its existing POST
field names, version checks and publication behavior.

Four new regressions in `classroom/test_ui_integrity.py` cover unbound/invalid
forms, help/label references and unique IDs, the unchanged version publication
payload and student visibility, and the corrected lecturer-only poll wording
without invoking a model. **69 relevant tests passed** (2.356 seconds), including
these four, homework submission/review, polls and generation-contract tests.
The worker test runtime was isolated from the live worker lock. The preceding
site-wide audit had passed 177 Django tests and 17 JavaScript tests; those counts
are historical, not a new full-suite run after these corrections.

After restarting only the existing web servers to refresh cached templates,
the authenticated HTTP audit again visited 119 lecturer and 48 student pages:
**zero findings** for the inspected ID/reference, label, CSRF, heading/landmark,
encoding and visible-link checks. All linked static assets returned 200. Six
lecturer-only direct URLs returned 403 to the student; anonymous meeting access
redirected to login. Source UTF-8 and diff-whitespace checks passed. Protected
Gemini/PDF hashes were unchanged. No real AI request was made.

The saved browser permission remains blocked. These are server/markup checks,
not a visual, screen-reader, keyboard or real-phone verification. The optional
video-copy, side-by-side feedback layout and cross-page visual refinements from
the audit remain suggestions. No commit or push was performed.

## UI commit review - 2026-11-18

The earlier "uncommitted" notes describe their respective review stages. The
approved UI change set includes the final charcoal/light palettes, Appearance
selection, local activity illustrations, corrected encoding and final arrow-free
cards, poll wording, form accessibility fixes and their regression tests.
Pre-commit source review also corrected three malformed shadow declarations
(`var(...)` followed by hexadecimal suffixes) to use the existing `--shadow`
token. Variable references and the corrected declarations were checked without
rerunning the software/AI suites. Validation relies on the recorded 69 relevant
tests after form fixes, the preceding full 177-test audit, 17 JavaScript tests and
authenticated HTTP checks. Visual browser/mobile verification remains limited
by the saved browser permission; no new visual or AI success is claimed.

## iPhone login heading and safe-area correction - 2026-11-18

The user reported joined words in the login heading and possible overlap between
the header branding and the iPhone status area. The heading had `start<br>to`
without a space, and the narrow-screen CSS hid that break. It is now plain text,
`A clear start to every class.`, with natural wrapping; the obsolete break-hiding
rule was removed. No font, palette or business-flow change was made.

The header is in normal flow, not fixed/absolute. The viewport now uses
`viewport-fit=cover`; the header reserves `safe-area-inset-top`, and page sides/
bottom plus the focused skip link respect their safe-area insets. Insets fall
back to zero, so no constant desktop top spacer was added. This addresses the
CSS safe-area boundary; the reported Safari overlap has not been visually
reproduced or confirmed resolved by the agent.

**24 foundation tests passed** (8.581 seconds), including login/access checks.
HTTP checks confirmed the exact heading, no forced heading break and the updated
viewport. The existing LAN server needed a restart to discard its cached old
templates; network/firewall settings and workers were unchanged. Browser access
remains blocked. User verification is pending in iPhone Safari, portrait and
landscape, after refreshing the login page; check branding against the status
area and heading wrapping in Light/Dark. No commit or push was performed.

## My courses vertical card list - 2026-11-18

The course list is now a single column at desktop and mobile widths. Desktop
cards place a reusable local learning SVG on the left, title/description in the
middle and the existing role plus Open course action on the right. At 640px and
below these areas stack, with a full-width action. Styles are scoped to the
course list; the existing theme tokens provide charcoal surfaces/white primary
actions in Dark and the Light palette. No new data, progress indicators,
permission rules or sorting were introduced. The view still orders current-user
memberships by course code. Existing empty-state and missing-description text
remain. Decorative art is hidden from assistive technology, and each Open action
has a course-specific accessible name.

**24 foundation tests passed** (8.293 seconds). Additional template checks used
three synthetic courses, including a long title/description, mixed-language text,
HTML-like content and an empty description; order, escaping, unique IDs, label
targets, illustration markup and the no-course state passed. The generic SVG
parsed as XML. These are markup/server checks, not visual rendering. Browser
access remains blocked: desktop alignment, narrow-screen overflow, focus and
Light/Dark presentation require user review. Previous login/safe-area changes
were preserved. No AI request, commit or push was performed.

### Desktop screenshot follow-up

The user's screenshot showed two columns and oversized SVG art instead of the
intended horizontal rows. Both servers returned the updated CSS on direct HTTP
inspection, but its URL had no version marker and no Cache-Control response
header. A stale browser stylesheet is consistent with the screenshot; the
client cache could not be inspected directly. A version query was added to the
stylesheet URL. The list no longer carries the legacy two-column `course-grid`
class and explicitly defines a single-column grid. Illustration size is reduced
to 128 by 80 pixels, with intrinsic SVG dimensions as a fallback, smaller artwork
panels, and more compact card spacing/title sizing. Desktop row content still has
three areas; the course list itself always has one column.

**24 foundation tests passed** (8.459 seconds). Server/markup checks confirmed
the new versioned asset URL, current stylesheet, removed legacy grid class and
bounded SVG dimensions for both roles. Synthetic course/empty-state checks remain
valid. Browser access is still blocked; the corrected desktop/mobile appearance
awaits user review, and is not certified by these checks. No commit or push.

### Header wordmark refinement

The Teaching Tool link retains its text and destination, with a small decorative
local open-book SVG replacing the letter T. Subtle word-weight/color differences
use existing Light/Dark tokens. The SVG has explicit dimensions and is hidden
from assistive technology; the brand target is at least 44px tall and retains
keyboard focus styling. The stylesheet version was updated to refresh cached
styles. Django system check and authenticated HTTP name/SVG/destination checks
passed for both roles. Visual browser/phone confirmation remains pending because
browser access is blocked. No external assets, new behavior, commit or push.

### User-reported visual review and approval - 2026-11-18

The user reported reviewing the current presentation, said that it looks very
good, and approved saving the changes. This is user-reported visual acceptance
of the presentation they viewed, not an agent-performed browser test. No explicit
device/browser, viewport, additional page or Light/Dark coverage was supplied;
do not infer those checks or a separate confirmation of the iPhone safe-area
issue from this report. Earlier pending-review notes describe their respective
stages. The header/login corrections, wordmark and course-card layout are now
approved for a focused commit. Validation relies on the checks already recorded;
no additional design, software test or AI experiment was performed for this save.

## Selected demonstration-group workflow - 2026-11-18

User-approved D-58 extends UC-05 only. The software now previews 2–4 latest-owner
versions, confirms one frozen source/context snapshot, and atomically creates a
ReviewBatch plus all private child ReviewJobs. The selected-group scope is explicit;
it does not replace the individual route's all-eligible-peer rule. Each draft still
requires separate Lecturer editing/publication. There is no group-wide publish.

**206 server tests passed** in 55.941 seconds with file-backed SQLite and isolated
test runtime, no skips. **20 JavaScript tests passed**, including three new group
status-polling cases. Of the server suite, **25 new group tests** cover:

| Component / responsibility | Risk and software evidence |
|---|---|
| homework_batches.prepare_preview / confirm_group | Changed version/instructions/criteria/rubric/language; expired or wrong-requester token; invalid group or input limits; active-version conflict; rollback after a simulated second-child insert failure. |
| ReviewBatch / ReviewJob constraints | Duplicate and concurrent same-token confirmation; conflicting independent groups; one active review per version; all children or no group. |
| Frozen selected sources | Latest version per selected owner only, no self-version comparisons or unselected owners; later resubmission/rubric change cannot alter frozen jobs. |
| homework_worker.process_batch_job / LocalHomeworkReviewer.reserve_resource | Busy resource invokes no inference and starts no processing clock; bounded queue expiry; reservation before the 180-second clock; expiry recheck after reservation; interrupted restart without replay; access revocation; late result rejection. |
| Resource handoff / local adapter | A real temporary OS lock spans both mocked child calls; group children receive the reservation flag; single-review calls do not, retaining their own child lock. No actual model or child inference process is started. |
| Partial results and publication | Individual failure does not cancel another job; comparison failure retains only a private personal draft; explicit individual-only publication; other feedback stays unpublished; Students see only matching published content and the selected-group scope notice. |
| Group routes/state API | Login/course/role/parent binding and CSRF; no raw work/rubric snapshots in status JSON. |
| homework_groups.js | Safe text nodes, real counts, visible-page five-second reads, stopping after completion/access loss; no generation request. |

Two initial test corrections were made transparently: the busy-label assertion
selected a different job because default job order differs from table order; it
now checks the matching job ID. A test-method placement error introduced while
adding reservation coverage was corrected. Final counts above are the successful
runs. Existing individual-feedback, poll, video and other website suites remained
green; no real AI experiment or new comparison-quality measurement was performed.

Queue deadlines are confirmation +15 minutes and survive restart. Pending expired
jobs become failed on worker or authorized group/status reads; overdue display
guards prevent indefinite waiting even when the worker stays stopped. Processing
starts only after reservation and keeps the existing 180-second limit. Interrupted
running work fails on restart, and stale running group work expires on status
reads. No automatic inference retry occurs. Review/publication remains private and
separate; known real-model false comparisons and human corrections still apply.

Migration 0011 was applied to the local development DB after an ignored backup.
No live group/review request was created and no AI worker was started by the
implementation checks. The homework class diagram was updated and rendered with
the existing offline renderer; this is document inspection, not website browser
validation. Browser access remains blocked, so the new group UI awaits user review.
Other proposals (manual polls, comment export, lecturer video insights and load
testing) were not implemented. No commit or push was performed.

### Real-model group follow-up — 2026-11-19

After the user confirmed group 1, two sequential normal worker invocations
produced private drafts for Alex Version 1 (47.575 seconds) and Casey Version 1
(34.458 seconds). Authenticated HTTP checks verified frozen sources, ownership,
private drafts and denied peer access. They did not perform visual browser
acceptance or publication. Neither draft was edited/published by those checks. See the
[full process/content assessment](homework-group-acceptance.md) for preserved
preserved evidence, model configuration and the subsequent manual publication
check. The earlier no-real-model statements describe the implementation milestone.

Quality did not pass: both comparisons returned `no_difference`, missing the
known conditional-update versus row-lock difference and Alex's duplicate-topic
omission. Alex's personal feedback falsely credited that topic. Quote matching
passed 21/22 overall and 6/6 comparison quotes, demonstrating that exact quotes
can still accompany unsupported conclusions. Casey's individual findings matched
the expected coverage in this sample. No additional software suite, inference
retry or prompt revision was run for this follow-up.

Final focused checks after status-count wording and state-helper expiry refinement:
**55 homework/group/UI regression tests passed** in 2.561 seconds, no skips, plus
all three group JavaScript tests. The earlier 206/20 suite result remains the
broader regression record. Live authenticated HTTP GET checks opened the existing
synthetic assignment and new selection form as the Lecturer at loopback and LAN
addresses, verified unique IDs/label targets and denied Student access. DB counts
confirmed no live ReviewBatch/ReviewJob was created. No worker or real AI request
was started. The offline diagram source/SVG manifest hashes and local document
file targets were checked; poll/video/attendance/style files and protected Gemini/
PDF hashes remained unchanged. Visual website acceptance remains pending.

### User-reported separate group publication — 2026-11-19

The user reported manually verifying that Alex sees the corrected feedback and
Casey remains an unpublished draft. This confirms the reported separate-
publication workflow, not automatic comparison correctness. The supplied review
corrections addressed missing duplicate-topic coverage, the actual approach
difference and the malformed quote. Corrected publication is human-reviewed
content; original model findings remain preserved separately. No additional
browser/device scenarios or agent-performed visual check are inferred.


## Submission closure validation - 2026-11-19

Final file-backed isolated Django suite: **215 passed**, 21.100 seconds, no skips.
Final JavaScript suite: **21 passed**, about 0.151 seconds. No real AI is invoked
by either suite. Initial focused checks passed; the later full run supersedes
that count after cross-segment and cleanup coverage. Migration dry-run reported
no changes. Clean source-only install/migrations/seeding/login/server startup
passed as recorded in [operations](operations.md). No demo data was deleted.

| Component / responsibility | Risk | Existing/new evidence |
|---|---|---|
| ManualPollForm / create_manual_draft / Poll origin | Accidental AI dependency, forged answer metadata, duplicate options, role leak | ManualExportTests: both types, model factory must not run, manual provenance, Hebrew, existing publication/vote/disclosure, draft Student 404 and role 403 |
| participation_views.requests_export | Cross-user export, spreadsheet formula execution, source mutation | ManualExportTests: Lecturer-only exact meeting, Student/outsider denial, literal `= + - @` and Hebrew round-trip; database text unchanged |
| lecturer_review_contract | Unmatched/repeated quote, wrong generated time, segment cutoff | ReviewContractTests: exact quotes, zero/max points, rejection, cross-segment time binding. Writing-system checks reuse summary validation; no semantic certification |
| video_worker / LocalQwenLecturerReviewer | Optional failure discards completed work, interruption, expired private text | OptionalReviewTests: success/zero points, invalid quote/failure, summary/transcript preserved, restart/interruption, owner role and direct access, expiry clears points |
| videos.js | Completed optional stage never becomes visible or loses transcript link | New JS regression: one reload and retained transcript link; earlier summary/polling tests retained |
| cleanup_demo | Unintended deletion or unknown scope | Preview test proves no mutation; --apply requires explicit seeded course. No apply was executed outside isolated software tests |
| Attendance / PollVote HTTP + SQLite | Burst write contention, duplicates, count corruption | Versioned load probe: 80 then 100 users, true loopback HTTP/session/CSRF, expected duplicate handling, exact counts and latency conditions passed |

The optional review stage used a real installed Qwen model on the saved SHORT
transcript. Initial failures and unsupported criticisms, the final unedited
suggestions/timings, and the narrow usefulness assessment are in
[closure results](submission-closure.md#real-local-lecturer-review-output). This is
adapter evidence, not a fresh full MP4/phone/browser test or broad semantic quality
pass. No feedback/comparison experiment was repeated. The prior group model failure
and user-reported corrected Alex publication/private Casey remain separate evidence.

Browser observation of loopback was denied by saved permission again. No workaround
was used. New HTML is server-tested; Light/Dark/narrow visual acceptance for the
new manual form and optional report remains manual. Prior Safari/iPhone and guided
rehearsal reports retain their stated scope. Item 10 remains not performed.

## Recorded manual closure reports - 2026-11-22

Recorded from the user's preceding messages, not from agent browser execution:
the user confirmed creating/saving and separately publishing a manual poll, and
then reported completing the meeting-comment XLSX export/opening check. These
reports establish those observed flows only. No additional formula-safety,
individual-cell, device, Light/Dark or narrow-layout coverage is inferred; the
automated export-safety evidence remains separate.

A current read of the development database found no completed lecturer-review
video task. The earlier real-model review probe is a local experiment result,
not an existing website task. No new inference/upload was performed for this
manual-check preparation. The website was started on loopback and the previously
authorized exact home-LAN address without firewall changes or AI workers.

Both pages of the local source PDF were extracted and visually inspected again.
Page 2 has eleven populated To Do items; it specifies no delivery channel,
archive/document packaging convention or deadline. Page 1 requests an approximately
ten-minute classroom demonstration; no slide deck is specified. Delivery details
and defense arrangements require external confirmation. Item 10 stays not
performed; experimental homework comparison failures and human corrections remain
explicit. The PDF and existing Gemini changes were not modified or committed.
