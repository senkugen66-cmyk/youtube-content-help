// Ripening — a 10-second watercolor film. Uses the Lemo-Opuscar watercolor stroke engine (engine.js).
// Everything is a pure function of t; every stroke is built once in init under a fixed seed.
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
window.DUR = 10.2;

// ---------- timeline (single source of truth; exported as EV for the mix) ----------
const TL = {
  stem: [0.3, 1.5],            // branch brushed in
  leaves0: 0.8, leafStep: 0.32, leafDur: 0.75,
  cherry0: 1.9, cherryStep: 0.26, cherryDur: 0.7,
  ripen0: 3.3, ripenStep: 0.42, ripenDur: 1.7,
  vo: [1.0, 5.3],
  sub: [0.95, 5.95],
  notes: { genus: [4.8, 7.45], ripe: [5.3, 7.6], size: [5.6, 7.6] },
  mist: [7.2, 8.4],
  title: [7.8, 10.2],
};

const LEAF = '#6f8f4e', LEAF2 = '#4e6e3c', SHADE = '#3a5530', BARK = '#7a6544', BARK2 = '#4f3f2a';
const C_GREEN = '#8fae5a', C_GSH = '#5b7a3a', C_YEL = '#dcae3f', C_RED = '#c8442a', C_RSH = '#7e2418';

let PAPER_IMG, STEM = [], NODES = [], LEAVES = [], CHERRIES = [], HERO, CAM_END;

function stemPt(u) { // centre-line of the branch, u ∈ [0,1]
  const P = STEM_PTS, m = (P.length - 1) * clamp(u), k = Math.min(P.length - 2, Math.floor(m)), f = m - k;
  return [lerp(P[k][0], P[k + 1][0], f), lerp(P[k][1], P[k + 1][1], f)];
}
let STEM_PTS;

function leaf(x, y, ang, len, w) {
  const tip = [x + Math.cos(ang) * len, y + Math.sin(ang) * len], bend = rnd(-.12, .12) * len;
  const mid = qcurve(x, y, tip[0], tip[1], bend, 14);
  const S = [];
  const body = mk(mid, w, LEAF, { prof: 'leaf', nb: 5, a: .86, rough: .16 });
  S.push(body);
  // second, darker glaze on one half: the leaf folds along its midrib
  const side = rnd() < .5 ? 1 : -1;
  const half = mid.map((p, i) => [p[0] + body.nx[i] * body.ws[i] * .2 * side, p[1] + body.ny[i] * body.ws[i] * .2 * side]);
  S.push(mk(half, w * .5, LEAF2, { prof: 'leaf', nb: 3, a: .62, rough: .25 }));
  S.push(edgeOf(body, -side, 2.4, SHADE, .55));
  S.push(mk(mid.slice(0, 13), 2.6, SHADE, { prof: 'tip', nb: 0, a: .55, rough: .1 }));   // midrib
  return S;
}

