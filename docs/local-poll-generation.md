# Local English Poll Draft Generation — 2026-11-11

## Implemented boundary

The existing PollGenerator interface now returns LocalPollGenerator. A Lecturer chooses comprehension/opinion, English and pasted material (1–6,000 Unicode characters, including whitespace); the normal CSRF POST invokes the installed Qwen3 8B and saves valid output as origin=ai, status=draft. Generation runs outside database transactions; current course membership is rechecked under a short write lock before saving. Editing and publication are separate existing actions; there is no automatic publication or canned fallback.

English is the initial generation-form default. Hebrew remains an explicit choice with an English-only generation message, and form/service/provider boundaries reject Hebrew generation before inference. Existing Hebrew draft editing, publication and voting remain unchanged; their validators do not inherit the English-only generated-output restriction. Material may be pasted in either script, but the generated output must be English. Failure responses keep the bound form/material and do not create a poll.

## Runtime and operational behavior

Uses only existing .ai-lab Python and the bundled Ollama 0.40.14 executable/model store. Pinned Qwen3 8B Q4_K_M weights a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f and manifest b3d9ba7c899cfd112df2574c6a91458a70b724c5e4e50dfffd75574b2d1648e7 are verified through the existing read-only checkpoint helper. No changes were made to video transcription/summarization engines or their experiments, and no Gemini call or file mutation occurred.

Each request uses an isolated child/private loopback-only Ollama service, cloud disabled and system proxies bypassed. No arbitrary provider URL or remote/paid fallback is configurable. The request has a 120-second startup/generation deadline, no automatic retry, and a busy message if the shared local compute lock is already held. This serializes against video AI without changing that pipeline. The synchronous create form may wait while generation runs; 6,000-character maximum latency/concurrent classroom throughput is not established by the short examples. The model unloads and its private service exits afterward; Windows ProcessTree ownership and watchdogs bound orphan compute. No additional persistent Ollama service is needed.

Runtime settings: temperature 0.1, seed 42, context 8192, thinking false, max 768 output tokens, type-specific JSON schema. Private input/output files live under ignored .local/poll-generation and normal/error cleanup removes the per-request temporary directory. Unexpected process/machine termination may leave private temp files; no new failed-input retention policy is claimed. No prompt/output content is printed in model protocol logs. Model downloads are never initiated by the adapter.

## Pre-save checks and limits

Both provider and service validate exact type-specific fields, one nonempty question, exactly four distinct nonempty options and English-compatible script. Generated duplicate checking normalizes whitespace/case/trailing punctuation. Comprehension requires one integer index 0–3 (not a boolean) and a nonempty explanation of at least six words with sentence-ending punctuation; it rejects obviously incomplete outputs. Opinion forbids all answer/explanation fields. Output-size limits and a normal stop reason reject oversized/truncated responses. These generated-only rules do not narrow existing Hebrew editing.

These are structural/completeness heuristics, not proofs of a correct answer, semantic uniqueness, grounded explanation, natural grammar or a genuine opinion. The UI explicitly requires Lecturer meaning/content review and editing before a separate Publish action. No model result is represented as vetted simply because it passes checks.

## Actual local validation on a new topic

The new material described stacks as LIFO, push/pop with A then B returning B, queues as FIFO with A then B returning A, and practice through diagrams/tracing/sandbox/discussion. Real normal-form/view requests used CSRF-enforced authenticated in-process Django clients and the production local provider, with no fake model. This was not browser automation.

- Course DEMO-CS101; meeting **Local AI polls: stacks and queues** (6).
- Comprehension poll **3**, generation **9.652 s**: asks which structure returns the newest item; one marked answer Stack with a full source-supported LIFO explanation. Four choices are distinct; list/tree distractors are not explained by the source, so Lecturer review of wording remains appropriate. Edited the title to add Stacks and queues, then published. Student draft HTML/JSON returned 404 before publication. Answer key/explanation were absent from active student HTML/JSON, then appeared only after closure. Student voting succeeded. Final state closed.
- Initial opinion poll **4**, generation **8.114 s**: passed structural checks but incorrectly asked which structure is preferred when newest-task-first behavior is required. That is effectively a factual LIFO question. The mechanical route check had already edited/published it; semantic review caught the defect and this newly created test poll was explicitly closed, not deleted or rewritten. Its raw output is retained only in ignored experiment evidence.
- The bounded prompt revision **poll-en-v2** explicitly forbids constraints that determine the engineering answer and prefers learning-activity preferences. Opinion poll **5**, generation **9.520 s**, asks which practice activity the respondent prefers: diagrams, sandbox code, group discussion or step tracing. All four are legitimate preferences with no answer key. This revised draft was semantically reviewed, edited with the same topic prefix, separately published and voted on; student draft HTML/JSON were 404 before publication and no correctness fields appeared while active. Final state active.

No general semantic validator was added to conceal the initial opinion defect, and no further generation retry loop exists. The revised provider still requires Lecturer judgment. Raw drafts before editing, source text and measured evidence remain ignored/local. The two successful final drafts were presented to the user without rewriting their generated content.

## Manual Lecturer check

With the existing website running, sign in as lecturer_alpha, open a course meeting -> Polls -> Create a poll draft. Choose English and type, paste material, then Generate draft. Inspect/edit all fields, save and use Publish separately. A busy/unavailable/invalid result returns to the same material form. Selecting Hebrew explains the current generation limitation; use existing Hebrew drafts or the separate labeled demo command to check Hebrew lifecycle behavior.

The test meeting above contains comprehension 3 (closed), initial rejected opinion 4 (closed) and reviewed opinion 5 (active). Close an active poll before publishing another in the same meeting. The usual one-final-vote, live Lecturer results and post-close Student disclosure rules remain unchanged. Browser/phone and larger-input/classroom-load acceptance remain open. Tests and retained limitations are in testing.md. No commit or push in this stage.
