import { describe, expect, it } from 'vitest';
import * as THREE from 'three';

import type { SiteZone } from '@/types';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { roundStreetCenterline } from '@/utils/streetRouteCurves';
import { detectConnectedStreetIntersections, detectFourWayStreetIntersections } from './streetGraphIntersections';
import { resolveStreetJunctionLayout } from './streetJunctionGeometry';
import { buildSectionJunctionGeometry } from './streetJunctionGeometry';
import { nativeStreetPilot } from './nativeStreetPilot';
import { validateStreetRecipeProperties } from './streetLegoContract';

function street(
  id: string,
  line: number[][],
  width: number,
  options: { legacy?: boolean; appearanceKitId?: string; familyVersion?: number } = {},
): SiteZone {
  const isMain = width >= 18;
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
          family_id: isMain
            ? (width >= 20 ? 'street_complete_main_22m' : 'street_complete_main_18m')
            : 'street_local_public_realm',
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

function nativeCandidateStreet(id: string, line: number[][], pilotId: string): SiteZone {
  const pilot = nativeStreetPilot(pilotId)!;
  const zone = street(id, line, pilot.widthM);
  zone.properties = {
    width: pilot.widthM,
    lane_count: pilotId === 'student_market_street_v1' ? 0 : 2,
    road_archetype_id: pilot.sourceArchetypeId,
    road_selected_variant_id: `${pilot.sourceArchetypeId}_v0`,
    native_street_pilot_id: pilot.id,
    plan_centerline: line,
  };
  return zone;
}

describe('review-only mixed native pedestrian junctions', () => {
  const mainLine = [[-114.1, 51], [-114.09, 51]];
  const marketCrossing = [[-114.095, 50.995], [-114.095, 51.005]];
  const marketStem = [[-114.095, 51], [-114.095, 51.005]];

  it.each([
    ['X', marketCrossing, 4],
    ['T', marketStem, 3],
  ])('gives a %s one owned surface and crossings only on the vehicle street', (_name, marketLine, arms) => {
    const zones = [nativeCandidateStreet('main', mainLine, 'student_main_street_v1'),
      nativeCandidateStreet('market', marketLine, 'student_market_street_v1')];
    const nodes = detectConnectedStreetIntersections(zones);
    expect(nodes).toHaveLength(1);
    expect(nodes[0].armCount).toBe(arms);
    const layout = resolveStreetJunctionLayout(nodes[0], zones);
    expect(layout?.pedestrianAxes).toEqual([false, true]);
    const geometry = buildSectionJunctionGeometry(layout!);
    expect(geometry.crosswalks.getAttribute('position').count).toBe(7 * 6 * 2);
    const covers = (surface: THREE.BufferGeometry, x: number, y: number) => {
      const material = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide });
      const hit = new THREE.Raycaster(new THREE.Vector3(x, y, 10), new THREE.Vector3(0, 0, -1))
        .intersectObject(new THREE.Mesh(surface, material)).length > 0;
      material.dispose();
      return hit;
    };
    expect(covers(geometry.promenadePaving, 0, 14)).toBe(true);
    expect(covers(geometry.promenadePaving, 6, 14)).toBe(true);
    expect(covers(geometry.pavement, 0, 0)).toBe(true);
    expect(covers(geometry.promenadePaving, 0, -14)).toBe(arms === 4);
    Object.values(geometry).forEach(item => item.dispose());
  });

  it('joins the market candidate to an existing compiled street without promoting the candidate', () => {
    const main = street('compiled-main', mainLine, 18, { appearanceKitId: 'classic_tree_lined_v1' });
    const market = nativeCandidateStreet('market', marketStem, 'student_market_street_v1');
    const nodes = detectConnectedStreetIntersections([main, market]);
    expect(nodes).toHaveLength(1);
    expect(resolveStreetJunctionLayout(nodes[0], [main, market])?.pedestrianAxes).toContain(true);
    market.properties = { ...market.properties, native_street_pilot_id: undefined };
    expect(detectConnectedStreetIntersections([main, market])).toHaveLength(0);
  });

  it('keeps the promenade as the through surface when its axis comes first', () => {
    const zones = [nativeCandidateStreet('market', mainLine, 'student_market_street_v1'),
      nativeCandidateStreet('main', marketCrossing, 'student_main_street_v1')];
    const node = detectConnectedStreetIntersections(zones)[0];
    const layout = resolveStreetJunctionLayout(node, zones);
    expect(layout?.pedestrianAxes).toEqual([true, false]);
    expect(layout?.surfaceZoneId).toBe('market');
    const geometry = buildSectionJunctionGeometry(layout!);
    expect(geometry.crosswalks.getAttribute('position').count).toBe(7 * 6 * 2);
    expect(geometry.promenadePaving.getAttribute('position').count).toBeGreaterThan(0);
    expect(geometry.pavement.getAttribute('position').count).toBeGreaterThan(0);
    Object.values(geometry).forEach(item => item.dispose());
  });

  it('keeps a market-to-market crossing fully paved and car-free', () => {
    const zones = [nativeCandidateStreet('east-west-market', mainLine, 'student_market_street_v1'),
      nativeCandidateStreet('north-south-market', marketCrossing, 'student_market_street_v1')];
    const node = detectConnectedStreetIntersections(zones)[0];
    const layout = resolveStreetJunctionLayout(node, zones);
    expect(layout?.pedestrianAxes).toEqual([true, true]);
    const geometry = buildSectionJunctionGeometry(layout!);
    expect(geometry.crosswalks.getAttribute('position').count).toBe(0);
    expect(geometry.promenadePaving.getAttribute('position').count).toBeGreaterThan(0);
    Object.values(geometry).forEach(item => item.dispose());
  });
});

