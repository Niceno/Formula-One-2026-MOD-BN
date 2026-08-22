# Formula One 2026 Mod for the ZX Spectrum

An unofficial, non-commercial modification of the 1985 ZX Spectrum game
*Formula One* by G. B. Munday and B. P. Wheelhouse.

This project builds upon MOD2020 by R. Martins and J. Pois.  It includes a
configurable season-tweaking script, detailed technical documentation, fixes
for several bugs inherited from the original 1985 game, a custom font, and
additional graphical adjustments.

## Main changes

- configurable teams, drivers, sponsors, colours, year and race calendar;
- fixes for several bugs inherited from the original 1985 game;
- optional gameplay adjustments, including automatic pit stops and less
  frequent random repair incidents;
- a custom font and additional graphical adjustments;
- Celsius temperatures and the original 1985 scoring system;
- detailed technical documentation of the game’s memory and Z80 code.

For complete technical details, see
[F1-2026-Mod-Technical-Reference.md](F1-2026-Mod-Technical-Reference.md).

## Main files

- `F1-2026-Mod.sna` — the modified game
- `Tweak-F1.py` — season-customisation program
- `F1-2026-Mod-Technical-Reference.md` — technical documentation
- `Inputs/` — sample season definitions
- `Images/` — screenshots and supporting images

## Status

The repository is currently private while permission to publish the
MOD2020-derived artwork and snapshot is being requested.

## Credits

- Original game: G. B. Munday and B. P. Wheelhouse
- MOD2020: R. Martins and J. Pois
- 2026 modification, documentation and tools: Bojan Niceno

## Acknowledgements

Development of this modification was assisted by OpenAI Codex, particularly
in the reverse engineering of the Z80 program, analysis and patching of SNA
snapshots, development of `Tweak-F1.py`, and preparation of the technical
documentation. All design decisions, testing and final responsibility remain
with Bojan Niceno.
