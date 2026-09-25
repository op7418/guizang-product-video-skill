import {build} from 'esbuild';
import {readFile, writeFile, mkdir, cp, rm} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import path from 'node:path';
import integration from './integration.config.mjs';
// Client-mounted film: product components run in the browser (fixture /api in src/fake-api.js),
// one paused GSAP timeline + per-shot render hooks drive every frame through window.seek(t).
const plan = JSON.parse(await readFile('plan.json', 'utf8'));
const repoDir = integration.repoDir || plan.repo;
await rm('dist', {recursive: true, force: true});
await mkdir('dist', {recursive: true});
const result = await build({
  entryPoints: ['src/client.jsx'], bundle: true, platform: 'browser', format: 'iife', jsx: 'automatic',
  outfile: '.build/client.js', metafile: true, minify: true, legalComments: 'none',
  // Resolve product dependencies from the product's own node_modules first.
  nodePaths: [...(repoDir ? [path.resolve(repoDir, 'node_modules')] : []), path.resolve('node_modules')],
  // One React runtime shared by the film and every bundled product component.
  alias: {...integration.aliases, react: path.resolve('node_modules/react'), 'react-dom': path.resolve('node_modules/react-dom')},
  define: {'process.env.NODE_ENV': '"production"', 'process.env': '{}', 'process.platform': '"darwin"', ...integration.define},
  external: integration.external || [],
  loader: {'.js': 'jsx', '.css': 'css', '.module.css': 'local-css', '.png': 'file', '.jpg': 'file', '.svg': 'file', '.woff': 'file', '.woff2': 'file', '.ttf': 'file', ...integration.loaders},
  assetNames: 'assets/[name]-[hash]', logLevel: 'error',
});
await mkdir('evidence', {recursive: true});
await writeFile('evidence/component-imports.json', JSON.stringify(result.metafile, null, 2));
const bundle = await readFile('.build/client.js', 'utf8');
if (!plan.demo && bundle.includes('data-skill-placeholder')) throw new Error('Technical fixture is still on screen. Connect the actual product feature components before production.');
let css = '';
for (const f of ['assets/fallback/tokens.css', 'src/product.css', '.build/client.css', 'src/film.css']) if (existsSync(f)) css += '\n' + await readFile(f, 'utf8');
await writeFile('dist/index.html', `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${plan.product || 'film'}</title><style>${css}</style><body><div id="film-root"></div><script src="client.js"></script></body></html>`);
await cp('.build/client.js', 'dist/client.js');
if (existsSync('public')) await cp('public', 'dist', {recursive: true});
if (existsSync('assets')) await cp('assets', 'dist/assets', {recursive: true});
for (const file of Object.keys(result.metafile.outputs)) {
  if (/\.(?:js|css|map)$/.test(file)) continue;
  const dest = path.join('dist', path.relative('.build', file));
  await mkdir(path.dirname(dest), {recursive: true}); await cp(file, dest);
}
console.log('Built dist/index.html; imports recorded in evidence/component-imports.json');
