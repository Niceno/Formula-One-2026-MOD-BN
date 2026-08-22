Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
try {
  python .\Tweak-F1.py `
    --game .\F1-2026-MOD-BN.sna `
    --year 1985 `
    --suffix Season-1985 `
    --races .\Inputs\races_1985.txt `
    --teams .\Inputs\teams_1985.txt `
    --colors .\Inputs\colors_1985.txt `
    --sponsors .\Inputs\sponsors_1985.txt `
    --drivers .\Inputs\drivers_1985.txt `
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