function cherry(cx, cy, r, ang, sx, sy) {
  // a round berry from three crossing wide dabs per layer; yellow and red glazes on top ripen it
  const dabs = (rad, w, col, o, rot = 0) => [0, 1, 2].map(k => {
    const a = ang + rot + k * 1.047, c = Math.cos(a), s = Math.sin(a);
    return mk(qcurve(cx - rad * c, cy - rad * s, cx + rad * c, cy + rad * s, rad * .12 * (k - 1), 8), w, col, { ...o, nb: k ? 0 : o.nb });
  });
  const arc = (r0, a0, a1, n = 10) => { const o = []; for (let i = 0; i <= n; i++) { const a = lerp(a0, a1, i / n); o.push([cx + Math.cos(a) * r0, cy + Math.sin(a) * r0]); } return o; };
  const body = dabs(r * .9, r * 1.75, C_GREEN, { prof: 'leaf', nb: 3, a: .62, rough: .12 });
  const shadow = mk(arc(r * .6, -.4, 2.1), r * .5, C_GSH, { prof: 'leaf', nb: 2, a: .6, rough: .25 });
  const yel = mk(qcurve(cx - r * .85, cy - r * .2, cx + r * .85, cy + r * .25, r * .3, 8), r * 1.8, C_YEL, { prof: 'leaf', nb: 3, a: .6, rough: .2 });
  const red = dabs(r * .95, r * 1.85, C_RED, { prof: 'leaf', nb: 4, a: .62, rough: .12 }, .5);
  const rsh = mk(arc(r * .6, -.3, 2.0), r * .5, C_RSH, { prof: 'leaf', nb: 2, a: .6, rough: .25 });
  const hi = mk(arc(r * .45, 3.6, 4.4, 5), r * .26, PAPER, { prof: 'leaf', nb: 0, a: .6, rough: .3 });  // light = unpainted paper
  // a short stalk toward the branch
  const da = Math.atan2(sy - cy, sx - cx);
  const stalk = mk(qcurve(cx + Math.cos(da) * r * .7, cy + Math.sin(da) * r * .7, cx + Math.cos(da) * r * 1.35, cy + Math.sin(da) * r * 1.35, r * .1, 5), r * .22, BARK, { prof: 'even', nb: 0, a: .8, rough: .2 });
  return { cx, cy, r, body, shadow, yel, red, rsh, hi, stalk };
}

function build() {
  // the branch: from lower left, rising to the right with a gentle sag
  STEM_PTS = qcurve(40, 900, 1700, 300, -70, 60);
  const st = mk(STEM_PTS, 19, BARK, { prof: 'trunk', nb: 6, a: .9, rough: .2 });
  STEM = [st, edgeOf(st, 1, 3, BARK2, .7)];
  // nodes along the branch: opposite leaf pairs + a cherry cluster in each axil
  const US = [.17, .33, .49, .64, .79, .92];
  US.forEach((u, i) => {
    const [x, y] = stemPt(u), [x2, y2] = stemPt(u + .01), da = Math.atan2(y2 - y, x2 - x);
    const scale = 1 - i * .07;
    const node = { u, x, y, i, leaves: [], cherries: [] };
    for (const side of [-1, 1]) {
      const ang = da + side * rnd(1.0, 1.35) + rnd(-.1, .1);
      node.leaves.push(leaf(x, y, ang, rnd(230, 300) * scale, rnd(84, 104) * scale));
    }
    if (i < 5) {
      const n = i === 2 ? 7 : Math.round(rnd(4, 6));
      for (let k = 0; k < n; k++) {
        const along = rnd(-34, 34) * scale, off = (k % 2 ? 1 : -1) * rnd(10, 30) * scale;
        const px = x + Math.cos(da) * along - Math.sin(da) * off, py = y + Math.sin(da) * along + Math.cos(da) * off;
        node.cherries.push(cherry(px, py, rnd(19, 24) * scale, rnd(0, Math.PI), x, y));
      }
      node.cherries.sort((a, b) => a.cy - b.cy);
    }
    NODES.push(node);
  });
  // the hero: a front cherry of the middle cluster, slightly larger
  const hn = NODES[2];
  HERO = cherry(hn.x + 14, hn.y + 34, 27, .6, hn.x - 4, hn.y - 6);
  hn.cherries.push(HERO);
  CAM_END = { x: HERO.cx, y: HERO.cy, s: 2.4 };
}

// ---------- camera ----------
function cam(t) {
  // a slow lean-in while the branch ripens, then a close push onto the one cherry as the page mists away
  const p = eio(seg(t, 0, 9.2)), p1 = eio(seg(t, 0, 7.2)), p2 = eio(seg(t, 7.1, 9.9));
  const fx = lerp(900, CAM_END.x, p), fy = lerp(600, CAM_END.y, p), s = lerp(1, 1.2, p1) * lerp(1, CAM_END.s, p2);
  const cx = 960, cy = lerp(540, 430, p);
  return { fx, fy, s, cx, cy, X: x => (x - fx) * s + cx, Y: y => (y - fy) * s + cy };
}

