# Fixed-rubric personal feedback and comparison draft experiment

## Scope and conclusion

2026-11-15; HEAD 61f6a70. Local Qwen3 8B only, synthetic submissions only,
no website/database changes, downloads, external inference, retries or prompt tuning.
The user authorized continuing past individual semantic errors to evaluate editable
Lecturer drafts. This is not a retroactive pass of the earlier B quality gate.

The pair gives a useful starting draft, especially the real conditional-update versus
locked-recheck contrast, but still needs substantive Lecturer correction. Recommend
an explicitly experimental English route under the existing private-draft, review,
edit and separate-publication lifecycle, subject to user approval. Do not enable it
as a reliable automatic evaluator or publish any raw output. This run does not
validate Hebrew, noisy/long answers, larger cohorts, failed-comparison workflow or
runtime website privacy. The website provider remains disabled.

## Prior B finding retained

The [earlier rubric report](homework-rubric-review-feasibility.md) records successful
UNIQUE-error identification in both B versions and cache-only status change after
the controlled correction. It also records the false atomicity criticism: the model
acknowledges grouping/rollback but demands explicit atomicity terminology and, in
the corrected version, concurrent-request rollback discussion. These demands are
unsupported by the fixed assignment rubric. That earlier semantic failure remains;
B was not rerun here. Its 10/10 exact quotes did not establish correct conclusions.

## Design, precommitted expectations and evidence

The [fixed rubric](../experiments/local_ai/homework_fixtures/enrollment-detailed-rubric.json)
was unchanged (SHA256 e3ea88e1f26860c676c18d498384b2d2dd7a3bc0cb9ef6c0c7032879480c4d09).
[Two new submissions](../experiments/local_ai/homework_fixtures/rubric-draft-pair-inputs.json)
use a conditional positive-count update and an exclusive row lock with recheck.
Both correctly cover all four criteria. Fictional Author headers were added solely
as privacy canaries; no real students or personal account data are used.
The [independent expected map](../experiments/local_ai/homework_fixtures/rubric-draft-pair-expectations.json)
was saved at 08:40:00 UTC, before inference began at 08:42:03 UTC. Neither runner
reads it. Each individual call sees only its single criterion, fixed rubric and
full own work. Each comparison sees the two full works and the same rubric, not
individual feedback or expectations. Comparisons were generated in both target
directions to check attribution. There were 8 individual and 2 comparison calls.

[Portable records](../experiments/local_ai/results/homework-focused/rubric-draft-pair/summary.json)
include inputs, rubric, pre-run map, exact prompts, schema, unchanged generated
response text, metadata and quote audits in the same directory. Only Ollama's
opaque token-context arrays were removed. Full raw logs remain local-only at
`.ai-lab/results/rubric-draft-pair/20261115T084000618128Z/`; model assets and runtime
are also local-only. These records and fixtures are included in the experiment unit. No dependency on a private demo database is required.

## Runtime and measurements

Ollama 0.40.14; qwen3:8b Q4_K_M; weights digest
`a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f`, manifest
`b3d9ba7c899cfd112df2574c6a91458a70b724c5e4e50dfffd75574b2d1648e7`.
Temperature 0.1, seed 42, context 8192, max output 2304, think=false,
stream=false, timeout 180s, no retries. Actual experiment prompts are saved in
records; the identity helper's inherited `lecture-grounding-v3` field is not the
prompt version of this homework experiment. Service binds loopback 11435 with cloud
disabled; the shared decoder lock prevents competing application decoding.

| Draft | Calls | Request wall seconds | Included load seconds | Included token-generation seconds |
|---|---:|---:|---:|---:|
| Conditional-update individual | 4 | 21.605 | 2.983 | 17.203 |
| Locked-recheck individual | 4 | 14.990 | 0.017 | 14.089 |
| Conditional-update target comparison | 1 | 12.397 | See record | See record |
| Locked-recheck target comparison | 1 | 9.964 | See record | See record |

Wall time includes loading/request overhead but excludes service startup and
review. First individual call and first comparison follow model unloading; these
are not controlled cold-boot speed comparisons. Individual residency snapshots
report all 6,194,766,806 model bytes in VRAM; GPU offload is also logged. This is
not peak total device VRAM or system RAM measurement. No RAM peak was measured.
All 10 inference responses stopped normally with parseable structured output.

