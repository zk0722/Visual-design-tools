#!/usr/bin/env python3
"""Batch-generate letter icons from reference lists (light + dark themes)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "batch_output"
FONTS = json.loads((ROOT / "letter_fonts.json").read_text(encoding="utf-8"))

FONT_LARGE = FONTS["FONT_LARGE"]
FONT_MEDIUM = FONTS["FONT_MEDIUM"]
FONT_SMALL = FONTS["FONT_SMALL"]
CIRCLE_PIXELS = [tuple(p) for p in FONTS["CIRCLE_PIXELS"]]
PILL_PIXELS = [tuple(p) for p in FONTS["PILL_PIXELS"]]

_TY_GLYPHS = json.loads((ROOT / "letter_ty_glyphs.json").read_text(encoding="utf-8"))
FONT_ONE_NO_OUTLINE_TY = _TY_GLYPHS["oneNoOutline"]
FONT_ONE_OUTLINE_TY = _TY_GLYPHS["oneOutline"]
FONT_TWO_NO_OUTLINE_TY = _TY_GLYPHS["twoNoOutline"]
FONT_THREE_NO_OUTLINE_IM = _TY_GLYPHS["threeNoOutline"]
ICON_GROUPS: list[tuple[str, list[tuple[str, bool]]]] = [
    (
        "Pill outline (LS–SX)",
        [(text, True) for text in "LS LP SA SD SM SN SR SQ SX".split()],
    ),
    (
        "Plain 2–3 letter (UF–SIM)",
        [(text, False) for text in ["UF", "UZ", "ACS", "ALS", "SCS", "SIM"]],
    ),
    (
        "Plain 2 letter (CF–SZ)",
        [(text, False) for text in "CF CT CZ DV LD LE MD NC PD SZ".split()],
    ),
    (
        "Circle outline (A–T)",
        [(text, True) for text in "A E F L M P R T".split()],
    ),
    (
        "Circle + pill (U–LG)",
        [("U", True)]
        + [(text, True) for text in "CA CC CV GC GG GN GX LC LG".split()],
    ),
]

ICON_SPECS: list[tuple[str, bool, str]] = [
    (letters, outline, group_key)
    for group_key, items in [
        ("pill", ICON_GROUPS[0][1]),
        ("plain-mixed", ICON_GROUPS[1][1]),
        ("plain-2", ICON_GROUPS[2][1]),
        ("circle", ICON_GROUPS[3][1]),
        ("circle-pill", ICON_GROUPS[4][1]),
    ]
    for letters, outline in items
]

REVIEW_PAD = 48
ICON_SIZE = 16


def glyph_pixel_width(pixels: list[list[int]]) -> int:
    return max(p[0] for p in pixels) + 1


def get_two_no_outline_ty_pixels(letter: str, letter_index: int) -> list[list[int]] | None:
    if letter_index == 0 and letter in FONT_TWO_NO_OUTLINE_TY:
        return FONT_TWO_NO_OUTLINE_TY[letter]
    if letter_index == 1:
        if letter == "T":
            return FONT_TWO_NO_OUTLINE_TY["T_second"]
        if letter == "Y":
            return FONT_TWO_NO_OUTLINE_TY["Y_second"]
    return None


def resolve_letter_pixels(
    letter: str,
    font: dict[str, list[list[int]]],
    letter_count: int,
    outline_on: bool,
    letter_index: int,
) -> list[list[int]]:
    if letter_count == 1 and outline_on and letter in FONT_ONE_OUTLINE_TY:
        return FONT_ONE_OUTLINE_TY[letter]
    if letter_count == 1 and not outline_on and letter in FONT_ONE_NO_OUTLINE_TY:
        return FONT_ONE_NO_OUTLINE_TY[letter]
    if letter_count == 2 and not outline_on:
        special = get_two_no_outline_ty_pixels(letter, letter_index)
        if special is not None:
            return special
    if letter_count == 3 and not outline_on and letter in FONT_THREE_NO_OUTLINE_IM:
        return FONT_THREE_NO_OUTLINE_IM[letter]
    return font.get(letter, [])


def three_letter_slot_width(letter: str, letter_width: int, pixels: list[list[int]] | None) -> int:
    if pixels:
        return glyph_pixel_width(pixels)
    if letter == "I":
        return 3
    if letter == "M":
        return 5
    return letter_width


def two_letter_slot_width(
    letter: str,
    use_large: bool,
    narrow_ty: bool,
    letter_index: int,
    pixels: list[list[int]] | None,
) -> int:
    if pixels:
        return glyph_pixel_width(pixels)
    if narrow_ty and letter in ("T", "Y"):
        return 5 if letter_index == 0 else 6
    if use_large:
        return 6
    return 5 if letter in ("T", "Y") else 4


def two_letter_spacing(letters: str, outline_on: bool) -> int:
    if not outline_on and ("T" in letters or "Y" in letters):
        return 2
    return 1 if "T" in letters or "Y" in letters else 2


def letter_params(letters: str, outline_on: bool) -> dict:
    letter_count = len(letters)
    if letter_count == 1:
        return {
            "letters": letters,
            "font": FONT_LARGE,
            "letter_width": 6,
            "letter_height": 10,
            "spacing": 0,
            "outline_on": outline_on,
            "letter_count": 1,
        }
    if letter_count == 2:
        if outline_on:
            return {
                "letters": letters,
                "font": FONT_MEDIUM,
                "letter_width": 4,
                "letter_height": 8,
                "spacing": 2,
                "outline_on": True,
                "letter_count": 2,
            }
        return {
            "letters": letters,
            "font": FONT_LARGE,
            "letter_width": 6,
            "letter_height": 10,
            "spacing": 2,
            "outline_on": False,
            "letter_count": 2,
        }
    if outline_on:
        return {
            "letters": letters,
            "font": FONT_SMALL,
            "letter_width": 3,
            "letter_height": 5,
            "spacing": 1,
            "outline_on": True,
            "letter_count": 3,
        }
    return {
        "letters": letters,
        "font": FONT_MEDIUM,
        "letter_width": 4,
        "letter_height": 8,
        "spacing": 2,
        "outline_on": False,
        "letter_count": 3,
    }


def draw_pixels(draw: ImageDraw.ImageDraw, pixels: list[tuple[int, int]], color: tuple[int, int, int, int]) -> None:
    for x, y in pixels:
        draw.point((x, y), fill=color)


def draw_letter(
    draw: ImageDraw.ImageDraw,
    letter: str,
    offset_x: int,
    offset_y: int,
    font: dict[str, list[list[int]]],
    color: tuple[int, int, int, int],
    letter_count: int = 1,
    outline_on: bool = True,
    letter_index: int = 0,
) -> None:
    pixels = resolve_letter_pixels(letter, font, letter_count, outline_on, letter_index)
    for x, y in pixels:
        draw.point((offset_x + x, offset_y + y), fill=color)


def create_icon(letters: str, outline_on: bool, color: tuple[int, int, int, int]) -> Image.Image:
    params = letter_params(letters, outline_on)
    font = params["font"]
    letter_count = params["letter_count"]
    letter_width = params["letter_width"]
    letter_height = params["letter_height"]
    spacing = params["spacing"]

    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if outline_on:
        shape = CIRCLE_PIXELS if letter_count == 1 else PILL_PIXELS
        draw_pixels(draw, shape, color)

    if outline_on:
        start_y = 3 if letter_count in (1, 2) else 5
    else:
        start_y = (16 - letter_height) // 2

    if letter_count == 2:
        letter_spacing = two_letter_spacing(letters, outline_on)
        use_large = font is FONT_LARGE
        narrow_ty = not outline_on
        chars = list(letters)
        resolved = [resolve_letter_pixels(ch, font, letter_count, outline_on, i) for i, ch in enumerate(chars)]
        widths = [
            two_letter_slot_width(ch, use_large, narrow_ty, i, resolved[i])
            for i, ch in enumerate(chars)
        ]
        total_width = widths[0] + letter_spacing + widths[1]
        start_x = (16 - total_width) // 2
        x = start_x
        for i, ch in enumerate(chars):
            draw_letter(draw, ch, x, start_y, font, color, letter_count, outline_on, i)
            if i == 0:
                x += widths[i] + letter_spacing
    elif letter_count == 3 and not outline_on:
        chars = list(letters)
        resolved = [resolve_letter_pixels(ch, font, letter_count, outline_on, i) for i, ch in enumerate(chars)]
        widths = [three_letter_slot_width(ch, letter_width, resolved[i]) for i, ch in enumerate(chars)]
        total_width = sum(widths) + spacing * (len(chars) - 1)
        start_x = (16 - total_width) // 2
        x = start_x
        for i, ch in enumerate(chars):
            draw_letter(draw, ch, x, start_y, font, color, letter_count, outline_on, i)
            if i < len(chars) - 1:
                x += widths[i] + spacing
    else:
        one_letter_pixels = resolve_letter_pixels(letters[0], font, letter_count, outline_on, 0)
        is_one_letter_ty = (
            letter_count == 1
            and one_letter_pixels
            and letters[0] in ("T", "Y")
            and (
                (outline_on and letters[0] in FONT_ONE_OUTLINE_TY)
                or (not outline_on and letters[0] in FONT_ONE_NO_OUTLINE_TY)
            )
        )
        slot_width = glyph_pixel_width(one_letter_pixels) if is_one_letter_ty else letter_width
        total_width = letter_count * slot_width + (letter_count - 1) * spacing
        start_x = (16 - total_width) // 2
        for i, ch in enumerate(letters):
            draw_letter(draw, ch, start_x + i * (slot_width + spacing), start_y, font, color, letter_count, outline_on, i)

    return img


def rgba_for_theme(theme: str) -> tuple[int, int, int, int]:
    return (0, 0, 0, 255) if theme == "light" else (255, 255, 255, 255)


def bg_for_theme(theme: str) -> tuple[int, int, int, int]:
    return (254, 254, 254, 255) if theme == "light" else (59, 68, 83, 255)


def safe_name(letters: str, outline: bool, theme: str) -> str:
    outline_tag = "outline" if outline else "no-outline"
    return f"icon_{letters}_{outline_tag}_{theme}.png"


def generate_all() -> list[dict]:
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in ("light", "dark"):
        theme_dir = OUT / theme
        theme_dir.mkdir(exist_ok=True)
        for old in theme_dir.glob("*.png"):
            old.unlink()

    records: list[dict] = []
    for letters, outline, group in ICON_SPECS:
        for theme in ("light", "dark"):
            color = rgba_for_theme(theme)
            icon = create_icon(letters, outline, color)
            filename = safe_name(letters, outline, theme)
            path = OUT / theme / filename
            icon.save(path, "PNG")
            records.append(
                {
                    "letters": letters,
                    "outline": outline,
                    "theme": theme,
                    "group": group,
                    "path": str(path.relative_to(ROOT)),
                }
            )
    return records


def create_review_sheet(records: list[dict]) -> Path:
    """Review PNG: light icons grouped together, then dark icons, 48px outer padding."""
    cell = ICON_SIZE
    col_gap = 8
    row_gap = 8
    section_gap = 24
    group_gap = 16
    cols = 10

    row_h = cell + row_gap

    def group_rows(count: int) -> int:
        return (count + cols - 1) // cols

    def section_height() -> int:
        total = 0
        for _, items in ICON_GROUPS:
            rows = group_rows(len(items))
            total += rows * row_h + group_gap
        return total - group_gap

    content_w = cols * cell + (cols - 1) * col_gap
    content_h = section_height() * 2 + section_gap
    width = REVIEW_PAD * 2 + content_w
    height = REVIEW_PAD * 2 + content_h

    sheet = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    def render_icon(letters: str, outline: bool, theme: str) -> Image.Image:
        return create_icon(letters, outline, rgba_for_theme(theme))

    def draw_section(y_start: int, theme: str) -> int:
        y = y_start
        x0 = REVIEW_PAD

        for _, items in ICON_GROUPS:
            for idx, (letters, outline) in enumerate(items):
                row = idx // cols
                col = idx % cols
                x = x0 + col * (cell + col_gap)
                yy = y + row * row_h
                icon = render_icon(letters, outline, theme)
                sheet.paste(icon, (x, yy), icon)

            rows = group_rows(len(items))
            y += rows * row_h + group_gap

        return y - group_gap

    y = REVIEW_PAD
    y = draw_section(y, "light")
    draw_section(y + section_gap, "dark")

    out_path = OUT / "review.png"
    sheet.save(out_path, "PNG")
    return out_path


def create_grid_sheet(records: list[dict], scale: int = 6) -> Path:
    """Compact grid grouped by category."""
    groups: dict[str, list[tuple[str, bool]]] = {}
    for letters, outline, group in ICON_SPECS:
        groups.setdefault(group, []).append((letters, outline))

    cell = 16 * scale
    pad = 8
    label_h = 16
    section_gap = 20

    group_titles = {
        "plain-2": "Plain (2-letter, no outline)",
        "plain-mixed": "Plain (2–3 letter, no outline)",
        "pill": "Pill outline",
        "circle": "Circle outline",
        "circle-pill": "Circle + pill outline",
    }

    try:
        font = ImageFont.truetype(str(ROOT / "fonts" / "PixelifySans-SemiBold.ttf"), 12)
        small = ImageFont.truetype(str(ROOT / "fonts" / "PixelifySans-SemiBold.ttf"), 9)
    except OSError:
        font = ImageFont.load_default()
        small = font

    cols = 10
    sections = []
    for group_key in ("pill", "plain-mixed", "plain-2", "circle", "circle-pill"):
        items = groups.get(group_key, [])
        if not items:
            continue
        rows = (len(items) + cols - 1) // cols
        sections.append((group_key, items, rows))

    total_rows = sum(s[2] for s in sections) + len(sections) * 2
    width = pad + cols * (cell + pad)
    height = pad + total_rows * (cell + label_h + pad) + len(sections) * section_gap

    sheet = Image.new("RGBA", (width, height), (248, 248, 248, 255))
    draw = ImageDraw.Draw(sheet)
    y = pad

    for group_key, items, rows in sections:
        draw.text((pad, y), group_titles[group_key], fill=(40, 40, 40, 255), font=font)
        y += label_h + 4
        for idx, (letters, outline) in enumerate(items):
            row = idx // cols
            col = idx % cols
            x = pad + col * (cell + pad)
            yy = y + row * (cell + label_h + pad)

            for theme_idx, theme in enumerate(("light", "dark")):
                sub_w = cell // 2 - 1
                icon = create_icon(letters, outline, rgba_for_theme(theme))
                bg = Image.new("RGBA", (sub_w, cell), bg_for_theme(theme))
                scaled = icon.resize((sub_w, sub_w), Image.NEAREST)
                bg.paste(scaled, (0, (cell - sub_w) // 2), scaled)
                sheet.paste(bg, (x + theme_idx * (sub_w + 2), yy))

            tag = letters if outline else f"{letters}*"
            draw.text((x, yy + cell + 2), tag, fill=(60, 60, 60, 255), font=small)

        y += rows * (cell + label_h + pad) + section_gap

    out_path = OUT / "review_grid.png"
    sheet.save(out_path, "PNG")
    return out_path


def main() -> None:
    records = generate_all()
    review = create_review_sheet(records)
    grid = create_grid_sheet(records)
    manifest = OUT / "manifest.json"
    manifest.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")

    unique = len(records) // 2
    print(f"Generated {len(records)} icons ({unique} unique × 2 themes)")
    print(f"Light icons: {OUT / 'light'}")
    print(f"Dark icons:  {OUT / 'dark'}")
    print(f"Review PNG:  {review} ({REVIEW_PAD}px padding)")
    print(f"Review grid: {grid}")
    print(f"Manifest:    {manifest}")


if __name__ == "__main__":
    main()
