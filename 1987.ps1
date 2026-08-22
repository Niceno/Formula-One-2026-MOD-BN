Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
try {
  python .\Tweak-F1.py `
    --game .\F1-2026-MOD-BN.sna `
    --year 1987 `
    --suffix Season-1987 `
    --races .\Inputs\races_1987.txt `
    --teams .\Inputs\teams_1987.txt `
    --colors .\Inputs\colors_1987.txt `
    --sponsors .\Inputs\sponsors_1987.txt `
    --drivers .\Inputs\drivers_1987.txt `
    --automatic-human-pit-stops `
    --double-starting-money `
    --random-incidents rare

  if ($LASTEXITCODE -ne 0) {
    throw "Tweak-F1.py failed with exit code $LASTEXITCODE."
  }
}
finally {
  Pop-Location
}
