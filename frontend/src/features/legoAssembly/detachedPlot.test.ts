import { expect, it } from 'vitest';
import { computeFootprintFrame } from '@/components/viewer/globe/buildingPlacement';
import { detachedPlotCoordinates, isDetachedArchetype } from './detachedPlot';

it('retains a rotated concave plot in the actual globe instance frame', () => {
  const angle = 0.46;
  const ring = [[-60, -30], [60, -30], [60, 0], [0, 0], [0, 30], [-60, 30]].map(([x, y]) => {
    const e = x * Math.cos(angle) - y * Math.sin(angle); const n = x * Math.sin(angle) + y * Math.cos(angle);
    return [-114 + e / (111320 * Math.cos(51 * Math.PI / 180)), 51 + n / 111320];
  });
  const local = detachedPlotCoordinates('calgary_inner_city_bungalow', [...ring, ring[0]], { width_m: 120, depth_m: 60 })!;
  expect(local).toHaveLength(6);
  const frame = computeFootprintFrame(ring)!;
  local.forEach(([x, y], index) => {
    const e = x * Math.cos(frame.bearingRad) + y * Math.sin(frame.bearingRad) + frame.rectCenterLocal[0];
    const n = x * Math.sin(frame.bearingRad) - y * Math.cos(frame.bearingRad) + frame.rectCenterLocal[1];
    expect(frame.centroidLng + e / (111320 * Math.cos(frame.centroidLat * Math.PI / 180))).toBeCloseTo(ring[index][0], 9);
    expect(frame.centroidLat + n / 111320).toBeCloseTo(ring[index][1], 9);
  });
});
it('only enables dwelling lots for known detached families and their exact variants', () => {
  expect(isDetachedArchetype('vancouver_laneway_house_variant_3')).toBe(true);
  expect(isDetachedArchetype('urban_skyscraper')).toBe(false);
  expect(detachedPlotCoordinates('urban_skyscraper', [[0, 0], [1, 0], [1, 1]], { width_m: 100, depth_m: 100 })).toBeUndefined();
});
