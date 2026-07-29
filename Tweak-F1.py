#!/usr/bin/env python3
"""Make simple text, season, schedule and colour variants of Formula One.

Example:

    python Tweak-f1.py --year=1991 --teams=teams.txt --drivers=drivers.txt \
        --sponsors=sponsors.txt --races=races.txt --colours=colours.txt \
        --game=F1-game.sna --suffix=Season-1991

    python Tweak-F1.py --automatic-human-pit-stops \
        --game=F1-game.sna --suffix=Automatic-Pit-Stops

    python Tweak-F1.py --random-incidents=rare \
        --game=F1-game.sna --suffix=Rare-Incidents

Each names file contains one name per line. Empty lines and lines beginning
with # are ignored. A races file contains exactly sixteen pipe-separated lines
in the form RACE | CIRCUIT | LAPS. The source snapshot is never overwritten.
The mandatory --suffix option names the result: --game=F1-2026-Mod.sna
--suffix=Season-1991 writes F1-2026-Mod-Season-1991.sna. Generated SNA files
are written directly to the current working directory, overwriting any
existing file of that name without prompting; no previews, manifests, JSON
files or output directories are created.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


# =============================================================================
# 1. Snapshot layout and fixed Formula One memory addresses
#
# A 48K .sna file contains a 27-byte CPU-register header followed by the full
# 48 KiB RAM image for Z80 addresses $4000-$FFFF. The constants below are Z80
# addresses inside that RAM image, not ordinary positions in the .sna file.
# =============================================================================

SNA_SIZE = 49_179
SNA_HEADER_SIZE = 27
RAM_BASE = 0x4000

# Fixed-width driver-name records. Record zero is deliberately left blank.
DRIVER_NAMES_ADDRESS = 0x6E87
DRIVER_RECORD_SIZE = 10
FIRST_DRIVER_RECORD = 1       # Record zero is blank.
EDITABLE_DRIVER_RECORDS = 24  # Records 25 and 26 are special game labels.

# Six editable team-name records follow a blank record.
TEAM_NAMES_ADDRESS = 0x6F95
TEAM_RECORD_SIZE = 8
FIRST_TEAM_RECORD = 1         # Record zero is blank.
EDITABLE_TEAM_RECORDS = 6     # Records 7 and 8 are status/extra labels.

# Sponsor records begin directly at this address; there is no blank record.
SPONSOR_NAMES_ADDRESS = 0x8771
SPONSOR_RECORD_SIZE = 12
EDITABLE_SPONSOR_RECORDS = 13

# The schedule has two copies of sixteen right-aligned eight-byte race names,
# one table of left-aligned 18-byte circuit names, one binary lap byte per race,
# and a separate display row of sixteen two-digit lap strings.
RACE_COUNT = 16
RACE_NAME_RECORD_SIZE = 8
RACE_NAMES_ADDRESS = 0x7025
RACE_DISPLAY_NAMES_ADDRESS = 0x9402
CIRCUIT_NAME_RECORD_SIZE = 18
CIRCUIT_NAMES_ADDRESS = 0x70A5
RACE_LAPS_ADDRESS = 0x6AD5
RACE_DISPLAY_LAPS_ADDRESS = 0x9486  # Four-byte "Laps" label begins at $9482.

# Team palette and the two sets of car colour-attribute maps.
TEAM_PALETTE_ADDRESS = 0x6FDD
SIDE_COLOUR_MAP_ADDRESS = 0x6CB8
SIDE_COLOUR_MAP_SIZE = 20      # 10 x 2 Spectrum attribute cells per team.
SIDE_NUMBER_ATTRIBUTE_INDEX = 5  # Zero-based cell containing the overlaid glyph.
TOP_COLOUR_MAP_ADDRESS = 0x8094
TOP_COLOUR_MAP_SIZE = 55       # 11 x 5 Spectrum attribute cells per team.
TOP_NUMBER_ATTRIBUTE_INDEX = 30
# Three non-bright outline cells above and below each top-view car body.
TOP_SECONDARY_LINE_INDICES = (4, 5, 6, 48, 49, 50)
# Seven panels whose PAPER pixels draw the curved lines around the cockpit.
TOP_COCKPIT_CURVE_INDICES = (15, 16, 17, 28, 37, 38, 39)

# Each starting-grid number has a record containing four attribute bytes.
GRID_NUMBER_RECORD_ADDRESS = 0x8FD3
GRID_NUMBER_RECORD_SIZE = 0x24
GRID_NUMBER_ATTRIBUTES_OFFSET = 0x20

# Five LD HL,nn instructions form the displayed season and previous-winner
# years by adding the game's existing season-offset counter to these bases.
SEASON_YEAR_BASE_INSTRUCTIONS = (0x9854, 0xCCF0, 0xE64C, 0xE8D7)
PREVIOUS_WINNER_YEAR_BASE_INSTRUCTION = 0xCC93
LD_HL_IMMEDIATE_OPCODE = 0x21

# Two three-byte JP NZ instructions skip the automatic pit-stop scheduler when
# the corresponding team is human-controlled. Replacing each complete
# instruction with NOPs lets the existing scheduler evaluate all twelve cars.
AUTOMATIC_HUMAN_PIT_STOP_JUMPS = (
    (0xD23A, bytes((0xC2, 0x40, 0xD2))),
    (0xD2EE, bytes((0xC2, 0xF4, 0xD2))),
)
THREE_NOPS = bytes((0x00, 0x00, 0x00))

# The original random-incident gate at $C210 requires five random bits to be
# set, giving one incident chance in 32 per car per lap. The compact replacement
# tests six or seven bits and pads the remainder of the original 25-byte block
# with NOPs, leaving the following CALL at $C229 at its original address.
RANDOM_INCIDENT_GATE_ADDRESS = 0xC210
RANDOM_INCIDENT_GATE_SIZE = 25
RANDOM_INCIDENT_GATES = {
    "original": bytes.fromhex(
        "CB 6F CA E4 C0 "
        "CB 67 CA E4 C0 "
        "CB 5F CA E4 C0 "
        "CB 57 CA E4 C0 "
        "CB 4F CA E4 C0"
    ),
    "reduced": bytes.fromhex("E6 3F FE 3F C2 E4 C0") + bytes(18),
    "rare": bytes.fromhex("E6 7F FE 7F C2 E4 C0") + bytes(18),
}
if any(len(gate) != RANDOM_INCIDENT_GATE_SIZE for gate in RANDOM_INCIDENT_GATES.values()):
    raise ValueError("Invalid built-in random-incident gate")

# Standard ZX Spectrum colour numbers used by the INK and PAPER attribute bits.
COLOURS = {
    "black": 0,
    "blue": 1,
    "red": 2,
    "magenta": 3,
    "purple": 3,
    "green": 4,
    "cyan": 5,
    "yellow": 6,
    "white": 7,
}


# =============================================================================
# 2. Attribute-map paint masks
#
# Each character in a mask describes one attribute cell in row-major order.
# The mask says which colour component belongs to the team's paint and may be
# changed without recolouring tyres, the cockpit or fixed mechanical details.
# =============================================================================

def paint_mask(pattern: str, expected_size: int) -> bytes:
    """Turn a readable string of mask digits into validated numeric masks."""
    result = bytes(int(character) for character in pattern)
    if len(result) != expected_size or any(value > 3 for value in result):
        raise ValueError("Invalid built-in paint mask")
    return result


def paint_roles(pattern: str, expected_size: int) -> bytes:
    """Build a fixed map in which P is primary and S is secondary paint."""
    if len(pattern) != expected_size or any(
        character not in ".PS" for character in pattern
    ):
        raise ValueError("Invalid built-in paint-role map")
    return bytes(character == "P" for character in pattern)


# Each mask value identifies the paint-bearing part of one Spectrum attribute:
# 0 = neither, 1 = INK, 2 = PAPER, 3 = both. These masks describe the six
# verified MOD2020-derived liveries in the final game, while excluding tyres,
# cockpit, number panels and other fixed mechanical/detail colours.
SIDE_PAINT_MASKS = (
    paint_mask("11011112010101011021", SIDE_COLOUR_MAP_SIZE),
    paint_mask("11011112010001011021", SIDE_COLOUR_MAP_SIZE),
    # Lotus begins as a black car with fixed yellow detailing. Its paint cells
    # cannot be discovered merely by looking for a non-black team hue, so use
    # the verified shared body-cell layout while leaving the yellow cells out.
    paint_mask("11011112010101011021", SIDE_COLOUR_MAP_SIZE),
    paint_mask("11011112010101011021", SIDE_COLOUR_MAP_SIZE),
    paint_mask("11011112010101011021", SIDE_COLOUR_MAP_SIZE),
    paint_mask("11011112010101011021", SIDE_COLOUR_MAP_SIZE),
)

TOP_PAINT_MASKS = (
    paint_mask(
        "0000111000010011110111111101101111001111011100001110000",
        TOP_COLOUR_MAP_SIZE,
    ),
    paint_mask(
        "0000111000010011110111111101101111001111011100001110000",
        TOP_COLOUR_MAP_SIZE,
    ),
    paint_mask(
        "0000111000010011110111111101101111001111011100001110000",
        TOP_COLOUR_MAP_SIZE,
    ),
    paint_mask(
        "0000111000010011110111111101101111001111011100001110000",
        TOP_COLOUR_MAP_SIZE,
    ),
    paint_mask(
        "0000111000010011110111111101101111001111011100001110000",
        TOP_COLOUR_MAP_SIZE,
    ),
    paint_mask(
        "0000111000010011110111111101101111001111011100001110000",
        TOP_COLOUR_MAP_SIZE,
    ),
)

# These role maps are intentionally independent of the current BRIGHT bits.
# Consequently, a snapshot produced with dim primary paint can safely be used
# as the input to a later run: primary and secondary cells remain distinguishable.
SIDE_PRIMARY_ROLES = paint_roles("SS.SPPPS.S.S.S.SS.PS", SIDE_COLOUR_MAP_SIZE)
TOP_PRIMARY_ROLES = paint_roles(
    "....SSS....S..SPPP.PPSSSSS.SS.PPSS..SPPP.PPS....SSS....",
    TOP_COLOUR_MAP_SIZE,
)


# =============================================================================
# 3. Small data objects passed between input parsing and snapshot patching
# =============================================================================

@dataclass(frozen=True)
class ColourPair:
    """Primary/detail hues plus the optional BRIGHT state of primary paint."""

    primary: int
    secondary: int
    primary_bright: bool = True


@dataclass(frozen=True)
class RaceEntry:
    """One validated fixed-width race name, circuit name and lap count."""

    name: bytes
    circuit: bytes
    laps: int


# =============================================================================
# 4. Address conversion
# =============================================================================

def sna_offset(address: int) -> int:
    """Convert a Z80 RAM address into its byte offset inside a 48K .sna."""
    return SNA_HEADER_SIZE + address - RAM_BASE


# =============================================================================
# 5. Plain-text name, race-schedule and colour-list parsing
#
# Blank lines and lines beginning with # are comments. Keeping line numbers
# allows validation errors to point to the exact offending entry.
# =============================================================================

def read_names(path: Path, maximum: int, width: int, kind: str) -> list[bytes]:
    """Read, validate and space-pad a fixed-width game name table."""
    names: list[tuple[int, str]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        name = line.strip()
        if not name or name.startswith("#"):
            continue
        names.append((line_number, name))

    if not names:
        raise ValueError(f"{path}: no {kind} names found")
    if len(names) > maximum:
        raise ValueError(
            f"{path}: found {len(names)} {kind} names; the game supports at most "
            f"{maximum}"
        )

    # The Spectrum game expects raw single-byte text and fixed-width records.
    # ASCII therefore avoids silently writing an unsupported character code.
    encoded: list[bytes] = []
    for line_number, name in names:
        try:
            value = name.encode("ascii")
        except UnicodeEncodeError as error:
            raise ValueError(
                f"{path}:{line_number}: {kind} name {name!r} must use ASCII characters"
            ) from error
        if len(value) > width:
            raise ValueError(
                f"{path}:{line_number}: {kind} name {name!r} is {len(value)} "
                f"characters; the game allows {width}"
            )
        encoded.append(value.ljust(width, b" "))
    return encoded


def read_races(path: Path) -> list[RaceEntry]:
    """Read exactly sixteen `RACE | CIRCUIT | LAPS` schedule entries."""
    entries: list[tuple[int, str]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        entries.append((line_number, value))

    if len(entries) != RACE_COUNT:
        raise ValueError(
            f"{path}: found {len(entries)} races; the game requires exactly "
            f"{RACE_COUNT}"
        )

    races: list[RaceEntry] = []
    for line_number, value in entries:
        fields = [field.strip() for field in value.split("|")]
        if len(fields) != 3:
            raise ValueError(
                f"{path}:{line_number}: expected RACE | CIRCUIT | LAPS, "
                "for example 'Brazil | Interlagos | 71'"
            )
        name, circuit, laps_text = fields

        try:
            encoded_name = name.encode("ascii")
        except UnicodeEncodeError as error:
            raise ValueError(
                f"{path}:{line_number}: race name {name!r} must use ASCII characters"
            ) from error
        if not encoded_name:
            raise ValueError(f"{path}:{line_number}: race name cannot be empty")
        if len(encoded_name) > RACE_NAME_RECORD_SIZE:
            raise ValueError(
                f"{path}:{line_number}: race name {name!r} is {len(encoded_name)} "
                f"characters; the game allows {RACE_NAME_RECORD_SIZE}"
            )

        try:
            encoded_circuit = circuit.encode("ascii")
        except UnicodeEncodeError as error:
            raise ValueError(
                f"{path}:{line_number}: circuit name {circuit!r} must use "
                "ASCII characters"
            ) from error
        if not encoded_circuit:
            raise ValueError(f"{path}:{line_number}: circuit name cannot be empty")
        if len(encoded_circuit) > CIRCUIT_NAME_RECORD_SIZE:
            raise ValueError(
                f"{path}:{line_number}: circuit name {circuit!r} is "
                f"{len(encoded_circuit)} characters; the game allows "
                f"{CIRCUIT_NAME_RECORD_SIZE}"
            )

        try:
            laps = int(laps_text, 10)
        except ValueError as error:
            raise ValueError(
                f"{path}:{line_number}: lap count {laps_text!r} is not an integer"
            ) from error
        if not 1 <= laps <= 99:
            raise ValueError(
                f"{path}:{line_number}: lap count {laps} is outside the supported "
                "range 1-99"
            )

        # Short race names use leading spaces (b"  Brazil"), whereas circuit
        # names use trailing spaces (b"Interlagos        ") in the stock game.
        races.append(
            RaceEntry(
                encoded_name.rjust(RACE_NAME_RECORD_SIZE, b" "),
                encoded_circuit.ljust(CIRCUIT_NAME_RECORD_SIZE, b" "),
                laps,
            )
        )
    return races


def read_colours(path: Path) -> list[ColourPair]:
    """Read up to six [BRIGHT|DIM] PRIMARY SECONDARY team-colour entries."""
    lines: list[tuple[int, str]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        lines.append((line_number, value))

    if not lines:
        raise ValueError(f"{path}: no team colours found")
    if len(lines) > 6:
        raise ValueError(f"{path}: found {len(lines)} colour pairs; the game has six teams")

    result: list[ColourPair] = []
    choices = ", ".join(
        ("black", "blue", "red", "magenta", "green", "cyan", "yellow", "white")
    )
    for line_number, line in lines:
        # Recommended: "dim red red" or "bright blue yellow". The brightness
        # word controls primary paint only; secondary paint is invariably dim.
        # Legacy "blue red" and one-word "blue" entries remain accepted and
        # imply a bright primary colour.
        words = re.sub(r"[-,/]+", " ", line.casefold()).split()
        primary_bright = True
        brightness_explicit = False
        if len(words) == 1:
            words.append(words[0])
        elif len(words) == 2 and words[0] in ("bright", "dim"):
            brightness_explicit = True
            primary_bright = words.pop(0) == "bright"
            words.append(words[0])
        elif len(words) == 3 and words[0] in ("bright", "dim"):
            brightness_explicit = True
            primary_bright = words.pop(0) == "bright"
        if len(words) != 2:
            raise ValueError(
                f"{path}:{line_number}: expected BRIGHTNESS PRIMARY SECONDARY, "
                f"for example 'dim red red'"
            )
        values: list[int] = []
        for word in words:
            if word in COLOURS:
                values.append(COLOURS[word])
            elif len(word) == 1 and word in "01234567":
                values.append(int(word))
            else:
                raise ValueError(
                    f"{path}:{line_number}: unknown Spectrum colour {word!r}; "
                    f"choose {choices}"
                )
        if values[0] == COLOURS["white"]:
            if not brightness_explicit:
                raise ValueError(
                    f"{path}:{line_number}: white primary must explicitly say "
                    "'bright white', for example 'bright white black'"
                )
            if not primary_bright:
                raise ValueError(
                    f"{path}:{line_number}: dim white cannot be a primary colour "
                    "because it would blend into the road; use 'bright white'"
                )
        if values[1] == COLOURS["white"]:
            raise ValueError(
                f"{path}:{line_number}: white cannot be a secondary colour "
                "because secondary paint is always dim and would blend into the road"
            )
        result.append(ColourPair(values[0], values[1], primary_bright))
    return result


# =============================================================================
# 6. Low-level fixed-record writing
#
# Every write records its file offsets in allowed_offsets. make_variant() later
# uses that set as a safety check against accidental changes elsewhere in RAM.
# =============================================================================

def write_records(
    snapshot: bytearray,
    base_address: int,
    first_record: int,
    records: list[bytes],
    allowed_offsets: set[int],
) -> None:
    """Write consecutive fixed-width records into one known game table."""
    if not records:
        return
    width = len(records[0])
    for index, record in enumerate(records):
        address = base_address + (first_record + index) * width
        offset = sna_offset(address)
        snapshot[offset : offset + width] = record
        allowed_offsets.update(range(offset, offset + width))


def apply_race_schedule(
    snapshot: bytearray,
    races: list[RaceEntry],
    allowed_offsets: set[int],
) -> None:
    """Write race names, circuit names and laps into every required table."""
    if not races:
        return
    if len(races) != RACE_COUNT:
        raise ValueError(f"A complete schedule must contain {RACE_COUNT} races")

    names = [race.name for race in races]
    circuits = [race.circuit for race in races]
    write_records(snapshot, RACE_NAMES_ADDRESS, 0, names, allowed_offsets)
    write_records(snapshot, CIRCUIT_NAMES_ADDRESS, 0, circuits, allowed_offsets)

    # $9402 is a separate, dedicated copy read only by the in-race HUD banner
    # (drawn via a fixed-position, no-trim glyph blitter at $9EC5). Unlike the
    # announcement/track-report table above, it is not shown next to other
    # text on the same line, so it is centred here instead of reusing the
    # right-justified `names`: this keeps the visible word roughly centred
    # under/over the fixed "Grand Prix" line beneath it for any name length,
    # rather than flush to one edge. When the padding is odd, the extra blank
    # cell goes on the right (Python's bytes.center() convention), e.g.
    # b"Brazil" (6) -> b" Brazil ", b"Dutch" (5) -> b" Dutch  ". The original
    # 1985 table used pure right-justification for every entry (all padding
    # on the left, none on the right; e.g. b"  Brazil", b"   Dutch"), so there
    # is no historical centring convention to match here - this is a new,
    # independent choice for this one table.
    display_names = [name.strip().center(RACE_NAME_RECORD_SIZE, b" ") for name in names]
    write_records(snapshot, RACE_DISPLAY_NAMES_ADDRESS, 0, display_names, allowed_offsets)

    binary_laps = bytes(race.laps for race in races)
    lap_offset = sna_offset(RACE_LAPS_ADDRESS)
    snapshot[lap_offset : lap_offset + RACE_COUNT] = binary_laps
    allowed_offsets.update(range(lap_offset, lap_offset + RACE_COUNT))

    # The track-summary table is text, not binary: 71 laps is stored as b"71".
    display_laps = b"".join(f"{race.laps:02d}".encode("ascii") for race in races)
    display_offset = sna_offset(RACE_DISPLAY_LAPS_ADDRESS)
    snapshot[display_offset : display_offset + len(display_laps)] = display_laps
    allowed_offsets.update(range(display_offset, display_offset + len(display_laps)))


# =============================================================================
# 7. Spectrum attribute and team-colour rules
#
# Attribute byte: bit 7 FLASH, bit 6 BRIGHT, bits 5-3 PAPER, bits 2-0 INK.
# Fixed role maps identify primary and secondary panels even after primary paint
# has been made dim. Component masks decide whether INK, PAPER, both, or neither
# belongs to the paint in each cell. Secondary panels are invariably dim.
# =============================================================================

def recolour_attribute(
    attribute: int,
    mask: int,
    is_primary: bool,
    primary: int,
    secondary: int,
    primary_bright: bool,
) -> int:
    """Apply one paint role, its hue and its required panel brightness."""
    colour = primary if is_primary else secondary
    if is_primary and primary_bright:
        attribute |= 0x40
    else:
        attribute &= ~0x40
    if mask & 1:
        attribute = (attribute & ~0x07) | colour
    if mask & 2:
        attribute = (attribute & ~0x38) | (colour << 3)
    return attribute


def team_number_colour(primary: int) -> int:
    """Choose a readable number solely from the team's primary/base colour.

    Blue and red use white; black uses yellow; every other permitted primary
    colour uses black. Secondary paint never affects car numbers.
    """
    if primary in (COLOURS["blue"], COLOURS["red"]):
        return COLOURS["white"]
    if primary == COLOURS["black"]:
        return COLOURS["yellow"]
    return COLOURS["black"]


def cockpit_curve_colour(panel_colour: int) -> int:
    """Choose black or white curves from the body colour in one top-view panel.

    The decision is deliberately panel-local. A mixed primary/secondary livery
    can therefore have white curves over a blue panel and black curves over a
    yellow panel, even where both panels belong to the same car.
    """
    if panel_colour in (
        COLOURS["black"],
        COLOURS["blue"],
        COLOURS["red"],
    ):
        return COLOURS["white"]
    return COLOURS["black"]


def number_panel_attribute(
    attribute: int, primary: int, primary_bright: bool
) -> int:
    """Build a side/top number cell from primary hue and brightness."""
    # The overlaid car-number glyph is reversed: its visible pixels use PAPER,
    # while the surrounding body uses INK.
    number = team_number_colour(primary)
    bright_bit = 0x40 if primary_bright else 0
    return (attribute & 0x80) | bright_bit | (number << 3) | primary


def apply_team_colours(
    snapshot: bytearray,
    colours: list[ColourPair],
    allowed_offsets: set[int],
) -> None:
    """Apply team colours to palette, car maps, number panels and grid boxes."""
    for team, pair in enumerate(colours):
        # This one-byte palette is used by other game screens and logic.
        palette_offset = sna_offset(TEAM_PALETTE_ADDRESS + team)
        snapshot[palette_offset] = pair.primary
        allowed_offsets.add(palette_offset)

        # Recolour the shared side-view and top-view attribute maps. The bitmap
        # shapes are shared; these maps give each team its individual livery.
        for base, size, mask, primary_roles in (
            (
                SIDE_COLOUR_MAP_ADDRESS,
                SIDE_COLOUR_MAP_SIZE,
                SIDE_PAINT_MASKS[team],
                SIDE_PRIMARY_ROLES,
            ),
            (
                TOP_COLOUR_MAP_ADDRESS,
                TOP_COLOUR_MAP_SIZE,
                TOP_PAINT_MASKS[team],
                TOP_PRIMARY_ROLES,
            ),
        ):
            map_offset = sna_offset(base + team * size)
            for index, component_mask in enumerate(mask):
                if component_mask:
                    snapshot[map_offset + index] = recolour_attribute(
                        snapshot[map_offset + index],
                        component_mask,
                        bool(primary_roles[index]),
                        pair.primary,
                        pair.secondary,
                        pair.primary_bright,
                    )
                    allowed_offsets.add(map_offset + index)

        # The three upper and three lower body-outline cells always use
        # secondary-colour INK without BRIGHT. PAPER and FLASH are retained.
        top_map_offset = sna_offset(TOP_COLOUR_MAP_ADDRESS + team * TOP_COLOUR_MAP_SIZE)
        for index in TOP_SECONDARY_LINE_INDICES:
            attribute_offset = top_map_offset + index
            snapshot[attribute_offset] = (
                snapshot[attribute_offset] & ~0x47
            ) | pair.secondary
            allowed_offsets.add(attribute_offset)

        # The curved cockpit detail is stored in PAPER, while the body paint in
        # each of these panels is INK. Select black/white contrast independently
        # for every panel after its primary or secondary paint has been applied.
        for index in TOP_COCKPIT_CURVE_INDICES:
            attribute_offset = top_map_offset + index
            attribute = snapshot[attribute_offset]
            body_colour = attribute & 0x07
            curve_colour = cockpit_curve_colour(body_colour)
            snapshot[attribute_offset] = (
                attribute & ~0x38
            ) | (curve_colour << 3)
            allowed_offsets.add(attribute_offset)

        # Make the side and top number panels identical. Their number colour is
        # selected solely from the primary/base paint; secondary paint is never
        # consulted.
        side_number_offset = sna_offset(
            SIDE_COLOUR_MAP_ADDRESS
            + team * SIDE_COLOUR_MAP_SIZE
            + SIDE_NUMBER_ATTRIBUTE_INDEX
        )
        top_number_offset = sna_offset(
            TOP_COLOUR_MAP_ADDRESS
            + team * TOP_COLOUR_MAP_SIZE
            + TOP_NUMBER_ATTRIBUTE_INDEX
        )
        side_number = number_panel_attribute(
            snapshot[side_number_offset], pair.primary, pair.primary_bright
        )
        snapshot[side_number_offset] = side_number
        snapshot[top_number_offset] = side_number
        allowed_offsets.add(side_number_offset)
        allowed_offsets.add(top_number_offset)

        # Two grid numbers belong to every team. Here the ordinary glyph uses
        # INK for the visible number and primary paint as its PAPER background.
        for car in (team * 2, team * 2 + 1):
            attribute_address = (
                GRID_NUMBER_RECORD_ADDRESS
                + car * GRID_NUMBER_RECORD_SIZE
                + GRID_NUMBER_ATTRIBUTES_OFFSET
            )
            attribute_offset = sna_offset(attribute_address)
            for index in range(4):
                attribute = snapshot[attribute_offset + index]
                ink = team_number_colour(pair.primary)
                bright_bit = 0x40 if pair.primary_bright else 0
                snapshot[attribute_offset + index] = (
                    (attribute & 0x80)
                    | bright_bit
                    | (pair.primary << 3)
                    | ink
                )
                allowed_offsets.add(attribute_offset + index)


# =============================================================================
# 8. Starting-season year constants
# =============================================================================

def apply_starting_year(
    snapshot: bytearray,
    year: int,
    allowed_offsets: set[int],
) -> None:
    """Set the opening season and its corresponding previous-winner year."""
    # New-game setup advances the offset from zero to one before displaying the
    # opening season. Therefore Y-1 produces season Y, while Y-2 produces the
    # previous-winner label Y-1. Later seasons continue incrementing normally.
    year_bases = (
        *((address, year - 1) for address in SEASON_YEAR_BASE_INSTRUCTIONS),
        (PREVIOUS_WINNER_YEAR_BASE_INSTRUCTION, year - 2),
    )
    for instruction_address, base_year in year_bases:
        instruction_offset = sna_offset(instruction_address)
        if snapshot[instruction_offset] != LD_HL_IMMEDIATE_OPCODE:
            raise ValueError(
                f"Unexpected snapshot layout at ${instruction_address:04X}; "
                "expected an LD HL,nn year instruction"
            )
        operand = base_year.to_bytes(2, "little")
        snapshot[instruction_offset + 1 : instruction_offset + 3] = operand
        allowed_offsets.update((instruction_offset + 1, instruction_offset + 2))


# =============================================================================
# 9. Optional gameplay-code patches
# =============================================================================

def apply_automatic_human_pit_stops(
    snapshot: bytearray,
    enabled: bool,
    allowed_offsets: set[int],
) -> None:
    """Allow the normal automatic pit-stop scheduler to evaluate human cars."""
    if not enabled:
        return

    for address, original in AUTOMATIC_HUMAN_PIT_STOP_JUMPS:
        offset = sna_offset(address)
        current = bytes(snapshot[offset : offset + len(original)])

        # Accept an already-patched source so the option is idempotent, but
        # reject every unknown instruction sequence rather than patching code
        # whose layout has not been verified.
        if current not in (original, THREE_NOPS):
            found = current.hex(" ").upper()
            expected = original.hex(" ").upper()
            raise ValueError(
                f"Unexpected snapshot layout at ${address:04X}; "
                f"expected {expected} or 00 00 00, found {found}"
            )

        snapshot[offset : offset + len(original)] = THREE_NOPS
        allowed_offsets.update(range(offset, offset + len(original)))


def apply_random_incident_rate(
    snapshot: bytearray,
    setting: str | None,
    allowed_offsets: set[int],
) -> None:
    """Select the original, reduced or rare random-incident probability."""
    if setting is None:
        return

    offset = sna_offset(RANDOM_INCIDENT_GATE_ADDRESS)
    current = bytes(snapshot[offset : offset + RANDOM_INCIDENT_GATE_SIZE])

    # All three forms are accepted so the option is reversible and idempotent.
    # Anything else may be unrelated code and is therefore rejected.
    if current not in RANDOM_INCIDENT_GATES.values():
        found = current.hex(" ").upper()
        raise ValueError(
            f"Unexpected snapshot layout at ${RANDOM_INCIDENT_GATE_ADDRESS:04X}; "
            f"the random-incident gate is not recognised (found {found})"
        )

    replacement = RANDOM_INCIDENT_GATES[setting]
    snapshot[offset : offset + RANDOM_INCIDENT_GATE_SIZE] = replacement
    allowed_offsets.update(range(offset, offset + RANDOM_INCIDENT_GATE_SIZE))


# =============================================================================
# 10. Assemble and verify one requested snapshot variant
# =============================================================================

def make_variant(
    source: bytes,
    teams: list[bytes],
    drivers: list[bytes],
    sponsors: list[bytes],
    colours: list[ColourPair],
    year: int | None = None,
    races: list[RaceEntry] | None = None,
    automatic_human_pit_stops: bool = False,
    random_incidents: str | None = None,
) -> bytes:
    """Return a patched copy of source while proving all writes were expected."""
    # Work on a bytearray copy. The immutable source bytes are never modified.
    result = bytearray(source)
    allowed_offsets: set[int] = set()

    write_records(
        result,
        TEAM_NAMES_ADDRESS,
        FIRST_TEAM_RECORD,
        teams,
        allowed_offsets,
    )
    write_records(
        result,
        DRIVER_NAMES_ADDRESS,
        FIRST_DRIVER_RECORD,
        drivers,
        allowed_offsets,
    )
    write_records(
        result,
        SPONSOR_NAMES_ADDRESS,
        0,
        sponsors,
        allowed_offsets,
    )
    apply_race_schedule(result, races or [], allowed_offsets)
    apply_team_colours(result, colours, allowed_offsets)
    if year is not None:
        apply_starting_year(result, year, allowed_offsets)
    apply_automatic_human_pit_stops(
        result,
        automatic_human_pit_stops,
        allowed_offsets,
    )
    apply_random_incident_rate(
        result,
        random_incidents,
        allowed_offsets,
    )

    # Defence in depth: even if a future edit introduces a stray write, refuse
    # the result unless every changed byte was explicitly placed on the allowlist.
    changed_offsets = {
        index
        for index, (before, after) in enumerate(zip(source, result))
        if before != after
    }
    if not changed_offsets.issubset(allowed_offsets):
        raise AssertionError("A byte outside the requested tables was modified")
    return bytes(result)


# =============================================================================
# 11. Output naming and protection of the source snapshot
# =============================================================================

def valid_suffix(value: str) -> str:
    """Parse --suffix for argparse: any text safe to use as a bare filename part."""
    if not value:
        raise argparse.ArgumentTypeError("suffix cannot be empty")
    if "/" in value or "\\" in value:
        raise argparse.ArgumentTypeError("suffix cannot contain '/' or '\\'")
    if value in (".", ".."):
        raise argparse.ArgumentTypeError("suffix cannot be '.' or '..'")
    return value


def output_path(game: Path, suffix: str) -> Path:
    """Choose the output name in the current working directory."""
    return Path.cwd() / f"{game.stem}-{suffix}.sna"


def save_overwriting(path: Path, data: bytes, source: Path) -> None:
    """Save a variant, overwriting any existing file at path without prompting."""
    if path.resolve() == source.resolve():
        raise ValueError(f"Refusing to overwrite the source snapshot: {source}")
    path.write_bytes(data)
    print(f"Created: {path.name}")


# =============================================================================
# 12. Command-line option definitions
# =============================================================================

def four_digit_year(value: str) -> int:
    """Parse a four-digit starting season for argparse."""
    try:
        year = int(value, 10)
    except ValueError as error:
        raise argparse.ArgumentTypeError("year must be a four-digit integer") from error
    if not 1000 <= year <= 9999:
        raise argparse.ArgumentTypeError("year must be between 1000 and 9999")
    return year


def parse_args() -> argparse.Namespace:
    """Define and parse the command-line interface shown by --help."""
    parser = argparse.ArgumentParser(
        description=(
            "Patch a Formula One 48K SNA with an optional starting year, race "
            "schedule, team-name, driver-name, sponsor-name and team-colour lists. "
            "The output is written to the current directory as a single .sna file."
        )
    )
    parser.add_argument("--game", required=True, type=Path, help="source 48K .sna")
    parser.add_argument(
        "--suffix",
        required=True,
        type=valid_suffix,
        metavar="TEXT",
        help=(
            "mandatory output-name suffix; the result is written as "
            "<game>-<suffix>.sna, for example --suffix=Season-1991 with "
            "--game=F1-2026-Mod.sna produces F1-2026-Mod-Season-1991.sna, "
            "overwriting any existing file of that name without prompting"
        ),
    )
    parser.add_argument(
        "--year",
        type=four_digit_year,
        metavar="YYYY",
        help="opening championship season, for example --year=1991",
    )
    parser.add_argument(
        "--teams",
        type=Path,
        help="text file: up to six team names, one per line, maximum eight characters",
    )
    parser.add_argument(
        "--drivers",
        type=Path,
        help="text file: up to 24 driver names, one per line, maximum ten characters",
    )
    parser.add_argument(
        "--sponsors",
        type=Path,
        help="text file: up to 13 sponsor names, one per line, maximum 12 characters",
    )
    parser.add_argument(
        "--races",
        type=Path,
        help=(
            "text file: exactly 16 lines as RACE | CIRCUIT | LAPS; race names "
            "are at most 8 ASCII characters, circuits at most 18 and laps 1-99"
        ),
    )
    parser.add_argument(
        "--colours",
        "--colors",
        dest="colours",
        type=Path,
        help=(
            "text file: up to six [BRIGHT|DIM] PRIMARY SECONDARY entries, "
            "one team per line; secondary is always dim, white primary must "
            "explicitly be 'bright white', and dim/secondary white is not allowed"
        ),
    )
    parser.add_argument(
        "--automatic-human-pit-stops",
        action="store_true",
        help=(
            "allow human-controlled cars to be called into the pits "
            "automatically under the same conditions as computer-controlled cars"
        ),
    )
    parser.add_argument(
        "--random-incidents",
        choices=tuple(RANDOM_INCIDENT_GATES),
        metavar="{original,reduced,rare}",
        help=(
            "random racing-incident rate: original is 1/32 per car per lap, "
            "reduced is 1/64, and rare is 1/128; omitted leaves the source unchanged"
        ),
    )
    return parser.parse_args()


# =============================================================================
# 13. Top-level orchestration
#
# Inputs are parsed once, the requested tables are patched, and exactly one
# output snapshot is produced. The input snapshot is always left untouched.
# =============================================================================

def main() -> int:
    """Load requested inputs, build one variant and save it safely."""
    args = parse_args()
    if (
        args.year is None
        and args.teams is None
        and args.drivers is None
        and args.sponsors is None
        and args.races is None
        and args.colours is None
        and not args.automatic_human_pit_stops
        and args.random_incidents is None
    ):
        print("Nothing to do; no SNA file was written.")
        return 0

    # Resolve the game path before comparing it with destination paths.
    game = args.game.expanduser().resolve()
    source = game.read_bytes()
    if len(source) != SNA_SIZE:
        raise ValueError(
            f"{game}: found {len(source)} bytes; expected a {SNA_SIZE}-byte 48K SNA"
        )

    # An omitted option becomes an empty list, so its table is left untouched.
    teams = (
        read_names(args.teams.expanduser().resolve(), 6, 8, "team")
        if args.teams is not None
        else []
    )
    drivers = (
        read_names(args.drivers.expanduser().resolve(), 24, 10, "driver")
        if args.drivers is not None
        else []
    )
    sponsors = (
        read_names(args.sponsors.expanduser().resolve(), 13, 12, "sponsor")
        if args.sponsors is not None
        else []
    )
    races = (
        read_races(args.races.expanduser().resolve())
        if args.races is not None
        else []
    )
    colours = (
        read_colours(args.colours.expanduser().resolve())
        if args.colours is not None
        else []
    )
    variant = make_variant(
        source,
        teams,
        drivers,
        sponsors,
        colours,
        args.year,
        races,
        args.automatic_human_pit_stops,
        args.random_incidents,
    )
    destination = output_path(game, args.suffix)
    save_overwriting(destination, variant, game)
    return 0


# =============================================================================
# 14. Executable entry point and concise error reporting
# =============================================================================

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