// ---------- drawing ----------
function drawCherry(c, t, rip0, am = 1) {
  const pb = seg(t, c.t0, c.t0 + TL.cherryDur);
  if (pb <= 0) return;
  const ry = seg(t, rip0, rip0 + TL.ripenDur * .55), rr = seg(t, rip0 + TL.ripenDur * .3, rip0 + TL.ripenDur);
  const fadeG = 1 - .9 * ss(rr);
  drawS(ctx, c.stalk, seg(pb, 0, .4), null, am);
  drawList(ctx, c.body, pb, null, am * fadeG);
  drawS(ctx, c.shadow, seg(pb, .6, 1), null, am * (1 - ss(rr)));
  if (ry > 0) drawS(ctx, c.yel, ry, null, am * (1 - .7 * ss(rr)));
  if (rr > 0) { drawList(ctx, c.red, rr, null, am); drawS(ctx, c.rsh, seg(rr, .5, 1), null, am); }
  drawS(ctx, c.hi, seg(pb, .8, 1), null, am);
  // calyx: the dried flower at the cherry's tip — a tiny ink star
  if (pb >= 1) {
    ctx.save(); ctx.translate(c.cx + c.r * .45, c.cy - c.r * .35);
    ctx.strokeStyle = rgba(INK2, .55 * am); ctx.lineWidth = 1.4;
    for (let k = 0; k < 5; k++) { const a = k * 1.2566 + .3; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.cos(a) * c.r * .16, Math.sin(a) * c.r * .16); ctx.stroke(); }
    ctx.restore();
  }
}

function hand(txt, x, y, p, o = {}) {
  if (p <= 0) return;
  ctx.save(); ctx.font = o.font || `${o.w || 600} ${o.size || 40}px Caveat`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  const w = ctx.measureText(txt).width;
  ctx.beginPath(); ctx.rect(x - 6, y - 50, (w + 12) * eo(p), 100); ctx.clip();
  ctx.shadowColor = rgba(PAPER, .95); ctx.shadowBlur = 12; ctx.fillStyle = rgba(o.col || INK, o.a ?? .9);
  ctx.fillText(txt, x, y); ctx.fillText(txt, x, y);
  ctx.restore();
  return w;
}
function leader(x0, y0, x1, y1, p, bend = 20, a = .75) {
  if (p <= 0) return;
  const pts = qcurve(x0, y0, x1, y1, bend, 16), m = Math.max(1, Math.round(16 * clamp(p)));
  ctx.beginPath(); for (let i = 0; i <= m; i++) i ? ctx.lineTo(pts[i][0], pts[i][1]) : ctx.moveTo(pts[i][0], pts[i][1]);
  ctx.strokeStyle = rgba(INK, a); ctx.lineWidth = 1.7; ctx.lineCap = 'round'; ctx.stroke();
  if (p >= 1) { ctx.beginPath(); ctx.arc(x1, y1, 3, 0, 7); ctx.fillStyle = rgba(INK, a); ctx.fill(); }
}
const fade2 = (t, a, b, fi = .4, fo = .45) => ss(seg(t, a, a + fi)) * (1 - ss(seg(t, b - fo, b)));

