# Verification Record — Units A, B, C and D

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
