import { describe, expect, it } from 'vitest';

import {
  buildCurbBandGeometry,
  applyTerrainPlaneToStreetGeometry,
  buildAccessibleFourWayIntersectionGeometry,
  buildOffsetCurbGeometry,
  buildDashGeometry,
  buildRibbonBandGeometry,
  buildRoundaboutGeometry,
  densifyPolyline,
  streetStationElevationAt,
} from './streetMesh3D';
import { ROUNDABOUT_PARAMS, STREET_DETAIL_3D } from '@/data/streetGeometryParams';
import {
  PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS,
  PUBLIC_REALM_STREET_MARKING_LIFT_METERS,
  PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS,
} from './publicRealmDepthPolicy';

const line100 = [
  { x: 0, y: 0 },
  { x: 100, y: 0 },
];

function zRange(geo: THREE.BufferGeometry | null): [number, number] {
  const pos = geo!.getAttribute('position');
  let min = Infinity;
  let max = -Infinity;
  for (let i = 0; i < pos.count; i++) {
    min = Math.min(min, pos.getZ(i));
    max = Math.max(max, pos.getZ(i));
  }
  return [min, max];
}

import type * as THREE from 'three';

describe('densifyPolyline', () => {
  it('splits long spans at the station step', () => {
    const out = densifyPolyline(line100, 4);
    expect(out.length).toBe(26); // 0..100 every 4m
    expect(out[0]).toEqual({ x: 0, y: 0 });
    expect(out[out.length - 1]).toEqual({ x: 100, y: 0 });
  });

  it('leaves short segments alone', () => {
    expect(densifyPolyline([{ x: 0, y: 0 }, { x: 2, y: 0 }], 4).length).toBe(2);
  });
});

describe('buildCurbBandGeometry', () => {
  it('builds prisms on both edges with curb-height tops', () => {
    const geo = buildCurbBandGeometry(line100, 5);
    expect(geo).not.toBeNull();
    const [zMin, zMax] = zRange(geo);
    expect(zMin).toBeCloseTo(PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS, 5);
    expect(zMax).toBeCloseTo(
      PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS + STREET_DETAIL_3D.curbHeight_m,
      5,
    );

    // 2 sides x stations x 4 cross-section verts
    const pos = geo!.getAttribute('position');
    expect(pos.count).toBe(2 * line100.length * 4);

    // outer edges sit at ±halfWidth, inner at ±(halfWidth - curbWidth)
    let maxY = -Infinity;
    for (let i = 0; i < pos.count; i++) maxY = Math.max(maxY, pos.getY(i));
    expect(maxY).toBeCloseTo(5, 5);
  });

  it('returns null for degenerate input', () => {
    expect(buildCurbBandGeometry([{ x: 0, y: 0 }], 5)).toBeNull();
  });
});

describe('buildDashGeometry', () => {
  it('emits the expected dash count for a 100m line', () => {
    const geo = buildDashGeometry(line100);
    // dashes start at 0,6,12,...,96 -> 17 dashes, 4 verts each
    expect(geo!.getAttribute('position').count).toBe(17 * 4);
    const [zMin] = zRange(geo);
    expect(zMin).toBeCloseTo(STREET_DETAIL_3D.dashLift_m, 5);
  });

  it('offsets markings from the road centerline', () => {
    const geo = buildDashGeometry(line100, undefined, undefined, 2)!;
    const pos = geo.getAttribute('position');
    let minY = Infinity;
    let maxY = -Infinity;
    for (let i = 0; i < pos.count; i++) {
      minY = Math.min(minY, pos.getY(i));
      maxY = Math.max(maxY, pos.getY(i));
    }
    expect(minY).toBeGreaterThan(1.8);
    expect(maxY).toBeLessThan(2.2);
  });
});

describe('buildOffsetCurbGeometry', () => {
  it('places detailed-section curbs at authored internal offsets', () => {
    const geometry = buildOffsetCurbGeometry(line100, [-3, 4]);
    expect(geometry).not.toBeNull();
    const position = geometry!.getAttribute('position');
    const ys = Array.from({ length: position.count }, (_, index) => position.getY(index));
    expect(Math.min(...ys)).toBeCloseTo(-3 - STREET_DETAIL_3D.curbWidth_m / 2, 5);
    expect(Math.max(...ys)).toBeCloseTo(4 + STREET_DETAIL_3D.curbWidth_m / 2, 5);
    geometry!.dispose();
  });

  it('leaves graph-owned curb-ramp gaps at skipped intersection stations', () => {
    const full = buildOffsetCurbGeometry(line100, [-3, 3])!;
    const withGap = buildOffsetCurbGeometry(line100, [-3, 3], undefined, undefined, [true, false])!;
    expect(withGap.getIndex()?.count).toBeLessThan(full.getIndex()?.count ?? 0);
    expect(withGap.getIndex()?.count).toBe(0);
    full.dispose();
    withGap.dispose();
  });
});

