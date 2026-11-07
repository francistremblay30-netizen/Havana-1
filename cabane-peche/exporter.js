// Assemble les feuilles SVG en un PDF (lettre paysage) et en PNG.
// Usage : node exporter.js   (après python3 generer_plans.py)
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

(async () => {
  const dir = __dirname;
  const svgs = fs.readdirSync(dir).filter((f) => /^feuille-\d\.svg$/.test(f)).sort();
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    @page { size: 11in 8.5in; margin: 0 }
    body { margin: 0 }
    .p { width: 11in; height: 8.5in; page-break-after: always; overflow: hidden }
    .p svg { width: 11in; height: 8.5in; display: block }
  </style></head><body>${svgs
    .map((f) => `<div class="p">${fs.readFileSync(path.join(dir, f), "utf8")}</div>`)
    .join("")}</body></html>`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2, viewport: { width: 1056, height: 816 } });
  await page.setContent(html);
  await page.pdf({ path: path.join(dir, "Plans_cabane_peche_8x10.pdf"), width: "11in", height: "8.5in", printBackground: true });
  const pages = await page.$$(".p");
  for (let i = 0; i < pages.length; i++) {
    await pages[i].screenshot({ path: path.join(dir, `feuille-${i + 1}.png`) });
  }
  await browser.close();
  console.log("PDF + PNG écrits");
})();
