import { describe, expect, it } from 'vitest';
import { computeFootprintFrame, computeModelPlacement } from './buildingPlacement';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

// Build a WGS84 rectangle w×d meters centered at (lng, lat), rotated by
// bearingDeg CCW from East — the inverse of what computeFootprintFrame does.
function rectRing(
  lng: number, lat: number, w: number, d: number, bearingDeg = 0,
): number[][] {
  const mLon = metersPerDegLon(lat);
  const theta = (bearingDeg * Math.PI) / 180;
  const corners: Array<[number, number]> = [
    [-w / 2, -d / 2], [w / 2, -d / 2], [w / 2, d / 2], [-w / 2, d / 2],
  ];
  return corners.map(([u, v]) => {
    const x = u * Math.cos(theta) - v * Math.sin(theta);
    const y = u * Math.sin(theta) + v * Math.cos(theta);
    return [lng + x / mLon, lat + y / METERS_PER_DEG_LAT];
  });
}

const CALGARY = { lng: -114.085, lat: 51.0405 };

describe('computeFootprintFrame', () => {
  it('recovers dimensions and axis bearing of a known rectangle', () => {
    const frame = computeFootprintFrame(rectRing(CALGARY.lng, CALGARY.lat, 40, 20, 30));
    expect(frame).not.toBeNull();
    expect(frame!.longDim).toBeCloseTo(40, 0);
    expect(frame!.shortDim).toBeCloseTo(20, 0);
    expect(frame!.bearingRad).toBeCloseTo((30 * Math.PI) / 180, 2);
    // Symmetric rectangle: oriented-rect center coincides with vertex centroid.
    expect(frame!.rectCenterLocal[0]).toBeCloseTo(0, 1);
    expect(frame!.rectCenterLocal[1]).toBeCloseTo(0, 1);
  });

  it('folds the bearing to an axis (a rectangle at 120° reads as 30°... folded)', () => {
    const frame = computeFootprintFrame(rectRing(CALGARY.lng, CALGARY.lat, 40, 20, 120));
    // 120° folded to [-90°, 90°) is -60°.
    expect(frame!.bearingRad).toBeCloseTo((-60 * Math.PI) / 180, 2);
    expect(frame!.longDim).toBeCloseTo(40, 0);
  });

  it('returns null on degenerate input', () => {
    expect(computeFootprintFrame([])).toBeNull();
    expect(computeFootprintFrame([[0, 0], [1, 1]])).toBeNull();
    // Sub-meter sliver.
    expect(computeFootprintFrame(rectRing(CALGARY.lng, CALGARY.lat, 0.5, 0.2))).toBeNull();
  });

  it('is deterministic', () => {
    const ring = rectRing(CALGARY.lng, CALGARY.lat, 33, 17, 12);
    expect(computeFootprintFrame(ring)).toEqual(computeFootprintFrame(ring));
  });
});

describe('computeModelPlacement', () => {
  const frame = computeFootprintFrame(rectRing(CALGARY.lng, CALGARY.lat, 40, 20, 0))!;

  it('contain-fits: scaled model never exceeds either footprint dimension', () => {
    // Model 8 long (x) × 2 wide (z): long-axis ratio 5, short-axis ratio 10 → 5 wins.
    const placement = computeModelPlacement(frame, { x: 8, y: 3, z: 2 }, undefined, 0)!;
    expect(placement.scale).toBeCloseTo(5, 5);
    expect(placement.scale * 8).toBeLessThanOrEqual(40 + 1e-6);
    expect(placement.scale * 2).toBeLessThanOrEqual(20 + 1e-6);
  });

  it('short-axis constraint wins when the model is squatter than the parcel', () => {
    // Model 4×4 footprint: long ratio 10, short ratio 5 → 5.
    const placement = computeModelPlacement(frame, { x: 4, y: 3, z: 4 }, undefined, 0)!;
    expect(placement.scale).toBeCloseTo(5, 5);
  });

  it('aligns the model long axis with the footprint, whichever model axis is longer', () => {
    // Long axis on model X → no correction.
    const px = computeModelPlacement(frame, { x: 8, y: 3, z: 2 }, undefined, 0)!;
    expect(px.yawRad).toBeCloseTo(frame.bearingRad, 5);
    // Long axis on model Z → +90° correction.
    const pz = computeModelPlacement(frame, { x: 2, y: 3, z: 8 }, undefined, 0)!;
    expect(pz.yawRad).toBeCloseTo(frame.bearingRad + Math.PI / 2, 5);
  });

  it('applies rotation_degrees as an additional CCW yaw', () => {
    const p0 = computeModelPlacement(frame, { x: 8, y: 3, z: 2 }, undefined, 0)!;
    const p90 = computeModelPlacement(frame, { x: 8, y: 3, z: 2 }, undefined, 90)!;
    expect(p90.yawRad - p0.yawRad).toBeCloseTo(Math.PI / 2, 5);
  });

  it('anchors scale to target height when the parcel allows it', () => {
    // heightFit = 12/3 = 4 < containFit 5 → height wins; exact target height.
    const placement = computeModelPlacement(frame, { x: 8, y: 3, z: 2 }, 12, 0)!;
    expect(placement.scale).toBeCloseTo(4, 5);
    expect(placement.heightWarning).toBe(false);
  });

  it('clamps to contain-fit when reaching target height would overflow the parcel', () => {
    // heightFit = 30/3 = 10, containFit 5 → parcel clamp wins; model ends up
    // at half the target height → warning fires (undershoot only, by design).
    const placement = computeModelPlacement(frame, { x: 8, y: 3, z: 2 }, 30, 0)!;
    expect(placement.scale).toBeCloseTo(5, 5);
    expect(placement.heightWarning).toBe(true);
  });

  it('regression: same-block siblings land at a uniform height (measured live data)', () => {
    // Building C, 2026-07-11: model 1.90×1.06×1.20 on a 28.6×16.9 m parcel,
    // target 9.6 m. Pure contain-fit gave scale 14.1 → a 14.9 m giant next to
    // a 9.3 m sibling ("miniature" report). Height anchor: scale ≈ 9.06.
    const parcelC = computeFootprintFrame(rectRing(CALGARY.lng, CALGARY.lat, 28.6, 16.9, 0))!;
    const placement = computeModelPlacement(parcelC, { x: 1.9, y: 1.06, z: 1.2 }, 9.6, 0)!;
    expect(placement.scale).toBeCloseTo(9.6 / 1.06, 2);
    expect(placement.scale * 1.06).toBeCloseTo(9.6, 2);
    expect(placement.heightWarning).toBe(false);
  });

  it('returns null for a degenerate model', () => {
    expect(computeModelPlacement(frame, { x: 0, y: 3, z: 0 }, undefined, 0)).toBeNull();
  });
});
