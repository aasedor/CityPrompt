import { describe, expect, it } from 'vitest';

import { inverseDepthValue, videoDepthWindow } from './videoDepthWindow';

describe('videoDepthWindow', () => {
  it('centres an aerial window on the route distance', () => {
    const window = videoDepthWindow('path_follow', 400);
    expect(window).toEqual({ nearMeters: 140, farMeters: 2000 });
    expect(inverseDepthValue(window, 140)).toBe(1);
    expect(inverseDepthValue(window, 2000)).toBe(0);
    // The site itself sits in the readable middle of the range.
    const site = inverseDepthValue(window, 400);
    expect(site).toBeGreaterThan(0.25);
    expect(site).toBeLessThan(0.4);
  });

  it('clamps extreme aerial distances and keeps far beyond near', () => {
    expect(videoDepthWindow('path_follow', 2)).toEqual({ nearMeters: 3, farMeters: 200 });
    const far = videoDepthWindow('path_follow', 5000);
    expect(far.nearMeters).toBe(300);
    expect(far.farMeters).toBe(8000);
    expect(videoDepthWindow('path_follow', Number.NaN).farMeters).toBeGreaterThan(
      videoDepthWindow('path_follow', Number.NaN).nearMeters,
    );
  });

  it('uses a fixed pedestrian window for near-field routes', () => {
    expect(videoDepthWindow('street_walkby', 400)).toEqual({ nearMeters: 2, farMeters: 400 });
    expect(videoDepthWindow('detail_flythrough', 12)).toEqual({ nearMeters: 2, farMeters: 400 });
  });

  it('is monotonic: nearer surfaces are always brighter', () => {
    const window = videoDepthWindow('street_walkby', 0);
    const values = [1, 2, 5, 10, 20, 50, 100, 400, 1000].map((distance) => inverseDepthValue(window, distance));
    for (let index = 1; index < values.length; index += 1) {
      expect(values[index]).toBeLessThanOrEqual(values[index - 1]);
    }
    expect(values[0]).toBe(1);
    expect(values[values.length - 1]).toBe(0);
  });
});
