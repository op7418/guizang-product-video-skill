// Particles that fly in and settle into a shape (Three.js, orthographic px space, y down).
// Targets come from the product's own geometry: its logo SVG, an icon, a chart path, the
// outline of a key UI element. `targetsFromSvg` samples the rendered SVG's shapes.
import * as THREE from 'three';
/** Boxes of each drawable child of an on-screen SVG, placed at (cx, cy) with rendered size px. */
export function targetsFromSvg(svg, {cx = 960, cy = 540, px = 300} = {}) {
  const vb = svg.viewBox.baseVal, k = px / vb.width;
  return [...svg.querySelectorAll('path,rect,circle,ellipse,polygon')].map(el => {
    const b = el.getBBox(), o = Number(el.getAttribute('opacity') || el.getAttribute('fill-opacity') || 1);
    return {x: cx - px / 2 + (b.x - vb.x) * k, y: cy - px * vb.height / vb.width / 2 + (b.y - vb.y) * k, w: b.width * k, h: b.height * k, o,
      round: el.tagName === 'circle' || el.tagName === 'ellipse'};
  });
}
export function createSettle(canvas, targets, {count = 2200, color = 0x111111, from = 'ring', dur = 1.25, order = (t, i) => i * 0.02, size = [1920, 1080]} = {}) {
  const renderer = new THREE.WebGLRenderer({canvas, antialias: true, alpha: true, preserveDrawingBuffer: true});
  renderer.setPixelRatio(1); renderer.setSize(size[0], size[1], false);
  const scene = new THREE.Scene(), camera = new THREE.OrthographicCamera(0, size[0], 0, size[1], -10, 10);
  let seed = 5; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const w = targets.map(t => t.w * t.h * Math.max(0.15, t.o)), total = w.reduce((a, b) => a + b, 0);
  const P = [];
  targets.forEach((tg, ti) => {
    for (let k = 0, n = Math.round(count * w[ti] / total); k < n; k++) {
      let x, y; do { x = rnd() - 0.5; y = rnd() - 0.5; } while (tg.round && x * x + y * y > 0.25);
      const a = rnd() * Math.PI * 2, r = 500 + rnd() * 900;
      const start = from === 'ring' ? {x: size[0] / 2 + Math.cos(a) * r * 1.3, y: size[1] / 2 + Math.sin(a) * r * 0.8} : {x: rnd() * size[0], y: from === 'below' ? size[1] + rnd() * 300 : -rnd() * 300};
      P.push({tx: tg.x + tg.w / 2 + x * tg.w * 0.92, ty: tg.y + tg.h / 2 + y * tg.h * 0.92, o: tg.o, sx: start.x, sy: start.y, delay: order(tg, ti) + rnd() * 0.25, s: 2.4 + rnd() * 2.2});
    }
  });
  const pos = new Float32Array(P.length * 3), alpha = new Float32Array(P.length), sz = new Float32Array(P.length), geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('a', new THREE.BufferAttribute(alpha, 1)); geo.setAttribute('sz', new THREE.BufferAttribute(sz, 1));
  scene.add(new THREE.Points(geo, new THREE.ShaderMaterial({transparent: true, depthWrite: false, uniforms: {uColor: {value: new THREE.Color(color)}},
    vertexShader: 'attribute float a; attribute float sz; varying float va; void main(){va=a; gl_PointSize=sz; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
    fragmentShader: 'uniform vec3 uColor; varying float va; void main(){float m=smoothstep(0.5,0.35,length(gl_PointCoord-0.5)); gl_FragColor=vec4(uColor,va*m);}'})));
  const ease = x => 1 - Math.pow(1 - Math.min(1, Math.max(0, x)), 4);
  return function render(t, {fade = 1} = {}) {
    P.forEach((p, i) => {
      const u = ease((t - p.delay) / dur);
      pos[i * 3] = p.sx + (p.tx - p.sx) * u + Math.sin(u * Math.PI) * 40; pos[i * 3 + 1] = p.sy + (p.ty - p.sy) * u;
      alpha[i] = Math.min(1, u * 1.6) * (0.35 + 0.65 * p.o) * fade; sz[i] = p.s * (1 + (1 - u) * 1.5);
    });
    geo.attributes.position.needsUpdate = true; geo.attributes.a.needsUpdate = true; geo.attributes.sz.needsUpdate = true;
    renderer.render(scene, camera);
  };
}
