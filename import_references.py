#!/usr/bin/env python3
"""Extract 16×16 pixel data from reference PNGs and update project symbol files.

Reference images live in references/<symbolKey>.png (one per GD&T symbol).
Run: python3 import_references.py
Updates: custom-symbols.json, index.html (pixels only; SVG preserved)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REFS = ROOT / "references"
CUSTOM = ROOT / "custom-symbols.json"
INDEX = ROOT / "index.html"


def extract_pixels(path: Path) -> list[list[int]]:
    from PIL import Image

    img = Image.open(path).convert("RGBA")
    w, h = img.size
    px = img.load()
    raw: list[tuple[int, int]] = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > 128 or lum < 64:
                raw.append((x, y))
    if not raw:
        raise ValueError(f"No pixels found in {path}")

    xs = [p[0] for p in raw]
    ys = [p[1] for p in raw]
    if w == 16 and h == 16:
        return sorted({(x, y) for x, y in raw})

    bw = max(xs) - min(xs) + 1
    bh = max(ys) - min(ys) + 1
    ox = (16 - bw) // 2 - min(xs)
    oy = (16 - bh) // 2 - min(ys)
    pts = sorted(
        (x + ox, y + oy)
        for x, y in raw
        if 0 <= x + ox < 16 and 0 <= y + oy < 16
    )
    return [[x, y] for x, y in pts]


def update_index_html(symbols: dict[str, list[list[int]]]) -> None:
    html = INDEX.read_text(encoding="utf-8")
    for key, pixels in symbols.items():
        pattern = (
            rf"('{key}': \{{ name: ')([^']*)(', pixels: )\[[\s\S]*?"
            rf"(, svg: ')([^']*)(' \}})"
        )
        match = re.search(pattern, html)
        if not match:
            print(f"  warn: no index.html entry for {key}")
            continue
        replacement = (
            match.group(1)
            + match.group(2)
            + match.group(3)
            + json.dumps(pixels)
            + match.group(4)
            + match.group(5)
            + match.group(6)
        )
        html = html[: match.start()] + replacement + html[match.end() :]
    INDEX.write_text(html, encoding="utf-8")


def main() -> None:
    symbols: dict[str, list[list[int]]] = {}
    for png in sorted(REFS.glob("*.png")):
        key = png.stem
        pixels = extract_pixels(png)
        symbols[key] = pixels
        print(f"{key}: {len(pixels)} pixels")

    CUSTOM.write_text(json.dumps(symbols, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {CUSTOM}")

    update_index_html(symbols)
    print(f"Updated {INDEX}")


if __name__ == "__main__":
    main()