describe('four-way street graph adapter', () => {
  it('joins the fixed collector, shared streets and exact 5 m green alley', () => {
    const collector = street('collector', [[-114.081,51.04],[-114.079,51.04]],20);
    collector.properties = {...collector.properties, public_realm_lego: undefined,
      road_archetype_id:'calgary_collector', road_selected_variant_id:'calgary_collector_v0',
      public_realm_fallback:{state:'family_pending'}, plan_centerline:[[-114.081,51.04],[-114.079,51.04]]};
    const shared = street('shared', [[-114.08,51.039],[-114.08,51.04]],6);
    shared.properties = {...shared.properties, lane_count:1, road_archetype_id:'yield_street', road_selected_variant_id:'yield_street_v0',
      public_realm_lego:{...(shared.properties!.public_realm_lego as object),archetype_id:'yield_street',variant_id:'yield_street_v0',profile_id:'yield-street-v1',appearance_kit_id:'dutch_woonerf_v1'}};
    const alley = street('alley', [[-114.081,51.039],[-114.079,51.039]],5);
    alley.properties = {...alley.properties, lane_count:1, road_archetype_id:'green_alley', road_selected_variant_id:'green_alley_v0',
      public_realm_lego:{...(alley.properties!.public_realm_lego as object),archetype_id:'green_alley',variant_id:'green_alley_v0',profile_id:'green-alley-v1',appearance_kit_id:'green_corridor_v1'}};
    const zones = [collector,shared,alley];
    expect(validateStreetRecipeProperties(shared.properties)).toMatchObject({valid:true});
    expect(validateStreetRecipeProperties(alley.properties)).toMatchObject({valid:true});
    const nodes = detectConnectedStreetIntersections(zones);
    expect(nodes).toHaveLength(2);
    for (const node of nodes) expect(resolveStreetJunctionLayout(node,zones)?.sections).toHaveLength(2);
    collector.properties.road_selected_variant_id = 'invented';
    expect(detectConnectedStreetIntersections(zones)).toHaveLength(1);
  });
  it('drops the node when a planner street has a present-but-invalid plan_centerline', () => {
    // An empty persisted centerline (seen on AI-plan access stubs next to a
    // roundabout) must exclude the street from V1 junction anchoring — the
    // server's independent proof falls back to different polygon geometry
    // and would 409 every claim forever.
    const eastWest = street('east-west', [[-114.1, 51], [-114.09, 51]], 22);
    const northSouth = street('north-south', [[-114.095, 50.995], [-114.095, 51.005]], 14);
    (northSouth.properties as Record<string, unknown>).plan_centerline = [];

    expect(detectFourWayStreetIntersections([eastWest, northSouth])).toHaveLength(0);
  });

  it('drops the node when a planner-marked street has no persisted centerline', () => {
    const eastWest = street('east-west', [[-114.1, 51], [-114.09, 51]], 22);
    const northSouth = street('north-south', [[-114.095, 50.995], [-114.095, 51.005]], 14);
    (northSouth.properties as Record<string, unknown>)._imported_from = 'plan';

    expect(detectFourWayStreetIntersections([eastWest, northSouth])).toHaveLength(0);
  });

  it('keeps the node when persisted plan_centerlines are valid', () => {
    const eastWest = street('east-west', [[-114.1, 51], [-114.09, 51]], 22);
    const northSouth = street('north-south', [[-114.095, 50.995], [-114.095, 51.005]], 14);
    (eastWest.properties as Record<string, unknown>).plan_centerline = [[-114.1, 51], [-114.09, 51]];
    (northSouth.properties as Record<string, unknown>).plan_centerline = [[-114.095, 50.995], [-114.095, 51.005]];

    expect(detectFourWayStreetIntersections([eastWest, northSouth])).toHaveLength(1);
  });

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

  it('keeps accessible node masks when an 18 m complete-main segment contributes', () => {
    const nodes = detectFourWayStreetIntersections([
      street('east-west-18m', [[-114.1, 51], [-114.09, 51]], 18),
      street('north-south-local', [[-114.095, 50.995], [-114.095, 51.005]], 14),
    ]);

    expect(nodes).toHaveLength(1);
    expect(nodes[0]).toMatchObject({
      familyId: 'street_four_way_intersection',
      zoneIds: ['east-west-18m', 'north-south-local'],
    });
    expect(nodes[0].axisAHalfWidthM + nodes[0].axisBHalfWidthM).toBeCloseTo(16, 1);
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


describe('bounded connected T graph', () => {
  const main = () => street('main', [[-114.101, 51], [-114.099, 51]], 16);
  const stem = (north = true) => street('stem', [[-114.1, 51], [-114.1, north ? 51.001 : 50.999]], 14);

  it.each([true, false])('retains exactly three directed arms, north=%s', (north) => {
    const zones = [main(), stem(north)];
    const node = detectConnectedStreetIntersections(zones)[0];
    expect(node.armCount).toBe(3);
    expect(node.familyId).toBe('street_t_intersection');
    expect(node.approachSides[0]).toEqual([-1, 1]);
    expect(node.approachSides[1]).toEqual([north ? 1 : -1]);
    const layout = resolveStreetJunctionLayout(node, zones);
    expect(layout).not.toBeNull();
    expect(layout!.roadA).toBeLessThan(layout!.rowA);
    expect(layout!.roadB).toBeLessThan(layout!.rowB);
    expect(detectConnectedStreetIntersections([...zones].reverse())).toEqual([node]);
    expect(detectFourWayStreetIntersections(zones)).toEqual([]);
  });

  it('joins a skew T while preserving its actual approach bearing', () => {
    const diagonal = street('stem', [[-114.1, 51], [-114.099, 51.001]], 14);
    const original = JSON.stringify(diagonal);
    const zones = [main(), diagonal], [node] = detectConnectedStreetIntersections(zones);
    expect(node.armCount).toBe(3);
    expect(node.orthogonal).toBe(false);
    const layout = resolveStreetJunctionLayout(node, zones)!;
    expect(layout).not.toBeNull();
    expect(layout.shear).toBeCloseTo(111320 * Math.cos(51 * Math.PI / 180) / 111320, 3);
    expect(layout.rowB * Math.sin(node.axisBBearingRad)).toBeCloseTo(node.axisBHalfWidthM, 5);
    expect(JSON.stringify(diagonal)).toBe(original);
  });

  it('keeps a remote bend without disabling the straight segment entering a T', () => {
    const bent = street('stem', [[-114.1, 51], [-114.0995, 51.001], [-114.0985, 51.0013]], 14);
    const zones = [main(), bent], [node] = detectConnectedStreetIntersections(zones);
    expect(resolveStreetJunctionLayout(node, zones)).not.toBeNull();
  });

  it('keeps a rounded approach tangent and an owned T surface', () => {
    const line = roundStreetCenterline([[-114.1, 51], [-114.1, 51.0007], [-114.0993, 51.0013]], 24);
    const curved = street('curved-stem', line, 14);
    curved.properties = { ...curved.properties, plan_centerline: line };
    const zones = [main(), curved];
    const nodes = detectConnectedStreetIntersections(zones);
    expect(nodes).toHaveLength(1);
    expect(nodes[0].armCount).toBe(3);
    expect(resolveStreetJunctionLayout(nodes[0], zones)).not.toBeNull();
  });

  it('joins a compiled public-road route with a redundant saved station at the T', () => {
    const through = street('public', [[-114.101, 51], [-114.1, 51], [-114.099, 51]], 16);
    through.properties = { ...through.properties, connect_to_public_road: true };
    const zones = [through, stem()];
    const [node] = detectConnectedStreetIntersections(zones);
    expect(node.armCount).toBe(3);
    expect(node.zoneIds).toEqual(['public', 'stem']);
    expect(resolveStreetJunctionLayout(node, zones)).not.toBeNull();
  });

  it('does not claim a turn inside the junction envelope as a straight arm', () => {
    const turning = street('turning', [[-114.1, 51], [-114.1, 51.00004], [-114.099, 51.0005]], 14);
    expect(detectConnectedStreetIntersections([main(), turning])).toEqual([]);
  });

  it('reconstructs a three-source T with split through arms', () => {
    const zones = [street('west', [[-114.101, 51], [-114.1, 51]], 16),
      street('east', [[-114.1, 51], [-114.099, 51]], 16), stem()];
    const [node] = detectConnectedStreetIntersections(zones);
    expect(node.armCount).toBe(3);
    expect(node.zoneIds).toEqual(['east', 'stem', 'west']);
  });

  it('keeps the existing four-way identity and eligibility', () => {
    const zones = [main(), street('cross', [[-114.1, 50.999], [-114.1, 51.001]], 14)];
    expect(detectConnectedStreetIntersections(zones)).toEqual(detectFourWayStreetIntersections(zones));
  });
});


it('does not disguise a bent through street as an orthogonal T by grouping bearings', () => {
  const zones = [street('west', [[-114.101, 50.9999], [-114.1, 51]], 16),
    street('east', [[-114.1, 51], [-114.099, 51]], 16),
    street('stem', [[-114.1, 51], [-114.1, 51.001]], 14)];
  expect(detectConnectedStreetIntersections(zones)).toEqual([]);
});


it('does not extend a tiny T stem beyond its authored footprint to fit a junction', () => {
  const zones = [street('main', [[-114.101, 51], [-114.099, 51]], 16),
    street('stem', [[-114.1, 51], [-114.1, 51.00005]], 14)];
  const [node] = detectConnectedStreetIntersections(zones);
  expect(node?.armCount).toBe(3);
  expect(resolveStreetJunctionLayout(node, zones)).toBeNull();
});
