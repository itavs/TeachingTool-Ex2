# Isolated experiment only. No installer, permanent environment changes, or driver changes.
param([string]$PythonExecutable = 'python')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$labRoot = Join-Path $projectRoot '.ai-lab'
New-Item -ItemType Directory -Force -Path $labRoot | Out-Null
$env:PIP_CACHE_DIR = Join-Path $labRoot 'pip-cache'
$env:HF_HOME = Join-Path $labRoot 'hf-cache'
$env:HF_HUB_DISABLE_TELEMETRY = '1'
$env:HF_HUB_DISABLE_XET = '1'
$basePython = $PythonExecutable
$python = Join-Path $labRoot 'venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    & $basePython -m venv (Join-Path $labRoot 'venv')
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}
& $python -m pip install --index-url https://pypi.org/simple -r (Join-Path $PSScriptRoot 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
$version = 'v0.40.14'
$asset = 'ollama-windows-amd64.zip'
$releaseUrl = "https://github.com/ollama/ollama/releases/download/$version"
$archive = Join-Path $labRoot $asset
if (-not (Test-Path -LiteralPath $archive)) {
    Invoke-WebRequest -Uri "$releaseUrl/$asset" -OutFile $archive
}
$checksums = (Invoke-WebRequest -Uri "$releaseUrl/sha256sum.txt").Content
if ($checksums -is [byte[]]) { $checksums = [System.Text.Encoding]::UTF8.GetString($checksums) }
$line = ($checksums -split "`n" | Where-Object { $_ -match ('\s(?:\./)?\*?' + [regex]::Escape($asset) + '\s*$') })
if (@($line).Count -ne 1) { throw 'No unique official archive checksum found.' }
$expected = ($line.Trim() -split '\s+')[0]
$actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected.ToLowerInvariant()) { throw 'Archive checksum mismatch.' }
$runtime = Join-Path $labRoot 'ollama'
if (-not (Test-Path -LiteralPath (Join-Path $runtime 'ollama.exe'))) {
    Expand-Archive -LiteralPath $archive -DestinationPath $runtime
}
Write-Output "Verified archive SHA256: $actual"
& $python -m pip freeze
Write-Output 'Bootstrap completed. Model inference and downloads are separate steps.'
