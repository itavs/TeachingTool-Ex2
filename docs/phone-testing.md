# Private-Network Phone Test — Limited User-Reported Results and Remaining Plan

The original Unit B plan below preceded phone execution. A later temporary
server was bound to the verified home Wi-Fi address `10.0.0.17:8000`, with that
exact host allowed only in the server process. The original loopback server and
tracked settings were preserved. The agent did not create a firewall rule; a
narrow Private-profile/local-subnet/port-8000 rule was supplied for the user if
needed. Its execution by the user has not been reported. LAN IPs can change;
recheck before a future test. No public exposure or router forwarding is approved.

## User-reported real-device checks

The user reported Safari on an iPhone over the home network:

- Login succeeded.
- QR scanning registered attendance, which appeared to the Lecturer.
- In another user-reported sequence, a QR scan led to login; an expired-code
  message appeared; a new QR scan subsequently registered attendance.
- A comment was submitted and appeared to the Lecturer.
- A poll vote was submitted; results were viewed on the phone after closure.
- In the subsequently reported comprehension-poll check, the correct answer,
  explanation and results were hidden before closure. After closure and a page
  reload, all three appeared correctly in Safari on the iPhone.

The manual phone round has ended for now at the user's request. These are
user-reported paths only, not agent-observed device execution. iPhone model,
iOS/Safari versions, layout/orientation checks and timings were not supplied.
Only the stated post-close reload behavior is confirmed. Do not infer checks of
other screens, unreported disclosure/expiry variants, duplicate submission, XLSX,
video processing/transcripts/summaries or homework review/publication on iPhone.
Server authorization and concurrency checks remain separate evidence; see
[the coverage review](testing.md#phone-evidence-and-focused-demo-test-gaps).

## Preparation for a separately approved LAN test

1. Use a trusted private Wi-Fi network with both the computer and phone on it.
   Use demo accounts only. Do not expose this DEBUG development server publicly.
2. Read the computer's Wi-Fi IPv4 address, for example with `ipconfig`; do not
   assume an address. Guest/client-isolated Wi-Fi may prevent device access.
3. After authorizing the temporary network exposure, add that exact IPv4 address
   to `ALLOWED_HOSTS` in the development settings, preserving loopback entries.
   Do not use `*`. This edit has **not** been made by the agent.
4. Stop the existing loopback development server, then start it on that specific
   address: `.\.venv\Scripts\python.exe manage.py runserver <private-ip>:8000`.
   Replace the placeholder; do not bind all interfaces. This command is not
   currently running. No dependency, public tunnel or port forwarding is needed.
5. Open `http://<private-ip>:8000/` on both computer and phone. Use the LAN URL
   for the lecturer page too: QR URLs inherit its host. A lecturer page opened
   on 127.0.0.1 would generate links that target the phone's own loopback.
6. If Windows asks about network access, or connection is blocked, stop and
   review a narrowly scoped Private-network firewall rule separately before
   changing anything. Do not disable the firewall or allow Public networks.
   Plain HTTP is only for this controlled demo test, not real credentials/data.
7. When finished, stop the LAN server, restore loopback-only ALLOWED_HOSTS and
   binding, and remove any separately authorized temporary firewall rule.

## Two-account attendance test

- Computer: sign in as lecturer_alpha, open a DEMO-CS101 meeting and its
  Attendance page. Phone: use student_alex; credentials are in the ignored
  local demo credential file, never a committed document.
- Open the first window: expect 300 seconds and a new QR every 30 seconds.
  Scan using the phone's native camera. While signed out, expect login then
  return to the same attendance path and a POST-backed save. Without JavaScript,
  press Register attendance. Check the student confirmation and lecturer row.
- Repeat the scan: one record, unchanged first time/status. With a separate
  private-browser session as student_casey, register a second student; verify
  two separate records. Two tabs may exercise repeated clicks, but this is
  separate from the automated simultaneous-connection tests.
- For expiry during login, scan a freshly rotated QR while logged out, wait
  over 45 seconds before completing login, and expect Scan the current QR
  again with no new record. Scan a current code to continue. A freshly created
  meeting makes this check easier without existing attendance.
- Close the window and try its saved URL: reject it. Open again: expect 120
  seconds. A first registration by the second student now reads Registered in
  an additional window; an already registered student keeps the original data.
- Export XLSX; compare rows/status/time with the online roster at export time.
  Add a later registration and confirm the old file stays unchanged. Editing
  the file does not change the site. There is no manual correction UI.
- In student role, try a copied lecturer roster/export/open/close URL; expect
  refusal. Try a different course's meeting URL as student_alex: generic 404.
  Automated server tests cover direct POST/CSRF and cannot be replaced by
  checking button visibility alone.

## Comments, live updates and mobile layout

- Keep lecturer and student Comments and suggestions pages open for the same
  meeting. Send both types in Hebrew/English, including multiline text; refresh
  the student page and check persistence. Submit 1 and 1000 characters; blank
  or over-1000 text should be rejected after trimming.
- The lecturer sees new stored requests on the next visible-page read, normally
  within about 5 seconds plus request time. Students see only their own history.
  Hidden lecturer tabs pause polling and refresh when visible again. Simulate
  loss of connectivity: no successful-save claim or background send queue.
- Check 375-pixel portrait and landscape layouts, readable QR, native scanning,
  keyboard/form labels, focus, text wrapping, horizontal roster scrolling and
  button reachability. Record actual phone, browser, network and failures.

The during/outside-class interpretation was already resolved by D-17; these
connected tests make no claim of disconnected operation. No
university-network-origin check is implemented or required to continue. QR
does not conclusively prove physical presence or prevent real-time forwarding.
