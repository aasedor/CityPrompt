import { describe, expect, it } from 'vitest';

import type { SiteZone } from '@/types';
import {
  MAX_STREET_BENCHES_PER_ZONE,
  MAX_STREET_BIKE_RACKS_PER_ZONE,
  MAX_STREET_BOLLARDS_PER_ZONE,
  MAX_STREET_DRAINS_PER_ZONE,
  MAX_STREET_FIXTURE_STATIONS,
  MAX_STREET_LIGHTS_PER_ZONE,
  MAX_STREET_PLANTING_CELLS_PER_ZONE,
  MAX_STREET_SIDEWALK_JOINTS_PER_ZONE,
  MAX_STREET_TREES_PER_ZONE,
  MAX_STREET_WASTE_BINS_PER_ZONE,
  MAX_WOONERF_PLANTERS_PER_ZONE,
  STREET_BENCH_EDGE_CLEARANCE_M,
  STREET_NODE_FIXTURE_CLEARANCE_M,
  buildStreetFamilyFixturePlacements,
  buildWoonerfPlanterPlacements,
  interpolateStreetFixtureElevation,
  resolveBenchCenterInBand,
  type StreetFamilyFixturePlacements,
  type StreetFixturePose,
} from './streetFamilyFurniture';
import { resolvePilotStreetSectionProfile } from './streetSectionProfiles';

function mainStreetProfile() {
  return resolvePilotStreetSectionProfile({
    properties: {
      road_archetype_id: 'main_street_complete',
      road_selected_variant_id: 'main_street_complete_v0',
      public_realm_lego: {
        schema_version: 1,
        family_id: 'street_complete_main_22m',
        family_version: 1,
        kind: 'street',
        generator: 'street_section',
        archetype_id: 'main_street_complete',
        variant_id: 'main_street_complete_v0',
        profile_id: 'complete-main-22m-v1',
        profile_version: 1,
        appearance_kit_id: 'calgary_contemporary_native',
        target: { target_type: 'street_segment', row_width_m: 22, length_m: 1_000 },
        catalog_fingerprint: 'a'.repeat(64),
        capability_fingerprint: 'b'.repeat(64),
        recipe_hash: 'c'.repeat(64),
      },
    },
  } as Pick<SiteZone, 'properties'>);
}

function straightPoints(lengthM: number) {
  return Array.from({ length: Math.floor(lengthM / 4) + 1 }, (_, index) => ({
    x: index * 4,
    y: 0,
  }));
}

function allFixturePoses(fixtures: StreetFamilyFixturePlacements): StreetFixturePose[] {
  return [
    ...fixtures.trees,
    ...fixtures.benches,
    ...fixtures.lights,
    ...fixtures.drains,
    ...fixtures.sidewalkJoints,
    ...fixtures.wasteBins,
    ...fixtures.bikeRacks,
    ...fixtures.bollards,
    ...fixtures.plantingCells,
  ];
}

