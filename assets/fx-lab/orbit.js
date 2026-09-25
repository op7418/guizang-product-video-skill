// Items on a tilted ring around a centre, projected by hand (no CSS 3D needed): depth drives
// scale, opacity, blur and z-order so items pass behind and in front of the centre element.
// Use for "many things connect to one" (integrations, providers, plugins). Derive the item
// count from real data; don't invent members to fill the ring.
export function paintOrbit(items, t, {cx = 960, cy = 610, R = 760, r = 230, speed = 0.38, grow = 1, front = 6, back = 2} = {}) {
  const n = items.length;
  items.forEach((el, i) => {
    const phi = (i / n) * Math.PI * 2 + t * speed, depth = Math.sin(phi);
    const x = cx + Math.cos(phi) * R * grow, y = cy + depth * r * grow, sc = 0.72 + 0.34 * (depth + 1) / 2;
    el.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%) scale(${sc})`;
    el.style.opacity = String(grow * (0.45 + 0.55 * (depth + 1) / 2));
    el.style.filter = depth < -0.2 ? `blur(${((-depth - 0.2) * 3).toFixed(2)}px)` : 'none';
    el.style.zIndex = String(depth > 0 ? front : back);
  });
}
