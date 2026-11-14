// Renders report.html to the final PDF with continuous page numbers, then fills the contents page.
const { chromium } = require('playwright'); const path = require('path'); const { execSync } = require('child_process'); const fs = require('fs');
const OUT = path.resolve('../final/25120989_EHT_FinalProject.pdf');
const FF = `<style>@font-face{font-family:'EF Inter';src:url(data:font/ttf;base64,${fs.readFileSync('fonts/Inter-400.ttf').toString('base64')}) format('truetype');}</style>`;
const footer = FF + `<style>html,body{margin:0!important;padding:0!important}</style><div style="width:100%;height:12.6mm;margin:0;background:#FBF9F5;-webkit-print-color-adjust:exact;font-family:'JetBrains Mono';font-size:6.6pt;letter-spacing:.06em;color:#8A8490;display:flex;align-items:center;justify-content:space-between;padding:0 19mm;box-sizing:border-box;border:0">
  <span>25120989 · EditFlo · Entrepreneurship Final Project</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`;
const header = `<style>html,body{margin:0!important;padding:0!important}</style><div style="width:100%;height:10.3mm;margin:0;background:#FBF9F5;-webkit-print-color-adjust:exact"></div>`;
async function render(page, file) {
  await page.pdf({ path: file, format: 'A4', printBackground: true, displayHeaderFooter: true, headerTemplate: header, footerTemplate: footer, margin: { top: '15mm', bottom: '17mm', left: '0', right: '0' }, preferCSSPageSize: false });
}
(async () => {
  const b = await chromium.launch(); const page = await b.newPage();
  page.on('pageerror', (e) => console.log('ERR', e.message));
  await page.goto('file://' + path.resolve('report.html')); await page.evaluate(() => document.fonts.ready); await page.waitForTimeout(500);
  // pass 1: mark each TOC target with a unique token, find its page in the PDF
  const ids = await page.evaluate(() => [...document.querySelectorAll('[data-toc]')].map((e) => e.dataset.toc));
  await page.evaluate((ids) => ids.forEach((id) => { const el = document.getElementById(id); const m = document.createElement('span'); m.textContent = 'TOCMARK' + id.toUpperCase() + 'X'; m.className = 'tocmark'; m.style.cssText = 'font-size:1px;color:#FBF9F5;position:absolute'; el.prepend(m); }), ids);
  await render(page, '/tmp/editflo_pass1.pdf');
  const n = parseInt(execSync('pdfinfo /tmp/editflo_pass1.pdf').toString().match(/Pages:\s+(\d+)/)[1]);
  const found = {};
  for (let p = 1; p <= n; p++) { const t = execSync(`pdftotext -f ${p} -l ${p} /tmp/editflo_pass1.pdf -`).toString(); for (const id of ids) if (!found[id] && t.includes('TOCMARK' + id.toUpperCase() + 'X')) found[id] = p; }
  console.log('pages', n, JSON.stringify(found));
  await page.evaluate((found) => { document.querySelectorAll('.tocmark').forEach((m) => m.remove()); document.querySelectorAll('[data-toc]').forEach((td) => td.textContent = found[td.dataset.toc] || '?'); }, found);
  await render(page, OUT);
  await b.close();
  console.log('wrote', OUT, execSync(`pdfinfo "${OUT}" | grep Pages`).toString().trim());
})();
