# Verification Record — Units A, B, C, D and E

## Unit E — Local Transcription — 2026-11-08

- **106 website tests passed**, file-backed SQLite, 48.750 s, no skips; 32 focused video/transcription checks passed in 15.381 s. Tests inject ASR fixtures only; actual GPU evidence is separate below.
- **10 JavaScript tests passed**, fake DOM, not a browser. New cases cover real-stage labels, audio deletion state, successful transcript link visibility and expiry hiding.
- Tests cover normal transcription-before-WAV-cleanup, private escaped full text, mixed-language markup, no text in polling JSON, same-course other Lecturer/student/anonymous denial, revoked/demoted owner, mismatched parent URLs, exact seven-day expiry/HTTP 410 and content purge, cleanup, model failure, invalid output, missing runtime/no download, original shared deadline and legacy extraction-only behavior. Existing timeout/stop/watchdog tests cover shared worker recovery; no real GPU hard-kill test is claimed.
- Two **new actual sample uploads**, real offline CUDA float16 medium inference: SHORT detected en, load 2.837 s, ASR 12.439 s, total 26.666 s; STATIC detected he, load 1.578 s, ASR 190.870 s, total 195.856 s. WAV/pending JSON absent after both. Both owner-authenticated detail/full-text responses returned HTTP 200 and included the complete escaped text. This used the upload service, real separate worker and in-process Django requests, not browser automation or a new browser-upload report.
- The user reported difficulty preparing a reliable listening-only reference and approved continuing functional checks. **Word accuracy and English programming-term accuracy have not been verified against manual transcription.** No verified word examples or WER are claimed. Mixed-language visual layout still needs user/browser inspection.
- Summary remains disabled. No API calls, model downloads, installations or billing occurred in this stage. The 13 pre-existing Gemini experiment changes remain separate/unchanged. See [local-transcription.md](local-transcription.md) for exact local versions, privacy/expiry, timing boundaries and manual steps.

## Unit D — Video Infrastructure — 2026-11-08

Implemented boundary: private upload, queued persistent state, real MP4 checks
and audio extraction. No transcription/summarization/model request, download,
billing or agent-run browser test occurred. Gemini experiment files were left unchanged.

| Executed check | Observed result |
|---|---|
| Focused video suite, file-backed SQLite | **20 passed**, 5.343 s, no skips |
| Full website suite, file-backed SQLite | **94 passed**, 44.669 s, no skips: previous 74 plus 20 video tests |
| `node --test tests_js/*.test.cjs` | **8 passed**, including 3 video polling/state tests; fake DOM, not a browser |
| Dependency installation | Only PyAV 16.0.0 added to the website .venv; 32.3 MB official wheel; no model/driver/system change |
| Migration 0004 / dependency / schema checks | Local migration applied; no broken requirements or pending migration changes |
| Actual existing MP4 clips | Both within 240 s and 200,000,000 bytes; real extraction completed via local queued jobs and separate worker commands; temporary WAV absent after each |

Sample evidence (not an AI benchmark): SHORT-EXPLAIN.mp4, 14,645,300 bytes,
56.74957 s video, 56.74956 s extracted audio, 4.43773 s worker elapsed;
STATIC-EXPLNATION.mp4, 10,477,365 bytes, 235.28780 s video, 235.28781 s extracted
audio, 2.919206 s worker elapsed. Elapsed times include startup and integrity
decoding; neither predicts AI latency/quality. Originals were opened read-only;
private uploaded copies and run metadata are ignored by Git.

### Actual assertions

- Real generated MP4 audio/video data, streaming save, queued POST redirect and
  use of another site page; actual worker extraction; verified 16-kHz mono PCM
  WAV samples and deletion before success.
- Corrupt bytes, no-audio video and audio-only container rejected by worker with
  persisted Checking video failure stage/code. Extension and multi-file forms
  rejected; MIME/extension alone never establish successful decoding.
- Size is 200,000,000 bytes. Declared 200,000,001 rejects before saving; actual
  multipart/copy byte boundaries are exercised with lowered test limits rather
  than allocating a 200-MB fixture. Both existing real clips pass the actual cap.
- Duration enforcement uses real media under lowered test limits; exact measured
  duration accepted, just-above boundary rejected. Both supplied clips pass the
  production 240-second cap; no full 241-second fixture was generated.
- Owner-only HTML/JSON including same-course second Lecturer denial, students,
  foreign/mismatched paths, anonymous login, CSRF, demotion and removed membership.
  Queued role revocation prevents decoding. Private paths do not appear in pages.
- Queue wait is distinct from processing time; one-hour-old queue entry still
  gets a fresh worker-start budget. Single-worker OS lock and FIFO are checked.
- Actual subprocess termination under a shortened test timeout, plus persisted
  started-at >600-second recovery; no 10-minute wall-clock wait is claimed.
- Graceful stop and stale heartbeat recovery; actual hard termination of a test
  coordinator, parent-death watchdog/decoder-lock release, failed persisted state
  and partial-WAV removal. Test subprocess helpers are test-only, not runtime modes.
- Independent maintenance command, expired queued-source cleanup, orphan WAV and
  old multipart cleanup, fixed-path/traversal protection and unrelated-file safety.
- Separate disabled transcription/summary contracts, neither invoked by extraction.
  No synthetic text is presented as actual AI processing.

