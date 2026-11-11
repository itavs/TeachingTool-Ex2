# Local Automatic Video Summaries

## Current implementation (2026-11-08)

New normal meeting MP4 uploads now continue from real turbo transcription into Qwen3 8B summarization. Existing extraction/transcription-only tasks keep their original results and do not acquire summaries automatically. After transcription returns, the worker removes WAV, then commits the transcript, language, provenance and seven-day expiry before invoking the replaceable summary adapter. A WAV cleanup failure fails the job instead of proceeding. No fake/canned summary is selectable in runtime; tests alone inject fixtures.

Success renders **Automatic summary**, one short paragraph and 3–5 key points in the recording language, with a full-transcript link and **This summary is based on an automatic transcript and may contain errors.** Summary text is escaped in server-rendered HTML, not inserted as HTML by JavaScript. Owner-only status JSON carries availability flags rather than generated text; one guarded reload renders a newly ready summary. Other site pages remain usable.

## Model and isolated runtime

- Existing qwen3:8b / Qwen3 8B Q4_K_M; weights digest a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f; pinned local manifest SHA-256 b3d9ba7c899cfd112df2574c6a91458a70b724c5e4e50dfffd75574b2d1648e7.
- Uses the installed .ai-lab Python and Ollama binary 0.40.14 with existing private model blobs. No installation/download or hosted inference. Missing/different manifest or blobs fails explicitly; /api/generate does not pull a missing model.
- The adapter launches an isolated child which owns a short-lived Ollama service on an OS-selected loopback port, with cloud disabled and proxies bypassed. No arbitrary URL is configurable, and the unrelated desktop Ollama service is not used. Local loopback HTTP is process communication, not an external-provider request.
- ASR finishes/unloads before Qwen starts. A shared OS lock prevents overlapping media/ASR/summary compute. One model and one slot, context 8192, thinking off, temperature 0.1, seed 42, at most 768 output tokens, structured JSON schema. Truncated/nonconforming output fails, with no automatic retry or prepared fallback.
- Windows kill-on-job-close process-tree ownership covers the summary child, private Ollama server and model descendants. Deadline/interruption/parent death closes handles and terminates the owned tree; a child watchdog and explicit normal cleanup also apply. The concrete owned-grandchild termination test uses ordinary Python processes, not a real GPU hard-crash experiment. This installed runtime is Windows-specific.

## State, deadline and partial success

New states after transcription are Loading local summary model -> Summarizing transcript locally -> Summary completed, or a persisted failed stage/reason. The original 600-second worker-claim deadline is passed unchanged through validation, extraction, ASR, Qwen loading and generation. Queue waiting remains separate; each stage does not receive a new budget. Heartbeats and independent maintenance/restart recovery include the summary states. No invented percentage is shown.

A summary failure, invalid output, unsupported output script, model unavailability, timeout or interruption does not erase a saved transcript. Its full-text route stays available to its authorized owner until expiry. Summary failure reasons do not expose raw exceptions, paths, prompts or credentials. Private summary.input.json / summary.pending.json files are deleted in adapter/worker finally blocks; failure/recovery/maintenance also remove leftovers. No transcript/summary text is emitted in subprocess protocol logs.

## Privacy and retention

Only the uploader while still a Lecturer member of the same course may access task/summary/transcript, including copied/direct URLs and status JSON. Another same-course Lecturer is not the owner. Demotion/revocation blocks access. Summary text is rendered only while both its own expiry and source transcript access remain valid. It expires at min(summary creation +7 days, source transcript expiry), so it never outlives its source. At the exact deadline, a direct task URL contains no generated content; maintenance clears paragraph/points and transcript/segments. Metadata/history remain. Physical deletion requires maintenance/machine uptime; expiry checks apply independently of cleanup. MP4 remains under the existing maximum 24-hour policy.

## Grounding prompt and evidence limits

