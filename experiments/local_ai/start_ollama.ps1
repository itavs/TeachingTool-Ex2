# These settings apply only to this process and its child, never to the system.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$labRoot = Join-Path $projectRoot '.ai-lab'
$env:OLLAMA_HOST = '127.0.0.1:11435'
$env:OLLAMA_MODELS = Join-Path $labRoot 'models\ollama'
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_CONTEXT_LENGTH = '8192'
$env:OLLAMA_NUM_PARALLEL = '1'
$env:OLLAMA_MAX_LOADED_MODELS = '1'
$env:OLLAMA_KEEP_ALIVE = '10m'
$env:OLLAMA_TMPDIR = Join-Path $labRoot 'tmp'
$process = Start-Process -FilePath (Join-Path $labRoot 'ollama\ollama.exe') -ArgumentList 'serve' -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $labRoot 'ollama-stdout.log') -RedirectStandardError (Join-Path $labRoot 'ollama-stderr.log')
$process.Id | Set-Content -LiteralPath (Join-Path $labRoot 'ollama.pid')
Write-Output "Experiment server PID: $($process.Id), loopback port 11435, cloud disabled."
