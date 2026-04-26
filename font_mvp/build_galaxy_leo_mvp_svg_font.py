#!/usr/bin/env python3
"""Build an expandable SVG MVP font inspired by the provided '銀河Leo星王' key art.

Output: font_mvp/GalaxyLeoKing-MVP.svg

This is a style-inspired original draft, not an extracted/copy font.
"""

from __future__ import annotations

from pathlib import Path

UPEM = 1000
ASCENT = 860
DESCENT = -140


# 14-segment layout (boxy display) for fast MVP Latin/digit coverage.
SEGMENTS = {
    "A": (170, 700, 560, 70),
    "B": (560, 640, 70, 260),
    "C": (560, 340, 70, 260),
    "D": (170, 100, 560, 70),
    "E": (120, 340, 70, 260),
    "F": (120, 640, 70, 260),
    "G": (170, 400, 560, 70),
    "H": (170, 760, 250, 70),
    "I": (480, 760, 250, 70),
    "J": (170, 30, 250, 70),
    "K": (480, 30, 250, 70),
    "L": (170, 400, 250, 70),
    "M": (170, 330, 250, 70),
    "N": (170, 470, 250, 70),
}

SEGMENT_MAP = {
    # digits
    "0": "ABCD EF    HIKJ",
    "1": " BC        IK  ",
    "2": "AB D EFG   JK  ",
    "3": "ABCD  FG   IJK ",
    "4": "  C  FG  HIK   ",
    "5": "A CD FG  H JK  ",
    "6": "A CDEFG H JK  ",
    "7": "ABC       IK   ",
    "8": "ABCDEFG HIKJ  ",
    "9": "ABCD FG HIK   ",
    # uppercase
    "A": "ABC EFG HIK   ",
    "B": "ABCD EFG HIJK ",
    "C": "A  D EF  H J  ",
    "D": "ABCD EF  HIJK ",
    "E": "A  D EFG H J  ",
    "F": "A    EFG H    ",
    "G": "A CD EFG H JK ",
    "H": " BC  FG HIK   ",
    "I": "AB D    I JK  ",
    "J": " BCD   F  IK  ",
    "K": "    EFG HIKJ  ",
    "L": "   D E   H J  ",
    "M": " BC EF  HIKJ  ",
    "N": " BC EF  HIKJ  ",
    "O": "ABCD EF  HIKJ ",
    "P": "AB   EFG HI   ",
    "Q": "ABCD EF  HIKJ ",
    "R": "AB   EFG HIK  ",
    "S": "A CD FG H JK  ",
    "T": "A      I JK   ",
    "U": " BCD EF  HIKJ ",
    "V": "    EF  H JK  ",
    "W": " BCD EF  HIKJ ",
    "X": "    FG HIKJ   ",
    "Y": "    FG HIK    ",
    "Z": "AB D  G  JK   ",
}

# hand-authored CJK + tuned latin from original MVP
MANUAL_GLYPHS = {
    " ": {"name": "space", "horiz": 360, "d": ""},
    "e": {
        "name": "e",
        "horiz": 700,
        "d": (
            "M350 90 C180 90 90 210 90 380 C90 555 190 690 360 690 C470 690 550 640 600 555 "
            "L500 505 C470 550 430 575 365 575 C280 575 230 520 220 430 L610 430 "
            "C615 410 615 390 615 370 C615 210 510 90 350 90 Z "
            "M225 345 C240 280 285 210 355 210 C430 210 480 275 490 345 L225 345 Z"
        ),
    },
    "o": {
        "name": "o",
        "horiz": 730,
        "d": (
            "M365 90 C190 90 90 220 90 390 C90 560 195 690 365 690 C535 690 640 560 640 390 "
            "C640 220 540 90 365 90 Z M365 215 C455 215 510 285 510 390 C510 500 455 565 365 565 "
            "C275 565 220 500 220 390 C220 285 275 215 365 215 Z"
        ),
    },
    "銀": {
        "name": "uni9280",
        "horiz": 1000,
        "d": (
            "M120 760 L880 760 L880 690 L120 690 Z M170 620 L830 620 L830 560 L170 560 Z "
            "M200 500 L800 500 L800 440 L200 440 Z M110 390 L450 390 L450 330 L110 330 Z "
            "M550 390 L890 390 L890 330 L550 330 Z M160 280 L840 280 L840 220 L160 220 Z "
            "M120 160 L420 160 L420 90 L120 90 Z M520 160 L880 160 L880 90 L520 90 Z "
            "M450 620 L550 620 L550 90 L450 90 Z"
        ),
    },
    "河": {
        "name": "uni6CB3",
        "horiz": 1000,
        "d": (
            "M120 740 L300 740 L300 680 L120 680 Z M140 600 L320 600 L320 540 L140 540 Z "
            "M160 460 L340 460 L340 400 L160 400 Z M420 760 L890 760 L890 690 L420 690 Z "
            "M620 690 L700 690 L700 90 L620 90 Z M450 500 L880 500 L880 430 L450 430 Z "
            "M450 260 L880 260 L880 190 L450 190 Z M420 140 L890 140 L890 80 L420 80 Z"
        ),
    },
    "星": {
        "name": "uni661F",
        "horiz": 1000,
        "d": (
            "M120 760 L880 760 L880 690 L120 690 Z M470 760 L530 760 L530 90 L470 90 Z "
            "M120 580 L880 580 L880 520 L120 520 Z M220 430 L780 430 L780 370 L220 370 Z "
            "M140 260 L860 260 L860 200 L140 200 Z M220 140 L780 140 L780 80 L220 80 Z"
        ),
    },
    "王": {
        "name": "uni738B",
        "horiz": 1000,
        "d": (
            "M140 730 L860 730 L860 660 L140 660 Z M220 470 L780 470 L780 400 L220 400 Z "
            "M120 200 L880 200 L880 130 L120 130 Z M470 760 L530 760 L530 90 L470 90 Z"
        ),
    },
}