Prompt lecture-grounding-v3 requests actually explained topics rather than introductory promises, preservation of negations and relationship direction, explicit example scope for code claims, and omission of unclear details/uncertain identifiers. It forbids constructing guessed camelCase names from spaced speech. An output-language/script check rejects unexpected writing systems (while allowing Hebrew/Latin and mathematical Greek); it is not semantic language/accuracy verification.

The initial v2 prompt still overstated static-function coverage and reconstructed minimumCarPrice. A bounded v3 revision removed the static-function-coverage statement in the two saved-input checks and retained boat inheriting from vehicle. It still inferred class ownership and access through the class in STATIC, beyond the explicit transcript, and not every bullet adopted example scope. These are unresolved grounding limitations despite the prompt; automatic format validation cannot prove meaning or source accuracy.

Two saved turbo-input checks used the real adapter (each starts/loads its own local service): STATIC 10.382 s wall / 7.607 s model request, SHORT 8.719 s wall / 5.943 s model request. Exact observed measurements and claim review are in testing.md; cold service startup makes these incomparable with the earlier warm-model CLI probe. Generated words were not edited. Full inputs/raw output remain ignored local artifacts.

A full STATIC upload produced an unexpected Korean word. That invalid output was snapshotted locally for diagnosis and then removed from the new acceptance task; the task was marked summary-language failure and its original transcript retained. This repair did not change old transcripts. An additional full SHORT upload was required to verify the successful end-to-end route after the validation correction. The subsequent user-reported SHORT interface review is recorded below; no STATIC success is inferred.

## Run and manual review

Use the existing separate website, run_video_worker and run_video_maintenance commands from README; no additional persistent Ollama service is required. Each summary job starts/stops its own service. After reboot restart those three services. From a meeting, upload a new MP4, return to its task and wait for Summary completed. The page reloads once to display the summary and full-transcript link. A failure shows its actual stage/reason; use the transcript link when available. Do not infer that a displayed summary is verified; review important negations/technical claims against the recording. Source-grounded quality and broader capacity remain open.

## Actual full-route acceptance

Both checks used the normal authenticated CSRF-enforced MP4 upload view/middleware through an in-process Django client and the separate real worker, not browser automation:

- STATIC, Test Meeting / DEMO-CS101, job 03b0bfec-f199-4aa1-9dfc-0e26eb2225f9: 57.276 s ASR, 7.745 s model-summary request, 77.416 s total. Unexpected Korean script in the generated summary exposed a missing validation case. The original invalid output was kept in ignored diagnostic storage, then invalidated on that newly created acceptance task after adding the language check. Its transcript is unchanged and owner-accessible; the task now explains summary-language failure. This was an explicit one-task repair during development, not an automatic retry or a successful language-quality pass.
- SHORT, same meeting, job dd68e11b-2d34-40ae-9fb5-9bca05e14c7b: 4.835 s ASR, 5.972 s model-summary request, 21.985 s total; Summary completed. Owner task and full-transcript pages returned HTTP 200; all generated paragraph/points were verified in escaped HTML. Its summary matched the saved-input v3 English check exactly. The inheritance direction remained boat -> vehicle.

WAV, transcript.pending.json and both summary IPC files were absent after both tasks. The private per-job model services exited; only the unrelated desktop Ollama service remained. Seven pre-existing jobs retained exact transcript/segments/model metadata. Tests: 126 server tests, 52.922 s, no skips; 12 JavaScript tests. The subsequent user-reported SHORT interface review is recorded below. Details and evidence boundaries are in testing.md. No commit or push.

## User-reported interface acceptance

The user signed in as lecturer_alpha and reviewed SHORT task dd68e11b-2d34-40ae-9fb5-9bca05e14c7b: summary/points were readable and the link opened the full transcript of the same video. This is a user-reported interface/navigation result, not recording-grounded accuracy, phone acceptance or a replacement for server authorization tests. STATIC retains its distinct saved-transcript success versus MP4 summary-language failure with a preserved transcript. A language regression test explicitly permits Hebrew with static and Car alongside the unexpected-script rejection test.
