// Reusable set pieces for the "night town" world.
// Each prop draws itself in world space; the scene decides layer/parallax.

import { inkPoly, inkLine, glow, softEllipse } from './draw.js';
import { rng, noise1, lerp } from './core.js';

export const PALETTE = {
  ink: '#0b0a18',
  skyTop: '#070a1c',
  skyMid: '#1a1838',
  skyLow: '#3a2c55',
  moon: '#f3e7c4',
  moonGlow: 'rgba(214,200,255,0.55)',
  cloud: '#1e1d3d',
  cloudRim: '#4b4677',
  fog: 'rgba(120,110,170,1)',
  lampLight: 'rgba(255,190,110,1)',
  windowCore: '#ffd88a',
  windowEdge: '#e08a3c',
  windowGlow: 'rgba(255,170,80,1)',
  glassDark: '#151428',
  walls: ['#1f2740', '#272040', '#1a2c3a', '#2c2342', '#203244', '#32263c'],
  roofs: ['#141327', '#18152c', '#101a26', '#1c1530'],
  rim: 'rgba(170,180,255,0.13)',
  ground: '#141225',
  road: '#1c1a30',
};

// ---------- Sky ----------
export function drawSky(ctx, W, H, t, opt) {
  const g = ctx.createLinearGradient(0, -200, 0, H);
  g.addColorStop(0, PALETTE.skyTop);
  g.addColorStop(0.55, PALETTE.skyMid);
  g.addColorStop(1, PALETTE.skyLow);
  ctx.fillStyle = g;
  ctx.fillRect(-W, -H, W * 3, H * 3);

  // Stars (twinkle)
  const r = rng(7);
  for (let i = 0; i < 160; i++) {
    const x = r() * W * 1.4 - W * 0.2, y = r() * H * 0.55 - 120;
    const s = r() * 1.6 + 0.4;
    const tw = 0.55 + 0.45 * Math.sin(t * (1 + r() * 3) + i);
    ctx.globalAlpha = tw * (0.4 + r() * 0.6);
    ctx.fillStyle = '#e9e4ff';
    ctx.fillRect(x, y, s, s);
  }
  ctx.globalAlpha = 1;

  // Moon
  const { mx, my, mr } = opt.moon;
  glow(ctx, mx, my, mr * 6, 'rgba(150,140,230,0.35)');
  glow(ctx, mx, my, mr * 2.4, PALETTE.moonGlow, 0.8);
  ctx.fillStyle = PALETTE.moon;
  ctx.beginPath();
  ctx.arc(mx, my, mr, 0, Math.PI * 2);
  ctx.fill();
  // craters in flat gouache
  ctx.fillStyle = 'rgba(190,170,140,0.45)';
  [[-0.3, -0.2, 0.22], [0.25, 0.15, 0.16], [-0.05, 0.35, 0.12], [0.35, -0.35, 0.09]].forEach(([dx, dy, rr]) => {
    ctx.beginPath();
    ctx.arc(mx + dx * mr, my + dy * mr, rr * mr, 0, Math.PI * 2);
    ctx.fill();
  });
}

// Flat cut-paper clouds that drift slowly
export function drawClouds(ctx, t, clouds, boil) {
  clouds.forEach((c, i) => {
    const x = c.x + t * c.speed;
    const pts = [];
    const n = 22;
    for (let k = 0; k <= n; k++) {
      const a = (k / n) * Math.PI;
      const bump = 1 + 0.18 * Math.sin(k * 2.3 + i) + 0.1 * Math.sin(k * 5.1 + i * 3);
      pts.push([x + Math.cos(Math.PI - a) * c.w * 0.5, c.y - Math.sin(a) * c.h * bump]);
    }
    pts.push([x + c.w * 0.45, c.y + c.h * 0.12], [x - c.w * 0.45, c.y + c.h * 0.12]);
    inkPoly(ctx, pts, { fill: PALETTE.cloud, ink: PALETTE.cloudRim, lw: 1.6, amp: 1.5, seed: 50 + i, boil });
    ctx.globalAlpha = c.alpha ?? 1;
  });
  ctx.globalAlpha = 1;
}

