import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  holdTileQueueUpdates,
  type SceneTileRenderer,
  waitForTileDisplayReady,
  waitForTilesSettled,
  waitForVisibleTileCoverage,
} from './tileLoadReadiness';

class FakeTiles implements SceneTileRenderer {
  isLoading = false;
  visibleTiles = new Set<unknown>();
  downloadQueue?: SceneTileRenderer['downloadQueue'];
  parseQueue?: SceneTileRenderer['parseQueue'];

  private listeners = {
    'tiles-load-start': new Set<() => void>(),
    'tiles-load-end': new Set<() => void>(),
  };

  addEventListener(type: 'tiles-load-start' | 'tiles-load-end', listener: () => void) {
    this.listeners[type].add(listener);
  }

  removeEventListener(type: 'tiles-load-start' | 'tiles-load-end', listener: () => void) {
    this.listeners[type].delete(listener);
  }

  emit(type: 'tiles-load-start' | 'tiles-load-end') {
    this.isLoading = type === 'tiles-load-start';
    this.listeners[type].forEach((listener) => listener());
  }

  listenerCount() {
    return this.listeners['tiles-load-start'].size + this.listeners['tiles-load-end'].size;
  }
}

describe('waitForTilesSettled', () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it('accepts an already idle renderer after the stable window', async () => {
    vi.useFakeTimers();
    const tiles = new FakeTiles();
    const result = waitForTilesSettled(tiles, { stableMs: 600, timeoutMs: 8_000 });

    await vi.advanceTimersByTimeAsync(599);
    let resolved = false;
    void result.then(() => { resolved = true; });
    await Promise.resolve();
    expect(resolved).toBe(false);

    await vi.advanceTimersByTimeAsync(1);
    await expect(result).resolves.toBe(true);
    expect(tiles.listenerCount()).toBe(0);
  });

  it('restarts the stable window when camera movement streams more tiles', async () => {
    vi.useFakeTimers();
    const tiles = new FakeTiles();
    const result = waitForTilesSettled(tiles, { stableMs: 500, timeoutMs: 8_000 });

    await vi.advanceTimersByTimeAsync(400);
    tiles.emit('tiles-load-start');
    await vi.advanceTimersByTimeAsync(2_000);
    tiles.emit('tiles-load-end');
    await vi.advanceTimersByTimeAsync(499);

    let resolved = false;
    void result.then(() => { resolved = true; });
    await Promise.resolve();
    expect(resolved).toBe(false);

    await vi.advanceTimersByTimeAsync(1);
    await expect(result).resolves.toBe(true);
  });

  it('returns false at the safety timeout and removes its listeners', async () => {
    vi.useFakeTimers();
    const tiles = new FakeTiles();
    tiles.isLoading = true;
    const result = waitForTilesSettled(tiles, { stableMs: 500, timeoutMs: 2_000 });

    await vi.advanceTimersByTimeAsync(2_000);
    await expect(result).resolves.toBe(false);
    expect(tiles.listenerCount()).toBe(0);
  });

  it('fails closed when the tile renderer is unavailable', async () => {
    await expect(waitForTilesSettled(null)).resolves.toBe(false);
  });
});

