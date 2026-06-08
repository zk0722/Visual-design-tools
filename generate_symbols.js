#!/usr/bin/env node
/**
 * Reference generator for GD&T special symbols (16×16, 1px stroke).
 * See SYMBOL_GENERATION.md for rules and size tokens.
 *
 * Usage:
 *   node generate_symbols.js           # write preview_symbols.png only
 *   node generate_symbols.js --write   # also update custom-symbols.json + index.html
 */
const fs = require('fs');
const zlib = require('zlib');

const SIZE = 16;
const WRITE = process.argv.includes('--write');
const GLYPH_KEYS = ['integral', 'section', 'centerline'];

// ---------- rasterizer ----------
function plot(set, x, y) {
  x = Math.round(x);
  y = Math.round(y);
  if (x < 0 || y < 0 || x >= SIZE || y >= SIZE) return;
  set.add(`${x},${y}`);
}

function line(set, x0, y0, x1, y1) {
  x0 = Math.round(x0);
  y0 = Math.round(y0);
  x1 = Math.round(x1);
  y1 = Math.round(y1);
  let dx = Math.abs(x1 - x0);
  let dy = Math.abs(y1 - y0);
  let sx = x0 < x1 ? 1 : -1;
  let sy = y0 < y1 ? 1 : -1;
  let err = dx - dy;
  while (true) {
    plot(set, x0, y0);
    if (x0 === x1 && y0 === y1) break;
    const e2 = 2 * err;
    if (e2 > -dy) { err -= dy; x0 += sx; }
    if (e2 < dx) { err += dx; y0 += sy; }
  }
}

function polyline(set, pts, close) {
  for (let i = 0; i < pts.length - 1; i++) {
    line(set, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]);
  }
  if (close) {
    line(set, pts[pts.length - 1][0], pts[pts.length - 1][1], pts[0][0], pts[0][1]);
  }
}

function rect(set, x, y, w, h) {
  polyline(set, [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], true);
}

function quad(set, x0, y0, cx, cy, x1, y1) {
  const steps = 40;
  let prev = null;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const u = 1 - t;
    const x = u * u * x0 + 2 * u * t * cx + t * t * x1;
    const y = u * u * y0 + 2 * u * t * cy + t * t * y1;
    const p = [x, y];
    if (prev) line(set, prev[0], prev[1], p[0], p[1]);
    prev = p;
  }
}

/** Midpoint circle — 1px outline on integer grid (preferred over arc sampling). */
function circleOutline(set, cx, cy, r) {
  r = Math.round(r);
  if (r <= 0) {
    plot(set, cx, cy);
    return;
  }
  let x = 0;
  let y = r;
  let d = 3 - 2 * r;
  const pts = (px, py) => {
    plot(set, cx + px, cy + py);
    plot(set, cx - px, cy + py);
    plot(set, cx + px, cy - py);
    plot(set, cx - px, cy - py);
    plot(set, cx + py, cy + px);
    plot(set, cx - py, cy + px);
    plot(set, cx + py, cy - px);
    plot(set, cx - py, cy - px);
  };
  while (x <= y) {
    pts(x, y);
    if (d < 0) d += 4 * x + 6;
    else { d += 4 * (x - y) + 10; y--; }
    x++;
  }
}

function filledRect(set, x0, y0, x1, y1) {
  for (let y = Math.min(y0, y1); y <= Math.max(y0, y1); y++) {
    for (let x = Math.min(x0, x1); x <= Math.max(x0, x1); x++) {
      plot(set, x, y);
    }
  }
}

function mergeSets(...sets) {
  const out = new Set();
  for (const s of sets) s.forEach(k => out.add(k));
  return out;
}

function build(fn) {
  const set = new Set();
  fn(set);
  return Array.from(set).map(s => s.split(',').map(Number));
}

function setFromPixels(pixels) {
  return pixelsToSet(pixels);
}

// ---------- circle templates (see SYMBOL_GENERATION.md) ----------
const TOKENS = {
  CIRCLE_INNER: { cx: 7.5, cy: 7.5, r: 3.5 },
  CIRCLE_BODY: { cx: 6.5, cy: 7.5, r: 5 },
  CIRCLE_TINY: { cx: 7.5, cy: 7.5, r: 2.5 },
};

function circleToken(set, tokenName) {
  const t = TOKENS[tokenName];
  circleOutline(set, t.cx, t.cy, t.r);
}

function applyCircleMd(set) {
  applyPixels(set, CIRCLE_MD_PIXELS);
}