The local worker and separate maintenance process were started for current demo
use; the web server remains 127.0.0.1:8000. They must be restarted after a machine
restart. Maintenance is required independently of the worker for 24-hour cleanup;
offline/stopped services cannot guarantee physical deletion on schedule. See
[video-processing.md](video-processing.md) for commands and the early-purge margin.

Agent-run browser interactions, phone upload/layout, class load, pathological
codecs and real AI quality are not verified here. The previously denied browser-
origin gate was not bypassed. The later user-reported manual result below is
separate evidence for its reported path only. Full AS-04/AC-04 remains incomplete;
this stage establishes extraction infrastructure.

### Unit D pre-commit verification

After recording the user report, the full suite passed **94 tests**, 45.239 s,
on isolated file-backed SQLite, with no skips. All **8 JavaScript logic tests**
passed. Django check, migration drift, dependency consistency and diff whitespace
checks passed. No AI request or billing action was part of this verification.

### User-reported manual video check — 2026-11-08

The user reported testing SHORT-EXPLAIN.mp4 in the browser. After starting the
worker, the already queued task changed to **Audio extraction completed**.
The UI displayed **118.2 seconds waiting**, **4.5 seconds processing**, and
**56.75 seconds of audio**. The site reported that temporary audio had been
deleted. These are user-reported browser observations, not actions directly
performed or observed by the agent; the UI deletion notice is not a separate
user inspection of files on disk.

This report does not establish other media cases, phone layout, permissions,
recovery, timeouts, 24-hour expiry or AI quality; their specific automated evidence
and remaining limitations are recorded separately. **Transcription and summaries
remain disabled and unverified.** No additional AI request is implied by this check.

Date: 2026-11-05. Environment: Windows 64-bit, Python 3.12.14, Django 5.2.19,
SQLite. The historical Unit A section below covers the shared foundation; the Unit B section records later attendance/comments checks. It does not
mark any five-capability acceptance check AC-01 through AC-07 as passed.

## Executed checks

| Check | Observed result |
|---|---|
| Install website dependencies in separate `.venv` | Django 5.2.19, asgiref 3.13.0, sqlparse 0.6.1, tzdata 2026.6 installed |
| `python manage.py check` | No issues |
| `python manage.py migrate` | Django/auth/session and classroom initial migrations applied to local SQLite |
| `python manage.py seed_demo` | Two courses, six random-password accounts, seven memberships, four initial meetings created; no passwords printed |
| `python manage.py test --verbosity 2` | **24 tests passed**, 8.434 seconds; isolated in-memory SQLite test database |
| Pre-commit test rerun after replacing literal test credentials with runtime-generated values | **24 tests passed**, 8.261 seconds; system check passed and no migration drift |
| `python manage.py makemigrations --check --dry-run` | No changes detected |
| `python -m pip check` / `findstatic css/site.css` | No dependency conflicts; stylesheet discovered |
| Documentation consistency | 60 unique register IDs, 27 local links; original assignment-source rows and AC-01 through AC-07 unchanged |
| Runtime fixture counts and Git hygiene | Six users, two courses, seven memberships, four meetings; no generated demo/signing/API secret found in Git-visible files; runtime directories ignored |

The tests use Django's request client, not a browser. CSRF rejection is
explicitly tested using `Client(enforce_csrf_checks=True)`; default client
behavior alone would not establish CSRF coverage.

## Class-aware coverage

| Component | Actual assertions |
|---|---|
| Django auth views and middleware | Valid/invalid/inactive login; safe handling of external `next`; POST-only logout clears the session; anonymous requests redirect; CSRF enforced for login/logout/writes |
| Course/Membership | Lists expose only memberships; multiple courses supported; one account can be lecturer in one course and student in another; no global staff/superuser bypass; uniqueness and role database constraints |
| Current-membership lookup | Foreign direct URLs denied; membership deletion takes effect on next request; demotion prevents submission of a previously accessible edit form |
| Meeting lookup and view | Meeting ID must match authorized parent course; missing IDs return 404; read routes reject POST; cross-course edit does not modify the row |
| MeetingForm / management view | Authorized create/edit persists; posted course cannot change ownership; student GET/POST denied even with forged role/user fields; invalid date, blank/overlong title do not save; timezone-aware date stored |
| Templates | Forbidden data absent from denied responses; student management buttons absent; description HTML escaped; empty membership state displayed |
| seed_demo command | Rerun preserves password hashes and initial fixture counts; mixed-role/no-membership cases created; generated passwords are not printed; unrelated existing account is not overwritten |

Test fixtures generate synthetic passwords at runtime; no usable test password
is embedded in source. Actual
generated demo passwords, signing keys and the existing Gemini key are not
source fixtures and remain ignored local files.

## User-reported manual browser checks

On 2026-11-05, the user reported performing these checks manually in a browser:

| Check reported by the user | Reported result |
|---|---|
| Sign in and view courses and course roles | Worked |
| Create a meeting | Worked |
| Edit a meeting description and refresh the page | Saved description persisted after refresh |
| View the site with a Student role | Creation/edit buttons were absent |

These are **user-reported results**, not browser actions performed or directly
observed by the agent. Browser/device/version and viewport were not specified.
They do not establish a phone test, responsive-layout acceptance, or rejection
of unauthorized direct GET/POST requests. Hidden buttons are not an access
control: the separate automated server permission tests above provide that
evidence.

