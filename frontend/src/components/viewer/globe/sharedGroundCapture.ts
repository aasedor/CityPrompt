import type { SharedSiteGroundState } from './SharedSiteGroundProvider';
import type { SharedSiteGroundSnapshot } from './sharedSiteGround';

export function groundReadinessMessage(state: SharedSiteGroundState): string {
  if (state.status === 'sampling') return 'Aligning to ground…';
  if (state.failureReason === 'discontinuity') {
    return 'Ground has abrupt height changes. Check for roofs, trees or steep terrain inside the site. Use Clear site only for an intentional redevelopment.';
  }
  if (state.status === 'unavailable') {
    return 'Ground alignment could not be verified. Check the site boundary and terrain; try a smaller clear area or reload the site.';
  }
  return 'Ground alignment is not ready. Keep the site in view while its 3D terrain loads, then try again.';
}

/** Capture must never turn a missing mesh measurement into a guessed grade. */
export function captureSharedGround(state: SharedSiteGroundState): SharedSiteGroundSnapshot | undefined {
  if (state.status === 'inactive') return undefined;
  if (state.status !== 'ready' || !state.snapshot) {
    throw new Error(state.status === 'sampling'
      ? 'Ground alignment is not ready. Keep the site in view while its 3D terrain loads, then try again.'
      : groundReadinessMessage(state));
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
