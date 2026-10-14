# Helper script to run Quarto live preview server safely on Windows
$env:TEMP = "C:\Temp"
$env:TMP = "C:\Temp"
if (Test-Path "C:\Quarto\bin") {
    $env:PATH = "C:\Quarto\bin;" + $env:PATH
}

Write-Host "Starting Quarto live preview server..." -ForegroundColor Cyan
quarto preview $args