## Remaining UI verification limitation

An attempt to open `http://127.0.0.1:8000` with browser automation was rejected
by the browser origin approval gate. No alternative browser, raw browser
automation or indirect workaround was used. No agent-run browser interaction
or screenshot check passed. The later user-reported functional browser checks
are recorded separately above. **Viewport-specific rendering and real-phone
usability remain unverified.** This limitation does not invalidate the
executed in-process server permission tests.

Additional manual browser checklist, not reported as completed:

1. At desktop and approximately 375-pixel widths, sign in and check for overflow,
   keyboard focus, readable labels, button reachability and date input behavior.
2. As student_alex, see DEMO-CS101 only; confirm direct beta URLs are denied.
3. As lecturer_alpha, create/edit a CS101 meeting; view SE201 as Student and
   verify its management buttons/routes are denied.
4. As student_casey, see both courses; as observer, see the empty state.
5. Sign out and verify protected pages require sign-in again.

## Unverified and deferred

- Actual classroom user count and SQLite capacity. Unit B verifies only two simultaneous requests, not classroom load.
- Hosting/HTTPS/phone access; current server listens only on loopback.
- Production hardening, login throttling, retention/deletion and real identities.
- Browser/phone attendance scanning, XLSX UI/download and live-update usability; the server paths are covered under Unit B below. Polls, video summaries and homework feedback remain unimplemented website features.
- Offline interpretation and university-network checks.
- AI providers/adapters and AI correctness. Existing feasibility reports remain
  separate evidence; no new AI request occurred during this unit.

The foundation is a meaningful commit unit, with user-reported manual checks
and remaining UI limitations explicitly separated from server test evidence.

## Unit B — Executed Attendance and Connected-Request Checks

Date: 2026-11-05. Same Windows/Python/Django environment, with qrcode 8.2 and
openpyxl 3.1.5. Tests use generated synthetic users/data and credentials;
the development database, real passwords, media and AI keys are not test inputs.

| Check | Observed result |
|---|---|
| Full Django suite with file-backed SQLite test DB | **48 passed**, 38.411 seconds, no skips. Includes 24 Unit A tests, 21 Unit B functional tests and 3 concurrency tests. |
| `node --test tests_js/participation.test.cjs` | **3 passed**: visible-page polling pause/resume and 5-second schedule; safe text rendering and QR boundary refresh; scan form submission. Logic-only fake DOM/timers, no browser. |
| Pre-commit rerun after shortening the request notice | **48 passed**, 39.928 seconds on file-backed SQLite; **3 JavaScript logic tests passed**. |
| `manage.py check` | No issues |
| `manage.py makemigrations --check --dry-run` | No changes detected |
| `python -m pip check` | No broken requirements |
| Local migration 0002 | Applied successfully to ignored development SQLite; demo seeding was not rerun. |

The first test run found missing course context in the forbidden-response
template. That caused 500 errors instead of the intended 403; it was fixed
and the full suite rerun successfully. No failed run is treated as a pass.

### Actual assertions

- Initial 300-second and subsequent 120-second windows; active-open idempotency;
  automatic-expiry reopening and invalidation of all explicitly closed codes.
- Stable QR tokens within 30-second buckets, rotation at the boundary, valid
  overlap through 44.999999 seconds, rejection at 45 seconds and at window end;
  future/tampered/malformed/wrong-meeting codes are rejected.
- GET scan does not register; CSRF-protected POST does. Login preserves the
  attendance continuation. Expiry during login, between GET and POST, or closure
  after GET requires a new scan. Membership/role is freshly checked.
- Student/meeting uniqueness, preserved first timestamp/window/status, and exact
  Registered in an additional window label. Two requests from the same student
  create one record; two different students create two. Concurrent opens create
  one window. These tests use a barrier, threads and separate database connections.
- Lecturer-only roster/state/export/window actions; students denied management;
  nonmembers/mismatched parent courses denied; per-course roles and removed or
  changed memberships enforced. HTML/JSON are not substitutes for server checks.
- Real XLSX bytes loaded with openpyxl: expected fields/current-student roster,
  additional-window label, unchanged old snapshot after new registration, no
  write-back on editing, and leading '=' in a display name stored as text.
- Comment/suggestion history persistence and own-only student access; lecturer
  all-meeting feed; 1/1000-character Unicode boundaries after trim, blank/1001
  rejection, invalid type rejection, escaped script text and duplicate-form
  submission deduplication. CSRF rejection and database-failure reporting tested.

### Reproduce without touching the development database

```powershell
$env:DJANGO_TEST_SQLITE_NAME = Join-Path (Get-Location) ('.local/unit-b-test-' + [guid]::NewGuid().ToString('N') + '.sqlite3')
.\.venv\Scripts\python.exe manage.py test --noinput
Remove-Item Env:DJANGO_TEST_SQLITE_NAME
node --test tests_js/participation.test.cjs
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pip check
```

The generated path is an isolated temporary test database managed by Django.
Without the environment variable, regular tests use in-memory SQLite and the
three real-connection concurrency tests explicitly skip; that run cannot be
reported as equivalent concurrency evidence. The file-backed suite above ran
all three. Two-request success does not establish classroom capacity.

