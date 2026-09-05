import type { SharedSiteGroundState } from './SharedSiteGroundProvider';
import type { SharedSiteGroundSnapshot } from './sharedSiteGround';

/** Capture must never turn a missing mesh measurement into a guessed grade. */
export function captureSharedGround(state: SharedSiteGroundState): SharedSiteGroundSnapshot | undefined {
  if (state.status === 'inactive') return undefined;
  if (state.status !== 'ready' || !state.snapshot) {
    throw new Error('Ground alignment is not ready. Keep the site in view while its 3D terrain loads, then try again.');
  }
  return structuredClone(state.snapshot);
}

export function assertSharedGroundUnchanged(
  snapshot: SharedSiteGroundSnapshot | undefined,
  current: SharedSiteGroundState,
): void {
  if (snapshot ? current.status !== 'ready' || snapshot.signature !== current.snapshot?.signature
    : current.status !== 'inactive') {
    throw new Error('The terrain changed during capture. Let ground alignment finish and try again.');
  }
}
