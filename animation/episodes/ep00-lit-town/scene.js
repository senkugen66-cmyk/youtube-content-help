// EP00 — "Every Light On" (15s proof of concept)
// A sleeping town where every window is lit and nobody is home.
// One attic window flickers. The camera creeps in. Someone is standing there.
//
// Edit the CONFIG block to re-time beats; everything else derives from it.

import { track, noise1, boilFrame, applyLayer, clamp, rng, lerp } from '../../engine/core.js';
import { postFX, inkPoly, glow, softEllipse } from '../../engine/draw.js';
import {
  PALETTE, drawSky, drawClouds, drawFarTown, drawHouse, drawWindow,
  drawLamp, drawTree, drawFence, drawFog,
} from '../../engine/props.js';

export const META = { title: 'ep00-lit-town', width: 1920, height: 1080, fps: 24, duration: 15 };

export const CONFIG = {
  // The flickering window (world coords, focal plane)
  target: { x: 1046, y: 446, w: 52, h: 64, arch: true, curtain: true, decor: null },

  // Camera: [time, [x, y, zoom], easing]. Zoom is interpolated in log space.
  camera: [
    [0.0, [890, 560, 1.0]],
    [5.0, [985, 540, 1.13], 'inOutSine'],
    [6.0, [992, 536, 1.16], 'linear'],
    [12.4, [1072, 482, 5.6], 'inOutCubic'],
    [15.0, [1072, 480, 6.4], 'linear'],
  ],
  handheld: 2.2, // px of slow camera drift (scaled down as we zoom)

  // Flicker events for the target window: [start, duration, level]
  flicker: [
    [4.55, 0.07, 0.35], [4.7, 0.05, 0.65],
    [6.8, 0.1, 0.2], [6.98, 0.05, 0.55],
    [8.7, 0.18, 0.08], [8.95, 0.05, 0.45],
    [9.9, 0.06, 0.25], [10.05, 0.1, 0.05], [10.25, 0.04, 0.4],
    [10.95, 0.75, 0.02],            // blackout
    [11.32, 0.04, 0.5],             // half-second "was that…?" flash (empty)
    [11.78, 0.07, 0.0],             // stutter after it returns
    [13.85, 0.06, 0.55],
  ],
  silhouetteFrom: 11.7, // revealed when light returns
  headTilt: [[13.3, 0], [14.15, -0.5, 'inOutCubic']],
  allLightsOff: 14.35, // every window in town cuts at once
  fadeToBlack: [14.55, 15.0],
};

// ---------- World layout ----------
const W = META.width, H = META.height;
const BOIL_RATE = 8;

const focalHouse = {
  x: 1078, base: 880, w: 300, h: 340, roofH: 190, roof: 'gable', lean: -10, peakShift: -8,
  wall: '#2d2a4b', roofCol: '#15132a', seed: 41,
  chimney: { x: 210, h: 40 }, door: { x: 40, w: 54, h: 100 },
  windows: [
    { x: 40, y: 290, w: 58, h: 74, curtain: true, decor: 'lamp' },
    { x: 200, y: 290, w: 58, h: 74, curtain: false, decor: 'frame' },
    { x: 120, y: 180, w: 58, h: 74, curtain: true, decor: 'plant' },
    { x: 200, y: 180, w: 58, h: 74, curtain: false, decor: 'chair' },
  ],
};

const neighbours = [
  { x: 770, base: 885, w: 230, h: 250, roofH: 120, roof: 'steep', lean: 8, wall: '#24364a', roofCol: '#101a26', seed: 12,
    chimney: { x: 30, h: 30 }, door: { x: 150, w: 46, h: 92 },
    windows: [{ x: 30, y: 200, w: 50, h: 64, decor: 'chair', curtain: true }, { x: 130, y: 200, w: 50, h: 64, decor: 'plant' }, { x: 30, y: 100, w: 50, h: 64, decor: 'frame' }] },
  { x: 1400, base: 882, w: 250, h: 280, roofH: 70, roof: 'mansard', lean: 6, wall: '#382b46', roofCol: '#1c1530', seed: 23,
    door: { x: 30, w: 46, h: 92 },
    windows: [{ x: 40, y: 220, w: 50, h: 66, curtain: true, decor: 'lamp' }, { x: 160, y: 220, w: 50, h: 66, decor: 'chair' }, { x: 160, y: 110, w: 50, h: 66, curtain: true }, { x: 40, y: 330, w: 40, h: 50, arch: true }] },
];

