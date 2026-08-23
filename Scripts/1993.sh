#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir/.."

python ./Tweak-F1.py \
  --game ./F1-2026-MOD-BN.sna \
  --year 1993 \
  --suffix Season-1993 \
  --races ./Inputs/races_1993.txt \
  --teams ./Inputs/teams_1993.txt \
  --colors ./Inputs/colors_1993.txt \
  --sponsors ./Inputs/sponsors_1993.txt \
  --drivers ./Inputs/drivers_1993.txt \
  --automatic-human-pit-stops \
  --double-starting-money \
  --random-incidents rare
