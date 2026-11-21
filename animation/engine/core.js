// Core utilities: deterministic randomness, noise, easing, timelines, camera.
// Everything is a pure function of time `t` (seconds) so any frame can be
// rendered independently — required for frame-accurate export.

export function rng(seed) {
  // mulberry32
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function hash(n) {
  const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return s - Math.floor(s);
}

// Smooth 1D value noise in [-1, 1]
export function noise1(x, seed = 0) {
  const i = Math.floor(x);
  const f = x - i;
  const a = hash(i + seed * 101.3);
  const b = hash(i + 1 + seed * 101.3);
  const u = f * f * (3 - 2 * f);
  return (a + (b - a) * u) * 2 - 1;
}

export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const lerp = (a, b, t) => a + (b - a) * t;
export const invLerp = (a, b, v) => clamp((v - a) / (b - a));

export const ease = {
  linear: (t) => t,
  inOutSine: (t) => -(Math.cos(Math.PI * t) - 1) / 2,
  inOutCubic: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  inCubic: (t) => t * t * t,
  outCubic: (t) => 1 - Math.pow(1 - t, 3),
  inOutQuint: (t) => (t < 0.5 ? 16 * t ** 5 : 1 - Math.pow(-2 * t + 2, 5) / 2),
};

// Keyframe track: [[time, value], ...] with optional easing name per segment
// e.g. track([[0, 1], [4, 1.1, 'inOutSine'], [12, 5, 'inOutCubic']], t)
export function track(keys, t) {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [t1, v1, e = 'inOutSine'] = keys[i];
    const [t0, v0] = keys[i - 1];
    if (t <= t1) {
      const k = ease[e]((t - t0) / (t1 - t0));
      return Array.isArray(v0) ? v0.map((x, j) => lerp(x, v1[j], k)) : lerp(v0, v1, k);
    }
  }
  return keys[keys.length - 1][1];
}

// "Boil" frame: hand-drawn line jitter refreshes at a lower rate than the
// camera (animating "on threes" at 24fps = 8 drawings/sec).
export const boilFrame = (t, rate = 8) => Math.floor(t * rate);

// Camera with per-layer parallax.
// cam = { x, y, zoom } in world units of the reference frame (W x H).
// A layer with depth factor f (0 = infinitely far, 1 = focal plane, >1 = foreground)
// gets a proportionally scaled offset and zoom.
export function applyLayer(ctx, cam, f, W, H) {
  const ax = W / 2, ay = H / 2;
  const cx = ax + (cam.x - ax) * f;
  const cy = ay + (cam.y - ay) * f;
  const z = Math.max(0.05, 1 + (cam.zoom - 1) * f);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.translate(W / 2, H / 2);
  ctx.scale(z, z);
  ctx.translate(-cx, -cy);
  return z;
}
