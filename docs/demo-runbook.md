# Ten-minute demo runbook

## Status, scope and evidence boundaries

This is a proposed rehearsal schedule, not a completed classroom demonstration
or a measured ten-minute pass. Use the approved current scope in
[D-57](decisions-and-assumptions.md#d-57---approved-current-demo-boundary): existing
rotating QR, English automatic polls, manual Hebrew poll workflows, and experimental
English homework feedback/comparison with Lecturer review/edit/separate publication.
No face recognition, new capabilities, paid service or automatic Hebrew work.

The handout asks for an approximately ten-minute in-class web demo and a short
account of results (page 1 guidance; page 2 To Do 9–11). It does not explicitly
require a slide-deck submission. Slides are an optional presentation aid.

## Preparation before the timed demo

- Verify the actual demonstration network, exact server IP/allowed host and the
  phone's access if using it. Home-network Safari success is not evidence of
  classroom Wi-Fi access. Lecturer and Student must use the same LAN origin so
  the QR targets the computer. Keep access private/temporary and follow
  [phone instructions](phone-testing.md); do not introduce a public tunnel.
- Open separate authenticated Lecturer/Student browser sessions (lecturer_alpha
  and student_alex). Keep demo credentials in their existing ignored local file,
  never in documents/slides. Use a fresh authorized meeting for attendance and
  polls, with no active poll. Do not erase previous attendance/publications.
- Open the needed five-feature pages in advance and identify their local IDs.
  Test materials are synthetic, except the permitted lecture sample. Use the
  checked SHORT-EXPLAIN.mp4 sample for the live video; recheck it is locally
  available and inside 4 minutes/200 MB. Do not distribute media in Git.
- Prepare a theoretical assignment, its fixed professional rubric and the two
  synthetic conditional-update/locked-recheck works from
  [demo_homework.json](../classroom/demo_homework.json). Keep the source/criteria
  visible for reviewing feedback. Another Student's work must remain private.
- In separate terminals, start the existing run_homework_worker and
  run_video_worker commands in the website environment. Verify no stale/queued
  unrelated jobs precede the demonstration. Missing models fail; do not download
  or change providers during the demo. These preparations were not executed by
  the agent while writing this plan.
- Prepare **previously generated** English poll, video summary/transcript and
  homework feedback views as backups before the presentation, with model/date,
  source/version and Lecturer edits identified. A ready draft must be unpublished
  if it is to be edited live; published feedback is immutable. Never reset an
  existing publication just for the demo.
- Important preparation finding: the read-only inventory on 2026-11-15 found
  all existing site video transcript/summary links expired, including the old
  successful SHORT job. They are not currently usable site backups. Prepare a
  fresh successful upload before rehearsal/presentation under the normal policy,
  then check it again on demo day. Do not extend expiry or resurrect old content.
  The frozen historical summary below remains a document-only evidence backup.
- Prepare a short English poll input: 'A stack removes the most recently added
  item first (LIFO), like a pile of plates. A queue removes the earliest added
  item first (FIFO), like customers waiting at a service desk.' Check generated
  meaning before publishing; no particular new output is promised.
- The comprehension visibility check now has [user-reported Safari/iPhone evidence](testing.md#user-reported-comprehension-disclosure-check---completed); the agent browser attempt remains blocked. Do not repeat this solely to replace the missing automation. Complete one timed rehearsal before claiming
  the following schedule fits. No new software suite is required.

## Running order: 10:00 target

| Time | Presenter actions / user roles | Expected result and explicit fallback |
|---|---|---|
| 00:00–00:30 | Explain one course/meeting, Lecturer versus Student and the five features. State synthetic work, local AI, current English limits and draft review. | Audience understands project choices and the live-versus-previous-result labels. |
| 00:30–00:55 | Student submits a new synthetic homework version and requests feedback; existing peer work is already present. | Submitted/version confirmation and queued request; worker begins in background. Do not wait on this screen or publish automatically. |
| 00:55–02:00 | Lecturer opens initial attendance window; Student scans current QR (phone if connected). Show Lecturer roster and optionally export XLSX. | Student registration confirmation, one roster entry/time; XLSX is a snapshot. QR rotates, but can be forwarded and does not prove physical presence. If classroom phone access fails, disclose that and use the Student browser; do not claim a classroom phone pass. |
| 02:00–02:40 | Student sends a comment associated with the meeting; show Lecturer view. Explain during/outside-class meaning. | Stored request appears to Lecturer; Student sees own history. Do not claim disconnected operation. |
| 02:40–04:20 | Confirm homework generation has finished/GPU is free. Lecturer generates an English comprehension draft from the short input, reviews/edits and publishes. Student votes. Lecturer shows live counts, then closes; Student reloads. | Correct answer/explanation and aggregates hidden from Student before close, shown after close. One final vote. If generation fails/delays, switch explicitly to a previously AI-generated draft/result; a seed_demo_polls fixture is labeled demo data and proves lifecycle only. |
| 04:20–04:50 | Only after prior GPU work finishes, upload SHORT MP4 to the meeting's Video processing page. | New queued/processing task; site remains usable. No completion claim while it is waiting. |
| 04:50–07:10 | Lecturer opens the homework draft for the exact requested version; compare against source/rubric and private evidence. Correct a real model error and anonymous comparison/outcome; remove/correct unmatched evidence, save, then explicitly publish. Student opens matching version. | Published personal feedback and anonymous comparison only for that version. Show the prior version unchanged if useful. If live review failed, show a labeled previous generated draft/publication and its recorded correction; never fabricate a successful generation. |
| 07:10–09:20 | Return to new video task. If ready, show Automatic summary, paragraph/points and full transcript link; inspect a short known passage. | Same-recording-language, speech-only analysis and error notices. If not ready/failed, show actual status plus the labeled prepared previous result or historical document backup; distinguish this from success of the new task. |
| 09:20–10:00 | Recap five paths, current limitations and observed failures; state what ran now versus earlier. | Honest short results account; stop rather than launching another experiment. |

Qwen/video work shares one GPU lock. Background work can be interleaved with
attendance/comments and reviewing existing drafts, not with another model call.
If the first homework task is not finished by the poll segment, use the prepared
poll and avoid another model request. A 30-second presentation timebox for any
foreground wait is a switch to disclosed backup, **not cancellation**: confirm
the earlier model process has ended before starting another GPU job. If it has
not, use prepared results for the remaining AI segments. The software's existing
120-second poll, 180-second homework and 600-second video limits are not promises
that the entire class demo will finish within those times.

No-peers, comparison failure with successful personal feedback and completed
no-supported-difference remain distinct states. Do not manufacture an error for
the presentation; show an actual recorded case if available. A model's false
no-difference claim must be corrected before publication, not promoted as fact.

## Prepared AI evidence backups

Say: **'This is a real result generated earlier, not by the current request.'**
For a Lecturer-edited result add: **'The Lecturer corrected this comparison.'**
Backups are independent evidence displays, never injected as provider fallbacks.

| Capability | Available recorded backup | Boundary |
|---|---|---|
| Polls | [Actual English comprehension output](../experiments/local_ai/results/qwen3-8b/poll_en_comprehension.json) and [local poll findings](local-poll-feasibility.md); local closed AI polls were present in meeting 6 at preparation time. | Prior actual generation; not a new run. Review correctness before presentation. A non-AI seeded draft must never be called generated. |
| Homework | [Full fixed-rubric drafts/comparisons](homework-rubric-draft-pair-feasibility.md), [portable outputs](../experiments/local_ai/results/homework-focused/rubric-draft-pair/summary.json), and user-reviewed version-specific publication in [testing](testing.md#user-reported-manual-review-and-version-specific-publication). | Generated comparisons contain substantive mistakes. Published corrections are human work; raw peer evidence is Lecturer-private. No website submissions are exported into this runbook. |
| Video | The frozen SHORT summary below, from the prior local summary experiment, plus [claim-by-claim review](local-summary-feasibility.md#claim-by-claim-transcript-grounding-review). | Historical experiment prompt, not proof of current upload completion or current prompt output; old website links have expired. Full media/raw transcript remain local-only. |

### Frozen actual SHORT summary (unchanged output)

Qwen3 8B Q4_K_M, previous local experiment on 2026-11-08; wall time
2.863 seconds in that already-warm experiment, **not** full video processing time.
The original source record is local-only at
`.ai-lab/results/turbo-summary-probe/20261108T145201877600Z/short.json`.
Only the generated summary is reproduced; the original transcript is not copied.

Object-oriented programming is a popular approach that organizes code around objects, using classes as blueprints to create instances with attributes and methods. Inheritance allows new classes, like a boat, to inherit properties and methods from existing ones, such as a vehicle, while adding unique functionality. However, objects can have mutable states, making debugging more challenging, especially when passed around.

- Object-oriented programming organizes code around objects and classes.
- Inheritance allows new classes to inherit properties and methods from existing ones.
- Objects may have mutable states, complicating debugging.

Source review found this English summary consistent with the supplied automatic
transcript, including boat inheriting from vehicle. This is not word-level
verification against the recording. Transcription errors may propagate; unspoken
visual content is excluded. Hebrew transcription/summary accuracy remains limited.

## Closing and recording the actual rehearsal

Record actual total/segment times, which model jobs completed live, backups used,
any Lecturer edits and failures; do not pre-fill this plan as an executed demo.
Stop the temporary LAN server and remove only the specifically created temporary
firewall rule after network testing/demo use ends, using the earlier provided
cleanup instructions. No firewall or process settings were changed while writing
this runbook. Keep submitted versions/publications through the required demo and
submission checks; intentional cleanup remains planned rather than silently done.


## Rehearsal readiness and reported model-busy handling

A read-only readiness check at documentation closure found the pinned local
Qwen3 8B manifest/model blobs valid, the configured Python/Ollama files present
and the turbo checkpoint directory present. There were no queued/running homework
requests and no video tasks in an active state. There were **zero unexpired saved
website video summaries**. File checks do not prove a future inference will work;
no inference was run as part of this check. Prepare and inspect one fresh video
result before rehearsal and verify model readiness again at rehearsal time.

The user reported a “model busy” message. Its exact source was not supplied.
The shared decoder lock is nonblocking across video/poll/homework, so these
features do not form one guaranteed wait-until-free queue. A busy response may
mean that a new operation failed rather than remaining queued. Inspect the
affected job/form state before an explicit later retry; do not click repeatedly.

Preserve this order: request homework, perform QR/comments while it runs, confirm
its terminal state and the inference process has ended, then generate the poll;
only after poll generation finishes start video processing. While video runs,
review/edit/publish the already generated homework draft. Viewing/editing/voting
does not require another model call. If an earlier model operation has not ended,
use a labeled previous result for the next AI segment instead of competing for
the lock. No model download/provider switch or new infrastructure is needed.
