// One-off generator: re-rasterize GD&T symbols larger (12-16px) on a 16x16 grid
// keeping a true 1px stroke and the existing elegant geometric design.
const fs = require('fs');
const zlib = require('zlib');

const SIZE = 16;

// ---------- rasterizer ----------
function key(x, y) { return x + ',' + y; }
function plot(set, x, y) {
  x = Math.round(x); y = Math.round(y);
  if (x < 0 || y < 0 || x >= SIZE || y >= SIZE) return;
  set.add(key(x, y));
}
function line(set, x0, y0, x1, y1) {
  x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
  let dx = Math.abs(x1 - x0), dy = Math.abs(y1 - y0);
  let sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1, err = dx - dy;
  while (true) {
    plot(set, x0, y0);
    if (x0 === x1 && y0 === y1) break;
    const e2 = 2 * err;
    if (e2 > -dy) { err -= dy; x0 += sx; }
    if (e2 < dx) { err += dx; y0 += sy; }
  }
}
function polyline(set, pts, close) {
  for (let i = 0; i < pts.length - 1; i++) line(set, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]);
  if (close) line(set, pts[pts.length - 1][0], pts[pts.length - 1][1], pts[0][0], pts[0][1]);
}
function circle(set, cx, cy, r) {
  const steps = Math.max(48, Math.ceil(2 * Math.PI * r * 4));
  let prev = null;
  for (let i = 0; i <= steps; i++) {
    const a = 2 * Math.PI * i / steps;
    const p = [cx + r * Math.cos(a), cy + r * Math.sin(a)];
    if (prev) line(set, prev[0], prev[1], p[0], p[1]);
    prev = p;
  }
}
function rect(set, x, y, w, h) {
  polyline(set, [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], true);
}
function quad(set, x0, y0, cx, cy, x1, y1) {
  const steps = 40; let prev = null;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps, u = 1 - t;
    const x = u * u * x0 + 2 * u * t * cx + t * t * x1;
    const y = u * u * y0 + 2 * u * t * cy + t * t * y1;
    const p = [x, y];
    if (prev) line(set, prev[0], prev[1], p[0], p[1]);
    prev = p;
  }
}

function build(fn) {
  const set = new Set();
  fn(set);
  return Array.from(set).map(s => s.split(',').map(Number));
}

// ---------- geometry specs (enlarged, centered, 1px) ----------
const SPECS = {
  straightness: s => line(s, 1, 8, 14, 8),
  flatness: s => polyline(s, [[7, 3], [14, 3], [10, 13], [3, 13]], true),
  roundness: s => circle(s, 7.5, 7.5, 6.5),
  cylindricity: s => { circle(s, 7.5, 7.5, 2.5); line(s, 5, 2, 2, 13); line(s, 12, 2, 9, 13); },
  lineProfile: s => quad(s, 1, 11, 7.5, 2, 14, 11),
  surfaceProfile: s => { quad(s, 1, 11, 7.5, 2, 14, 11); line(s, 1, 11, 14, 11); },
  angularity: s => { line(s, 2, 14, 14, 14); line(s, 2, 14, 14, 2); },
  perpendicularity: s => { line(s, 8, 1, 8, 14); line(s, 2, 14, 14, 14); },
  parallelism: s => { line(s, 8, 2, 3, 14); line(s, 13, 2, 8, 14); },
  position: s => { circle(s, 7.5, 7.5, 6.5); line(s, 7, 0, 7, 15); line(s, 0, 7, 15, 7); },
  concentricity: s => { circle(s, 7.5, 7.5, 6.5); circle(s, 7.5, 7.5, 2.5); },
  symmetry: s => { line(s, 4, 4, 12, 4); line(s, 1, 8, 14, 8); line(s, 4, 12, 12, 12); },
  circularRunout: s => { line(s, 2, 14, 13, 3); polyline(s, [[10, 3], [13, 3], [13, 6]]); },
  totalRunout: s => { line(s, 2, 14, 8, 4); polyline(s, [[5, 4], [8, 4], [8, 7]]); line(s, 8, 14, 14, 4); polyline(s, [[11, 4], [14, 4], [14, 7]]); line(s, 2, 14, 8, 14); },
  diameter: s => { circle(s, 7.5, 7.5, 6.5); line(s, 1, 14, 14, 1); },
  plusMinus: s => { line(s, 8, 2, 8, 8); line(s, 4, 5, 12, 5); line(s, 4, 12, 12, 12); },
  degree: s => circle(s, 7, 8, 4),
  square: s => rect(s, 2, 2, 12, 12),
  taper: s => polyline(s, [[2, 3], [14, 8], [2, 13]], true),
  slope: s => { line(s, 2, 2, 2, 13); line(s, 2, 13, 14, 13); line(s, 2, 2, 14, 13); },
  counterbore: s => polyline(s, [[2, 3], [2, 13], [14, 13], [14, 3]]),
  countersink: s => polyline(s, [[1, 3], [7, 12], [8, 12], [14, 3]]),
  depth: s => { line(s, 2, 2, 13, 2); line(s, 8, 2, 8, 13); polyline(s, [[5, 10], [8, 13], [11, 10]]); },
  circularProjection: s => { circle(s, 6, 8, 5); line(s, 11, 8, 15, 8); polyline(s, [[13, 6], [15, 8], [13, 10]]); },
  between: s => { line(s, 1, 8, 14, 8); polyline(s, [[3, 5], [1, 8], [3, 11]]); polyline(s, [[12, 5], [14, 8], [12, 11]]); },
  coaxiality: s => { circle(s, 7.5, 7.5, 6.5); circle(s, 7.5, 7.5, 3.5); },
};
// kept as-is (already tall glyphs): integral, section, centerline