### User-reported Unit B manual checks

The user reported the following checks; they were not performed or directly
observed by the agent:

| Reported action | Reported result |
|---|---|
| Manual QR check | The user reported checking the QR. Device, exact steps and successful attendance registration were not specified; no additional QR scenario is inferred. |
| Submit a comment as student_alex and view it as lecturer_alpha in the same meeting | The comment appeared to the lecturer without a manual refresh. |

These reports do not establish a successful phone test, an exact five-second
latency, login continuation, expiry handling, additional windows, duplicate
prevention, XLSX correctness, server authorization or classroom load. Server
checks above remain separate evidence for their specific assertions.

No agent-run Unit B browser, real-phone, native-camera scan or responsive
screenshot check passed. JavaScript logic tests are not browser tests. The prior
browser origin rejection was not bypassed. Existing Unit A user-reported checks
above remain separate historical evidence.

Use [phone-testing.md](phone-testing.md) for desktop/two-account and future
private-LAN phone instructions. Current binding and ALLOWED_HOSTS remain
loopback-only; no firewall/network changes were made. Offline meaning, lecturer
acceptance of attendance automatically/online-offline, university-network
feasibility, retention, production security and classroom load remain open.
No AI experiment or AI website feature was started in Unit B.

## Unit C — Executed Poll Lifecycle Checks

Date: 2026-11-05. Existing Windows/Python/Django environment, no new dependency
or AI request. Real generation is disabled/unverified; tests use synthetic data
and a fake generator defined only in the test module. Local demo fixtures are
separate approved non-AI data, not evidence of generation or model quality.

| Check | Observed result |
|---|---|
| First complete website suite after lifecycle implementation | 72 tests passed, 37.926 s, isolated file-backed SQLite |
| Final complete suite after adding failed-vote save reporting | **73 tests passed**, 38.362 s, no skips; 48 earlier foundation/participation tests plus 25 poll tests |
| Targeted rerun after a small active-poll message adjustment | 2 disclosure/lifecycle tests passed, 0.107 s; no new provider calls |
| Poll test breakdown | 21 functional/server/command tests, 4 real separate-connection concurrency tests |
| `node --test tests_js/*.test.cjs` | **5 passed**: 3 participation tests plus 2 poll tests for safe live results, visibility pause/resume and stale-action handling |
| Django check / migration drift / dependency consistency | No issues, no migration changes, no broken requirements |
| Local migration 0003 | Applied successfully to ignored development SQLite |
| `seed_demo_polls --language he` | Created Draft poll 1 (comprehension) and Draft poll 2 (opinion), meeting 5 in DEMO-CS101; explicitly not generated by AI; no account reseeding, publication or votes |

### Actual server assertions

- Disabled normal generation reports unavailable and creates no placeholder.
  The only real runtime factory returns DisabledPollGenerator. Explicit test
  injection exercises valid Hebrew/English responses for both types, malformed
  output, provider exceptions, and revoked lecturer membership after generation.
  These tests are not real generation/language-quality evidence.
- Material lengths 1/6000 accepted at the input-validation boundary, 6001
  rejected on the server, including Unicode and whitespace-only cases. A valid
  request still returns 503 because generation is disabled, not a saved draft.
- Draft-only edits to question, four distinct options, comprehension key and
  explanation; invalid/duplicate/blank content rejected. Stale versions reject
  lost edits and publication of content not reviewed by that page. Opinion
  drafts reject forged answer/explanation fields.
- Drafts invisible to students; course/membership/role enforcement for direct
  HTML and JSON routes, mismatched parents, role changes/revocation, lecturer
  voting rejection, anonymous login redirects, CSRF and POST-only transitions.
- Active student HTML/JSON excludes the comprehension key/explanation and all
  counts/distributions. Closed comprehension reveals approved key/explanation;
  opinion results never designate/evaluate correctness. Student payloads contain
  no respondent identities; demo provenance and escaping are tested.
- One active poll per meeting, manual close, idempotent repeated close, no
  reopening or published-content editing, and another poll after closure.
  One final vote per student with invalid/multi-value choices and changes
  rejected. DB uniqueness/check constraints are exercised directly.
- Zero-safe counts/percentages and a known two-vote 50/50 result. Database-busy
  vote failure reports unconfirmed save without persisting a vote or leaking key.
- Separate-connection SQLite races: same student/different options yields one
  accepted vote and one conflict; two students both count; two simultaneous
  publications yield one active poll; voting competing with closure either
  commits before closure or is rejected. Further votes after close are rejected.
  This is two-request correctness evidence, not a classroom capacity benchmark.
- Demo command labels, two types/languages, repeat-run preservation of edited
  content and active status, explicit new-set behavior, and missing-target error.
  The command never calls a fake/real model or publishes its drafts.

### Reproduction and manual boundary

Use the file-backed test database command shown under Unit B above, followed
by `node --test tests_js/*.test.cjs`; this runs all current website tests.
Ordinary in-memory test runs explicitly skip real-connection races and must
not be reported as the complete concurrency run.