def _rect_path(x: int, y: int, w: int, h: int, chamfer: int = 18) -> str:
    """Rectangle with tiny cut corners for metallic/chiseled feeling."""
    c = min(chamfer, w // 3, h // 3)
    return (
        f"M{x+c} {y} L{x+w-c} {y} L{x+w} {y+c} L{x+w} {y+h-c} "
        f"L{x+w-c} {y+h} L{x+c} {y+h} L{x} {y+h-c} L{x} {y+c} Z"
    )


def build_segment_glyph(ch: str) -> dict[str, str | int] | None:
    key = ch.upper()
    mapping = SEGMENT_MAP.get(key)
    if not mapping:
        return None

    active = {c for c in mapping if c.isalpha()}
    paths = []
    for seg, (x, y, w, h) in SEGMENTS.items():
        if seg in active:
            paths.append(_rect_path(x, y, w, h))

    horiz = 900
    name = ch if ch.isascii() and ch.isalnum() else f"uni{ord(ch):04X}"
    return {"name": name, "horiz": horiz, "d": " ".join(paths)}


def build_glyph_table() -> dict[str, dict[str, str | int]]:
    table = dict(MANUAL_GLYPHS)

    # Cover A-Z, a-z, 0-9 in MVP.
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
        table.setdefault(ch, build_segment_glyph(ch))
    for ch in "abcdefghijklmnopqrstuvwxyz":
        # Lowercase uses same segmented skeleton but slightly narrower advance.
        base = build_segment_glyph(ch)
        if base:
            base["horiz"] = 860
            table[ch] = base

    # Keep the hand-tuned display feel for key letters in the title word.
    table["e"] = MANUAL_GLYPHS["e"]
    table["o"] = MANUAL_GLYPHS["o"]

    # Clean out None entries if any mapping is missing.
    return {k: v for k, v in table.items() if v is not None}


def _escape_unicode_attr(ch: str) -> str:
    if ch == '"':
        return "&quot;"
    if ch == "&":
        return "&amp;"
    return ch


def build_svg_font(glyphs: dict[str, dict[str, str | int]]) -> str:
    glyph_entries: list[str] = []
    for ch, meta in glyphs.items():
        glyph_entries.append(
            f'    <glyph glyph-name="{meta["name"]}" unicode="{_escape_unicode_attr(ch)}" '
            f'horiz-adv-x="{meta["horiz"]}" d="{meta["d"]}" />'
        )

    glyph_xml = "\n".join(glyph_entries)
    return f'''<?xml version="1.0" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <defs>
    <font id="GalaxyLeoKingMVP" horiz-adv-x="900">
      <font-face font-family="Galaxy Leo King MVP" units-per-em="{UPEM}" ascent="{ASCENT}" descent="{DESCENT}"/>
      <missing-glyph horiz-adv-x="900" d="M120 90 L120 760 L780 760 L780 90 Z M220 190 L680 190 L680 660 L220 660 Z"/>
{glyph_xml}
    </font>
  </defs>
</svg>
'''


def main() -> None:
    out = Path(__file__).resolve().parent / "GalaxyLeoKing-MVP.svg"
    glyphs = build_glyph_table()
    out.write_text(build_svg_font(glyphs), encoding="utf-8")
    print(f"Wrote {out} with {len(glyphs)} glyphs")


if __name__ == "__main__":
    main()