// ---------- Distant town silhouette ----------
export function drawFarTown(ctx, W, baseY, seed, t) {
  const r = rng(seed);
  ctx.fillStyle = '#1b1735';
  ctx.beginPath();
  ctx.moveTo(-W * 0.5, baseY + 200);
  let x = -W * 0.5;
  const tops = [];
  while (x < W * 1.5) {
    const w = 30 + r() * 60, h = 30 + r() * 70;
    const steep = r() < 0.5;
    ctx.lineTo(x, baseY - h);
    if (steep) ctx.lineTo(x + w / 2, baseY - h - 20 - r() * 25);
    ctx.lineTo(x + w, baseY - h);
    tops.push([x, w, h]);
    if (r() < 0.08) { // church spire / water tower
      ctx.lineTo(x + w, baseY - h - 70);
      ctx.lineTo(x + w + 8, baseY - h - 110);
      ctx.lineTo(x + w + 16, baseY - h - 70);
      ctx.lineTo(x + w + 16, baseY - h);
      x += 16;
    }
    x += w;
  }
  ctx.lineTo(W * 1.5, baseY + 200);
  ctx.closePath();
  ctx.fill();
  // Tiny lit windows — every one lit
  tops.forEach(([tx, w, h], i) => {
    const cols = Math.max(1, Math.floor(w / 18));
    const rows = Math.max(1, Math.floor(h / 22));
    for (let c = 0; c < cols; c++) for (let rr = 0; rr < rows; rr++) {
      if (hashGate(i, c, rr)) continue;
      const wx = tx + 6 + c * 18, wy = baseY - h + 8 + rr * 22;
      ctx.fillStyle = '#e9a85a';
      ctx.fillRect(wx, wy, 5, 7);
      glow(ctx, wx + 2.5, wy + 3.5, 10, 'rgba(255,160,70,0.5)', 0.5);
    }
  });
}
function hashGate(a, b, c) {
  const s = Math.sin(a * 12.9 + b * 78.2 + c * 37.7) * 43758.5;
  return s - Math.floor(s) < 0.35;
}

