# Submission closure — 19 November 2026

## Requirement boundary and reading route

The two-page local Exercise 2 PDF was read again for this closure. Page 1 requires
the five teaching capabilities, an implementable KISS smartphone website and
real-class use; design is the main challenge and implementation is secondary.
Page 2 lists eleven populated To Do items. It does not prescribe a ZIP layout,
submission channel, slide deck or exact due date. The PDF is intentionally not
redistributed in the repository. Lecture timestamps elsewhere are user-supplied
review summaries, not independently inspected recordings/transcripts.

Start with the [eleven-item submission map](../README.md#assignment-deliverables),
then [SoW](SoW.md), [requirements/use cases](SRS.md),
[architecture](architecture.md), [rendered diagrams](diagrams/README.md),
[testing](testing.md#submission-closure-validation---2026-11-19) and
[tools](local-ai-feasibility.md#current-tools-and-evidence-index).
Item 10, the classroom demonstration/defense, **has not been performed**. The
reported guided rehearsal is not a substitute. This is a technically prepared
repository, not an unconditional claim that every assignment item is complete.

Project choices remain QR attendance, English automatic polls and experimental
English homework review/comparison with private Lecturer editing and separate
publication. Automatic Hebrew is a future target, not a current-demo blocker.
Short MP4s are sufficient for this proof of feasibility. Manual Hebrew polls
remain supported. Production hosting and real-student-data policy are outside
the approved demonstration scope.

## Approved additions completed in this closure

| Addition | Implemented behavior and evidence |
|---|---|
| Manual polls | Lecturer chooses comprehension/opinion, writes a question/four options and saves a private draft without a model. Comprehension requires one correct answer/explanation; opinion forbids them. English/Hebrew, existing validation/edit/publication/voting gates, explicit `manual` provenance. |
| Comment XLSX | Lecturer-only per-meeting snapshot with request ID, author, username, type, text and Jerusalem time. All strings are stored as spreadsheet text, including `=`, `+`, `-`, `@` prefixes; original database text is unchanged. No import/sync. |
| Points for lecturer review | New video uploads optionally generate zero to two short inspection suggestions after the summary is safely stored. Each has an exact quote and a server-derived time range spanning the matching ASR segments. No audio/image/student-understanding judgment. Failure, interruption and timeout preserve saved summary/transcript. Same owner/course guard, seven-day expiry and overall 600-second budget. Old tasks are not reprocessed. |
| Attendance limitations | Roster and documentation distinguish account registration from physical presence. The Lecturer discusses discrepancies with the student; an additional window allows registration without duplicates. No face recognition or new manual-correction mechanism. |
| Intentional cleanup | `cleanup_demo` previews counts by default; deletion requires explicit seeded course code(s) and `--apply`, and refuses active work. No data/evidence was deleted in this closure. Accounts/credentials remain; private file maintenance is separate. |

## Validation and measured results

The final software suite passed **215 Django tests** (21.100 seconds, no skips)
and **21 JavaScript tests**. New tests cover manual provenance/lifecycle/disclosure,
server role/direct-URL guards, opinion metadata rejection, spreadsheet literal
text, exact/cross-segment evidence, optional-report failure/recovery/expiry, cleanup
preview and polling refresh. Model providers in these tests are injected fakes;
they establish software behavior only. Migration 0012 was applied locally after retaining a private DB backup;
no records were deleted. Migration consistency and clean startup
are checked separately; see [reproduction and operations](operations.md).

### Isolated attendance and voting load

Success conditions were fixed before requests: for each of 80 and 100 users,
zero unexpected statuses, p95 below 5 seconds, maximum below 10 seconds, exactly
one attendance/vote per account, unchanged original vote choices after duplicate
attempts. Each phase released its user requests concurrently. Authentication
sessions were prepared before timing; requests used real loopback HTTP, session
cookies and CSRF through threaded WSGI and file-backed SQLite. No AI and no demo
database were used. Expected duplicate-vote HTTP 409 responses are not errors.

| Accounts | Attendance p95 / max | Vote p95 / max | Exact counts | Result |
|---|---|---|---|---|
| 80 | 2.079 / 2.452 s | 3.588 / 4.025 s | 80 attendance, 80 votes | Passed |
| 100 | 2.867 / 3.404 s | 4.825 / 5.233 s | 100 attendance, 100 votes | Passed |

Duplicate attendance kept the same counts; duplicate voting was rejected in all
180 attempts. Full [measurements](../experiments/results/closure-load-20261119.json)
and [opt-in reproduction code](../experiments/load_probe.py) are versioned. At 100
users voting p95 is close to the chosen threshold: this is evidence for this
machine/workload, not a production capacity guarantee. Wi-Fi, multiple physical
devices, repeated sustained waves and concurrent classroom AI were not measured.

### Real local lecturer-review output

Only the new video-review stage was exercised with installed Qwen3 8B Q4_K_M /
Ollama 0.40.14 and the saved English SHORT turbo transcript, without another
transcription or homework experiment. Earlier development attempts were retained
locally: 20.601 s and 9.009 s were output-validation failures; a diagnostic run
showed an exact phrase crossing ASR segments being rejected, and false claims
that the lecture omitted explanations. An intermediate 8.387-second output was
structurally accepted but still made unsupported absence claims. These are not
quality passes or silent automatic retries.

The final `lecturer-review-v2` contract requests only a quote and a cautious check,
not a verdict/defect assessment. Exact matching uses the full transcript with only
segment-boundary whitespace normalized; time bounds are derived from the actual
matching segments. Ambiguous or unmatched evidence fails, rather than being guessed.
Final adapter wall time **7.671 s**, model request **4.908 s**, load **2.823 s**,
generation **1.742 s**. It produced:

| Time range (seconds) | Exact quote | Unedited generated suggestion |
|---|---|---|
| 5.68–11.44 | It separates and organizes your code around objects. | Check if 'objects' is clearly defined before introducing the concept. |
| 23.04–33.78 | But where this gets really powerful though is through inheritance. | Verify that 'inheritance' is explicitly explained with an example. |

Both quotes/time ranges match the saved transcript. A boat/vehicle example follows,
so the second suggestion is a check the Lecturer can resolve, **not evidence that
an example is absent**. Suggestions are basic and their usefulness is limited;
accurate quotes do not validate conclusions. Zero points is valid and tested in
software. No new Hebrew real-model validation or full fresh MP4 run of this optional
stage is claimed. The stage's worker integration is software-tested; the real
adapter result is [preserved](../experiments/results/lecturer-review-short-20261119.json).
Raw transcripts/media and development failure captures remain local-only.

## AI limitations and remaining acceptance

- The selected homework group completed and the user verified Alex's corrected
  publication while Casey stayed private. The model missed known differences and
  duplicate-topic coverage. These human corrections are not automatic successes:
  [full evidence](homework-group-acceptance.md). Reliable deep comparison remains
  a substantive AS-05 quality gap, even though the proposed review workflow works.
- English poll generation still requires Lecturer semantic review. Hebrew
  transcription can corrupt technical terms/negation. STATIC summary language
  validation previously rejected a full-upload result while retaining its transcript.
  Neither successful UI flows nor exact quote checks establish broad AI accuracy.
- The source PDF's real-class use/item 10 remains unverified/not performed.
  Guided rehearsal and the user's earlier real-iPhone participation checks retain
  their actual evidence scope. This closure did not perform another phone test.
- Browser observation is still denied by the saved local-origin permission. No
  alternate browser or headless application workaround was used. The only remaining
  focused visual checklist is: inspect the manual poll form in Light/Dark and narrow
  view, and inspect the optional review section on a video task. The user has
  subsequently reported manual poll creation/publication and comment XLSX export/
  opening; see [recorded reports](testing.md#recorded-manual-closure-reports---2026-11-22).
  No additional device/theme coverage is inferred. There was no existing website
  review-point task on 22 November; another real run was not silently performed.
  Software checks do not substitute for visual acceptance.
- Submission channel/package convention, exact deadline and demonstration/defense
  arrangements require external confirmation. No slide deck or export format is
  invented. The repository and linked SVG gallery are the prepared deliverable.

No payment, external inference, new model download, model research or deletion of
existing evidence occurred during closure. Existing uncommitted Gemini/PDF source
files are unchanged; the tools report summarizes only relevant saved observations.
