// node render.mjs --audio assets/master.wav --output renders/final.mp4 [--from s --to s] [--still t --output f.png]
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';
import {readFile, mkdir, mkdtemp, rm} from 'node:fs/promises';
import {spawn} from 'node:child_process';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {serve} from './server.mjs';
const args = process.argv.slice(2), option = (k, d) => { const i = args.indexOf(k); return i < 0 ? d : args[i + 1]; };
const plan = JSON.parse(await readFile('plan.json', 'utf8'));
const output = option('--output', 'renders/technical-demo.mp4'), still = option('--still', null), audio = option('--audio', null);
const from = Number(option('--from', 0)), to = Number(option('--to', plan.duration)), partial = from > 0 || to < plan.duration;
const approvedSilent = !plan.demo && plan.audioRequired === false && typeof plan.audioExceptionReason === 'string' && plan.audioExceptionReason.trim();
if (still === null && !partial && !audio && !approvedSilent && !args.includes('--silent-demo')) throw new Error('Provide --audio master.wav; silent technical tests require --silent-demo (drafts: pass --from/--to).');
if (still === null && !partial && !plan.demo && args.includes('--silent-demo')) throw new Error('Silent-demo is only for technical samples.');
if (still === null && !partial && !plan.demo && plan.audioRequired && plan.sfxRequired !== false) {
  const report = JSON.parse(await readFile('evidence/audio-mix.json', 'utf8'));
  const digest = bytes => createHash('sha256').update(bytes).digest('hex');
  if (report.planSha256 !== digest(await readFile('plan.json'))) throw new Error('Audio mix is stale; remix for the current plan.');
  if (!report.cues?.length) throw new Error('Music-only report: SFX cues missing.');
  if (!audio || digest(await readFile(audio)) !== report.master.sha256) throw new Error('Use the verified BGM + SFX master.');
}
await mkdir(path.dirname(output), {recursive: true});
const {server, url} = await serve();
// SwiftShader keeps WebGL (Three.js layers) available in headless capture.
const browser = await chromium.launch({headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
let frames;
try {
  const page = await browser.newPage({viewport: {width: plan.width, height: plan.height}, deviceScaleFactor: 1});
  const failures = [];
  page.on('pageerror', e => failures.push(e.message));
  page.on('requestfailed', r => failures.push('failed ' + r.url()));
  page.on('response', r => { if (r.status() >= 400) failures.push(`${r.status()} ${r.url()}`); });
  await page.goto(url, {waitUntil: 'networkidle'});
  await page.evaluate(async () => { await window.__filmReady; await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode().catch(() => {}))); });
  if (failures.length) throw new Error(failures.join('\n'));
  if (still !== null) {
    await page.evaluate(t => window.seek(t), Number(still));
    await page.screenshot({path: output});
  } else {
    frames = await mkdtemp(path.join(tmpdir(), 'software-film-'));
    const first = Math.round(from * plan.fps), last = Math.round(to * plan.fps), t0 = Date.now();
    for (let f = first; f < last; f++) {
      await page.evaluate(t => window.seek(t), f / plan.fps);   // seek may await drivers (clicks, popovers)
      await page.screenshot({path: path.join(frames, String(f - first).padStart(6, '0') + '.jpg'), type: 'jpeg', quality: 95});
      if ((f - first) % 300 === 0) console.log(`frame ${f}/${last} · ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    if (failures.length) throw new Error(failures.join('\n'));
    const ff = ['-v', 'error', '-y', '-framerate', String(plan.fps), '-i', path.join(frames, '%06d.jpg')];
    if (audio) ff.push('-ss', String(from), '-i', audio, '-map', '0:v:0', '-map', '1:a:0', '-af', 'apad', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000');
    ff.push('-t', String(to - from), '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', output);
    await new Promise((res, rej) => { const p = spawn('ffmpeg', ff, {stdio: 'inherit'}); p.on('error', rej); p.on('close', c => c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}`))); });
  }
  console.log(output);
} finally {
  await browser?.close();
  await new Promise(resolve => server.close(resolve));
  if (frames) await rm(frames, {recursive: true, force: true});
}
