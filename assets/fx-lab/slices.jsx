import React from 'react';
// Slice entrance: a word rendered as N horizontal strips that snap in from different offsets,
// optionally with thin light bars. Reads as "signal / interruption"; use it for a hard section
// change, not as a default title entrance. Strip count, offsets and bar colours are film choices.
export function Sliced({text, strips = 14, height = 360, className = '', lang = 'en'}) {
  return <div className={'fx-sliced ' + className} style={{position: 'relative', height}}>
    {Array.from({length: strips}, (_, i) => <div key={i} className="fx-slice" style={{position: 'absolute', inset: 0, clipPath: `inset(${i / strips * 100}% 0 ${100 - (i + 1) / strips * 100}% 0)`}}><span lang={lang}>{text}</span></div>)}
  </div>;
}
export function sliceIn(tl, root, at, {spread = 520, dur = 0.42, seed = 3} = {}) {
  let s = seed; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  root.querySelectorAll('.fx-slice').forEach(el => tl.fromTo(el, {x: (rnd() - 0.5) * spread, opacity: 0}, {x: 0, opacity: 1, duration: dur, ease: 'expo.out'}, at + rnd() * 0.08));
}
