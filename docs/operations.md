# Installation, reproduction and safe shutdown

## Source-only website setup

Windows 64-bit, Python 3.12 and PowerShell are the validated environment. From a
clean repository root, use an actual Python interpreter (not the Windows Store
alias):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py seed_demo_polls
.\.venv\Scripts\python.exe manage.py seed_demo_homework_review
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

The seed commands use versioned synthetic fixtures, do not generate AI output,
and never publish AI feedback. Open the generated **local-only**
`.local/demo-credentials.json` privately for each account's random password.
Do not copy it into reports, commits or screenshots. Accounts/roles are listed in
[README](../README.md#local-setup-and-run). Re-seeding preserves existing passwords
and does not take over unrelated matching accounts. No personal API key is needed.

The source-only site supports authentication, courses/meetings, QR attendance,
comments/XLSX, manual/demo polls and versioned homework. Model-backed generation
requires the separate assets below; a source-only clone cannot silently reproduce
those outputs. Missing models fail explicitly, without downloads or fake results.

**Clean setup evidence, 19 November:** HEAD source archive plus the closure code,
new venv and pinned requirements installed from PyPI; no copied `.local`, media,
models or database. `check`, all migrations through 0012, migration dry-run,
seed_demo twice, both other seeds and cleanup preview exited 0. Fresh generated
demo credentials authenticated successfully; a real loopback development server
served the login page with HTTP 200 and was then stopped. The [structured check record](../experiments/results/clean-install-20261119.json)
is versioned; the temporary source copy/installation logs are local-only. This verifies website installation, not
GPU asset installation on a second machine.

## Separate local AI prerequisites

The tested workstation has 24 GB RAM and NVIDIA RTX 5050 Laptop 8 GB VRAM.
Driver/CUDA availability on another machine must be checked separately; do not
change drivers automatically. Website and AI Python environments are separate.
The existing setup script downloads an official checksum-verified Ollama archive
and installs AI Python dependencies; review download sizes first (several GB for
runtime/models). No setup/download was repeated during submission closure.

```powershell
.\experiments\local_ai\bootstrap.ps1 -PythonExecutable python
```

It uses Ollama **0.40.14** and the dependency ranges in
[AI requirements](../experiments/local_ai/requirements.txt); the
[recorded lock](../experiments/local_ai/requirements-lock.txt) documents the
tested exact environment. The website locks its own dependencies separately.

Install the tested ASR checkpoint without running any experiment or requiring a
private Downloads file:

```powershell
@'
from huggingface_hub import snapshot_download
from classroom.asr_checkpoint import REPO, REVISION, FILE_SHA256, verify_checkpoint
folder = '.ai-lab/models/faster-whisper-large-v3-turbo'
snapshot_download(REPO, revision=REVISION, allow_patterns=list(FILE_SHA256), local_dir=folder, token=False)
verify_checkpoint(folder)
print('Pinned local ASR files verified.')
'@ | .\.ai-lab\venv\Scripts\python.exe -
```

Source is the public `dropbox-dash/faster-whisper-large-v3-turbo` CTranslate2
checkpoint, revision `0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf`; model.bin is
approximately 1.62 GB. File hashes are versioned in `asr_checkpoint.py`.
The child uses the Ollama bundle's `cuda_v12` DLL directory only for its process,
faster-whisper 1.2.1 / CTranslate2 4.8.5 / PyAV 16.0.0, CUDA float16. There is
no automatic CPU/model fallback. See [ASR details](local-transcription.md).

For Qwen, start the existing isolated setup/experiment service in PowerShell:

```powershell
.\experiments\local_ai\start_ollama.ps1
$env:OLLAMA_HOST = '127.0.0.1:11435'
$env:OLLAMA_MODELS = Join-Path (Get-Location) '.ai-lab/models/ollama'
$env:OLLAMA_NO_CLOUD = '1'
.\.ai-lab\ollama\ollama.exe pull qwen3:8b
@'
from classroom.summary_contract import verify_local_model
print(verify_local_model('.ai-lab/models/ollama'))
'@ | .\.ai-lab\venv\Scripts\python.exe -
```

Qwen3 8B Q4_K_M weights are about 5.2 GB. A registry tag can change: the adapter
requires the manifest/weight identity in `summary_contract.py`, not just the tag.
If verification differs, stop; do not silently substitute or update the pin.
The setup service is not required for ordinary workers, which own separate local
services. To stop that setup service, read `.ai-lab/ollama.pid`, verify the PID's
executable is this checkout's `.ai-lab/ollama/ollama.exe` with `Get-CimInstance
Win32_Process`, then stop only that PID. Do not kill every Python/Ollama process.

## Daily operation and stopping

Use separate foreground PowerShell windows, all in the repository root:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
# A second window:
.\.venv\Scripts\python.exe manage.py run_video_worker
# A third window:
.\.venv\Scripts\python.exe manage.py run_video_maintenance
# A fourth window:
.\.venv\Scripts\python.exe manage.py run_homework_worker
```

Ctrl+C in each window stops that command. Worker-owned subprocesses have bounded
lifetimes; on restart interrupted work fails rather than replaying inference.
Maintenance can mark abandoned jobs after heartbeat expiry. Keep it running for
24-hour MP4 cleanup and seven-day transcript/summary/review-point deletion. No
machine can physically delete files while powered off. Poll/video/homework share
compute, so avoid simultaneous live AI actions; group jobs wait at most 15 minutes,
while polls retain explicit busy failure. No paid or external fallback exists.

### Temporary network access and revocation

Default ALLOWED_HOSTS is exact loopback names, not a wildcard. LAN access is an
explicit temporary process-only override and must use the current private IPv4
address, not a stale QR/link. See [phone plan](phone-testing.md). On the current
workstation only, `.local/phone_lan_server.py` and `.local/stop_phone_lan.ps1`
are ignored local helpers, **not a fresh-clone prerequisite**. The latter checks
the recorded PID's command identity before stopping it. Run it to stop that
temporary server, or Ctrl+C if the LAN server is foreground. Stopping it removes
the process-only ALLOWED_HOSTS override; restart the loopback command above.

Check an existing named firewall rule before changing it:

```powershell
Get-NetFirewallRule -DisplayName 'TeachingTool-Ex2-Phone-Demo-8000' -ErrorAction SilentlyContinue
```

Only if that exact temporary rule exists and is no longer needed, remove it in
elevated PowerShell:

```powershell
Remove-NetFirewallRule -DisplayName 'TeachingTool-Ex2-Phone-Demo-8000'
```

Do not disable the firewall, remove unrelated rules or expose a public interface.
If new LAN access is desired from a fresh clone, choose the current private IP,
authorize a temporary binding/exact host and, if required, Private-profile,
LocalSubnet, TCP 8000 access separately. Nothing in source-only installation
creates that access. No network rule was changed in closure.

## Cleanup preview and intentional deletion

Preview is safe and does not delete anything:

```powershell
.\.venv\Scripts\python.exe manage.py cleanup_demo
```

After preserving required evidence, stopping workers and explicitly deciding to
remove synthetic course records, use an exact seeded course code (repeat the
option for both courses). **Do not run this during review or while evidence is
still needed**:

```powershell
.\.venv\Scripts\python.exe manage.py cleanup_demo --course-code DEMO-CS101 --apply
```

It refuses active work and deletes only the named demo course's records, retaining
accounts/credentials. It does not delete private files; the existing video
maintenance removes orphan UUID media after its grace period. It does not purge
experiment reports, user Downloads or model files. The independent
`run_video_maintenance --once` performs retention cleanup, **not a preview**.
No deletion was executed as part of closure; even isolated validation artifacts
were retained locally.

## Repeating software and load checks

```powershell
$env:TEACHINGTOOL_VALIDATION_DIR = Join-Path (Get-Location) '.local/my-final-tests'
.\.venv\Scripts\python.exe manage.py test classroom --settings=teachingtool.validation_settings --noinput
node --test tests_js/*.test.cjs
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe experiments/load_probe.py --directory .local/my-new-load-run
```

Choose a new load directory; the probe refuses an existing validation database.
It creates 80 then 100 synthetic accounts, performs real loopback requests and
retains its isolated DB/results for review. It neither uses demo data nor invokes
AI. Its MD5 hasher is test-only; ordinary settings retain Django's password policy.
The clean install does not require Node; Node is only needed for these logic tests
and optional offline diagram reproduction.

For an explicitly requested real lecturer-review reproduction, provide JSON with
`segments: [{start, end, text}]` and `language: "en"` (or Hebrew for a separately
assessed trial), then run `experiments/lecturer_review_probe.py --input <file>
--output <new-report.json>` with website Python. That script uses installed AI
assets, no cloud, and refuses to overwrite evidence. A synthetic input example is
[included](../experiments/lecturer-review-input-example.json); it is not the private
SHORT transcript used for the recorded run and has not been inferred on here.
