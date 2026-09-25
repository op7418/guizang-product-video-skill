// Deterministic browser runtime for the film. Import before any product module.
// - fixed clock and seeded Math.random (time-of-day greetings, random picks)
// - fixture-backed fetch for the product's API routes, so real components run their effects offline
// - silent EventSource / WebSocket stubs (no streaming connections)
import {API_FIXTURES, API_PREFIXES} from './fixtures/api.js';

const FIXED_NOW = new Date('2026-01-15T10:00:00+08:00').getTime();   // pick a time that suits the story
const RealDate = Date;
class FilmDate extends RealDate { constructor(...a) { a.length ? super(...a) : super(FIXED_NOW); } static now() { return FIXED_NOW; } }
globalThis.Date = FilmDate;
let seed = 7418;
Math.random = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
try { localStorage.clear(); sessionStorage.clear(); } catch {}

window.__filmApiLog = [];
const json = (data, status = 200) => new Response(JSON.stringify(data), {status, headers: {'Content-Type': 'application/json'}});
const realFetch = window.fetch.bind(window);
window.fetch = async (input, init) => {
  const url = new URL(typeof input === 'string' ? input : input.url, location.href);
  if (!API_PREFIXES.some(p => url.pathname.startsWith(p))) return realFetch(input, init);
  window.__filmApiLog.push(url.pathname + url.search);   // inspect in stills.mjs output to find missing fixtures
  const h = API_FIXTURES[url.pathname];
  return h === undefined ? json({}) : json(typeof h === 'function' ? h(url, init) : h);
};
class Silent { constructor() { this.readyState = 0; } close() {} send() {} addEventListener() {} removeEventListener() {} }
window.EventSource = Silent;
window.WebSocket = Silent;
