import { expect, it } from 'vitest';
import { computeFootprintFrame } from '@/components/viewer/globe/buildingPlacement';
import { assemblyFootprintCoordinates, authoredHomePlotFrame, detachedPlotCoordinates, isDetachedArchetype, preservesAuthoredPlotAxes } from './detachedPlot';
import { rectangleAt } from '@/features/pickPlace/geometry';

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

it('provides the actual concave footprint to non-detached clay plans too', () => {
  const ring = [[-114, 51], [-113.999, 51], [-113.999, 51.0002], [-113.9996, 51.0002], [-113.9996, 51.0005], [-114, 51.0005]];
  const target = { width_m: 70, depth_m: 56 };
  const local = assemblyFootprintCoordinates([...ring, ring[0]], target);
  expect(local).toHaveLength(6);
  expect(local).toEqual(detachedPlotCoordinates('vancouver_laneway_house', ring, target));
  expect(assemblyFootprintCoordinates([[NaN, 51], ...ring], target)).toBeUndefined();
  expect(assemblyFootprintCoordinates(undefined, target)).toBeUndefined();
});

it('keeps the chosen frontage through aspect-ratio changes and a full turn', () => {
  for (const width of [12, 16, 36]) for (const degrees of [0, 15, 90, 135, 180, 270]) {
    const ring = rectangleAt([-114, 51], width, 16, degrees);
    const frame = authoredHomePlotFrame(ring)!;
    expect(frame.width_m).toBe(width);
    expect(frame.depth_m).toBe(16);
    expect(Math.cos(frame.yawRad)).toBeCloseTo(Math.cos(degrees*Math.PI/180), 8);
    const local = assemblyFootprintCoordinates(ring, frame, true)!;
    expect(local[0][0]).toBeCloseTo(-width/2, 4);
    expect(local[0][1]).toBeCloseTo(8, 4);
    expect(local[1][0]).toBeCloseTo(width/2, 4);
    expect(local[1][1]).toBeCloseTo(8, 4);
  }
});

it('preserves landmark frontage independently of the detached-home repeat contract', () => {
  const properties = { native_plot_axes: true };
  expect(preservesAuthoredPlotAxes(properties)).toBe(true);
  expect(preservesAuthoredPlotAxes({ native_home_plot: true })).toBe(true);
  expect(preservesAuthoredPlotAxes({ native_plot_axes: false })).toBe(false);
  const first = authoredHomePlotFrame(rectangleAt([-114,51],29,42,25))!;
  const flipped = authoredHomePlotFrame(rectangleAt([-114,51],29,42,205))!;
  expect(Math.cos(flipped.yawRad-first.yawRad)).toBeCloseTo(-1, 8);
  expect(flipped.width_m).toBe(29);
  expect(flipped.depth_m).toBe(42);
});
