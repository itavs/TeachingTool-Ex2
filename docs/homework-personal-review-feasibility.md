# Personal Criterion Review Probe — 2026-11-11

## Independent pre-run expectations (not model input)

Use the previously prepared coverage map for the original synthetic A/B/C. Evaluate each work alone: no peers, comparison task or website integration. The original samples/criteria remain unchanged. All assessment expectations below stay outside the model prompt.

| Case | Atomicity / rollback | Duplicate versus capacity | Concrete overbooking protection | Cache trade-off |
|---|---|---|---|---|
| A | Correct: transaction grouping and explicit rollback. | Correct: UNIQUE for duplicate student/course, separate capacity safeguard. | Correct: conditional update succeeds only if a seat remains, or isolation. | Correct: faster reads, staleness and final DB authorization. |
| B | Present/correct: groups both updates and explicitly says rollback if either fails. | Incorrect: UNIQUE is claimed to prevent different students taking the final seat. | Incorrect/unsupported: no capacity-race mechanism beyond that false guarantee. | Incorrect: faster reads acknowledged, but cache-only enrollment approval is unsafe. |
| C | Missing failure/rollback explanation, explicitly acknowledged. | Missing same-student duplicate protection, explicitly acknowledged. | Sound isolation or row locking/recheck. | Sound staleness warning and refusal of cache-only approval. |
| B with only cache sentence corrected | Unchanged; rollback must still be recognized. | The false last-seat UNIQUE claim must still be identified. | No atomic reservation/isolation was added by the cache correction. | Cache-only authorization criticism should disappear; latency/staleness/DB checking are covered. |

The sole B edit replaces the sentence approving immediate cache-based enrollment without DB checking with: If the cache says a seat is available, we must check the database before confirming enrollment because cached availability may be stale. All other original text, including the wrong UNIQUE guarantee and rollback sentence, is preserved exactly. The replacement does not add atomic reservation or isolation. A timestamped map and hashes are retained in ignored local audit storage before generation.

Exact quote matching will be checked mechanically, without normalization, repair or retry. Quote presence alone is not proof that a status/conclusion is supported; the latter will be reviewed separately against this map and the source. Explicitly incorrect explanations must not be conflated with absent topics; partially correct but incomplete coverage is another distinct status.


## Executed setup and timing

Four separate local requests using installed Qwen3 8B Q4_K_M through Ollama 0.40.14 on loopback port 11435. No peer text, comparison, expected classifications or coverage map was passed to the model. Inputs were only assignment, four criteria and one synthetic submission. No download, cloud inference, Gemini request, website change or billing occurred. Each case ran once, without retry.

Weights digest: `a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f`; manifest SHA-256: `b3d9ba7c899cfd112df2574c6a91458a70b724c5e4e50dfffd75574b2d1648e7`. Settings: temperature 0.1, seed 42, context 8192, output budget 2304 tokens, thinking off, structured JSON, 180-second request timeout. The shared identity helper also returns a lecture-summary prompt-version label; that inherited label is not this experiment's prompt version. The complete actual personal-review prompt is preserved per run.

| Case | Wall time | Model load (included) | Generation evaluation (included) |
|---|---:|---:|---:|
| sample-a | 13.994 s | 2.985 s | 10.634 s |
| sample-b | 11.232 s | 0.005 s | 10.912 s |
| sample-c | 11.888 s | 0.006 s | 11.672 s |
| b-cache-fixed | 9.047 s | 0.003 s | 8.873 s |

The first case includes initial model loading; subsequent cases reuse the loaded model. These are single-run timings, not averages or classroom-load measurements. No new RAM/VRAM measurement was taken in this probe. All four returned normal stop and four criterion rows. Local raw inputs/prompts/outputs and the timestamped pre-run map are retained under ignored `.ai-lab/results/personal-review/20261111T131558976875Z/`.

## Mechanical checks versus assessment quality