// ---------- apply ----------
const json = JSON.parse(fs.readFileSync('custom-symbols.json', 'utf8'));
const out = {};
for (const k of Object.keys(json)) {
  out[k] = SPECS[k] ? build(SPECS[k]) : json[k];
}
fs.writeFileSync('custom-symbols.json', JSON.stringify(out, null, 2));

// update index.html pixels for regenerated symbols
let html = fs.readFileSync('index.html', 'utf8');
for (const k of Object.keys(SPECS)) {
  const re = new RegExp("('" + k + "': \\{ name: ')([^']*)(', pixels: )\\[[\\s\\S]*?(, svg: ')([^']*)(' \\})");
  if (!re.test(html)) { console.warn('NO MATCH:', k); continue; }
  html = html.replace(re, (m, p1, name, p3, p4, svg, p6) =>
    p1 + name + p3 + JSON.stringify(out[k]) + p4 + svg + p6);
}
fs.writeFileSync('index.html', html);

// ---------- PNG contact sheet preview ----------
const order = Object.keys(json);
const SCALE = 10, CELL = SIZE * SCALE, COLS = 5, ROWS = Math.ceil(order.length / COLS), PAD = 6;
const W = COLS * CELL + (COLS + 1) * PAD, H = ROWS * CELL + (ROWS + 1) * PAD;
const px = Buffer.alloc(W * H * 3, 245); // light gray bg
function setpx(x, y, r, g, b) { if (x < 0 || y < 0 || x >= W || y >= H) return; const i = (y * W + x) * 3; px[i] = r; px[i + 1] = g; px[i + 2] = b; }
order.forEach((k, idx) => {
  const c = idx % COLS, rr = Math.floor(idx / COLS);
  const ox = PAD + c * (CELL + PAD), oy = PAD + rr * (CELL + PAD);
  for (let y = 0; y < CELL; y++) for (let x = 0; x < CELL; x++) setpx(ox + x, oy + y, 255, 255, 255); // white cell
  for (const [gx, gy] of out[k]) for (let y = 0; y < SCALE; y++) for (let x = 0; x < SCALE; x++) setpx(ox + gx * SCALE + x, oy + gy * SCALE + y, 17, 17, 17);
});
// encode PNG
function chunk(type, data) {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length, 0);
  const td = Buffer.concat([Buffer.from(type), data]);
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td) >>> 0, 0);
  return Buffer.concat([len, td, crc]);
}
const CRC_T = (() => { const t = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
function crc32(buf) { let c = 0xffffffff; for (let i = 0; i < buf.length; i++) c = CRC_T[(c ^ buf[i]) & 0xff] ^ (c >>> 8); return c ^ 0xffffffff; }
const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(W, 0); ihdr.writeUInt32BE(H, 4); ihdr[8] = 8; ihdr[9] = 2;
const raw = Buffer.alloc(H * (W * 3 + 1));
for (let y = 0; y < H; y++) { raw[y * (W * 3 + 1)] = 0; px.copy(raw, y * (W * 3 + 1) + 1, y * W * 3, (y + 1) * W * 3); }
const idat = zlib.deflateSync(raw);
const png = Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
fs.writeFileSync('preview_symbols.png', png);

console.log('done. order:', order.join(', '));
