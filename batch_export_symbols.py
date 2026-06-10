#!/usr/bin/env python3
"""Export all special symbols at 100–400% in light and dark themes via the web app renderer."""

from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "batch_output" / "symbols"
REVIEW_PAD = 48
RESOLUTIONS = [100, 150, 200, 300, 400]


def sanitize_export_label(label: str) -> str:
    return re.sub(r'[/\\:*?"<>|]', "-", label)


def safe_name(name: str, theme: str) -> str:
    return f"{sanitize_export_label(name)}_{theme}.png"


def symbol_size(resolution: int) -> int:
    return round(16 * resolution / 100)


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


def export_all() -> tuple[list[dict], list[dict]]:
    from playwright.sync_api import sync_playwright

    ensure_server()
    records: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:3000/", wait_until="networkidle")
        page.wait_for_function("typeof window.batchRenderSymbolIcon === 'function'")
        specs = page.evaluate("() => window.getSymbolExportSpecs()")

        for resolution in RESOLUTIONS:
            for theme in ("light", "dark"):
                theme_dir = OUT / str(resolution) / theme
                theme_dir.mkdir(parents=True, exist_ok=True)
                for old in theme_dir.glob("*.png"):
                    old.unlink()

            for spec in specs:
                symbol_key = spec["key"]
                name = spec["name"]
                for theme in ("light", "dark"):
                    data_url = page.evaluate(
                        """async (cfg) => await window.batchRenderSymbolIcon(cfg)""",
                        {
                            "symbolKey": symbol_key,
                            "resolution": resolution,
                            "theme": theme,
                        },
                    )
                    if not data_url or not data_url.startswith("data:image/png;base64,"):
                        raise RuntimeError(f"Failed to render {symbol_key} {resolution} {theme}")

                    raw = base64.b64decode(data_url.split(",", 1)[1])
                    filename = safe_name(name, theme)
                    path = OUT / str(resolution) / theme / filename
                    path.write_bytes(raw)
                    records.append(
                        {
                            "key": symbol_key,
                            "name": name,
                            "theme": theme,
                            "resolution": resolution,
                            "path": str(path.relative_to(ROOT)),
                        }
                    )

        browser.close()

    return records, specs


def create_review_png(specs: list[dict]) -> Path:
    from PIL import Image, ImageDraw, ImageFont

    cols_per_section = len(RESOLUTIONS) * 2
    col_gap = 12
    row_gap = 12
    header_h = 28
    max_cell = max(symbol_size(r) for r in RESOLUTIONS)
    cell = max_cell
    n_icons = len(specs)

    content_w = cols_per_section * cell + (cols_per_section - 1) * col_gap
    row_h = cell + row_gap
    content_h = n_icons * row_h
    width = REVIEW_PAD * 2 + content_w
    height = REVIEW_PAD * 2 + header_h + content_h

    sheet = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    try:
        font = ImageFont.truetype(str(ROOT / "fonts" / "PixelifySans-SemiBold.ttf"), 11)
    except OSError:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(sheet)

    x0 = REVIEW_PAD
    y0 = REVIEW_PAD
    col = 0
    for res in RESOLUTIONS:
        sz = symbol_size(res)
        for theme in ("light", "dark"):
            cx = x0 + col * (cell + col_gap) + (cell - sz) // 2
            draw.text((cx, y0), f"{res}% {theme}", fill=(80, 80, 80, 255), font=font)
            col += 1

    y = y0 + header_h
    for spec in specs:
        col = 0
        name = spec["name"]
        for res in RESOLUTIONS:
            sz = symbol_size(res)
            for theme in ("light", "dark"):
                rel = OUT / str(res) / theme / safe_name(name, theme)
                icon = Image.open(rel).convert("RGBA")
                if icon.size[0] != sz:
                    icon = icon.resize((sz, sz), Image.NEAREST)
                cx = x0 + col * (cell + col_gap) + (cell - sz) // 2
                sheet.paste(icon, (cx, y), icon)
                col += 1
        y += row_h

    out_path = OUT / "review.png"
    sheet.save(out_path, "PNG")
    return out_path


def main() -> None:
    try:
        import playwright  # noqa: F401
    except ImportError:
        print("Install playwright: pip install playwright && playwright install chromium")
        sys.exit(1)

    records, specs = export_all()
    review = create_review_png(specs)
    manifest = OUT / "manifest.json"
    manifest.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")

    unique = len(specs)
    print(f"Exported {len(records)} symbol icons ({unique} symbols × {len(RESOLUTIONS)} resolutions × 2 themes)")
    print(f"Output:      {OUT}")
    print(f"Review PNG:  {review}")
    print(f"Manifest:    {manifest}")


if __name__ == "__main__":
    main()
