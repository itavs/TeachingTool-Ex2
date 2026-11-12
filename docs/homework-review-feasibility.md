# Local Homework Review Feasibility — 2026-11-11

## Pre-run independent source map

This map was prepared before model generation, directly from the existing three synthetic samples and assignment criteria. It will be used to audit the outputs and is **not supplied to the model**. No real student work/personal data is used. The case IDs below are local audit labels, not peer identities exposed in Student output.

| Source | Atomicity / rollback | Duplicate versus capacity | Overbooking safeguard | Cache trade-off | Approach |
|---|---|---|---|---|---|
| A | One transaction groups both changes; explicitly says rollback cancels changes on failure. | UNIQUE(student,course) handles duplicate enrollment separately. | Conditional update if a seat remains, or suitable isolation. | Faster reads, stale information, final DB authorization. | Conditional update/isolation; no explicit row lock required. |
| B | Explicit transaction grouping and rollback if either operation fails: rollback IS present. | Incorrectly claims UNIQUE prevents two different students taking the last seat. | No sound capacity safeguard; UNIQUE is misapplied. | Recognizes faster reads but wrongly approves from cache without checking DB. | Unsafe UNIQUE/cache-only reliance contrasts with peers. |
| C | Isolation transaction is mentioned, but failure/rollback behavior is explicitly omitted. | Same-student duplicate handling explicitly omitted. | Isolation or course-row locking followed by availability recheck. | Recognizes stale-data risk and refuses cache-only approval. | Explicit lock/recheck is distinct from A's conditional-update option. |

A covers all four criteria; do not invent mandatory gaps. B needs correction of capacity/UNIQUE and cache authorization, plus a valid overbooking safeguard; do not report rollback absent. C needs atomic-failure/rollback and duplicate prevention, while retaining credit for its correct concurrency/cache explanation. Comparisons must identify actual topic/approach differences, not merely rank answers or treat majority agreement as correctness.

The single-submission case uses A alone: personal review remains possible, comparison must be false and explicitly state no other submissions are available. Peer texts will be passed without IDs/names; feedback must not reproduce peer works or identify peers, including by language. A detailed pre-run map with UTC timestamp and source hash is stored in ignored local audit data.

## Executed local protocol and timing

After the poll-stage commit/push, four real local generations used the installed Qwen3 8B Q4_K_M via a dedicated cloud-disabled loopback Ollama 0.40.14 service. Model manifest SHA-256 b3d9ba7c899cfd112df2574c6a91458a70b724c5e4e50dfffd75574b2d1648e7 and weights digest a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f were verified with the existing helper. Context 8192, temperature 0.1, seed 42, thinking disabled, max output 1536 tokens, structured JSON, 180-second request timeout and no retries. Each of A/B/C was reviewed against the other two original sample texts; A was also reviewed with no peers. No grade, code execution or real student data was requested.

The expected-answer map was prepared at 2026-11-11 13:05:24 UTC; the run directory was created at 13:06:18 UTC. Each input included only the assignment instructions, four original criteria, target text and anonymous peer texts. Local sample IDs, the supplied manual_review_expectations and this independent map were NOT given to the model. The map/source hash and prompts/raw responses are retained under ignored .ai-lab/results/homework-review. No raw/full peer works are published in this report.

| Case | Wall time | Model loading | Output generation | Outcome |
|---|---:|---:|---:|---|
| A + two peers | 14.859 s | 2.690 s | 11.717 s | False mandatory gaps contradict the target; confused comparison; mixed-script Hebrew. |
| B + two peers | 7.363 s | 0.003 s | 6.919 s | Rollback quote recognized, but central UNIQUE/cache errors inadequately identified. |
| C + two peers | 10.427 s | 0.004 s | 10.145 s | Real rollback/duplicate omissions recognized; unsupported recommendations and comparison errors remain. |
| A alone | 7.929 s | 0.004 s | 7.732 s | Personal feedback and false comparison flag; required explicit no-other-submissions message missing. |

All four stopped normally, with four criterion indices 0–3. Later runs reused the loaded model; these are single observations, not speed guarantees or a language benchmark. No new RAM/VRAM peak sampling was collected. The actual CLI/HTTP process is loopback local inference; no external API, model download, paid service or Gemini access occurred. The model was unloaded and the dedicated experiment service stopped after the run.

## Source audit against the pre-run map

### A

Rollback, duplicate prevention, conditional capacity update/isolation and stale-cache safeguards are all present. The model credits rollback/UNIQUE/cache, but then alleges no condition checking remaining capacity even though its own target_evidence quotes the condition succeeding only if a seat remains. It also invents a gap about different students without acknowledging the target's separate capacity safeguard. All four criteria receive partial without a supported reason. Recommendation to reconsider UNIQUE duplicates something already present. Peer comparison uses individually numbered peers, treats unsafe cache discussion too generously and fails to clearly compare A's conditional-update approach with C's lock/recheck. This is not reliable feedback on an otherwise complete target.