describe('waitForVisibleTileCoverage', () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it('accepts stable visible context even while background refinement is loading', async () => {
    vi.useFakeTimers();
    const tiles = new FakeTiles();
    tiles.isLoading = true;
    tiles.visibleTiles.add({ id: 'context-a' });
    const result = waitForVisibleTileCoverage(tiles, {
      stableMs: 900,
      pollMs: 100,
      timeoutMs: 12_000,
    });

    await vi.advanceTimersByTimeAsync(900);
    await expect(result).resolves.toBe(true);
  });

  it('restarts the stability window when the visible tile identity changes', async () => {
    vi.useFakeTimers();
    const tiles = new FakeTiles();
    const original = { id: 'context-a' };
    tiles.visibleTiles.add(original);
    const result = waitForVisibleTileCoverage(tiles, {
      stableMs: 500,
      pollMs: 100,
      timeoutMs: 4_000,
    });

    await vi.advanceTimersByTimeAsync(400);
    tiles.visibleTiles.delete(original);
    tiles.visibleTiles.add({ id: 'context-b' });
    await vi.advanceTimersByTimeAsync(500);
    let resolved = false;
    void result.then(() => { resolved = true; });
    await Promise.resolve();
    expect(resolved).toBe(false);

    await vi.advanceTimersByTimeAsync(100);
    await expect(result).resolves.toBe(true);
  });

  it('fails closed when no visible context tiles arrive', async () => {
    vi.useFakeTimers();
    const tiles = new FakeTiles();
    const result = waitForVisibleTileCoverage(tiles, {
      stableMs: 300,
      pollMs: 100,
      timeoutMs: 1_000,
    });

    await vi.advanceTimersByTimeAsync(1_000);
    await expect(result).resolves.toBe(false);
  });

  it('can accept existing visible coverage when only background refinement times out', async () => {
    vi.useFakeTimers();
    const tiles = new FakeTiles();
    const first = { id: 1 };
    const second = { id: 2 };
    tiles.visibleTiles.add(first);
    const result = waitForVisibleTileCoverage(tiles, {
      stableMs: 2_000,
      pollMs: 100,
      timeoutMs: 500,
      acceptVisibleCoverageAtTimeout: true,
    });

    await vi.advanceTimersByTimeAsync(200);
    tiles.visibleTiles.delete(first);
    tiles.visibleTiles.add(second);
    await vi.advanceTimersByTimeAsync(300);
    await expect(result).resolves.toBe(true);
  });

  it('keeps capture readiness fail-closed at timeout unless explicitly opted in', async () => {
    vi.useFakeTimers();
    const tiles = new FakeTiles();
    tiles.visibleTiles.add({ id: 'still-refining' });
    const result = waitForVisibleTileCoverage(tiles, {
      stableMs: 2_000,
      pollMs: 100,
      timeoutMs: 500,
    });

    await vi.advanceTimersByTimeAsync(500);
    await expect(result).resolves.toBe(false);
  });
});

describe('waitForTileDisplayReady', () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it('bounds perpetual background refinement once visible context exists', async () => {
    vi.useFakeTimers();
    const tiles = new FakeTiles();
    tiles.isLoading = true;
    tiles.visibleTiles.add({ id: 0 });
    const result = waitForTileDisplayReady(tiles, {
      stableMs: 2_000,
      pollMs: 100,
      timeoutMs: 500,
    });

    for (let index = 1; index <= 4; index += 1) {
      await vi.advanceTimersByTimeAsync(100);
      tiles.visibleTiles.clear();
      tiles.visibleTiles.add({ id: index });
    }
    await vi.advanceTimersByTimeAsync(100);

    await expect(result).resolves.toBe(true);
  });

  it('does not falsely settle empty or unavailable tile renderers', async () => {
    vi.useFakeTimers();
    const tiles = new FakeTiles();
    const emptyResult = waitForTileDisplayReady(tiles, {
      stableMs: 200,
      pollMs: 50,
      timeoutMs: 500,
    });

    await vi.advanceTimersByTimeAsync(500);
    await expect(emptyResult).resolves.toBe(false);
    await expect(waitForTileDisplayReady(null)).resolves.toBe(false);
  });
});

describe('holdTileQueueUpdates', () => {
  it('freezes new tile work and resumes previously active queues once', () => {
    const scheduleDownload = vi.fn();
    const scheduleParse = vi.fn();
    const tiles = new FakeTiles();
    tiles.downloadQueue = {
      autoUpdate: true,
      running: true,
      scheduleJobRun: scheduleDownload,
    };
    tiles.parseQueue = {
      autoUpdate: false,
      running: true,
      scheduleJobRun: scheduleParse,
    };

    const release = holdTileQueueUpdates(tiles);
    expect(tiles.downloadQueue.autoUpdate).toBe(false);
    expect(tiles.parseQueue.autoUpdate).toBe(false);

    release();
    release();
    expect(tiles.downloadQueue.autoUpdate).toBe(true);
    expect(tiles.parseQueue.autoUpdate).toBe(false);
    expect(scheduleDownload).toHaveBeenCalledTimes(1);
    expect(scheduleParse).not.toHaveBeenCalled();
  });
});