function makeRow(seed, x0, x1, base) {
  const r = rng(seed);
  const out = [];
  let x = x0;
  const decors = ['lamp', 'plant', 'chair', 'frame', null];
  while (x < x1) {
    const w = 150 + r() * 90, h = 160 + r() * 140;
    const cols = Math.max(1, Math.floor((w - 30) / 60)), rows = Math.max(1, Math.floor((h - 40) / 85));
    const windows = [];
    for (let c = 0; c < cols; c++) for (let rr = 0; rr < rows; rr++) {
      windows.push({ x: 22 + c * ((w - 44) / cols) + ((w - 44) / cols - 36) / 2, y: h - 30 - rr * 85, w: 36, h: 48,
        curtain: r() < 0.5, decor: decors[Math.floor(r() * decors.length)] });
    }
    out.push({ x: x + w / 2, base: base + (r() - 0.5) * 8, w, h, roofH: 50 + r() * 90,
      roof: ['gable', 'steep', 'mansard', 'flat'][Math.floor(r() * 4)], lean: (r() - 0.5) * 18,
      wall: PALETTE.walls[Math.floor(r() * PALETTE.walls.length)], roofCol: PALETTE.roofs[Math.floor(r() * PALETTE.roofs.length)],
      seed: Math.floor(r() * 1000), chimney: r() < 0.5 ? { x: 20 + r() * (w - 60), h: 20 + r() * 30 } : null, windows });
    x += w + 10 + r() * 30;
  }
  return out;
}
const midLeft = makeRow(5, -500, 640, 770);
const midRight = makeRow(9, 1330, 2500, 770);

const clouds = [
  { x: 300, y: 170, w: 520, h: 70, speed: 6 },
  { x: 1300, y: 110, w: 700, h: 80, speed: 4 },
  { x: 1900, y: 250, w: 420, h: 50, speed: 8 },
];

// ---------- Timing helpers ----------
export function targetLight(t) {
  if (t >= CONFIG.allLightsOff) return 0;
  let L = 1 + 0.03 * Math.sin(t * 50) * clamp((t - 4) / 4); // faint electrical shimmer, growing
  for (const [s, d, lvl] of CONFIG.flicker) if (t >= s && t < s + d) L = lvl + 0.04 * Math.sin(t * 90);
  return clamp(L);
}
const townLight = (t) => (t >= CONFIG.allLightsOff ? 0 : 1);

function camera(t) {
  const keys = CONFIG.camera.map(([tt, [x, y, z], e]) => [tt, [x, y, Math.log(z)], e]);
  const [x, y, lz] = track(keys, t);
  const zoom = Math.exp(lz);
  const hh = CONFIG.handheld / Math.sqrt(zoom);
  return { x: x + noise1(t * 0.35, 3) * hh * 4, y: y + noise1(t * 0.3, 8) * hh * 3, zoom };
}

