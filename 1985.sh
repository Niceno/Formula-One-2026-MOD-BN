#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

python ./Tweak-F1.py \
  --game ./F1-2026-Mod.sna \
  --year 1985 \
  --suffix Season-1985 \
  --races ./Inputs/races_1985.txt \
  --teams ./Inputs/teams_1985.txt \
  --colors ./Inputs/colors_1985.txt \
  --sponsors ./Inputs/sponsors_1985.txt \
  --drivers ./Inputs/drivers_1985.txt \
  --automatic-human-pit-stops \
  --double-starting-money \
  --random-incidents rare
