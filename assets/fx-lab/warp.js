// Streak field (Three.js): points rushing toward / away from camera. Position is the integral of
// speed, so any t renders identically. Derive: colour from the product palette, density and
// speed curve from the film's energy, direction (toward/away/sideways) from the story beat.
import * as THREE from 'three';
export function createStreaks(canvas, {count = 2400, depth = 1400, color = [1, 1, 1], radius = 900, v0 = 180, accel = 70, spin = 0.06, size = [1920, 1080]} = {}) {
  const renderer = new THREE.WebGLRenderer({canvas, antialias: true, alpha: true, preserveDrawingBuffer: true});
  renderer.setPixelRatio(1); renderer.setSize(size[0], size[1], false);
  const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(72, size[0] / size[1], 1, 3000);
  let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const P = Array.from({length: count}, () => { const a = rnd() * Math.PI * 2, r = 30 + Math.pow(rnd(), 0.7) * radius; return {x: Math.cos(a) * r, y: Math.sin(a) * r * 0.8, z: rnd() * depth, b: 0.35 + rnd() * 0.65}; });
  const pos = new Float32Array(count * 6), col = new Float32Array(count * 6), geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  scene.add(new THREE.LineSegments(geo, new THREE.LineBasicMaterial({vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false})));
  const dist = t => v0 * t + accel * t ** 4, speed = t => v0 + 4 * accel * t ** 3;
  return function render(t, {fade = 1} = {}) {
    const d = dist(t), streak = Math.min(900, 0.045 * speed(t) + 4);
    P.forEach((p, i) => {
      const z = ((p.z - d) % depth + depth) % depth, zz = -z - 5, tail = Math.min(streak * (1 - z / depth) * 1.6 + 2, z + 4);
      pos.set([p.x, p.y, zz, p.x, p.y, zz - tail], i * 6);
      const c = p.b * Math.pow(1 - z / depth, 1.4) * fade;
      col.set([c * color[0], c * color[1], c * color[2], c * color[0] * .15, c * color[1] * .15, c * color[2] * .15], i * 6);
    });
    geo.attributes.position.needsUpdate = true; geo.attributes.color.needsUpdate = true;
    camera.rotation.z = t * spin;
    renderer.render(scene, camera);
  };
}
