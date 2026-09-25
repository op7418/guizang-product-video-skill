import {frame} from '../engine.js';
// Real interactions with product components, driven from onDrive(). Keep them idempotent:
// compute the wanted state from local time and only act when the DOM differs.
/** Set a React-controlled textarea/input value and fire the input event React listens to. */
export function setFieldValue(field, value) {
  if (!field || field.value === value) return;
  const proto = field instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto, 'value').set.call(field, value);
  field.dispatchEvent(new Event('input', {bubbles: true}));
}
/** Type `text` from `at` at `cps` characters/second (clears at `clearAt`). */
export function typed(text, local, at, cps, clearAt = Infinity) {
  const chars = Array.from(text);
  if (local < at || local >= clearAt) return '';
  return chars.slice(0, Math.min(chars.length, Math.floor((local - at) * cps) + 1)).join('');
}
/** Open/close something toggled by a real click (menus, popovers). isOpen() reads the DOM. */
export async function ensureOpen(want, isOpen, toggle) {
  if (want === isOpen()) return;
  toggle();
  await frame(); await frame();   // let positioning (e.g. floating-ui) settle before capture
}
