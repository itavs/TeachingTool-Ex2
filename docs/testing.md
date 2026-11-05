# Verification Record — Units A and B

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
