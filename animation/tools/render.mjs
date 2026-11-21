// Frame-accurate renderer. Serves the project folder, drives player.html with Playwright.
//   node tools/render.mjs stills ep00-lit-town 0.5 4 9 12.5      -> out/<ep>/stills/*.png
//   node tools/render.mjs frames ep00-lit-town [--fps 24]          -> out/<ep>/frames/%05d.png
import { createRequire } from 'node:module';
// Uses the globally installed Playwright (require() honours NODE_PATH).
const { chromium } = createRequire(import.meta.url)('playwright');
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [mode, ep, ...rest] = process.argv.slice(2);
if (!mode || !ep) { console.error('usage: render.mjs stills|frames <episode> [times...]'); process.exit(1); }

const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const port = server.address().port;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('pageerror', (e) => console.error('page error:', e));
await page.goto(`http://localhost:${port}/player.html?ep=${ep}&capture=1`);
await page.waitForFunction(() => window.ready);
const meta = await page.evaluate(() => window.META);
const canvas = await page.$('#c');

async function grab(t, file) {
  await page.evaluate((t) => window.renderAt(t), t);
  const data = await page.evaluate(() => document.getElementById('c').toDataURL('image/png'));
  fs.writeFileSync(file, Buffer.from(data.split(',')[1], 'base64'));
}

if (mode === 'stills') {
  const dir = path.join(root, 'out', ep, 'stills');
  fs.mkdirSync(dir, { recursive: true });
  for (const s of rest) { const t = +s; await grab(t, path.join(dir, `t${t.toFixed(2).padStart(5, '0')}.png`)); console.log('still', t); }
} else {
  const fi = rest.indexOf('--fps');
  const fps = fi >= 0 ? +rest[fi + 1] : meta.fps;
  const dir = path.join(root, 'out', ep, 'frames');
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  const n = Math.round(meta.duration * fps);
  for (let i = 0; i < n; i++) {
    await grab(i / fps, path.join(dir, String(i).padStart(5, '0') + '.png'));
    if (i % 24 === 0) console.log(`frame ${i}/${n}`);
  }
}
await browser.close();
server.close();