### B — explicit rollback regression check

The target explicitly says transaction grouping with rollback if either change fails. The model quotes this verbatim under criterion 0; it does NOT repeat the earlier claim that rollback is absent. However, its Partial assessment is unexplained and the main strengths do not acknowledge that coverage. Recognition of a rollback string is therefore not a full rubric-quality pass.

The statement that UNIQUE prevents duplicate enrollment is supported, but the strength says this addresses the core simultaneous-last-seat issue, conflating duplicate prevention with capacity concurrency. The target's distinction is incorrect rather than merely unmentioned; describing it as absent loses the actual misconception. The recommendation to distinguish them is useful but does not explicitly correct UNIQUE's last-seat guarantee or propose the needed conditional update/isolation. The unsafe cache-only approval is quoted but not called out in gaps/recommendations. Criterion 2's claimed exact target quote is a rewritten combination of source sentences, not an exact quote (the automatic substring audit flagged it).

Its comparison identifies a real difference in whether duplicate/capacity separation is discussed, but does not explain the concrete conditional-update versus row-lock solution alternatives or fully expose cache-only authorization. It uses Peer 1/Peer 2 rather than the requested aggregate comparison. No actual person is identified, but this does not meet the requested output format/privacy guardrail.

### C

The model correctly identifies missing rollback and same-student duplicate protection, consistent with C's explicit self-acknowledged omissions. It also gives credit for isolation and cache staleness. However, it invents a requirement to use cache as overbooking protection, despite the target correctly rejecting cache-only approval. Suggesting that transactions with isolation are the only protection is unsupported and excludes the conditional-update alternative in A. Its evidence rows are mismatched to criteria (e.g. cache text for overbooking, omission text for cache), despite being exact source strings. It attributes course-row synchronization to both peers without support. Exact quote presence alone does not establish a valid rubric assessment.

### Single submission

The model provides strengths, no gaps and optional-sounding recommendations. It sets comparison_performed=false and does not invent a peer comparison. Its comparison text is exactly **אין תובנות משותפות**. That does not explicitly say there are no other submissions yet, so this required message check **failed**. The four assessment labels also contain a Hebrew misspelling. No source-based evidence suggests that missing-rollback feedback should be added for A. This run must not be described as a complete no-peer acceptance pass.

## Privacy, evidence and language checks

No source IDs/names were passed into prompts or reproduced in outputs, and no complete peer work was emitted. The three comparison runs nevertheless invented individual ordinal Peer labels, against the aggregate-only instruction. These are synthetic local audit inputs; no student-facing website was created or feedback published. The outputs would not be released to students unchanged. Hebrew A/C also contain Arabic-script fragments/awkward wording, creating a separate readability/language problem.

15 of 16 target_evidence fields were exact substrings (including empty evidence), but several cited the wrong criterion and one B quote was rewritten. Correct JSON/criterion count/boolean flags did not establish meaningful review. No numerical accuracy grade, real-world student benchmark, plagiarism judgment or human-source transcription claim is made. The samples are theoretical answers; optional code examples are not a mandatory rubric requirement.

## Conclusion — do not connect this reviewer to the website yet

Current results do not justify a student-facing homework feedback/comparison integration. Serious missing-error and false-gap findings remain, especially when peer comparison is added. Before another approval decision, try a bounded redesign that first evaluates target criteria with exact evidence, then compares anonymized approaches separately; verify quoted evidence automatically and test it against an independently written map. These are proposals, not implemented features or guarantees of semantic correctness.

A future no-peer notice should be deterministic application text based on the actual peer count, rather than entrusted to model phrasing; the model may still provide personal feedback. Keep peer IDs/names/full works out of Student output and avoid individual peer labels. The teacher/user should evaluate quality on these same checks before an integration is approved. No homework website code was written; no design work was started.

The standalone probe executed four times without generation retries and was compiled; no website regression rerun is claimed for this experiment-only change. The experiment code and findings remain uncommitted, separate from the already-pushed poll stage. Gemini file hashes remained unchanged.

## Published experiment closure and reproduction

This experiment round is closed, with model-quality readiness **not accepted**.
The exact synthetic source fixtures, independent expectation maps, probe code and
recorded readable inputs/prompts/outputs are now included in the experiment
publication. See [reproduction](../experiments/local_ai/README.md#focused-homework-probes---reproduction)
and [recorded evidence](../experiments/local_ai/results/homework-focused/).
Earlier local-only/uncommitted statements above describe the original run stage;
this section supersedes them for those published artifacts. Model weights,
services/environments and original service logs remain local-only. No new inference
or website integration occurred in preparing the closure. The per-criterion probe
now runs from published fixtures by default, without a demo database or missing
local map file. Findings and generated text above are unchanged.
