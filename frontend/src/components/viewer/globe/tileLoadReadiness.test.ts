import { afterEach, describe, expect, it, vi } from 'vitest';

import { type SceneTileRenderer, waitForTilesSettled } from './tileLoadReadiness';

class FakeTiles implements SceneTileRenderer {
  isLoading = false;

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
