// Render cover images from cover/cover.html.
// Each cover is an element with data-cover="3x4" | "4x3" | "16x9" (any subset), sized in CSS px:
//   3x4 → 1080×1440, 4x3 → 1440×1080, 16x9 → 1920×1080. Exported at 2× device scale.
// node cover.mjs [--scale 2] [--out covers]
import {chromium} from 'playwright';
import {mkdir} from 'node:fs/promises';
import path from 'node:path';
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i < 0 ? d : args[i + 1]; };
const scale = Number(opt('--scale', 2)), out = opt('--out', 'covers');
const SIZES = {'3x4': [1080, 1440], '4x3': [1440, 1080], '16x9': [1920, 1080]};
await mkdir(out, {recursive: true});
const browser = await chromium.launch({headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
try {
  const page = await browser.newPage({viewport: {width: 2000, height: 1600}, deviceScaleFactor: scale});
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('requestfailed', r => errors.push('failed ' + r.url()));
  await page.goto('file://' + path.resolve('cover/cover.html'));
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode().catch(() => {}))); });
  const covers = await page.$$eval('[data-cover]', els => els.map(el => ({id: el.dataset.cover, w: el.offsetWidth, h: el.offsetHeight})));
  if (!covers.length) throw new Error('No [data-cover] elements in cover/cover.html');
  for (const c of covers) {
    const want = SIZES[c.id];
    if (!want) throw new Error(`Unknown cover ratio "${c.id}" (use 3x4, 4x3, 16x9)`);
    if (c.w !== want[0] || c.h !== want[1]) throw new Error(`${c.id} cover is ${c.w}×${c.h}; expected ${want[0]}×${want[1]}`);
    const file = path.join(out, `cover-${c.id}.png`);
    await page.locator(`[data-cover="${c.id}"]`).screenshot({path: file});
    console.log(file, `${want[0] * scale}×${want[1] * scale}`);
  }
  if (errors.length) throw new Error(errors.join('\n'));
} finally { await browser.close(); }