// ---------- Houses ----------
// h = { x, base, w, h, roofH, roof:'gable'|'steep'|'flat'|'mansard', lean, wall, roofCol,
//       windows:[{x,y,w,h,kind,decor,id,arch}], chimney:{x,h}, door:{x,w,h}, seed }
export function drawHouse(ctx, h, t, boil, lightFor, insideFor, lw = 2) {
  const L = h.x - h.w / 2, R = h.x + h.w / 2, B = h.base, T = h.base - h.h;
  const lean = h.lean || 0; // top-shift in px
  const wall = [[L, B], [R, B], [R + lean, T], [L + lean, T]];

  // chimney behind roof
  if (h.chimney) {
    const cx = L + lean + h.chimney.x;
    inkPoly(ctx, [[cx, T], [cx + 26, T], [cx + 28 + lean * 0.2, T - h.roofH * 0.6 - h.chimney.h], [cx - 2 + lean * 0.2, T - h.roofH * 0.6 - h.chimney.h]],
      { fill: h.roofCol, ink: PALETTE.ink, lw, seed: h.seed + 9, boil });
  }

  inkPoly(ctx, wall, { fill: h.wall, ink: PALETTE.ink, lw, seed: h.seed, boil });

  // clapboard texture lines
  ctx.save();
  pathRect(ctx, wall);
  ctx.clip();
  ctx.strokeStyle = 'rgba(0,0,0,0.18)';
  ctx.lineWidth = lw * 0.5;
  for (let y = B - 14; y > T; y -= 14) {
    const k = (B - y) / (B - T);
    ctx.beginPath();
    ctx.moveTo(L + lean * k, y);
    ctx.lineTo(R + lean * k, y + Math.sin(y * 0.3 + h.seed) * 1.2);
    ctx.stroke();
  }
  // moonlight rim on left edge
  const rim = ctx.createLinearGradient(L, 0, L + h.w * 0.35, 0);
  rim.addColorStop(0, PALETTE.rim);
  rim.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = rim;
  ctx.fillRect(L - 10 + Math.min(0, lean), T - 10, h.w * 0.5 + Math.abs(lean), h.h + 20);
  // shadow toward the right
  const sh = ctx.createLinearGradient(R - h.w * 0.4, 0, R + lean, 0);
  sh.addColorStop(0, 'rgba(0,0,0,0)');
  sh.addColorStop(1, 'rgba(5,3,15,0.35)');
  ctx.fillStyle = sh;
  ctx.fillRect(R - h.w * 0.4, T - 10, h.w * 0.4 + Math.abs(lean) + 10, h.h + 20);
  ctx.restore();

  // roof
  const over = 14;
  let roof;
  if (h.roof === 'flat') {
    roof = [[L + lean - over, T], [R + lean + over, T], [R + lean + over * 0.6, T - 18], [L + lean - over * 0.6, T - 18]];
  } else if (h.roof === 'mansard') {
    roof = [[L + lean - over, T], [R + lean + over, T], [R + lean - 20, T - h.roofH], [L + lean + 20, T - h.roofH]];
  } else {
    const peakX = (L + R) / 2 + lean * 1.25 + (h.peakShift || 0);
    roof = [[L + lean - over, T + 4], [R + lean + over, T + 4], [peakX, T - h.roofH]];
  }
  inkPoly(ctx, roof, { fill: h.roofCol, ink: PALETTE.ink, lw, seed: h.seed + 3, boil });
  // shingle rows with staggered tile ticks + weathering (reads at close range)
  ctx.save();
  pathRect(ctx, roof);
  ctx.clip();
  ctx.lineWidth = lw * 0.5;
  let row = 0;
  for (let y = T; y > T - h.roofH - 20; y -= 9, row++) {
    ctx.strokeStyle = 'rgba(0,0,0,0.28)';
    ctx.beginPath();
    ctx.moveTo(L - 40, y);
    ctx.lineTo(R + 40 + lean * 2, y + Math.sin(row * 1.7 + h.seed) * 0.8);
    ctx.stroke();
    ctx.strokeStyle = 'rgba(150,140,230,0.07)';
    ctx.beginPath();
    ctx.moveTo(L - 40, y - 1.5);
    ctx.lineTo(R + 40 + lean * 2, y - 1.5);
    ctx.stroke();
    ctx.strokeStyle = 'rgba(0,0,0,0.22)';
    for (let x = L - 40 + (row % 2) * 7; x < R + 40; x += 14) {
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + 0.6, y - 8);
      ctx.stroke();
    }
  }
  const wr = rng(h.seed + 400);
  for (let k = 0; k < 14; k++) {
    softEllipse(ctx, L + wr() * h.w, T - wr() * h.roofH, 8 + wr() * 18, 4 + wr() * 6, 'rgba(0,0,0,1)', 0.18, 'source-over');
  }
  ctx.restore();

  // door
  if (h.door) {
    const dx = L + h.door.x;
    inkPoly(ctx, [[dx, B], [dx + h.door.w, B], [dx + h.door.w, B - h.door.h], [dx, B - h.door.h]],
      { fill: '#120f22', ink: PALETTE.ink, lw, seed: h.seed + 5, boil });
    // porch light — on, but nobody home
    glow(ctx, dx + h.door.w + 10, B - h.door.h - 6, 60, 'rgba(255,180,90,0.55)', 0.8);
    ctx.fillStyle = '#ffe1a0';
    ctx.fillRect(dx + h.door.w + 6, B - h.door.h - 12, 8, 10);
  }

  // windows
  (h.windows || []).forEach((w, i) => {
    const k = (B - (B - w.y)) / h.h; // fraction up the wall for lean
    const wx = L + w.x + lean * ((w.y) / h.h);
    const wy = B - w.y;
    const lvl = lightFor ? lightFor(h, w, t) : 1;
    drawWindow(ctx, { ...w, x: wx, y: wy, seed: h.seed * 10 + i }, lvl, boil, insideFor ? insideFor(h, w, t) : null, lw);
  });
}

