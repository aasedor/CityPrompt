import { describe, expect, it } from 'vitest';
import {
  fitTerrainContactPlane,
  resolveFoundationContactProfile,
  resolveTerrainContactElevation,
  samplePlaneOffset,
  type TerrainContactSample,
} from './terrainContactProfile';

function elevationAt(
  plane: NonNullable<ReturnType<typeof fitTerrainContactPlane>>,
  x: number,
  y: number,
): number {
  return plane.originZ + samplePlaneOffset(plane, x, y);
}

describe('fitTerrainContactPlane', () => {
  it('fits a flat terrain contact without introducing drift', () => {
    const plane = fitTerrainContactPlane([
      { x: -5, y: -5, z: 1025.4 },
      { x: 5, y: -5, z: 1025.4 },
      { x: 5, y: 5, z: 1025.4 },
      { x: -5, y: 5, z: 1025.4 },
      { x: 0, y: 0, z: 1025.4 },
    ]);

    expect(plane).not.toBeNull();
    expect(plane?.kind).toBe('least_squares');
    expect(plane?.slopeX).toBeCloseTo(0, 10);
    expect(plane?.slopeY).toBeCloseTo(0, 10);
    expect(elevationAt(plane!, 17, -23)).toBeCloseTo(1025.4, 8);
    expect(plane?.rmsResidualMeters).toBeCloseTo(0, 10);
  });

  it('preserves a real cross-slope and interpolates in local ENU metres', () => {
    const samples: TerrainContactSample[] = [];
    for (const x of [-10, 0, 10]) {
      for (const y of [-8, 8]) {
        samples.push({ x, y, z: 100 + x * 0.08 - y * 0.035 });
      }
    }

    const plane = fitTerrainContactPlane(samples);

    expect(plane?.kind).toBe('least_squares');
    expect(plane?.slopeX).toBeCloseTo(0.08, 8);
    expect(plane?.slopeY).toBeCloseTo(-0.035, 8);
    expect(elevationAt(plane!, 7.5, -3)).toBeCloseTo(100.705, 8);
  });

  it('deterministically rejects a high roof/canopy hit before least-squares refinement', () => {
    const ground: TerrainContactSample[] = [
      { x: -10, y: -10, z: 98.5 },
      { x: 0, y: -10, z: 99 },
      { x: 10, y: -10, z: 99.5 },
      { x: -10, y: 0, z: 99.5 },
      { x: 0, y: 0, z: 100 },
      { x: 10, y: 0, z: 100.5 },
      { x: -10, y: 10, z: 100.5 },
      { x: 10, y: 10, z: 101.5 },
    ];
    const canopy = { x: 3, y: 4, z: 118 };

    const first = fitTerrainContactPlane([...ground, canopy]);
    const second = fitTerrainContactPlane([...ground, canopy]);

    expect(first).toEqual(second);
    expect(first?.kind).toBe('least_squares');
    expect(first?.sampleCount).toBe(9);
    expect(first?.inlierCount).toBe(8);
    expect(first?.slopeX).toBeCloseTo(0.05, 8);
    expect(first?.slopeY).toBeCloseTo(0.1, 8);
    expect(elevationAt(first!, 3, 4)).toBeCloseTo(100.55, 8);
  });

  it('uses a flat explicit fallback for missing samples', () => {
    expect(fitTerrainContactPlane([])).toBeNull();

    const plane = fitTerrainContactPlane([], { fallbackElevationMeters: 1042.25 });
    expect(plane).toMatchObject({
      kind: 'flat_fallback',
      originX: 0,
      originY: 0,
      originZ: 1042.25,
      slopeX: 0,
      slopeY: 0,
      sampleCount: 0,
      fitSampleCount: 0,
    });
  });

  it('falls back safely when probes are collinear and cannot define a plane', () => {
    const plane = fitTerrainContactPlane([
      { x: -10, y: 0, z: 99 },
      { x: 0, y: 0, z: 100 },
      { x: 10, y: 0, z: 101 },
      { x: 20, y: 0, z: 102 },
    ], { fallbackElevationMeters: 100.5 });

    expect(plane).toMatchObject({
      kind: 'flat_fallback',
      originX: 5,
      originY: 0,
      originZ: 100.5,
      slopeX: 0,
      slopeY: 0,
    });
    expect(samplePlaneOffset(plane, 200, 200)).toBe(0);
    expect(samplePlaneOffset(null, 1, 1)).toBe(0);
  });

  it('keeps ground relief but replaces isolated object-top and coarse-tile hits', () => {
    const plane = fitTerrainContactPlane([
      { x: -5, y: -5, z: 99.5 },
      { x: 5, y: -5, z: 100.5 },
      { x: 5, y: 5, z: 100.5 },
      { x: -5, y: 5, z: 99.5 },
    ])!;
    expect(resolveTerrainContactElevation(plane, 100.8, 0, 0)).toBe(100.8);
    expect(resolveTerrainContactElevation(plane, 115, 0, 0)).toBeCloseTo(100, 8);
    expect(resolveTerrainContactElevation(plane, 70, 0, 0)).toBeCloseTo(100, 8);
    expect(resolveTerrainContactElevation(plane, null, 4, 0)).toBeCloseTo(100.4, 8);
  });
});

