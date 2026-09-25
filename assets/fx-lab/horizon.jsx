import React from 'react';
// Luminous horizon (CSS only): a lit rim behind a dark body, for staging a product or a title.
// Derive: core/fringe colours from the brand (monochrome brands keep a near-white core and a
// faint fringe; colourful brands can let the fringe carry the palette). Animate the wrapper
// (y, opacity, scale) from the timeline. Tune size/top per layout; it is not a fixed look.
export function Horizon({top = 780, core = '255,255,255', fringe = ['99,102,241', '56,189,248', '251,191,36', '244,114,182'], ground = '#050404', className = ''}) {
  const [a, b, c, d] = fringe;
  return <div className={'fx-horizon ' + className} style={{position: 'absolute', left: '50%', top, width: 2800, height: 1400, marginLeft: -1400, pointerEvents: 'none'}}>
    <i style={{...ring, width: 2600, height: 900, marginLeft: -1300, top: -260, background: `radial-gradient(closest-side, rgba(${core},.22), rgba(${core},.05) 55%, transparent 75%)`, filter: 'blur(40px)'}} />
    <i style={{...ring, width: 2300, height: 1150, marginLeft: -1150, top: -40, background: `conic-gradient(from 270deg at 50% 50%, rgba(${a},.55), rgba(${b},.35) 22%, rgba(${core},.4) 50%, rgba(${c},.35) 78%, rgba(${d},.5))`, filter: 'blur(46px)', opacity: .55}} />
    <i style={{...ring, width: 2100, height: 1060, marginLeft: -1050, top: -8, background: `radial-gradient(closest-side, rgba(${core},.95), rgba(${core},.6) 80%, rgba(${core},0))`, filter: 'blur(18px)'}} />
    <i style={{...ring, width: 2140, height: 1100, marginLeft: -1070, top: 18, background: ground, filter: 'blur(6px)'}} />
    <i style={{...ring, width: 2120, height: 1086, marginLeft: -1060, top: 10, borderTop: `2px solid rgba(${core},.85)`, filter: 'blur(1.2px)'}} />
  </div>;
}
const ring = {position: 'absolute', left: '50%', borderRadius: '50%'};
