import { expect, it } from 'vitest';
import { createStreetGroundRetry } from './streetGroundRetry';

it('recovers from coarse startup geometry only after replacement tiles settle', () => {
  const retry = createStreetGroundRetry();
  const coarse = {}, detailed = {};
  retry.failed([coarse]);
  expect(retry.shouldRetry([coarse], 5000)).toBe(false);
  expect(retry.shouldRetry([], 5000)).toBe(false);
  expect(retry.shouldRetry([detailed], 5000)).toBe(false);
  expect(retry.shouldRetry([detailed], 5899)).toBe(false);
  expect(retry.shouldRetry([detailed], 5900)).toBe(true);
  expect(retry.shouldRetry([detailed], 9000)).toBe(false);
});

it('restarts the settling window if the replacement coverage disappears', () => {
  const retry = createStreetGroundRetry();
  const detailed = {};
  retry.failed([{}]);
  retry.shouldRetry([detailed], 0);
  expect(retry.shouldRetry([], 800)).toBe(false);
  expect(retry.shouldRetry([detailed], 1000)).toBe(false);
  expect(retry.shouldRetry([detailed], 1900)).toBe(true);
});

it('bounds repeat failures even while tile coverage keeps changing', () => {
  const retry = createStreetGroundRetry();
  for (let n = 0; n < 3; n++) {
    retry.failed([{}]);
    const next = {};
    expect(retry.shouldRetry([next], n * 2000)).toBe(false);
    expect(retry.shouldRetry([next], n * 2000 + 900)).toBe(n < 2);
  }
});