## Source-based review and required Lecturer edits

| Draft / criterion | Expected vs actual | Assessment and edit before publication | Severity |
|---|---|---|---|
| Conditional-update, all four | correct vs correct | Source/rubric conclusions supported. No required substantive correction. Shorten repeated full-work descriptions if desired. | Minor presentation |
| Locked-recheck, atomicity | correct vs correct | Appropriate credit for rollback. Remove fictional Author header copied into description for cleaner feedback. | Minor presentation |
| Locked-recheck, duplicate distinction | correct vs correct | Meaning correct, but quoted `A UNIQUE...` changes source `a UNIQUE...` after removing `Separately,`. Replace with the actual contiguous source text. | Evidence integrity |
| Locked-recheck, capacity | correct vs correct | Reasoning adds `a conditional update` to the locked solution. A conditional branch under a lock is not evidence of the distinct atomic conditional-update approach. Describe lock/recheck/write-before-release only. | Moderate attribution ambiguity |
| Locked-recheck, cache | correct vs partial | Invented gap: faster reads, staleness and final locked DB validation are all explicit. Change to correct; replace the criticism and remove mandatory correction. | Major false criticism |
| Conditional target comparison, first difference | Shared transaction/rollback vs asserted contrast | Move common all-or-nothing transaction/rollback to similarities; locking protects capacity/isolation, not a replacement for transaction atomicity. | Major conceptual conflation |
| Conditional target comparison, capacity | Real contrast found | Keep conditional update versus locked recheck. Fix private peer quote: source ends `enrollment, then commit...`, not `enrollment.` | Evidence integrity |
| Conditional target comparison, duplicates | Both distinguish duplicates/capacity | Wording singles out target clarification as a difference, although peer explicitly says `this is different from the lock protecting capacity across students`. Move to similarities without implied exclusive credit. | Moderate misleading contrast |
| Locked target comparison, capacity | Correct real contrast | Keep description; fix private target quote that changes `I start a transaction and hold...` to `I hold...`. | Evidence integrity |
| Locked target comparison, cache | Same authoritative policy, different wording | Claims individually supported, but not a distinct policy. Move to similarities or explain optional TTL mention without inventing a deficiency. | Minor categorization |

No incorrect status occurs for the conditional-update work; locked-recheck has
one false partial among four. Four substantive correction locations across the
four drafts: locked capacity wording, locked cache row, first comparison's
atomicity contrast and first comparison's duplicate contrast. Separately three
quote locations require source-exact replacement; optional shortening and cache
recategorization improve readability. These are a review checklist, not measured
Lecturer edit time. No errors justify discarding the whole experiment, but a
blanket approve action is unsafe.

Individual quote presence: 12/13 exact; comparison private evidence: 8/10 exact;
overall 20/23. Exact-match failures are recorded without repairing originals.
Three altered quotes preserve approximate meaning but fail the promised exact
quotation contract. A real provider must reject/flag these or require Lecturer
source correction; matching quotes still require semantic review.

No cross-author attribution or fictional author canary leaked into either public
comparison projection; no peer verbatim quote/full work is shown there. Private
comparison evidence intentionally contains source quotes and must not become a
student payload. Individual feedback copies its own author canary once; this is
not a peer leak. Anonymity is checked on two synthetic cases only, not established
against indirect identity inference, prompt injection or every possible output.
No grades, plagiarism claims or fabricated identities were generated. Correct
core attribution survives swapping target and peer, but the conceptual/contrast
errors above still need correction.

## Full individual drafts, verbatim structured fields

JSON below is decoded generated output, not corrected Lecturer feedback. It
includes every field; long repeated descriptions are left intact deliberately.

### conditional-update

#### Criterion 1

```json
{
  "what_student_wrote": "I use one database transaction to create the enrollment and consume a seat, committing both together. If either fails, rollback undoes both changes.",
  "quotes": [
    "I use one database transaction to create the enrollment and consume a seat, committing both together. If either fails, rollback undoes both changes."
  ],
  "status": "correct",
  "reasoning": "The submission correctly describes atomicity by grouping enrollment and seat-count updates into a single transaction and explicitly mentions rollback to undo changes on failure, aligning with the professional principle.",
  "suggested_correction": ""
}
```

