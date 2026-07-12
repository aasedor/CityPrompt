import { describe, expect, it } from 'vitest';

import {
  buildCurbBandGeometry,
  buildDashGeometry,
  buildRoundaboutGeometry,
  densifyPolyline,
} from './streetMesh3D';
import { ROUNDABOUT_PARAMS, STREET_DETAIL_3D } from '@/data/streetGeometryParams';

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
    expect(zMin).toBe(0);
    expect(zMax).toBeCloseTo(STREET_DETAIL_3D.curbHeight_m, 5);

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
    const tops = topFaceNormalZs(geo, STREET_DETAIL_3D.curbHeight_m);
    expect(tops.length).toBeGreaterThan(0);
    for (const nz of tops) expect(nz).toBeGreaterThan(0);
  });

  it('splitter island tops face up on all four legs', () => {
    const rb = buildRoundaboutGeometry(ROUNDABOUT_PARAMS.ICD / 2 + ROUNDABOUT_PARAMS.SLEN)!;
    const tops = topFaceNormalZs(rb.splitters, STREET_DETAIL_3D.curbHeight_m);
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
    expect(islandTop).toBeCloseTo(STREET_DETAIL_3D.islandHeight_m, 5);
    const [, splitterTop] = zRange(rb!.splitters);
    expect(splitterTop).toBeCloseTo(STREET_DETAIL_3D.curbHeight_m, 5);
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
