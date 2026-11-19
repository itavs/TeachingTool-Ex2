# Selected-group real-model acceptance fixture

Synthetic material only. This folder preserves the two-work check from
19 November 2026; it is not an additional generation run. See the
[assessment and timings](../../docs/homework-group-acceptance.md).

- `inputs.json`: complete assignment instructions, four criteria, professional
  rubric, English language and both synthetic source texts.
- `expected.json`: coverage map fixed before inference; **never send it to the
  model**. It is an independent assessment oracle, not a prompt or provider input.
- `alex-original.json`, `casey-original.json`: unedited generated individual
  findings/comparisons, exact-source quote audits and processing times. These are
  curated synthetic experiment artifacts, not exports of website submission or
  account records. Local database IDs, secrets, runtime paths and edited/published
  draft records are excluded. Full private capture hashes are in the report.

## Reproducing the procedure

Use the normal installation/setup in the [project README](../../README.md),
including migration 0011 and prepared demo accounts. Real inference additionally
requires the pinned local Qwen assets/runtime described in
[local review setup](../../docs/local-homework-review.md); they are not included
in Git. No missing local experiment file is needed for the inputs or expected
results. No automatic download, external provider or fake website output is used.

1. As a Lecturer, create a fresh assignment in a demo meeting. Copy title,
   instructions, each criterion, professional rubric and language from
   `inputs.json` to their corresponding assignment fields.
2. As each listed demo Student, submit the corresponding `text` as Version 1.
   Do not include `expected.json` in either submission or the rubric.
3. As the Lecturer, choose **Review demonstration group**, select the two owners,
   preview the latest versions and confirm. Record the new IDs; the report's
   original local IDs are not required.
4. In the configured environment, run the existing worker twice sequentially:

   ```powershell
   .\.venv\Scripts\python.exe manage.py run_homework_worker --once
   .\.venv\Scripts\python.exe manage.py run_homework_worker --once
   ```

5. Before editing, preserve each review page's **Original generated findings and
   private comparison sources**. Check both jobs' recorded sources/context and
   private state. Assess findings against `expected.json` outside the model.
   Check quote exactness and whether each quote actually supports its conclusion.
6. Record original and edited content separately. Correct false content and
   unverified evidence, save, then explicitly publish only the chosen feedback.
   Check its matching Student/version and verify the other draft stays private.

This procedure intentionally requests real local inference when manually run;
do not run it as a software test. Outputs/timings can vary. The recorded outcome
is successful processing but failed comparison quality, followed by a user-
reported Lecturer correction and separate publication of Alex only. Repeating
these steps does not imply that the model will produce the same wording.