describe('buildRibbonBandGeometry', () => {
  it('builds an offset band that follows station elevations', () => {
    const geo = buildRibbonBandGeometry(line100, -2, 3, 0.2, [1, 2])!;
    const pos = geo.getAttribute('position');
    expect(pos.count).toBe(4);

    let minY = Infinity;
    let maxY = -Infinity;
    for (let i = 0; i < pos.count; i++) {
      minY = Math.min(minY, pos.getY(i));
      maxY = Math.max(maxY, pos.getY(i));
    }
    expect(minY).toBeCloseTo(-2);
    expect(maxY).toBeCloseTo(3);
    expect(pos.getZ(0)).toBeCloseTo(1.2);
    expect(pos.getZ(2)).toBeCloseTo(2.2);
  });
});

describe('buildAccessibleFourWayIntersectionGeometry', () => {
  it('builds four zebra crossings and eight directional curb-ramp/tactile pairs', () => {
    const geometry = buildAccessibleFourWayIntersectionGeometry(0, Math.PI / 2, 11, 7)!;
    expect(geometry).not.toBeNull();
    expect(geometry.crosswalks.getAttribute('position').count).toBe(2 * 2 * 7 * 4);
    expect(geometry.curbRamps.getAttribute('position').count).toBe(8 * 8);
    expect(geometry.tactilePads.getAttribute('position').count).toBe(8 * 4);
    expect(zRange(geometry.curbRamps)[0]).toBeCloseTo(PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS, 5);
    expect(zRange(geometry.curbRamps)[1]).toBeCloseTo(PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS, 5);
    expect(zRange(geometry.crosswalks)[0]).toBeCloseTo(
      PUBLIC_REALM_STREET_MARKING_LIFT_METERS,
      6,
    );
    expect(zRange(geometry.crosswalks)[1]).toBeCloseTo(
      PUBLIC_REALM_STREET_MARKING_LIFT_METERS,
      6,
    );
    geometry.crosswalks.dispose();
    geometry.curbRamps.dispose();
    geometry.tactilePads.dispose();
  });

  it('drapes a node assembly onto one terrain plane without changing its authored separation', () => {
    const road = buildRibbonBandGeometry(line100, -2, 2, 0.1)!;
    const before = zRange(road);
    applyTerrainPlaneToStreetGeometry(road, {
      originX: 0,
      originY: 0,
      originZ: 100,
      slopeX: 0.02,
      slopeY: 0.1,
      kind: 'least_squares',
      sampleCount: 5,
      fitSampleCount: 5,
      inlierCount: 5,
      rmsResidualMeters: 0,
      maxResidualMeters: 0,
    }, 100);
    const position = road.getAttribute('position');
    expect(position.getZ(0)).toBeCloseTo(before[0] - 0.2, 6);
    expect(position.getZ(1)).toBeCloseTo(before[1] + 0.2, 6);
    expect(position.getZ(2)).toBeCloseTo(before[0] + 2 - 0.2, 6);
    road.dispose();
  });

  it('rejects implausibly narrow or invalid graph nodes', () => {
    expect(buildAccessibleFourWayIntersectionGeometry(0, Math.PI / 2, 1, 7)).toBeNull();
    expect(buildAccessibleFourWayIntersectionGeometry(Number.NaN, Math.PI / 2, 7, 7)).toBeNull();
  });

  it('interpolates distinct left and right terrain contact across the right-of-way', () => {
    const crossSlope = [0, 1].map(() => ({
      centerZ: 0,
      leftZ: 1,
      rightZ: -1,
      halfWidthM: 5,
    }));
    const geo = buildRibbonBandGeometry(line100, -5, 5, 0.1, crossSlope)!;
    const pos = geo.getAttribute('position');
    expect(pos.getZ(0)).toBeCloseTo(-0.9, 6);
    expect(pos.getZ(1)).toBeCloseTo(1.1, 6);
    expect(streetStationElevationAt(crossSlope, 0, -2.5)).toBeCloseTo(-0.5, 8);
    expect(streetStationElevationAt(crossSlope, 0, 2.5)).toBeCloseTo(0.5, 8);
    geo.dispose();
  });
});

