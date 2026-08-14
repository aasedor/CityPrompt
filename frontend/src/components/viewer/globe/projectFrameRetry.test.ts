import { describe, expect, it, vi } from 'vitest';

import {
  getFrameableProjectCoordinates,
  runProjectFrameRetry,
} from './projectFrameRetry';

describe('project camera frame retry', () => {
  it('waits through delayed camera readiness and then reapplies the pose', async () => {
    let ready = false;
    const frame = vi.fn(async () => true);
    const wait = vi.fn(async (delayMs: number) => {
      if (delayMs >= 330) ready = true;
    });

    await expect(runProjectFrameRetry({
      isReady: () => ready,
      isCancelled: () => false,
      frame,
      wait,
      offsetsMs: [0, 120, 450, 900],
    })).resolves.toBe(true);

    expect(frame).toHaveBeenCalledTimes(2);
    expect(wait).toHaveBeenCalledTimes(3);
  });

  it('reapplies after an initially successful frame so a late controls update cannot win', async () => {
    const frame = vi.fn(async () => true);

    await expect(runProjectFrameRetry({
      isReady: () => true,
      isCancelled: () => false,
      frame,
      wait: async () => undefined,
      offsetsMs: [0, 100, 400],
    })).resolves.toBe(true);

    expect(frame).toHaveBeenCalledTimes(3);
  });

  it('stops queued retries as soon as a real user interaction takes ownership', async () => {
    let cancelled = false;
    const frame = vi.fn(async () => true);

    const result = await runProjectFrameRetry({
      isReady: () => true,
      isCancelled: () => cancelled,
      frame,
      wait: async () => { cancelled = true; },
      offsetsMs: [0, 100, 400],
    });

    expect(result).toBe(true);
    expect(frame).toHaveBeenCalledTimes(1);
  });
});

describe('project frame coordinates', () => {
  it('becomes frameable when asynchronously loaded zones arrive', () => {
    expect(getFrameableProjectCoordinates([])).toEqual([]);
    expect(getFrameableProjectCoordinates([
      { coordinates: [[-114.1, 51.0], [-114.09, 51.0]] },
      {
        coordinates: [
          [-114.118, 51.027],
          [-114.117, 51.027],
          [-114.117, 51.026],
          [-114.118, 51.027],
        ],
      },
    ])).toEqual([
      [-114.118, 51.027],
      [-114.117, 51.027],
      [-114.117, 51.026],
      [-114.118, 51.027],
    ]);
  });
});
