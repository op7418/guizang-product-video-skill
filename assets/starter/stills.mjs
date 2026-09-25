// Batch stills in one browser session: node stills.mjs evidence/stills 1.2 4.5 9.0
import {chromium} from 'playwright';
import {readFile, mkdir} from 'node:fs/promises';
import {serve} from './server.mjs';
const [out = 'evidence/stills', ...times] = process.argv.slice(2);
const plan = JSON.parse(await readFile('plan.json', 'utf8'));
await mkdir(out, {recursive: true});
const {server, url} = await serve();
const browser = await chromium.launch({headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
try {
  const page = await browser.newPage({viewport: {width: plan.width, height: plan.height}});
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror ' + e.message));
  page.on('response', r => { if (r.status() >= 400) errors.push(r.status() + ' ' + r.url()); });
  await page.goto(url, {waitUntil: 'networkidle'});
  await page.evaluate(() => window.__filmReady);
  for (const t of times) { await page.evaluate(x => window.seek(x), Number(t)); await page.screenshot({path: `${out}/t${Number(t).toFixed(2).padStart(6, '0')}.png`}); }
  console.log(JSON.stringify({stills: times.length, errors, api: await page.evaluate(() => [...new Set(window.__filmApiLog || [])])}));
} finally { await browser.close(); server.close(); }
