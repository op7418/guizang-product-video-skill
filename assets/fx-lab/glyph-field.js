// Character field on a 2D canvas: glyphs whose brightness follows a moving noise field.
// Derive the glyph source from the product (its own code, CLI output, data values, a language's
// script, musical notation…) and the colour from its palette. Pure function of t.
export function createGlyphField(canvas, {source = '01', cell = [12, 22], font = '500 15px ui-monospace, monospace', color = [214, 211, 209], max = 0.55, threshold = 0.42, size = [1920, 1080]} = {}) {
  const ctx = canvas.getContext('2d'), [cw, ch] = cell, cols = Math.ceil(size[0] / cw), rows = Math.ceil(size[1] / ch);
  const h = (x, y) => { const s = Math.sin(x * 127.1 + y * 311.7) * 43758.5453; return s - Math.floor(s); };
  const noise = (x, y) => { const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi, u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf), a = h(xi, yi), b = h(xi + 1, yi), c = h(xi, yi + 1), d = h(xi + 1, yi + 1); return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v; };
  return function render(t, {fade = 1, clearCenter = 0.8} = {}) {
    ctx.clearRect(0, 0, size[0], size[1]); ctx.font = font; ctx.textBaseline = 'top';
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const n = noise(c * 0.08 + t * 0.35, r * 0.12 - t * 0.5) * 0.7 + noise(c * 0.23 - t, r * 0.3) * 0.3;
      const dx = (c * cw - size[0] / 2) / (size[0] / 2), dy = (r * ch - size[1] / 2) / (size[1] / 2);
      const centre = Math.max(0, 1 - Math.sqrt(dx * dx * 0.6 + dy * dy));
      const a = Math.max(0, n - threshold) * 1.5 * (1 - centre * clearCenter);
      if (a < 0.03) continue;
      ctx.fillStyle = `rgba(${color[0]},${color[1]},${color[2]},${Math.min(max, a) * fade})`;
      ctx.fillText(source[(c + r * cols + Math.floor(t * 12) * (1 + (r % 3))) % source.length], c * cw, r * ch);
    }
  };
}