function pathRect(ctx, pts) {
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  ctx.closePath();
}

// Window at top-left (x,y), size (w,h). level 0..1 = interior light.
// `inside(ctx, rect, level)` lets a scene draw something behind the glass.
export function drawWindow(ctx, w, level, boil, inside, lw = 2) {
  const { x, y } = w;
  const W = w.w, H = w.h;
  const arch = w.arch ? W * 0.5 : 0;
  const shape = arch
    ? arcPts(x, y, W, H, arch)
    : [[x, y], [x + W, y], [x + W, y + H], [x, y + H]];

  // outer glow (behind frame)
  glow(ctx, x + W / 2, y + H / 2, Math.max(W, H) * 1.9, PALETTE.windowGlow, 0.3 * level);

  // glass
  ctx.save();
  pathRect(ctx, shape);
  ctx.clip();
  const g = ctx.createRadialGradient(x + W / 2, y + H * 0.55, 2, x + W / 2, y + H / 2, Math.max(W, H) * 0.8);
  g.addColorStop(0, mixColor('#2a2238', PALETTE.windowCore, level));
  g.addColorStop(1, mixColor(PALETTE.glassDark, PALETTE.windowEdge, level * 0.9));
  ctx.fillStyle = g;
  ctx.fillRect(x - 5, y - arch - 5, W + 10, H + arch + 10);

  // interior decor: empty rooms
  const ic = `rgba(60,25,20,${0.55 * Math.max(level, 0.15)})`;
  ctx.fillStyle = ic;
  if (w.decor === 'lamp') {
    ctx.beginPath();
    ctx.moveTo(x + W * 0.62, y + H * 0.55);
    ctx.lineTo(x + W * 0.82, y + H * 0.55);
    ctx.lineTo(x + W * 0.77, y + H * 0.4);
    ctx.lineTo(x + W * 0.67, y + H * 0.4);
    ctx.fill();
    ctx.fillRect(x + W * 0.715, y + H * 0.55, W * 0.03, H * 0.3);
    ctx.fillRect(x, y + H * 0.85, W, H * 0.15);
  } else if (w.decor === 'plant') {
    ctx.fillRect(x + W * 0.3, y + H * 0.82, W * 0.25, H * 0.18);
    for (let k = 0; k < 6; k++) {
      ctx.beginPath();
      ctx.ellipse(x + W * 0.42 + Math.cos(k) * W * 0.12, y + H * (0.7 - k * 0.04), W * 0.08, H * 0.04, k, 0, Math.PI * 2);
      ctx.fill();
    }
  } else if (w.decor === 'chair') {
    ctx.fillRect(x + W * 0.2, y + H * 0.45, W * 0.08, H * 0.45);
    ctx.fillRect(x + W * 0.2, y + H * 0.66, W * 0.35, H * 0.06);
    ctx.fillRect(x + W * 0.5, y + H * 0.66, W * 0.05, H * 0.24);
  } else if (w.decor === 'frame') {
    ctx.fillRect(x + W * 0.55, y + H * 0.2, W * 0.22, H * 0.25);
  }

  if (inside) inside(ctx, { x, y, w: W, h: H, arch }, level);

  // curtains
  if (w.curtain) {
    const cc = mixColor('#1a0f1c', '#b0532c', level * 0.8);
    ctx.fillStyle = cc;
    const sway = Math.sin(boil * 0.7 + w.seed) * 0.6;
    ctx.beginPath();
    ctx.moveTo(x, y - arch);
    ctx.lineTo(x + W * 0.24, y - arch);
    ctx.quadraticCurveTo(x + W * 0.12 + sway, y + H * 0.55, x + W * 0.2, y + H);
    ctx.lineTo(x, y + H);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(x + W, y - arch);
    ctx.lineTo(x + W * 0.76, y - arch);
    ctx.quadraticCurveTo(x + W * 0.88 - sway, y + H * 0.55, x + W * 0.8, y + H);
    ctx.lineTo(x + W, y + H);
    ctx.fill();
  }
  // glass sheen
  ctx.fillStyle = `rgba(255,255,255,${0.06 + 0.05 * level})`;
  ctx.beginPath();
  ctx.moveTo(x + W * 0.1, y + H);
  ctx.lineTo(x + W * 0.45, y - arch);
  ctx.lineTo(x + W * 0.58, y - arch);
  ctx.lineTo(x + W * 0.23, y + H);
  ctx.fill();
  ctx.restore();

  // mullions + frame
  const fl = lw * 1.1;
  inkLine(ctx, [x + W / 2, y - arch], [x + W / 2, y + H], { ink: PALETTE.ink, lw: fl * 1.3, seed: w.seed + 1, boil, amp: 0.6 });
  inkLine(ctx, [x, y + H * 0.48], [x + W, y + H * 0.48], { ink: PALETTE.ink, lw: fl * 1.3, seed: w.seed + 2, boil, amp: 0.6 });
  inkPoly(ctx, shape, { ink: PALETTE.ink, lw: fl * 1.8, seed: w.seed + 3, boil, amp: 0.8 });
  // sill
  inkPoly(ctx, [[x - 5, y + H], [x + W + 5, y + H], [x + W + 3, y + H + 6], [x - 3, y + H + 6]],
    { fill: '#3c3757', ink: PALETTE.ink, lw: fl, seed: w.seed + 4, boil, amp: 0.6 });

  // light spill below the sill
  softEllipse(ctx, x + W / 2, y + H + 18, W * 0.9, 16, 'rgba(255,160,80,0.5)', 0.45 * level);
}