The updated development server is loopback-only. Agent-run browser/native-camera,
phone layout and live visible-tab interactions for polls were **not** performed;
the prior browser-origin gate was not bypassed. Subsequent user-reported manual poll results are recorded below; unreported scenarios remain unverified. JS tests use fake DOM/timers and do not establish browser
rendering or timing. See [poll manual checks](poll-implementation-plan.md) for
lecturer_alpha/student_alex steps. Existing Unit A/B user reports are preserved
separately and are not repurposed as Unit C evidence.

Full AS-03/AC-03 acceptance remains incomplete until real generation, quality,
browser/phone and intended classroom evidence exists. No AI experiment, billing or network/firewall change occurred during implementation.

### Poll radio-selection follow-up — 2026-11-05

**User-reported defect:** as student_alex on an active poll, clicking an answer
showed no visual selection. The agent did not reproduce a browser click or
observe the original screen, so the report is not assigned a proven sole cause.

Read-only inspection of the actual Django-rendered VoteForm showed four native
radios sharing option_index, unique IDs and correctly linked labels. No student
poll script or automatic submission handler was present. The widget's group
CSS class poll-choices was also propagated to each radio, unintentionally applying
grid/margins to the control. There was no explicit selected-card style. These
are observed markup/style defects, not evidence of a broken label/POST link.

Fix: render a semantic fieldset/legend with four explicit input/label pairs;
separate group, native radio and label classes. Checked state styles the adjacent
label with border/background and a Selected text marker; focus-visible outlines
the option card. Native radio appearance and accent color are explicit, with a
forced-colors fallback. No click handler or automatic POST was added. Guidance
states that choosing is provisional until Submit final response is pressed.

Executed verification: **26 poll tests passed**, 1.140 s, with file-backed SQLite
and no skips, including the existing four concurrency tests. A new regression
parses the real student HTML and verifies unique for/id linkage, four same-name
radio values, no initial selection, no group class on inputs, a separate submit
button, no inline event handlers and no student polling script. GET saves no vote;
POST of a rendered option stores its index and later changes remain rejected.
Django check and diff whitespace check passed. This was a focused poll-suite run,
not a rerun of the entire 73-test prior suite; the new total is not claimed passed.

**Browser limitation:** the previously denied localhost browser origin and Chrome
automation approval were not bypassed or treated as granted. No agent browser,
pointer interaction, computed-style, screenshot, keyboard interaction or phone
check was completed. Parser/server checks establish wiring and persistence, not
actual native selection, focus appearance or visual correctness in the browser.

Additional manual coverage checklist (the limited later user report does not verify every step): hard-refresh an active, unvoted student poll; click
both the radio and the option text. Expect exactly one checked control and one
Selected card; choose another and confirm the marker moves without submitting.
Use Tab, arrow keys and Space to check visible focus/native group behavior.
Before pressing Submit final response, no response should be counted. After
submission the chosen value should count once and cannot be changed.


### User-reported poll manual results — before Unit C commit

The user reported these successful manual checks. They were not performed or
directly observed by the agent; browser/device/viewport details were not supplied.

| Reported check | User-reported result |
|---|---|
| Answer selection after the radio/selection fix | Selection is displayed correctly. |
| Active opinion poll, lecturer versus student visibility | Lecturer sees results before closure; student does not. |
| Opinion poll after closure | Both see the response distribution, without a correct-answer designation or grade. |

This report does not verify keyboard focus/navigation, separate radio versus
label click behavior, phone layout, comprehension-answer disclosure, concurrent
writes, every permission boundary or real AI generation. Server test evidence
for specific assertions remains separate. General visual-design improvements
are deferred to later work. Real AI generation remains disabled and unverified.


### Unit C pre-commit verification

After the selection fix and the user-reported opinion-poll checks were documented,
the complete website suite passed **74 tests**, 39.409 s, on isolated file-backed
SQLite with no skips. All **5 JavaScript logic tests** passed. Django check,
migration drift, dependency consistency and diff whitespace checks passed.
Real AI generation remains disabled/unverified; no AI request was sent. General
visual redesign is deferred. User manual observations and unverified keyboard,
phone and other scenarios remain distinguished above.

## Transcript readability correction — 2026-11-08

User feedback on the existing STATIC task prompted a presentation-only correction. Stored words/order are unchanged. Paragraphs use saved segment boundaries, >=0.8-second gaps, roughly 25-second groups or a 360-character target (individual segments stay intact). The renderer falls back to exact stored text if segment reconstruction differs. A constrained reading width, mobile padding, explicit Hebrew RTL/English LTR and isolated Latin phrases keep mixed text such as New Car in its original order. The teacher-facing explanation is now one sentence in the English UI; GPU/loading/worker details remain in technical documentation.

Executed: **15 focused transcription/display tests passed**, 3.711 s. Existing authorization/expiry/cleanup tests remained green. Actual saved tasks returned owner-authenticated HTTP 200: STATIC now has 13 reading paragraphs; SHORT has 4. HTML text extraction (with paragraph separators) matched every original word and punctuation in order; database text hashes remained unchanged. The existing STATIC New Car phrase is enclosed in a left-to-right bdi element inside RTL text. UTF-8 response decoding was strict and the document declares UTF-8. These are server-response/markup checks, not visual browser/phone verification; the previously denied browser gate was not bypassed.

