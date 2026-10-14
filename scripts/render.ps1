# Helper script to render Quarto website safely on Windows
$env:TEMP = "C:\Temp"
$env:TMP = "C:\Temp"
if (Test-Path "C:\Quarto\bin") {
    $env:PATH = "C:\Quarto\bin;" + $env:PATH
}

Write-Host "Rendering Quarto website..." -ForegroundColor Cyan
quarto render $args

