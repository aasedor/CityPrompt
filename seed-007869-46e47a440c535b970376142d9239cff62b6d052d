import { describe, expect, it } from 'vitest';
import type { FootprintCompatibility } from '@/components/viewer/aestheticCatalog';
import { analyzeLegoFootprint } from './footprintProfiles';

const compatibility: FootprintCompatibility = {
  preferredProfiles: ['rectangle', 'l_shape', 'u_shape', 'courtyard'],
  recommendedWidth_m: [24, 42],
  recommendedDepth_m: [16, 30],
  recommendedFloors: [5, 7],
  wingDepth_m: [8, 12],
};

function geographic(points: Array<[number, number]>): number[][] {
  return points.map(([x, y]) => [x / 111320, y / 110540]);
}

describe('analyzeLegoFootprint', () => {
  it('measures a rotated/closed rectangle in metres', () => {
    const result = analyzeLegoFootprint(geographic([
      [-15, -10], [15, -10], [15, 10], [-15, 10], [-15, -10],
    ]), compatibility);
    expect(result?.profile).toBe('rectangle');
    expect(result?.width_m).toBeCloseTo(30, 0);
    expect(result?.depth_m).toBeCloseTo(20, 0);
    expect(result?.within_recommended_size).toBe(true);
  });

  it('recognizes an L-shaped parcel and supplies the archetype wing depth', () => {
    const result = analyzeLegoFootprint(geographic([
      [-18, -14], [18, -14], [18, -4], [-8, -4], [-8, 14], [-18, 14],
    ]), compatibility);
    expect(result?.profile).toBe('l_shape');
    expect(result?.concave_vertices).toBe(1);
    expect(result?.wing_depth_m).toBe(10);
  });

  it('recognizes a U-shaped parcel from its two re-entrant corners', () => {
    const result = analyzeLegoFootprint(geographic([
      [-20, -15], [20, -15], [20, 15], [10, 15], [10, -4],
      [-10, -4], [-10, 15], [-20, 15],
    ]), compatibility);
    expect(result?.profile).toBe('u_shape');
    expect(result?.concave_vertices).toBe(2);
  });

  it('uses profile-specific fit guidance instead of one rectangular size envelope', () => {
    const result = analyzeLegoFootprint(geographic([
      [-18, -14], [18, -14], [18, -4], [-8, -4], [-8, 14], [-18, 14],
    ]), {
      ...compatibility,
      profiles: {
        l_shape: {
          recommendedWidth_m: [32, 40],
          recommendedDepth_m: [24, 30],
          recommendedFloors: [5, 7],
          wingDepth_m: [9, 11],
        },
      },
    });
    expect(result?.profile).toBe('l_shape');
    expect(result?.within_recommended_size).toBe(true);
    expect(result?.wing_depth_m).toBe(10);
  });
});