All **15/15 supplied quotes** are exact, case-sensitive substrings of the respective target submission, and all four criterion-index sets are valid. C supplies no quote for criterion 2. Absence of a quote is not evidence that the source lacks the topic. Two isolated audit unit tests passed, covering exact matches, changed case, paraphrases, joined fragments, empty quotes and duplicate indices. These are experiment-helper checks, not website acceptance tests.

The substantive review below was performed by the agent against the independent source map and target text; it is not a second model judgment. A real quote can be irrelevant, contradict the conclusion, or omit another decisive source sentence.

| Case | Correctly recognized | Missed error or false criticism |
|---|---|---|
| A | Transaction/rollback, explicit conditional seat update and cache warning are accepted. The capacity condition is quoted exactly. | Duplicate/capacity distinction is marked partial despite separate UNIQUE and last-seat safeguards. The requested isolation expansion repeats an already offered safeguard; this is an invented gap. |
| B original | Explicit rollback is quoted and acknowledged. The lack of a concrete concurrency safeguard and cache-staleness risk are mentioned. | Atomicity is unfairly marked partial by conflating it with concurrency/isolation. Wrong UNIQUE guarantee is marked correct. Unsafe cache-only authorization is treated as incomplete discussion, not an explicitly wrong policy. |
| C | Cache warning accepted; missing atomicity/rollback explanation is mentioned, although labeled partial. | Explicit row locking/isolation and recheck are called missing under concrete protection, even though the same text is quoted under another criterion. The missing duplicate-enrollment explanation is not identified; its distinction is marked correct. |
| B cache-fixed | Cache trade-off is correctly accepted; rollback is accepted as correct. | Wrong UNIQUE guarantee is still accepted. Concrete overbooking protection changes from partial to correct even though no atomic seat-reservation mechanism was added. |

The original B rollback finding is especially unstable: the same transaction sentence changes from partial to correct after an unrelated cache sentence changes. The original B overbooking warning is useful but weakened by the unsupported statement that a transaction itself prevents overbooking. After the edit, that warning disappears. The UNIQUE quote contains the actual false last-seat claim, so its presence directly fails to support the model's positive conclusion.

C's criterion-0 quote describes the race, not atomicity/rollback. The source explicitly admits failure handling was not addressed; this supports a missing finding rather than the emitted partial finding. For criterion 1, locking/recheck does not establish duplicate prevention. For criterion 2, the empty quote and missing classification overlook the already quoted locking mechanism. A's criterion-1 quote covers duplicates but the conclusion ignores the next source sentence about capacity.

### Controlled cache edit result

The cache-specific criticism disappears as expected and the corrected sentence supports accepting criterion 3. However, the original criticism never clearly identified the cache-only authorization as wrong, and the remaining separate UNIQUE/last-seat error is still missed in both versions. The edit therefore fails the required independence check: correcting one topic incorrectly improves judgments of unchanged topics. The model used no incorrect status in any of the sixteen findings despite B's explicit incorrect claims.

## B feedback before and after, verbatim

The following JSON contains all feedback fields exactly as generated; no language or assessment repairs were made. These are experiment outputs, not endorsed feedback.

### Original B

