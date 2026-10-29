# Copie le dossier winterbreak2 à la racine du Kindle branché en USB.
# Usage : clic droit > Exécuter avec PowerShell (ou : powershell -ExecutionPolicy Bypass -File .\copier_sur_kindle.ps1)
$src = Join-Path $PSScriptRoot "wb2\winterbreak2"
if (-not (Test-Path (Join-Path $src "dialoger.html"))) { Write-Host "Fichier wb2\winterbreak2\dialoger.html introuvable."; exit 1 }

$kindle = Get-Volume | Where-Object { $_.FileSystemLabel -eq "Kindle" -and $_.DriveLetter } | Select-Object -First 1
if (-not $kindle) {
    Write-Host "Aucun lecteur 'Kindle' détecté. Branche le Kindle en USB, attends qu'il apparaisse dans l'Explorateur, puis relance."
    exit 1
}
$root = "$($kindle.DriveLetter):\"
Write-Host "Kindle détecté sur $root"
Copy-Item -Path $src -Destination $root -Recurse -Force
if (Test-Path (Join-Path $root "winterbreak2\dialoger.html")) {
    Write-Host "OK : winterbreak2\dialoger.html copié à la racine du Kindle."
    $bins = Get-ChildItem -Path $root -Filter "update*.bin*" -File -ErrorAction SilentlyContinue
    if ($bins) { Write-Host "Attention, fichiers de mise à jour présents à la racine :"; $bins | ForEach-Object { "  $($_.Name)" } }
    Write-Host "Éjecte le Kindle (Retirer le périphérique en toute sécurité), puis ouvre le Navigateur expérimental sur https://penguins184.xyz/wb2"
} else {
    Write-Host "La copie semble avoir échoué."
    exit 1
}
