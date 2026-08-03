import { describe, expect, it } from 'vitest';

import {
  DEFAULT_VIDEO_ROUTE,
  DEFAULT_STREET_VIDEO_ROUTE,
  appendRoutePoint,
  normalizedRoutePoint,
  resampleRoute,
  routeSignature,
  routeSvgPoints,
} from './videoRenderPath';

describe('videoRenderPath', () => {
  it('normalizes and clamps pointer coordinates', () => {
    const rect = { left: 100, top: 50, width: 400, height: 200 } as DOMRect;
    expect(normalizedRoutePoint(300, 150, rect)).toEqual({ x: 0.5, y: 0.5 });
    expect(normalizedRoutePoint(10, 900, rect)).toEqual({ x: 0, y: 1 });
  });

  it('drops noisy pointer samples that are too close together', () => {
    const start = [{ x: 0.5, y: 0.8 }];
    expect(appendRoutePoint(start, { x: 0.505, y: 0.805 })).toBe(start);
    expect(appendRoutePoint(start, { x: 0.5, y: 0.6 })).toHaveLength(2);
  });

  it('resamples long routes while preserving endpoints', () => {
    const route = Array.from({ length: 40 }, (_, index) => ({ x: index / 39, y: 1 - index / 39 }));
    const sampled = resampleRoute(route, 12);
    expect(sampled).toHaveLength(12);
    expect(sampled[0]).toEqual(route[0]);
    expect(sampled[sampled.length - 1]).toEqual(route[route.length - 1]);
  });

  it('creates stable API signatures and SVG coordinates', () => {
    const route = [{ x: 0.123456, y: 0.75 }, { x: 1, y: 0 }];
    expect(routeSignature(route)).toBe('0.1235,0.7500|1.0000,0.0000');
    expect(routeSvgPoints(route)).toBe('12.35,75.00 100.00,0.00');
  });

  it('keeps the default flight short enough for the continuity-first pilot', () => {
    const distance = DEFAULT_VIDEO_ROUTE.slice(1).reduce((total, point, index) => {
      const previous = DEFAULT_VIDEO_ROUTE[index];
      return total + Math.hypot(point.x - previous.x, point.y - previous.y);
    }, 0);

    expect(distance).toBeLessThanOrEqual(0.05);
    expect(DEFAULT_VIDEO_ROUTE.every(({ x, y }) => x >= 0.4 && x <= 0.6 && y >= 0.4 && y <= 0.9)).toBe(true);
  });

  it('keeps the street walk-by short and near pedestrian eye-line', () => {
    expect(DEFAULT_STREET_VIDEO_ROUTE[0].x).toBeLessThan(DEFAULT_STREET_VIDEO_ROUTE[DEFAULT_STREET_VIDEO_ROUTE.length - 1].x);
    expect(DEFAULT_STREET_VIDEO_ROUTE.every(({ y }) => y >= 0.6 && y <= 0.7)).toBe(true);
  });
});
