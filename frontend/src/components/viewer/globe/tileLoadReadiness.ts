import type { Object3D } from 'three';

export interface SceneTileRenderer {
  group?: Object3D | null;
  isLoading?: boolean;
  addEventListener: (type: 'tiles-load-start' | 'tiles-load-end', listener: () => void) => void;
  removeEventListener: (type: 'tiles-load-start' | 'tiles-load-end', listener: () => void) => void;
}

interface WaitForTilesSettledOptions {
  /** How long tile loading must remain idle before a capture is safe. */
  stableMs?: number;
  /** Hard ceiling so a failed tile never leaves the render UI spinning forever. */
  timeoutMs?: number;
}

/**
 * Wait for the current Google tile stream to remain idle for a short window.
 *
 * Returns false when the renderer is unavailable or the bounded timeout wins.
 * Callers can then stop before starting a paid image request.
 */
export function waitForTilesSettled(
  tiles: SceneTileRenderer | null | undefined,
  { stableMs = 600, timeoutMs = 8_000 }: WaitForTilesSettledOptions = {},
): Promise<boolean> {
  if (!tiles) return Promise.resolve(false);

  return new Promise((resolve) => {
    let stableTimer: number | null = null;
    let timeoutTimer: number | null = null;
    let complete = false;

    const clearStableTimer = () => {
      if (stableTimer !== null) {
        window.clearTimeout(stableTimer);
        stableTimer = null;
      }
    };

    const cleanup = () => {
      clearStableTimer();
      if (timeoutTimer !== null) window.clearTimeout(timeoutTimer);
      tiles.removeEventListener('tiles-load-start', handleLoadStart);
      tiles.removeEventListener('tiles-load-end', handleLoadEnd);
    };

    const finish = (settled: boolean) => {
      if (complete) return;
      complete = true;
      cleanup();
      resolve(settled);
    };

    const armStableTimer = () => {
      clearStableTimer();
      stableTimer = window.setTimeout(() => finish(true), Math.max(0, stableMs));
    };

    function handleLoadStart() {
      clearStableTimer();
    }

    function handleLoadEnd() {
      armStableTimer();
    }

    tiles.addEventListener('tiles-load-start', handleLoadStart);
    tiles.addEventListener('tiles-load-end', handleLoadEnd);
    timeoutTimer = window.setTimeout(() => finish(false), Math.max(0, timeoutMs));

    if (tiles.isLoading !== true) armStableTimer();
  });
}
