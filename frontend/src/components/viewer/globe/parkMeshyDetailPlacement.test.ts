import { describe, expect, it } from 'vitest';

import type { ParkMeshyArchetypeAsset } from './parkMeshyArchetypeAssets';
import { resolveParkMeshyDetailPlacements } from './parkMeshyDetailPlacement';

function fixture(repeatOnOversize: boolean, dimensionsM: [number, number, number] = [6, 2, 2]) {
  return {
    id: 'fixture',
    url: '/park-kits/fixture.glb',
    archetypeId: 'fixture_park',
    variantIds: ['fixture_park_v0'],
    dimensionsM,
    placementRole: 'fixture_detail',
    sourceKind: 'meshy_multiview_archetype_reference',
    people: false,
    largeBuildings: false,
    placement: { u: 0.25, v: 0.5, yawDeg: 15, repeatOnOversize },
  } satisfies ParkMeshyArchetypeAsset;
}

describe('resolveParkMeshyDetailPlacements', () => {
  it('places an exact-size object once in a normal site', () => {
    const placements = resolveParkMeshyDetailPlacements(
      [fixture(false)],
      [[-20, -10], [20, -10], [20, 10], [-20, 10]],
    );
    expect(placements).toHaveLength(1);
    expect(placements[0].asset.id).toBe('fixture');
    expect(placements[0].yawRad).toBeCloseTo(Math.PI / 12);
  });

  it('adds a separated mirrored instance only when an authored repeatable object has an oversized site', () => {
    const placements = resolveParkMeshyDetailPlacements(
      [fixture(true)],
      [[-50, -20], [50, -20], [50, 20], [-50, 20]],
    );
    expect(placements).toHaveLength(2);
    expect(Math.hypot(
      placements[0].x - placements[1].x,
      placements[0].y - placements[1].y,
    )).toBeGreaterThan(10);
  });

  it('does not duplicate the same repeatable object on an ordinary site', () => {
    expect(resolveParkMeshyDetailPlacements(
      [fixture(true)],
      [[-20, -10], [20, -10], [20, 10], [-20, 10]],
    )).toHaveLength(1);
  });

  it('omits a complete object when its clearance disc cannot fit the polygon', () => {
    expect(resolveParkMeshyDetailPlacements(
      [fixture(false, [12, 12, 3])],
      [[-2.5, -2.5], [2.5, -2.5], [2.5, 2.5], [-2.5, 2.5]],
    )).toHaveLength(0);
  });
});
