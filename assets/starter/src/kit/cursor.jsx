import React from 'react';
// Pointer overlay (video layer, not a product element). Put it inside the scaled product root so
// it shares the product's camera; position it from a driver with paintCursor().
export function Cursor({id, color = '#111', stroke = '#fff'}) {
  return <div className="film-cursor" data-cursor={id}>
    <svg viewBox="0 0 24 24" width="32" height="32"><path d="M5 2.5v17.2l4.6-4.3 2.9 6.6 2.8-1.2-2.8-6.5h6.3z" fill={color} stroke={stroke} strokeWidth="1.3" strokeLinejoin="round" /></svg>
    <i className="film-ripple" />
  </div>;
}
const ease = x => (x < 0.5 ? 16 * x ** 5 : 1 - Math.pow(-2 * x + 2, 5) / 2);
/** keys [{at,x,y}] in product px; clicks [t]; show [from,to]. Pure function of local time. */
export function paintCursor(el, local, keys, clicks = [], show = [-1, 1e9]) {
  if (!el) return;
  const visible = local >= show[0] && local < show[1] && keys.length;
  el.style.opacity = visible ? '1' : '0';
  if (!visible) return;
  let p = keys[0];
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i], b = keys[i + 1];
    if (local >= b.at) { p = b; continue; }
    if (local >= a.at) { const u = ease((local - a.at) / (b.at - a.at)); p = {x: a.x + (b.x - a.x) * u, y: a.y + (b.y - a.y) * u}; }
    break;
  }
  const since = clicks.map(c => local - c).filter(d => d >= 0 && d < 0.45)[0];
  el.style.transform = `translate(${p.x - 6}px, ${p.y - 3}px)`;
  el.querySelector('svg').style.transform = since !== undefined && since < 0.18 ? `scale(${0.84 + 0.16 * since / 0.18})` : '';
  const r = el.querySelector('.film-ripple');
  r.style.opacity = since !== undefined ? String(1 - since / 0.45) : '0';
  r.style.transform = since !== undefined ? `scale(${0.4 + since * 3})` : '';
}
