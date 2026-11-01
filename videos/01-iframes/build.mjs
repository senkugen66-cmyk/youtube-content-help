// Builds episode.html (self-contained: fonts and mascot SVGs inlined) and,
// with --render, renders every frame through Chromium into episode.mp4.
//
//   node videos/01-iframes/build.mjs            # build the HTML only
//   node videos/01-iframes/build.mjs --render   # build + render MP4 (needs ffmpeg + playwright)
import { readFileSync, writeFileSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const here = dirname(fileURLToPath(import.meta.url));
const brand = join(here, '..', '..', 'brand');
const poses = ['neutral', 'point', 'think', 'hype', 'oops', 'deadpan'];
const svgs = Object.fromEntries(poses.map(p => [p, readFileSync(join(brand, 'mascot', `meowdude-${p}.svg`), 'utf8').trim()]));
const font = f => readFileSync(join(here, 'fonts', f)).toString('base64');

const out = readFileSync(join(here, 'episode.src.html'), 'utf8')
  .replace('__SVGS__', () => JSON.stringify(svgs))
  .replace('__FONT_ARCHIVO__', () => font('Archivo-latin.woff2'))
  .replace('__FONT_SHANTELL__', () => font('ShantellSans-latin.woff2'));
writeFileSync(join(here, 'episode.html'), out);
console.log('wrote episode.html', (out.length / 1024).toFixed(0), 'KB');

if (process.argv.includes('--render')) {
  const require = createRequire(import.meta.url);
  const { chromium } = require('playwright');
  const TOTAL = 750;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + join(here, 'episode.html') + '?render');
  await page.evaluate(() => document.fonts.ready);
  // Show only the stage, unscaled, at the top-left of the viewport.
  await page.addStyleTag({ content: 'body{padding:0!important;margin:0} .head,.bar{display:none!important} .wrap{max-width:none} .viewport{width:1920px;height:1080px;border-radius:0} #stage{transform:none!important}' });
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', join(here, 'episode.mp4')],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const stage = await page.$('#stage');
  for (let f = 0; f < TOTAL; f++) {
    await page.evaluate(n => window.render(n), f);
    const buf = await stage.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log('frame', f);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('wrote episode.mp4');
}
