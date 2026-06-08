// Enlarge the glyph-style symbols (integral, section, centerline) by scaling
// their EXISTING hand-drawn pixel design up to fill the canvas, re-rasterized
// at a true 1px stroke (connect originally-adjacent pixels after scaling).
const fs = require('fs');
const zlib = require('zlib');
const SIZE = 16;
const GLYPHS = ['integral', 'section', 'centerline'];
const TARGET = 15; // largest dimension spans ~15px

function plot(set, x, y) { x = Math.round(x); y = Math.round(y); if (x < 0 || y < 0 || x >= SIZE || y >= SIZE) return; set.add(x + ',' + y); }
function line(set, x0, y0, x1, y1) {
  x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
  let dx = Math.abs(x1 - x0), dy = Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1, err = dx - dy;
  while (true) { plot(set, x0, y0); if (x0 === x1 && y0 === y1) break; const e2 = 2 * err; if (e2 > -dy) { err -= dy; x0 += sx; } if (e2 < dx) { err += dx; y0 += sy; } }
}
function scaleGlyph(pts) {
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  const minx = Math.min(...xs), miny = Math.min(...ys), maxx = Math.max(...xs), maxy = Math.max(...ys);
  const f = TARGET / Math.max(maxx - minx, maxy - miny);
  const sp = p => [(p[0] - minx) * f, (p[1] - miny) * f];
  const set = new Set();
  for (const p of pts) { const q = sp(p); plot(set, q[0], q[1]); }
  for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) {
    if (Math.abs(pts[i][0] - pts[j][0]) <= 1 && Math.abs(pts[i][1] - pts[j][1]) <= 1) {
      const a = sp(pts[i]), b = sp(pts[j]); line(set, a[0], a[1], b[0], b[1]);
    }
  }
  let arr = Array.from(set).map(s => s.split(',').map(Number));
  const nx = arr.map(p => p[0]), ny = arr.map(p => p[1]);
  const ox = Math.round((SIZE - 1 - (Math.max(...nx) + Math.min(...nx))) / 2);
  const oy = Math.round((SIZE - 1 - (Math.max(...ny) + Math.min(...ny))) / 2);
  const out = new Set();
  for (const p of arr) plot(out, p[0] + ox, p[1] + oy);
  return Array.from(out).map(s => s.split(',').map(Number));
}

const json = JSON.parse(fs.readFileSync('custom-symbols.json', 'utf8'));
for (const k of GLYPHS) json[k] = scaleGlyph(json[k]);
fs.writeFileSync('custom-symbols.json', JSON.stringify(json, null, 2));

let html = fs.readFileSync('index.html', 'utf8');
for (const k of GLYPHS) {
  const re = new RegExp("('" + k + "': \\{ name: ')([^']*)(', pixels: )\\[[\\s\\S]*?(, svg: ')([^']*)(' \\})");
  html = html.replace(re, (m, p1, name, p3, p4, svg, p6) => p1 + name + p3 + JSON.stringify(json[k]) + p4 + svg + p6);
}
fs.writeFileSync('index.html', html);

// regenerate preview
const order = Object.keys(json);
const SCALE = 10, CELL = SIZE * SCALE, COLS = 5, ROWS = Math.ceil(order.length / COLS), PAD = 6;
const W = COLS * CELL + (COLS + 1) * PAD, H = ROWS * CELL + (ROWS + 1) * PAD;
const px = Buffer.alloc(W * H * 3, 245);
function setpx(x, y, r, g, b) { if (x < 0 || y < 0 || x >= W || y >= H) return; const i = (y * W + x) * 3; px[i] = r; px[i + 1] = g; px[i + 2] = b; }
order.forEach((k, idx) => {
  const c = idx % COLS, rr = Math.floor(idx / COLS), ox = PAD + c * (CELL + PAD), oy = PAD + rr * (CELL + PAD);
  for (let y = 0; y < CELL; y++) for (let x = 0; x < CELL; x++) setpx(ox + x, oy + y, 255, 255, 255);
  for (const [gx, gy] of json[k]) for (let y = 0; y < SCALE; y++) for (let x = 0; x < SCALE; x++) setpx(ox + gx * SCALE + x, oy + gy * SCALE + y, 17, 17, 17);
});
const CRC_T = (() => { const t = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
function crc32(buf) { let c = 0xffffffff; for (let i = 0; i < buf.length; i++) c = CRC_T[(c ^ buf[i]) & 0xff] ^ (c >>> 8); return c ^ 0xffffffff; }
function chunk(type, data) { const len = Buffer.alloc(4); len.writeUInt32BE(data.length, 0); const td = Buffer.concat([Buffer.from(type), data]); const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td) >>> 0, 0); return Buffer.concat([len, td, crc]); }
const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(W, 0); ihdr.writeUInt32BE(H, 4); ihdr[8] = 8; ihdr[9] = 2;
const raw = Buffer.alloc(H * (W * 3 + 1));
for (let y = 0; y < H; y++) { raw[y * (W * 3 + 1)] = 0; px.copy(raw, y * (W * 3 + 1) + 1, y * W * 3, (y + 1) * W * 3); }
const png = Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
fs.writeFileSync('preview_symbols.png', png);
console.log('glyphs enlarged:', GLYPHS.join(', '));
