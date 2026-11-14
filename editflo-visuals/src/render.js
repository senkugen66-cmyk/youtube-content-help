// Renders the four screens (Participants A and B) to PNG and builds a contact-sheet preview.
// Usage (from editflo-visuals/src):  node render.js
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

const OUT = path.resolve(__dirname, "..");
const IDS = ["A_01", "A_02", "B_01", "B_02"];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1520, height: 3400 }, deviceScaleFactor: 1 });
  const problems = [];
  for (const id of IDS) {
    const url = "file://" + path.join(__dirname, "screen.html") + "#" + id;
    await page.goto("about:blank");
    await page.goto(url);
    await page.waitForFunction(() => document.body.dataset.ready === "1");
    await page.evaluate(() => document.fonts.ready);
    const info = await page.evaluate(() => ({
      overflow: document.body.dataset.overflow === "1",
      fonts: [...new Set([...document.querySelectorAll(".bubble,.ident,.time,.footer")].map(e => getComputedStyle(e).fontFamily))],
      interLoaded: document.fonts.check('46px "Inter"'),
    }));
    if (info.overflow) problems.push(`${id}: thread overflows header`);
    if (!info.interLoaded) problems.push(`${id}: Inter not available`);
    const dir = path.join(OUT, "PARTICIPANT_" + id[0]);
    fs.mkdirSync(dir, { recursive: true });
    await page.locator("#sheet").screenshot({ path: path.join(dir, id + ".png") });
    console.log("rendered", id);
  }

  // Contact sheet: all four side by side, for review only.
  const imgs = IDS.map(id => "file://" + path.join(OUT, "PARTICIPANT_" + id[0], id + ".png"));
  const html = `<html><body style="margin:0;background:#fff;font-family:Inter">
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:40px;padding:40px;width:2800px">
    ${imgs.map((src, i) => `<div><div style="font-size:30px;font-weight:600;margin:0 0 10px 6px;color:#333">${IDS[i]}</div><img src="${src}" style="width:100%"></div>`).join("")}
    </div></body></html>`;
  const sheetPath = path.join(OUT, "preview_A_B.html");
  fs.writeFileSync(sheetPath, html);
  const p2 = await browser.newPage({ viewport: { width: 2800, height: 1000 } });
  await p2.goto("file://" + sheetPath);
  await p2.waitForLoadState("load");
  await p2.screenshot({ path: path.join(OUT, "preview_A_B.png"), fullPage: true });
  fs.unlinkSync(sheetPath);
  await browser.close();
  console.log(problems.length ? "PROBLEMS:\n" + problems.join("\n") : "QA: no overflow, Inter loaded on all screens");
})();
