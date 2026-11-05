# Gemini Free-Tier Feasibility — 2026-11-05

## Status

**Partial experiment: connectivity succeeded; task-output quality was not
evaluated.** The subsequent request-code review below made no Gemini API calls.

The user configured the local key and confirmed Free with no linked billing
account. Authenticated model listing returned 60 models. Three generation
requests were attempted: one successful trivial smoke, one failed task request
and one failed smoke on a bounded free alternative. No substantive task result
was obtained. No payment, account, site, scope, commit or push changes occurred.
Project tier is user-confirmed; metadata listing is not billing verification.

## Public documentation findings

The pricing page lists free Standard input/output for Gemini 3.8 Flash and
other Flash variants, including 3.1 Flash-Lite. Gemini 4 Argon is not free.
3.8 Flash supports text/audio input and text output, making it a candidate
for this bounded experiment, not a selected product dependency.

Quotas are project/model-specific RPM, input TPM and RPD. AI Studio displays
the active values; public documentation does not establish this account's
numbers. Daily quota resets at Pacific midnight. Exceeding a limit can return
429. Paid-tier selection is outside authorization; free limits will not be
worked around by payment or additional keys.

Audio-to-text is supported by the documented multimodal API; actual free
audio capacity still depends on model access and quota in this project.
Documentation recommends Files API for payloads exceeding 20MB. The two
existing extracted mono WAVs are below that size, though full request size
and encoding overhead must also be checked before choosing inline input.

Unpaid-service terms allow use of submitted content and outputs to improve
Google products and permit human review. Sensitive/confidential/personal
information should not be submitted. Regional exceptions exist; do not infer
this account's regional status from the machine's time zone. This experiment
uses synthetic homework and permitted sample media, not real student data.

The user explicitly confirmed permission for both speech clips and their
transcripts under these conditions. This resolves the transfer-permission
question for those inputs only; no song transfer or general real-data use
is authorized. That confirmation is not proof of transcription correctness.

## Evidence and next required input

The preflight, secure-input helper, one-request client and bounded runner are
in `experiments/gemini_free/`. The client reads the local secret file directly,
authenticates through an HTTPS header, and never logs request headers. It
redacts the actual key before saving server payloads. A scan found no actual
key in Git-visible files. Raw results are under ignored `.ai-lab/gemini/`;
sanitized evidence is in `experiments/gemini_free/results/attempt-summary.json`.

## Actual attempts

| Model | Case | Wall time | Result |
|---|---|---|---|
| gemini-3.8-flash | Single-word READY smoke | 70.62 s | Exact READY; finish STOP |
| gemini-3.8-flash | Hebrew comprehension poll, exact local prompt/schema | 180.12 s | No usable response; connection/response failure at timeout boundary |
| gemini-3.5-flash-lite | Single-word READY smoke | 7.34 s | 503 UNAVAILABLE; server reported high demand |

The first response reported modelVersion gemini-3.8-flash, 44 input tokens,
one output token and Standard service tier. Settings: temperature 0,
maxOutputTokens 4096, thinkingLevel LOW. The poll additionally requested JSON
with the same schema and source material as the local experiment. Exact
prompts, input hashes and settings are retained privately.

The original generic handler did not retain the first failure's exception
type. Its duration matches the configured 180-second timeout; no HTTP status
or quota error was received. It does not prove a model-quality error or quota
exhaustion. The handler now records exception class without exception text.
Remote wall time combines network, queue and inference; the available response
cannot separate those phases.

The original sequence stopped on its first failed task. One separately
announced recovery used 3.5 Flash-Lite, which is listed in the account and
documented as free for Standard text/audio input/output. Its smoke failed,
so no task requests used that model. No automatic retries, key rotation,
paid model or billing changes occurred. No 429 was observed; numeric active
RPM/TPM/RPD and actual free audio quota remain unknown.

Beyond smoke instructions, only the synthetic learning text for the failed
poll was submitted. Homework, speech transcripts and audio were not sent.
The remaining three polls, all reviews/comparisons, both summaries and both
transcriptions were not executed. The rollback regression was not tested
on Gemini. These gaps are not recorded as passes.

For source-check preparation only, local video frames confirmed displayed
identifiers Vehicle/make/model/year and Car/minimumCarPrice. This is limited
visual evidence, not a check of spoken words or a reference transcript. Frames
remain private and were not uploaded. Existing PyAV encoded PNGs after an
initial helper found Pillow unavailable; no package was installed. No visual
AI capability was added to the approved audio-only product scope.

## Comparison and recommendation

| Area | Local evidence | Gemini evidence |
|---|---|---|
| Polls | Warm 8B model totals 2.26–2.63 s; Hebrew phrasing/opinion semantics failures | First poll failed at 180.12 s; no quality result |
| Homework | 8B totals 6.70–8.84 s; false missing-rollback and peer-attribution errors | Not run |
| Speech summaries | English/Hebrew model totals 6.27/6.56 s; Hebrew wording problems | Not run |
| Speech transcription | GPU: 10.97 s English / 171.00 s Hebrew with terms; terminology degraded | Not run; free audio quota not established |

