import React from 'react';
export default function Link({href, children, prefetch, ...rest}) {
  return <a href={typeof href === 'string' ? href : '#'} {...rest}>{children}</a>;
}