// note layout in screen space, anchored to world points through the camera
function noteGeom(t) {
  const C = cam(t), hn = NODES[1];
  return {
    genus: { lx: 110, ly: 120, txt: 'Coffea arabica' },
    ripe: { ax: C.X(HERO.cx + HERO.r * .8), ay: C.Y(HERO.cy + HERO.r * .6), lx: C.X(HERO.cx) + 330, ly: C.Y(HERO.cy) + 300, txt: 'ripe cherry' },
    size: { lx: C.X(HERO.cx) + 332, ly: C.Y(HERO.cy) + 346, txt: '≈ 15 mm' },
  };
}
function drawNotes(t) {
  const G = noteGeom(t), N = TL.notes;
  for (const k of ['genus', 'ripe']) {
    const g = G[k], [t0, t1] = N[k], f = fade2(t, t0, t1, .01); if (t < t0 || f <= 0) continue;
    ctx.globalAlpha = f;
    if (k === 'ripe') leader(g.lx - 10, g.ly - 22, g.ax, g.ay, seg(t, t0, t0 + .55), -30);
    hand(g.txt, g.lx, g.ly, seg(t, t0 + (k === 'ripe' ? .25 : 0), t0 + (k === 'ripe' ? 1.0 : .9)), { size: k === 'genus' ? 58 : 44 });
    ctx.globalAlpha = 1;
  }
  { const g = G.size, [t0, t1] = N.size, f = fade2(t, t0, t1, .01); if (t >= t0 && f > 0) {
    ctx.globalAlpha = f; ctx.save(); ctx.font = '400 20px "IBM Plex Mono"'; ctx.letterSpacing = '3px';
    const w = ctx.measureText(g.txt).width; ctx.beginPath(); ctx.rect(g.lx - 4, g.ly - 20, (w + 10) * eo(seg(t, t0, t0 + .5)), 40); ctx.clip();
    ctx.textBaseline = 'middle'; ctx.fillStyle = rgba(INK2, .8); ctx.fillText(g.txt, g.lx, g.ly); ctx.restore(); ctx.globalAlpha = 1;
  } }
}

// mist: paper rises from the bottom with a wavy edge and washes the page back to blank
function mistY(t) { return lerp(1180, -160, eio(seg(t, TL.mist[0], TL.mist[1]))); }
function drawMist(t) {
  if (t < TL.mist[0]) return;
  const Y0 = mistY(t);
  const band = (yy, a, amp, ph) => {
    ctx.save(); ctx.beginPath(); ctx.moveTo(0, H + 10);
    for (let x = 0; x <= W; x += 24) ctx.lineTo(x, yy + amp * (Math.sin(x * .006 + ph) * .6 + Math.sin(x * .017 + ph * 2.3) * .4) + 40 * (fbm(x * .004 + ph) - .5));
    ctx.lineTo(W, H + 10); ctx.closePath(); ctx.clip(); ctx.globalAlpha = a; ctx.drawImage(PAPER_IMG, 0, 0); ctx.restore();
  };
  band(Y0 - 170, .35, 26, 1.7); band(Y0 - 80, .6, 30, .4); band(Y0, 1, 34, 2.9);
}

function drawSub(t) {
  const [t0, t1] = TL.sub, a = fade2(t, t0, t1, .3, .35); if (a <= 0) return;
  ctx.save(); ctx.font = 'italic 400 38px "Cormorant Garamond"'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.shadowColor = rgba(PAPER, .98); ctx.shadowBlur = 14; ctx.fillStyle = rgba(INK, .8 * a);
  for (const [txt, y] of SUB_LINES) { ctx.fillText(txt, W / 2, y); ctx.fillText(txt, W / 2, y); }
  ctx.restore();
}
const SUB_LINES = [["Before it’s a cup, coffee is a cherry,", 972], ['ripening slowly on the branch.', 1018]];

const TITLE = 'It begins here.';
function titleGeom(t) { const C = cam(t); return { x: W / 2, y: C.Y(HERO.cy) + HERO.r * C.s + 150 }; }
function drawTitle(t) {
  const [t0] = TL.title; if (t < t0) return;
  const g = titleGeom(t), p = eo(seg(t, t0, t0 + 1.1));
  ctx.save(); ctx.font = 'italic 500 64px "Cormorant Garamond"'; ctx.textBaseline = 'middle';
  const w = ctx.measureText(TITLE).width, x0 = g.x - w / 2;
  ctx.beginPath(); ctx.rect(x0 - 10, g.y - 60, (w + 20) * p, 120); ctx.clip();
  ctx.fillStyle = rgba(INK, .86); ctx.fillText(TITLE, x0, g.y); ctx.restore();
  // a short pen rule under the title
  const pr = seg(t, t0 + .6, t0 + 1.4); if (pr > 0) { ctx.save(); ctx.translate(g.x - 60, g.y + 52); drawS(ctx, RULE, pr); ctx.restore(); }
}
let RULE;

