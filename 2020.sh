#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

python ./Tweak-F1.py \
  --game ./F1-2026-Mod.sna \
  --year 2020 \
  --suffix Season-2020 \
  --races ./Inputs/races_2020.txt \
  --teams ./Inputs/teams_2020.txt \
  --colors ./Inputs/colors_2020.txt \
  --sponsors ./Inputs/sponsors_2020.txt \
  --drivers ./Inputs/drivers_2020.txt
