# Run locally by the user. Never paste the key into chat or a command argument.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$secretDir = Join-Path $projectRoot '.ai-lab\secrets'
New-Item -ItemType Directory -Force -Path $secretDir | Out-Null
$keyPath = Join-Path $secretDir 'gemini-api-key.txt'
$secureValue = Read-Host 'Paste the Gemini API key (hidden input)' -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureValue)
try {
    $keyValue = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    if ([string]::IsNullOrWhiteSpace($keyValue)) { throw 'Empty key; nothing saved.' }
    [IO.File]::WriteAllText($keyPath, $keyValue.Trim(), (New-Object Text.UTF8Encoding($false)))
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    $keyValue = $null
    $secureValue = $null
}
Write-Output 'Key saved locally in the Git-ignored experiment directory. Key value was not printed.'