function render(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.drawImage(PAPER_IMG, 0, 0);
  const C = cam(t), sway = t > 3.2 ? .004 * (Math.sin(1.15 * t) + .4 * Math.sin(2.7 * t + 1)) * ss(seg(t, 3.2, 4.2)) : 0;
  ctx.setTransform(C.s, 0, C.s * sway, C.s, C.cx - C.fx * C.s - C.s * sway * C.fy, C.cy - C.fy * C.s);
  // branch
  drawList(ctx, STEM, seg(t, TL.stem[0], TL.stem[1]));
  // leaves, node by node from the base outward (structure before detail)
  for (const n of NODES) {
    const t0 = TL.leaves0 + n.i * TL.leafStep;
    n.leaves.forEach((L, j) => drawList(ctx, L, seg(t, t0 + j * .14, t0 + j * .14 + TL.leafDur)));
  }
  // cherries: painted green, then glazed yellow and red, cluster by cluster
  for (const n of NODES) {
    n.cherries.forEach((c, k) => {
      c.t0 = TL.cherry0 + n.i * TL.cherryStep + k * .05;
      const rip0 = c === HERO ? 4.5 : TL.ripen0 + n.i * TL.ripenStep + hash(n.i * 13 + k) * .5;
      drawCherry(c, t, rip0);
    });
  }
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  drawNotes(t);
  drawSub(t);
  drawMist(t);
  // the hero cherry stays when the page washes away
  if (t >= TL.mist[0]) {
    ctx.setTransform(C.s, 0, C.s * sway, C.s, C.cx - C.fx * C.s - C.s * sway * C.fy, C.cy - C.fy * C.s);
    drawCherry(HERO, t, 4.5);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
  }
  drawTitle(t);
}
window.render = render;

// every on-screen text, for readcheck
window.TEXTS = t => {
  const out = [], G = noteGeom(t);
  for (const k of ['genus', 'ripe', 'size']) {
    const [t0, t1] = TL.notes[k]; if (t >= t0 && t < t1) out.push({ id: k, text: G[k].txt, x0: G[k].lx, y0: G[k].ly - 25, x1: G[k].lx + 260, y1: G[k].ly + 25 });
  }
  if (t >= TL.title[0]) { const g = titleGeom(t); out.push({ id: 'title', text: TITLE, x0: g.x - 200, y0: g.y - 40, x1: g.x + 200, y1: g.y + 40 }); }
  return out;
};

window.EV = (() => {
  const ev = [{ t: TL.stem[0], type: 'brush', d: TL.stem[1] - TL.stem[0] }];
  for (let i = 0; i < 6; i++) ev.push({ t: TL.leaves0 + i * TL.leafStep, type: 'brush', d: TL.leafDur + .14 });
  for (let i = 0; i < 5; i++) ev.push({ t: TL.cherry0 + i * TL.cherryStep, type: 'dab', node: i });
  for (let i = 0; i < 5; i++) ev.push({ t: TL.ripen0 + i * TL.ripenStep + .5, type: 'ripen', node: i });
  ev.push({ t: 4.5 + TL.ripenDur * .3, type: 'hero' });
  for (const k of ['genus', 'ripe']) ev.push({ t: TL.notes[k][0] + .25, type: 'pen', d: .75 });
  ev.push({ t: TL.mist[0], type: 'mist', d: TL.mist[1] - TL.mist[0] });
  ev.push({ t: TL.title[0], type: 'title' });
  ev.push({ t: TL.vo[0], type: 'vo', id: 'v01' });
  return ev;
})();

(async () => {
  PAPER_IMG = new Image(); PAPER_IMG.src = 'paper.jpg'; await PAPER_IMG.decode();
  await Promise.all(['600 48px Caveat', 'italic 400 38px "Cormorant Garamond"', 'italic 500 64px "Cormorant Garamond"', '400 20px "IBM Plex Mono"'].map(f => document.fonts.load(f, 'Coffea ≈15mm')));
  withSeed(4041, build);
  RULE = withSeed(77, () => mk(qcurve(0, 0, 120, 0, -3, 10), 3.2, INK2, { prof: 'even', nb: 2, a: .7, rough: .3 }));
  window.READY = true;
})();