function arcPts(x, y, W, H, arch) {
  const pts = [[x, y + H], [x, y]];
  for (let k = 1; k < 12; k++) {
    const a = Math.PI - (k / 12) * Math.PI;
    pts.push([x + W / 2 + Math.cos(a) * W / 2, y - Math.sin(a) * arch]);
  }
  pts.push([x + W, y], [x + W, y + H]);
  return pts;
}

export function mixColor(a, b, k) {
  const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
  const ch = (p, s) => (p >> s) & 255;
  const m = (s) => Math.round(lerp(ch(pa, s), ch(pb, s), Math.max(0, Math.min(1, k))));
  return `rgb(${m(16)},${m(8)},${m(0)})`;
}

// ---------- Street furniture ----------
export function drawLamp(ctx, x, base, h, boil, seed, lw = 2, on = 1) {
  inkPoly(ctx, [[x - 4, base], [x + 4, base], [x + 3, base - h], [x - 3, base - h]], { fill: '#0f0d1d', ink: PALETTE.ink, lw, seed, boil });
  inkPoly(ctx, [[x, base - h], [x + 30, base - h - 8], [x + 32, base - h - 2], [x + 2, base - h + 6]], { fill: '#0f0d1d', ink: PALETTE.ink, lw, seed: seed + 1, boil });
  inkPoly(ctx, [[x + 22, base - h - 6], [x + 40, base - h - 6], [x + 36, base - h + 10], [x + 26, base - h + 10]], { fill: '#ffd98f', ink: PALETTE.ink, lw, seed: seed + 2, boil });
  glow(ctx, x + 31, base - h + 4, 120, 'rgba(255,190,100,0.6)', on);
  // cone of light
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  const g = ctx.createLinearGradient(0, base - h, 0, base);
  g.addColorStop(0, 'rgba(255,190,110,0.16)');
  g.addColorStop(1, 'rgba(255,190,110,0.0)');
  ctx.fillStyle = g;
  ctx.globalAlpha = on;
  ctx.beginPath();
  ctx.moveTo(x + 24, base - h + 10);
  ctx.lineTo(x + 38, base - h + 10);
  ctx.lineTo(x + 110, base);
  ctx.lineTo(x - 50, base);
  ctx.fill();
  ctx.restore();
  softEllipse(ctx, x + 30, base + 6, 110, 22, 'rgba(255,180,100,0.6)', 0.5 * on);
}

