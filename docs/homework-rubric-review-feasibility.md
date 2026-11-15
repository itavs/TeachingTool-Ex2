# Detailed-Rubric Personal Review Probe - 2026-11-15

Historical B gate result: the stop decision below describes that completed run.
The user subsequently authorized a separate editable-draft experiment despite
isolated semantic errors. Its unchanged rubric, new pair, full individual and
comparison drafts, editing assessment and timings are recorded in
[the continuation report](homework-rubric-draft-pair-feasibility.md).
The original B false atomicity criticism remains a documented failure.

## Prior-work check and design

No previous detailed professional-rubric inference was found in tracked experiment
code/results, homework reports or local experiment-result directories. The prior
criterion_review_probe supplied a short criterion and full work, without an
assignment-level domain rubric. Planning documents mention rubrics, but are not
evidence that this experiment already ran. Current HEAD was 61f6a70.

This round retains the prior per-criterion English method, installed Qwen3 8B
Q4_K_M/Ollama 0.40.14 and settings: temperature 0.1, seed 42, context 8192,
2304 output tokens per request, thinking false, JSON schema, one call per criterion,
no retries. The change is a **fixed assignment-level professional rubric** supplied
with each selected criterion. It is the same across both B versions, not an answer
key customized for a particular work. The criterion prompt otherwise retains the
previous instructions about quotes, correct/partial/missing/incorrect, and avoiding
extra SQL/code requirements. Eight requests only, with no tuning after outputs.

Rubric: [enrollment-detailed-rubric.json](../experiments/local_ai/homework_fixtures/enrollment-detailed-rubric.json).
It separates all-or-nothing grouping/rollback from isolation, per-student duplicate
keys from shared capacity, and safe capacity reservation from cache trust. Valid
alternatives include conditional positive-capacity update, locked recheck and
serializable conflict handling; any one sound conceptual approach is sufficient.
The theoretical assignment does not require SQL or every listed alternative.

Inputs: [B pair](../experiments/local_ai/homework_fixtures/rubric-b-inputs.json).
The second differs only in replacing unsafe cache-only authorization with a final
DB check because the cached value may be stale. The UNIQUE guarantee and rollback
sentence are unchanged. The professional rubric is model input; the independent
[expected judgments](../experiments/local_ai/homework_fixtures/rubric-expectations.json)
are **not** model input and are not read by the runner. Expectations, input hashes,
rubric hash and stop/pass conditions were saved before the first inference.

The predefined gate requires both clear rejection of the UNIQUE guarantee and
stable, source-correct unaffected findings, including credit for the explicit
transaction/rollback explanation. It does not require identical wording. A merely
stable but false conclusion does not pass. Consistent partial for capacity can
be accepted if the false guarantee/actual reservation gap is clearly explained.
This pass criterion is documented before generation, not tightened afterward.

## Actual results and gate decision

| Criterion | Expected original -> corrected B | Actual original -> corrected B | Source/rubric assessment |
|---|---|---|---|
| Atomicity / rollback | correct -> correct; same explicit all-or-nothing coverage | partial -> partial | FAIL. Both invent a missing explicit atomicity requirement. Corrected B adds an unsupported concurrent-requests rollback requirement, despite unchanged source coverage. |
| Duplicate versus capacity | incorrect -> incorrect, explicitly reject different-student guarantee | incorrect -> incorrect | PASS. Both accurately explain that distinct students form distinct UNIQUE pairs. |
| Concrete overbooking protection | Do not approve false guarantee; same absence of sound reservation mechanism | partial -> partial | Useful stable warning: UNIQUE is insufficient and conditional update/locking is needed. It still softens an explicit false protection claim into partial coverage. Under the predefined flexible rule the essential reservation critique is present. |
| Cache trade-off | incorrect -> correct | incorrect -> correct | PASS. Original unsafe cache-only policy is identified; corrected DB-validation/staleness explanation is accepted. |

Only the cache **status** changes. This is a material improvement over the earlier
per-criterion run, where all four B statuses improved after the cache edit and the
UNIQUE error was approved. However, source-correctness still fails for atomicity,
and its reasoning also drifts into an unrelated concurrency requirement. This
is not a claim that UNIQUE detection failed again: that specific check succeeded.
The overall predefined B quality gate failed, so **the new pair and comparison
were not run**. Their synthetic inputs were prepared before inference and remain
unused; no generated output is claimed for them.

The unchanged source already says:

> A transaction can update the seat count and save the enrollment together, with rollback if either fails.

Original B's actual criterion-0 reasoning:

> The student correctly describes a transaction that includes rollback, which addresses atomicity. However, the explanation is incomplete as it does not explicitly discuss atomicity as a principle or clarify how rollback ensures the transaction is treated as an all-or-nothing unit. The mention of caching is relevant but not directly tied to the criterion.

Corrected B's actual criterion-0 reasoning:

