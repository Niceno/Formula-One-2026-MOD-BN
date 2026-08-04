Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
try {
  python .\Tweak-F1.py `
    --game .\F1-2026-Mod.sna `
    --year 1993 `
    --suffix Season-1993 `
    --races .\Inputs\races_1993.txt `
    --teams .\Inputs\teams_1993.txt `
    --colors .\Inputs\colors_1993.txt `
    --sponsors .\Inputs\sponsors_1993.txt `
    --drivers .\Inputs\drivers_1993.txt `
    --automatic-human-pit-stops `
    --random-incidents rare

  if ($LASTEXITCODE -ne 0) {
    throw "Tweak-F1.py failed with exit code $LASTEXITCODE."
  }
}
finally {
  Pop-Location
}
