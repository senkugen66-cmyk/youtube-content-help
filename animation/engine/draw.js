// Illustrated "ink & gouache" drawing primitives.
// The look: flat limited-palette shapes, wobbly hand-inked outlines that
// boil at 8 drawings/sec, soft additive glows, paper grain on top.

import { hash, rng } from './core.js';

// Jitter a polygon's points deterministically per boil frame.
export function wobble(points, amp, seed, boil) {
  return points.map(([x, y], i) => [
    x + (hash(seed * 13.1 + i * 7.7 + boil * 3.3) - 0.5) * 2 * amp,
    y + (hash(seed * 17.9 + i * 5.3 + boil * 9.1) - 0.5) * 2 * amp,
  ]);
}

// Subdivide straight edges so wobble reads as hand-drawn, not just shifted corners.
export function subdivide(points, maxLen = 40, closed = true) {
  const out = [];
  const n = points.length;
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const [x0, y0] = points[i];
    const [x1, y1] = points[(i + 1) % n];
    const steps = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / maxLen));
    for (let s = 0; s < steps; s++) out.push([x0 + ((x1 - x0) * s) / steps, y0 + ((y1 - y0) * s) / steps]);
  }
  if (!closed) out.push(points[n - 1]);
  return out;
}

export function pathPoly(ctx, pts, closed = true) {
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  if (closed) ctx.closePath();
}

// Filled shape with optional inked outline.
// style = { fill, ink, lw, amp, seed, boil, closed }
export function inkPoly(ctx, points, s) {
  const pts = wobble(subdivide(points, s.seg ?? 30, s.closed !== false), s.amp ?? 1.2, s.seed ?? 1, s.boil ?? 0);
  pathPoly(ctx, pts, s.closed !== false);
  if (s.fill) {
    ctx.fillStyle = s.fill;
    ctx.fill();
  }
  if (s.ink) {
    ctx.strokeStyle = s.ink;
    ctx.lineWidth = s.lw ?? 2;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.stroke();
  }
}

export function inkLine(ctx, a, b, s) {
  inkPoly(ctx, [a, b], { ...s, closed: false, fill: null, seg: s.seg ?? 25 });
}

// Soft additive light.
export function glow(ctx, x, y, r, color, alpha = 1) {
  if (alpha <= 0.001) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, color);
  g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.globalAlpha = alpha;
  ctx.fillStyle = g;
  ctx.fillRect(x - r, y - r, r * 2, r * 2);
  ctx.restore();
}

// Ellipse helper (for halos, pools of light)
export function softEllipse(ctx, x, y, rx, ry, color, alpha, mode = 'lighter') {
  if (alpha <= 0.001) return;
  ctx.save();
  ctx.globalCompositeOperation = mode;
  ctx.globalAlpha = alpha;
  ctx.translate(x, y);
  ctx.scale(1, ry / rx);
  const g = ctx.createRadialGradient(0, 0, 0, 0, 0, rx);
  g.addColorStop(0, color);
  g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g;
  ctx.fillRect(-rx, -rx, rx * 2, rx * 2);
  ctx.restore();
}

// ---------- Post-processing ----------

let grainCache = null;
function makeGrain(W, H, variants = 6) {
  const out = [];
  for (let v = 0; v < variants; v++) {
    const c = document.createElement('canvas');
    c.width = W / 2;
    c.height = H / 2;
    const g = c.getContext('2d');
    const img = g.createImageData(c.width, c.height);
    const r = rng(1000 + v);
    for (let i = 0; i < img.data.length; i += 4) {
      const n = 128 + (r() - 0.5) * 90;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = n;
      img.data[i + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    // paper fibres
    g.globalAlpha = 0.08;
    g.strokeStyle = '#fff';
    for (let k = 0; k < 220; k++) {
      const x = r() * c.width, y = r() * c.height, a = r() * Math.PI;
      g.beginPath();
      g.moveTo(x, y);
      g.lineTo(x + Math.cos(a) * 14, y + Math.sin(a) * 14);
      g.stroke();
    }
    out.push(c);
  }
  return out;
}

export function postFX(ctx, W, H, t, opts = {}) {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  // Vignette
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.0);
  v.addColorStop(0, 'rgba(0,0,0,0)');
  v.addColorStop(1, `rgba(3,2,10,${opts.vignette ?? 0.75})`);
  ctx.fillStyle = v;
  ctx.fillRect(0, 0, W, H);

  // Grain (refreshes at 12 fps, like film/paper boil)
  if (!grainCache) grainCache = makeGrain(W, H);
  const g = grainCache[Math.floor(t * 12) % grainCache.length];
  ctx.save();
  ctx.globalCompositeOperation = 'overlay';
  ctx.globalAlpha = opts.grain ?? 0.22;
  ctx.drawImage(g, 0, 0, W, H);
  ctx.restore();

  // Global fade (for blackouts / fade to black)
  if (opts.black > 0) {
    ctx.fillStyle = `rgba(2,1,6,${opts.black})`;
    ctx.fillRect(0, 0, W, H);
  }
}
