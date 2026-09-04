import type { Camera, Object3D } from 'three';

export interface SceneTileRenderer {
  group?: Object3D | null;
  isLoading?: boolean;
  visibleTiles?: Set<unknown>;
  downloadQueue?: SceneTileQueue;
  parseQueue?: SceneTileQueue;
  processNodeQueue?: SceneTileQueue;
  errorTarget?: number;
  loadSiblings?: boolean;
  lruCache?: {
    minSize: number;
    maxSize: number;
    minBytesSize: number;
    maxBytesSize: number;
  };
  setResolution?: (camera: Camera, width: number, height: number) => boolean;
  addEventListener: (type: 'tiles-load-start' | 'tiles-load-end', listener: () => void) => void;
  removeEventListener: (type: 'tiles-load-start' | 'tiles-load-end', listener: () => void) => void;
}

interface WaitForTilesSettledOptions {
  /** How long tile loading must remain idle before a capture is safe. */
  stableMs?: number;
  /** Hard ceiling so a failed tile never leaves the render UI spinning forever. */
  timeoutMs?: number;
}

export interface SceneTileQueue {
  autoUpdate: boolean;
  readonly running?: boolean;
  scheduleJobRun?: () => void;
}

interface WaitForVisibleTileCoverageOptions {
  /** How long the exact visible tile set must remain unchanged. */
  stableMs?: number;
  /** Poll cadence for checking the renderer's visible tile set. */
  pollMs?: number;
  /** Hard ceiling so background refinement cannot block capture forever. */
  timeoutMs?: number;
  /** Reject an empty or incomplete base tileset. */
  minimumVisibleTiles?: number;
  /** Accept loaded visible coverage when only background refinement times out. */
  acceptVisibleCoverageAtTimeout?: boolean;
}

type WaitForTileDisplayReadyOptions = Omit<
  WaitForVisibleTileCoverageOptions,
  'acceptVisibleCoverageAtTimeout'
>;

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

/**
 * Wait for the exact visible Google context to stop changing.
 *
 * Google Photorealistic 3D Tiles can keep the renderer-wide `isLoading` flag
 * set while low-priority descendants refine outside the useful camera view.
 * High-quality route capture therefore gates on the set of tiles actually
 * being drawn. Object identity is included in the signature so a same-sized
 * replacement set still restarts the stability window.
 */
export function waitForVisibleTileCoverage(
  tiles: SceneTileRenderer | null | undefined,
  {
    stableMs = 900,
    pollMs = 100,
    timeoutMs = 12_000,
    minimumVisibleTiles = 1,
    acceptVisibleCoverageAtTimeout = false,
  }: WaitForVisibleTileCoverageOptions = {},
): Promise<boolean> {
  if (!tiles?.visibleTiles) return Promise.resolve(false);

  return new Promise((resolve) => {
    const objectIds = new WeakMap<object, number>();
    let nextObjectId = 1;
    let lastSignature: string | null = null;
    let stableSince = Date.now();
    let complete = false;
    let pollTimer: number | null = null;
    let timeoutTimer: number | null = null;

    const tileId = (tile: unknown) => {
      if ((typeof tile === 'object' && tile !== null) || typeof tile === 'function') {
        const objectTile = tile as object;
        let id = objectIds.get(objectTile);
        if (id === undefined) {
          id = nextObjectId;
          nextObjectId += 1;
          objectIds.set(objectTile, id);
        }
        return `o${id}`;
      }
      return `${typeof tile}:${String(tile)}`;
    };

    const finish = (settled: boolean) => {
      if (complete) return;
      complete = true;
      if (pollTimer !== null) window.clearInterval(pollTimer);
      if (timeoutTimer !== null) window.clearTimeout(timeoutTimer);
      resolve(settled);
    };

    const sample = () => {
      const visibleTiles = tiles.visibleTiles;
      if (!visibleTiles || visibleTiles.size < minimumVisibleTiles) {
        lastSignature = null;
        stableSince = Date.now();
        return;
      }
      const signature = Array.from(visibleTiles, tileId).sort().join(',');
      const now = Date.now();
      if (signature !== lastSignature) {
        lastSignature = signature;
        stableSince = now;
        return;
      }
      if (now - stableSince >= stableMs) finish(true);
    };

    sample();
    pollTimer = window.setInterval(sample, Math.max(16, pollMs));
    timeoutTimer = window.setTimeout(() => {
      const visibleCount = tiles.visibleTiles?.size ?? 0;
      finish(acceptVisibleCoverageAtTimeout && visibleCount >= minimumVisibleTiles);
    }, Math.max(0, timeoutMs));
  });
}

/** Capture the settled visible context without waiting for off-camera downloads.
 * Unlike the display indicator, this never accepts changing or empty coverage
 * merely because its deadline expired. */
export function waitForCaptureTileReadiness(
  tiles: SceneTileRenderer | null | undefined,
  options: WaitForTileDisplayReadyOptions = {},
): Promise<boolean> {
  return waitForVisibleTileCoverage(tiles, {
    stableMs: 900,
    timeoutMs: 8_000,
    ...options,
    acceptVisibleCoverageAtTimeout: false,
  });
}

/**
 * Bound the user-facing loading indicator without weakening capture gates.
 *
 * A non-empty visible tile set is enough to release the UI after the timeout
 * even when low-priority descendants keep refining. Empty or unavailable tile
 * sets still fail closed. Capture callers continue to use the stricter helpers
 * above and must opt into timeout acceptance explicitly when appropriate.
 */
export function waitForTileDisplayReady(
  tiles: SceneTileRenderer | null | undefined,
  {
    stableMs = 900,
    pollMs = 100,
    timeoutMs = 8_000,
    minimumVisibleTiles = 1,
  }: WaitForTileDisplayReadyOptions = {},
): Promise<boolean> {
  return waitForVisibleTileCoverage(tiles, {
    stableMs,
    pollMs,
    timeoutMs,
    minimumVisibleTiles,
    acceptVisibleCoverageAtTimeout: true,
  });
}

/** Pause new Google tile work after a full route preload, then resume exactly
 * the queues that were active before capture. Already visible tiles remain
 * renderable from the enlarged capture cache. */
export function holdTileQueueUpdates(
  tiles: SceneTileRenderer | null | undefined,
): () => void {
  const queues = [tiles?.downloadQueue, tiles?.parseQueue, tiles?.processNodeQueue]
    .filter((queue): queue is SceneTileQueue => Boolean(queue));
  const previous = queues.map((queue) => queue.autoUpdate);
  queues.forEach((queue) => { queue.autoUpdate = false; });
  let restored = false;

  return () => {
    if (restored) return;
    restored = true;
    queues.forEach((queue, index) => {
      queue.autoUpdate = previous[index];
      if (previous[index] && queue.running) queue.scheduleJobRun?.();
    });
  };
}
