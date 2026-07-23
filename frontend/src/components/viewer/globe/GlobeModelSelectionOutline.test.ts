import { describe, expect, it } from 'vitest';
import { computeFootprintFrame } from './buildingPlacement';
import { buildModelSelectionOutlinePoints } from './GlobeModelSelectionOutline';

describe('buildModelSelectionOutlinePoints', () => {
  it('closes the footprint ring and raises it above the terrain', () => {
    const ring = [[-114, 51], [-113.9999, 51], [-113.9999, 51.0001], [-114, 51.0001]];
    const frame = computeFootprintFrame(ring)!;
    const points = buildModelSelectionOutlinePoints(ring, frame);

    expect(points).toHaveLength(ring.length + 1);
    expect(points[0].equals(points[points.length - 1])).toBe(true);
    expect(points.every((point) => point.z === 0.24)).toBe(true);
  });
});
