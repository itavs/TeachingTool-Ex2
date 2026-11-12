# Local AI feasibility experiment

This is an isolated experiment, not website implementation or a final technology
selection. All text fixtures are synthetic. Inference is local only. No paid
or external inference service is used.

## Files and isolation

- `bootstrap.ps1`: create `.ai-lab/venv`, install dependencies from PyPI,
  download the portable official Ollama archive, verify its published SHA256.
  It accepts `-PythonExecutable` for an installed Python interpreter; the
  default is `python`, avoiding a machine-specific user-profile path.
- `start_ollama.ps1`: start a hidden process bound to `127.0.0.1:11435`, cloud
  disabled, model files under `.ai-lab/models`. Variables are process-local.
- `download_asr.py`: fetch the official SYSTRAN model and record its revision.
- `samples.json`: synthetic learning material, criteria, three theoretical
  submissions, and expectations used for manual assessment.
- `run_experiment.py`: run `text`, or `asr --manifest PATH [--device cpu]`.
  `AI_LAB_MODEL` selects a locally downloaded Ollama model; `AI_LAB_RUN`
  names the text-results directory. `AI_LAB_AUDIO_RUN` isolates follow-up audio
  outputs under `.ai-lab/results/` without overwriting earlier cases.
  Inference HTTP has a fixed loopback URL.
- `extract_audio.py INPUT OUTPUT`: extract mono 16-kHz WAV with PyAV.
- `requirements-lock.txt`: observed full environment after the PyAV correction.
- `results/`: actual synthetic-input outputs, prompts, configurations, and
  sampled resource measurements. The first 4B run predates named subdirectories
  and its cases are directly in this directory.

Publication review removed local filesystem instructions from the two
`environment.json` model metadata records (the `modelfile` field). Model
identities, parameters, observed timing and generated synthetic examples are
unchanged. Raw originals remain private under ignored `.ai-lab/`.

`.ai-lab/` is Git-ignored: environments, binaries, downloaded models, source
media, extracted audio, transcripts and summaries of user-provided media.
An audio manifest is a JSON list with `name`, `path`, `permission`, and
`language` (`he`, `en`, or null for automatic detection). An optional
`reference` is human-authored ground truth. Never fabricate audio or replace
an ASR test with a prepared transcript. No reference was supplied for the
user's video, so transcript accuracy has not been scored.

Stop the experiment server after use by verifying the process whose PID is
stored in `.ai-lab/ollama.pid` belongs to this runtime, then stopping it.
Restarting the script should be done only when port 11435 is unused.

## Measurement interpretation

Ollama reports load, prompt evaluation and generation durations separately,
in nanoseconds; recorded values are converted to seconds. Wall time includes
HTTP and monitoring overhead. Fresh load here means unloading model memory;
OS disk and driver caches were not cleared. The first run can include runtime
initialization and is not a reproducible cold-boot benchmark.

RAM is summed sampled process RSS, not a peak private-allocation measurement.
The initial 4B run omitted the `llama-server` worker from RAM accounting and
its RAM values must not be used as total model RAM. This was corrected for
8B. GPU memory is total device usage including Windows, sampled about once
per second. API `size_vram` and runtime logs additionally establish GPU use.

Schema-valid JSON establishes structure only. Manual review found semantic,
language and cross-submission attribution failures in both tested models.
No application permissions, publication lifecycle, classroom concurrency,
offline behavior, or production acceptance were tested here.

## Focused homework probes - reproduction

The Qwen3 8B round is closed with **failed readiness**: per-criterion English
assessment handles Alex's two synthetic stacks/queues versions, but the controlled
B cache edit still changes unrelated judgments and leaves false UNIQUE conclusions.
26/26 quote matches do not certify entailment. No homework provider is enabled.

Source fixtures: `samples.json` contains original theoretical A/B/C and criteria;
`homework_fixtures/criterion-inputs.json` contains Alex v1/v2 and B before/after.
The three independent coverage/expectation maps are in `homework_fixtures/` and
must stay out of model input. These are synthetic, not exported real coursework.
Recorded source inputs, exact prompts, model outputs, configuration and timings
are under `results/homework-focused/{comparison,personal,criterion}`. Only token
context arrays were removed from those responses; the generated text is unchanged.

Offline audit (no model, website database or API required), from repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest experiments.local_ai.test_personal_review_probe -v
```

For new inference, prerequisites are the previously installed pinned local
Ollama 0.40.14 portable binary/model store described above and the website Python
environment (standard-library probe/helper imports, no database access). These
large runtime/model assets are intentionally not in Git; missing assets fail,
not download or substitute a provider. No secret/API key is needed. All source
fixtures/maps required by the probes are in Git; none reads `.local` expectation
files or the demo database. Start the local-only service in PowerShell:

```powershell
.\experiments\local_ai\start_ollama.ps1
Invoke-RestMethod http://127.0.0.1:11435/api/version
```

Wait for that local readiness response before running a probe. Then choose one
command, each generating separate local results without retries:

```powershell
.\.venv\Scripts\python.exe experiments/local_ai/homework_review_probe.py
.\.venv\Scripts\python.exe experiments/local_ai/personal_review_probe.py
.\.venv\Scripts\python.exe experiments/local_ai/criterion_review_probe.py
```

The first two probes create new timestamped folders and use their corresponding
published maps for source consistency only; the criterion probe copies published
inputs into a new timestamped folder by default and does not read expectations.
`--run` is optional for an explicitly prepared input folder, never required for
normal reproduction. Outputs remain ignored/local. Stop only the verified service
started by start_ollama.ps1 afterward, as described above. No new inference was
run while preparing this reproducible experiment commit.
