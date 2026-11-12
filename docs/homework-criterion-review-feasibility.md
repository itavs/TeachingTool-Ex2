# Per-Criterion Personal Feedback Probe - 2026-11-12

## Scope and method

Local-only synthetic experiment, no website changes or peer comparisons. Read
Stacks and queues assignment 1 and student_alex versions 1/2 through read-only
SQLite. Its exact instructions are: Explain how a stack and a queue remove items.
Give one everyday example of each. Criteria: stack LIFO explanation, queue FIFO
explanation, and one everyday example of each structure. The two synthetic works
are copied unchanged in local inputs; no account IDs/names enter model input.

Use original B from experiments/local_ai/samples.json and the previously tested
B variant changing only cache-based authorization to require DB checking because
cached data may be stale. Reverse replacement was asserted to restore original B;
the false UNIQUE guarantee and rollback sentence remain unchanged.

An independent source/coverage map was written before inference and never read by
the runner or passed to the model. Each request contains only assignment
instructions, one exact instructor criterion, and the full target submission.
No previous criterion result, expected answer, other version or peer input is
included. Four works generate 3+3+4+4 = 14 independent inference calls, one each,
no retries or tuning after seeing outputs.

The single methodological change relative to the earlier personal probe is
one criterion per call rather than four at once. Use the same local Qwen3 8B
Q4_K_M, Ollama 0.40.14, temperature 0.1, seed 42, context 8192, thinking off and
2304-token per-request limit, structured JSON. The personal-review instruction is
adapted to one criterion and English as requested. This is not an equal-total-
token-budget benchmark: more calls repeat the full source and multiply the
maximum possible output budget. Case order is fixed, one run only.

The installed checkpoint identity was checked through the existing helper:
weights a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f,
manifest SHA-256 b3d9ba7c899cfd112df2574c6a91458a70b724c5e4e50dfffd75574b2d1648e7.
The helper's legacy lecture prompt-version field does not identify this probe's
prompt; exact actual prompts are stored per request. Runtime /api/ps separately
reports model digest 500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41,
Q4_K_M/context 8192 and size_vram=size=6,194,766,806 bytes after each work. This is
runtime GPU residency (including context/runtime allocation), not independently
sampled peak VRAM/RAM. No CPU fallback, download, external provider or billing.
One shared compute lock protected the local experiment.

## Measured per-work times and statuses

Wall time is the sum of sequential inference request times for that work, including
model load inside requests. It excludes service startup, metadata queries and
human review. Initial load affects Alex v1; subsequent calls reuse the model.
Columns of statuses follow the instructor criterion order.

| Work | Requests | Request wall sum | Included load sum | Emitted statuses |
|---|---:|---:|---:|---|
| alex-v1 | 3 | 11.917 s | 4.860 s | correct, missing, partial |
| alex-v2 | 3 | 7.197 s | 0.016 s | correct, correct, correct |
| b-original | 4 | 17.506 s | 0.021 s | partial, partial, partial, partial |
| b-cache-fixed | 4 | 12.854 s | 0.021 s | correct, correct, correct, correct |

All 14 calls stopped normally. These are single-run timings, not averages,
classroom throughput or an apples-to-apples cold/warm speed comparison.

## Expected versus actual, source-based review

| Test | Independent expectation | Actual output and assessment |
|---|---|---|
| Alex v1 LIFO/plates | Correct stack explanation, real plates example; no FIFO explanation and no queue example. | correct / missing / partial. Both explicit stack explanation and plates example credited. Queue omission correctly identified. Pass for conclusions. |
| Alex v2 additions | FIFO and service-desk queue example added; stack coverage stays correct. | correct / correct / correct. Credits earliest-first, customers waiting at service desk and plates; no new invented stack gap. Pass for conclusions. |
| B atomicity/rollback | Explicit grouped updates and rollback are correct in both versions. | partial -> correct. Original critique imports the unrelated cache policy into this criterion; after cache edit it disappears. Fails stability/criterion isolation. |
| B UNIQUE/distinction | Both versions explicitly misclaim same-student/course UNIQUE prevents different students taking last seat. | partial -> correct. Original mentions inadequate capacity handling but does not correct the actual UNIQUE misconception; fixed version says the distinction is correct. Fails. |
| B concrete overbooking safeguard | No valid capacity-race safeguard was added in either version; must not approve UNIQUE or plain transactions as sufficient. | partial -> correct. Original asks for locks/atomic operations but also claims duplicate prevention addresses overbooking. Fixed version approves UNIQUE as concrete protection. Fails; unrelated cache correction changes conclusion. |
| B cache trade-off | Original cache-only approval is explicitly wrong; fixed version correctly acknowledges speed/staleness/DB check. | partial -> correct. Criticism disappears after correction as desired, but original wrong policy is softened to an incomplete discussion and its explicit authorization sentence is ignored in reasoning. Partial success, classification still wrong before correction. |

Original B: the concrete-protection feedback usefully recommends locks/atomic
operations and warns against cache-only confirmation, but it does not adequately
correct the false UNIQUE guarantee. Correcting the cache sentence changes all
four criterion statuses even though only one source claim changed. Neither B
variant receives an incorrect status in any criterion despite the explicit
technical error. The supplied quotes do not justify those positive conclusions.

## Exact quote audit versus relevance/entailment

26/26 supplied quotes are exact case-sensitive substrings of the correct target.
That is presence only. Several are irrelevant to the selected criterion: Alex v1
FIFO cites stack/plates text, even though the conclusion that queue coverage is
missing is correct after reading the full source. Alex v2 LIFO additionally quotes
queue behavior. Some what_student_wrote fields copy the complete short submission
rather than focus on the selected criterion. No fabricated quote was needed to
produce a false technical assessment.

For B fixed, concrete-protection evidence is exactly:

> I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat.

The model's corresponding reasoning, verbatim:

> The student correctly explains how a UNIQUE constraint on student ID and course ID prevents duplicate enrollments, which directly addresses the criterion of concrete protection against overbooking.

This is wrong for capacity: different Student IDs generate different unique pairs,
so the constraint does not limit both Students taking the last seat. The cache
edit adds no atomic capacity reservation, locking or adequate isolation. A real
quote containing a wrong claim is not evidence that the claim is correct.

For B original, criterion 0 reasoning also says, verbatim:

> The submission correctly mentions transaction rollback, which relates to atomicity. However, it incorrectly suggests that a cache can confirm enrollment without a database check, which undermines the need for rollback and atomicity in concurrent transactions.

This acknowledges rollback but unfairly changes the criterion assessment based
on a separate error; the same rollback explanation is accepted after cache repair.

## Recommendation

Do not advance this method to the Lecturer-draft workflow yet. It handles the two
simple stacks/queues works well, but fails the controlled B independence check
and approves a material technical mistake. Lecturer review remains required, but
is not evidence that the engine has met the agreed readiness checks. Keep the
existing provider choice/English homework availability unaccepted and improve
criterion-grounded assessment before a separately authorized next experiment.
No Student comparisons or website integration were performed. Numerical accuracy
or a broad language acceptance score is not justified by four synthetic works.

## Evidence availability

New standalone runner: experiments/local_ai/criterion_review_probe.py. This report
and runner remain uncommitted. Raw inputs, independent timestamped map, 14 exact
prompts/responses/quote audits, progress, aggregate timings, runtime residency and
service logs are local-only under ignored
.ai-lab/results/criterion-review/20261112T102349516534Z/. They are not clone-accessible
unless a later separately reviewed publication makes suitable evidence available.
No raw media, actual student work or credentials are included. Existing website,
model files and previous experiment reports/code were not edited.

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
