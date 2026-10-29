# Installe kindle-dash (fork Paperwhite pusi77/kindle-dash-pw3) + nos réglages sur le Kindle branché en USB.
# Prérequis : la release extraite dans jailbreak\kindle-dash-pw3\ (dossiers dashboard\ et documents\).
# Usage : powershell -ExecutionPolicy Bypass -File .\copier_dashboard.ps1
$ErrorActionPreference = "Stop"
$proj = Split-Path $PSScriptRoot -Parent
$src = Join-Path $proj "jailbreak\kindle-dash-pw3\dashboard"
if (-not (Test-Path (Join-Path $src "dash.sh"))) { Write-Host "Release introuvable : attendu $src\dash.sh"; exit 1 }

$kindle = Get-Volume | Where-Object { $_.FileSystemLabel -eq "Kindle" -and $_.DriveLetter } | Select-Object -First 1
if (-not $kindle) { Write-Host "Aucun lecteur 'Kindle' détecté. Branche le Kindle en USB puis relance."; exit 1 }
$root = "$($kindle.DriveLetter):\"
$dst = Join-Path $root "dashboard"
Write-Host "Kindle sur $root - installation dans $dst"

# 1) fichiers du fork (dash.sh, start.sh, stop.sh, next-wakeup, local/fetch-dashboard.sh ...)
New-Item -ItemType Directory -Force $dst | Out-Null
New-Item -ItemType Directory -Force (Join-Path $dst "logs") | Out-Null
Copy-Item -Path (Join-Path $src "*") -Destination $dst -Recurse -Force
# 2) le binaire next-wakeup devient next-wakeup.bin, notre wrapper (deux rythmes) prend sa place
Move-Item -Path (Join-Path $dst "next-wakeup") -Destination (Join-Path $dst "next-wakeup.bin") -Force
# 3) nos fichiers : wrapper next-wakeup, local/env.sh, sleeping.png 758x1024
Copy-Item -Path (Join-Path $PSScriptRoot "dashboard\*") -Destination $dst -Recurse -Force
# 4) scriptlets en français dans documents (ceux du fork, en anglais, ne sont pas copiés)
Copy-Item -Path (Join-Path $PSScriptRoot "documents\*.sh") -Destination (Join-Path $root "documents") -Force
# 5) jamais de fichier STOP résiduel
Remove-Item -Path (Join-Path $dst "STOP") -Force -ErrorAction SilentlyContinue

Write-Host "`nContenu de $dst :"
Get-ChildItem -Path $dst -Recurse -File | ForEach-Object { "  " + $_.FullName.Substring($dst.Length) + "  (" + $_.Length + " o)" }
Write-Host "`nScriptlets :"
Get-ChildItem (Join-Path $root "documents") -Filter "Tableau*.sh" | ForEach-Object { "  " + $_.Name }
Write-Host "`nOK. Éjecte le Kindle, débranche-le, puis ouvre « Tableau de bord T2 - Test » dans la bibliothèque."
