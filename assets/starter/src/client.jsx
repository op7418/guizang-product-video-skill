import './fake-api.js';
import React from 'react';
import {createRoot} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {Film} from './film.jsx';
import {seek, frame, master} from './engine.js';
import {SHOT_BUILDERS} from './shots/index.js';
// If the product uses motion/framer-motion, make its micro-animations jump to the end state:
//   import {MotionGlobalConfig} from 'motion/react'; MotionGlobalConfig.skipAnimations = true;

const root = createRoot(document.getElementById('film-root'));
flushSync(() => root.render(<Film />));
window.seek = seek;
window.__master = master;
window.__filmReady = (async () => {
  await document.fonts.ready;
  await new Promise(r => setTimeout(r, 800));   // fixture fetches and effects settle
  await frame(); await frame();
  // Builders run after layout exists: they can measure real component positions.
  // Builders may be async. Only await real Promises: a GSAP timeline is thenable and a paused one
  // never resolves, so `tl => tl.set(...)` returning the timeline must not be awaited.
  for (const build of Object.values(SHOT_BUILDERS)) { const r = build(master); if (r instanceof Promise) await r; }
  await seek(0);
})();
let t0 = null, req = null;
window.playFilm = () => { cancelAnimationFrame(req); t0 = null; const loop = async now => { t0 ??= now; await seek((now - t0) / 1000); req = requestAnimationFrame(loop); }; req = requestAnimationFrame(loop); };
window.stopFilm = () => cancelAnimationFrame(req);