describe('resolveFoundationContactProfile', () => {
  it('keeps the requested reveal on flat ground', () => {
    const profile = resolveFoundationContactProfile(
      [100, 100, null, Number.NaN, 100],
      { revealMeters: 0.2, maxSkirtHeightMeters: 3 },
    );

    expect(profile).toMatchObject({
      sampleCount: 3,
      lowGroundElevationMeters: 100,
      highGroundElevationMeters: 100,
      terrainReliefMeters: 0,
      foundationTopElevationMeters: 100.2,
      skirtBottomElevationMeters: 100,
      skirtHeightMeters: 0.2,
      requiredSkirtHeightMeters: 0.2,
      uncoveredReliefMeters: 0,
      revealMeters: 0.2,
      isSkirtCapped: false,
    });
  });

  it('reaches the low side of a normal cross-slope', () => {
    const profile = resolveFoundationContactProfile(
      [102, 100.5, 101.25, 100],
      { revealMeters: 0.25, maxSkirtHeightMeters: 4 },
    );

    expect(profile?.terrainReliefMeters).toBe(2);
    expect(profile?.foundationTopElevationMeters).toBe(102.25);
    expect(profile?.skirtBottomElevationMeters).toBe(100);
    expect(profile?.skirtHeightMeters).toBe(2.25);
    expect(profile?.isSkirtCapped).toBe(false);
  });

  it('caps an excessive skirt and reports the relief needing site treatment', () => {
    const profile = resolveFoundationContactProfile(
      [100, 102, 106, 110],
      { revealMeters: 0.2, maxSkirtHeightMeters: 3 },
    );

    expect(profile?.foundationTopElevationMeters).toBe(110.2);
    expect(profile?.requiredSkirtHeightMeters).toBeCloseTo(10.2, 8);
    expect(profile?.skirtHeightMeters).toBe(3);
    expect(profile?.skirtBottomElevationMeters).toBeCloseTo(107.2, 8);
    expect(profile?.uncoveredReliefMeters).toBeCloseTo(7.2, 8);
    expect(profile?.isSkirtCapped).toBe(true);
  });

  it('uses a stable fallback only when perimeter data is unavailable', () => {
    expect(resolveFoundationContactProfile([])).toBeNull();
    expect(resolveFoundationContactProfile([], { fallbackElevationMeters: 50 })).toMatchObject({
      sampleCount: 0,
      lowGroundElevationMeters: 50,
      highGroundElevationMeters: 50,
      foundationTopElevationMeters: 50.18,
    });
  });
});
