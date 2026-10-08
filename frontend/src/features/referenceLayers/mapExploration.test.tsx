import { act, renderHook } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { explorationArea, useMapExploration } from './useMapExploration';

afterEach(() => vi.useRealTimers());
it('uses a bounded neighbourhood around the location and rejects invalid centres', () => {
  const ring = explorationArea({ lng: -114.1, lat: 51.05 });
  expect(ring).toHaveLength(4);
  expect(ring[0][0]).toBeLessThan(-114.1);
  expect(ring[2][1]).toBeGreaterThan(51.05);
  expect(explorationArea({ lng: NaN, lat: 51 })).toEqual([]);
});
it('updates only after the camera settles and clears the prior project location', () => {
  vi.useFakeTimers();
  let centre = { lng: -114.1, lat: 51.05 };
  const read = () => centre;
  const { result, rerender } = renderHook(({ id, reader }) => useMapExploration(id, reader, -114.1, 51.05),
    { initialProps: { id: 'one', reader: read as typeof read | undefined } });
  const original = result.current;
  centre = { lng: -114.15, lat: 51.06 };
  act(() => vi.advanceTimersByTime(750));
  expect(result.current).toEqual(original);
  act(() => vi.advanceTimersByTime(750));
  expect(result.current).not.toEqual(original);
  rerender({ id: 'two', reader: undefined });
  expect(result.current).toEqual(original);
});
