# Verification Record — Unit A

Date: 2026-11-05. Environment: Windows 64-bit, Python 3.12.14, Django 5.2.19,
SQLite. This record covers the shared website foundation only. It does not
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

- Actual classroom user count, parallel writes and SQLite capacity.
- Hosting/HTTPS/phone access; current server listens only on loopback.
- Production hardening, login throttling, retention/deletion and real identities.
- Attendance, XLSX, comments/history/live updates, polls, video summaries and
  homework feedback as integrated website features.
- Offline interpretation and university-network checks.
- AI providers/adapters and AI correctness. Existing feasibility reports remain
  separate evidence; no new AI request occurred during this unit.

The foundation is a meaningful commit unit, with user-reported manual checks
and remaining UI limitations explicitly separated from server test evidence.
