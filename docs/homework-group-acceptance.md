# Real-model demonstration-group check — 19 November 2026

## Scope and preserved evidence

The user confirmed group 1 for assignment 4 in Test Meeting, DEMO-CS101 through
the website. Two normal `run_homework_worker --once` invocations then processed
the group's existing requests sequentially. No retry, remote API, download,
draft edit or publication was performed by the agent. Subsequent user-reported
Lecturer correction/publication is recorded below. This is a process and content check,
not acceptance of automatic comparison quality.

Synthetic inputs and a separate expected-coverage map were prepared before
inference. The map was excluded from model inputs. Alex Version 1 describes a
conditional capacity update and affected-row check, but omits same-student
duplicate protection. Casey Version 1 describes a shared-row lock and fresh
capacity check, and separately explains UNIQUE(student_id, course_id). Both
describe transaction rollback and non-authoritative cached availability.

The [reproduction fixture](../experiments/homework_group/README.md) includes full
synthetic inputs, the predeclared expected map, unedited model findings/comparisons,
quote audits and timings. These exclude database/account records and edited site
submissions. Full private pre-processing/draft snapshots and authenticated HTTP
results remain **local-only**, under `.local/group-acceptance-20261118/`. The run
is `group-1-20261119T063723Z`; these ignored captures are not in Git. Full originals
were captured before any edit, using exclusive file creation:

| File | SHA-256 |
|---|---|
| job-7-original.json | 126c9b833fc172a8219cc42b27ce615b4f6db7469f42fb3686da4d895c6bbec5 |
| job-8-original.json | 63b7566154f774bba6fa98910f88d8f4e181657818d8ec196372180a6a29cc70 |

## Process results

The installed Qwen3 8B Q4_K_M (`qwen3:8b`) ran through the pinned local adapter,
Ollama 0.40.14, context 8,192. Each work used four criterion calls and one
comparison call. Model metadata reported GPU residency of 6,194,766,806 bytes
on the RTX 5050; this is not a measurement of peak total VRAM.

| Request / source | Worker processing time | Result |
|---|---:|---|
| 7 / Alex submission 9, Version 1 | 47.575 seconds | Private draft ready; generated comparison outcome `no_difference` |
| 8 / Casey submission 10, Version 1 | 34.458 seconds | Private draft ready; generated comparison outcome `no_difference` |

Times include the normal processing stages, not waiting since confirmation.
Worker invocation wall times were approximately 48.3 and 35.2 seconds. Initial
individual-stage model load times were about 5.4 and 2.9 seconds respectively;
comparison-stage loads were about 2.9 seconds each. These are two small synthetic
works, not a throughput benchmark or a test of four-member capacity.

Authenticated live HTTP checks confirmed:

- Exactly two finished requests, correct frozen sources/context, and only the
  other selected owner as each target's peer; no self-comparison.
- Lecturer access to both private review pages and group status.
- Student group/review access denied, peer-version access denied, and own
  submission pages still showing no published feedback. Draft narratives did
  not appear in those student responses.
- Both drafts remained revision 1 and unpublished after processing/capture.

Browser automation remains unavailable. These are server/HTTP checks, not visual
browser acceptance. Separate publication and the resulting student display were
later confirmed by the user report below. Existing automated
group/publication coverage is recorded in [testing](testing.md#selected-demonstration-group-workflow---2026-11-18).

## Content results against the predeclared expectations

| Check | Expected | Actual / assessment |
|---|---|---|
| Alex personal criteria 1–4 | Correct, missing, correct, correct | All marked correct. Criterion 2 falsely credits duplicate/capacity distinction using cache-authority evidence. Major correction required. |
| Casey personal criteria 1–4 | All correct | All correct, supported by the source in this sample. |
| Approach difference | Conditional write versus exclusive lock plus recheck; both valid | Both comparisons report `no_difference`. Alex's comparison incorrectly says both use a conditional update. |
| Coverage difference | Only Alex omits same-student duplicate protection | Both comparisons falsely credit both submissions with duplicate protection and complete coverage. |
| Quote fidelity | Exact source-bound quotations | Alex 9/10; Casey 12/12. Alex's criterion 3 quote inserts “than” into “Zero affected rows”. |
| Attribution and anonymity | Correct source binding; no peer identity/full work in public narrative | Evidence source labels match the quoted sources; no peer account identity/full work in the narratives. However, the comparison prose wrongly attributes shared coverage. |

All six comparison evidence quotations were exact, yet the conclusions were
wrong. Exact-quote validation therefore does not establish semantic support.
The malformed Alex quote remains unverified and must be corrected or removed
before publication. No missing-topic criticism was invented here; the major
failure was invented coverage and loss of an explicit approach distinction.

### Unedited generated comparison: Alex

> Both submissions correctly address transaction atomicity, duplicate prevention, and caching trade-offs. They both describe a conditional update to reserve a seat and use database validation as the final authority for enrollment decisions. Both emphasize that caching improves read performance but does not replace the need for authoritative database checks. The approaches are conceptually equivalent in their handling of concurrency and rollback mechanisms.

### Unedited generated comparison: Casey

> Both submissions correctly address transaction atomicity, duplicate prevention, and the cache latency/staleness trade-off. They both describe using a transaction to group seat-count updates and enrollment inserts, with rollback on failure. Both distinguish between duplicate enrollment (via UNIQUE constraints) and capacity concurrency (via row locks or conditional updates). Neither submission introduces unsupported claims or omits required coverage. The approaches are conceptually equivalent in their handling of concurrency, rollback, and cache use.

## Human corrections and user-reported publication check

The supplied human-review corrections were: mark Alex's duplicate
criterion as missing explanation, without asserting a proven implementation
defect; remove/correct the malformed quote; replace both false comparisons with
the actual conditional-write/row-lock distinction and the duplicate-protection
coverage difference. Change the reviewed comparison outcome to `compared`.
The original generated outcome and artifacts remain unchanged. Corrected text
must not be presented as successful automatic generation.

On 19 November 2026 the user reported checking manually that Alex sees the
corrected feedback and Casey remains an unpublished draft. This is a user-
reported check of separate publication/student visibility after Lecturer editing,
not an agent browser test or a new model-quality success. No further device,
browser or scenario coverage is inferred. The group mechanism and separate
publication worked in this scenario; automatic comparison quality failed the
known-difference test and required substantive human correction.