Local model totals and remote wall times are not equivalent compute metrics;
READY is also much simpler than a poll. This small cloud run demonstrates
some connectivity but insufficient task availability. It does not establish
Gemini's quality or prove it generally unreliable. Do not select a final backend
or claim cloud superiority from these results. A later bounded attempt after
reviewing local diagnostics may obtain missing evidence under the same free-only rules.
No payment or repeated model switching is recommended to bypass these failures.
An honest experiment-record commit is suitable after review and only on request.

The comparison is **local task results available; Gemini task results
unavailable**. Nothing has been staged, committed, pushed or implemented for
the site.

## Offline request-code review

The user requested review before any further attempt. Only local code, saved
results and public official documentation were inspected. No model-list,
generation, upload or other authenticated API request was sent in this review.
No experiment code or website implementation was changed.

| Item | Finding | Assessment / proposed correction before a future approved attempt |
|---|---|---|
| Model identifiers | `gemini-3.8-flash` and `gemini-3.5-flash-lite` match official stable IDs and the saved account inventory. The `v1beta/models/{model}:generateContent` route is documented. | No identifier/route mismatch found. Metadata visibility is not quota proof. |
| Thinking | REST `thinkingConfig.thinkingLevel=LOW` is documented and supported by both models. | It requests low reasoning, not disabled reasoning. Minimal is not supported by 3.8; 3.5 Flash-Lite does support it. Do not confuse this with the local experiment's disabled thinking. |
| Temperature | Code sends `temperature=0` to both models. Official REST docs state this field is ignored on 3.6 Flash and newer. | For 3.8 this setting does not establish deterministic output. This is a local configuration/interpretation issue, not an established cause of the failed poll. |
| Output ceiling | All requests use 4096 output tokens, below the models' documented 65536 maximum. This includes the one-word smoke and potentially long transcriptions. | Legal but not task-specific. A ceiling does not require producing that many tokens: the successful smoke produced one. Propose separate smoke/poll/review/transcription budgets and explicit truncation checks; no measured causal link to the failure exists. |
| Timeout | `urllib.request.urlopen(..., timeout=180)` bounds blocking socket operations, not a measured split of connect, first-byte and response-read phases or a guaranteed total deadline. | Separate those phases and add a bounded total deadline in a future code change; do not simply increase the timeout. The current measurements cannot locate the delay. |
| Diagnostics | The original catch-all omitted the poll exception class and network reason. The later handler records only the class for non-HTTP failures. | A confirmed local observability defect prevents root-cause attribution. Record sanitized error category/errno/phase and safe correlation metadata; never credentials, authorization headers or unredacted bodies. |
| Proxy | Read-only `urllib.request.getproxies()` currently returned no proxy schemes, and checked proxy environment variables were absent. | This is a current observation, not proof of past routing or network health. No connectivity probe was made. |
| Retries | No retry loop exists. The runner spaces cases by 15 seconds and stops on the first failure. One alternative model was tried as a separately announced recovery. | No automatic retry defect found. The spacing is not verified quota compliance. Rerunning scripts manually can resend/overwrite cases; propose immutable run IDs, completed-case guards and an explicit bounded retry policy before reuse. |
| Free-only boundary | There is no billing/upgrade API in these scripts. Model allowlisting is explicit; project tier was confirmed by the user. | Code cannot independently prove that the project's billing state remains Free; a free-listed model alone is not a cost guarantee. |

The 180.12-second failure must remain attributed to an **unknown request-path
failure**, consistent with the configured timeout boundary. Possible local
network/transport and remote causes were not isolated. Only the separate 503
response explicitly reported provider high demand; it does not establish the
cause of the earlier poll failure. No task-quality verdict is justified.

These are review findings and proposed corrections, not implemented fixes or
new experiments. The experiment remains partial and paused at the user's
request; payment remains outside its authorized scope.

### References for this review

- [Python urlopen timeout/proxy behavior](https://docs.python.org/3.12/library/urllib.request.html)
- [Gemini REST request configuration, thinking and temperature](https://ai.google.dev/api/generate-content)
- [Thinking levels by model](https://ai.google.dev/gemini-api/docs/thinking)
- [Gemini 3.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite)

## Official sources reviewed for the experiment

- [Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Audio understanding](https://ai.google.dev/gemini-api/docs/audio)
- [Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash)
- [Additional terms](https://ai.google.dev/gemini-api/terms)
- [API keys](https://ai.google.dev/gemini-api/docs/api-key)
- [Model metadata API](https://ai.google.dev/api/models)
- [Billing tiers](https://ai.google.dev/gemini-api/docs/billing)
