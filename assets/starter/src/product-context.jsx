import React from 'react';
// Display adapter: the providers the product's app shell normally supplies (i18n, theme, tooltip,
// router/panel contexts…). Read the product's root layout / shell and mirror only what the
// on-screen components actually need, with static values. Add `dark` to use the product's dark theme.
export function ProductContext({children, dark = false, className = ''}) {
  return <div className={'product-root ' + (dark ? 'dark ' : '') + className}>{children}</div>;
}
