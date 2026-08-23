Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location (Split-Path $PSScriptRoot -Parent)
try {
  python .\Tweak-F1.py `
    --game .\F1-2026-MOD-BN.sna `
    --year 2020 `
    --suffix Season-2020 `
    --races .\Inputs\races_2020.txt `
    --teams .\Inputs\teams_2020.txt `
    --colors .\Inputs\colors_2020.txt `
    --sponsors .\Inputs\sponsors_2020.txt `
    --drivers .\Inputs\drivers_2020.txt

  if ($LASTEXITCODE -ne 0) {
    throw "Tweak-F1.py failed with exit code $LASTEXITCODE."
  }
}
finally {
  Pop-Location
}
