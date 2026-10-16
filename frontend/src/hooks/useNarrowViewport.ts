import { useSyncExternalStore } from 'react';

const query = '(max-width: 1023px)';
function subscribe(notify: () => void) {
  const media = window.matchMedia?.(query);
  media?.addEventListener('change', notify);
  return () => media?.removeEventListener('change', notify);
}
const snapshot = () => window.matchMedia?.(query).matches ?? false;

/** Keep phone/tablet map tools compact below lg without a resize/render loop. */
export function useNarrowViewport() {
  return useSyncExternalStore(subscribe, snapshot, () => false);
}
