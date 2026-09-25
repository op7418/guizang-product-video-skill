// Film clock for React. Components subscribe through a selector and re-render only when
// the selected (discrete) value changes — e.g. how many tool steps are visible.
import {useSyncExternalStore, createContext, useContext} from 'react';
let time = 0;
const listeners = new Set();
export const FilmClock = {
  get: () => time,
  set(t) { time = t; listeners.forEach(fn => fn()); },
  subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
};
export const ShotContext = createContext({start: 0, end: 0});
/** Select a primitive from shot-local time. */
export function useShotState(select) {
  const {start} = useContext(ShotContext);
  return useSyncExternalStore(FilmClock.subscribe, () => select(time - start), () => select(0));
}
/** How many of the given local times have passed (a stage index). */
export const stageAt = (local, times) => times.filter(at => local >= at).length;
