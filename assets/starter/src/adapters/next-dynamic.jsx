// Lazy-loaded product panels are not part of any shot.
export default function dynamic() { return function DynamicPlaceholder() { return null; }; }
