[//]: # (----------------------------------------------------------------------)
[//]: # (                                                                      )
[//]: # (    Document layout follows this scheme:                              )
[//]: # (                                                                      )
[//]: # (    # — document title;                                               )
[//]: # (    ## — major Parts;                                                 )
[//]: # (    ### — numbered chapters;                                          )
[//]: # (    #### — subsections within chapters;                               )
[//]: # (    ##### — only if a further level is genuinely necessary.           )
[//]: # (----------------------------------------------------------------------)

# Formula One (ZX Spectrum 48K) Memory Map

This document describes the current snapshot:

`F1-2026-Mod.sna`

It combines the original 1985 teams, drivers and race data with the improved
MOD2020 artwork, plus the colour, temperature in Celsius, scoring, top-view
symmetry and faster progress-bar adjustments made during this project, together
with suppression of the transient chequerboard behind the race-scene country
name, safe handling of sponsor ID zero and corrections that limit both component
purchases and improvements before money is deducted. An optional gameplay
adjustment can double each season's starting money through `Tweak-F1.py`.

The memory map describes the final file and the technical changes it contains.
Temporary development snapshots are deliberately not named: their filenames and
individual hashes were useful during construction, but are not required to
understand or reproduce the final memory layout. The original 1985 snapshot is
retained as the named comparison baseline.

Verified SHA-256:

`4833e1c99ac8ca9fae6ba6c2255a53859470f98544475d363c03edebcda1b481`

## Motivation and history

I first encountered _Formula One_ as a teenager in 1986 and spent countless
hours playing it. Before long, however, I also became aware of some of its
limitations. The team and driver names remained tied to the original season,
even as the game advanced through later years, and I felt that parts of its
graphical presentation could benefit from some polishing.

Back in the 1980s, I modified the game to suit my own tastes. Unfortunately,
those versions were stored only on cassette tapes that have long since
disappeared.

A few weeks before this project began, I came across the 2020 modification by
R. Martins and J. Pois. Their improved artwork, considerably better than
anything I had achieved as a youngster, inspired me to revisit the game.
I used their exceptional graphical work as the foundation for this project,
while making the game easier to adapt to different _Formula One_ seasons.
Teams, drivers, sponsors, colour schemes, championship points, race calendars
and other details can now be adjusted much more systematically with the
enclosed Python script `Tweak-F1.py`.

This document records the resulting investigation and the modifications
carried out during the summer of 2026. It is both a memory map of the finished
snapshot and a record of how this remarkably compact 1985 game works
internally. I hope it will also provide a useful starting point for other
_Formula One_ game enthusiasts who may wish to modify, expand or otherwise
continue developing the game.

## Table of contents

- [Part I: Background and memory layout](#part-i-background-and-memory-layout)
  - [1. Converting a memory address to an SNA file offset](#1-converting-a-memory-address-to-an-sna-file-offset)
  - [2. Standard ZX Spectrum 48K memory layout](#2-standard-zx-spectrum-48k-memory-layout)
  - [3. Quick reference](#3-quick-reference)
  - [4. Program layout: where the Z80 instructions reside](#4-program-layout-where-the-z80-instructions-reside)
    - [Added routines in the final snapshot](#added-routines-in-the-final-snapshot)
    - [Snapshot resume point versus original program entry](#snapshot-resume-point-versus-original-program-entry)
- [Part II: Graphics, text and presentation](#part-ii-graphics-text-and-presentation)
  - [5. Text tables](#5-text-tables)
    - [Driver names](#driver-names)
    - [Team and status names](#team-and-status-names)
    - [Manager names](#manager-names)
    - [Race and circuit names](#race-and-circuit-names)
    - [Sponsors](#sponsors)
    - [Number and weather text](#number-and-weather-text)
  - [6. Team colours and Spectrum attribute bytes](#6-team-colours-and-spectrum-attribute-bytes)
  - [7. Side-view car graphics](#7-side-view-car-graphics)
  - [8. Top-view car graphics](#8-top-view-car-graphics)
    - [Narrow car-number glyphs](#narrow-car-number-glyphs)
    - [Shared engine symmetry adjustment](#shared-engine-symmetry-adjustment)
    - [Shared rear-suspension symmetry adjustment](#shared-rear-suspension-symmetry-adjustment)
  - [9. Starting-grid number boxes](#9-starting-grid-number-boxes)
  - [10. Championship points](#10-championship-points)
  - [11. Original 1985 race data](#11-original-1985-race-data)
    - [Automated schedule editing with `--races`](#automated-schedule-editing-with---races)
  - [12. Season years and previous winners](#12-season-years-and-previous-winners)
  - [13. Other graphics and display memory](#13-other-graphics-and-display-memory)
    - [Live Spectrum screen](#live-spectrum-screen)
    - [Custom character set](#custom-character-set)
    - [Pit and management direction arrows](#pit-and-management-direction-arrows)
    - [Faster car-management progress bars](#faster-car-management-progress-bars)
    - [Cached scene artwork](#cached-scene-artwork)
- [Part III: Game functionality](#part-iii-game-functionality)
  - [14. Celsius conversion](#14-celsius-conversion)
  - [15. Random-number generator and snapshot timing](#15-random-number-generator-and-snapshot-timing)
  - [16. AI maintenance and cars missing from the grid](#16-ai-maintenance-and-cars-missing-from-the-grid)
    - [Race-worthiness test](#race-worthiness-test)
    - [Why many computer cars can miss one race](#why-many-computer-cars-can-miss-one-race)
  - [17. Sponsorship and computer-team finances](#17-sponsorship-and-computer-team-finances)
    - [Zero-sponsor indexing correction](#zero-sponsor-indexing-correction)
    - [Optional double starting money](#optional-double-starting-money)
  - [18. Tyre choice, tyre wear and pit stops](#18-tyre-choice-tyre-wear-and-pit-stops)
    - [Runtime values](#runtime-values)
    - [Initial tyre/track suitability penalty](#initial-tyretrack-suitability-penalty)
    - [Progressive wear](#progressive-wear)
    - [Pit behaviour](#pit-behaviour)
  - [19. Fixed car numbers and the defending champion](#19-fixed-car-numbers-and-the-defending-champion)
  - [20. Modification history represented by the final snapshot](#20-modification-history-represented-by-the-final-snapshot)
  - [21. Verification against `F1-1985-Original.sna` and gameplay screenshots](#21-verification-against-f1-1985-originalsna-and-gameplay-screenshots)
    - [Confirmed identical fixed data](#211-confirmed-identical-fixed-data)
    - [New finding: driver cost is derived, not tabled](#212-new-finding-driver-cost-is-derived-not-tabled)
    - [Open items for further disassembly](#213-open-items-for-further-disassembly)
  - [22. Screen border-colour independence patches](#22-screen-border-colour-independence-patches)
    - [Purpose and original problem](#purpose-and-original-problem)
    - [Added data and routines](#added-data-and-routines)
    - [Patched call sites](#patched-call-sites)
    - [Verified scope of the changes](#verified-scope-of-the-changes)
    - [Recommended verification](#recommended-verification)
  - [23. Removal of the redundant "FORMULA 1" title text](#23-removal-of-the-redundant-formula-1-title-text)
    - [Where it comes from](#where-it-comes-from)
    - [The patch](#the-patch)
  - [24. Limiting acquisition and improvement entries](#24-limiting-acquisition-and-improvement-entries)
  - [25. Random racing incidents and repair-related pit stops](#25-random-racing-incidents-and-repair-related-pit-stops)
    - [Random-incident probability](#random-incident-probability)
    - [Incident selection and codes](#incident-selection-and-codes)
    - [Consequences and pit-stop branch](#consequences-and-pit-stop-branch)
    - [Optional incident-rate patch](#optional-incident-rate-patch)
  - [26. Game sections](#26-game-sections)
    - [The 24-section code map](#the-24-section-code-map)
- [Part IV: Using `Tweak-F1.py`](#part-iv-using-tweak-f1py)
  - [27. Purpose, scope and safeguards](#27-purpose-scope-and-safeguards)
    - [Option-to-memory cross-reference](#option-to-memory-cross-reference)
    - [Script safety checks](#script-safety-checks)
  - [28. Command-line use](#28-command-line-use)
    - [Requirements](#requirements)
    - [Basic syntax](#basic-syntax)
    - [Command-line options](#command-line-options)
    - [Examples](#examples)
    - [Output naming and overwriting](#output-naming-and-overwriting)
  - [29. Input-file formats](#29-input-file-formats)
    - [Common input-file rules](#common-input-file-rules)
    - [Team-name file](#team-name-file)
    - [Driver-name file](#driver-name-file)
    - [Sponsor-name file](#sponsor-name-file)
    - [Race-schedule file](#race-schedule-file)
    - [Team-colour file](#team-colour-file)

All addresses below are Z80 memory addresses unless explicitly described as file
offsets. Ranges are inclusive. Hexadecimal is retained because Spectrum
debuggers and disassemblers commonly use it.  Each number prefixed with $ is
hexadecimal. Decimal equivalents of hexadecimal memory addresses and address
ranges, together with decimal SNA file offsets, are shown in square brackets.
Other unprefixed numbers are decimal unless stated otherwise.
In disassembly listings and raw byte dumps, unprefixed two-digit byte values
are hexadecimal.

[//]: # (----------------------------------------------------------------------)
[//]: # (                                                                      )
[//]: # (    Part I                                                            )
[//]: # (                                                                      )
[//]: # (----------------------------------------------------------------------)
## Part I: Background and memory layout

### 1. Converting a memory address to an SNA file offset

A standard 48K `.sna` contains:

- a 27-byte register header;
- exactly 48 KiB of RAM copied from `$4000` [16384] through `$FFFF` [65535].

Therefore:

```text
SNA file offset = 27 + (Z80 address - $4000)          ; $4000 == [16384]
Z80 address     = $4000 + (SNA file offset - 27)      ; $4000 == [16384]

Decimal form:
SNA file offset = 27 + (Z80 address - 16384)
Z80 address     = 16384 + (SNA file offset - 27)
```

Examples:

| Item                       | Z80 address     | SNA file offset |
|----------------------------|----------------:|----------------:|
| First driver-name record   | `$6E87` [28295] | `$2EA2` [11938] |
| Championship points table  | `$7B96` [31638] | `$3BB1` [15281] |
| Top-view car bitmap        | `$7EDC` [32476] | `$3EF7` [16119] |
| Celsius conversion routine | `$EA70` [60016] | `$AA8B` [43659] |

Do not confuse an address in a debugger with its offset in the `.sna` file: the
latter is always 27 bytes farther into the file after accounting for the
`$4000` [16384] RAM origin.

### 2. Standard ZX Spectrum 48K memory layout

The following table summarises the normal memory arrangement of a 48K
ZX Spectrum under Sinclair BASIC.

| Address or range            | Decimal range  | Size  | Normal use                                                               |
|----------------------------:|---------------:|------:|--------------------------------------------------------------------------|
| `$0000-$3FFF`               | [0-16383]      | 16384 | Spectrum ROM                                                             |
| `$4000-$57FF`               | [16384-22527]  |  6144 | Display bitmap                                                           |
| `$5800-$5AFF`               | [22528-23295]  |   768 | Display attributes: colours, brightness and flashing                     |
| `$5B00-$5BFF`               | [23296-23551]  |   256 | ZX Printer buffer                                                        |
| `$5C00-$5CB5`               | [23552-23733]  |   182 | Spectrum system variables                                                |
| `$5CB6-$5CCA`               | [23734-23754]  |    21 | Channel information                                                      |
| `$5CCB-$FF57`               | [23755-65367]  | 41613 | BASIC program, variables, workspace and other RAM below default `RAMTOP` |
| `$FF58-$FFFF`               | [65368-65535]  |   168 | Default user-defined-graphics area above `RAMTOP`                        |

This is the ordinary ROM/BASIC arrangement, not a restriction on machine-code
programs. Once Formula One has loaded, it reuses much of the RAM above the
display and system-variable areas. The game-specific map below therefore
describes the actual contents of the snapshot.

The table follows the general 48K layout illustrated by
[Break Into Program](http://www.breakintoprogram.co.uk/hardware/computers/zx-spectrum/memory-map),
with the system-variable and channel boundaries refined according to Chapters
24 and 25 of the
[Sinclair ZX Spectrum BASIC Programming manual](https://worldofspectrum.org/ZXBasicManual/).

### 3. Quick reference

| Address or range             | Size  | Purpose                                                                                              |
|-----------------------------:|------:|------------------------------------------------------------------------------------------------------|
| `$4000-$57FF`  [16384-22527] |  6144 | Live Spectrum screen bitmap                                                                          |
| `$5800-$5AFF`  [22528-23295] |   768 | Live Spectrum screen attributes                                                                      |
| `$5B00-$5EE7`  [23296-24295] |  1000 | Original TZX tape bootstrap; temporary during loading; entry at `$5B00` via `RANDOMIZE USR 23296`    |
| `$5C36-$5C37`  [23606-23607] |     2 | Spectrum `CHARS` system variable; contains the offset font-base value `$E9FE` [59902]                |
| `$5C78-$5C79`  [23672-23673] |     2 | Spectrum `FRAMES` counter bytes mixed into the game RNG                                              |
| `$67E8-$67EA`  [26600-26602] |     3 | **Fully loaded game entry point**: `CALL $E99A`                                                      |
| `$6800-$96A9`  [26624-38569] | 11946 | Predominantly game state, text, tables and artwork; broad region overlaps the detailed entries below |
| `$6892-$6893`  [26770-26771] |     2 | Current 16-bit random-number seed                                                                    |
| `$6910-$6915`  [26896-26901] |     6 | Constructor championship totals at run time                                                          |
| `$6916-$692D`  [26902-26925] |    24 | Driver ability/condition values; lower values are better                                             |
| `$6948-$695F`  [26952-26975] |    24 | Active driver championship totals at run time                                                        |
| `$6979-$6984`  [27001-27012] |    12 | Per-car engine condition values                                                                      |
| `$6985-$6990`  [27013-27024] |    12 | Per-car chassis condition values                                                                     |
| `$6991-$699C`  [27025-27036] |    12 | Driver ID assigned to each car slot                                                                  |
| `$699D-$69A8`  [27037-27048] |    12 | Tyre selection for each car: 1-5                                                                     |
| `$69A9-$69B4`  [27049-27060] |    12 | _Accumulated tyre penalty_ for each car                                                              |
| `$69B5-$69CC`  [27061–27084] |    24 | Twelve 16-bit calculated performance/timing values, one per car                                      |
| `$69CD-$69D8`  [27085–27096] |    12 | Retirement-lap number for each car                                                                   |
| `$69D9-$69E4`  [27097–27108] |    12 | Race-participation/result markers; `$FF` [255] produces `DNS`                                        |
| `$69E5-$69F0`  [27109–27120] |    12 | Current incident/event code for each car                                                             |
| `$69F1-$69FC`  [27121–27132] |    12 | Temporary time-loss/delay value for the current race update                                          |
| `$69FD-$6A08`  [27133-27144] |    12 | Per-car race status; `$0D` [13] means excluded from the race                                         |
| `$6A51-$6A5C`  [27217-27228] |    12 | Per-car crew condition/ability values                                                                |
| `$6A5D-$6AA4`  [27229–27300] |    72 | Additional per-car race state: lap counters and 16-bit timing/ranking values                         |
| `$6AA5-$6AD4`  [27301–27348] |    48 | Three 16-entry per-race weighting tables used in race-performance calculations                       |
| `$6AD5-$6BA4`  [27349-27556] |   208 | Original 1985 per-race numeric data                                                                  |
| `$6BA5`        [27557]       |     1 | Current track state: 1 dry, 2 damp, 3 wet                                                            |
| `$6C18-$6CB7`  [27672-27831] |   160 | Shared side-view car bitmap                                                                          |
| `$6CB8-$6D2F`  [27832-27951] |   120 | Six side-view car attribute maps                                                                     |
| `$6E87-$6F94`  [28295-28564] |   270 | Driver names, 27 records x 10 bytes (first blank, 24 normal, one `No Driver' and one for 'Peroni')   |
| `$6F95-$6FDC`  [28565-28636] |    72 | Team/status names, 9 records x 8 bytes                                                               |
| `$6FDD-$6FE2`  [28637-28642] |     6 | Team palette: six Spectrum colour numbers                                                            |
| `$6FE3-$701E`  [28643-28702] |    60 | Manager (player) names, 6 records x 10 bytes                                                         |
| `$7025-$70A4`  [28709-28836] |   128 | Race names, 16 records x 8 bytes                                                                     |
| `$70A5-$71C4`  [28837-29124] |   288 | Circuit names, 16 records x 18 bytes                                                                 |
| `$73C4-$748B`  [29636-29835] |   200 | Right-aligned two-character number strings ` 0` through `99`                                         |
| `$748E-$760D`  [29838-30221] |   384 | Weather descriptions, 12 records x 32 bytes                                                          |
| `$7626-$7627`  [30246-30247] |     2 | Degree glyph and temperature-unit letter                                                             |
| `$7B96-$7B9D`  [31638-31645] |     8 | Championship points for places 1-8                                                                   |
| `$7DB0-$7DC7`  [32176-32199] |    24 | Twelve pointers to car-number glyphs                                                                 |
| `$7DC8-$7E27`  [32200-32295] |    96 | Car-number glyph bitmaps                                                                             |
| `$7E40-$7ECF`  [32320-32463] |   144 | Twelve top-view car/driver records                                                                   |
| `$7EDC-$8093`  [32476-32915] |   440 | Shared top-view car bitmap                                                                           |
| `$8094-$81DD`  [32916-33245] |   330 | Six top-view car attribute maps                                                                      |
| `$82A7`        [33447]       |     1 | Current displayed air temperature                                                                    |
| `$82EA-$82EE`  [33514-33518] |     5 | Purchase-mode dispatcher stored in the former `FORMULA 1` text                                       |
| `$8771-$880C`  [34673-34828] |   156 | Sponsor names, 13 records x 12 bytes                                                                 |
| `$880D-$8819`  [34829-34841] |    13 | Per-sponsor starting-fund values                                                                     |
| `$8841-$8846`  [34881-34886] |     6 | Primary sponsor IDs for the six teams                                                                |
| `$8847-$884C`  [34887-34892] |     6 | Secondary sponsor IDs for the six teams                                                              |
| `$887D-$8888`  [34941-34952] |    12 | Six 16-bit human-team bank balances                                                                  |
| `$8B07-$8B08`  [35591-35592] |     2 | Computer-manager difficulty/maintenance parameters                                                   |
| `$8BD0-$8BDB`  [35792-35803] |    12 | Per-car tyre-age counters                                                                            |
| `$8BDC`        [35804]       |     1 | Season/year offset counter                                                                           |
| `$8F2E` ->     [36654 ->]    |     - | Sorted driver order; first byte is the championship leader ID                                        |
| `$8FCA-$8FCE`  [36810-36814] |     5 | Distance unit text (`miles`)                                                                         |
| `$8FD3-$9182`  [36819-37250] |   432 | Starting-grid number boxes, 12 records x 36 bytes                                                    |
| `$91B8-$922F`  [37304-37423] |   120 | Moving race-scene sprite/blimp data                                                                  |
| `$9402-$9481`  [37890-38017] |   128 | Race-name copy used by the race display                                                              |
| `$9482-$9485`  [38018-38021] |     4 | Literal `Laps` label in the race-summary display                                                     |
| `$9486-$94A5`  [38022-38053] |    32 | Display copy of lap counts, 16 two-digit ASCII values                                                |
| `$9568-$956F`  [38248-38255] |     8 | Flashing left-arrow bitmap used beside the top-view car in the pits                                  |
| `$9643-$964A`  [38467-38474] |     8 | Shared right-arrow bitmap used as a management/menu cursor                                           |
| `$96AA-$EA6F`  [38570-60015] | 21446 | Main code region, with small constants, scratch values and local data interleaved between routines   |
| `$9FDB-$9FE6`  [40923-40934] |    12 | Normal-flow skip and final improvement-limit helper fragment                                         |
| `$B3C5-$B3D5`  [46021-46037] |    17 | Draw the pit arrow and assign its flashing screen attribute                                          |
| `$B97D-$B9AF`  [47485-47535] |    51 | Sponsor selection/reset and starting-balance setup                                                   |
| `$BA1C-$BA26`  [47644-47654] |    11 | Sponsor-ID-to-value pointer helper; ID zero safely maps to ROM                                       |
| `$BBD0-$BC22`  [48080-48162] |    83 | Sponsorship-based starting-balance calculation                                                       |
| `$BC0C-$BC12`  [48140-48146] |     7 | Original balance sequence; optional hook point for double starting money                             |
| `$BCC8-$BCD3`  [48328-48339] |    12 | Number-of-players skip and first improvement-limit helper fragment                                   |
| `$BED0-$BEDB`  [48848-48859] |    12 | Difficulty-screen skip and second improvement-limit helper fragment                                  |
| `$DCD3-$DCD5`  [56531-56533] |     3 | Hook to the context-aware pre-payment clamp wrapper                                                  |
| `$E182-$E184`  [57730-57732] |     3 | Acquisition path redirected through the purchase-mode marker                                         |
| `$E188-$E18A`  [57736-57738] |     3 | Improvement path redirected through the dynamic-limit calculator                                     |
| `$E21C-$E21E`  [57884-57886] |     3 | Hook to the faster car-management progress-bar routine                                               |
| `$E99A-$EA6F`  [59802-60015] |   214 | **Main game sequence begins here; effectively the game’s top-level organiser**                       |
| `$EA70-$EA89`  [60016-60041] |    26 | Added Fahrenheit-to-Celsius routine                                                                  |
| `$EA8A-$EA98`  [60042-60056] |    15 | Dormant optional every-season double-starting-money wrapper                                          |
| `$EA99-$EAB2`  [60057-60082] |    26 | Added faster progress-bar renderer                                                                   |
| `$EAB3-$EAC4`  [60083-60100] |    18 | Added fixed-blue border/PAPER routine and colour constant                                            |
| `$EAC5-$EAE1`  [60101-60129] |    29 | Added fixed-black/fixed-yellow border/PAPER routine and constants                                    |
| `$EAE2-$EAFB`  [60130-60155] |    26 | Added context-aware pre-payment clamp wrapper                                                        |
| `$EAFC-$EAFD`  [60156-60157] |     2 | Remaining zero-filled control-character space                                                        |
| `$EAFE-$EDFD`  [60158-60925] |   768 | Active custom character-set bitmaps, 96 glyphs × 8 bytes                                             |
| `$EDFE-$F5FD`  [60926-62973] |  2048 | Pit/garage bitmap cache                                                                              |
| `$F5FE-$F6FD`  [62974-63229] |   256 | Pit/garage attribute cache                                                                           |
| `$F6FE-$FEFD`  [63230-65277] |  2048 | Race-scene bitmap cache                                                                              |
| `$FEFE-$FFFD`  [65278-65533] |   256 | Race-scene attribute cache                                                                           |

**Note:** the `CHARS` variable and the font location

The Spectrum system variable `CHARS`, stored at `$5C36-$5C37` [23606-23607],
contains `$E9FE` [59902].  This is not the physical beginning of the font.
Character codes 0-31 are non-printable control codes;  at eight bytes per
character, they account for an offset of 256 bytes. The first printable
character is code 32, so its bitmap is found at `$E9FE` + 256 = `$EAFE` [60158].
The actual custom font therefore occupies `$EAFE-$EDFD` [60158-60925] and
contains 96 printable glyphs of eight bytes each. Address `$E9FE` itself
remains part of the executable code; it is merely the offset value stored in
`CHARS`, not font data.

### 4. Program layout: where the Z80 instructions reside

There is no separate executable object inside a 48K `.sna`. The file stores the
Z80 register state followed by a byte-for-byte copy of RAM. The Z80 also has no
executable-memory flag: any byte in RAM becomes an instruction when the program
counter reaches it. Formula One consequently keeps machine instructions,
constants, small local tables and temporary values in the same broad part of
memory.

The useful high-level division is:

| Contents                                 | Z80 address                 | SNA file offset             | Notes                                                                                      |
|------------------------------------------|----------------------------:|----------------------------:|--------------------------------------------------------------------------------------------|
| Spectrum ROM                             | `$0000-$3FFF` [    0-16383] | Not present                 | Operating-system, keyboard, display and floating-point routines                            |
| Spectrum screen and system workspace     | `$4000-$67FF` [16384-26623] | `$001B-$281A` [   27-10266] | Screen, attributes, system variables, empty BASIC workspace and the active machine stack   |
| Predominantly game data                  | `$6800-$96A9` [26624-38569] | `$281B-$56C4` [10267-22212] | Runtime state, text, fixed tables, graphics and drawing data                               |
| Main Z80 code region                     | `$96AA-$EA6F` [38570-60015] | `$56C5-$AA8A` [22213-43658] | region with most game instructions, small constants, scratch values and local data interleaved between routines |
| Added Z80 routines and constants         | `$EA70-$EAFB` [60016-60155] | `$AA8B-$AB16` [43659-43798] | Six documented code/data blocks added to the final 2026 snapshot below the printable font  |
| Remaining unused control-character slots | `$EAFC-$EAFD` [60156-60157] | `$AB17-$AB18` [43799-43800] | Verified zero-filled padding in this snapshot; not part of the printable font              |
| Printable custom font                    | `$EAFE-$EDFD` [60158-60925] | `$AB19-$AE18` [43801-44568] | Character codes 32-127, eight bytes per glyph                                              |
| Cached scene artwork                     | `$EDFE-$FFFD` [60926-65533] | `$AE19-$C018` [44569-49176] | Pit/garage and race-scene bitmap and attribute caches                                      |

`$96AA` [38570] is the lowest-address confirmed machine-code routine, not necessarily the historical tape loader's initial entry point. For example, the first seven bytes at `$96AA` are:

```text
F5 C5 D5 E5 21 DD 6F
```

The Z80 executes them as:

```z80
PUSH AF
PUSH BC
PUSH DE
PUSH HL
LD   HL,$6FDD
```

This begins the palette-selection routine. Other established entry points in
the main region include the text printer at `$9728` [38696], the
keyboard/input wait routine at `$99F1` [39409], the random-number
routine at `$9919` [39193], the championship-scoring routine at
`$CE54` [52820], the AI maintenance routine at `$CF23` [53027],
and the race loop around `$E9A8` [59816].

The phrase **main Z80 code region** does not mean that every byte from `$96AA`
through `$EA6F` is an opcode. Z80 programs commonly place lookup values,
immediate drawing parameters, short tables and writable scratch bytes beside
the instructions that use them. A disassembler therefore needs known entry
points and control-flow analysis; blindly decoding the entire range from its
first byte will sometimes display local data as nonsensical instructions.

#### Added routines in the final snapshot

| Routine                                                     | Z80 address                 | SNA file offset             | Size     |
|-------------------------------------------------------------|----------------------------:|----------------------------:|---------:|
| Fahrenheit-to-Celsius conversion                            | `$EA70-$EA89` [60016-60041] | `$AA8B-$AAA4` [43659-43684] | 26 bytes |
| Optional every-season double-starting-money wrapper         | `$EA8A-$EA98` [60042-60056] | `$AAA5-$AAB3` [43685-43699] | 15 bytes |
| Faster car-management progress-bar renderer                 | `$EA99-$EAB2` [60057-60082] | `$AAB4-$AACD` [43700-43725] | 26 bytes |
| Fixed-blue border/PAPER routine and constant                | `$EAB3-$EAC4` [60083-60100] | `$AACE-$AADF` [43726-43743] | 18 bytes |
| Fixed-black/fixed-yellow border/PAPER routine and constants | `$EAC5-$EAE1` [60101-60129] | `$AAE0-$AAFC` [43744-43772] | 29 bytes |
| Context-aware pre-payment clamp wrapper                     | `$EAE2-$EAFB` [60130-60155] | `$AAFD-$AB16` [43773-43798] | 26 bytes |

In the MOD2020-derived code layout used by the final snapshot, the pre-existing
occupied code ends at `$EA6F` [60015]. The original 1985 reference has
an equivalent six-byte tail at `$EA70-$EA75` because its surrounding code is
six bytes longer; it is therefore incorrect to describe the whole area as
universally zero-filled in every build. In the modified layout, `$EA70-$EAFB`
is repurposed for the six additions above and `$EAFC-$EAFD` remains zero-filled.
The normal printable character set does not begin until `$EAFE` [60158],
so none of these additions overwrites visible letters, digits or punctuation.

#### Snapshot resume point versus original program entry

Both reference snapshots have stack pointer `$67BC` [26556]. The first
two stack bytes are `38 00`, so the snapshot loader restores program counter
`$0038` [56], the 48K Spectrum ROM interrupt handler. The following two
stack bytes are `F8 99`, giving interrupt return address `$99F8` [39416],
inside the keyboard/input wait routine at `$99F1-$9A2C` [39409-39468].
When an emulator restores either snapshot, it resumes the ROM interrupt and
then returns to the waiting game code at `$99F8`.

That address is the saved **resume point**, not proof of the address originally
called by the tape loader. A snapshot preserves the already-running machine,
but not necessarily the original BASIC loader and its `RANDOMIZE USR` command.
The historical first entry address therefore cannot be stated with certainty
from these `.sna` files alone.

#### Annotated disassembly of the game entry and main sequence

The following annotated disassembly covers the game’s main control sequence-the
top-level organiser that calls the principal game phases and controls
progression through races and seasons. In the current snapshot, it occupies
`$E99A-$EA6F` [59802-60015], a total of 214 bytes, and is entered through the
`CALL $E99A` instruction at `$67E8` [26600].

```z80
; ---------------------------------------------------------------------------
; START-UP DISPATCH
; Section 01 handles the opening/load question.
; It returns A=1 if L was selected, or A=0 for a new game.
; ---------------------------------------------------------------------------
$E99A: CD 6A E3    CALL $E36A
$E99D: FE 00       CP   $00
$E99F: 28 07       JR   Z,$E9A8     ; new game: start season preparation

; ---------------------------------------------------------------------------
; LOADED-GAME RESUME TEST
; This block is reached after a previous game has been loaded.
; $6BB2 contains the saved Grand Prix counter.
; A value below 16 identifies a mid-season save, so execution resumes the
; existing season at $E9B5. A value of 16 identifies an end-of-season save,
; so execution falls through to preparation of the next season.
; Mid-season saving is possible if S was pressed during an earlier race.
; ---------------------------------------------------------------------------
$E9A1: 3A B2 6B    LD   A,($6BB2)   ; load A with byte stored at $6BB2
$E9A4: FE 10       CP   $10         ; compare with 16
$E9A6: 38 0D       JR   C,$E9B5     ; below 16: resume mid-season

; ---------------------------------------------------------------------------
; SEASON LOOP START
; $E3A9 performs season preparation, including sponsor and driver selection.
; $DD5C then runs the car, engine, chassis and crew acquisition section.
; ---------------------------------------------------------------------------
$E9A8: CD A9 E3    CALL $E3A9       ; sections 07 and 08
$E9AB: CD 5C DD    CALL $DD5C       ; section 09
$E9AE: 18 0B       JR   $E9BB       ; proceed to Grand Prix preparation

; ---------------------------------------------------------------------------
; CONDITIONAL BETWEEN-GRAND-PRIX SAVE CHECK
; This routine is called after Grands Prix 1–15, but it does not normally
; display the save question. Pressing S during the race sets the save-request
; flag at $96A8. If that flag is clear, $E504 returns immediately; if it is
; set, $E504 displays the save question and then clears the flag.
; Afterwards, continue to car and crew preparation for the next Grand Prix.
; ---------------------------------------------------------------------------
$E9B0: CD 04 E5    CALL $E504       ; section 22: save-game question
$E9B3: 18 03       JR   $E9B8

; ---------------------------------------------------------------------------
; MID-SEASON LOADED-GAME PATH
; A loaded game must ask for the Kempston setting again because that setting
; is not restored as part of the saved championship state.
; Both paths then enter the common car-and-crew acquisition routine.
; ---------------------------------------------------------------------------
$E9B5: CD 87 E6    CALL $E687       ; section 02: Kempston question
$E9B8: CD 5C DD    CALL $DD5C       ; section 09: car and crew acquisition

; ---------------------------------------------------------------------------
; GRAND PRIX LOOP START — PRE-RACE PREPARATION
; $E5A8 is currently a single RET, making its CALL effectively a placeholder.
; $E3C7 is the Grand Prix controller: it advances the race number, checks car
; eligibility and runs the announcement, tyre choice and starting-grid phases.
; It can also reach section 24 if no cars are eligible to race.
; ---------------------------------------------------------------------------
$E9BB: CD A8 E5    CALL $E5A8       ; currently an effective no-operation
$E9BE: CD C7 E3    CALL $E3C7       ; sections 10–12, or section 24

; ---------------------------------------------------------------------------
; RACE SIMULATION LOOP START — ONE PASS PER LAP
; Read the race-control keys, advance the simulation for all cars and update
; the moving race display.
; ---------------------------------------------------------------------------
$E9C1: CD 2D 9A    CALL $9A2D       ; read and process race-control keys
$E9C4: CD 8E C3    CALL $C38E       ; core race-simulation update
$E9C7: CD B3 9F    CALL $9FB3       ; update the moving race display

; ---------------------------------------------------------------------------
; RACE-DISPLAY/FINISH-ANIMATION DECISION
; $8B67 is a race-display control flag modified by the race keyboard controls.
; A zero value branches directly to the finish/marshal-animation path.
; A non-zero value requires an additional check of the animation phase.
; ---------------------------------------------------------------------------
$E9CA: 3A 67 8B    LD   A,($8B67)
$E9CD: FE 00       CP   $00
$E9CF: CA E8 E9    JP   Z,$E9E8

; ---------------------------------------------------------------------------
; FINISH-ANIMATION PHASE CONTROL
; If $8B68 is zero, skip the marshal animation for this lap.
; A phase value of 1 advances to 2; a value of 2 or more wraps back to zero.
; A non-zero phase then continues through the animation below.
; ---------------------------------------------------------------------------
$E9D2: 3A 68 8B    LD   A,($8B68)
$E9D5: FE 00       CP   $00
$E9D7: CA 03 EA    JP   Z,$EA03     ; no animation this lap
$E9DA: FE 02       CP   $02
$E9DC: D2 E3 E9    JP   NC,$E9E3
$E9DF: 3C          INC  A           ; phase 1 becomes phase 2
$E9E0: C3 E5 E9    JP   $E9E5

$E9E3: 3E 00       LD   A,$00       ; wrap the animation phase to zero
$E9E5: 32 68 8B    LD   ($8B68),A

; ---------------------------------------------------------------------------
; FIRST MARSHAL-ANIMATION STAGE
; Draw and update the first stage of the race-ending marshal sequence.
; ---------------------------------------------------------------------------
$E9E8: CD 04 A9    CALL $A904
$E9EB: CD 5E A7    CALL $A75E
$E9EE: CD 73 9F    CALL $9F73

; ---------------------------------------------------------------------------
; Pause for four Spectrum interrupt frames between animation stages.
; ---------------------------------------------------------------------------
$E9F1: 76          HALT
$E9F2: 76          HALT
$E9F3: 76          HALT
$E9F4: 76          HALT

; ---------------------------------------------------------------------------
; SECOND MARSHAL-ANIMATION STAGE
; Draw the alternative marshal stage and prepare a longer 15-frame pause.
; ---------------------------------------------------------------------------
$E9F5: CD 1F A9    CALL $A91F
$E9F8: CD 0F A0    CALL $A00F
$E9FB: 06 0F       LD   B,$0F       ; 15 frames

; ---------------------------------------------------------------------------
; Wait for the 15 interrupt frames counted in B.
; ---------------------------------------------------------------------------
$E9FD: 76          HALT
$E9FE: 10 FD       DJNZ $E9FD

; ---------------------------------------------------------------------------
; Refresh/restore the race display after the marshal-animation sequence.
; ---------------------------------------------------------------------------
$EA00: CD 73 9F    CALL $9F73

; ---------------------------------------------------------------------------
; CORE PER-LAP STATE UPDATE
; Advance car positions, timings, pit-stop and retirement state and the other
; race calculations. The race-control keyboard is sampled again afterwards.
; ---------------------------------------------------------------------------
$EA03: CD 46 AA    CALL $AA46
$EA06: CD A9 E5    CALL $E5A9
$EA09: CD 9F D1    CALL $D19F
$EA0C: CD A2 B4    CALL $B4A2
$EA0F: CD FC D2    CALL $D2FC
$EA12: CD DA D2    CALL $D2DA
$EA15: CD 2D 9A    CALL $9A2D

; ---------------------------------------------------------------------------
; LAP COUNTER AND FINAL-LAP PREPARATION
; $6816 contains the number of laps remaining. Decrement it after completing
; the current lap. During the final two laps, arm the finish animation by
; setting $8B68 to 1.
; ---------------------------------------------------------------------------
$EA18: 21 16 68    LD   HL,$6816
$EA1B: 35          DEC  (HL)
$EA1C: 7E          LD   A,(HL)
$EA1D: FE 03       CP   $03
$EA1F: D2 2A EA    JP   NC,$EA2A    ; three or more laps remain

$EA22: 21 68 8B    LD   HL,$8B68
$EA25: 36 01       LD   (HL),$01    ; arm the finish animation
$EA27: 21 16 68    LD   HL,$6816    ; return HL to the lap counter

; ---------------------------------------------------------------------------
; RACE SIMULATION LOOP END
; If the remaining-lap counter is non-zero, return to $E9C1 for another lap.
; If it is zero, leave the simulation loop and finish the Grand Prix.
; ---------------------------------------------------------------------------
$EA2A: AF          XOR  A
$EA2B: BE          CP   (HL)
$EA2C: C2 C1 E9    JP   NZ,$E9C1

; ---------------------------------------------------------------------------
; GRAND PRIX COMPLETED
; Pause for 100 interrupt frames—approximately two seconds on a 50 Hz
; Spectrum—then show the race results and championship standings.
; ---------------------------------------------------------------------------
$EA2F: 06 64       LD   B,$64
$EA31: 76          HALT
$EA32: 10 FD       DJNZ $EA31

$EA34: CD 7E E4    CALL $E47E       ; sections 17 and 18 and post-race updates

; ---------------------------------------------------------------------------
; GRAND PRIX LOOP END
; After Grands Prix 1–15, run the conditional save check and continue to the
; next race. After Grand Prix 16, call the season-end controller at $E722.
; That controller sets $96A8 and calls $E504 itself, making the end-of-season
; save question automatic.
; ---------------------------------------------------------------------------
$EA37: 3A B2 6B    LD   A,($6BB2)   ; load A with byte stored at $6BB2
$EA3A: FE 10       CP   $10         ; compare with 16
$EA3C: DA B0 E9    JP   C,$E9B0     ; fewer than 16: next Grand Prix
$EA3F: CD 22 E7    CALL $E722       ; sections 19–22: season-end processing

; ---------------------------------------------------------------------------
; SEASON-CONTINUATION DECISION
; $83A5 contains the number of human players. With no human players, continue
; automatically. Otherwise, display the “Another season?” question.
; ---------------------------------------------------------------------------
$EA42: 3A A5 83    LD   A,($83A5)   ; load A with byte stored at $83A5
$EA45: FE 00       CP   $00         ; compare with 0
$EA47: 28 21       JR   Z,$EA6A     ; no human players: continue automatically

; ---------------------------------------------------------------------------
; SECTION 23: ANOTHER SEASON?
; Prepare the display, print the question stored at $8978 and wait for a key.
; Anything other than Y jumps to the Spectrum ROM restart address $0000.
; Pressing Y falls through to the next-season preparation below.
; ---------------------------------------------------------------------------
$EA49: 3E 3F       LD   A,$3F
$EA4B: CD 76 99    CALL $9976
$EA4E: CD 5B 99    CALL $995B
$EA51: 11 78 89    LD   DE,$8978
$EA54: 3E 0A       LD   A,$0A
$EA56: 0E 00       LD   C,$00
$EA58: 06 20       LD   B,$20
$EA5A: CD 28 97    CALL $9728
$EA5D: 3E 07       LD   A,$07
$EA5F: CD 76 99    CALL $9976
$EA62: CD F1 99    CALL $99F1       ; wait for a key
$EA65: FE 59       CP   $59         ; ASCII "Y"
$EA67: C2 00 00    JP   NZ,$0000    ; anything else: restart/exit

; ---------------------------------------------------------------------------
; SEASON LOOP END / NEXT SEASON
; $BF2E updates sixteen season-dependent race values, subtracting 2 from each
; word at $6AE5-$6B04. Then return to $E9A8 to begin the next season.
; ---------------------------------------------------------------------------
$EA6A: CD 2E BF    CALL $BF2E
$EA6D: C3 A8 E9    JP   $E9A8
```

[//]: # (----------------------------------------------------------------------)
[//]: # (                                                                      )
[//]: # (    Part II                                                           )
[//]: # (                                                                      )
[//]: # (----------------------------------------------------------------------)
## Part II: Graphics, text and presentation

### 5. Text tables

All of these are fixed-width, space-padded records. Keep each replacement within
its existing width; making a string longer will overwrite the following record.

#### Driver names

- Range: `$6E87-$6F94` [28295-28564]
- Layout: 27 records x 10 bytes
- Address of record `n`: `$6E87 + n*10`; decimal base: `28295 + n*10`
- Encoding: game character/ASCII-compatible text, padded with spaces

Record zero is blank. The remaining records contain the original names and
special entries, including Lauda, Prost, De Angelis, Alboreto, Piquet, Arnoux,
Warwick, Rosberg, Senna, Mansell, Tambay, Fabi, Patrese, Laffite, Boutsen,
Cheever, De Cesaris, Brundle, Walker, Chambers, Rowland, Munday, Wood,
Wheelhouse, No Driver and Peroni.

#### Team and status names

- Range: `$6F95-$6FDC` [28565-28636]
- Layout: 9 records x 8 bytes
- Address of record `n`: `$6F95 + n*8`; decimal base: `28565 + n*8`

The records are: blank, Brabham, Ferrari, Lotus, Williams, McLaren, Renault,
Injured and Ligier. The final two are status/extra labels, not two more entries
in the six-team colour table.

#### Manager names

- Range: `$6FE3-$701E` [28643-28702]
- Layout: 6 records x 10 bytes
- Address of record `n`: `$6FE3 + n*10`; decimal base: `28643 + n*10`

The final snapshot contains Herb Blash, Piccinini, Peter Warr, P. Collins,
Ron Dennis and Jean Sage.

#### Race and circuit names

| Table             | Range                       | Layout  | Record formula         |
|-------------------|-----------------------------|---------|------------------------|
| Short race names  | `$7025-$70A4` [28709-28836] | 16 x  8 | `$7025 [28709] +  n*8` |
| Circuit names     | `$70A5-$71C4` [28837-29124] | 16 x 18 | `$70A5 [28837] + n*18` |
| Race-display copy | `$9402-$9481` [37890-38017] | 16 x  8 | `$9402 [37890] +  n*8` |

The race-display copy is separate from the main short-name table. In the
supplied final snapshot, the primary table right-aligns short labels, whereas
the display copy centres them within eight bytes; entries that already fill all
eight bytes are identical. If a race name must change everywhere, update both
`$7025-$70A4` [28709-28836] and `$9402-$9481` [37890-38017].

#### Sponsors

- Range: `$8771-$880C` [34673-34828]
- Layout: 13 records x 12 bytes
- Address of record `n`: `$8771 + n*12`; decimal base: `34673 + n*12`

The original set includes Elf, Benetton, Marlboro, J.P.S., Parmalat, Agip,
Unipart, Saudia, Denim, Nordica, Gitanes, ATS Wheels and Skoal.

#### Number and weather text

- `$73C4-$748B` [29636-29835]: 100 right-aligned two-character strings, ` 0`
  through ` 9` and then `10` through `99`.
- `$748E-$760D` [29838-30221]: 12 fixed weather descriptions of 32 bytes each.
- `$7626-$7627` [30246-30247]: the degree glyph followed by the unit letter.
  The final snapshot contains bytes `$27,$43`, displayed as degree-C by the
  game's custom character set.

The generic two-character number table is also how the temperature is printed;
the game does not have a separate table of Fahrenheit or Celsius strings.

### 6. Team colours and Spectrum attribute bytes

A Spectrum screen attribute byte is:

```text
bit 7       FLASH
bit 6       BRIGHT
bits 5-3    PAPER colour
bits 2-0    INK colour
```

Colour numbers are:

| Value | Colour  | Value | Colour |
|------:|---------|------:|--------|
|     0 | black   |     4 | green  |
|     1 | blue    |     5 | cyan   |
|     2 | red     |     6 | yellow |
|     3 | magenta |     7 | white  |

The main six-byte team palette is at `$6FDD-$6FE2` [28637-28642].
In the final snapshot it is:

```text
01 02 00 04 03 06
```

This maps the six normal team slots to blue, red, black, green, magenta and
yellow: Brabham, Ferrari, Lotus, Williams, McLaren and Renault.

Changing this palette affects places where the game asks for a team's basic
colour. It does not automatically recolour every car picture: the detailed
side-view and top-view pictures have their own attribute maps.

Relevant palette-selection routine: `$96AA` [38570].

### 7. Side-view car graphics

The six side-view cars share one monochrome bitmap and are differentiated by
separate colour attributes.

- Shared bitmap: `$6C18-$6CB7` [27672-27831], 160 bytes
- Image size: 80 x 16 pixels, or 10 x 2 attribute cells
- Attribute-map size: 20 bytes per team

| Team     | Attribute map               |
|----------|-----------------------------|
| Brabham  | `$6CB8-$6CCB` [27832-27851] |
| Ferrari  | `$6CCC-$6CDF` [27852-27871] |
| Lotus    | `$6CE0-$6CF3` [27872-27891] |
| Williams | `$6CF4-$6D07` [27892-27911] |
| McLaren  | `$6D08-$6D1B` [27912-27931] |
| Renault  | `$6D1C-$6D2F` [27932-27951] |

For team slots 1-6:

```text
attribute map = $6CB8 [27832] + (team_slot - 1)*20
```

Other related data:

- `$7DB0-$7DC7` [32176-32199]: twelve little-endian pointers to car-number glyphs;
- `$7DC8-$7E27` [32200-32295]: the number glyph bitmaps;
- `$6DE0-$6E6F` [28128-28271] and `$84C0-$854F` [33984-34127]:
  object records that refer to the car data.

Relevant drawing/composition code is around `$A163` [41315], `$A188` [41352]
and `$A346` [41798].

### 8. Top-view car graphics

As with the side view, the top-view cars share a bitmap and use one attribute
map per team.

- Twelve car/driver records: `$7E40-$7ECF` [32320-32463], 12 records x 12 bytes
- Shared top-view bitmap: `$7EDC-$8093` [32476-32915], 440 bytes
- Image size: 88 x 40 pixels, or 11 x 5 attribute cells
- Attribute-map size: 55 bytes per team

| Team     | Attribute map               |
|----------|-----------------------------|
| Brabham  | `$8094-$80CA` [32916-32970] |
| Ferrari  | `$80CB-$8101` [32971-33025] |
| Lotus    | `$8102-$8138` [33026-33080] |
| Williams | `$8139-$816F` [33081-33135] |
| McLaren  | `$8170-$81A6` [33136-33190] |
| Renault  | `$81A7-$81DD` [33191-33245] |

For team slots 1-6:

```text
attribute map = $8094 [32916] + (team_slot - 1)*55
```

The shared bitmap is stored cell-by-cell rather than as an ordinary linear
image. The original blitter also draws its cell rows from bottom to top. A raw
image viewer will therefore make these bytes look like random pixels unless
it reproduces the game's storage order.

Relevant code:

- `$A188` [41352]: original sprite/attribute blitter;
- `$A215` [41493]: clipping and setup;
- `$A8AA` [43178]: record-driven car drawing.

#### Narrow car-number glyphs

The shared car-number bitmap table occupies `$7DC8-$7E27` [32200-32295],
with one eight-byte glyph for each car number. The preceding table at
`$7DB0-$7DC7` [32176-32199] contains twelve little-endian pointers to those
glyphs. The same glyphs are used when composing cars in the top and side
views; the larger starting-grid number boxes in chapter 9 are separate
artwork.

The glyphs for all twelve cars were narrowed and redrawn as one consistent
set. Their narrow forms fit the available car panels, including the two-digit
numbers. Their final locations and bytes are:

| Car | Address                     | Final bytes               |
|----:|-----------------------------|---------------------------|
|   1 | `$7DC8-$7DCF` [32200-32207] | `FF FD F9 FD FD FD FD FF` |
|   2 | `$7DD0-$7DD7` [32208-32215] | `FF F3 ED FD F3 EF E1 FF` |
|   3 | `$7DD8-$7DDF` [32216-32223] | `FF F3 ED FB FD ED F3 FF` |
|   4 | `$7DE0-$7DE7` [32224-32231] | `FF EF EF EB E1 FB FB FF` |
|   5 | `$7DE8-$7DEF` [32232-32239] | `FF E1 EF E3 FD ED F3 FF` |
|   6 | `$7DF0-$7DF7` [32240-32247] | `FF F3 EF E3 ED ED F3 FF` |
|   7 | `$7DF8-$7DFF` [32248-32255] | `FF E1 FD FB F7 F7 F7 FF` |
|   8 | `$7E00-$7E07` [32256-32263] | `FF F3 ED F3 ED ED F3 FF` |
|   9 | `$7E08-$7E0F` [32264-32271] | `FF F3 ED ED F1 FD F3 FF` |
|  10 | `$7E10-$7E17` [32272-32279] | `FF D9 96 D6 D6 D6 D9 FF` |
|  11 | `$7E18-$7E1F` [32280-32287] | `FF ED C9 ED ED ED ED FF` |
|  12 | `$7E20-$7E27` [32288-32295] | `FF D9 96 DE D9 D7 D0 FF` |

These bitmaps use inverse storage: a cleared bit forms a visible dark stroke,
while a set bit leaves the surrounding number panel unchanged. The change is
confined to the 96-byte glyph table; all unrelated data remain unchanged.

#### Shared engine symmetry adjustment

The engine character is part of the shared top-view bitmap, so one edit updates
all six team renderings.

- Character range: `$7FC4-$7FCB` [32708-32715]
- Final bytes: `6D 6D FF 24 24 FF 6D 6D`
- Bytes changed relative to the previous documented snapshot:
  - `$7FC5` [32709]: `$FF` to `$6D`
  - `$7FC6` [32710]: `$24` to `$FF`
  - `$7FC8` [32712]: `$DB` to `$24`

After the game's INK/PAPER interpretation, the visible 8 x 8 pattern is
horizontally symmetric:

```text
#..#..#.
#..#..#.
........
##.##.##
##.##.##
........
#..#..#.
#..#..#.
```

#### Shared rear-suspension symmetry adjustment

The upper suspension cell used as the reference is `$801C-$8023`
[32796-32803]:

```text
81 83 8C B0 E0 FF 92 24
```

The lower cell at `$7F6C-$7F73` [32620-32627] is now the exact top-to-bottom
row reversal of the upper cell, producing a mirror across the car's horizontal
centreline:

```text
24 92 FF E0 B0 8C 83 81
```

The adjustment changes only three bytes:

| Address         | Previous | Final |
|-----------------|---------:|------:|
| `$7F70` [32624] |   `$9C`  | `$B0` |
| `$7F71` [32625] |   `$83`  | `$8C` |
| `$7F72` [32626] |   `$80`  | `$83` |

Both symmetry adjustments affect only the shared top-view bitmap. No colour
attributes, code, text or game-state bytes were changed.

### 9. Starting-grid number boxes

- Range: `$8FD3-$9182` [36819-37250]
- Layout: 12 records x 36 bytes (`$24` bytes)
- Record for car number `n`: `$8FD3 + (n-1)*$24`; decimal address: `36819 + (n-1)*36`
- Bytes 0-31 are four consecutive 8 x 8 bitmap cells. The renderer begins with the lower pair of cells and then draws the upper pair.
- The last four bytes, at `record+$20`, are the 2 x 2 attribute map. All four attributes currently have the same value within each record.

The complete record map is:

| Car | Full record                 | Bitmap                      | Attributes                 | Value     |
|----:|-----------------------------|-----------------------------|----------------------------|-----------|
|   1 | `$8FD3-$8FF6` [36819-36854] | `$8FD3-$8FF2` [36819-36850] | `$8FF3-$8FF6`[36851-36854] | `$4F` x 4 |
|   2 | `$8FF7-$901A` [36855-36890] | `$8FF7-$9016` [36855-36886] | `$9017-$901A`[36887-36890] | `$4F` x 4 |
|   3 | `$901B-$903E` [36891-36926] | `$901B-$903A` [36891-36922] | `$903B-$903E`[36923-36926] | `$57` x 4 |
|   4 | `$903F-$9062` [36927-36962] | `$903F-$905E` [36927-36958] | `$905F-$9062`[36959-36962] | `$57` x 4 |
|   5 | `$9063-$9086` [36963-36998] | `$9063-$9082` [36963-36994] | `$9083-$9086`[36995-36998] | `$45` x 4 |
|   6 | `$9087-$90AA` [36999-37034] | `$9087-$90A6` [36999-37030] | `$90A7-$90AA`[37031-37034] | `$45` x 4 |
|   7 | `$90AB-$90CE` [37035-37070] | `$90AB-$90CA` [37035-37066] | `$90CB-$90CE`[37067-37070] | `$60` x 4 |
|   8 | `$90CF-$90F2` [37071-37106] | `$90CF-$90EE` [37071-37102] | `$90EF-$90F2`[37103-37106] | `$60` x 4 |
|   9 | `$90F3-$9116` [37107-37142] | `$90F3-$9112` [37107-37138] | `$9113-$9116`[37139-37142] | `$58` x 4 |
|  10 | `$9117-$913A` [37143-37178] | `$9117-$9136` [37143-37174] | `$9137-$913A`[37175-37178] | `$58` x 4 |
|  11 | `$913B-$915E` [37179-37214] | `$913B-$915A` [37179-37210] | `$915B-$915E`[37211-37214] | `$70` x 4 |
|  12 | `$915F-$9182` [37215-37250] | `$915F-$917E` [37215-37246] | `$917F-$9182`[37247-37250] | `$70` x 4 |

The attribute meanings are:

| Cars  | Attribute | Meaning                               |
|------:|----------:|---------------------------------------|
|  1- 2 |   `$4F`   | BRIGHT white INK 7 on blue PAPER 1    |
|  3- 4 |   `$57`   | BRIGHT white INK 7 on red PAPER 2     |
|  5- 6 |   `$45`   | BRIGHT cyan INK 5 on black PAPER 0    |
|  7- 8 |   `$60`   | BRIGHT black INK 0 on green PAPER 4   |
|  9-10 |   `$58`   | BRIGHT black INK 0 on magenta PAPER 3 |
| 11-12 |   `$70`   | BRIGHT black INK 0 on yellow PAPER 6  |

Earlier work changed cars 11 and 12 from the cyan attribute `$68` to yellow
`$70`, matching their current team palette. Their bitmap records retained a
different, two-pixel-thick frame. In the final snapshot, the 32 bitmap bytes at
`$913B-$915A` and `$915F-$917E` use the same one-pixel frame geometry as records
1-10. The two-digit numerals and all eight `$70` attribute bytes are retained.

This adjustment affected only the two 32-byte bitmap records. No code,
attributes, other number boxes or unrelated artwork were changed.

Relevant code:

- `$D05A` [53338]: full starting-grid display;
- `$D0E7` [53479]: grid header;
- `$D11E` [53534]: individual number box.

### 10. Championship points

- Table: `$7B96-$7B9D` [31638-31645]
- Eight bytes, one for each finishing place considered by the scoring loop
- Final bytes: `09 06 04 03 02 01 00 00`

Therefore the final scoring system is:

| Finish | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|-------:|--:|--:|--:|--:|--:|--:|--:|--:|
| Points | 9 | 6 | 4 | 3 | 2 | 1 | 0 | 0 |

The principal scoring routine is `$CE54-$CE99` [52820-52889].
It reads this table and updates both:

- constructor totals at `$6910-$6915` [26896-26901];
- active driver totals at `$6948-$695F` [26952-26975].

The table is also referenced by a secondary management/calculation path around
`$B9E9` [47593], so editing the single table keeps the game's calculations
consistent. The point totals are mutable run-time data and are reset by the
new-season logic; the table at `$7B96` [31638] is the rule to edit.

### 11. Original 1985 race data

The restored numeric race-data block occupies `$6AD5-$6BA4` [27349-27556]:

| Range (hex)   | Range (decimal) | Layout         | Meaning                                |
|---------------|----------------:|---------------:|----------------------------------------|
| `$6AD5-$6AE4` | 27349-27364     | 16 x 1 byte    | number of laps                         |
| `$6AE5-$6B04` | 27365-27396     | 16 x 16-bit LE | baseline race timing/difficulty values |
| `$6B05-$6B24` | 27397-27428     | 16 x 16-bit LE | lap-record times                       |
| `$6B25-$6B34` | 27429-27444     | 16 x 1 byte    | lap-record holder driver IDs           |
| `$6B35-$6B44` | 27445-27460     | 16 x 1 byte    | lap-record team IDs                    |
| `$6B45-$6B54` | 27461-27476     | 16 x 1 byte    | previous-winner driver IDs             |
| `$6B55-$6B64` | 27477-27492     | 16 x 1 byte    | previous-winner team IDs               |
| `$6B65-$6B84` | 27493-27524     | 16 x 16-bit LE | circuit lengths, in miles              |
| `$6B85-$6BA4` | 27525-27556     | 16 x 16-bit LE | lap-record years                       |

`16-bit LE` means little-endian: the low byte comes first.

The restored lap counts, in calendar order, are:

```text
61, 75, 70, 60, 79, 76, 70, 63,
67, 71, 44, 51, 71, 51, 67, 70
```

The on-screen summary has a separate formatted copy at `$9482-$94A5` [38018-38053]:
the word `Laps` followed by sixteen two-digit text values. When changing the
schedule, update both the binary lap-count table and this display row.

#### Automated schedule editing with `--races`

The companion `Tweak-F1.py` script accepts `--races=races.txt` (equivalently,
`--races races.txt`). The file must contain exactly 16 nonblank, non-comment
entries. Each entry has three mandatory fields separated by vertical bars:

```text
Phoenix | Phoenix Street    | 81
Brazil  | Interlagos        | 71
SMarino | Imola             | 61
Monaco  | Circuit de Monaco | 78
```

The complete file must contain another 12 entries. Race and circuit names must
use ASCII. A race name may occupy at most 8 bytes; the script right-aligns
shorter names in the primary table and centres them in the separate
race-display copy. A circuit name may occupy at most 18 bytes; the script
left-aligns shorter names with trailing spaces, matching the original
representation. Lap counts must be integers from 1 through 99 because the
display allocates exactly two characters per value.

The earlier two-field `RACE LAPS` format is intentionally rejected: accepting
it would leave an old circuit name paired with a new race. For every valid
schedule, the script writes all five required regions:

| Data written                | Range (hex)   | Range (dec) | Encoding                                 |
|-----------------------------|---------------|-------------|------------------------------------------|
| Primary short race names    | `$7025-$70A4` | 28709-28836 | 16 right-aligned ASCII records x 8 bytes |
| Circuit names               | `$70A5-$71C4` | 28837-29124 | 16 left-aligned ASCII records x 18 bytes |
| Binary lap counts           | `$6AD5-$6AE4` | 27349-27364 | 16 unsigned one-byte values              |
| Race-display name copy      | `$9402-$9481` | 37890-38017 | 16 centred ASCII records x 8 bytes       |
| Race-display lap-count copy | `$9486-$94A5` | 38022-38053 | 16 two-digit ASCII values                |

The four-byte `Laps` label at `$9482-$9485` [38018-38021] is deliberately
preserved. The patcher's changed-byte allowlist rejects a result if schedule
editing modifies any byte outside the five regions above.

`--races` now changes short race labels, circuit names and lap counts. It still
does **not** rewrite the slot-associated timing/difficulty values, lap records,
record holders, previous winners, circuit lengths or record years at
`$6AE5-$6BA4` [27365-27556]. Those records therefore remain attached to their
original calendar positions unless separately edited.

The distance label at `$8FCA-$8FCE` [36810-36814] is `miles` in the final
snapshot.

Relevant code:

- `$9CB6` [40118]: circuit/lap header;
- `$A41C` [42012]: track, weather and temperature section;
- `$C7EC` [51180]: race initialisation and lap/timing-data reads;
- `$CBA9` [52137]: full track report;
- `$CBD0` [52176]: record and previous-winner fields.

### 12. Season years and previous winners

The current season is formed from a base year plus the season-offset byte at
`$8BDC` [35804]. That offset is incremented at `$C90E` [51470] when a season
advances.

The final snapshot restores these immediate year constants:

| Instruction address | Bytes      | Meaning                            |
|---------------------|------------|------------------------------------|
|   `$9854` [38996]   | `21 C0 07` | `LD HL,1984`                       |
|   `$CC93` [52371]   | `21 BF 07` | `LD HL,1983`, previous-winner base |
|   `$CCF0` [52464]   | `21 C0 07` | `LD HL,1984`                       |
|   `$E64C` [58956]   | `21 C0 07` | `LD HL,1984`                       |
|   `$E8D7` [59607]   | `21 C0 07` | `LD HL,1984`                       |

With the game's season offset applied, these produce the intended 1985 season
and 1984 previous-winner year rather than the MOD2020-era dates.

### 13. Other graphics and display memory

#### Live Spectrum screen

- Bitmap: `$4000-$57FF` [16384-22527]
- Attributes: `$5800-$5AFF` [22528-23295]

These bytes are merely the screen that happened to be visible when the snapshot
was saved. They are not the authoritative source for all game artwork.

##### Initial splash screen and bottom prompt

In this `.sna`, the initial splash screen is stored directly as the live
Spectrum screen: bitmap `$4000-$57FF` [16384-22527] and attributes `$5800-$5AFF`
[22528-23295]. A 48K snapshot restores these bytes verbatim, so this is the
image displayed immediately after loading; no separate full-screen copy is
needed for that initial display. This does not imply that every later game
screen is stored there, because the same screen RAM is continually reused.

The rasterised `Press 'L' to Load Previous Game` prompt occupies the final
32-character row, screen x=0 through x=255 and y=184 through y=191.
Its 256 bitmap bytes are interleaved as follows:

| Scanline | Address range               | SNA file-offset range |
|---------:|----------------------------:|----------------------:|
|        0 | `$50E0-$50FF` [20704-20735] |      [4347-4378]      |
|        1 | `$51E0-$51FF` [20960-20991] |      [4603-4634]      |
|        2 | `$52E0-$52FF` [21216-21247] |      [4859-4890]      |
|        3 | `$53E0-$53FF` [21472-21503] |      [5115-5146]      |
|        4 | `$54E0-$54FF` [21728-21759] |      [5371-5402]      |
|        5 | `$55E0-$55FF` [21984-22015] |      [5627-5658]      |
|        6 | `$56E0-$56FF` [22240-22271] |      [5883-5914]      |
|        7 | `$57E0-$57FF` [22496-22527] |      [6139-6170]      |

Its 32 attributes are `$5AE0-$5AFF` [23264-23295]; SNA file offsets [6907-6938].
Every attribute remains `$07`, meaning white INK 7 on black PAPER 0 with
BRIGHT clear.

In the final snapshot this row is rebuilt from the installed custom-font glyphs
while retaining the exact text, position and attributes. The change affects 120
bitmap-byte values; the remainder of the splash screen and all non-screen
memory are untouched.

#### Custom character set

The active font/character-set base is `$E9FE` [59902]. A character's eight
bitmap bytes are at:

```text
$E9FE [59902] + 8*character_code
```

Printable ASCII begins with character code 32 at `$EAFE` [60158]. The injected
routines and constants at `$EA70-$EAFB` [60016-60155] occupy control-code
storage below that point; they do not overwrite any printable letter, number or
punctuation glyph. In the final snapshot only `$EAFC-$EAFD` [60156-60157]
remains zero-filled. As noted in §4, the exact pre-patch contents differ
between the original 1985 and MOD2020-derived code layouts, so only the
specifically documented ranges should be treated as available.

Main text-printing routine: `$9728` [38696]. Other useful formatters include
`$9ADF` [39647] for numeric output and `$9756` [38742] for times.

#### Pit and management direction arrows

##### Flashing left pit arrow

The left-pointing arrow displayed immediately to the right of the top-view car
in the pits is an 8 x 8 bitmap stored at `$9568-$956F` [38248-38255]; SNA file
offsets [21891-21898]. The original bytes are:

```text
30 60 C0 FF FF C0 60 30
```

Code at `$B3C5-$B3D5` [46021-46037] draws it at screen x=160 through x=167 and
y=120 through y=127. Because Spectrum bitmap scanlines are interleaved, the
live-screen destination bytes are `$48F4`, `$49F4`, `$4AF4`, `$4BF4`, `$4CF4`,
`$4DF4`, `$4EF4` and `$4FF4` [18676, 18932, 19188, 19444, 19700, 19956, 20212
and 20468].

The corresponding screen attribute is `$59F4` [23028]. The original routine
loaded `$B8` at `$B3D1` [46033], selecting FLASH 1, BRIGHT 0, white PAPER 7
and black INK 0. Consequently, the apparently broken alternate image was not
a second arrow: it was the same bitmap with INK and PAPER exchanged by the
Spectrum's hardware flashing.

The final snapshot retains the flashing attribute but replaces only the eight
source-bitmap bytes with the user-supplied symmetrical design:

```text
00 10 30 7E 7E 30 10 00
```

Exactly eight consecutive byte values define this replacement; all code,
attributes and unrelated artwork remain untouched.

##### Shared right management/menu arrow

The separate right-pointing cursor seen beside `DRIVER` is stored at
`$9643-$964A` [38467-38474]; SNA file offsets [22110-22117].
Its original bitmap is:

```text
08 0C 06 FF FF 06 0C 08
```

It is referenced by at least three drawing paths, with `LD DE,$9643`
instructions beginning at `$9BDC`, `$9BFE` and `$E326` [39900, 39934 and 58150].
Therefore, changing this single source bitmap consistently changes its several
cursor uses.

In the captured two-car management screen, this arrow appears at screen x=0
through x=7 and y=32 through y=39. Its interleaved live-screen bytes are
`$4080`, `$4180`, `$4280`, `$4380`, `$4480`, `$4580`, `$4680` and `$4780`
[16512, 16768, 17024, 17280, 17536, 17792, 18048 and 18304].
The captured attribute at `$5880` [22656] is `$70`: FLASH 0, BRIGHT 1, yellow
PAPER 6 and black INK 0. This attribute belongs to that particular screen use
rather than to the shared source bitmap.

The final snapshot replaces the right-arrow bytes with the horizontal mirror
of the new left arrow:

```text
00 08 0C 7E 7E 0C 08 00
```

##### Final paired-arrow configuration

The final configuration consists of two related changes:

1. `$9643-$964A` [38467-38474] receives the eight-byte mirrored right-arrow
   bitmap above.
2. The attribute immediate at `$B3D1` [46033] changes from `$B8` to `$F2`.
   `$F2` selects FLASH 1, BRIGHT 1, yellow PAPER 6 and red INK 2, so the left
   pit arrow flashes between bright red-on-yellow and bright yellow-on-red.

Together, the two arrow bitmaps and the colour change account for seventeen
changed byte values. All unrelated code, data, attributes and artwork remain
untouched.

#### Faster car-management progress bars

The animated Driver, Engine, Chassis and Crew bars on the two-car management
screen are drawn one 8-pixel column at a time by the routine originally
occupying `$E21C-$E232` [57884-57906]. The bitmap pattern for each column comes
from `$9638` [38456]. This display routine does not calculate the underlying
car or driver values; it only visualises them.

The original routine waited three 50 Hz video frames after every column:

```text
LD B,3
delay:
HALT
DJNZ delay
```

That is approximately 60 milliseconds of deliberate delay per 8-pixel column.
Four columns therefore consumed twelve frames, or approximately 240
milliseconds.

The first three bytes at `$E21C-$E21E` [57884-57886] were changed from:

```text
C5 D5 E5
```

to a jump into verified unused space:

```text
C3 99 EA              ; JP $EA99, decimal address 60057
```

The 26-byte replacement renderer occupies `$EA99-$EAB2` [60057-60082]:

```text
C5 D5 E5 06 08 1A 77 24 13 10 FA E1 D1 C1 23
F5 78 E6 03 28 01 76 F1 10 E7 C9
```

It performs the same eight-byte vertical copy and advances to the same next
screen column. It waits one frame after three of every four columns and omits
the wait after the fourth. Thus, for each complete group of four columns:

```text
original: 4 columns * 3 frames = 12 frames
patched:  3 waits   * 1 frame  =  3 frames
speed-up: 12 / 3 = 4 times
```

Very short partial groups are between three and four times faster; ordinary
long bars are approximately four times faster. `AF`, `BC`, `DE`, the
screen-address progression and all copied pixels are preserved. Driver ability,
engine/chassis condition, crew values, efficiency calculations and game timing
outside this visual animation are untouched.

#### Cached scene artwork

| Range                       | Purpose                    |
|-----------------------------|----------------------------|
| `$EDFE-$F5FD` [60926-62973] | pit/garage bitmap cache    |
| `$F5FE-$F6FD` [62974-63229] | pit/garage attribute cache |
| `$F6FE-$FEFD` [63230-65277] | race-scene bitmap cache    |
| `$FEFE-$FFFD` [65278-65533] | race-scene attribute cache |

The pit/garage cache is copied by code around `$B55E` [46430]; the race-scene
cache is copied around `$9F73` [40819]. The moving race-scene sprite/blimp data
is at `$91B8-$922F` [37304-37423], with associated drawing parameters around
`$9FB7-$A062` [40887-41058].

##### Pit/garage `GOODYEAR` banner

The 80 x 8-pixel `GOODYEAR` banner occupies ten bytes on each of eight
interleaved Spectrum bitmap scanlines inside the pit/garage cache. Spectrum
bitmap rows within one character row are separated by 256 bytes, so the banner
is not one contiguous 80-byte range:

| Scanline | Range                       | SNA file-offset range |
|---------:|-----------------------------|-----------------------|
|        0 | `$EE14-$EE1D` [60948-60957] |     [44591-44600]     |
|        1 | `$EF14-$EF1D` [61204-61213] |     [44847-44856]     |
|        2 | `$F014-$F01D` [61460-61469] |     [45103-45112]     |
|        3 | `$F114-$F11D` [61716-61725] |     [45359-45368]     |
|        4 | `$F214-$F21D` [61972-61981] |     [45615-45624]     |
|        5 | `$F314-$F31D` [62228-62237] |     [45871-45880]     |
|        6 | `$F414-$F41D` [62484-62493] |     [46127-46136]     |
|        7 | `$F514-$F51D` [62740-62749] |     [46383-46392]     |

The ten corresponding attribute cells are `$F614-$F61D` [62996-63005]. Every
cell contains `$4F`: BRIGHT 1, white INK 7 and blue PAPER 1. Consequently, set
bitmap bits appear white and clear bits appear blue; replacing the lettering
requires changing only the 80 bitmap bytes above.

The final snapshot replaces the original block-letter banner with the supplied
italic 80 x 8 bitmap. Sixty-three byte values differ because seventeen
replacement bytes already matched the original data. No attribute, code or
unrelated bitmap byte changes.

##### Pit/garage `Mobil` banner

The original `Mobil` artwork occupies five 8-pixel cells, screen x=8 through
x=47, on the same eight interleaved cache scanlines. Its 40 bitmap bytes are:

| Scanline | Range                       | SNA file-offset range |
|---------:|-----------------------------|-----------------------|
|        0 | `$EDFF-$EE03` [60927-60931] |     [44570-44574]     |
|        1 | `$EEFF-$EF03` [61183-61187] |     [44826-44830]     |
|        2 | `$EFFF-$F003` [61439-61443] |     [45082-45086]     |
|        3 | `$F0FF-$F103` [61695-61699] |     [45338-45342]     |
|        4 | `$F1FF-$F203` [61951-61955] |     [45594-45598]     |
|        5 | `$F2FF-$F303` [62207-62211] |     [45850-45854]     |
|        6 | `$F3FF-$F403` [62463-62467] |     [46106-46110]     |
|        7 | `$F4FF-$F503` [62719-62723] |     [46362-46366]     |

The corresponding five attributes at `$F5FF-$F603` [62975-62979] are
`$79 $7A $79 $79 $79`. Each has bright white PAPER 7; the first, third,
fourth and fifth cells use blue INK 1, while the second cell, screen x=16
through x=23, uses red INK 2.

The supplied replacement is 29 x 8 pixels. It is placed at x=8 through x=36
and the remainder of the old five-cell area is cleared to white. Its red `o`
pixels land at x=17 through x=22, wholly inside the existing red attribute
cell; all blue pixels remain outside that cell. This preserves the attributes
unchanged and avoids Spectrum colour clash.

The final snapshot also contains this replacement Mobil artwork. Twenty-nine
bitmap-byte values differ from the original Mobil image; no attributes, code
or unrelated artwork change.

##### `Mobil`/`Time` separator cell

The 8 x 8 separator immediately after the Mobil area is screen x=48 through
x=55. Its eight interleaved bitmap bytes are:

| Scanline | Address         | SNA file offset |
|---------:|-----------------|-----------------|
|        0 | `$EE04` [60932] |     [44575]     |
|        1 | `$EF04` [61188] |     [44831]     |
|        2 | `$F004` [61444] |     [45087]     |
|        3 | `$F104` [61700] |     [45343]     |
|        4 | `$F204` [61956] |     [45599]     |
|        5 | `$F304` [62212] |     [45855]     |
|        6 | `$F404` [62468] |     [46111]     |
|        7 | `$F504` [62724] |     [46367]     |

In the earlier `Mobil`/`Time` arrangement, the cell's attribute at `$F604`
[62980]; SNA file offset [46623] was `$78`, meaning black INK 0 on bright-white
PAPER 7. The original bitmap byte `$0F` on every scanline therefore drew four
white pixels followed by four black pixels. Replacing all eight bytes with
`$FF` made the entire cell black without changing that attribute.

That all-black separator was a development step, not the final state: it was
subsequently incorporated into and superseded by the six-cell `ELAPSED` label
below. In the final snapshot, `$F604` is therefore `$47`, not `$78`.

##### Pit/garage `ELAPSED` label

The final snapshot replaces the black Mobil separator, the four cells spelling
`Time`, and the following blank cell with one six-cell, 48 x 8-pixel black
label. The supplied 42 x 8 `ELAPSED` bitmap is placed six pixels to the right
of its initially centred position. Its visible white artwork therefore occupies
screen x=61 through x=94 within the six-cell strip at x=48 through x=95. This
leaves one clear pixel before the timer's drawing area. The strip is rebuilt
directly from the source bitmap so that all four middle pixels of the `D`'s
right-hand vertical stroke are retained. The live timer and all later header
cells remain untouched.

| Scanline | Address range               | SNA file-offset range |
|---------:|-----------------------------|-----------------------|
|        0 | `$EE04-$EE09` [60932-60937] |     [44575-44580]     |
|        1 | `$EF04-$EF09` [61188-61193] |     [44831-44836]     |
|        2 | `$F004-$F009` [61444-61449] |     [45087-45092]     |
|        3 | `$F104-$F109` [61700-61705] |     [45343-45348]     |
|        4 | `$F204-$F209` [61956-61961] |     [45599-45604]     |
|        5 | `$F304-$F309` [62212-62217] |     [45855-45860]     |
|        6 | `$F404-$F409` [62468-62473] |     [46111-46116]     |
|        7 | `$F504-$F509` [62724-62729] |     [46367-46372]     |

The six attributes at `$F604-$F609` [62980-62985]; SNA file offsets
[46623-46628] are all `$47`, meaning bright-white INK 7 on black PAPER 0.
The `ELAPSED` adjustment changes 38 bitmap-byte values and one attribute
value compared with the earlier `Time`/separator arrangement.

##### Race-scene country-name placeholder

The country name printed on the blue banner above the yellow `GRAND PRIX`
artwork is an eight-character, 64 x 8-pixel field. In the original race-scene
cache, the field underneath that text was not empty: it contained a bright
blue-and-yellow one-pixel chequerboard.

The eight interleaved bitmap scanlines are:

| Scanline | Address range               | SNA file-offset range | Earlier bytes       | Final bytes |
|---------:|-----------------------------|-----------------------|---------------------|-------------|
|        0 | `$F701-$F708` [63233-63240] |     [46876-46883]     | 8 x `$55`           | 8 x `$00`   |
|        1 | `$F801-$F808` [63489-63496] |     [47132-47139]     | 8 x `$AA`           | 8 x `$00`   |
|        2 | `$F901-$F908` [63745-63752] |     [47388-47395]     | 8 x `$55`           | 8 x `$00`   |
|        3 | `$FA01-$FA08` [64001-64008] |     [47644-47651]     | 8 x `$AA`           | 8 x `$00`   |
|        4 | `$FB01-$FB08` [64257-64264] |     [47900-47907]     | 8 x `$55`           | 8 x `$00`   |
|        5 | `$FC01-$FC08` [64513-64520] |     [48156-48163]     | 8 x `$AA`           | 8 x `$00`   |
|        6 | `$FD01-$FD08` [64769-64776] |     [48412-48419]     | 8 x `$55`           | 8 x `$00`   |
|        7 | `$FE01-$FE08` [65025-65032] |     [48668-48675]     | 8 x `$AA`           | 8 x `$00`   |

The corresponding eight attributes at `$FF01-$FF08` [65281-65288]; SNA file
offsets [48924-48931] remain `$4E`: BRIGHT 1, yellow INK 6 and blue PAPER 1.

Routine `$9F73` [40819] first copies the complete race-scene bitmap cache from
`$F6FE` [63230] to `$4800` [18432], followed by the attribute cache from
`$FEFE` [65278] to `$5900` [22784]. The chequerboard consequently appears in
the live bitmap at `$4803-$480A`, `$4903-$490A`, ..., `$4F03-$4F0A`, with its
attributes at `$5903-$590A` [22787-22794].

Only after both cache copies does code beginning at `$9F95` [40853] select the
current eight-character race-name record from `$9402-$9481` [37890-38017].
The call at `$9FAB` [40875] then uses the shared glyph renderer at `$9EC5`
[40645] to overwrite the chequerboard with the country name. The cache copies
take roughly 14 milliseconds on a 3.5 MHz Spectrum, so the placeholder can
remain visible for nearly one video frame.

Direct calls to the cache-and-country-name routine occur at `$A910` [43280],
`$AB63` [43875], `$B752` [46930], `$E9EE` [59886] and `$EA00` [59904]. They
belong to race-scene setup, race-start restoration and end-of-race paths; the
car-movement loop at `$B83A` [47162] does not call this routine. It is therefore
not an every-lap redraw, although several major race-state changes can expose
the placeholder.

The final snapshot changes only the 64 alternating `$55`/`$AA` bitmap bytes to
`$00`. A cache restoration now briefly shows a plain blue banner before the
country name is written. The attributes, country-name records, text renderer
and all executable code remain unchanged.

##### Race-scene `GRAND PRIX` banner

The yellow `GRAND PRIX` raster on the blue banner is 80 x 8 pixels at
race-cache-local screen x=16 through x=95 and y=8 through y=15. It is
independent of the white `GRAND PRIX` lettering on the black timing tower.
The ten bitmap bytes on each scanline are interleaved as follows:

| Scanline | Address range               | SNA file-offset range |
|---------:|-----------------------------|-----------------------|
|        0 | `$F720-$F729` [63264-63273] |     [46907-46916]     |
|        1 | `$F820-$F829` [63520-63529] |     [47163-47172]     |
|        2 | `$F920-$F929` [63776-63785] |     [47419-47428]     |
|        3 | `$FA20-$FA29` [64032-64041] |     [47675-47684]     |
|        4 | `$FB20-$FB29` [64288-64297] |     [47931-47940]     |
|        5 | `$FC20-$FC29` [64544-64553] |     [48187-48196]     |
|        6 | `$FD20-$FD29` [64800-64809] |     [48443-48452]     |
|        7 | `$FE20-$FE29` [65056-65065] |     [48699-48708]     |

The ten corresponding attributes at `$FF20-$FF29` [65312-65321]; SNA file
offsets [48955-48964] remain `$4E`: BRIGHT 1, yellow INK 6 and blue PAPER 1.

In the final snapshot these ten cells are rebuilt from the installed custom-font
glyphs for `GRAND PRIX`, without changing their positions or attributes.
Exactly 43 bitmap-byte values differ from the earlier raster; the timing-tower
lettering and all unrelated data remain untouched.

##### Race-scene `Pirelli` panel

The rectangular Pirelli advertising panel is exactly 7 x 3 character cells,
or 56 x 24 pixels, at race-cache-local screen x=144 through x=199 and y=0
through y=23. The two cells immediately to its left, x=128 through x=143,
belong to the diagonal/structural transition and are not part of this panel.

Its seven bitmap bytes on each scanline are interleaved as follows:

| Scanline | Address range               | SNA file-offset range |
|---------:|-----------------------------|-----------------------|
|        0 | `$F710-$F716` [63248-63254] |     [46891-46897]     |
|        1 | `$F810-$F816` [63504-63510] |     [47147-47153]     |
|        2 | `$F910-$F916` [63760-63766] |     [47403-47409]     |
|        3 | `$FA10-$FA16` [64016-64022] |     [47659-47665]     |
|        4 | `$FB10-$FB16` [64272-64278] |     [47915-47921]     |
|        5 | `$FC10-$FC16` [64528-64534] |     [48171-48177]     |
|        6 | `$FD10-$FD16` [64784-64790] |     [48427-48433]     |
|        7 | `$FE10-$FE16` [65040-65046] |     [48683-48689]     |
|        8 | `$F730-$F736` [63280-63286] |     [46923-46929]     |
|        9 | `$F830-$F836` [63536-63542] |     [47179-47185]     |
|       10 | `$F930-$F936` [63792-63798] |     [47435-47441]     |
|       11 | `$FA30-$FA36` [64048-64054] |     [47691-47697]     |
|       12 | `$FB30-$FB36` [64304-64310] |     [47947-47953]     |
|       13 | `$FC30-$FC36` [64560-64566] |     [48203-48209]     |
|       14 | `$FD30-$FD36` [64816-64822] |     [48459-48465]     |
|       15 | `$FE30-$FE36` [65072-65078] |     [48715-48721]     |
|       16 | `$F750-$F756` [63312-63318] |     [46955-46961]     |
|       17 | `$F850-$F856` [63568-63574] |     [47211-47217]     |
|       18 | `$F950-$F956` [63824-63830] |     [47467-47473]     |
|       19 | `$FA50-$FA56` [64080-64086] |     [47723-47729]     |
|       20 | `$FB50-$FB56` [64336-64342] |     [47979-47985]     |
|       21 | `$FC50-$FC56` [64592-64598] |     [48235-48241]     |
|       22 | `$FD50-$FD56` [64848-64854] |     [48491-48497]     |
|       23 | `$FE50-$FE56` [65104-65110] |     [48747-48753]     |

The corresponding 21 attributes are `$FF10-$FF16`, `$FF30-$FF36` and
`$FF50-$FF56` [65296-65302], [65328-65334] and [65360-65366]; SNA file offsets
[48939-48945], [48971-48977] and [49003-49009].  Every attribute is `$72`:
FLASH 0, BRIGHT 1, yellow PAPER 6 and red INK 2.

The final snapshot replaces the full 56 x 24 panel bitmap pixel-for-pixel from
the supplied two-colour PNG. Of the panel's 168 bitmap-byte positions, 77 byte
values differ from the earlier artwork; all 21 attributes, the two transition
cells and every unrelated byte remain untouched.

##### Race-scene `John Player Special` banner

The `John Player Special` raster banner is 104 x 8 pixels at race-cache-local
screen x=0 through x=103 and y=56 through y=63. It occupies thirteen bytes on
each of eight interleaved scanlines:

| Scanline | Address range               | SNA file-offset range |
|---------:|-----------------------------|-----------------------|
|        0 | `$F7DE-$F7EA` [63454-63466] |     [47097-47109]     |
|        1 | `$F8DE-$F8EA` [63710-63722] |     [47353-47365]     |
|        2 | `$F9DE-$F9EA` [63966-63978] |     [47609-47621]     |
|        3 | `$FADE-$FAEA` [64222-64234] |     [47865-47877]     |
|        4 | `$FBDE-$FBEA` [64478-64490] |     [48121-48133]     |
|        5 | `$FCDE-$FCEA` [64734-64746] |     [48377-48389]     |
|        6 | `$FDDE-$FDEA` [64990-65002] |     [48633-48645]     |
|        7 | `$FEDE-$FEEA` [65246-65258] |     [48889-48901]     |

The thirteen attributes at `$FFDE-$FFEA` [65502-65514]; SNA file offsets
[49145-49157] remain `$46`, meaning bright-yellow INK 6 on black PAPER 0.

In the final snapshot, the pixels spelling `pecial` are shifted one pixel left
while `John Player S` remains fixed. The old final pixel column x=103 is
cleared and the adjacent FIAT artwork still begins at x=104, providing a
one-pixel separation between the two logos. Exactly thirty bitmap-byte values
define this adjustment; attributes, FIAT and all unrelated data remain
untouched.

Useful animation/drawing entry points include `$9FB3` [40883], `$A00F` [40975]
and the small-object renderer at `$AEAF` [44719].

[//]: # (----------------------------------------------------------------------)
[//]: # (                                                                      )
[//]: # (    Part III                                                          )
[//]: # (                                                                      )
[//]: # (----------------------------------------------------------------------)
## Part III: Game functionality

### 14. Celsius conversion

The original game generated an integer from 0 to 29 and added 55, producing
55-84 degrees Fahrenheit. There was no temperature lookup table.

Original flow:

- `$C877` [51319]: call the random-number generator at `$9919` [39193];
- `$C87A-$C880` [51322-51328]: reduce the value modulo 30;
- `$C882-$C888` [51330-51336]: originally add 55 and store the result at `$82A7` [33447].

In the final snapshot, `$C882-$C888` [51330-51336] contains:

```text
CD 70 EA 00 00 00 00
```

This calls the added routine at `$EA70` [60016] and pads the remaining bytes
with NOPs. The routine at `$EA70-$EA89` [60016-60041] stores:

```text
13 + floor((5*n + 2) / 9), where n = Fahrenheit - 55
```

This is integer rounding of `(F-32)*5/9` for the original 55-84 F range,
producing 13-29 C. It preserves `BC`, then writes the converted value to
`$82A7` [33447].

The display loads `$82A7` [33447] at `$A442` [42050] and prints it using the
generic right-aligned ` 0`-`99` number table. The unit letter at `$7627`
[30247] was changed from `F` to `C`. The stored value is only used by the
display path found in this snapshot; it does not alter race physics.

### 15. Random-number generator and snapshot timing

The principal random-number routine is `$9919-$995A` [39193-39258].

It is not a table of pre-generated values. Each call:

1. reads the 16-bit software seed at `$6892-$6893` [26770-26771];
2. performs a deterministic arithmetic transformation;
3. mixes the result with the Spectrum `FRAMES` bytes at `$5C78-$5C79` [23672-23673] using XOR;
4. writes the new seed back to `$6892-$6893` [26770-26771] and returns its low byte in `A`.

Race initialisation at `$C3BF-$C3C7` [50111-50119] seeds `$6892-$6893`
[26770-26771] from two reads of the Z80 refresh register `R`. The routine
briefly disables interrupts while updating the seed, but frame timing between
calls still affects the sequence.

Consequences:

- a real Spectrum tape load and an emulator snapshot will normally produce
  different sequences;
- input timing changes the sequence because it changes `R` and `FRAMES` at
  later calls;
- after loading the same snapshot, sufficiently similar input timing can make
  the season highly repeatable;
- a different sequence does not by itself show that the emulator's random
  distribution is defective.

The RNG, initial seeding code, AI maintenance code and race-worthiness code in
the final snapshot are byte-for-byte identical to the supplied 1985 snapshot.

### 16. AI maintenance and cars missing from the grid

#### Race-worthiness test

Routine `$C2BB-$C2FC` [49851-49916] checks all twelve cars before the grid is
displayed. Helper `$C2FD` [49917] rejects a car when any of these values is
`$33` [51] or greater:

- engine condition at  `$6979 [27001] + car_slot`;
- chassis condition at `$6985 [27013] + car_slot`;
- the assigned driver's value in `$6916-$692D` [26902-26925], selected through
  `$6991-$699C` [27025-27036].

`$C305` [49925] then writes status `$0D` [13] to `$69FD [27133] + car_slot`.
Grid routine `$D05A` [53338] skips any car with status `$0D` [13] or higher.

Lower engine, chassis and driver values are better. The value is a
penalty/condition quantity, not a conventional percentage where a larger number
would be desirable.

#### Why many computer cars can miss one race

Computer maintenance is performed by `$CF23-$D056` [53027-53334]. `$CFA5` [53157]
uses the two difficulty variables at `$8B07-$8B08` [35591-35592].

The original selection screen produces these initial pairs:

| Selection | Value at `$8B07` [35591] | Value at `$8B08` [35592] |
|:----------|-------------------------:|-------------------------:|
|         1 |                        8 |                        0 |
|         2 |                       16 |                        2 |
|         3 |                       24 |                        4 |
|         4 |                       32 |                        6 |
| 5, novice |                       40 |                        8 |

The AI normally replaces a component when its current value reaches the value
stored at `$8B07` [35591], plus 10. On the weakest setting that threshold is
initially 50. The flaw is that a component below the replacement threshold is
first allowed to deteriorate by a random amount. It can jump directly from
below 50 to 51 or considerably higher. It is then rejected at the following
race before the next replacement opportunity.

A captured mid-season diagnostic state demonstrated this exactly:

| Car | Team    | Driver  | Engine | Chassis | Reason for exclusion |
|----:|---------|---------|-------:|--------:|----------------------|
|   1 | Brabham | Lauda   |   38   |    71   | chassis              |
|   3 | Ferrari | Piquet  |   66   |    39   | engine               |
|   5 | Lotus   | Boutsen |   74   |    68   | both                 |
|   6 | Lotus   | Arnoux  |   58   |     9   | engine               |
|   9 | McLaren | Prost   |   47   |    51   | chassis              |
|  11 | Renault | Mansell |   42   |    72   | chassis              |
|  12 | Renault | Laffite |   32   |    59   | chassis              |

All seven carried status `$0D`; none failed the driver check. The runtime
difficulty bytes were 39 and 8, showing that selection 5 had been chosen and
`$8B07` [35591] had subsequently been decremented once by the game flow.

This exclusion is normally temporary. End-of-race processing calls `$CECC`
[52940], which reaches the AI component maintenance at `$CF21` [53025]. At the
next Grand Prix, `$C7BA` [51130] clears temporary race data; the zeroing loop
beginning at `$C7FB` [51195] includes `$69FD-$6A08` [27133-27144]. The rejected
cars can therefore return after their equipment is replaced, although other
cars may suffer the same one-race problem later.

The final documented snapshot preserves this original behaviour. A robust
future fix would replace or clamp an AI component immediately when a
deterioration update produces 51 or more.

### 17. Sponsorship and computer-team finances

The game does not maintain a genuine budget simulation for computer-controlled teams.

- `$701F-$7024` [28703-28708]: six team-control flags; zero means computer
  controlled and nonzero means human controlled.
- `$880D-$8819` [34829-34841]: thirteen one-byte sponsor values.
- `$8841-$8846` [34881-34886]: primary sponsor IDs.
- `$8847-$884C` [34887-34892]: secondary sponsor IDs.
- `$887D-$8888` [34941-34952]: six little-endian 16-bit bank balances.

Starting-balance routine `$BBD0-$BC22` [48080-48162] loops through the six
teams but skips any team whose control flag is zero. It begins with a fixed
150, processes the primary sponsor through the doubling helper twice, and
processes the secondary sponsor through it once.

The helper uses `RLC E` plus a separate increment of `D`, rather than an
ordinary 16-bit shift. Consequently, a carry can add an extra one. At the
beginning of a new game all thirteen sponsor values are `$7D` [125], producing
this actual byte-level calculation:

```text
primary:   125 -> 250 -> 501
secondary: 125 -> 250
fixed amount:          150
normal opening total:  901
```

Sponsor-reset routine `$B97D-$B9AF` [47485-47535] clamps the evolving sponsor
values to 100-175, performs the sponsor-selection paths and then calls the
starting-balance routine. This is why a later season can begin with a different
sponsorship-based sum.

The AI maintenance routine `$CF23-$D056` [53027-53334] never reads sponsor IDs
or bank balances; computer engines and chassis are replaced according to
difficulty and randomness, not affordability.

In that diagnostic state, Williams was the only human team. Its primary and
secondary sponsor IDs were 1 and 2 and its balance was 970. The five AI teams
had zero sponsor IDs and zero balances by design. Their grid absences were
therefore unrelated to sponsor income.

#### Zero-sponsor indexing correction

The original helper at `$BA1C-$BA26` [47644-47654] treated every sponsor ID as
a one-based index into `$880D-$8819` [34829-34841]. For ID zero, `DEC E`
wrapped the index to `$FF` [255], producing pointer `$890C` [35084]: the space
between `A` and `to` in `Press A to M for Selection`. A sponsor-value update
could consequently replace that space with a changing character.

The corrected 11-byte helper returns `$0000` for ID zero, using ROM as a
harmless write sink, while IDs 1-13 still map exactly to `$880D-$8819`:

```text
19 7E 6F 62 B7 C8 11 0C 88 19 C9
```

The two callers remain at `$B9D5` [47573] and `$B9DD` [47581]. The correction
changes no sponsor name, value or valid sponsor assignment.

#### Optional double starting money

The game calculates a new sponsorship-based balance for each human-controlled
team at the beginning of every season. The canonical snapshot preserves the
normal calculation. Players who prefer enough money to begin with two drivers,
under approximately the same practical conditions as the AI teams, can enable
the optional `--double-starting-money` adjustment in `Tweak-F1.py`.

The canonical seven-byte sequence at `$BC0C-$BC12` [48140-48146] is:

```text
EB 21 7D 88 CD 35 BC
```

The option replaces it with a call to the wrapper at `$EA8A` [60042], followed
by four NOPs:

```text
CD 8A EA 00 00 00 00
```

The 15-byte wrapper is stored at `$EA8A-$EA98` [60042-60056] but remains dormant
unless the option patches the call site:

```text
3A DC 8B B7 20 00 29 EB 21 7D 88 CD 35 BC C9
```

Disassembled:

```text
LD A,($8BDC)       ; address 35804 decimal; season-offset byte
OR A
JR NZ,$EA90        ; zero displacement: next instruction in either case
ADD HL,HL          ; double the complete calculated balance every season
EX DE,HL
LD HL,$887D        ; address 34941 decimal
CALL $BC35         ; address 48181 decimal; write this team's balance
RET
```

The zero relative-jump displacement at `$EA8F` [60047] makes both outcomes
continue at `$EA90` [60048], so the option applies at the beginning of every
season. With the initial sponsor values, the balance is `901*2 = 1802`. The
result remains proportional when sponsor values change in later seasons.
Purchases, prize money, component costs and other income/expense routines are
untouched. Computer-controlled teams remain unaffected because the original
loop continues to skip them. This is an optional gameplay-balance adjustment,
not a correction required for normal operation.

### 18. Tyre choice, tyre wear and pit stops

This section describes two separate effects that contribute to a car’s
_accumulated tyre penalty_: the immediate penalty for using tyres unsuitable
for the current track condition, and progressive deterioration as the tyres
age. For each car, the game records the selected tyre, its age in laps and its
_accumulated tyre penalty_. Changing tyres resets the age to zero and
initialises _accumulated tyre penalty_ from the tyre/track suitability table;
subsequent laps may increase it after a _tyre wear threshold_ is reached.

#### Runtime values

- `$699D-$69A8` [27037-27048], 12 bytes: tyre choice for each car.
- `$69A9-$69B4` [27049-27060], 12 bytes: _accumulated tyre penalty_;
  lower is better.
- `$8BD0-$8BDB` [35792-35803], 12 bytes: tyre-age counters.
- `$6BA5`       [27557], 1 byte:         track condition: 1 dry, 2 damp, 3 wet.

Tyre numbers are:

| Value | Tyre         |
|------:|--------------|
|   1   | soft slick   |
|   2   | medium slick |
|   3   | hard slick   |
|   4   | intermediate |
|   5   | rain tyre    |

#### Initial tyre/track suitability penalty

The global 15-byte lookup table at $6E78-$6E86 [28280-28294] contains the
initial _accumulated tyre penalty_ for each combination of five tyre types and
three track conditions. When tyres are selected, routine $A65B [42587] resets
the car’s tyre-age counter to zero and uses this table to initialise its
_accumulated tyre penalty_ value.  This table represents immediate tyre
suitability; progressive tyre wear is calculated separately, as explained in
the next section.

| Tyre         | Dry | Damp | Wet |
|--------------|----:|-----:|----:|
| Soft slick   |   0 |   10 | 200 |
| Medium slick |   5 |   20 | 200 |
| Hard slick   |  10 |   30 | 200 |
| Intermediate |  40 |    0 |  40 |
| Rain         |  60 |   30 |   0 |

This is why slicks in wet conditions are immediately disastrous rather than
merely wearing somewhat faster.

Track-condition changes call `$D27A` [53882], which adds the new tyre/track
mismatch penalty to each car's _accumulated tyre penalty_.

#### Progressive wear

Since the program uses several values (numbers) for tyre wear, The following
terms are used throughout this subsection:
- _Tyre age_                 = How many laps the has tyre completed.
- _Tyre wear threshold_      = The age at which the tyre starts to deteriorate.
- _Accumulated tyre penalty_ = Actual performance penalty applied to the car.
                               Lower is better.
- _Tyre wear increment_      = How much is added to _accumulated tyre penalty_
                               every lap after the _tyre wear threshold_ is
                               reached.

Within the main race-update routine beginning at `$C094` [49300], the loop at
`$C0A6-$C0AE` [49318-49326] increments each of the twelve one-byte tyre-age
counters by exactly one, effectively once per lap in normal play.  The code
which does it is listed here:

```z80
$C0A6: 06 0C       LD   B,$0C       ; 12 cars
$C0A8: 21 D0 8B    LD   HL,$8BD0    ; first tyre-age counter

$C0AB: 34          INC  (HL)        ; add 1 to this car's tyre age
$C0AC: 23          INC  HL          ; move to the next car
$C0AD: 10 FC       DJNZ $C0AB       ; repeat for all 12 cars
```

Routine `$C353` [50003] (59 bytes long, not listed here) compares the age with
a _tyre wear threshold_ from `$8BC1-$8BCF` [35777-35791]; after that _tyre wear
threshold_ it adds a _tyre wear increment_ `$8BB2-$8BC0` [35762-35776] to
_accumulated tyre penalty_ on each subsequent simulation cycle, effectively
each lap in normal play.

The _tyre wear threshold_ values are:

| Tyre         | Dry | Damp | Wet |
|--------------|----:|-----:|----:|
| Soft slick   |  20 |   20 |  30 |
| Medium slick |  30 |   22 |  30 |
| Hard slick   |  40 |   24 |  30 |
| Intermediate |  10 |   25 |  20 |
| Rain         |   5 |   20 |  25 |

The _tyre wear increment_ after the _tyre wear threshold_ has been reached is:

| Tyre         | Dry | Damp | Wet |
|--------------|----:|-----:|----:|
| Soft slick   |  10 |   15 |   1 |
| Medium slick |   5 |    8 |   1 |
| Hard slick   |   1 |    2 |   1 |
| Intermediate |  15 |    5 |   5 |
| Rain         |  20 |    5 |   2 |

##### Example: medium slick on a dry track

The table says:
- Initial _accumulated tyre penalty_:  5
- _tyre wear threshold_:              30 laps
- Later _tyre wear increment_:         5 per lap

The race therefore proceeds like this:

| Lap/age  | _Accumulated tyre penalty_ | What happens                                       |
|---------:|---------------------------:|----------------------------------------------------|
|        0 |                          5 | New tyre; small initial _accumulated tyre penalty_ |
|     1-29 |                          5 | Tyre is still below its _tyre wear threshold_      |
|       30 |                         10 | _Tyre wear threshold_ reached: add 5               |
|       31 |                         15 | Add another 5                                      |
|       32 |                         20 | Add another 5                                      |
|       33 |                         25 | Add another 5                                      |
|       34 |                         30 | Add another 5                                      |
|       35 |                         35 | Add another 5                                      |
|       36 |                         40 | AI may schedule a pit stop                         |

#### Pit behaviour

AI routine `$D2B4` [53940] schedules a computer car for a stop once its
_accumulated tyre penalty_ reaches 40, provided the race has progressed far
enough. Human-controlled cars are not automatically called in by this logic.

So, the tyre-age counter does not directly slow the car.  It merely tells the
game when to start increasing _accumulated tyre penalty_.  The value 40 is not
stored in a special table.  Rather, it is hard-coded in the routine `$D2B4`:

```z80
$D2B4: 21 A9 69    LD   HL,$69A9    ; _accumulated tyre penalty_ values
$D2B7: 19          ADD  HL,DE       ; select this car
$D2B8: 7E          LD   A,(HL)      ; read its _accumulated tyre penalty_
$D2B9: FE 28       CP   $28         ; compare _accumulated tyre penalty_ with 40
$D2BB: DA D9 D2    JP   C,$D2D9     ; if smaller than 40, do not schedule a stop
```

To call a human car into the pits, press `P`, enter a two-digit car number and
press Enter. Cars 1-9 require the leading zero: `01`, `02`, and so on. The
prompt continues waiting if only one digit is entered.

Every pit-service description at `$94B3` [38067] includes a tyre change.
A routine tyre-only stop is the quickest option when no component needs
attention. Changing tyres through `$A65B` [42587] resets the age counter and
returns _accumulated tyre penalty_ to the base value appropriate for the
current weather and tyre choice.

As a dry-race rule of thumb, softs invite a stop around lap 20-24, mediums
around lap 30-36, while hards often last a normal race without a planned stop.
Weather changes can make an immediate stop more important than these nominal
intervals.

#### Automatic pit stops for human-controlled cars

In the original program, the loops at `$D22A` [53802] and `$D2DE` [53982]
consult the six team-control flags at `$701F-$7024` [28703–28708]. A nonzero
flag identifies a human-controlled team and causes the automatic pit-stop
scheduler to be skipped.

If the conditional jumps at `$D23A-$D23C` [53818–53820] and `$D2EE-$D2F0`
[53998–54000] were replaced with three `NOP` instructions each, routine
`$D2B4` [53940] would evaluate _all_ twelve cars. This would allow
human-controlled cars to be called into the pits automatically under the same
conditions as computer-controlled cars.

The _tyre wear threshold_ and race-progress check would remain unchanged, and
human players could still request a pit stop manually by pressing `P`.
This modification has not been applied to the current snapshot.
The optional `--automatic-human-pit-stops` switch described in
[Part IV](#part-iv-using-tweak-f1py) applies exactly this six-byte patch while
leaving it absent by default.

#### Second-car pit scheduling bug and permanent fix

The original scheduler attempts to stagger the two cars belonging to one team.
The first car is assigned to the next lap, while its even-numbered team-mate is
assigned one lap later.  The distinction is made by these five bytes near the
end of routine `$D2B4` [53940]:

```z80
$D2C9: CB 43       BIT  0,E         ; distinguish the two cars in a team
$D2CB: 28 01       JR   Z,$D2CE     ; first car: retain next-lap appointment
$D2CD: 3C          INC  A           ; second car: postpone by one more lap
```

However, the scheduler runs again on every lap and does not preserve an
existing future appointment.  Before an even-numbered car reaches its assigned
lap, the same code moves its appointment forward again.  The car can therefore
continue racing indefinitely without entering the pits.  The rescheduling can
also overwrite a manual pit request made by pressing `P`.

The permanent correction replaces `$D2C9-$D2CD` [53961-53965] with five `NOP`
instructions:

```z80
$D2C9: 00          NOP
$D2CA: 00          NOP
$D2CB: 00          NOP
$D2CC: 00          NOP
$D2CD: 00          NOP
```

Both cars are consequently assigned to the next lap.  This removes the unfair
penalty applied to every second car, restores automatic stops for affected
computer-controlled cars and prevents manual requests for affected
human-controlled cars from being overwritten.  Emulator testing confirmed that
even-numbered cars, including car 12, now enter the pits correctly.  This is a
permanent game correction rather than an optional `Tweak-F1.py` feature.

### 19. Fixed car numbers and the defending champion

The game has no independent race-number field. It treats car slot 1 as
number 1, slot 2 as number 2, and so on through slot 12.

This assumption appears in several places:

- `$7DB0-$7DC7` [32176-32199]: pointers to number glyphs used with car slots;
- `$8FD3-$9182` [36819-37250]: twelve starting-grid number-box records selected
  directly by slot;
- top-view/side-view composition and car-detail displays;
- pit-stop input, where the entered number is converted directly to a slot.

The end-of-season standings sorter `$D5EE-$D6A4` [54766-54948] already places
the leading driver's ID first in the order table beginning at `$8F2E` [36654],
so the champion can be identified. No original routine uses that result to
remap next season's car numbers.

A complete defending-champion-number patch is feasible inside the SNA, but it
would require a persistent 12-entry slot-to-number mapping and the reverse
mapping for pit input. To follow the historical convention, the champion's car
would receive 1, the teammate 2, and the former 1/2 team would receive the
champion team's previous number pair. This feature has been analysed but is not
implemented in the final snapshot.

### 20. Modification history represented by the final snapshot

The final snapshot grew from a MOD2020-derived starting point. In logical order,
the retained changes are:

- original 1985 driver, team, manager, sponsor, race and circuit text;
- original 1985 lap counts, records, previous winners, lengths and year bases;
- MOD2020 car and scene artwork;
- classic team palette, including black Lotus and yellow Renault;
- consistently narrow car-number glyphs for cars 1-12;
- yellow starting-grid boxes for cars 11 and 12;
- correctly converted and labelled Celsius temperatures;
- horizontally symmetric shared engine artwork;
- mirrored upper/lower rear-suspension artwork;
- original 1985 championship points: 9, 6, 4, 3, 2, 1;
- a dormant wrapper supporting optional doubled starting money for
  human-controlled teams at the beginning of every season;
- sponsor ID zero handled without corrupting the sponsor-selection prompt;
- car-management progress bars animated approximately four times faster;
- the custom character set and selected pre-rendered text converted to the new font;
- revised `GOODYEAR`, `Mobil`, `ELAPSED`, `GRAND PRIX`, Pirelli and John Player Special raster artwork;
- mirrored direction arrows, with a bright red/yellow flashing pit arrow;
- uniform one-pixel starting-grid frames for cars 11 and 12;
- fixed blue, black and yellow general-screen border colours, independent of the editable team palettes;
- removal of two redundant small `FORMULA 1` captions from setup screens;
- replacement of the transient blue/yellow race-country chequerboard with a
  plain blue bitmap field;
- component-purchase entries limited to 255 before money is deducted;
- component-improvement entries limited to their remaining useful cost, with
  255 retained as the overall ceiling.

This is a history of changes, not a chain of build files. The obsolete
intermediate filenames and per-step hashes have intentionally been omitted.
This map is specific to the final snapshot named at the top. The RNG, AI
maintenance/no-show behaviour, underlying sponsorship model, tyre model and
fixed car-number behaviour are documented discoveries. The sponsor-pointer
correction and context-aware purchase/improvement limits are gameplay fixes,
while balance doubling is an optional gameplay adjustment and the progress-bar
patch changes presentation speed only. Addresses that hold free space, modified
code or replacement data should not be assumed identical in another snapshot
without a byte comparison.

### 21. Verification against `F1-1985-Original.sna` and gameplay screenshots

This section records findings from directly inspecting the unmodified original
snapshot, `F1-1985-Original.sna` (SHA-256
`34E5A9FD62C6355C43630255CBCE047940EF59480BEF8547D6842718333F5325`,
49,179 bytes), alongside a set of gameplay screenshots taken from an actual
play session. The two do not necessarily reflect the same moment of program
state — the snapshot may be a fresh/reset capture, while the screenshots come
from a played-through game — so run-time values are compared with that caveat,
while fixed tables and code are compared directly.

#### Confirmed identical fixed data

The following tables were read byte-for-byte from the original file and matched
the values already documented elsewhere in this map, confirming the snapshot's
"restored 1985 data" is faithful to the original:

- Driver names (`$6E87`, 27x10): identical, including the novice pool records
  19-24 (`Walker, Chambers, Rowland, Munday, Wood, Wheelhouse`).
- Team names (`$6F95`, 9x8): identical.
- Sponsor names (`$8771`, 13x12): identical.
- Championship points table (`$7B96`): `09 06 04 03 02 01 00 00`, identical.
- Race data block (`$6AD5`): lap counts
  `61,75,70,60,79,76,70,63,67,71,44,51,71,51,67,70`, identical.
- Race names (`$7025`, 16x8) and circuit names (`$70A5`, 16x18): identical,
  e.g. record 0 is `Brazil` / `Jacarepagua`.
- Weather descriptions (`$748E`, 12x32): all 12 records read cleanly; record 2
  is `Overcast sky but dry`, record 1 is `Broken cloudy sky but dry`.
- The Celsius-conversion routine's target address, `$EA70`, contains ordinary
  original code in this file (not the conversion routine), confirming the
  Celsius patch is exclusive to the modified snapshot and does not exist in the
  original.

#### New finding: driver cost is derived, not tabled

The Driver Selection screen shows a `Cost` column (e.g. Lauda / Prost /
De Angelis / Alboreto / Piquet / Arnoux at £186,000; Warwick / Rosberg /
Senna / Mansell / Tambay / Fabi at £154,000).  No address in this map
currently documents a stored cost table. Direct inspection of the driver-ability
block at `$6916-$692D` [26902-26925] shows the 24 bytes fall into six-driver
groups of identical value:

```text
16 16 16 16 16 16   (Lauda...Arnoux)   -> shown as £186,000
24 24 24 24 24 24   (Warwick...Fabi)   -> shown as £154,000
32 32 32 32 32 32   (Patrese...Brundle)
40 40 40 40 40 40   (Walker...Wheelhouse, the novice pool)
```

The tier boundaries in the ability table line up exactly with the tier
boundaries in the displayed cost. This strongly suggests the Driver Selection
screen computes cost from the ability byte at display time (e.g. an inverse /
linear function of ability) rather than reading a separate stored price table.
The exact formula and the routine that prints the `Cost` column have not yet
been isolated in the disassembly; this is listed as an open item in 21.3.

#### Open items for further disassembly

- **Driver cost formula and print routine**: isolate the code that turns an
  ability byte into the displayed `£nnn,000` figure on the Driver Selection
  screen.
- **Difficulty-byte discrepancy**: the original file's snapshot-time values at
  `$8B07-$8B08` were `40, 0`, whereas §16's documented "Novice" selection pair
  is `40, 8`. This may simply reflect the snapshot being captured before a full
  selection/initialisation pass; worth a short trace of the manager-standard
  selection routine to confirm the exact write sequence.

### 22. Screen border-colour independence patches

These related patches are included in the final snapshot and operate on the
same 49,179-byte image as the other documented changes. They were added after
the Celsius, starting-money, faster-progress-bar and starting-grid-frame
corrections described earlier.

#### Purpose and original problem

Four screens in the unpatched program set their Spectrum border and
default panel `PAPER` colour by hardcoding car number 1 and calling shared
palette routine `$96AA`, which re-reads team 1's current palette entry at
`$6FDD`. In the original 1985 game this was invisible because team 1 was
permanently blue. Once a tweaker repainted team 1, those four screens silently
followed it.

A second set of screens similarly hardcoded car 5 or car 11, causing their
border and default `PAPER` colours to follow team 3 (originally black) or team 6
(originally yellow). This was confirmed by comparing an original-palette run
with a repainted run. The same `LD A,n / CALL $96AA` pattern was found by
searching for `3E 05`/`3E 06` (car 5/6 → team index 2, i.e. team 3) and
`3E 0B`/`3E 0C` (car 11/12 → team index 5, i.e. team 6), then matching each
hit's surrounding routine against known text and table references.

The final patches decouple all nine screens from the team palette. They use
dedicated fixed-blue, fixed-black and fixed-yellow constants while leaving the
actual colours of teams 1, 3 and 6 free to be changed.

#### Added data and routines

##### Fixed-blue routine

`$EAB3-$EAC4` [60083-60100], 18 bytes, placed in space that was still
zero-filled immediately after the first three added routines at `$EA70-$EAB2`
(§4, "Added routines in the final snapshot"):

```text
$EAB3  01                BORDER_BLUE_CONST: db 1      ; Spectrum hue 1 = blue; edit this single byte to change all four screens
$EAB4  F5                PUSH AF
$EAB5  3A B3 EA          LD A,($EAB3)
$EAB8  D3 FE             OUT ($FE),A                   ; border
$EABA  CB 27             SLA A
$EABC  CB 27             SLA A
$EABE  CB 27             SLA A
$EAC0  32 48 5C          LD ($5C48),A                   ; default PAPER (ATTR_P)
$EAC3  F1                POP AF
$EAC4  C9                RET
```

This mirrors the border/PAPER-setting tail of `$96AA` (`$96B9-$96C3` in that
routine) exactly, but takes its hue from `$EAB3` instead of from the
team-palette table at `$6FDD`, and only preserves `AF` (the new routine
touches no other register, unlike `$96AA`, which also uses `BC`/`DE`/`HL` to
compute the team-table index). Entry point for callers is `$EAB4` (i.e. the
byte after the constant).

##### Fixed-black and fixed-yellow routine

`$EAC5-$EAE1` [60101-60129], 29 bytes, placed in the free space immediately
after the fixed-blue block (`$EAB3-$EAC4`), which was confirmed still
zero-filled beforehand:

```text
$EAC5  00                BLACK_CONST:  db 0          ; Spectrum hue 0 = black
$EAC6  06                YELLOW_CONST: db 6          ; Spectrum hue 6 = yellow
$EAC7  F5                entry_black:  PUSH AF
$EAC8  3A C5 EA                        LD A,($EAC5)
$EACB  C3 D5 EA                        JP $EAD5
$EACE  F5                entry_yellow: PUSH AF
$EACF  3A C6 EA                        LD A,($EAC6)
$EAD2  C3 D5 EA                        JP $EAD5
$EAD5  D3 FE             shared_tail:  OUT ($FE),A    ; border
$EAD7  CB 27 CB 27 CB 27               SLA A x3
$EADD  32 48 5C                        LD ($5C48),A   ; default PAPER (ATTR_P)
$EAE0  F1                              POP AF
$EAE1  C9                              RET
```

This second routine needs two fixed hues shared across five call sites, so the
`OUT`/`SLA`/store logic is factored into one common tail. The black and yellow
entry points load their respective constants and then share the same
border/PAPER-setting code.

#### Patched call sites

Each 5-byte `LD A,n / CALL $96AA` sequence was replaced in place with a call to
the matching fixed-colour entry point plus two `NOP`s. Every original 5-byte
slot is preserved exactly, so no other code shifts:

| Screen                                | Address  | Fixed colour | Original bytes   | New bytes        |
|---------------------------------------|---------:|--------------|------------------|------------------|
| Race Results (after each race)        | `$A47A`  | Blue         | `3E 01 CD AA 96` | `CD B4 EA 00 00` |
| Championship Points (after each race) | `$CD57`  | Blue         | `3E 01 CD AA 96` | `CD B4 EA 00 00` |
| Starting Grid                         | `$D06B`  | Blue         | `3E 01 CD AA 96` | `CD B4 EA 00 00` |
| End-of-season final screen            | `$E783`* | Blue         | `3E 01 CD AA 96` | `CD B4 EA 00 00` |
| Team Selection border                 | `$BD07`  | Black        | `3E 05 CD AA 96` | `CD C7 EA 00 00` |
| Race Announcement                     | `$CBB5`  | Black        | `3E 05 CD AA 96` | `CD C7 EA 00 00` |
| Novice Driver Pool                    | `$D516`  | Black        | `3E 05 CD AA 96` | `CD C7 EA 00 00` |
| "Racing cancelled" message            | `$E419`* | Black        | `3E 05 CD AA 96` | `CD C7 EA 00 00` |
| Manager Standard (difficulty select)  | `$BECB`  | Yellow       | `3E 0B CD AA 96` | `CD CE EA 00 00` |

The five additional screen identifications were verified from their surrounding
code. Team Selection handles the `Press 1-6 for number` and `Player _ enter
name` text; before §23 it also printed the redundant `FORMULA 1` title. Race
Announcement calls `$9CB6`, `$CBD0` and `$A41C`, the three subroutines already
attributed to its circuit/lap header, previous-winner and
track/weather/temperature sections. The Novice Driver Pool and "racing
cancelled" messages are embedded directly in their respective routines, while
the Manager Standard routine references its `...standard of...` and
`PRESS 1 to 5...` text.

Two starred addresses vary between builds. The end-of-season call site is at
`$E783` in the final snapshot, six bytes earlier than `$E789` in
`F1-1985-Original.sna`. The "racing cancelled" call is at `$E419`,
versus `$E41F` in the original snapshot. These sites should therefore be
relocated by their byte patterns and surrounding routines rather than assumed
to occupy fixed addresses in every build.

#### Verified scope of the changes

The combined patch occupies 92 byte positions: nine 5-byte call sites
(45 bytes), the 18-byte fixed-blue routine and the 29-byte
fixed-black/fixed-yellow block. A direct comparison registers 91 changed byte
values because `$EAC5`, the black constant, was already zero before the block
was installed. File size remains 49,179 bytes.

The nine general-purpose screens listed above are now independent of the
colours assigned to teams 1, 3 and 6. The team-palette table, `$96AA` itself,
Team Selection's car swatches, Sponsor Selection, the side/top-view cars and
every other legitimate consumer of team-dependent colours remain untouched.
Repainting the teams therefore continues to work normally everywhere except
these deliberately fixed-colour screen backgrounds.

Other hardcoded car numbers (2, 3, 4, 6, 7-10 and 12) have not been
exhaustively checked for the same pattern. The search is mechanical and can be
repeated if another stray screen appears.

#### Recommended verification

Verification consists of loading the final snapshot in an emulator, repainting
teams 1, 3 and 6, and checking that all nine
listed screens retain their intended blue, black or yellow border and default
`PAPER` colour. Team Selection's car swatches, Sponsor Selection and the
side/top-view cars should still reflect the teams' actual chosen colours.

### 23. Removal of the redundant "FORMULA 1" title text

Once the splash bitmap documented in §13 was replaced with custom artwork that
already includes a large graphical `FORMULA ONE` logo, the small plain-text
title `FORMULA 1` that the original 1985 game additionally prints on two later
setup screens became redundant duplication rather than a title in its own right.

#### Where it comes from

The original nine-character text `FORMULA 1` occupied `$82EA-$82F2`,
immediately followed in memory by `Press 1-6 for number of players` (`$82F3`)
and `Player   enter name, ` (`$8312`) as one contiguous block of embedded
strings. It was printed from two independent call sites, each a self-contained
12-byte sequence (`LD DE,$82EA` / `LD A,n` / `LD C,n` / `LD B,$09` /
`CALL $9728`, the shared text-printing routine used throughout the game):

| Screen                             | Address       | Followed immediately by                                            |
|------------------------------------|--------------:|--------------------------------------------------------------------|
| Number-of-players prompt           | `$BCC8-$BCD3` | `Press 1-6 for number of players` (`LD DE,$82F3` at `$BCD4`)       |
| Difficulty/manager-standard select | `$BED0-$BEDB` | `Please select the minimum standard...` (`LD DE,$8A72` at `$BEDC`) |

**Note:**

The number-of-players prompt belongs to the routine at `$BCBB-$BD64`, which
also contains the fixed-black border call at `$BD07`. The difficulty-level
prompt belongs to the routine beginning at `$BE89`, which contains the
fixed-yellow border call at `$BECB`.

In both cases the very next instruction reloads `DE`, `A`, `B` and `C` from
scratch for the following text, so the 12-byte block is fully self-contained:
nothing after it depends on the register state it sets up.

#### The patch

The two printing sequences were first replaced with `NOP`s. In the final
snapshot, their now-unused space is shared with the improvement-limit helper
documented in §24. Each screen begins with a short jump over its helper fragment
and therefore proceeds directly to the original follow-on prompt:

| Site    | Original bytes                        | Final bytes                            |
|---------|---------------------------------------|----------------------------------------|
| `$BCC8` | `11 EA 82 3E 00 0E 0C 06 09 CD 28 97` | `18 0A 3A 14 6C 4F 06 00 09 C3 D2 BE` |
| `$BED0` | `11 EA 82 3E 00 0E 0B 06 09 CD 28 97` | `18 0A 7E FE 33 38 02 3E 33 C3 DD 9F` |

At `$BCC8`, `JR $BCD4` skips to `Press 1-6 for number of players`. At
`$BED0`, `JR $BEDC` skips to `Please select the minimum standard...`. The
remaining ten bytes at each site are entered only by the improvement path.
The follow-on printing code is byte-for-byte unchanged.

The now-unreferenced nine-byte `FORMULA 1` string at `$82EA-$82F2`
[33514-33522] is also reused by §24: its first five bytes form the
purchase-mode dispatcher and its remaining four bytes are zero. Net effect:
both screens still show only their prompt/instruction text, with no small
`FORMULA 1` caption competing with the graphical logo above it.

### 24. Limiting acquisition and improvement entries

The car-and-crew acquisition screen accepts decimal amounts for buying and
improving engines, chassis and crews. Both operations eventually use the same
numeric-input and payment routines, but their useful upper limits differ:

- a new acquisition can use at most 255;
- an improvement can use at most the cost still required by that component,
  and never more than 255.

The shared numeric-input routine at `$9DC0` [40384] returns the entered value
in `DE`. In the original program, `$DCD3` [56531] calls `$9902` [39170] and
deducts the full 16-bit value before later code reduces the resulting component
value. Thus an oversized acquisition or improvement can deduct money that
provides no benefit.

#### Distinguishing buying from improving

The two operations are still separate immediately before they enter the shared
transaction code:

| Operation   | Original call                    | Final call                       |
|-------------|----------------------------------|----------------------------------|
| Acquisition | `$E182`: `CALL $DBD3`            | `$E182`: `CALL $82EA`            |
| Improvement | `$E188`: `CALL $DC1A`            | `$E188`: `CALL $BCCA`            |

The five-byte acquisition dispatcher at `$82EA-$82EE` [33514-33518] clears the
alternate accumulator and carry flag, marks the operation as an acquisition,
and enters the original routine:

```z80
$82EA: AF          XOR  A
$82EB: 08          EX   AF,AF'
$82EC: C3 D3 DB    JP   $DBD3
```

The improvement dispatcher calculates the useful ceiling from the selected
component's current internal condition/deficit byte. The component-table base
is already in `HL`, while `$6C14` [27668] holds the current car-slot index.
The condition is limited to 51 and multiplied by five because
`$DC50-$DC5A` [56400-56410] converts the entered improvement amount into one
condition point per five monetary units. The resulting ceiling is therefore:

```text
minimum(255, 5 x current internal condition/deficit)
```

For example, when only 10 units of useful improvement remain, entering 1000 is
reduced to 10 before payment. If at least 255 units remain, the ordinary 255
ceiling is retained.

The helper is split across three pieces of space that were no longer needed:

```z80
$BCCA: 3A 14 6C    LD   A,($6C14)  ; current car-slot index
$BCCD: 4F          LD   C,A
$BCCE: 06 00       LD   B,$00
$BCD0: 09          ADD  HL,BC       ; selected component record
$BCD1: C3 D2 BE    JP   $BED2

$BED2: 7E          LD   A,(HL)      ; current internal deficit
$BED3: FE 33       CP   $33         ; 51 x 5 = 255
$BED5: 38 02       JR   C,$BED9
$BED7: 3E 33       LD   A,$33       ; saturate at 51
$BED9: C3 DD 9F    JP   $9FDD

$9FDD: 07          RLCA              ; 2 x deficit
$9FDE: 07          RLCA              ; 4 x deficit
$9FDF: 86          ADD  A,(HL)       ; 5 x deficit
$9FE0: ED 42       SBC  HL,BC        ; restore component-table base
$9FE2: 37          SCF               ; mark improvement mode
$9FE3: 08          EX   AF,AF'       ; preserve mode and ceiling
$9FE4: C3 1A DC    JP   $DC1A        ; original improvement routine
```

Restoring `HL` at `$9FE0` is essential. The first helper fragment temporarily
adds the current car-slot index so it can inspect the selected component, but
the original routine at `$DC1A` expects the component-table base and applies
that index itself. The capped multiplication leaves carry clear, allowing
`SBC HL,BC` to undo the temporary indexing before `SCF` sets the improvement
mode marker.

Normal screen-drawing flow never executes these fragments. The short jumps at
`$BCC8` [48328], `$BED0` [48848] and `$9FDB` [40923] skip over them to
`$BCD4`, `$BEDC` and `$9FE7`, respectively.

#### Context-aware pre-payment clamp

The existing hook at `$DCD3-$DCD5` remains a call to `$EAE2`:

| Site            | Original bytes | Final bytes |
|-----------------|----------------|-------------|
| `$DCD3-$DCD5`   | `CD 02 99`     | `CD E2 EA`  |

The expanded wrapper at `$EAE2-$EAFB` [60130-60155] retrieves the operation
marker from the alternate `AF` register:

```z80
$EAE2: 08          EX   AF,AF'
$EAE3: 38 09       JR   C,$EAEE     ; carry: improvement

; Acquisition: accept 0-255, otherwise use 255.
$EAE5: 14          INC  D
$EAE6: 15          DEC  D
$EAE7: 28 0F       JR   Z,$EAF8
$EAE9: 11 FF 00    LD   DE,$00FF
$EAEC: 18 0A       JR   $EAF8

; Improvement: use the smaller of the entry and calculated useful ceiling.
$EAEE: 14          INC  D
$EAEF: 15          DEC  D
$EAF0: 20 03       JR   NZ,$EAF5
$EAF2: BB          CP   E
$EAF3: 30 03       JR   NC,$EAF8
$EAF5: 5F          LD   E,A
$EAF6: 16 00       LD   D,$00

$EAF8: 08          EX   AF,AF'      ; restore the caller's accumulator
$EAF9: C3 02 99    JP   $9902       ; deduct the corrected amount
```

The mode and calculated ceiling remain available if `$9902` reports
insufficient funds and the shared routine asks for another entry. Minimum-price
validation and the original component-condition calculations are unchanged.
The existing post-payment byte clamp also remains as an additional safeguard.
The correction applies consistently to engine, chassis and crew transactions.

### 25. Random racing incidents and repair-related pit stops

Repair-related pit stops are separate from the progressive tyre-wear and
weather logic documented in chapter 18. Inside the main race-update routine
beginning at `$C094` [49300], the fragment at `$C20D` [49677] gives each car
a chance of suffering one of six racing incidents during a normal simulation
cycle, effectively once per car per lap.

#### Random-incident probability

The routine calls the pseudo-random-number generator described in chapter 15,
then requires bits 5, 4, 3, 2 and 1 of the returned byte to be set:

```z80
$C20D: CD 19 99    CALL $9919       ; obtain a pseudo-random byte in A

$C210: CB 6F       BIT  5,A
$C212: CA E4 C0    JP   Z,$C0E4     ; tested bit is zero: no incident
$C215: CB 67       BIT  4,A
$C217: CA E4 C0    JP   Z,$C0E4
$C21A: CB 5F       BIT  3,A
$C21C: CA E4 C0    JP   Z,$C0E4
$C21F: CB 57       BIT  2,A
$C221: CA E4 C0    JP   Z,$C0E4
$C224: CB 4F       BIT  1,A
$C226: CA E4 C0    JP   Z,$C0E4
```

Each bit has an equal chance of being zero or one. All five must be one, so
the probability that a car has an incident in each lap is:

```text
1/2 x 1/2 x 1/2 x 1/2 x 1/2 = 1/32 = 3.125%
```

Bits 7, 6 and 0 are ignored. Equivalently, eight of the 256 possible bytes
pass the test: `$3E`, `$3F`, `$7E`, `$7F`, `$BE`, `$BF`, `$FE` and `$FF`.

#### Incident selection and codes

After the gate succeeds, a second random byte is repeatedly reduced by six.
The remainder in `C`, from 0 through 5, selects the incident. Adding nine
turns that index into the game's incident code from 9 through 14:

```z80
$C229: CD 19 99    CALL $9919       ; obtain another random byte
$C22C: 06 06       LD   B,$06

$C22E: B8          CP   B
$C22F: DA 35 C2    JP   C,$C235     ; below 6: remainder is ready
$C232: 90          SUB  B
$C233: 18 F9       JR   $C22E       ; reduce the value modulo 6

$C235: 06 00       LD   B,$00
$C237: 4F          LD   C,A         ; incident index 0-5
$C238: 3E 09       LD   A,$09
$C23A: 81          ADD  A,C         ; incident code 9-14
$C23B: CD 3A C3    CALL $C33A       ; process/display the incident
```

| Index | Code | Reported incident                        | Condition addition | Pit stop |
|------:|-----:|------------------------------------------|--------------------|:--------:|
|     0 |    9 | Spun after shunt - pit stop due          | chassis +3         | yes      |
|     1 |   10 | Spun: chassis damage - stop due          | chassis +25        | yes      |
|     2 |   11 | Spun and lost time - no damage           | none               | no       |
|     3 |   12 | Engine sick - coming into pits           | engine +25         | yes      |
|     4 |   13 | Gearbox problems - pit stop due          | engine +3          | yes      |
|     5 |   14 | Puncture - pit stop required             | tyre penalty +240  | yes      |

The condition additions come from the six-byte tables at `$6BD1-$6BD6`
[27601-27606] for the engine, `$6BD7-$6BDC` [27607-27612] for the chassis
and `$6BDD-$6BE2` [27613-27618] for the tyre penalty. The selected incident
code is stored in the current car's record beginning at `$69E5` [27109].

The modulo-six selection has a negligible bias because 256 is not divisible
by six: indices 0-3 occur 43 times each, and indices 4-5 occur 42 times each.

#### Consequences and pit-stop branch

After applying the tabled engine, chassis or tyre consequence, the code tests
for index 2. That is the sole harmless incident; it branches directly to the
end of the current car update. Every other index writes the internal cycle
markers that arrange a pit stop:

```z80
$C296: 3E 02       LD   A,$02
$C298: B9          CP   C
$C299: CA AB C2    JP   Z,$C2AB     ; index 2: no pit stop

$C29C: 3A 0F 69    LD   A,($690F)
$C29F: 3C          INC  A
$C2A0: 21 86 68    LD   HL,$6886
$C2A3: 19          ADD  HL,DE       ; DE = current car index
$C2A4: 77          LD   (HL),A      ; schedule pit-related action
$C2A5: 21 81 6A    LD   HL,$6A81
$C2A8: 19          ADD  HL,DE
$C2A9: 3C          INC  A
$C2AA: 77          LD   (HL),A      ; store the following cycle marker
```

Five of the six incidents therefore require a pit stop. Including the small
modulo bias, the exact probability per car per lap is `213/8192`, or about
2.60%. Across two cars and a 60-lap race, the expected value is approximately
3.12 repair-related pit stops. This explains why several repairs during one
Grand Prix are common even when tyre wear and weather cause no additional
stops.

#### Optional incident-rate patch

`Tweak-F1.py --random-incidents=rare` replaces the five original `BIT` tests
with the compact gate below and fills `$C217-$C228` with `NOP`s. It requires
seven bits instead of five, reducing the incident probability from 1/32 to
1/128 while leaving the selector, incident codes and consequences unchanged:

```z80
$C210: E6 7F       AND  $7F
$C212: FE 7F       CP   $7F
$C214: C2 E4 C0    JP   NZ,$C0E4    ; condition failed: no incident
```

The `reduced` setting uses `$3F` in both instructions for a 1/64 rate;
`original` restores the documented 1/32 gate. Omitting the option leaves the
source snapshot's existing gate untouched.

### 26. Game sections

This chapter divides the game into its principal screens and phases.
Sections 01-23 describe the normal progression through a game. Section 24 is
an alternative cancellation branch that can be reached before any Grand Prix.

The addresses in the table below identify the beginning or practical controller
of each recognisable gameplay section. Some screens are phases inside a larger
routine, so the fourth column also names the renderer, input loop, caller or
follow-on routine that fixes the identification more precisely.

| No. | Section                               | Beginning/controller | Related routines and addresses                                                                                          |
|----:|---------------------------------------|---------------------:|-------------------------------------------------------------------------------------------------------------------------|
|  01 | Opening screen / load previous game?  | `$E36A` [58218]      | Main dispatch calls it at `$E99A` [59802]; input resumes at `$E384` [58244]                                             |
|  02 | Kempston joystick question            | `$E687` [59015]      | Input result handled at `$E69A` [59034]                                                                                 |
|  03 | Number of players                     | `$BCBB` [48315]      | Prompt printed at `$BCD4` [48340]; input handled at `$BCE3` [48355]                                                     |
|  04 | Difficulty level (novice -> expert)   | `$BE89` [48777]      | Selection input handled at `$BE9E` [48798]                                                                              |
|  05 | Player name and team selection        | `$BD07` [48391]      | This is a phase inside `$BCBB`; screen renderer `$BD65` [48485]; player input loop begins `$BD12` [48402]               |
|  06 | Edit novice driver pool               | `$D503` [54531]      | Input handled at `$D521` [54561]; screen constructor `$D56A` [54634]                                                    |
|     | **SEASON LOOP START**                 |                      |                                                                                                                         |
|  07 | Sponsor selection                     | `$B97D` [47485]      | Human-team loop `$BA4C` [47692]; one sponsor-selection screen `$BA78` [47736]                                           |
|  08 | Driver selection                      | `$C906` [51462]      | Human driver-selection screen `$C9F4` [51700]                                                                           |
|     | **GRAND PRIX LOOP START**             |                      |                                                                                                                         |
|  09 | Car and crew acquisition              | `$DD5C` [56668]      | Main screen constructor `$DDCA` [56778]                                                                                 |
|  10 | Race announcement                     | `$CBA9` [52137]      | Called during race preparation at `$C889` [51337]                                                                       |
|  11 | Initial tyre choice                   | `$C8D0` [51408]      | Shared menu renderer `$A6D7` [42711]; keyboard selection `$A691` [42641]                                                |
|  12 | Print starting grid                   | `$D05A` [53338]      | Returns to Grand Prix setup at `$E3F1` [58353]                                                                          |
|     | **RACE LOOP START**                   |                      |                                                                                                                         |
|  13 | Race start (cars lined up)            | `$B724` [46884]      | Starting animation and car movement continue through `$B83A` [47162]                                                    |
|  14 | Tyre choice during pit stop           | `$B54A` [46410]      | Pit-specific header/menu `$A718` [42776]; keyboard selection `$A691` [42641]; shared tyre handler `$A65B` [42587]       |
|  15 | Interactive pit-stop sequence         | `$ADDE` [44510]      | Input sampler `$AEF6` [44790]; interactive update routines `$B071` [45169] and `$B2B0` [45744]                          |
|  16 | Marshal walks in                      | `$A904` [43268]      | Alternate entry `$A91F` [43295]; the race controller calls them at `$E9E8` [59880] and `$E9F5` [59893]                  |
|     | **RACE LOOP END**                     |                      | (Loop through laps)                                                                                                     |
|  17 | Report race results                   | `$CE2D` [52781]      | Results-screen composer `$A476` [42102]; championship-point award loop begins at `$CE54` [52820]                        |
|  18 | Report championship standings         | `$CD09` [52489]      | Screen setup `$CD4F` [52559]; shared column printer `$CD9B` [52635]; called at `$E491` [58513]                          |
|     | **GRAND PRIX LOOP END**               |                      | (Go back to step 09 16 times)                                                                                           |
|  19 | Report winners from the whole season  | `$E8ED` [59629]      | Season-title helper `$E8BF` [59583]; race/winner/team row loop `$E92B` [59691]                                          |
|  20 | Final championship standings          | `$E725` [59173]      | Uses the season-title/table setup at `$CD4F` [52559] and `$E8BF` [59583]; input wait returns at `$E730` [59184]         |
|  21 | Report how each human player finished | `$E77B` [59259]      | Result/advancement logic `$E7BC` [59324]; driver and team-name helpers `$E8AC` [59564] and `$E8B4` [59572]              |
|  22 | Save current game?                    | `$E504` [58628]      | Prompt input loop `$E52F` [58671]; result handled at `$E532` [58674]                                                    |
|  23 | Another season?                       | `$EA42` [59970]      | Input begins at `$EA62` [60002] and is tested at `$EA65` [60005]; a Yes continues through `$BF2E` [48942]               |
|     | **SEASON LOOP END**                   |                      | (Go back to step 07 if you chose to continue)                                                                           |
|  24 | Grand Prix is cancelled (dead end)    | `$E411` [58385]      | Reached between sections 09 and 10: Grand Prix controller `$E3C7` [58311] calls race-worthiness test `$C2BB` [49851] and zero-car detector `$BF5C` [48988]; branch `$E3DC` [58332] enters here |


[//]: # (----------------------------------------------------------------------)
[//]: # (                                                                      )
[//]: # (    Part IV                                                           )
[//]: # (                                                                      )
[//]: # (----------------------------------------------------------------------)
## Part IV: Using `Tweak-F1.py`

### 27. Purpose, scope and safeguards

`Tweak-F1.py` is a command-line patcher for making season variants of the
documented 48K snapshot. It can replace selected names, the opening year, the
sixteen-race calendar and the six team colour schemes. It can also apply the
optional automatic-pit-stop modification described in
[chapter 18](#18-tyre-choice-tyre-wear-and-pit-stops) and reduce the random
repair-incident frequency described in
[chapter 25](#25-random-racing-incidents-and-repair-related-pit-stops). It can
also double the sponsorship-based starting money described in
[chapter 17](#17-sponsorship-and-computer-team-finances).

Every modification option is independent. An omitted option leaves its
corresponding game data untouched, while several options may be combined to
produce one new snapshot. The script no longer imports fonts and does not
create previews, manifests, JSON files or separate output directories.

The script is deliberately tied to the fixed layout documented here. It is not
a general SNA editor, nor does it try to discover equivalent tables in an
unrelated version of the game.

#### Option-to-memory cross-reference

The following table connects the user-facing options with the detailed
technical descriptions elsewhere in this document.

| Option                              | Principal effect                                      | Relevant chapter |
|-------------------------------------|-------------------------------------------------------|------------------|
| `--year`                            | changes the opening season and previous-winner bases  | [chapter 12](#12-season-years-and-previous-winners) |
| `--teams`                           | replaces up to six team-name records                  | [chapter 5](#5-text-tables) |
| `--drivers`                         | replaces up to 24 editable driver-name records        | [chapter 5](#5-text-tables) |
| `--sponsors`                        | replaces up to thirteen sponsor-name records          | [chapter 5](#5-text-tables) |
| `--races`                           | replaces race names, circuits and lap counts          | [chapter 11](#11-original-1985-race-data) |
| `--colours` / `--colors`            | recolours cars, number panels and grid-number boxes   | [chapters 6-9](#6-team-colours-and-spectrum-attribute-bytes) |
| `--double-starting-money`           | doubles human-team starting balances every season     | [chapter 17](#17-sponsorship-and-computer-team-finances) |
| `--automatic-human-pit-stops`       | includes human cars in the automatic pit scheduler    | [chapter 18](#18-tyre-choice-tyre-wear-and-pit-stops) |
| `--random-incidents`                | selects the 1/32, 1/64 or 1/128 incident gate         | [chapter 25](#25-random-racing-incidents-and-repair-related-pit-stops) |

`--game` selects the source snapshot and `--suffix` determines the output
filename; neither is itself a game-data modification.

#### Script safety checks

The script applies several safeguards before writing an output file:

1. The source must be exactly 49,179 bytes, the size of a standard 48K SNA.
2. Names, colours, years and race entries are fully validated before use.
3. All changes are assembled in memory before the output file is written.
4. Every permitted write records its SNA offsets. The finished result is
   rejected if any changed byte lies outside those recorded offsets.
5. The year patch checks for the expected `LD HL,nn` opcodes.
6. The automatic-pit-stop patch accepts only the two verified jump
   instructions or an already-patched sequence of three `NOP` instructions.
7. The double-starting-money patch accepts only the verified original or
   optional call-site sequence and its documented wrapper.
8. The random-incident patch accepts only the verified `original`, `reduced`
   or `rare` instruction block at `$C210-$C228` [49680-49704].
9. The script refuses to use the source snapshot itself as the output path.

These checks protect the original and catch unexpected layouts or accidental
writes. They do not make an arbitrary snapshot compatible with this memory
map; the selected source must still use the documented game layout.

### 28. Command-line use

#### Requirements

The script requires Python 3.10 or newer and uses only the Python standard
library. No additional packages need to be installed. From PowerShell, its
built-in help can be displayed with:

```powershell
python .\Tweak-F1.py --help
```

On a Windows installation that provides the Python launcher, `py` may be used
instead of `python`.

#### Basic syntax

Every invocation requires a source snapshot and an output suffix, followed by
at least one modification option:

```powershell
python .\Tweak-F1.py `
    --game=SOURCE.sna `
    --suffix=OUTPUT-SUFFIX `
    MODIFICATION-OPTION
```

`MODIFICATION-OPTION` is a placeholder in the example, not literal text. It
may be replaced by one or more of `--year`, `--teams`, `--drivers`,
`--sponsors`, `--races`, `--colours` or
`--double-starting-money`, `--automatic-human-pit-stops`, or by
`--random-incidents` with its required value.

Options that take a value accept either an equals sign or a following
argument. For example, `--year=1991` and `--year 1991` are equivalent.
Likewise, `--random-incidents=rare` and `--random-incidents rare` are
equivalent. `--automatic-human-pit-stops` is a switch and takes no value.
`--double-starting-money` is also a switch and takes no value.

If no modification option is supplied, the script reports that there is
nothing to do and writes no SNA file.

#### Command-line options

| Option                              | Value             | Required | Meaning |
|-------------------------------------|-------------------|:--------:|---------|
| `--game`                            | SNA path          | yes      | source 48K snapshot |
| `--suffix`                          | filename text     | yes      | suffix added to the output filename |
| `--year`                            | four-digit year   | no       | opening championship season |
| `--teams`                           | text-file path    | no       | team-name list |
| `--drivers`                         | text-file path    | no       | driver-name list |
| `--sponsors`                        | text-file path    | no       | sponsor-name list |
| `--races`                           | text-file path    | no       | complete sixteen-race schedule |
| `--colours`, `--colors`             | text-file path    | no       | team-colour list |
| `--double-starting-money`           | none              | no       | double human-team starting balances every season |
| `--automatic-human-pit-stops`       | none              | no       | enable automatic stops for human cars |
| `--random-incidents`                | `original`, `reduced` or `rare` | no | select a 1/32, 1/64 or 1/128 incident rate |

The year must be a four-digit integer from 1000 through 9999. The file-based
options are described in [chapter 29](#29-input-file-formats) below.

#### Examples

The following command constructs a 1991 variant using every text and colour
input:

```powershell
python .\Tweak-F1.py `
    --game=F1-2026-Mod.sna `
    --suffix=Season-1991 `
    --year=1991 `
    --teams=teams_1991.txt `
    --drivers=drivers_1991.txt `
    --sponsors=sponsors_1991.txt `
    --races=races_1991.txt `
    --colours=colours_1991.txt
```

The automatic-pit-stop change can be applied on its own:

```powershell
python .\Tweak-F1.py `
    --game=F1-2026-Mod.sna `
    --suffix=Automatic-Pit-Stops `
    --automatic-human-pit-stops
```

It may instead be combined with a season variant by adding the switch to the
first command. If the option is omitted, human-controlled cars retain the
original manual-pit-stop behaviour.

Starting money can be doubled independently for every season:

```powershell
python .\Tweak-F1.py `
    --game=F1-2026-Mod.sna `
    --suffix=Double-Starting-Money `
    --double-starting-money
```

If the option is omitted, the original sponsorship-based starting balance is
preserved.

The random-incident frequency can be reduced independently:

```powershell
python .\Tweak-F1.py `
    --game=F1-2026-Mod.sna `
    --suffix=Rare-Incidents `
    --random-incidents=rare
```

`reduced` selects 1/64 and `rare` selects 1/128. `original` restores the
original 1/32 instruction block in a previously patched snapshot. If the
option is omitted, the incident gate in the source is preserved.

#### Output naming and overwriting

The output is written directly to the current working directory. Its name is
formed from the source filename stem and the mandatory suffix:

```text
F1-2026-Mod.sna + --suffix=Season-1991
    -> F1-2026-Mod-Season-1991.sna
```

The suffix cannot be empty, `.` or `..`, and cannot contain `/` or `\`.

An existing output file with the same generated name is overwritten without a
prompt. The source snapshot is never overwritten, even if a suffix would
otherwise produce the same path. No file is written when validation fails;
the error is printed with an `ERROR:` prefix and the script exits with a
nonzero status.

### 29. Input-file formats

#### Common input-file rules

All text input files follow these general rules:

- blank lines are ignored;
- lines whose first non-space character is `#` are comments;
- surrounding spaces on an entry are removed;
- UTF-8 files, with or without a byte-order mark, can be read;
- names stored in the snapshot must contain ASCII characters only.

Short names are padded with spaces to the fixed record width expected by the
game. An omitted file option leaves the corresponding table untouched. A
shorter name or colour list replaces the first entries only and preserves the
remaining original records.

#### Team-name file

`--teams` accepts from one through six names, one per line. Each name may
contain at most 8 ASCII characters.

```text
McLaren
Williams
Ferrari
Benetton
Jordan
Minardi
```

The order is significant: the first line replaces team 1, the second replaces
team 2, and so on. Team order and the associated fixed car numbers are not
rearranged.

#### Driver-name file

`--drivers` accepts from one through 24 names, one per line. Each name may
contain at most 10 ASCII characters.

```text
Senna
Mansell
Patrese
Berger
Prost
Piquet
```

The first line replaces editable driver record 1. Supplying fewer than 24
names leaves the later driver records unchanged. The two special labels after
the 24 editable records are always preserved.

#### Sponsor-name file

`--sponsors` accepts from one through thirteen names, one per line. Each name
may contain at most 12 ASCII characters.

```text
Marlboro
Shell
Boss
Canon
Labatts
Elf
```

The order is again positional. The script changes sponsor names only; it does
not alter the associated starting-fund values or team sponsor assignments.

#### Race-schedule file

`--races` requires exactly sixteen nonblank, non-comment entries. Every entry
has three fields separated by vertical bars:

```text
Phoenix | Phoenix Street    | 81
Brazil  | Interlagos        | 71
SMarino | Imola             | 61
Monaco  | Circuit de Monaco | 78
```

The complete file must contain another twelve entries. The limits are:

- race name: 1-8 ASCII characters;
- circuit name: 1-18 ASCII characters;
- lap count: an integer from 1 through 99.

Race names are right-aligned in the primary table and centred in the separate
race-display copy. Circuit names are left-aligned. The script writes all five
required regions listed in [chapter 11](#11-original-1985-race-data): both
race-name copies, circuit names, binary lap counts and the displayed two-digit
lap counts.

The remaining per-race timing, record, winner, length and year data are not
changed. They remain associated with their original calendar slots, as
explained in [chapter 11](#11-original-1985-race-data).

#### Team-colour file

`--colours` (or its American-English alias `--colors`) accepts from one through
six entries, one team per line. The recommended explicit format is:

```text
BRIGHTNESS PRIMARY SECONDARY
```

For example:

```text
bright blue blue
dim red red
bright white black
```

`BRIGHTNESS` may be `bright` or `dim` and applies only to the primary paint.
Secondary paint is always non-bright, so no second brightness word is used.
Accepted colour names are `black`, `blue`, `red`, `magenta`, `green`, `cyan`,
`yellow` and `white`; `purple` is accepted as an alias for `magenta`. Numeric
Spectrum colour values `0` through `7` are also accepted, although names are
clearer.

White has two deliberate restrictions because ordinary non-bright white
blends into the grey road:

- a white primary must be written explicitly as `bright white`;
- white is not allowed as a secondary colour.

For compatibility with earlier input files, a one-word entry such as `blue`
means `bright blue blue`, and `blue red` means `bright blue red`. Explicit
three-field entries are preferable because they state the intended primary
brightness unambiguously.

Changing colours updates more than the six-byte team palette. The script also
repaints the side-view and top-view attribute maps, secondary body outlines,
cockpit curves, side/top car-number panels and starting-grid number boxes.
The detailed paint masks and contrast rules are documented in chapters
[6](#6-team-colours-and-spectrum-attribute-bytes),
[7](#7-side-view-car-graphics), [8](#8-top-view-car-graphics) and
[9](#9-starting-grid-number-boxes).