Encoding/content audit: the saved direct model segment text, the full database transcript and the HTML text all contain the same **four U+FFFD replacement characters** and **one dishwasher**. The segment 57.72–64.60 seconds starts with two replacement characters; others occur in 82.16–86.52 and 86.52–89.48. Dishwasher occurs in 77.56–82.16. The affected segment strings match the full stored text and response text exactly. The worker constructs full text by joining original model segments; JSON file IO uses explicit UTF-8 and strict decoding. No replacement-character decoding is performed by the application. Thus no application transport/render encoding fault was found, and no guessed replacement or word rewrite was applied.

Evidence limitation: the original temporary model-result JSON from these jobs was intentionally deleted. This comparison uses the original model segment strings persisted losslessly in VideoJob, not an independent retained pre-database file. The earlier independent local-experiment raw STATIC result also contains U+FFFD, but it is a different run and contains no dishwasher; it is not evidence that the current sentence was identical across runs. Word/term accuracy (including dishwasher) remains pending comparison with the source audio. No new inference/API request was performed for this correction.

## Focused STATIC quality probe — 2026-11-08

Executed two genuine local CUDA medium transcriptions of the same 00:55–01:35 audio copy: automatic language (detected he), then fixed he, task transcribe unchanged. Roughly 34.7/34.5 s, one shared model load. Outputs differ slightly; both omit the prior dishwasher/U+FFFD artifacts on this cropped context but still contain suspicious words/unclear meaning. Human-reference accuracy/code terminology remain unverified; cropping prevents attributing improvements over the full-video run to the language argument. The existing task text was not replaced. No other local ASR model was found in inspected model/cache locations. A roughly 1.63-GB turbo download is proposed, not performed. Experiment findings and limits: [static-asr-quality.md](static-asr-quality.md). No application code changed in this probe; no website regression run is claimed for it.

## Full STATIC turbo comparison — 2026-11-08

Following explicit download approval, downloaded 1,621,665,983 bytes of public CTranslate2 checkpoint/config/tokenizer files from dropbox-dash/faster-whisper-large-v3-turbo, pinned revision 0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf. Actual full-recording CUDA float16 transcribe succeeded offline with automatic Hebrew detection, using the same ASR arguments as the existing full-medium job. Model load 1.822 s; transcription 54.893 s versus existing medium 190.870 s. Sampled maximum process RSS 1.301 GiB, total GPU-used memory 2,723 MiB; roughly one-second sampling is not an exact peak, GPU value includes other device users. No API/paid inference or application provider change.

Raw full output/model manifest/audio are stored separately under ignored .ai-lab/results/static-turbo; existing website transcript/segments and active medium setting were asserted unchanged. The source-timestamp comparison for 00:55–01:35 is described in [static-turbo-quality.md](static-turbo-quality.md), with the 01:17.560–01:22.160 listening window identified. Turbo is more readable but still has an unclear negation around 00:58–01:02. Human-source accuracy, code-identifier fidelity and the belongs/does-not-belong distinction in that unclear region remain unverified. No WER/quality pass is claimed. The 13 outstanding Gemini files were unchanged. Website regression tests were not rerun because only isolated experiment code/documentation changed in this step.

## Full SHORT-EXPLAIN turbo comparison — 2026-11-08

Actual full-English turbo transcription completed locally on CUDA float16 using the existing verified model, no download/network request. Same arguments as full medium, automatic en detection. Turbo load 1.749 s / transcription 4.824 s versus saved medium 2.837 s / 12.439 s. Sampled maximum process RSS 1.385 GiB and total GPU-used memory 2,715 MiB (sampling and shared-device limitations apply). Both inheritance excerpts retain class/boat/vehicle/inheritance and coherent high-level meaning. Turbo's drop an anchor differs from medium's drop and anchor; this is not verified against human listening. Full outputs are very similar, with no reference-based accuracy/WER claim. Existing website transcript/segments/medium setting and Gemini files remained unchanged. Raw results are ignored local artifacts; comparison findings and reproducibility are in [short-turbo-quality.md](short-turbo-quality.md). No website regression suite was run for this isolated experiment.

## Approved turbo default and normal STATIC upload — 2026-11-08

Executed **113 website tests passed**, file-backed SQLite, 52.562 s, no skips. New checks reject missing/modified checkpoint files, reject another model/revision or unverified result, assert requested/actual identity persistence, exercise unavailable-turbo failure with no fallback/subprocess, and retain loaded identity on later inference failure. Existing privacy/expiry/cleanup/legacy/display tests remain green. The earlier focused set had 37 passed before the final two failure/provenance tests; the full 113-test run includes both additions.

Actual new STATIC upload used the normal authenticated CSRF-enforced multipart POST view/form/upload middleware and real separate background worker, not the standalone experiment or a fake ASR. Upload returned 302 to a queued task. This was an in-process Django client request, not agent-operated browser automation. User manual browser acceptance is pending.

- Course DEMO-CS101, meeting **Test Meeting** (meeting 5), owner lecturer_alpha.
- Job **489f75a2-bca3-4c0a-a9fc-3cc602636ce5**.
- Actual persisted model dropbox-dash/faster-whisper-large-v3-turbo, revision 0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf, sha256_verified=true, CUDA float16.
- Model load **1.574 s**, transcription **54.555 s**, total worker processing **60.549 s**; automatic detected language he. Model-file hashing/decoder/startup/cleanup share the total budget, so total exceeds load + ASR.
- Owner full-transcript page returned **HTTP 200**; parsed reading text matched all stored words/punctuation in order. Actual audio.wav and transcript.pending.json were absent and audio removal was recorded. The page uses the existing paragraph/RTL/Latin-isolation rendering.
- All six pre-existing tasks retained identical transcript hashes, timed segments and asr_metadata. No retranscription or metadata backfill was applied to old jobs. Gemini-file hashes remained unchanged.

