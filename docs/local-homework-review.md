# Experimental local English homework feedback

## Current availability and boundary

UC-05 now uses the installed Qwen3 8B Q4_K_M/Ollama 0.40.14 for experimental
**English** individual feedback and anonymous comparison. Hebrew generation remains
unavailable. Synthetic demonstration work only; no remote API, paid fallback,
download or runtime fake. Lecturer review is mandatory; this is not an accepted
automatic assessment of correctness. The rubric experiment improved UNIQUE/cache
findings but retained false atomicity criticism. See the
[full prior draft experiment](homework-rubric-draft-pair-feasibility.md).

## Running and trying it

From the repository root, using the existing website environment and installed
local GPU/runtime assets:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo_homework_review
.\.venv\Scripts\python.exe manage.py run_homework_worker
```

Run the development server in another terminal as usual. `--once` processes one
queued request and exits. A single-worker lock prevents duplicate coordinators.
The worker creates/cleans its own loopback-only Ollama server and acquires the
shared decoder lock, so it does not require a manually started experiment server.
Missing/mismatched assets fail clearly; they are never downloaded/substituted.
Demo accounts and memberships must already exist; the seed command changes no
passwords and creates no AI feedback/publication. Its fixture is the versioned
[synthetic source](../classroom/demo_homework.json), not a missing private file.

1. As lecturer_alpha open DEMO-CS101 -> Homework AI review demo -> Assignments
   and submissions -> Synthetic registration approaches · AI review demo.
2. Read/edit the professional rubric on the assignment page. Existing requests
   retain their earlier recorded rubric. New assignments include this field.
3. As student_alex open an owned submitted version and request feedback. Refresh
   later to see status; a request never grants access to a private draft. No
   automatic browser polling or automatic publication is claimed here.
4. As lecturer_alpha open the version's review-request link. Read the recorded
   work, instructions, criteria and rubric alongside the editable individual
   feedback and comparison. Original generated JSON and full peer sources are
   confined to a Lecturer-only details panel.
5. Verify meaning and attribution. Correct false criticisms and wrong comparison
   outcomes, including false 'no supported difference' conclusions. The generated
   outcome is preserved; the draft's reviewed outcome can be changed independently.
6. Private quote fields show exact verification against their bound source. Fix
   or remove unmatched evidence, then Save draft. Public narrative fields do not
   automatically embed these private evidence fields. If a narrative itself has
   an unsupported claim, correct it separately; quote validation cannot judge it.
7. Publish in a separate action. With failed comparison, explicitly choose
   individual-only publication. Confirm as student_alex that only the matching
   version has the reviewed publication. Other students' URLs return 404.

The server enforces current course roles on request, source reading, draft
editing and publication. Students receive only published narrative/outcome,
never raw generation, rubric snapshots, peer sources or private quote fields.
Conservative checks also block known peer account identities and verbatim peer
passages at publication. They do not establish semantic anonymity; the Lecturer
must remove indirect identifying details. A common long passage can be flagged
even when it also appears in the target; rephrase the public narrative.

## Operating envelope and failure semantics

These are initial engineering limits, not assignment requirements or proven
classroom capacity. Small examples completed in about 35 seconds; the 180-second
processing deadline provides headroom without allowing indefinite generation.

| Bound | Enforced behavior / reason |
|---|---|
| English, professional rubric required | Preflight before enqueue; avoids waiting for unsupported language/provider. |
| 1–4 criteria, each <=250 characters | Independent criterion calls; measured scenario uses four. |
| Instructions <=2,000; rubric <=4,000 characters | Constrains repeated prompt overhead while fitting the tested 3,866-character rubric. |
| Each source <=4,000 characters | Bounds the full-work input repeated per criterion. |
| <=3 peers and <=8,000 characters across target plus all selected peers | Snapshot latest version of every other owner; reject overflow explicitly, never silently sample peers. Three-peer maximum remains unbenchmarked with a real model. |
| Context 8,192; output <=2,304 tokens per call | Same local model envelope as the probe. Character limits are conservative practical bounds, not an exact tokenizer guarantee. Truncated/invalid output fails rather than becoming a draft. |
| 180 seconds from worker start, excluding queue wait | One deadline across both stages, service startup and inference. No automatic retries. |
| One worker / shared decoder lock | One local review at a time; busy GPU work can fail explicitly and requires a new user request. Classroom throughput is not validated. |

The owned subprocess tree is closed on timeout/worker exit; temporary private
IPC files are removed. A hard-stopped coordinator can leave a running DB state
until `run_homework_worker` restarts, when it marks interrupted work failed.
No automatic service supervisor is included. Existing queued requests are
rechecked against the envelope by the adapter before inference.

No peers produces personal feedback with the system no-peer notice. Comparison
failure retains a successful personal draft and requires individual-only
publication with the approved failure notice. A completed comparison with no
supported difference is a separate outcome, editable by the Lecturer if wrong.
Individual failure creates no publishable draft. Unmatched quotes alone do not
discard otherwise structured output: they remain unverified and block publishing
until corrected/removed. Invalid source indexes/structural failures still fail
the affected stage. Subsequent reviews require separate review/publication.

Source texts, latest-peer version IDs, instructions, criteria, language and rubric
are frozen at request creation. Resubmission never relabels earlier feedback.
Original generated output, identity, options, per-call load/generation/wall times
and errors remain private. Synthetic versions/feedback follow demo retention;
intentional cleanup and real-student-work policy remain separate open work.

## Implementation and evidence

`LocalHomeworkReviewer` implements the existing provider contract and configures
the recorded rubric/deadline. `local_homework_runner` owns the pinned service,
watchdog and shared GPU lock; `homework_contract.generate` evaluates each
criterion separately and then compares actual full submissions. No expected
coverage map enters a prompt. `homework_worker` validates structure/source
references, preserves originals and creates a private `FeedbackDraft`.
`homework_evidence` checks source-bound quotes; `homework_review.publish` rechecks
evidence and privacy after edits before recording immutable published content.

Migrations 0009/0010 add assignment/job rubric fields, processing start time,
editable private evidence and reviewed comparison outcome. Existing publications
and source versions are retained. Software checks are in
[test_local_homework.py](../classroom/test_local_homework.py) and the existing
[workflow suite](../classroom/test_homework_review.py). Actual-model measurements,
failures and content review are recorded separately in
[testing](testing.md#experimental-local-homework-integration).

The user subsequently reported manually editing Alex Version 2's comparison,
removing the misattributed Evidence 13, saving and separately publishing it.
Alex saw that corrected publication on Version 2; Version 1 retained its earlier
publication time and comparison. This verifies the reported browser workflow,
not the model's comparison correctness. The original ready-private-draft links
in the integration record now refer to published review history. New manual
draft checks require a new explicit request; published feedback is immutable.
