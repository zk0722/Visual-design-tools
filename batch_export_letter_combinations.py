#!/usr/bin/env python3
"""Export all letter combinations at 100–400% and 128px Slack emoji in light and dark themes via the web app renderer."""

from __future__ import annotations

import base64
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "batch_output" / "Letter combination"
REVIEW_PAD = 48
RESOLUTIONS = [100, 150, 200, 300, 400, 128]

# Same specs as generate_batch_icons.py
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


def safe_name(letters: str, outline: bool, theme: str) -> str:
    outline_tag = "outline" if outline else "no-outline"
    return f"icon_{letters}_{outline_tag}_{theme}.png"


def ensure_server() -> None:
    import urllib.request

    try:
        urllib.request.urlopen("http://localhost:3000/", timeout=2)
        return
    except OSError:
        pass
    subprocess.Popen(
        ["node", str(ROOT / "server.js")],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        try:
            urllib.request.urlopen("http://localhost:3000/", timeout=2)
            return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("Could not start or reach http://localhost:3000")


def export_all() -> list[dict]:
    from playwright.sync_api import sync_playwright

    ensure_server()
    records: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:3000/", wait_until="networkidle")
        page.wait_for_function("typeof window.batchRenderLetterIcon === 'function'")

        for resolution in RESOLUTIONS:
            for theme in ("light", "dark"):
                theme_dir = OUT / str(resolution) / theme
                theme_dir.mkdir(parents=True, exist_ok=True)
                for old in theme_dir.glob("*.png"):
                    old.unlink()

            for letters, outline, group in ICON_SPECS:
                for theme in ("light", "dark"):
                    data_url = page.evaluate(
                        """async (cfg) => await window.batchRenderLetterIcon(cfg)""",
                        {
                            "letters": letters,
                            "outlineOn": outline,
                            "resolution": resolution,
                            "theme": theme,
                        },
                    )
                    if not data_url or not data_url.startswith("data:image/png;base64,"):
                        raise RuntimeError(f"Failed to render {letters} {resolution} {theme}")

                    raw = base64.b64decode(data_url.split(",", 1)[1])
                    filename = safe_name(letters, outline, theme)
                    path = OUT / str(resolution) / theme / filename
                    path.write_bytes(raw)
                    records.append(
                        {
                            "letters": letters,
                            "outline": outline,
                            "theme": theme,
                            "resolution": resolution,
                            "group": group,
                            "path": str(path.relative_to(ROOT)),
                        }
                    )

        browser.close()

    return records


def create_review_png(records: list[dict]) -> Path:
    from PIL import Image

    # One row per icon; columns: each resolution light then dark (5 res × 2 = 10 cols)
    cols_per_section = len(RESOLUTIONS) * 2
    col_gap = 12
    row_gap = 12
    section_gap = 32
    label_h = 14

    def icon_size(res: int) -> int:
        if res == 100:
            return 16
        if res == 128:
            return 128
        return round(res * 20 / 100)

    def resolution_label(res: int) -> str:
        return "128px" if res == 128 else f"{res}%"

    max_cell = max(icon_size(r) for r in RESOLUTIONS)
    cell = max_cell

    n_icons = len(ICON_SPECS)
    n_groups = len(ICON_GROUPS)

    content_w = cols_per_section * cell + (cols_per_section - 1) * col_gap
    row_h = cell + row_gap
    content_h = n_icons * row_h + (n_groups - 1) * section_gap

    # Header row for resolution labels
    header_h = 28
    width = REVIEW_PAD * 2 + content_w
    height = REVIEW_PAD * 2 + header_h + content_h

    sheet = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    from PIL import ImageDraw, ImageFont

    try:
        font = ImageFont.truetype(str(ROOT / "fonts" / "PixelifySans-SemiBold.ttf"), 11)
    except OSError:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(sheet)
    x0 = REVIEW_PAD
    y0 = REVIEW_PAD

    col = 0
    for res in RESOLUTIONS:
        sz = icon_size(res)
        for theme in ("light", "dark"):
            cx = x0 + col * (cell + col_gap) + (cell - sz) // 2
            label = f"{resolution_label(res)} {theme}"
            draw.text((cx, y0), label, fill=(80, 80, 80, 255), font=font)
            col += 1

    y = y0 + header_h
    icon_idx = 0
    for group_idx, (_, items) in enumerate(ICON_GROUPS):
        for letters, outline in items:
            col = 0
            for res in RESOLUTIONS:
                sz = icon_size(res)
                for theme in ("light", "dark"):
                    rel = OUT / str(res) / theme / safe_name(letters, outline, theme)
                    icon = Image.open(rel).convert("RGBA")
                    if icon.size[0] != sz:
                        icon = icon.resize((sz, sz), Image.NEAREST)
                    cx = x0 + col * (cell + col_gap) + (cell - sz) // 2
                    sheet.paste(icon, (cx, y), icon)
                    col += 1
            icon_idx += 1
            y += row_h
        if group_idx < n_groups - 1:
            y += section_gap

    out_path = OUT / "review.png"
    sheet.save(out_path, "PNG")
    return out_path


def main() -> None:
    try:
        import playwright  # noqa: F401
    except ImportError:
        print("Install playwright: pip install playwright && playwright install chromium")
        sys.exit(1)

    records = export_all()
    review = create_review_png(records)
    manifest = OUT / "manifest.json"
    manifest.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")

    unique = len(ICON_SPECS)
    print(f"Exported {len(records)} icons ({unique} combinations × {len(RESOLUTIONS)} resolutions × 2 themes)")
    print(f"Output:      {OUT}")
    print(f"Review PNG:  {review}")
    print(f"Manifest:    {manifest}")


if __name__ == "__main__":
    main()