> The submission correctly describes a transaction that includes both seat count and enrollment updates with rollback, which covers atomicity. However, it lacks explicit mention of atomicity as a principle and does not fully address rollback in the context of concurrent requests, which is required by the criterion.

The rubric explicitly accepts conceptual grouping plus rollback without the word
atomicity and assigns concurrency safety to another criterion. Demanding that
word or additional concurrency discussion is a false gap, not a genuine omitted
requirement. Both results acknowledge the correct content then penalize it with
an unsupported demand. This contradicts the supplied professional rubric.

## Timing and technical checks

Times are sums of the four sequential inference requests per work, including
model loads inside requests, excluding service startup, metadata queries and
human review. The first work includes initial loading; subsequent calls reuse
the loaded model. Do not compare cold/warm times as a speedup claim.

| Work | Requests | Wall time | Included model-load sum | Included generation-evaluation sum |
|---|---:|---:|---:|---:|
| b-original | 4 | 25.207 s | 5.847 s | 17.571 s |
| b-cache-fixed | 4 | 17.749 s | 0.084 s | 16.783 s |

All eight stopped normally. **10/10 quotes were exact case-sensitive source
substrings**. This verifies presence, not relevance or entailment: both atomicity
responses additionally quote cache text irrelevant to that criterion. Some
what_student_wrote fields copy the entire work instead of one focused sentence.
No numerical broad accuracy score is justified by two works/one run each.

The installed checkpoint was verified by the existing helper (weights digest
`a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f`, manifest
SHA-256 `b3d9ba7c899cfd112df2574c6a91458a70b724c5e4e50dfffd75574b2d1648e7`).
The helper's inherited lecture prompt-version label is not this probe's prompt
version; exact actual prompts are stored in the local records. /api/ps reports
qwen3:8b fully GPU-resident with size_vram=size=6,194,766,806 bytes after both
works. This is allocation/residency, not a sampled RAM/VRAM peak. There were no
external-provider requests, downloads, billing changes or CPU model fallback.

## Actual generated feedback - verbatim

These are model outputs, not endorsed assessments. Formatting is JSON
pretty-printing only; generated field values are unchanged.

### b-original

Criterion 1:

```json
{
  "what_student_wrote": "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat. A transaction can update the seat count and save the enrollment together, with rollback if either fails. A cache makes reads faster. If the cache says a seat is available, we can confirm enrollment immediately without a database check.",
  "quotes": [
    "A transaction can update the seat count and save the enrollment together, with rollback if either fails.",
    "A cache makes reads faster. If the cache says a seat is available, we can confirm enrollment immediately without a database check."
  ],
  "status": "partial",
  "reasoning": "The student correctly describes a transaction that includes rollback, which addresses atomicity. However, the explanation is incomplete as it does not explicitly discuss atomicity as a principle or clarify how rollback ensures the transaction is treated as an all-or-nothing unit. The mention of caching is relevant but not directly tied to the criterion.",
  "suggested_correction": "Clarify that the transaction's atomicity ensures both the seat count update and enrollment are treated as a single unit, and that rollback guarantees the system reverts to its previous state if any part of the transaction fails."
}
```

Criterion 2:

```json
{
  "what_student_wrote": "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat.",
  "quotes": [
    "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat."
  ],
  "status": "incorrect",
  "reasoning": "The student incorrectly claims that a UNIQUE constraint on (student ID, course ID) prevents different students from taking the last seat, which conflates duplicate enrollment with capacity concurrency. The UNIQUE constraint only prevents a single student from enrolling in the same course twice, not different students competing for seats.",
  "suggested_correction": "Clarify that a UNIQUE constraint on (student ID, course ID) prevents duplicate enrollment by the same student, while capacity concurrency requires a separate mechanism (e.g., a shared lock or seat count) to manage multiple students competing for limited seats."
}
```

Criterion 3:

```json
{
  "what_student_wrote": "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat.",
  "quotes": [
    "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat."
  ],
  "status": "partial",
  "reasoning": "The student correctly identifies the need for a UNIQUE constraint to prevent duplicate enrollments but fails to address the concurrent access issue. A UNIQUE constraint alone does not provide atomic protection against overbooking in a multi-user environment without proper transactional handling.",
  "suggested_correction": "Include a transactional approach that atomically checks and consumes the remaining capacity, such as using a conditional update or an exclusive lock on the course-capacity record."
}
```

Criterion 4:

```json
{
  "what_student_wrote": "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat. A transaction can update the seat count and save the enrollment together, with rollback if either fails. A cache makes reads faster. If the cache says a seat is available, we can confirm enrollment immediately without a database check.",
  "quotes": [
    "A cache makes reads faster. If the cache says a seat is available, we can confirm enrollment immediately without a database check."
  ],
  "status": "incorrect",
  "reasoning": "The student incorrectly claims that relying solely on the cache to confirm seat availability is sufficient, which violates the principle that authoritative enrollment decisions must be validated against the database state. The submission fails to acknowledge the risk of stale data in the cache and the necessity of final database validation.",
  "suggested_correction": "The student should revise the statement to include a final database validation step to ensure that cached seat availability is not trusted alone, as this is required to resolve the cache-trust issue."
}
```

