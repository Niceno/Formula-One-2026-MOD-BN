#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

python ./Tweak-F1.py \
  --game ./F1-2026-Mod.sna \
  --year 1987 \
  --suffix Season-1987 \
  --races ./Inputs/races_1987.txt \
  --teams ./Inputs/teams_1987.txt \
  --colors ./Inputs/colors_1987.txt \
  --sponsors ./Inputs/sponsors_1987.txt \
  --drivers ./Inputs/drivers_1987.txt \
  --automatic-human-pit-stops \
  --random-incidents rare
