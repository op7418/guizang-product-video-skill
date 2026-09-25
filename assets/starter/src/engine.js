// Deterministic film engine. seek(t) is a pure function of t:
//   1. publish t to React (discrete product states re-render synchronously)
//   2. run DOM drivers (real interactions: typing, clicks, popovers) and await them
//   3. seek the paused GSAP master timeline
//   4. toggle shot visibility, then call per-shot render hooks (canvas / WebGL layers)
import gsap from 'gsap';
import {flushSync} from 'react-dom';
import plan from '../plan.json';
import {FilmClock} from './film-store.js';

gsap.ticker.sleep();                       // never tick on wall-clock time
export const master = gsap.timeline({paused: true});
export const shots = plan.shots;
export const shot = id => shots.find(s => s.id === id);
const renders = [], drivers = [];
/** Canvas/WebGL/text work that must be recomputed every frame. fn(localTime, filmTime). */
export const onRender = (id, fn) => renders.push({s: shot(id), fn});
/** Real product interaction for a shot. fn(localTime) may return a Promise (e.g. wait for a popover). */
export const onDrive = (id, fn) => drivers.push({s: shot(id), fn});
export const frame = () => new Promise(r => requestAnimationFrame(() => r()));
const PAD = 0.8;   // shots stay mounted/visible this long around their window so transitions can overlap
const near = (s, t) => t >= s.start - PAD && t < s.end + PAD;

export async function seek(seconds) {
  const t = Math.min(Math.max(Number(seconds) || 0, 0), plan.duration - 1 / plan.fps);
  flushSync(() => FilmClock.set(t));
  const pending = drivers.filter(d => near(d.s, t)).map(d => d.fn(t - d.s.start)).filter(r => r && r.then);
  if (pending.length) await Promise.all(pending);
  master.seek(t, true);
  for (const s of shots) {
    const el = document.querySelector(`section[data-shot="${s.id}"]`);
    if (el) el.style.visibility = near(s, t) ? 'visible' : 'hidden';
  }
  for (const r of renders) if (near(r.s, t)) r.fn(t - r.s.start, t);
  window.CURRENT_TIME = t;
}
