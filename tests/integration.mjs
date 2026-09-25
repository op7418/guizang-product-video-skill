// Optional real build/browser regression. Uses installed dependencies; no downloads.
// node tests/integration.mjs --modules /absolute/video/node_modules [--python python3]
import assert from 'node:assert/strict';
import {mkdtemp, mkdir, writeFile, symlink, rm, readdir, readFile} from 'node:fs/promises';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {statSync} from 'node:fs';
const args = process.argv.slice(2);
const option = (name, fallback) => { const i = args.indexOf(name); return i < 0 ? fallback : args[i + 1]; };
const modules = option('--modules');
if (!modules) throw Error('Pass --modules pointing to an installed starter node_modules; this test never installs packages.');
const dependencies = createRequire(path.join(path.resolve(modules), 'integration.cjs'));
const packages = ['esbuild', 'react', 'react-dom', 'playwright', 'gsap', 'three'];
// Some packages (three) do not export package.json; fall back to the node_modules search path.
const locate = name => { try { return path.dirname(dependencies.resolve(name + '/package.json')); } catch (e) {
  for (const d of dependencies.resolve.paths(name) || []) { const dir = path.join(d, name); try { if (statSync(path.join(dir, 'package.json')).isFile()) return dir; } catch {} } throw e; } };
const paths = Object.fromEntries(packages.map(name => [name, locate(name)]));
const {chromium} = dependencies('playwright');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const workspace = await mkdtemp(path.join(tmpdir(), 'software-video-integration-'));
let browser, server;
try {
  const repo = path.join(workspace, 'product'), video = path.join(workspace, 'video');
  await mkdir(path.join(repo, 'src/components'), {recursive: true});
  await mkdir(path.join(repo, 'node_modules/fake-icons'), {recursive: true});
  await writeFile(path.join(repo, 'node_modules/fake-icons/package.json'), JSON.stringify({name: 'fake-icons', main: 'index.js'}));
  await writeFile(path.join(repo, 'node_modules/fake-icons/index.js'), 'exports.label="Repository-only dependency";');
  // A product component with its own CSS asset, a repo-only dependency and a data-fetching effect.
  await writeFile(path.join(repo, 'src/components/Panel.jsx'), `import React, {useEffect, useState} from 'react';
import {label} from 'fake-icons'; import './panel.css';
export function Panel() {
  const [data, setData] = useState(null);
  useEffect(() => { fetch('/api/panel').then(r => r.json()).then(setData); }, []);
  return <div className="panel"><h2>{label}</h2><p className="fetched">{data ? data.title : 'loading'}</p></div>;
}`);
  await writeFile(path.join(repo, 'src/components/panel.css'), `.panel{background-image:url('./mark.svg');padding:40px}.panel h2{font-size:31px}`);
  await writeFile(path.join(repo, 'src/components/mark.svg'), '<svg xmlns="http://www.w3.org/2000/svg" width="4" height="4"><rect width="4" height="4" fill="red"/></svg>');
  execFileSync(option('--python', 'python3'), [path.join(root, 'scripts/init_project.py'), '--output', video, '--style', 'repo', '--repo', repo], {stdio: 'pipe'});
  await mkdir(path.join(video, 'node_modules'));
  for (const name of packages) await symlink(paths[name], path.join(video, 'node_modules', name), process.platform === 'win32' ? 'junction' : 'dir');
  await writeFile(path.join(video, 'integration.config.mjs'), 'export default ' + JSON.stringify({repoDir: repo, aliases: {'@': path.join(repo, 'src')}, external: [], loaders: {}, define: {}}));
  await writeFile(path.join(video, 'src/fixtures/api.js'), `export const API_PREFIXES = ['/api/'];\nexport const API_FIXTURES = {'/api/panel': {title: 'Fixture data'}};\n`);
  await writeFile(path.join(video, 'src/shots/index.js'), `import React from 'react';
import * as THREE from 'three';
import {Panel} from '@/components/Panel.jsx';
import {shot, onRender} from '../engine.js';
const sec = id => document.querySelector('section[data-shot="' + id + '"]');
const Title = () => <div className="title">title</div>;
const Feature = () => <div className="wrap"><Panel /><canvas className="gl" width="64" height="64" /></div>;
export const SHOT_VIEWS = {intro: Title, component: Feature, close: Title};
const show = id => tl => tl.set(sec(id), {opacity: 1}, shot(id).start);
export const SHOT_BUILDERS = {intro: show('intro'), close: show('close'), component: tl => {
  const s = shot('component');
  tl.set(sec('component'), {opacity: 1}, s.start);
  tl.fromTo(sec('component').querySelector('.wrap'), {opacity: 0}, {opacity: 1, duration: 0.5, ease: 'none'}, s.start + 0.5);
  const canvas = sec('component').querySelector('.gl');
  const renderer = new THREE.WebGLRenderer({canvas, preserveDrawingBuffer: true});
  onRender('component', local => { renderer.setClearColor(local > 1 ? 0xff0000 : 0x0000ff); renderer.clear(); });
}};
`);
  execFileSync(process.execPath, ['build.mjs'], {cwd: video, stdio: 'pipe'});
  const graph = JSON.parse(await readFile(path.join(video, 'evidence/component-imports.json'), 'utf8'));
  assert.ok(Object.keys(graph.inputs).some(k => k.includes('fake-icons/index.js')), 'repository-only dependency must be bundled');
  assert.ok((await readdir(path.join(video, 'dist/assets'))).some(n => /^mark-.*\.svg$/.test(n)), 'CSS asset must be copied');
  const {serve} = await import(pathToFileURL(path.join(video, 'server.mjs')).href);
  const oldCwd = process.cwd(); process.chdir(video);
  let serving; try { serving = await serve(); } finally { process.chdir(oldCwd); }
  server = serving.server;
  browser = await chromium.launch({headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
  const page = await browser.newPage({viewport: {width: 1920, height: 1080}});
  const failures = []; page.on('pageerror', e => failures.push(e.message));
  page.on('response', r => { if (r.status() >= 400) failures.push(`${r.status()} ${r.url()}`); });
  await page.goto(serving.url, {waitUntil: 'networkidle'});
  const snap = await page.evaluate(async () => {
    await window.__filmReady;
    const wrap = document.querySelector('section[data-shot="component"] .wrap');
    const gl = document.querySelector('.gl');
    const pixel = () => { const c = document.createElement('canvas'); c.width = c.height = 1; const x = c.getContext('2d'); x.drawImage(gl, 0, 0, 1, 1); return [...x.getImageData(0, 0, 1, 1).data.slice(0, 3)]; };
    await seek(5); const late = {opacity: getComputedStyle(wrap).opacity, px: pixel()};
    await seek(3.6); const early = {opacity: getComputedStyle(wrap).opacity, px: pixel()};
    await seek(5); const back = getComputedStyle(wrap).opacity;
    return {late, early, back, heading: getComputedStyle(document.querySelector('.panel h2')).fontSize,
      text: document.querySelector('.panel h2').textContent, fetched: document.querySelector('.fetched').textContent,
      introHidden: getComputedStyle(document.querySelector('section[data-shot="intro"]')).visibility};
  });
  assert.equal(snap.text, 'Repository-only dependency');
  assert.equal(snap.fetched, 'Fixture data', 'component effect must receive fixture API data');
  assert.equal(snap.heading, '31px');
  assert.equal(snap.late.opacity, '1'); assert.ok(Number(snap.early.opacity) < 0.5, 'seeking back must restore the earlier GSAP state');
  assert.equal(snap.back, '1');
  assert.deepEqual(snap.late.px, [255, 0, 0], 'WebGL layer must render in headless capture');
  assert.deepEqual(snap.early.px, [0, 0, 255]);
  assert.equal(snap.introHidden, 'hidden', 'shots far from t are hidden');
  assert.deepEqual(failures, []);
  console.log('PASS: repo-only dependency, alias, CSS asset, fixture API, GSAP forward/back seek, WebGL render, shot visibility.');
} finally {
  await browser?.close();
  if (server) await new Promise(resolve => server.close(resolve));
  await rm(workspace, {recursive: true, force: true});
}
