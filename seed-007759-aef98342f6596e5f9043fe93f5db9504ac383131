import { describe, expect, it } from 'vitest';

import type { SiteZone } from '@/types';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { detectFourWayStreetIntersections } from './streetGraphIntersections';

function street(
  id: string,
  line: number[][],
  width: number,
  options: { legacy?: boolean; appearanceKitId?: string; familyVersion?: number } = {},
): SiteZone {
  const isMain = width >= 20;
  const archetypeId = isMain ? 'main_street_complete' : 'calgary_local';
  const variantId = `${archetypeId}_v0`;
  return {
    id,
    project_id: 'project',
    zone_type: 'road',
    coordinates: bufferLineToPolygon(line, width),
    color: '#777777',
    sort_order: 0,
    created_at: '2026-07-21T00:00:00Z',
    updated_at: '2026-07-21T00:00:00Z',
    properties: {
      width,
      lane_count: width <= 5 ? 0 : 2,
      road_archetype_id: archetypeId,
      road_selected_variant_id: variantId,
      ...(!options.legacy ? {
        public_realm_lego: {
          schema_version: 1,
          family_id: isMain ? 'street_complete_main_22m' : 'street_local_public_realm',
          family_version: options.familyVersion ?? 1,
          kind: 'street',
          generator: 'street_section',
          archetype_id: archetypeId,
          variant_id: variantId,
          profile_id: `${archetypeId.replace(/_/g, '-')}-v1`,
          profile_version: 1,
          appearance_kit_id: options.appearanceKitId ?? 'calgary_contemporary_native',
          target: { target_type: 'street_segment', row_width_m: width },
          catalog_fingerprint: 'a'.repeat(64),
          capability_fingerprint: 'b'.repeat(64),
          recipe_hash: 'c'.repeat(64),
        },
      } : {}),
    },
  } as SiteZone;
}

describe('four-way street graph adapter', () => {
  it('emits one graph-owned node for two continuous crossing centerlines', () => {
    const nodes = detectFourWayStreetIntersections([
      street('east-west', [[-114.1, 51], [-114.09, 51]], 22),
      street('north-south', [[-114.095, 50.995], [-114.095, 51.005]], 14),
    ]);
    expect(nodes).toHaveLength(1);
    expect(nodes[0]).toMatchObject({
      familyId: 'street_four_way_intersection',
      familyVersion: 1,
      archetypeId: 'protected_intersection',
      variantId: 'protected_intersection_v0',
      appearanceKitId: 'dutch_corner_islands_v1',
      zoneIds: ['east-west', 'north-south'],
    });
    expect(nodes[0].axisAHalfWidthM + nodes[0].axisBHalfWidthM).toBeCloseTo(18, 1);
  });

  it('does not promote a three-arm T junction to the four-way family', () => {
    const nodes = detectFourWayStreetIntersections([
      street('east-west', [[-114.1, 51], [-114.09, 51]], 14),
      street('north-leg', [[-114.095, 51], [-114.095, 51.005]], 14),
    ]);
    expect(nodes).toEqual([]);
  });

  it('never adds V1 accessible geometry to a Classic-only crossing', () => {
    const nodes = detectFourWayStreetIntersections([
      street('east-west', [[-114.1, 51], [-114.09, 51]], 22, { legacy: true }),
      street('north-south', [[-114.095, 50.995], [-114.095, 51.005]], 14, { legacy: true }),
    ]);
    expect(nodes).toEqual([]);
  });

  it('fails the entire inferred node closed when any contributing recipe is unsupported', () => {
    const nodes = detectFourWayStreetIntersections([
      street('east-west', [[-114.1, 51], [-114.09, 51]], 22),
      street('north-south', [[-114.095, 50.995], [-114.095, 51.005]], 14, {
        appearanceKitId: 'classic_tree_lined_v1',
      }),
    ]);
    expect(nodes).toEqual([]);
  });

  it('does not turn a multi-use-trail crossing into a motor-street four-way node', () => {
    const trail = street('trail', [[-114.095, 50.995], [-114.095, 51.005]], 4);
    trail.properties = { width: 4, lane_count: 0, street_role: 'path', road_archetype_id: 'multi_use_trail' };
    const nodes = detectFourWayStreetIntersections([
      street('east-west', [[-114.1, 51], [-114.09, 51]], 14),
      trail,
    ]);
    expect(nodes).toEqual([]);
  });

  it('reconstructs opposing fragments clipped at a continuous main-street band', () => {
    const elevenMetresLat = 11 / 111_320;
    const nodes = detectFourWayStreetIntersections([
      street('main', [[-114.1, 51], [-114.09, 51]], 22),
      street('north-local', [[-114.095, 51 + elevenMetresLat], [-114.095, 51.005]], 14),
      street('south-local', [[-114.095, 50.995], [-114.095, 51 - elevenMetresLat]], 14),
    ]);
    expect(nodes).toHaveLength(1);
    expect(nodes[0].zoneIds).toEqual(['main', 'north-local', 'south-local']);
    expect(nodes[0].longitude).toBeCloseTo(-114.095, 5);
    expect(nodes[0].latitude).toBeCloseTo(51, 5);
  });

  it('does not coerce a six-arm crossing into the four-arm contract', () => {
    const nodes = detectFourWayStreetIntersections([
      street('east-west', [[-114.1, 51], [-114.09, 51]], 22),
      street('north-south', [[-114.095, 50.995], [-114.095, 51.005]], 14),
      street('southwest-northeast', [[-114.099, 50.997], [-114.091, 51.003]], 14),
    ]);
    expect(nodes).toEqual([]);
  });
});
