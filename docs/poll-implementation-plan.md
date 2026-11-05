# Unit C — Poll Lifecycle and Deferred AI Generation

Status: lifecycle implemented with server and JavaScript logic checks; browser/phone acceptance remains unverified. Real AI generation is disabled and unverified. D-08 through D-11 remain the approved target; D-31 resolves language/input length and D-32/D-33 define the implemented boundary and separate local demo route.

## Implemented lifecycle and approved boundary

The user approved this stage under D-31 through D-33. Django models, migrations,
server forms/views and basic responsive screens implement Draft -> Active ->
Closed. Editing is draft-only; publication, final voting and closure require
CSRF-protected POST. The source type is chosen before generation and stays fixed.
The normal generation adapter is disabled, makes no provider calls and produces
no invented draft. Its UI reports unavailable/unverified. Only automated tests
inject a fake provider. There is no runtime fake-provider setting or automatic
fallback. No external AI request or billing change occurred in this stage.

A separately approved local command, seed_demo_polls, now creates clearly labeled
non-AI demo drafts for manual checks. This is not a fake provider or automatic
creation substitute. It provides one comprehension and one opinion sample in
Hebrew by default, with English available via --language en. It never publishes,
resets votes, overwrites edited drafts or changes an existing status. --new-set
explicitly creates another pair. The initial local examples are polls 1 and 2
in meeting 5 of DEMO-CS101; both were created as drafts.

Real provider wiring, model language/quality validation and data permissions are
future integration work. Further AI requests remain outside this unit; no paid route is approved.
Completing this unit establishes the lifecycle with fixture evidence, not full
AS-03 coverage or a genuine end-to-end AI demo.

## Lifecycle behavior and full generation target

1. **Generation and editable draft (full target; real generation deferred):** a lecturer in their own course selects
   comprehension/opinion before creation and pastes learning material. A real
   model proposes a question and four options. Comprehension additionally has
   one correct option and short explanation; opinion has neither. The lecturer
   can review/edit every applicable field before publication. Failure shows an
   error and an explicit retry action; no prepared answer masquerades as a
   generated result. Do not save a partial/invalid response as a publishable draft.
2. **Publish:** validate the complete draft and transition it to Active with a
   CSRF-protected POST. Enforce one active poll per meeting at the database and
   transaction boundary. Multiple drafts may exist; no unapproved one-draft or
   one-course system limit is introduced. Reject edits after publication.
3. **Vote:** identified Student members cast one single-choice response through
   POST. Server uniqueness on poll/student prevents repeats and changes, even
   through direct requests or concurrent tabs. Validate option/poll/meeting/course
   association and active status while holding the transition lock.
4. **Live lecturer results:** show number of respondents and counts/percentages
   for each option. Suggested reuse of Unit B visible-page 5-second polling;
   denominator is accepted votes, with zero votes displayed as 0/0% and no
   division error. Students receive no live aggregates or comprehension keys.
5. **Manual close and disclosure:** close by lecturer POST; reject subsequent
   votes and permit another poll to be activated. Students then see aggregate
   results without respondent identities, and only for comprehension, the
   lecturer-approved correct option and explanation. No grades or correctness
   evaluation for opinion polls.

## Technical boundary

- Reuse Django Templates, small JavaScript, membership-scoped permissions and
  SQLite development setup. Implemented entities: Poll (type, language, material, four options in validated JSON, content, lifecycle, origin/version and timestamps) and unique PollVote (option index, student and timestamp).
  Preserve the type chosen before generation. Never include the answer/key in
  student HTML, JSON or hidden elements while the poll is active.
- Put real generation behind a replaceable Python interface, e.g.
  `generate_poll(material, poll_type, language)`. Validate output structure before
  presenting it. Treat pasted material as source data, not instructions. Do not
  hold a database write transaction while waiting for a provider. Recheck current
  lecturer membership and draft state when saving a returned result.