describe('street family furniture placement', () => {
  it('caps and evenly distributes woonerf chicane planters on long corridors', () => {
    const points = straightPoints(1_000);
    const planters = buildWoonerfPlanterPlacements(points, 5);
    expect(planters).toHaveLength(MAX_WOONERF_PLANTERS_PER_ZONE);
    expect(planters[0].centerX).toBeLessThan(20);
    expect(planters[planters.length - 1].centerX).toBeGreaterThan(980);
    planters.forEach((planter, index) => {
      expect(Math.sign(planter.y)).toBe(index % 2 === 0 ? -1 : 1);
    });
  });

  it('anchors woonerf planters to left/right cross-slope at their signed offset', () => {
    const points = straightPoints(40);
    const stationTerrain = points.map(() => ({
      centerZ: 10,
      leftZ: 12,
      rightZ: 8,
      halfWidthM: 5,
    }));
    const planters = buildWoonerfPlanterPlacements(points, 5, stationTerrain);
    expect(planters.length).toBeGreaterThanOrEqual(2);
    expect(planters[0].y).toBeCloseTo(-3.6, 8);
    expect(planters[0].z).toBeCloseTo(8.56, 8);
    expect(planters[0].centerZ).toBeCloseTo(10, 8);
    expect(planters[1].y).toBeCloseTo(3.6, 8);
    expect(planters[1].z).toBeCloseTo(11.44, 8);
    expect(planters[1].centerZ).toBeCloseTo(10, 8);
  });

  it('interpolates shifted fixture contact along grade and clamps to sampled bounds', () => {
    const distances = [0, 4, 8, 12];
    const elevations = [0, 4, 8, 12];
    expect(interpolateStreetFixtureElevation(elevations, distances, 2, 0, -2)).toBe(6);
    expect(interpolateStreetFixtureElevation(elevations, distances, 2, 0, 2)).toBe(10);
    expect(interpolateStreetFixtureElevation(elevations, distances, 0, 0, -100)).toBe(0);
    expect(interpolateStreetFixtureElevation(elevations, distances, 3, 0, 100)).toBe(12);

    const crossSlope = distances.map((centerZ) => ({
      centerZ,
      leftZ: centerZ + 2,
      rightZ: centerZ - 2,
      halfWidthM: 4,
    }));
    expect(interpolateStreetFixtureElevation(crossSlope, distances, 0, 2, 2)).toBe(3);
  });
  it('keeps the complete bench footprint inside its boulevard band', () => {
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(160),
      profile: mainStreetProfile(),
      sectionScale: 1,
      enabled: true,
    });
    expect(fixtures.benches.length).toBeGreaterThan(0);
    fixtures.benches.forEach((bench) => {
      const centerM = bench.offsetM;
      const halfDepthM = bench.footprintDepthM / 2;
      expect(centerM - halfDepthM).toBeGreaterThanOrEqual(
        bench.bandStartM + STREET_BENCH_EDGE_CLEARANCE_M - 1e-8,
      );
      expect(centerM + halfDepthM).toBeLessThanOrEqual(
        bench.bandEndM - STREET_BENCH_EDGE_CLEARANCE_M + 1e-8,
      );
    });
  });

  it('turns benches on opposing boulevards inward toward the street', () => {
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(160),
      profile: mainStreetProfile(),
      sectionScale: 1,
      enabled: true,
    });
    const negativeSide = fixtures.benches.find((bench) => bench.offsetM < 0);
    const positiveSide = fixtures.benches.find((bench) => bench.offsetM > 0);
    expect(negativeSide).toBeDefined();
    expect(positiveSide).toBeDefined();
    const delta = Math.abs((negativeSide!.yawRad - positiveSide!.yawRad) % (Math.PI * 2));
    expect(Math.min(delta, Math.PI * 2 - delta)).toBeCloseTo(Math.PI, 8);
  });

  it('is deterministic and enforces every explicit per-zone cap', () => {
    const options = {
      points: straightPoints(1_000),
      profile: mainStreetProfile(),
      sectionScale: 1,
      enabled: true,
    } as const;
    const first = buildStreetFamilyFixturePlacements(options);
    const second = buildStreetFamilyFixturePlacements(options);
    expect(second).toEqual(first);
    expect(first.stationCount).toBe(MAX_STREET_FIXTURE_STATIONS);
    expect(first.trees).toHaveLength(MAX_STREET_TREES_PER_ZONE);
    expect(first.lights).toHaveLength(MAX_STREET_LIGHTS_PER_ZONE);
    expect(first.benches).toHaveLength(MAX_STREET_BENCHES_PER_ZONE);
    expect(first.drains).toHaveLength(MAX_STREET_DRAINS_PER_ZONE);
    expect(first.sidewalkJoints).toHaveLength(MAX_STREET_SIDEWALK_JOINTS_PER_ZONE);
    expect(first.bollards).toHaveLength(MAX_STREET_BOLLARDS_PER_ZONE);
    expect(first.plantingCells).toHaveLength(MAX_STREET_PLANTING_CELLS_PER_ZONE);
    expect(first.wasteBins.length).toBeGreaterThan(0);
    expect(first.wasteBins.length).toBeLessThanOrEqual(MAX_STREET_WASTE_BINS_PER_ZONE);
    expect(first.bikeRacks.length).toBeGreaterThan(0);
    expect(first.bikeRacks.length).toBeLessThanOrEqual(MAX_STREET_BIKE_RACKS_PER_ZONE);
  });

  it('distributes capped stations across both ends of a long street', () => {
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(1_000),
      profile: mainStreetProfile(),
      sectionScale: 1,
      enabled: true,
    });
    const stations = [...new Set(fixtures.trees.map((tree) => tree.stationM))];
    expect(stations).toHaveLength(MAX_STREET_FIXTURE_STATIONS);
    expect(stations[0]).toBeLessThanOrEqual(28);
    expect(stations[stations.length - 1]).toBeGreaterThanOrEqual(972);
    expect(fixtures.drains[0].stationM).toBeLessThanOrEqual(32);
    expect(fixtures.drains[fixtures.drains.length - 1].stationM).toBeGreaterThanOrEqual(968);
    expect(fixtures.sidewalkJoints[0].stationM).toBeLessThanOrEqual(20);
    expect(fixtures.sidewalkJoints[fixtures.sidewalkJoints.length - 1].stationM)
      .toBeGreaterThanOrEqual(980);
  });

  it('emits renderer-ready local ENU frames and defaults micro-detail z to zero', () => {
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(160),
      profile: mainStreetProfile(),
      sectionScale: 1,
      enabled: true,
    });
    const microDetails = [
      ...fixtures.drains,
      ...fixtures.sidewalkJoints,
      ...fixtures.wasteBins,
      ...fixtures.bikeRacks,
      ...fixtures.bollards,
      ...fixtures.plantingCells,
    ];
    expect(microDetails.length).toBeGreaterThan(0);
    microDetails.forEach((fixture) => {
      expect(fixture.z).toBe(0);
      expect(fixture.stationIndex).toBeGreaterThan(0);
      expect(fixture.stationM).toBeGreaterThan(0);
      expect(fixture.tangentX).toBeCloseTo(1, 8);
      expect(fixture.tangentY).toBeCloseTo(0, 8);
      expect(fixture.normalX).toBeCloseTo(0, 8);
      expect(fixture.normalY).toBeCloseTo(1, 8);
      expect(fixture.yawRad).toBeCloseTo(0, 8);
      expect(fixture.y).toBeCloseTo(fixture.offsetM, 8);
    });
  });

  it('places drainage, joints, cycle protection and tree grates in their engineered bands', () => {
    const profile = mainStreetProfile()!;
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(180),
      profile,
      sectionScale: 1,
      enabled: true,
    });
    expect(fixtures.drains.length).toBeGreaterThan(0);
    fixtures.drains.forEach((drain) => {
      expect(profile.curbOffsetsM).toContainEqual(drain.offsetM);
    });
    expect(fixtures.sidewalkJoints.length).toBeGreaterThan(0);
    fixtures.sidewalkJoints.forEach((joint) => {
      expect(joint.offsetM).toBeGreaterThanOrEqual(joint.bandStartM);
      expect(joint.offsetM).toBeLessThanOrEqual(joint.bandEndM);
      expect(joint.widthM).toBeLessThan(joint.bandEndM - joint.bandStartM);
    });
    const bufferCenters = profile.bands
      .filter((band) => band.kind === 'buffer')
      .map((band) => band.centerM);
    expect(fixtures.bollards.length).toBeGreaterThan(0);
    fixtures.bollards.forEach((bollard) => {
      expect(bufferCenters).toContainEqual(bollard.offsetM);
    });
    expect(fixtures.plantingCells.length).toBeGreaterThan(0);
    fixtures.plantingCells.forEach((cell) => {
      expect(cell.style).toBe('tree_grate');
      expect(cell.offsetM - cell.widthM / 2).toBeGreaterThanOrEqual(cell.bandStartM - 1e-8);
      expect(cell.offsetM + cell.widthM / 2).toBeLessThanOrEqual(cell.bandEndM + 1e-8);
    });
    [...fixtures.wasteBins, ...fixtures.bikeRacks].forEach((fixture) => {
      expect(fixture.offsetM).toBeGreaterThanOrEqual(fixture.bandStartM);
      expect(fixture.offsetM).toBeLessThanOrEqual(fixture.bandEndM);
    });
  });

  it('does not suppress road-surface details when a family has no planting band', () => {
    const profile = mainStreetProfile()!;
    const withoutPlanting = {
      ...profile,
      bands: profile.bands.filter((band) => band.kind !== 'planting'),
      treeOffsetsM: [],
    };
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(180),
      profile: withoutPlanting,
      sectionScale: 1,
      enabled: true,
    });
    expect(fixtures.stationCount).toBeGreaterThan(0);
    expect(fixtures.trees).toEqual([]);
    expect(fixtures.benches).toEqual([]);
    expect(fixtures.plantingCells).toEqual([]);
    expect(fixtures.drains.length).toBeGreaterThan(0);
    expect(fixtures.sidewalkJoints.length).toBeGreaterThan(0);
    expect(fixtures.bollards.length).toBeGreaterThan(0);
  });

  it('reserves node clearances for legacy furniture and all new micro-details', () => {
    const clearance = { x: 80, y: 0 };
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(200),
      profile: mainStreetProfile(),
      sectionScale: 1,
      clearancePoints: [clearance],
      enabled: true,
    });
    allFixturePoses(fixtures).forEach((fixture) => {
      expect(Math.hypot(fixture.x - clearance.x, fixture.y - clearance.y))
        .toBeGreaterThanOrEqual(STREET_NODE_FIXTURE_CLEARANCE_M - 1e-8);
    });
  });

  it('forwards terrain samples by station to every flush micro-detail', () => {
    const points = straightPoints(160);
    const stationZ = points.map((_, index) => index * 0.125);
    const fixtures = buildStreetFamilyFixturePlacements({
      points,
      stationZ,
      profile: mainStreetProfile(),
      sectionScale: 1,
      enabled: true,
    });
    [
      ...fixtures.drains,
      ...fixtures.sidewalkJoints,
      ...fixtures.bollards,
      ...fixtures.plantingCells,
    ].forEach((fixture) => {
      expect(fixture.z).toBe(stationZ[fixture.stationIndex]);
    });
  });

  it('interpolates tangent-shifted benches, bins and racks along the centreline grade', () => {
    const points = straightPoints(240);
    const stationZ = points.map((_, index) => index);
    const fixtures = buildStreetFamilyFixturePlacements({
      points,
      stationZ,
      profile: mainStreetProfile(),
      sectionScale: 1,
      enabled: true,
    });
    expect(fixtures.benches.length).toBeGreaterThan(0);
    expect(fixtures.wasteBins.length).toBeGreaterThan(0);
    expect(fixtures.bikeRacks.length).toBeGreaterThan(0);
    fixtures.benches.forEach((bench) => {
      expect(bench.z).toBeCloseTo(stationZ[bench.stationIndex] - 1.15 / 4 + 0.16, 8);
    });
    fixtures.wasteBins.forEach((bin) => {
      expect(bin.z).toBeCloseTo(stationZ[bin.stationIndex] + 2.1 / 4, 8);
    });
    fixtures.bikeRacks.forEach((rack) => {
      expect(rack.z).toBeCloseTo(stationZ[rack.stationIndex] - 2.25 / 4, 8);
    });
  });

  it('does not force a bench into a furnishing band that is too narrow', () => {
    expect(resolveBenchCenterInBand(0, 0.5, 0.25, 0.9)).toBeNull();
    expect(resolveBenchCenterInBand(0, 1.2, 1.1, 0.9)).toBeCloseTo(0.832, 6);
  });

  it('keeps the trail family sparse and emits no road drainage or furniture', () => {
    const trail = resolvePilotStreetSectionProfile('multi_use_trail');
    expect(buildStreetFamilyFixturePlacements({
      points: straightPoints(160),
      profile: trail,
      sectionScale: 1,
      enabled: true,
    })).toEqual({
      trees: [],
      benches: [],
      lights: [],
      drains: [],
      sidewalkJoints: [],
      wasteBins: [],
      bikeRacks: [],
      bollards: [],
      plantingCells: [],
      stationCount: 0,
    });
  });

  it('gives a compiled green alley bounded bioswale planting cells without road drainage', () => {
    const greenAlley = resolvePilotStreetSectionProfile({
      properties: {
        public_realm_lego: {
          schema_version: 1,
          family_id: 'street_local_public_realm',
          family_version: 1,
          kind: 'street',
          generator: 'street_section',
          archetype_id: 'green_alley',
          variant_id: 'green_alley_v1',
          profile_id: 'green-alley-v1',
          profile_version: 1,
          appearance_kit_id: 'heritage_brick_stone',
          target: { target_type: 'street_segment', row_width_m: 5, length_m: 160 },
          catalog_fingerprint: 'a'.repeat(64),
          capability_fingerprint: 'b'.repeat(64),
          recipe_hash: 'c'.repeat(64),
        },
      },
    } as Pick<SiteZone, 'properties'>);
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(160),
      profile: greenAlley,
      sectionScale: 1,
      enabled: true,
    });
    expect(fixtures.plantingCells.length).toBeGreaterThan(0);
    expect(fixtures.plantingCells.every((cell) => cell.style === 'low_planting_cell')).toBe(true);
    expect(fixtures.drains).toEqual([]);
    expect(fixtures.sidewalkJoints).toEqual([]);
  });
});
