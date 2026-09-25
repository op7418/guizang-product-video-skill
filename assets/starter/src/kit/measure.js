// Measuring real components for camera moves and cursor paths.
/** Centre of `el` in `root`'s own CSS pixels via the offset chain — unaffected by transforms. */
export function offsetCenter(el, root) {
  let x = 0, y = 0, n = el;
  while (n && n !== root) { x += n.offsetLeft; y += n.offsetTop; n = n.offsetParent; }
  return {x: x + el.offsetWidth / 2, y: y + el.offsetHeight / 2};
}
/** Where `el` really appears on screen at film time `t` (3D tilt, perspective, scale included).
 *  Seeks the timeline built so far, measures, then returns to 0. Use it to aim push-ins. */
export function screenCenterAt(tl, t, el) {
  tl.seek(t, true);
  const r = el.getBoundingClientRect();
  tl.seek(0, true);
  return {x: r.left + r.width / 2, y: r.top + r.height / 2};
}
