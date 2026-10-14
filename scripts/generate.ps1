# PowerShell launcher for CV Knowledge Base Document Generator
param (
    [string]$arxiv,
    [string]$topic,
    [string]$model = "gemini-2.5-flash",
    [switch]$skipRender
)

$PYTHON_EXE = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"

if (-not (Test-Path $PYTHON_EXE)) {
    Write-Host "가상환경(.venv)을 찾을 수 없습니다. python -m venv .venv를 먼저 실행해 주세요." -ForegroundColor Red
    exit 1
}

$cmdArgs = @("scripts\generate_document.py")
if ($arxiv) {
    $cmdArgs += @("--arxiv", $arxiv)
}
if ($topic) {
    $cmdArgs += @("--topic", $topic)
}
if ($model) {
    $cmdArgs += @("--model", $model)
}
if ($skipRender) {
    $cmdArgs += "--skip-render"
}

& $PYTHON_EXE $cmdArgs