// Bare, crooked tree with branches that sway in the wind.
export function drawTree(ctx, x, base, scale, t, boil, seed, lw = 2, fill = '#08070f') {
  const r = rng(seed);
  ctx.fillStyle = fill;
  ctx.strokeStyle = fill;
  ctx.lineCap = 'round';
  function branch(x0, y0, ang, len, width, depth) {
    const sway = noise1(t * 0.6 + depth * 0.7, seed + depth) * 0.04 * (5 - depth);
    const a = ang + sway;
    const x1 = x0 + Math.cos(a) * len, y1 = y0 + Math.sin(a) * len;
    const mx = (x0 + x1) / 2 + (r() - 0.5) * len * 0.25, my = (y0 + y1) / 2 + (r() - 0.5) * len * 0.25;
    ctx.lineWidth = width;
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.quadraticCurveTo(mx, my, x1, y1);
    ctx.stroke();
    if (depth < 5 && len > 8) {
      const n = 2 + (r() < 0.4 ? 1 : 0);
      for (let i = 0; i < n; i++) branch(x1, y1, a + (r() - 0.5) * 1.3, len * (0.62 + r() * 0.15), width * 0.62, depth + 1);
    }
  }
  branch(x, base, -Math.PI / 2 + 0.15, 170 * scale, 26 * scale, 0);
}

export function drawFence(ctx, x0, x1, base, h, boil, seed, lw = 2) {
  const fill = '#0a0914';
  inkPoly(ctx, [[x0, base - h * 0.62], [x1, base - h * 0.6], [x1, base - h * 0.52], [x0, base - h * 0.54]], { fill, ink: PALETTE.ink, lw, seed, boil, amp: 1.5 });
  inkPoly(ctx, [[x0, base - h * 0.28], [x1, base - h * 0.26], [x1, base - h * 0.18], [x0, base - h * 0.2]], { fill, ink: PALETTE.ink, lw, seed: seed + 1, boil, amp: 1.5 });
  const r = rng(seed);
  for (let x = x0; x < x1; x += 34 + r() * 6) {
    const tilt = (r() - 0.5) * 10, hh = h * (0.9 + r() * 0.2);
    inkPoly(ctx, [[x, base + 40], [x + 20, base + 40], [x + 20 + tilt, base - hh], [x + 10 + tilt, base - hh - 14], [x + tilt, base - hh]],
      { fill, ink: PALETTE.ink, lw, seed: seed + x, boil, amp: 1.2 });
  }
}

// Layered drifting fog band (world space)
export function drawFog(ctx, x0, x1, y, thick, t, speed, alpha, seed) {
  ctx.save();
  for (let i = 0; i < 5; i++) {
    const off = ((t * speed * (1 + i * 0.3) + i * 400 + seed * 50) % 1400) - 300;
    for (let k = -1; k < Math.ceil((x1 - x0) / 700) + 1; k++) {
      softEllipse(ctx, x0 + k * 700 + off, y + Math.sin(i * 2 + seed) * thick * 0.3, 520, thick, 'rgba(110,100,160,1)', alpha * (0.5 + 0.5 * Math.sin(i + seed)), 'source-over');
    }
  }
  ctx.restore();
}