function crosshairPixels(cx, cy) {
  const set = new Set();
  const icx = Math.round(cx);
  const icy = Math.round(cy);
  line(set, icx, 0, icx, 15);
  line(set, 0, icy, 15, icy);
  return set;
}

// ---------- symbol specs ----------
function generateSymbol(key) {
  switch (key) {
    case 'straightness':
      return build(s => line(s, 1, 8, 14, 8));
    case 'flatness':
      return build(s => polyline(s, [[7, 3], [14, 3], [10, 13], [3, 13]], true));
    case 'roundness':
      return CIRCLE_MD_PIXELS.map(p => [...p]);
    case 'cylindricity':
      return build(s => {
        circleToken(s, 'CIRCLE_TINY');
        line(s, 5, 2, 2, 13);
        line(s, 12, 2, 9, 13);
      });
    case 'lineProfile':
      return build(s => quad(s, 1, 11, 7.5, 2, 14, 11));
    case 'surfaceProfile':
      return build(s => { quad(s, 1, 11, 7.5, 2, 14, 11); line(s, 1, 11, 14, 11); });
    case 'angularity':
      return build(s => { line(s, 2, 14, 14, 14); line(s, 2, 14, 14, 2); });
    case 'perpendicularity':
      return build(s => { line(s, 8, 1, 8, 14); line(s, 2, 14, 14, 14); });
    case 'parallelism':
      return build(s => { line(s, 8, 2, 3, 14); line(s, 13, 2, 8, 14); });
    case 'position': {
      const merged = mergeSets(pixelsToSet(CIRCLE_MD_PIXELS), crosshairPixels(7.5, 7.5));
      return Array.from(merged).map(k => k.split(',').map(Number));
    }
    case 'concentricity':
      return build(s => {
        applyCircleMd(s);
        filledRect(s, 6, 6, 9, 9);
      });
    case 'symmetry':
      return build(s => {
        line(s, 4, 4, 12, 4);
        line(s, 1, 8, 14, 8);
        line(s, 4, 12, 12, 12);
      });
    case 'circularRunout':
      return build(s => {
        line(s, 2, 14, 13, 3);
        polyline(s, [[10, 3], [13, 3], [13, 6]]);
      });
    case 'totalRunout':
      return build(s => {
        line(s, 2, 14, 8, 4);
        polyline(s, [[5, 4], [8, 4], [8, 7]]);
        line(s, 8, 14, 14, 4);
        polyline(s, [[11, 4], [14, 4], [14, 7]]);
        line(s, 2, 14, 8, 14);
      });
    case 'diameter':
      return build(s => {
        applyCircleMd(s);
        line(s, 1, 14, 14, 1);
      });
    case 'plusMinus':
      return build(s => {
        line(s, 8, 2, 8, 8);
        line(s, 4, 5, 12, 5);
        line(s, 4, 12, 12, 12);
      });
    case 'degree':
      return CIRCLE_SM_PIXELS.map(p => [...p]);
    case 'square':
      return build(s => rect(s, 2, 2, 12, 12));
    case 'taper':
      return build(s => polyline(s, [[2, 3], [14, 8], [2, 13]], true));
    case 'slope':
      return build(s => {
        line(s, 2, 2, 2, 13);
        line(s, 2, 13, 14, 13);
        line(s, 2, 2, 14, 13);
      });
    case 'counterbore':
      return build(s => polyline(s, [[2, 3], [2, 13], [14, 13], [14, 3]]));
    case 'countersink':
      return build(s => polyline(s, [[1, 3], [7, 12], [8, 12], [14, 3]]));
    case 'depth':
      return build(s => {
        line(s, 2, 2, 13, 2);
        line(s, 8, 2, 8, 13);
        polyline(s, [[5, 10], [8, 13], [11, 10]]);
      });
    case 'circularProjection':
      return build(s => {
        circleToken(s, 'CIRCLE_BODY');
        line(s, 11, 8, 15, 8);
        polyline(s, [[13, 6], [15, 8], [13, 10]]);
      });
    case 'between':
      return build(s => {
        line(s, 1, 8, 14, 8);
        polyline(s, [[3, 5], [1, 8], [3, 11]]);
        polyline(s, [[12, 5], [14, 8], [12, 11]]);
      });
    case 'coaxiality':
      return build(s => {
        applyCircleMd(s);
        circleToken(s, 'CIRCLE_INNER');
      });
    default:
      return null;
  }
}

// ---------- main ----------
const saved = JSON.parse(fs.readFileSync('custom-symbols.json', 'utf8'));
const keys = Object.keys(saved);

// Authoritative templates from hand-tuned custom-symbols.json
const CIRCLE_MD_PIXELS = saved.roundness;
const CIRCLE_SM_PIXELS = saved.degree;

