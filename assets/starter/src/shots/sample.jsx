import React from 'react';
import {Split, reveal} from '../kit/text.jsx';
import {shot} from '../engine.js';
import {FeatureVisual} from '../presentations.jsx';
// Technical sample only: proves mount → timeline → seek → capture. It has no visual direction on
// purpose. Production shots are written per film from DIRECTION.md (references/direction.md).
const q = (id, sel) => document.querySelector(`section[data-shot="${id}"] ${sel}`);
export function TitleView({shot: s}) {
  return <div className="sample-title"><div className="en"><Split text={s.headlineEn || ''} lang="en" /></div><div className="zh"><Split text={s.headline} lang="zh-CN" /></div></div>;
}
export function ComponentView() {
  return <div className="sample-component"><div className="sample-cam"><FeatureVisual /></div></div>;
}
export const buildTitle = id => tl => {
  const s = shot(id);
  tl.set(document.querySelector(`section[data-shot="${id}"]`), {opacity: 1}, s.start);
  reveal(tl, q(id, '.en'), s.start + 0.1);
  reveal(tl, q(id, '.zh'), s.start + 0.4, {stagger: 0.05});
};
export const buildComponent = id => tl => {
  const s = shot(id);
  tl.set(document.querySelector(`section[data-shot="${id}"]`), {opacity: 1}, s.start);
  tl.fromTo(q(id, '.sample-cam'), {scale: 0.9, opacity: 0}, {scale: 1, opacity: 1, duration: 0.8, ease: 'expo.out'}, s.start);
  tl.to(q(id, '.sample-cam'), {scale: 1.04, duration: s.end - s.start - 0.8, ease: 'none'}, s.start + 0.8);
};