Task page: /courses/1/meetings/5/videos/489f75a2-bca3-4c0a-a9fc-3cc602636ce5/ ; full text: append transcript/ . The loopback server and single worker were restarted with current settings; independent maintenance remains running. No new model downloads, API calls, payment, commit or push occurred in this switch stage. Hebrew readability is improved, but meaning/negation, word accuracy and exact technical identifiers remain unverified against a manual source reference (see static-turbo-quality.md); no quality acceptance or summary capability is claimed. The subsequent user-reported browser review is recorded below.

## User-reported STATIC browser review and stage completion — 2026-11-08

**Provenance: reported by the user, not an agent-executed browser test.** The user opened the full STATIC transcript on the website. The explanation of variables belonging to an object versus a shared static variable was understandable. Some words remained garbled, and part of a sentence containing a negation remained unclear even when listening to the recording. No word-by-word accuracy measurement was performed.

This supports usability/understandability of that reviewed result, not verbatim fidelity, exact code-identifier accuracy, a quantified accuracy score or a phone/layout acceptance pass. The user approved completing the local transcription stage with large-v3-turbo as the new-upload default. Summary generation remains a separate, disabled stage. Existing transcripts remain unchanged.

The reading page now uses the heading **Automatic transcript** and the warning **Some words and code terms may be transcribed incorrectly.** It retains the short speech-only explanation. Server template assertions cover the heading, warning and speech-only notice; raw transcript outputs remain local/ignored and are not published in the quality reports.

Final pre-commit verification for this completed stage: **113 server tests passed** in 49.785 s using file-backed SQLite; **10 JavaScript tests passed** in the fake-DOM harness. Migration drift check reported no changes; dependency check reported no broken requirements. These checks include the final Automatic transcript heading and warning. Documentation links and the explicit publication file list were checked; raw transcript tables were removed from published quality reports while the original local artifacts remain unchanged.

## Local summary feasibility on saved turbo transcripts — 2026-11-08

Executed two real local Qwen3 8B (Q4_K_M, Ollama 0.40.14) CLI generations from saved full STATIC/SHORT turbo transcripts; no retranscription/download/external-provider request. Thinking off, JSON paragraph + 3–5 points, source-only/negation/inheritance/omit-unclear instructions, one call each/no retries. Both format checks passed: STATIC 4 points, SHORT 3. Wall times 10.098 s and 2.863 s; first model load 4.919 s versus 0.004 s warm reuse. Output-generation durations 4.182/2.510 s. Context/CUDA use confirmed in local logs; no new peak-memory measurement is claimed.

Claim-by-claim review against ASR input found the per-object versus shared-static distinction and boat-inherits-vehicle direction preserved. STATIC nevertheless overstates coverage of static functions and adds class-ownership/only-once inferences beyond explicit wording. SHORT claims were supported by its transcript. This is not recording-reference accuracy verification. Raw outputs and inputs remain ignored/local; full review and a proposed controlled draft integration are in [local-summary-feasibility.md](local-summary-feasibility.md). Website summarization remains disabled; no feature implementation or website regression run occurred. Gemini experiment files remain separate/unchanged. No commit/push.

## Initial automatic local summaries — 2026-11-08

Implemented the approved initial local Qwen3 8B stage (D-42/D-43). **126 server tests passed** in 52.922 s on file-backed SQLite, no skips; **12 JavaScript tests passed**. Migration 0006 applied; schema drift check passed. Tests use injected engines, except an ordinary-Python owned-process-tree test; real-model evidence is separate below.

Automated coverage includes transcript persistence before summary invocation, WAV removal before summary, shared original deadline, summary failure/timeout/interruption preserving transcript access, invalid output and wrong-language/script rejection, safe unexpected-error messages, legacy task preservation, actual model metadata, owner-only escaped summary HTML and direct URLs/status, current membership/revocation, exact expiry and cleanup of both text products, private IPC removal, and Windows owned-grandchild termination on process-tree close. JavaScript covers one reload for ready server-rendered summary, terminal polling stop and a retained transcript link on failure. An initial reload test exposed a double reload and passed after a one-shot guard. No real GPU hard-crash or browser/phone run is claimed.

Real saved-input prompt checks used unchanged full turbo transcripts and the installed model through the production adapter. Initial lecture-grounding-v2 still falsely attributed static-function instruction and reconstructed an uncertain identifier. A bounded v3 refinement generated valid paragraph/point structures in Hebrew/English: STATIC 10.382 s wall, 7.607 s model request; SHORT 8.719 s wall, 5.943 s model request. These cold per-job services include loading, unlike the earlier warm CLI experiment. In v3, STATIC did NOT claim static functions were explained; SHORT retained boat inheriting from vehicle. STATIC still inferred class ownership/access through the class, and not all points were example-scoped. No semantic accuracy pass is claimed despite the prompt. Raw outputs/prompts remain ignored local artifacts and are displayed to the user without editing.