// ---------- The figure ----------
function silhouette(ctx, r, level, t) {
  if (t < CONFIG.silhouetteFrom) return;
  // Tall, narrow, uneven shoulders, standing too close to the glass and
  // half-hidden by the curtain. Perfectly still except breathing — then the head tilts.
  const cx = r.x + r.w * 0.6 + noise1(t * 0.25, 2) * 0.3;
  const sh = r.y + 21 + Math.sin(t * 1.7) * 0.5; // shoulder line rises/falls with breath
  const tilt = track(CONFIG.headTilt, t);
  ctx.save();
  ctx.fillStyle = '#0d0811';
  ctx.beginPath();
  ctx.moveTo(cx - 3, sh - 8);
  ctx.bezierCurveTo(cx - 8, sh - 4, cx - 17, sh + 2, cx - 20, sh + 11); // left shoulder sags
  ctx.lineTo(cx - 23, r.y + r.h + 4);
  ctx.lineTo(cx + 22, r.y + r.h + 4);
  ctx.lineTo(cx + 19, sh + 5);
  ctx.bezierCurveTo(cx + 16, sh - 3, cx + 8, sh - 6, cx + 3, sh - 9);
  ctx.closePath();
  ctx.fill();
  // long thin neck, leaning slightly forward
  ctx.beginPath();
  ctx.moveTo(cx - 3, sh - 6); ctx.lineTo(cx - 2.2, sh - 21); ctx.lineTo(cx + 2.4, sh - 21); ctx.lineTo(cx + 3, sh - 6);
  ctx.fill();
  // head pivots at the top of the neck
  ctx.translate(cx + 0.2, sh - 20);
  ctx.rotate(tilt);
  ctx.beginPath();
  ctx.ellipse(0, -9, 8.4, 10.8, 0.06, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath(); // one ear / tuft, so it's not a perfect egg
  ctx.ellipse(7.5, -8, 2.6, 3.6, 0.3, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function targetCasing(ctx, boil, lw) {
  const { x, y, w, h } = CONFIG.target;
  const p = 7, arch = w / 2 + p;
  const pts = [[x - p, y + h], [x - p, y]];
  for (let k = 1; k < 14; k++) { const a = Math.PI - (k / 14) * Math.PI; pts.push([x + w / 2 + Math.cos(a) * (w / 2 + p), y - Math.sin(a) * arch]); }
  pts.push([x + w + p, y], [x + w + p, y + h]);
  inkPoly(ctx, pts, { fill: '#3b3557', ink: PALETTE.ink, lw, seed: 77, boil, amp: 0.7 });
  // keystone
  inkPoly(ctx, [[x + w / 2 - 6, y - arch - 4], [x + w / 2 + 6, y - arch - 4], [x + w / 2 + 4, y - arch + 9], [x + w / 2 - 4, y - arch + 9]],
    { fill: '#4a4468', ink: PALETTE.ink, lw, seed: 78, boil, amp: 0.5 });
}

// ---------- Render ----------
export function render(ctx, t) {
  const boil = boilFrame(t, BOIL_RATE);
  const cam = camera(t);
  const town = townLight(t);
  const lit = () => town;
  const lw = (z) => 2.2 / Math.pow(z, 0.55); // keep ink line weight readable at all zooms

  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = '#05040c';
  ctx.fillRect(0, 0, W, H);

  // Sky
  applyLayer(ctx, cam, 0.04, W, H);
  drawSky(ctx, W, H, t, { moon: { mx: 420, my: 210, mr: 62 } });
  applyLayer(ctx, cam, 0.1, W, H);
  drawClouds(ctx, t, clouds, boil);

  // Distant town
  applyLayer(ctx, cam, 0.25, W, H);
  ctx.globalAlpha = town ? 1 : 1;
  drawFarTown(ctx, W, 650, 77, t);
  if (!town) { ctx.fillStyle = 'rgba(5,4,12,0.85)'; ctx.fillRect(-W, 400, W * 3, 600); }
  drawFog(ctx, -800, 2800, 660, 50, t, 14, 0.12, 1);

  // Mid row
  let z = applyLayer(ctx, cam, 0.6, W, H);
  ctx.fillStyle = PALETTE.ground;
  ctx.fillRect(-1500, 760, 5000, 1200);
  [...midLeft, ...midRight].forEach((h) => drawHouse(ctx, h, t, boil, lit, null, lw(z)));
  drawFog(ctx, -1000, 3000, 790, 60, t, 22, 0.08, 2);

  // Focal plane
  z = applyLayer(ctx, cam, 1, W, H);
  // street & yard
  ctx.fillStyle = '#121022';
  ctx.fillRect(-1500, 865, 5000, 1500);
  inkPoly(ctx, [[560, 1400], [1360, 1400], [1160, 885], [960, 885]], { fill: PALETTE.road, ink: '#0b0a18', lw: lw(z), seed: 3, boil, amp: 2 });
  ctx.strokeStyle = 'rgba(140,130,200,0.07)';
  ctx.lineWidth = 1.2;
  for (let y = 900; y < 1100; y += 14) { ctx.beginPath(); ctx.moveTo(lerp(960, 560, (y - 885) / 515), y); ctx.lineTo(lerp(1160, 1360, (y - 885) / 515), y); ctx.stroke(); }

  neighbours.forEach((h) => drawHouse(ctx, h, t, boil, lit, null, lw(z)));
  drawHouse(ctx, focalHouse, t, boil, lit, null, lw(z));
  weathervane(ctx, 1057, 352, t, boil, lw(z));

  // THE window
  const L = targetLight(t);
  targetCasing(ctx, boil, lw(z));
  drawWindow(ctx, { ...CONFIG.target, seed: 999 }, L, boil, (c, r, lvl) => silhouette(c, r, lvl, t), lw(z));
  // the flicker throws light onto the roof around it
  glow(ctx, CONFIG.target.x + 26, CONFIG.target.y + 20, 160, 'rgba(255,150,70,0.5)', 0.35 * L);

  drawLamp(ctx, 1238, 905, 230, boil, 70, lw(z), town);
  drawFog(ctx, -600, 2600, 900, 55, t, 30, 0.12 * clamp(1.6 - z / 3), 3);

  // Foreground (flies past as we push in)
  z = applyLayer(ctx, cam, 1.55, W, H);
  drawTree(ctx, 120, 1180, 2.1, t, boil, 404);
  drawFence(ctx, -300, 2300, 1120, 120, boil, 88, lw(z));
  drawTree(ctx, 1880, 1250, 1.4, t + 3, boil, 515);

  // Post
  const black = clamp((t - CONFIG.fadeToBlack[0]) / (CONFIG.fadeToBlack[1] - CONFIG.fadeToBlack[0]));
  const cut = t >= CONFIG.allLightsOff ? 0.55 : 0;
  postFX(ctx, W, H, t, { vignette: 0.7 + 0.2 * clamp((t - 6) / 6), grain: 0.2, black: Math.max(black, cut) });
}

function weathervane(ctx, x, y, t, boil, lw) {
  const a = noise1(t * 0.4, 11) * 0.5;
  ctx.save();
  ctx.translate(x, y);
  inkPoly(ctx, [[-1.5, 0], [1.5, 0], [1.5, -50], [-1.5, -50]], { fill: '#0b0a18', seed: 5, boil, amp: 0.5 });
  ctx.translate(0, -44);
  ctx.scale(Math.cos(a), 1);
  // a crow-shaped vane
  inkPoly(ctx, [[-22, 0], [-6, -6], [2, -12], [8, -10], [14, -6], [22, -4], [12, 0], [4, 2], [-6, 4]], { fill: '#0b0a18', ink: '#0b0a18', lw, seed: 6, boil, amp: 0.6 });
  ctx.restore();
}