#### Criterion 2

```json
{
  "what_student_wrote": "I use one database transaction to create the enrollment and consume a seat, committing both together. If either fails, rollback undoes both changes. A UNIQUE constraint on (student, course) prevents the same student enrolling twice, but does not reserve capacity for different students. For capacity I perform a conditional update that reduces remaining seats only when the count is positive. I accept the enrollment only if that update succeeds and roll back the transaction if enrollment creation fails. Thus competing requests cannot both consume the same final seat. Cached availability speeds up display reads but may be stale, so cached results never authorize enrollment; the conditional database reservation is authoritative.",
  "quotes": [
    "A UNIQUE constraint on (student, course) prevents the same student enrolling twice, but does not reserve capacity for different students.",
    "Thus competing requests cannot both consume the same final seat."
  ],
  "status": "correct",
  "reasoning": "The student correctly distinguishes duplicate enrollment (same student, same course) from capacity concurrency (different students competing for seats) by explaining how a UNIQUE constraint addresses the former and a conditional update handles the latter. The student also correctly notes that caching does not authorize enrollment, ensuring the database remains authoritative.",
  "suggested_correction": ""
}
```

#### Criterion 3

```json
{
  "what_student_wrote": "I use one database transaction to create the enrollment and consume a seat, committing both together. If either fails, rollback undoes both changes. A UNIQUE constraint on (student, course) prevents the same student enrolling twice, but does not reserve capacity for different students. For capacity I perform a conditional update that reduces remaining seats only when the count is positive. I accept the enrollment only if that update succeeds and roll back the transaction if enrollment creation fails. Thus competing requests cannot both consume the same final seat. Cached availability speeds up display reads but may be stale, so cached results never authorize enrollment; the conditional database reservation is authoritative.",
  "quotes": [
    "I perform a conditional update that reduces remaining seats only when the count is positive. I accept the enrollment only if that update succeeds and roll back the transaction if enrollment creation fails.",
    "Thus competing requests cannot both consume the same final seat."
  ],
  "status": "correct",
  "reasoning": "The student correctly describes a conditional update approach that ensures atomic capacity reservation under concurrent requests, fulfilling the criterion of concrete protection against overbooking.",
  "suggested_correction": ""
}
```

#### Criterion 4

```json
{
  "what_student_wrote": "I use one database transaction to create the enrollment and consume a seat, committing both together. If either fails, rollback undoes both changes. A UNIQUE constraint on (student, course) prevents the same student enrolling twice, but does not reserve capacity for different students. For capacity I perform a conditional update that reduces remaining seats only when the count is positive. I accept the enrollment only if that update succeeds and roll back the transaction if enrollment creation fails. Thus competing requests cannot both consume the same final seat. Cached availability speeds up display reads but may be stale, so cached results never authorize enrollment; the conditional database reservation is authoritative.",
  "quotes": [
    "Cached availability speeds up display reads but may be stale, so cached results never authorize enrollment; the conditional database reservation is authoritative."
  ],
  "status": "correct",
  "reasoning": "The student correctly explains the trade-off between cache latency and staleness by acknowledging that cached availability can be stale and that it should never authorize enrollment. The student emphasizes that the conditional database reservation is authoritative, which aligns with the professional principle and valid solutions provided in the rubric.",
  "suggested_correction": ""
}
```

### locked-recheck

#### Criterion 1

```json
{
  "what_student_wrote": "Author: SyntheticAuthorMaple I start a transaction and hold an exclusive lock on the shared course-capacity row. After acquiring that lock I read the current capacity again; when there is a seat I decrement it and insert the enrollment, then commit and release the lock. The next request waits for the lock and rechecks the updated availability. Failure of either write rolls back all transaction changes.",
  "quotes": [
    "Failure of either write rolls back all transaction changes."
  ],
  "status": "correct",
  "reasoning": "The submission correctly describes atomicity and rollback by ensuring that if either write operation fails, all changes are rolled back, maintaining the all-or-nothing property of a transaction.",
  "suggested_correction": ""
}
```

