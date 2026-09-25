import React from 'react';
// Split text into spans so GSAP can stagger it. Choose the unit that fits the film's voice:
// 'ch' (per character), 'word', or 'line' (one span per \n-separated line).
export function Split({text, by = 'ch', className = '', lang}) {
  const parts = by === 'line' ? text.split('\n') : by === 'word' ? text.split(/(\s+)/) : Array.from(text);
  return <span className={'split ' + className} lang={lang}>
    {parts.map((p, i) => <span key={i} className={'u u-' + by}>{p === ' ' ? ' ' : p}</span>)}
  </span>;
}
/** Stagger the split units of `root` from `from` to rest. The from-state is the film's decision. */
export function reveal(tl, root, at, {from = {opacity: 0, y: 24, filter: 'blur(12px)'}, dur = 0.7, stagger = 0.035, ease = 'expo.out'} = {}) {
  const units = root.querySelectorAll('.u');
  const to = Object.fromEntries(Object.keys(from).map(k => [k, k === 'filter' ? 'blur(0px)' : k === 'opacity' || k === 'scale' ? 1 : 0]));
  tl.fromTo(units, from, {...to, duration: dur, ease, stagger}, at);
}