/** Face normals of all triangles whose vertices ALL sit at height z. */
function topFaceNormalZs(geo: THREE.BufferGeometry, z: number): number[] {
  const pos = geo.getAttribute('position');
  const idx = geo.getIndex()!;
  const out: number[] = [];
  for (let t = 0; t < idx.count; t += 3) {
    const [i, j, k] = [idx.getX(t), idx.getX(t + 1), idx.getX(t + 2)];
    if (
      Math.abs(pos.getZ(i) - z) > 1e-6 ||
      Math.abs(pos.getZ(j) - z) > 1e-6 ||
      Math.abs(pos.getZ(k) - z) > 1e-6
    )
      continue;
    const ax = pos.getX(j) - pos.getX(i);
    const ay = pos.getY(j) - pos.getY(i);
    const bx = pos.getX(k) - pos.getX(i);
    const by = pos.getY(k) - pos.getY(i);
    out.push(ax * by - ay * bx); // z of cross product
  }
  return out;
}

describe('winding (regression: side=-1 curbs and splitters rendered inside-out)', () => {
  it('curb tops face up on BOTH sides of the road', () => {
    const geo = buildCurbBandGeometry(line100, 5)!;
    const tops = topFaceNormalZs(
      geo,
      PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS + STREET_DETAIL_3D.curbHeight_m,
    );
    expect(tops.length).toBeGreaterThan(0);
    for (const nz of tops) expect(nz).toBeGreaterThan(0);
  });

  it('splitter island tops face up on all four legs', () => {
    const rb = buildRoundaboutGeometry(ROUNDABOUT_PARAMS.ICD / 2 + ROUNDABOUT_PARAMS.SLEN)!;
    const tops = topFaceNormalZs(
      rb.splitters,
      PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS + STREET_DETAIL_3D.curbHeight_m,
    );
    expect(tops.length).toBe(4);
    for (const nz of tops) expect(nz).toBeGreaterThan(0);
  });
});

describe('buildRoundaboutGeometry', () => {
  it('matches the standard radii at full scale', () => {
    const rb = buildRoundaboutGeometry(ROUNDABOUT_PARAMS.ICD / 2 + ROUNDABOUT_PARAMS.SLEN);
    expect(rb).not.toBeNull();
    expect(rb!.scale).toBe(1);

    rb!.ring.computeBoundingBox();
    const ringMax = rb!.ring.boundingBox!.max.x;
    expect(ringMax).toBeCloseTo(ROUNDABOUT_PARAMS.ICD / 2, 3);

    rb!.island.computeBoundingBox();
    const islandR = rb!.island.boundingBox!.max.x;
    expect(islandR).toBeCloseTo(
      ROUNDABOUT_PARAMS.ICD / 2 - ROUNDABOUT_PARAMS.CIRC - ROUNDABOUT_PARAMS.APRON,
      3,
    );

    // island stands islandHeight above grade; splitters at curb height
    const [, islandTop] = zRange(rb!.island);
    expect(islandTop).toBeCloseTo(
      PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS + STREET_DETAIL_3D.islandHeight_m,
      5,
    );
    const [, splitterTop] = zRange(rb!.splitters);
    expect(splitterTop).toBeCloseTo(
      PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS + STREET_DETAIL_3D.curbHeight_m,
      5,
    );
    expect(rb!.approachMarkings.getAttribute('position').count).toBe(4 * (7 + 1) * 4);
    expect(zRange(rb!.approachMarkings)[0]).toBeCloseTo(
      PUBLIC_REALM_STREET_MARKING_LIFT_METERS,
      6,
    );
  });

  it('clamps into small zones via uniform radial scale', () => {
    const rb = buildRoundaboutGeometry(14.5); // half the standard 29m reach
    expect(rb!.scale).toBeCloseTo(0.5, 3);
    rb!.ring.computeBoundingBox();
    expect(rb!.ring.boundingBox!.max.x).toBeCloseTo(ROUNDABOUT_PARAMS.ICD / 4, 3);
  });

  it('rejects zones too small to read as a roundabout', () => {
    expect(buildRoundaboutGeometry(1.5)).toBeNull();
  });
});