#### Criterion 2

```json
{
  "what_student_wrote": "The student explains a university registration system's handling of two students requesting the last seat, discussing transactions, duplicate prevention, and caching.",
  "quotes": [
    "I start a transaction and hold an exclusive lock on the shared course-capacity row.",
    "A UNIQUE key on (student, course) rejects repeated enrollment by the same student; this is different from the lock protecting capacity across students."
  ],
  "status": "correct",
  "reasoning": "The student correctly distinguishes duplicate enrollment (same student, same course) from capacity concurrency (different students, same course) by using a UNIQUE key for duplicates and a lock for capacity management.",
  "suggested_correction": ""
}
```

#### Criterion 3

```json
{
  "what_student_wrote": "The student explains how a university registration system should handle two students simultaneously requesting the last seat, discussing transactions, duplicate prevention, and the benefits and risks of caching.",
  "quotes": [
    "I start a transaction and hold an exclusive lock on the shared course-capacity row. After acquiring that lock I read the current capacity again; when there is a seat I decrement it and insert the enrollment, then commit and release the lock.",
    "Failure of either write rolls back all transaction changes. Separately, a UNIQUE key on (student, course) rejects repeated enrollment by the same student; this is different from the lock protecting capacity across students."
  ],
  "status": "correct",
  "reasoning": "The submission correctly describes concrete protection against overbooking by using an exclusive lock on the shared course-capacity row and a conditional update within a transaction. It also acknowledges the role of a UNIQUE key for preventing duplicate enrollments by the same student, which is distinct from the lock protecting shared capacity.",
  "suggested_correction": ""
}
```

#### Criterion 4

```json
{
  "what_student_wrote": "The student explains a university registration system's handling of two students requesting the last seat, discussing transactions, duplicate prevention, and caching.",
  "quotes": [
    "Cached course availability makes browsing faster but can be stale even with a short TTL.",
    "Enrollment uses the database recheck under the lock, never cached availability."
  ],
  "status": "partial",
  "reasoning": "The submission addresses the cache latency versus staleness trade-off by mentioning that cached availability can be stale and that enrollment uses database recheck. However, it does not fully explain the trade-off between faster cached reads and the risk of stale data, nor does it clearly discuss the balance between these factors as required by the criterion.",
  "suggested_correction": "Clarify the trade-off between faster cached reads and the risk of stale data, and explicitly mention the need for a final database validation to resolve the cache-trust issue."
}
```

## Full comparison drafts, unchanged

Evidence fields are Lecturer-private. Public projection excludes those fields.

### Target: conditional-update

```json
{
  "comparison_text": "Both submissions address the handling of concurrent seat requests, transactions, and caching, but differ in their approaches to concurrency control and capacity reservation.",
  "differences": [
    {
      "dimension": "Transaction and Rollback Mechanism",
      "description": "The target submission describes a transaction that includes both enrollment and seat consumption, with rollback on failure. The other submission uses an exclusive lock on the course-capacity row to ensure atomicity.",
      "target_evidence": "I use one database transaction to create the enrollment and consume a seat, committing both together. If either fails, rollback undoes both changes.",
      "other_evidence": "I start a transaction and hold an exclusive lock on the shared course-capacity row."
    },
    {
      "dimension": "Capacity Reservation and Concurrency",
      "description": "The target submission uses a conditional update to safely consume a seat, while the other submission explicitly locks the course-capacity row to prevent race conditions.",
      "target_evidence": "For capacity I perform a conditional update that reduces remaining seats only when the count is positive.",
      "other_evidence": "After acquiring that lock I read the current capacity again; when there is a seat I decrement it and insert the enrollment."
    },
    {
      "dimension": "Duplicate Enrollment Prevention",
      "description": "Both submissions use a UNIQUE constraint on (student, course) to prevent duplicate enrollment, but the target submission clarifies that this does not reserve capacity for other students.",
      "target_evidence": "A UNIQUE constraint on (student, course) prevents the same student enrolling twice, but does not reserve capacity for different students.",
      "other_evidence": "Separately, a UNIQUE key on (student, course) rejects repeated enrollment by the same student;"
    }
  ],
  "similarities": [
    "Both submissions use transactions to ensure atomicity and rollback on failure.",
    "Both address the need to prevent duplicate enrollment using a UNIQUE constraint on (student, course).",
    "Both acknowledge the trade-off between caching for speed and the risk of stale data."
  ],
  "limitations": "No supported differences exist in the rubric criteria that are not already covered in the comparison."
}
```

