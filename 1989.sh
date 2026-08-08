#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

python ./Tweak-F1.py \
  --game ./F1-2026-Mod.sna \
  --year 1989 \
  --suffix Season-1989 \
  --races ./Inputs/races_1989.txt \
  --teams ./Inputs/teams_1989.txt \
  --colors ./Inputs/colors_1989.txt \
  --sponsors ./Inputs/sponsors_1989.txt \
  --drivers ./Inputs/drivers_1989.txt \
  --automatic-human-pit-stops \
  --double-starting-money \
  --random-incidents rare
