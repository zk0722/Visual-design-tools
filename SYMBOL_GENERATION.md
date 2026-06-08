# Symbol Generation Spec

Guidelines for generating the 29 GD&T special symbols on a **16×16 pixel grid** with a true **1px stroke**. Derived from hand-edited symbols in `custom-symbols.json`, especially circle-related corrections.

## Source of truth

| File | Role |
|---|---|
| `references/*.png` | Refined 16×16 reference PNGs (one per symbol) |
| `custom-symbols.json` | **Authoritative** pixel data (extracted from references) |
| `import_references.py` | Re-extract pixels from `references/` → JSON + index.html |
| `generate_symbols.js` | Preview PNG from `custom-symbols.json` |
| `index.html` | App + baked-in defaults (keep in sync with JSON) |

Re-import after editing reference PNGs:

```bash
python3 import_references.py
```

Run the generator for previews:

```bash
node generate_symbols.js              # preview PNG only
node generate_symbols.js --write      # sync index.html pixels from custom-symbols.json
```

Glyph-style symbols (`integral`, `section`, `centerline`) are copied from `custom-symbols.json` unless explicitly regenerated.

---

## Core constraints

1. **Canvas:** 16×16, transparent background on export
2. **Stroke:** exactly 1px — no double-thick diagonals or cardinal points
3. **Algorithm:** integer-grid rasterization (Bresenham / midpoint circle). **Do not** use trig arc sampling + polyline approximation (creates extra pixels and uneven thickness)
4. **Center convention:** most centered symbols use **(7.5, 7.5)** — the intersection of pixel boundaries at row/col 7–8
5. **Sizing:** not every symbol is “max size”. Use **size tokens** (below)

---

## Circle size tokens

| Token | Center | Radius | ~BBox | Used for |
|---|---|---|---|---|
| `CIRCLE_MD` | (7.5, 7.5) | 6.5 | 14×14 | Roundness, Position ring, Diameter ring, Concentricity outer, Coaxiality outer |
| `CIRCLE_INNER` | (7.5, 7.5) | 3.5 | 8×8 | Coaxiality inner ring |
| `CIRCLE_SM` | (7.5, 5.5) | 3.5 | 8×8 | Degree (small, upper-biased) |
| `CIRCLE_BODY` | (6.5, 7.5) | 5.0 | ~12×12 | Circular Projection main circle (offset left for arrow) |
| `CIRCLE_TINY` | (7.5, 7.5) | 2.5 | 6×6 | Cylindricity center circle |

**Key lesson:** `CIRCLE_MD` is the shared template for “standard GD&T circle”. Position reuses the same ring as Roundness — do not draw a separate max-size circle.

---

## Composite symbol rules

Build composites by **merging pixel sets** from primitives. Reuse templates; do not redraw similar shapes with different parameters.

### Position
```
position = CIRCLE_MD + crosshair(7.5, 7.5, extend=1)
```
Crosshair lines run from 0→15 on both axes (1px beyond the circle ring).

### Diameter
```
diameter = CIRCLE_MD + diagonal(1,14 → 14,1)
```
Diagonal endpoints sit outside the ring.

### Concentricity
```
concentricity = CIRCLE_MD + filled_dot(7.5, 7.5, 2×2)
```
Center is a **filled dot**, not a hollow small circle.

### Coaxiality
```
coaxiality = CIRCLE_MD + CIRCLE_INNER
```

### Cylindricity
```
cylindricity = CIRCLE_TINY + left_tangent(5,2→2,13) + right_tangent(12,2→9,13)
```
Tangent lines must **not** pass through the center circle.

### Circular Projection
```
circularProjection = CIRCLE_BODY + arrow_right(y=8, from x=11 to x=15)
```
Compose first, then center the group if needed. Circle is offset to leave room for the arrow.

---

## Non-circle symbols (summary)

| Symbol | Rule |
|---|---|
| Straightness | Horizontal line, y=8, x=1–14 |
| Flatness | Parallelogram; straight vertical left/right edges |
| Line Profile | Open arc (quadratic), no baseline |
| Surface Profile | Same arc + closed baseline |
| Angularity | Horizontal base + 45° diagonal |
| Perpendicularity | 1px vertical + horizontal base |
| Parallelism | Two parallel diagonals, **equal length** |
| Symmetry | Three horizontal lines |
| Plus/Minus | 1px vertical bar + two horizontals |
| Square | Rect outline, ~12×12 inset |
| Depth | 1px vertical + top bar + arrowhead |
| Integral / Section / Centerline | Hand-drawn glyphs — scale from saved pixels, do not geometrically approximate |

---

## Post-processing checklist

After rasterization, run on every symbol:

1. **Deduplicate** pixel coordinates
2. **Clip** to `[0, 15]` grid
3. **Reject** 2×2 solid blocks on 1px stroke paths (sign of overlap)
4. **Verify** roundness ring pixel count ≈ 36 for `CIRCLE_MD`
5. **Verify** position ring matches roundness ring (≥ 95% overlap)
6. Compare against AutoCAD reference screenshots when available

---

## Workflow for new symbols or updates

```
1. Define primitive tokens + composite rule
2. Generate with generate_symbols.js
3. Render contact sheet (preview_symbols.png)
4. Compare to reference / existing custom-symbols.json
5. Hand-edit in Special Symbols tab if needed
6. Save → custom-symbols.json
7. Sync index.html defaults before commit
```

---

## Lessons learned (circle edits)

| Problem | Cause | Fix |
|---|---|---|
| “Rounded rectangle” look | Wrong rasterizer / wrong radius | Midpoint circle at (7.5, 7.5), r=6.5 |
| Position circle too large | Independent max-size circle | Reuse `CIRCLE_MD` template |
| Uneven circle thickness | Arc sampling with line segments | Midpoint/Bresenham circle |
| Too many circle pixels | Over-drawn path | User edits often **remove** 10–20 spurious pixels |
| Degree too large when scaled | Applied `CIRCLE_MD` to all circles | Keep `CIRCLE_SM` for degree |
| Crosshair clipped | Lines stopped at circle edge | Extend crosshair 1px beyond ring |

---

## Files superseded by this spec

- `scale_symbols.js` — one-off enlargement script (arc sampling; do not reuse)
- `glyph_scale.js` — one-off glyph scaler (still valid approach for § ℄ ∫)

Use `generate_symbols.js` for future batch generation.