### Target: locked-recheck

```json
{
  "comparison_text": "Both submissions address the university registration system's handling of two students requesting the last seat, discussing transactions, duplicate prevention, and caching. They both correctly describe the need for atomicity and rollback, and both distinguish between duplicate enrollment and capacity concurrency. However, they differ in their approaches to concrete protection against overbooking and in their treatment of caching.",
  "differences": [
    {
      "dimension": "Concrete protection against overbooking",
      "description": "The target submission uses an exclusive lock on the shared course-capacity row to ensure atomic capacity check and seat consumption, while the other submission uses a conditional update that reduces remaining seats only when the count is positive.",
      "target_evidence": "I hold an exclusive lock on the shared course-capacity row. After acquiring that lock I read the current capacity again; when there is a seat I decrement it and insert the enrollment, then commit and release the lock.",
      "other_evidence": "I perform a conditional update that reduces remaining seats only when the count is positive. I accept the enrollment only if that update succeeds and roll back the transaction if enrollment creation fails."
    },
    {
      "dimension": "Cache latency versus staleness trade-off",
      "description": "The target submission explicitly states that cached course availability is used for browsing but not for enrollment decisions, while the other submission emphasizes that cached results never authorize enrollment and that the conditional database reservation is authoritative.",
      "target_evidence": "Cached course availability makes browsing faster but can be stale even with a short TTL. Enrollment uses the database recheck under the lock, never cached availability.",
      "other_evidence": "Cached availability speeds up display reads but may be stale, so cached results never authorize enrollment; the conditional database reservation is authoritative."
    }
  ],
  "similarities": [
    "Both submissions correctly describe the need for atomicity and rollback, grouping enrollment and seat-count updates into a single transaction.",
    "Both submissions distinguish between duplicate enrollment (handled by a UNIQUE key on (student, course)) and capacity concurrency (handled by separate mechanisms).",
    "Both submissions acknowledge the trade-off between cache latency and staleness, emphasizing that cached availability is not sufficient for authoritative enrollment decisions."
  ],
  "limitations": "No supported differences exist in the other criteria."
}
```

## Reproduction and limits

Use the already installed pinned local runtime/model, then start the loopback-only
service using `experiments/local_ai/start_ollama.ps1` as described in its README.
From the repository root, prepare a fresh folder; never overwrite this run:

```powershell
$pairRun = Join-Path $PWD ('.ai-lab/results/rubric-draft-pair/' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ'))
New-Item -ItemType Directory -Path $pairRun | Out-Null
Copy-Item experiments/local_ai/homework_fixtures/rubric-draft-pair-inputs.json (Join-Path $pairRun 'inputs.json')
Copy-Item experiments/local_ai/homework_fixtures/enrollment-detailed-rubric.json (Join-Path $pairRun 'rubric.json')
Copy-Item experiments/local_ai/homework_fixtures/rubric-draft-pair-expectations.json (Join-Path $pairRun 'pre-run-expectations.json')
.\.venv\Scripts\python.exe -B experiments/local_ai/rubric_review_probe.py --run $pairRun
.\.venv\Scripts\python.exe -B experiments/local_ai/rubric_comparison_probe.py --run $pairRun
```

Stop only the owned, verified experimental service afterward. Models are neither
bundled nor downloaded by these probes; missing local assets fail. Reproduction
requires local GPU/runtime assets; reviewing saved JSON/drafts requires no model,
API key, hidden fixture or website database. Fixed seeds do not guarantee bytewise
identical results across runtime/hardware changes. No human Lecturer editing or
classroom acceptance was measured. English two-work comparison results cannot be
extrapolated to production quality or Hebrew availability.