function applyPixels(set, pixels) {
  pixels.forEach(([x, y]) => plot(set, x, y));
}

function pixelsToSet(pixels) {
  return new Set(pixels.map(p => `${p[0]},${p[1]}`));
}
const out = {};

for (const key of keys) {
  // custom-symbols.json is authoritative (extracted from reference PNGs in references/)
  out[key] = saved[key];
}

function writePreview() {
  const SCALE = 10;
  const CELL = SIZE * SCALE;
  const COLS = 5;
  const ROWS = Math.ceil(keys.length / COLS);
  const PAD = 6;
  const W = COLS * CELL + (COLS + 1) * PAD;
  const H = ROWS * CELL + (ROWS + 1) * PAD;
  const px = Buffer.alloc(W * H * 3, 245);

  function setpx(x, y, r, g, b) {
    if (x < 0 || y < 0 || x >= W || y >= H) return;
    const i = (y * W + x) * 3;
    px[i] = r;
    px[i + 1] = g;
    px[i + 2] = b;
  }

  keys.forEach((k, idx) => {
    const c = idx % COLS;
    const rr = Math.floor(idx / COLS);
    const ox = PAD + c * (CELL + PAD);
    const oy = PAD + rr * (CELL + PAD);
    for (let y = 0; y < CELL; y++) {
      for (let x = 0; x < CELL; x++) setpx(ox + x, oy + y, 255, 255, 255);
    }
    for (const [gx, gy] of out[k]) {
      for (let y = 0; y < SCALE; y++) {
        for (let x = 0; x < SCALE; x++) setpx(ox + gx * SCALE + x, oy + gy * SCALE + y, 17, 17, 17);
      }
    }
  });

  const CRC_T = (() => {
    const t = [];
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c >>> 0;
    }
    return t;
  })();

  function crc32(buf) {
    let c = 0xffffffff;
    for (let i = 0; i < buf.length; i++) c = CRC_T[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
    return c ^ 0xffffffff;
  }

  function chunk(type, data) {
    const len = Buffer.alloc(4);
    len.writeUInt32BE(data.length, 0);
    const td = Buffer.concat([Buffer.from(type), data]);
    const crc = Buffer.alloc(4);
    crc.writeUInt32BE(crc32(td) >>> 0, 0);
    return Buffer.concat([len, td, crc]);
  }

  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(W, 0);
  ihdr.writeUInt32BE(H, 4);
  ihdr[8] = 8;
  ihdr[9] = 2;
  const raw = Buffer.alloc(H * (W * 3 + 1));
  for (let y = 0; y < H; y++) {
    raw[y * (W * 3 + 1)] = 0;
    px.copy(raw, y * (W * 3 + 1) + 1, y * W * 3, (y + 1) * W * 3);
  }
  const png = Buffer.concat([
    sig,
    chunk('IHDR', ihdr),
    chunk('IDAT', zlib.deflateSync(raw)),
    chunk('IEND', Buffer.alloc(0)),
  ]);
  fs.writeFileSync('preview_symbols.png', png);
}

function writeFiles() {
  fs.writeFileSync('custom-symbols.json', JSON.stringify(out, null, 2));
  let html = fs.readFileSync('index.html', 'utf8');
  for (const k of keys) {
    if (GLYPH_KEYS.includes(k)) continue;
    const re = new RegExp("('" + k + "': \\{ name: ')([^']*)(', pixels: )\\[[\\s\\S]*?(, svg: ')([^']*)(' \\})");
    if (!re.test(html)) {
      console.warn('No index.html match for', k);
      continue;
    }
    html = html.replace(re, (m, p1, name, p3, p4, svg, p6) =>
      p1 + name + p3 + JSON.stringify(out[k]) + p4 + svg + p6);
  }
  fs.writeFileSync('index.html', html);
}

writePreview();
console.log('Preview written: preview_symbols.png');

if (WRITE) {
  writeFiles();
  console.log('Updated: custom-symbols.json, index.html');
} else {
  console.log('Dry run (glyphs preserved). Pass --write to update JSON + index.html.');
}

// Quality checks
const roundness = out.roundness.length;
const positionRing = out.position.filter(([x, y]) => {
  const d = Math.hypot(x - 7.5, y - 7.5);
  return d >= 5.8 && d <= 7.2;
}).length;
const roundSet = new Set(out.roundness.map(p => p.join(',')));
const overlap = out.position.filter(p => roundSet.has(p.join(','))).length;
console.log(`Roundness: ${roundness}px | Position ring overlap with roundness: ${overlap}/${positionRing}`);
