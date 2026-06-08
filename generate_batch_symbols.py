#!/usr/bin/env python3
"""Batch-export GD&T special symbols (light + dark themes) and a review PNG."""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "batch_output" / "symbols"
SYMBOLS_JSON = ROOT / "custom-symbols.json"
INDEX_HTML = ROOT / "index.html"

REVIEW_PAD = 48
ICON_SIZE = 16
REVIEW_COLS = 10


def sanitize_export_label(label: str) -> str:
    return re.sub(r'[/\\:*?"<>|]', "-", label)


def load_symbol_specs() -> list[tuple[str, str, list[list[int]]]]:
    pixels_by_key = json.loads(SYMBOLS_JSON.read_text(encoding="utf-8"))
    html = INDEX_HTML.read_text(encoding="utf-8")
    pattern = re.compile(r"'([a-zA-Z]+)': \{ name: '([^']+)'")
    specs: list[tuple[str, str, list[list[int]]]] = []
    seen: set[str] = set()

    for key, name in pattern.findall(html):
        if key not in pixels_by_key or key in seen:
            continue
        seen.add(key)
        specs.append((key, name, pixels_by_key[key]))

    missing = set(pixels_by_key) - seen
    if missing:
        for key in sorted(missing):
            specs.append((key, key, pixels_by_key[key]))

    return specs


def rgba_for_theme(theme: str) -> tuple[int, int, int, int]:
    return (0, 0, 0, 255) if theme == "light" else (255, 255, 255, 255)


def create_symbol_icon(pixels: list[list[int]], color: tuple[int, int, int, int]) -> Image.Image:
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for x, y in pixels:
        draw.point((x, y), fill=color)
    return img


def safe_name(name: str, theme: str) -> str:
    return f"{sanitize_export_label(name)}_{theme}.png"


def generate_all(specs: list[tuple[str, str, list[list[int]]]]) -> list[dict]:
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in ("light", "dark"):
        theme_dir = OUT / theme
        theme_dir.mkdir(exist_ok=True)
        for old in theme_dir.glob("*.png"):
            old.unlink()

    records: list[dict] = []
    for key, name, pixels in specs:
        for theme in ("light", "dark"):
            icon = create_symbol_icon(pixels, rgba_for_theme(theme))
            filename = safe_name(name, theme)
            path = OUT / theme / filename
            icon.save(path, "PNG")
            records.append(
                {
                    "key": key,
                    "name": name,
                    "theme": theme,
                    "path": str(path.relative_to(ROOT)),
                }
            )
    return records


def create_review_sheet(specs: list[tuple[str, str, list[list[int]]]]) -> Path:
    """Review PNG: all light symbols, then all dark symbols, 48px padding, no labels."""
    cell = ICON_SIZE
    col_gap = 8
    row_gap = 8
    section_gap = 24
    cols = REVIEW_COLS
    row_h = cell + row_gap

    def section_rows(count: int) -> int:
        return (count + cols - 1) // cols

    rows = section_rows(len(specs))
    content_w = cols * cell + (cols - 1) * col_gap
    content_h = rows * row_h * 2 + section_gap
    width = REVIEW_PAD * 2 + content_w
    height = REVIEW_PAD * 2 + content_h

    sheet = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    def draw_section(y_start: int, theme: str) -> None:
        color = rgba_for_theme(theme)
        for idx, (_, _, pixels) in enumerate(specs):
            row = idx // cols
            col = idx % cols
            x = REVIEW_PAD + col * (cell + col_gap)
            y = y_start + row * row_h
            icon = create_symbol_icon(pixels, color)
            sheet.paste(icon, (x, y), icon)

    light_y = REVIEW_PAD
    dark_y = REVIEW_PAD + rows * row_h + section_gap
    draw_section(light_y, "light")
    draw_section(dark_y, "dark")

    out_path = OUT / "review.png"
    sheet.save(out_path, "PNG")
    return out_path


def main() -> None:
    specs = load_symbol_specs()
    records = generate_all(specs)
    review = create_review_sheet(specs)
    manifest = OUT / "manifest.json"
    manifest.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")

    print(f"Generated {len(records)} symbol icons ({len(specs)} unique × 2 themes)")
    print(f"Light icons: {OUT / 'light'}")
    print(f"Dark icons:  {OUT / 'dark'}")
    print(f"Review PNG:  {review} ({REVIEW_PAD}px padding, actual size)")


if __name__ == "__main__":
    main()
