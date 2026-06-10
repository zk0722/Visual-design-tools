#!/usr/bin/env python3
"""Import 150x150 SVG design PNGs into 16x16 viewBox path markup for index.html."""

from __future__ import annotations

import io
import re
from pathlib import Path

import numpy as np
import vtracer
from PIL import Image
from svgpathtools import parse_path

ROOT = Path(__file__).resolve().parent
ASSETS = Path(
    "/Users/zhouka/.cursor/projects/Users-zhouka-Documents-AI-project-Small-Font/assets"
)
INDEX_HTML = ROOT / "index.html"
GRID = 16
MARGIN = 1
PADDING = 4

FILE_TO_KEY = {
    "Angularity": "angularity",
    "Between": "between",
    "Centerline": "centerline",
    "Circular_Projection": "circularProjection",
    "Circular_Runout": "circularRunout",
    "Coaxiality": "coaxiality",
    "Concentricity": "concentricity",
    "Counterbore": "counterbore",
    "Countersink": "countersink",
    "Cylindricity": "cylindricity",
    "Degree": "degree",
    "Depth": "depth",
    "Diameter": "diameter",
    "Flatness": "flatness",
    "Integral": "integral",
    "Line_Profile": "lineProfile",
    "Parallelism": "parallelism",
    "Perpendicularity": "perpendicularity",
    "Plus": "plusMinus",
    "Position": "position",
    "Roundness": "roundness",
    "Section": "section",
    "Square": "square",
    "Surface_Profile": "surfaceProfile",
    "Symmetry": "symmetry",
    "Taper": "taper",
    "Total_Runout": "totalRunout",
}


def visible_mask(rgba: np.ndarray) -> np.ndarray:
    return rgba[:, :, 3] > 96


def crop_symbol_rgba(rgba: np.ndarray) -> np.ndarray:
    mask = visible_mask(rgba)
    ys, xs = np.where(mask)
    minx, maxx = int(xs.min()), int(xs.max())
    miny, maxy = int(ys.min()), int(ys.max())
    minx = max(0, minx - PADDING)
    miny = max(0, miny - PADDING)
    maxx = min(rgba.shape[1] - 1, maxx + PADDING)
    maxy = min(rgba.shape[0] - 1, maxy + PADDING)
    return rgba[miny : maxy + 1, minx : maxx + 1]


def rgba_to_white_bg_png_bytes(rgba: np.ndarray) -> bytes:
    alpha = rgba[:, :, 3:4] / 255.0
    rgb = rgba[:, :, :3]
    white = np.ones_like(rgb) * 255
    comp = (rgb * alpha + white * (1.0 - alpha)).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(comp).save(buf, format="PNG")
    return buf.getvalue()


def scale_path_to_grid(path_d: str, src_w: int, src_h: int) -> str:
    path = parse_path(path_d)
    if len(path) == 0:
        return ""

    scale = min(GRID / src_w, GRID / src_h)
    path = path.scaled(scale)

    xmin, xmax, ymin, ymax = path.bbox()
    width = xmax - xmin
    height = ymax - ymin
    if width <= 0 or height <= 0:
        return path.d()

    inner = GRID - 2 * MARGIN
    fit_scale = min(inner / width, inner / height)
    ox = MARGIN + (inner - width * fit_scale) / 2 - xmin * fit_scale
    oy = MARGIN + (inner - height * fit_scale) / 2 - ymin * fit_scale
    path = path.scaled(fit_scale)
    path = path.translated(complex(ox, oy))
    return path.d()


NESTED_CIRCLE_SVG = (
    '<circle cx="7.5" cy="7.5" r="6.5" fill="none" stroke="currentColor"/>'
    '<circle cx="7.5" cy="7.5" r="3" fill="none" stroke="currentColor"/>'
)

STROKE_CIRCLE_SYMBOLS = {
    "concentricity": NESTED_CIRCLE_SVG,
    "coaxiality": NESTED_CIRCLE_SVG,
    "degree": '<circle cx="8.25" cy="8" r="2.75" fill="none" stroke="currentColor"/>',
}


def png_to_svg_markup(png_path: Path, symbol_key: str | None = None) -> str:
    if symbol_key in STROKE_CIRCLE_SYMBOLS:
        return STROKE_CIRCLE_SYMBOLS[symbol_key]
    rgba = np.array(Image.open(png_path).convert("RGBA"))
    if not visible_mask(rgba).any():
        return ""

    crop = crop_symbol_rgba(rgba)
    src_h, src_w = crop.shape[:2]
    svg = vtracer.convert_raw_image_to_svg(
        rgba_to_white_bg_png_bytes(crop),
        img_format="PNG",
        colormode="binary",
        hierarchical="stacked",
        mode="spline",
        filter_speckle=4,
        corner_threshold=60,
        length_threshold=4.0,
        path_precision=3,
    )

    path_ds = re.findall(r'd="([^"]+)"', svg)
    if not path_ds:
        return ""

    elements: list[str] = []
    for path_d in path_ds:
        if path_d.strip() in {"M0,0 L150,0 L150,150 L0,150 Z", "M0 0 L150 0 L150 150 L0 150 Z"}:
            continue
        scaled = scale_path_to_grid(path_d, src_w, src_h)
        if not scaled or scaled.startswith("M0,0 L16,0"):
            continue
        elements.append(
            f'<path d="{scaled}" fill="currentColor" fill-rule="evenodd"/>'
        )

    return "".join(elements)


def find_design_pngs() -> dict[str, Path]:
    found: dict[str, Path] = {}
    for path in ASSETS.glob("*.png"):
        if "_light" in path.name:
            continue
        if Image.open(path).size != (150, 150):
            continue
        prefix = path.name.split("-", 1)[0]
        key = FILE_TO_KEY.get(prefix)
        if key:
            found[key] = path
    return found


def update_index_html(svg_by_key: dict[str, str]) -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    updated = 0
    for key, svg in svg_by_key.items():
        if not svg:
            print(f"  skip empty svg: {key}")
            continue
        pattern = re.compile(
            rf"('{re.escape(key)}': {{ name: '[^']+', pixels: .*?, svg: ')([^']*)(')",
            re.DOTALL,
        )
        escaped = svg.replace("\\", "\\\\").replace("'", "\\'")
        html, count = pattern.subn(rf"\1{escaped}\3", html, count=1)
        if count != 1:
            raise RuntimeError(f"Failed to update svg for {key}")
        updated += 1
    INDEX_HTML.write_text(html, encoding="utf-8")
    print(f"Updated {updated} symbols in index.html")


def main() -> None:
    designs = find_design_pngs()
    print(f"Found {len(designs)} design PNGs")
    svg_by_key: dict[str, str] = {}
    for key, path in sorted(designs.items(), key=lambda item: item[0]):
        svg = png_to_svg_markup(path, key)
        svg_by_key[key] = svg
        print(f"  {key}: {svg.count('<path')} paths, {len(svg)} chars")
    update_index_html(svg_by_key)
    missing = sorted(set(FILE_TO_KEY.values()) - set(svg_by_key))
    if missing:
        print("No design PNG for:", ", ".join(missing))


if __name__ == "__main__":
    main()
