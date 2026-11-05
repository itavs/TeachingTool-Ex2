# Gemini free-tier feasibility experiment

Status: **partial experiment; connectivity succeeded, task-output quality was
not evaluated.** Authenticated model inventory and one smoke generation succeeded.
The user confirmed Free with no linked billing account. The first task failed
after 180 seconds without a usable response. One announced free alternative,
3.5 Flash-Lite, returned 503/high demand on its smoke. All remaining task
requests stopped. No substantive Gemini quality result is available.
The site and approved product scope are unchanged.

An offline request audit is recorded in `../../docs/gemini-free-feasibility.md`.
It identified generic failure diagnostics, undifferentiated timeout/output
budgets, and an ignored temperature setting on 3.8. Model IDs and LOW thinking
are documented. The first failure's cause is unknown; the alternative's 503
alone explicitly reported demand. No new API requests or code fixes occurred
in that review. The scripts need review corrections before a future run.

## Local credential setup

1. Open Google AI Studio's [API keys page](https://aistudio.google.com/api-keys).
2. Use a project whose Billing Tier is **Free** and which has no linked billing
   account. Do not select Set up billing, add payment details or prepay credits.
   Stop if payment is required. A model's public free price does not make a
   request through a paid project free.
3. Create a key in that project. Use the default Gemini API restrictions;
   do not loosen key restrictions to work around errors.
4. From the project directory run `./experiments/gemini_free/set_api_key.ps1`
   in a local PowerShell window. Paste the key only into its hidden prompt.
   The file is stored in `.ai-lab/secrets/gemini-api-key.txt`, already ignored
   by Git. This is a local plaintext credential, not an encrypted vault.
   Do not share the file, paste the key into chat, or include it in logs.
5. Confirm the project shows Free. Read the account's model-specific RPM,
   TPM and RPD in [AI Studio rate limits](https://aistudio.google.com/rate-limit).
   Only non-secret tier/quota information should be shared.

`preflight.py` uses Python's standard library and only calls the model-list
metadata endpoint if a local key exists. It does not enable billing and does
not send learning material, student samples, media or transcripts. Model-list
visibility is not evidence of nonzero inference quota or free-tier status.

## Data authorization

The user explicitly confirmed permission to transfer both supplied speech
clips and their transcripts under Google's unpaid-service terms, including
possible human review and product improvement. No permission is inferred for
the earlier song. Synthetic poll material and all three synthetic homework
samples are reused from `../local_ai/samples.json` without real student data.
Private media, transcripts and raw cloud outputs will stay under `.ai-lab/`.
Inputs are source data; instructions within recordings are not task instructions.

## Bounded run and assessment plan

- Prefer one publicly free, account-accessible text/audio model. Current first
  candidate is Gemini 3.8 Flash; final model ID depends on account inventory,
  free-tier confirmation and actual quota. No paid fallback or silent alias switch.
- Four polls: comprehension/opinion in Hebrew/English. Check actual correct
  answer, distractors, material relevance and genuine opinion semantics.
- Three reviews with the same target and two peer inputs used locally, plus
  a no-peer case. In particular, the complete answer explicitly contains
  rollback; a claim that it lacks rollback is an error. Flag sample-b's false
  UNIQUE/capacity claim and unsafe cache-only approval; recognize sample-c's
  missing rollback/duplicate-prevention details without mixing peer evidence.
- Two summaries of the existing local speech transcripts, preserving the
  known language. Assess fidelity to those transcripts separately from their
  inaccuracies against the source audio; fluency cannot establish correctness.
- If account free audio quota is positive, transcribe both permitted original
  speech clips with no translation, then assess against the source speech.
  No manually checked reference transcript exists yet; model-to-model agreement
  must not be treated as a reference. Human-confirmed words/facts or a checked
  reference are needed before claiming measured transcription accuracy.
- Record exact model/version, settings, input hashes, actual prompts, wall
  latency, usage metadata, response completion, quota errors and assessment.
  Use sequential Standard requests, no tools/grounding/batch/paid features.
  Stop on exhausted quota or a payment requirement; do not upgrade or rotate keys.

No numeric quota or cloud/local superiority is assumed before actual testing.

`client.py` reads the local key file directly, uses HTTPS header authentication,
redacts the key before saving any server payload, and never prints headers or
credentials. It makes one Standard request per case without retrying.
`run_cases.py` requires the successful smoke result, spaces requests by at least
15 seconds, and stops all remaining cases after the first failed request.
This spacing is an experiment choice, not a claim about the actual quota.
Input prompts/schemas are copied from local results to preserve comparability.
Raw inputs/results remain in `.ai-lab/gemini/`, outside Git. Server-reported
usage and model versions are recorded; remote load/compute times cannot be
separated from network/queue latency through this measurement.