```json
{
  "criteria_findings": [
    {
      "criterion_index": 0,
      "what_student_wrote": "The student mentions using a transaction with rollback.",
      "quotes": [
        "A transaction can update the seat count and save the enrollment together, with rollback if either fails."
      ],
      "status": "partial",
      "reasoning": "The student correctly mentions a transaction and rollback, but does not explicitly address atomicity in the context of handling two students simultaneously. The explanation lacks a clear discussion of how atomicity ensures that the seat count is updated correctly and consistently across both students' requests.",
      "suggested_correction": "Clarify how atomicity ensures that the seat count is updated correctly and consistently when two students request the last seat simultaneously."
    },
    {
      "criterion_index": 1,
      "what_student_wrote": "The student discusses preventing duplicate enrollment using a UNIQUE constraint.",
      "quotes": [
        "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat."
      ],
      "status": "correct",
      "reasoning": "The student correctly identifies the use of a UNIQUE constraint to prevent duplicate enrollment, which directly addresses the distinction between duplicate enrollment and capacity concurrency.",
      "suggested_correction": ""
    },
    {
      "criterion_index": 2,
      "what_student_wrote": "The student discusses preventing overbooking with a transaction and rollback.",
      "quotes": [
        "A transaction can update the seat count and save the enrollment together, with rollback if either fails."
      ],
      "status": "partial",
      "reasoning": "The student correctly mentions using a transaction to prevent overbooking, but does not explicitly discuss concrete protection mechanisms such as locking or isolation levels that ensure the seat count is not overbooked when two students request the last seat simultaneously.",
      "suggested_correction": "Specify concrete protection mechanisms such as locking or isolation levels to ensure the seat count is not overbooked."
    },
    {
      "criterion_index": 3,
      "what_student_wrote": "The student discusses the trade-off between cache latency and staleness.",
      "quotes": [
        "A cache makes reads faster. If the cache says a seat is available, we can confirm enrollment immediately without a database check."
      ],
      "status": "partial",
      "reasoning": "The student correctly mentions the trade-off between cache latency and staleness, but does not explicitly discuss the risks of using a cache in this context, such as stale data leading to overbooking or incorrect seat availability.",
      "suggested_correction": "Discuss the risks of using a cache, such as stale data leading to overbooking or incorrect seat availability."
    }
  ]
}
```

### B with only cache authorization corrected

```json
{
  "criteria_findings": [
    {
      "criterion_index": 0,
      "what_student_wrote": "The student mentioned using a transaction with rollback.",
      "quotes": [
        "A transaction can update the seat count and save the enrollment together, with rollback if either fails."
      ],
      "status": "correct",
      "reasoning": "The student correctly describes using a transaction with rollback to ensure atomicity and prevent partial updates.",
      "suggested_correction": ""
    },
    {
      "criterion_index": 1,
      "what_student_wrote": "The student discussed preventing duplicate enrollment using a UNIQUE constraint.",
      "quotes": [
        "I would add a UNIQUE constraint on student ID and course ID. This guarantees that two different students cannot take the last seat."
      ],
      "status": "correct",
      "reasoning": "The student correctly distinguishes duplicate enrollment from capacity concurrency by using a UNIQUE constraint to prevent the same student from enrolling twice, though it doesn't fully address concurrency between students.",
      "suggested_correction": ""
    },
    {
      "criterion_index": 2,
      "what_student_wrote": "The student mentioned using a transaction to prevent overbooking.",
      "quotes": [
        "A transaction can update the seat count and save the enrollment together, with rollback if either fails."
      ],
      "status": "correct",
      "reasoning": "The student correctly describes using a transaction to ensure atomicity and prevent overbooking by rolling back if the update fails.",
      "suggested_correction": ""
    },
    {
      "criterion_index": 3,
      "what_student_wrote": "The student discussed the trade-off between cache latency and staleness.",
      "quotes": [
        "A cache makes reads faster. If the cache says a seat is available, we must check the database before confirming enrollment because cached availability may be stale."
      ],
      "status": "correct",
      "reasoning": "The student correctly addresses the trade-off between cache latency and staleness by acknowledging the need to verify the database state before confirming enrollment.",
      "suggested_correction": ""
    }
  ]
}
```

## Recommendation and limits

Do not yet advance to comparison between works or integrate personal feedback into the website. The focused personal assessment still fails to recognize explicit technical mistakes consistently and invents gaps in valid coverage. Exact-quote checks are useful for traceability but cannot certify entailment or technical correctness. Hebrew feedback also contains corrupted/mixed-script wording (for example A's cache explanation), so it is not publication-ready.

A next separately approved experiment should first improve per-criterion evidence/contradiction handling and repeat the controlled B test while preserving unchanged criteria, before attempting peer comparisons. These four short synthetic cases do not measure broad accuracy or repeatability. Existing website tests were not rerun because no website code changed. All outputs remain uncommitted for review.

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
