import React from 'react';
// next/image → plain <img>; the film has no image optimizer.
export default function Image({src, alt = '', width, height, className, style, fill, priority, unoptimized, ...rest}) {
  const url = typeof src === 'object' ? src.src : src;
  return <img src={url} alt={alt} width={fill ? undefined : width} height={fill ? undefined : height} className={className} style={fill ? {position: 'absolute', inset: 0, width: '100%', height: '100%', ...style} : style} {...rest} />;
}