Real full-route uploads (in-process authenticated CSRF multipart request, actual separate worker):

| Clip / job | Observed result |
|---|---|
| STATIC / 03b0bfec-f199-4aa1-9dfc-0e26eb2225f9 | ASR 57.276 s; model-summary request 7.745 s; total 77.416 s. Unexpected Korean word in summary prompted a new language validation rule. The initially accepted invalid output was snapshotted locally then explicitly invalidated on this new development acceptance task; task now shows summary_language failure, with the completed transcript retained. No silent correction/retranslation occurred. |
| SHORT / dd68e11b-2d34-40ae-9fb5-9bca05e14c7b | ASR 4.835 s; model-summary request 5.972 s; total 21.985 s. Summary completed; generated English output matches the v3 saved-input check and preserves inheritance direction. |

An additional SHORT upload was necessary after the STATIC failure to verify the successful full path. Both belong to lecturer_alpha, DEMO-CS101 / Test Meeting. Owner task/full-transcript requests returned HTTP 200; successful summary paragraph/points were present as escaped text, and rejected STATIC summary was absent with a clear reason. Actual WAV and transcript/summary pending/input files were absent. No per-job Ollama/model process remained afterward. Seven old task transcripts/segments/asr_metadata were verified unchanged; all Gemini file hashes stayed unchanged. The existing summary fixture language tests and direct-page privacy tests are not replaced by this owner-only real sample check.

The original ten-minute worker-start limit covers all phases; queue wait stays separate. Summaries expire no later than their source transcript (max seven days), with direct access hiding content at expiry and maintenance clearing it. This does not guarantee physical deletion when the machine/maintenance is stopped. User browser review and recording-grounded word/summary fidelity remain open. Full behavior/setup/limitations: [local-summaries.md](local-summaries.md).

One intermediate test invocation encountered a Windows lock because a preceding test run still owned its SQLite test file. After the previous run completed, the final suite used a separate file and passed; no production database was deleted. No new dependencies/models, external-provider inference, billing, commit or push occurred in this stage.

## User-reported SHORT summary interface review — 2026-11-08

**Provenance: a manual interface check reported by the user, not agent-executed browser automation.** Signed in as lecturer_alpha, the user reviewed SHORT task dd68e11b-2d34-40ae-9fb5-9bca05e14c7b. The summary paragraph and key points were readable, and the link opened the full transcript of the same video. This verifies the reported display/navigation path only; it does not establish phone layout, other users' permissions, source-audio accuracy, or a quantified summary-quality score.

STATIC evidence remains distinct: the saved-transcript v3 summary check succeeded structurally and did not attribute static-function coverage, with grounding limitations recorded above. The normal MP4-upload run produced an invalid-language summary and was marked summary_language failure; its full transcript remained accessible. The SHORT interface report does not convert that STATIC upload into a successful summary run.

Language regression coverage explicitly accepts a Hebrew paragraph and points containing English code terms **static** and **Car**, with exact generated strings retained. The unexpected-script rejection check remains separate, so rejecting the Korean-script case does not require rejecting ordinary Hebrew/English technical mixtures.

Final pre-commit verification after the user report and mixed-language regression addition: **127 server tests passed** in 53.362 s using file-backed SQLite, no skips; **12 JavaScript tests passed**. The new acceptance test covers a Hebrew summary paragraph and points with static and Car without rewriting, alongside rejection of unexpected script. Schema drift/system/dependency checks passed. Publication review covered only stage code/tests/documentation; Gemini files and ignored raw/media/model/database/secret artifacts were excluded.

## Clarified comments timing (D-17) — 2026-11-11

The user reported the resolved assignment interpretation: online means during class and offline means outside class. Both use normal connected website submission to an associated meeting. Local persistence, a send queue and disconnected synchronization are not required. This clarification applies to comments/suggestions only; attendance interpretation remains separate.

Code inspection found no meeting-time, attendance-window or simultaneous-lecturer-login gate in the existing request submission/history paths. Runtime submission/storage/authorization logic was unchanged. The student-facing notice now reads: You can send comments and suggestions during or outside class.

**Executed automated server checks: 25 participation tests passed in 31.285 s**, file-backed SQLite, no skips; system check reported no issues. The added regression exercises both comment and suggestion through the normal form/view/middleware path with CSRF enforcement:

- Set the meeting date seven days before submission; no attendance window exists.
- Submit each type using a fresh submission ID and a valid CSRF token. Verify the redirect and persisted meeting ID, student ID, kind, exact text and submission timestamp.
- Log the student out, use a fresh authenticated client, and verify both requests in personal history. Verify neither appears under a different meeting.
- Create a fresh Lecturer client with the clock advanced two days, and verify stored requests on the meeting page and lecturer feed. This is a mocked later timestamp, not a real two-day wait.
- Use another student account in the same course: neither private request is present in its page, and the lecturer feed returns HTTP 403.

This is automated request/database/rendering evidence, not a manual browser/phone or classroom-capacity test. Existing participation tests also cover identity/role revalidation, failed-save reporting, escaping, duplicate submission and input boundaries. README, SoW, SRS and the decision register now consistently record the resolved comments timing; the former unresolved-offline statements in older dated test records describe historical decisions and are superseded by this entry. No disconnected feature, database migration, AI request, commit or push was introduced.
