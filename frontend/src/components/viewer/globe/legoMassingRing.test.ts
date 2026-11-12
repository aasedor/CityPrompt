import { describe, expect, it } from 'vitest';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import {
  cleanRing, insetKitRing, insideKitRing, kitCourtyardAreaM2, kitCourtyardRing, kitRingArea, localKitRing,
} from './legoMassingRing';

const rectangle = (width: number, depth: number) => [[-width / 2, -depth / 2], [width / 2, -depth / 2], [width / 2, depth / 2], [-width / 2, depth / 2]];
const lShape = (width: number, depth: number, arm: number) => [[0, 0], [width, 0], [width, arm], [arm, arm], [arm, depth], [0, depth]];
const rounded = (ring: number[][] | null) => ring?.map(point => point.map(value => Math.round(value * 1000) / 1000));

describe('insetKitRing', () => {
  it('moves every wall of a rectangle inward and keeps each corner’s place in the ring', () => {
    expect(rounded(insetKitRing(rectangle(30, 24.4), 5.4))).toEqual([[-9.6, -6.8], [9.6, -6.8], [9.6, 6.8], [-9.6, 6.8]]);
  });

  it('follows an L shape round its inside corner', () => {
    const inset = insetKitRing(lShape(60, 46, 24), 5.4)!;
    expect(rounded(inset)).toEqual([[5.4, 5.4], [54.6, 5.4], [54.6, 18.6], [18.6, 18.6], [18.6, 40.6], [5.4, 40.6]]);
    expect(kitRingArea(inset)).toBeCloseTo(49.2 * 13.2 + 13.2 * 22, 6);
  });

  it('keeps every moved wall the full distance from every original wall', () => {
    const outline = [[-26, -18], [24, -20], [30, 6], [4, 22], [-24, 14]];
    const inset = insetKitRing(outline, 5.4)!;
    expect(inset).toHaveLength(5);
    for (const point of inset) expect(insideKitRing(outline, point[0], point[1], 5.4 - 1e-3)).toBe(true);
  });

  it('refuses an outline too thin for the distance, and a ring that is not counter-clockwise', () => {
    expect(insetKitRing(rectangle(80, 10), 5.4)).toBeNull();
    expect(insetKitRing(rectangle(10.8, 30), 5.4)).toBeNull();
    // Arms 9 m wide: the two wings of each arm would meet.
    expect(insetKitRing(lShape(50, 30, 9), 5.4)).toBeNull();
    expect(insetKitRing(rectangle(30, 24).reverse(), 5.4)).toBeNull();
    expect(insetKitRing(rectangle(30, 24), 0)).toBeNull();
    expect(insetKitRing([[0, 0], [10, 0]], 1)).toBeNull();
  });

  it('treats two walls in one straight line as one', () => {
    const withMidpoint = [[-15, -12], [0, -12], [15, -12], [15, 12], [-15, 12]];
    expect(rounded(insetKitRing(withMidpoint, 5))).toEqual([[-10, -7], [0, -7], [10, -7], [10, 7], [-10, 7]]);
  });
});

describe('kitCourtyardRing', () => {
  it('leaves a courtyard only where one of the minimum clear width fits', () => {
    expect(rounded(kitCourtyardRing(rectangle(30, 24.4), 5.4, 8))).toEqual([[-9.6, -6.8], [9.6, -6.8], [9.6, 6.8], [-9.6, 6.8]]);
    // 18.7 m deep leaves 7.9 m clear: just too narrow, so the block is solid.
    expect(kitCourtyardRing(rectangle(30, 18.7), 5.4, 8)).toBeNull();
    expect(kitCourtyardRing(rectangle(30, 18.9), 5.4, 8)).not.toBeNull();
    // An L with 15 m arms is a double-loaded bar, not a perimeter block.
    expect(kitCourtyardRing(lShape(50, 30, 15), 5.4, 8)).toBeNull();
    expect(kitCourtyardRing(lShape(60, 46, 24), 5.4, 8)).not.toBeNull();
  });
});

describe('outlines drawn in longitude and latitude', () => {
  const longitude = -114, latitude = 51;
  const ll = (x: number, y: number) => [longitude + x / metersPerDegLon(latitude), latitude + y / METERS_PER_DEG_LAT];
  const drawn = rectangle(30, 24.4).map(([x, y]) => ll(x, y));

  it('measures the courtyard a student’s outline leaves open', () => {
    expect(kitCourtyardAreaM2(drawn, 5.4, 8)).toBeCloseTo(19.2 * 13.6, 3);
    expect(kitCourtyardAreaM2([...drawn].reverse(), 5.4, 8)).toBeCloseTo(19.2 * 13.6, 3);
    expect(kitCourtyardAreaM2([...drawn, drawn[0]], 5.4, 8)).toBeCloseTo(19.2 * 13.6, 3);
    expect(kitCourtyardAreaM2(rectangle(18, 14).map(([x, y]) => ll(x, y)), 5.4, 8)).toBe(0);
    expect(kitCourtyardAreaM2(drawn.slice(0, 2), 5.4, 8)).toBe(0);
  });

  it('keeps the first drawn edge as the front whichever way the outline was drawn', () => {
    const clockwise = [drawn[0], drawn[3], drawn[2], drawn[1]];
    const local = localKitRing(cleanRing(clockwise), longitude, latitude)!;
    expect(kitRingArea(local)).toBeGreaterThan(0);
    // Wall 0 still joins the first two drawn corners.
    expect(rounded([local[0], local[1]])).toEqual([[-15, 12.2], [-15, -12.2]]);
    expect(localKitRing([[0, 0], [1, 1], [2, 2]], 0, 0)).toBeNull();
  });
});
