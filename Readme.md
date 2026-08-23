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

The 2026 MOD-BN can be used in three ways.

### 1. Use the base snapshot

Load `F1-2026-MOD-BN.sna` in your favourite ZX Spectrum 48K emulator. This
base snapshot contains the original 1985 season, artwork inherited from 2020
MOD, a custom font, several graphical adjustments and fixes for bugs inherited
from the original game.

This is the simplest way to play, but it does not use the principal feature of
the 2026 MOD-BN: season customisation.

### 2. Run Tweak-F1.py from the command line

`Tweak-F1.py` is the main customisation tool supplied with the 2026 MOD-BN. It
can be run from PowerShell on Windows or from a Bash-compatible command prompt
on Linux or WSL.

The script accepts input files defining teams, drivers, sponsors, colours and
races. You can also select the championship year and enable optional gameplay
adjustments. It creates a new `.sna` file and leaves the verified base snapshot
`F1-2026-MOD-BN.sna` unchanged.

#### Basic PowerShell example

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

On Linux or WSL, use `python3 ./Tweak-F1.py` and replace the PowerShell
backticks used for line continuation with backslashes (`\`). Ready-made
PowerShell and Bash scripts are also available in the `Scripts/` directory.

Sample input files for several seasons are available in the `Inputs/`
directory.

Complete instructions and command-line options are documented in
[Technical-Reference.md](Technical-Reference.md#part-iv-using-tweak-f1py).

### 3. Use the online Season Builder

Users who prefer _not_ to work with a command prompt can use the
[online Season Builder](https://niceno.github.io/Formula-One-2026-MOD-BN/Index.html).
It provides a graphical interface for the same `Tweak-F1.py` program. You can
choose one of the supplied seasons or provide your own input files.

The builder runs entirely inside the browser. It does not upload the selected
files or the generated snapshot to a server, and it always uses the verified
`F1-2026-MOD-BN.sna` as its base.

## Main files

- `F1-2026-MOD-BN.sna` — the modified game
- `Tweak-F1.py` — season-customisation program
- `Technical-Reference.md` — technical documentation
- `Inputs/` — sample season definitions
- `Images/` — screenshots and supporting images
- `Index.html`, `Season-Builder.js` and `Season-Builder.css` — online Season
  Builder

## Credits

- Original game: G. B. Munday and B. P. Wheelhouse
- 2020 MOD: Rui Martins and Jorge Pois
- 2026 MOD-BN modifications, documentation and tools: Bojan Niceno

## Acknowledgements

- I would like to thank Rui Martins and Jorge Pois for their work on the
  2020 MOD and for taking the time to review this modification and share their
  feedback before making it public.

- Development of this modification was assisted by OpenAI Codex, particularly
  in the reverse engineering of the Z80 program, analysis and patching of SNA
  snapshots, development of `Tweak-F1.py`, and preparation of the technical
  documentation. All design decisions, testing and final responsibility remain
  with Bojan Niceno.