- Keep keys in ignored local configuration. Use bounded timeouts and safe
  diagnostics, with no automatic retry/provider fallback. Current permission
  covers a sample experiment, not real-class data or paid operation.
- Reuse responsive participation patterns. No files, open questions, automatic
  scheduling, post-publication editing, vote changes or grades are introduced.
  Offline ambiguity and university-network feasibility are unchanged.

## Verification and completion boundary

- Synthetic provider responses in automated tests verify success, malformed JSON,
  wrong type/option count, missing key/explanation, timeout and safe failure.
  These are test doubles, never evidence of genuine model generation.
- The regular application uses only the disabled adapter in this stage; tests
  assert that it cannot silently use the fake provider or call a real endpoint.
  Fixtures permit lifecycle testing without enabling generation in normal use.
- Two student accounts plus lecturer exercise create/edit/publish/vote/close,
  counts and percentages, zero votes, disclosure timing and a further poll.
- Direct GET/POST and JSON access tests cover foreign courses, wrong roles,
  removed membership, CSRF, key leakage before closure, and no respondent
  identities in student results. Race tests cover publication, duplicate votes
  and a vote competing with closure. Reject edits/vote changes server-side.
- A permitted successful real-model generation and manual desktop/phone checks
  are recorded separately. If the provider is unavailable, describe that gap;
  do not claim the end-to-end demo or model quality passed on mocked evidence.
- Lifecycle-stage completion: draft editing, publication, one final vote,
  closure and disclosure rules pass through real server code with test fixtures;
  normal generation remains explicitly disabled/unverified. English documents
  distinguish fixture-based checks from real-model evidence and unperformed
  browser/phone checks. The full poll target is not marked complete.
- Full capability completion, later: approved lifecycle works with genuine
  generation, server checks pass, English documents
  reflect actual results/limitations, and the five-capability scope is unchanged.
  Any commit/push requires a separate user request.

## Resolved decisions and remaining integration work

- D-31: Hebrew and English, lecturer-selected output language; at most 6,000
  Unicode code points of material including whitespace, checked by form/service.
  Whitespace-only input is rejected. Real-model language quality is not verified.
- D-32: lifecycle implementation with disabled replaceable generation interface;
  fake provider only in tests. No new lifecycle decision is required to use it.
- D-33: local non-AI demo command and visible provenance labels are approved;
  this does not satisfy real automatic creation.
- Still open for a later AI step: real provider/model, permitted input data,
  successful integration and quality evidence, measured latency and any future
  spending decision. No paid route or additional AI request is authorized now.
- Browser/phone usability and classroom capacity still need actual evidence.
  Offline meaning and the optional university-network study remain unchanged.

## Short manual two-account check — not executed by the agent

1. As lecturer_alpha, open DEMO-CS101, meeting 5, then Polls. Both demo drafts
   are explicitly labeled not generated by AI. Review and edit poll 1, including
   all options, the correct answer and explanation; save and publish it.
2. In a separate browser/private session as student_alex, open the same meeting's
   Polls page. A draft must not appear. Once published, submit one option;
   attempts to change it must fail. Neither the answer nor live totals are shown.
3. Keep the lecturer page visible: counts/percentages update without a manual
   refresh, on the 5-second read schedule plus request time. Close manually.
   Reload the student page to see aggregates and the comprehension explanation.
4. Publish poll 2 only after poll 1 closes. Vote and close again; opinion results
   contain no correct answer or correctness evaluation. No respondent identities
   or grades are displayed. A second student_casey session can verify known
   50/50 distributions with two different choices.
5. The generation form offers Hebrew/English and rejects over-6000 material;
   a valid request reports disabled/unverified generation without adding a draft
   or sending AI requests. Do not treat the demo command as successful generation.
6. Rerunning seed_demo_polls preserves the pair/status; use --new-set for fresh
   drafts after a complete rehearsal. See README for exact commands.
