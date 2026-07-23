import { describe, expect, it } from 'vitest';
import { allSettledWithConcurrency } from './allSettledWithConcurrency';

describe('allSettledWithConcurrency', () => {
  it('preserves input order while respecting the active-worker limit', async () => {
    let active = 0;
    let peakActive = 0;
    const release: Array<() => void> = [];
    const gate = () => new Promise<void>((resolve) => release.push(resolve));

    const pending = allSettledWithConcurrency(
      [0, 1, 2, 3, 4],
      async (value) => {
        active += 1;
        peakActive = Math.max(peakActive, active);
        await gate();
        active -= 1;
        return value * 2;
      },
      2,
    );

    await Promise.resolve();
    expect(active).toBe(2);
    release.shift()?.();
    release.shift()?.();
    await Promise.resolve();
    await Promise.resolve();
    release.splice(0).forEach((resolve) => resolve());
    await Promise.resolve();
    release.splice(0).forEach((resolve) => resolve());
    await Promise.resolve();
    release.splice(0).forEach((resolve) => resolve());

    const results = await pending;
    expect(peakActive).toBe(2);
    expect(results).toEqual([
      { status: 'fulfilled', value: 0 },
      { status: 'fulfilled', value: 2 },
      { status: 'fulfilled', value: 4 },
      { status: 'fulfilled', value: 6 },
      { status: 'fulfilled', value: 8 },
    ]);
  });

  it('captures failures without preventing later work', async () => {
    const results = await allSettledWithConcurrency(
      ['ok', 'bad', 'later'],
      async (value) => {
        if (value === 'bad') throw new Error('no family');
        return value.toUpperCase();
      },
      2,
    );

    expect(results[0]).toEqual({ status: 'fulfilled', value: 'OK' });
    expect(results[1].status).toBe('rejected');
    expect(results[2]).toEqual({ status: 'fulfilled', value: 'LATER' });
  });
});
