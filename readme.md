# Formula One 2026 MOD-BN for the ZX Spectrum

An unofficial, non-commercial modification of the 1985 ZX Spectrum game
*Formula One* by G. B. Munday and B. P. Wheelhouse.

This project builds upon [*Formula One (2020 MOD), update 1.25*](https://planetasinclair.blogspot.com/2021/01/formula-one-2020-mod-update-125.html)
by Rui Martins and Jorge Pois.  It includes a configurable season-tweaking
script, detailed technical documentation, fixes for several bugs inherited
from the original 1985 game, a custom font, and small graphical adjustments.

## Main changes

- Configurable teams, drivers, sponsors, colours, year and race calendar.
- Fixes for several bugs inherited from the original 1985 game.
- Optional gameplay adjustments, including automatic pit stops and less
  frequent random repair incidents.
- A custom font and additional graphical adjustments.
- Celsius temperatures and the original 1985 scoring system.
- Detailed technical documentation of the game’s memory and Z80 code.

For complete technical details, see
[Technical-Reference.md](Technical-Reference.md).

## Usage

One possibility is to load `F1-2026-MOD-BN.sna` in your favourite ZX Spectrum
48K emulator. This base snapshot contains the original 1985 season, artwork
inherited from 2020 MOD, a custom font, several graphical adjustments and fixes
for bugs inherited from the original game.  However, doing only that misses the
most interesting part of the 2026 MOD-BN.

The principal feature of the 2026 MOD-BN is season customisation. You can use
the provided `Tweak-F1.py` script with input files defining teams, drivers,
sponsors, colours and races. You can also select the championship year
and enable optional gameplay adjustments. The script creates a new `.sna`
file and leaves the base snapshot `F1-2026-MOD-BN.sna` unchanged.

### Basic example

For example, the following command creates a 1991 season using the supplied
input files:

```powershell
python .\Tweak-F1.py `
  --game=F1-2026-MOD-BN.sna `
  --suffix=Season-1991 `
  --year=1991 `
  --teams=Inputs\teams_1991.txt `
  --drivers=Inputs\drivers_1991.txt `
  --sponsors=Inputs\sponsors_1991.txt `
  --races=Inputs\races_1991.txt `
  --colours=Inputs\colors_1991.txt
```

This creates `F1-2026-MOD-BN-Season-1991.sna` in the current directory and
leaves the original snapshot unchanged. All options except `--game` and
`--suffix` may be omitted or combined as required.

Sample input files for several seasons are available in the `Inputs/`
directory.  Complete instructions and command-line options are documented
in [Technical-Reference.md](Technical-Reference.md#part-iv-using-tweak-f1py).

## Main files

- `F1-2026-MOD-BN.sna` — the modified game
- `Tweak-F1.py` — season-customisation program
- `Technical-Reference.md` — technical documentation
- `Inputs/` — sample season definitions
- `Images/` — screenshots and supporting images

## Status

The repository is currently private while permission to publish the
2020 MOD-derived artwork and snapshot is being requested.

## Credits

- Original game: G. B. Munday and B. P. Wheelhouse
- 2020 MOD: Rui Martins and Jorge Pois
- 2026 MOD-BN modifications, documentation and tools: Bojan Niceno

## Acknowledgements

Development of this modification was assisted by OpenAI Codex, particularly
in the reverse engineering of the Z80 program, analysis and patching of SNA
snapshots, development of `Tweak-F1.py`, and preparation of the technical
documentation. All design decisions, testing and final responsibility remain
with Bojan Niceno.