### b-cache-fixed

Criterion 1:

```json
{
  "what_student_wrote": "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat. A transaction can update the seat count and save the enrollment together, with rollback if either fails. A cache makes reads faster. If the cache says a seat is available, we must check the database before confirming enrollment because cached availability may be stale.",
  "quotes": [
    "A transaction can update the seat count and save the enrollment together, with rollback if either fails.",
    "A cache makes reads faster. If the cache says a seat is available, we must check the database before confirming enrollment because cached availability may be stale."
  ],
  "status": "partial",
  "reasoning": "The submission correctly describes a transaction that includes both seat count and enrollment updates with rollback, which covers atomicity. However, it lacks explicit mention of atomicity as a principle and does not fully address rollback in the context of concurrent requests, which is required by the criterion.",
  "suggested_correction": "Explicitly state that the transaction ensures atomicity by grouping the seat count update and enrollment write as an all-or-nothing operation, and clarify that rollback undoes both changes if any part of the transaction fails."
}
```

Criterion 2:

```json
{
  "what_student_wrote": "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat.",
  "quotes": [
    "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat."
  ],
  "status": "incorrect",
  "reasoning": "The student incorrectly claims that a UNIQUE constraint on (student ID, course ID) prevents different students from taking the last seat, which conflates duplicate enrollment with capacity concurrency. The UNIQUE constraint only prevents a single student from enrolling in the same course twice, not multiple students competing for the same seat.",
  "suggested_correction": "Clarify that a UNIQUE constraint on (student ID, course ID) prevents duplicate enrollment by the same student, while capacity concurrency requires a separate mechanism (e.g., a shared lock or seat count) to manage multiple students competing for the same seat."
}
```

Criterion 3:

```json
{
  "what_student_wrote": "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat.",
  "quotes": [
    "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat."
  ],
  "status": "partial",
  "reasoning": "The student correctly acknowledges the need for a UNIQUE constraint to prevent duplicate enrollments, but this alone does not provide concrete protection against overbooking. A UNIQUE constraint on student ID and course ID prevents duplicate entries for the same student and course but does not address the concurrent request scenario for the last seat. The submission lacks a proper transactional mechanism to atomically check and consume shared remaining capacity under concurrent requests.",
  "suggested_correction": "Implement a transaction that conditionally updates the seat count and creates an enrollment only if the seat count is positive, ensuring atomicity and preventing overbooking."
}
```

Criterion 4:

```json
{
  "what_student_wrote": "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat. A transaction can update the seat count and save the enrollment together, with rollback if either fails. A cache makes reads faster. If the cache says a seat is available, we must check the database before confirming enrollment because cached availability may be stale.",
  "quotes": [
    "A cache makes reads faster. If the cache says a seat is available, we must check the database before confirming enrollment because cached availability may be stale."
  ],
  "status": "correct",
  "reasoning": "The student correctly addresses the cache latency versus staleness trade-off by acknowledging that cached availability may be stale and that a final database check is necessary.",
  "suggested_correction": ""
}
```

## Stop decision and review status

Stop here as required by the failed B gate. The detailed rubric improves UNIQUE
recognition and localizes status changes, but does not yet produce reliable,
criterion-faithful personal feedback. Do not enable a normal-site provider or
infer readiness of the planned pair/comparison from this result. Further trials,
if any, need a separate decision; no prompt/rubric retries occurred in this round.
The existing website, submission database and previous experiment files were not
edited. No application tests, integration, commit, staging or push was performed.

## Reproduction and availability

New runner: [rubric_review_probe.py](../experiments/local_ai/rubric_review_probe.py).
With the already installed pinned runtime/model and the local-only Ollama service
on 127.0.0.1:11435, run from the project root:

```powershell
.\.venv\Scripts\python.exe experiments/local_ai/rubric_review_probe.py
```

It defaults to the fixed B-pair fixture, creates a timestamped ignored result
folder and does not read expected judgments or a website database. The same local
service prerequisites/shutdown guidance as the existing local-ai README apply.
It never downloads a model or selects an external provider. The optional pair
input exists for a later separately approved run; it was not invoked here.

Report/code/fixtures and [portable recorded results](../experiments/local_ai/results/homework-focused/rubric-b/summary.json) are included in the experiment unit. Portable records preserve generated text, prompts, timings and audits; only opaque token-context arrays were removed. Full raw model responses,
exact prompts, quote checks, assignment rubric snapshot, pre-run expectations,
progress/timings/GPU metadata and gate review are local-only under
.ai-lab/results/rubric-review/20261115T082453982502Z/. The readable generated
feedback is reproduced above; service logs and model assets remain ignored.
