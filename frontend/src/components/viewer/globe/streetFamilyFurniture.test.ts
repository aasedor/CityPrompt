import { describe, expect, it } from 'vitest';

import type { SiteZone } from '@/types';
import {
  MAX_STREET_BENCHES_PER_ZONE,
  MAX_STREET_BIKE_RACKS_PER_ZONE,
  MAX_STREET_DRAINS_PER_ZONE,
  MAX_STREET_FIXTURE_STATIONS,
  MAX_STREET_PLANTING_CELLS_PER_ZONE,
  MAX_STREET_SIDEWALK_JOINTS_PER_ZONE,
  MAX_STREET_WASTE_BINS_PER_ZONE,
  MAX_WOONERF_PLANTERS_PER_ZONE,
  MAX_WOONERF_PLAY_NODES_PER_ZONE,
  MAX_MAIN_STREET_LIGHTS_PER_ZONE,
  MAX_MAIN_STREET_TREES_PER_ZONE,
  MAX_MAIN_STREET_VEHICLES_PER_ZONE,
  MAX_NARROW_RESIDENTIAL_LIGHTS_PER_ZONE,
  MAX_NARROW_RESIDENTIAL_TREES_PER_ZONE,
  MAX_NARROW_RESIDENTIAL_VEHICLES_PER_ZONE,
  MAIN_STREET_LIGHT_SPACING_M,
  MAIN_STREET_TREE_SPACING_M,
  MAIN_STREET_VEHICLE_SPACING_M,
  NARROW_RESIDENTIAL_LIGHT_SPACING_M,
  NARROW_RESIDENTIAL_TREE_SPACING_M,
  STREET_BENCH_EDGE_CLEARANCE_M,
  STREET_NODE_FIXTURE_CLEARANCE_M,
  STREET_PARKED_VEHICLE_EDGE_CLEARANCE_M,
  STREET_TRANSIT_SHELTER_EDGE_CLEARANCE_M,
  buildStreetFamilyFixturePlacements,
  buildWoonerfPlanterPlacements,
  buildWoonerfPlayPlacements,
  buildYieldStreetEntrySignPlacements,
  interpolateStreetFixtureElevation,
  resolveBenchCenterInBand,
  type StreetFamilyFixturePlacements,
  type StreetFixturePose,
} from './streetFamilyFurniture';
import { resolvePilotStreetSectionProfile } from './streetSectionProfiles';
import { STREET_APPEARANCE_KITS, type StreetAppearanceKitId } from './streetFamilyCatalog';
import { seatStreetFamilyFixtures } from './streetSharedGround';

describe('street fixture builder shared-ground handoff', () => {
  it.each([mainStreetProfile, narrowResidentialProfile])('preserves metadata when the live terrain becomes ready', (makeProfile) => {
    const fixtures = buildStreetFamilyFixturePlacements({ points: straightPoints(160), profile: makeProfile(), sectionScale: 1, enabled: true });
    expect(fixtures.stationCount).toBeGreaterThan(0);
    const before = structuredClone(fixtures);
    const offsetAt = (x: number, y: number) => x * 0.015 + y * 0.02;
    const seated = seatStreetFamilyFixtures(fixtures, offsetAt);
    expect(seated.stationCount).toBe(fixtures.stationCount);
    let poseCount = 0;
    for (const [key, poses] of Object.entries(fixtures)) {
      if (!Array.isArray(poses)) continue;
      const result = seated[key as keyof typeof seated] as StreetFixturePose[];
      expect(result).toHaveLength(poses.length);
      poses.forEach((pose, index) => {
        expect(result[index]).toEqual({ ...pose, z: pose.z + offsetAt(pose.x, pose.y) });
        poseCount += 1;
      });
    }
    expect(poseCount).toBeGreaterThan(0);
    expect(fixtures).toEqual(before);
    const refined = seatStreetFamilyFixtures(fixtures, () => 2);
    expect(refined.lights[0].z).toBeCloseTo(fixtures.lights[0].z + 2);
  });
  it('handles the actual disabled-builder output and never replaces metadata with an array', () => {
    const empty = buildStreetFamilyFixturePlacements({ points: [], profile: null, sectionScale: 1, enabled: false });
    expect(seatStreetFamilyFixtures(empty, () => 2)).toEqual(empty);
    expect(seatStreetFamilyFixtures(empty, () => 2).stationCount).toBe(0);
  });
});

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

function narrowResidentialProfile() {
  return resolvePilotStreetSectionProfile({
    properties: {
      road_archetype_id: 'narrow_residential_street',
      road_selected_variant_id: 'narrow_residential_street_v0',
      public_realm_lego: {
        schema_version: 1,
        family_id: 'street_local_public_realm',
        family_version: 1,
        kind: 'street',
        generator: 'street_section',
        archetype_id: 'narrow_residential_street',
        variant_id: 'narrow_residential_street_v0',
        profile_id: 'narrow-residential-street-v1',
        profile_version: 1,
        appearance_kit_id: 'classic_tree_lined_v1',
        target: { target_type: 'street_segment', row_width_m: 10, length_m: 240 },
        catalog_fingerprint: 'a'.repeat(64),
        capability_fingerprint: 'b'.repeat(64),
        recipe_hash: 'c'.repeat(64),
      },
    },
  } as Pick<SiteZone, 'properties'>);
}

function tropicalMainStreetProfile() {
  return resolvePilotStreetSectionProfile({
    properties: {
      road_archetype_id: 'main_street_complete',
      road_selected_variant_id: 'main_street_complete_v3',
      public_realm_lego: {
        schema_version: 1,
        family_id: 'street_complete_main_18m',
        family_version: 1,
        kind: 'street',
        generator: 'street_section',
        archetype_id: 'main_street_complete',
        variant_id: 'main_street_complete_v3',
        profile_id: 'complete-main-18m-tropical-v1',
        profile_version: 1,
        appearance_kit_id: 'tropical_boulevard_v1',
        target: { target_type: 'street_segment', row_width_m: 18, length_m: 240 },
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
    ...fixtures.parkedVehicles,
    ...fixtures.transitShelters,
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
    expect(first.trees).toHaveLength(MAX_MAIN_STREET_TREES_PER_ZONE);
    expect(first.lights).toHaveLength(MAX_MAIN_STREET_LIGHTS_PER_ZONE);
    expect(first.benches).toHaveLength(MAX_STREET_BENCHES_PER_ZONE);
    expect(first.drains).toHaveLength(MAX_STREET_DRAINS_PER_ZONE);
    expect(first.sidewalkJoints).toHaveLength(MAX_STREET_SIDEWALK_JOINTS_PER_ZONE);
    expect(first.bollards).toEqual([]);
    expect(first.plantingCells).toHaveLength(MAX_STREET_PLANTING_CELLS_PER_ZONE);
    expect(first.wasteBins.length).toBeGreaterThan(0);
    expect(first.wasteBins.length).toBeLessThanOrEqual(MAX_STREET_WASTE_BINS_PER_ZONE);
    expect(first.bikeRacks.length).toBeGreaterThan(0);
    expect(first.bikeRacks.length).toBeLessThanOrEqual(MAX_STREET_BIKE_RACKS_PER_ZONE);
    expect(first.parkedVehicles).toHaveLength(MAX_MAIN_STREET_VEHICLES_PER_ZONE);
    expect(first.transitShelters).toHaveLength(1);
  });

  it('adds a bounded deterministic woonerf play cadence beside the chicane', () => {
    const planters = buildWoonerfPlanterPlacements(straightPoints(1_000), 5);
    const playNodes = buildWoonerfPlayPlacements(planters);
    expect(playNodes).toHaveLength(MAX_WOONERF_PLAY_NODES_PER_ZONE);
    expect(buildWoonerfPlayPlacements(planters)).toEqual(playNodes);
    playNodes.forEach((node, index) => {
      const sourcePlanter = planters[2 + index * 4];
      expect(Math.hypot(node.x - sourcePlanter.x, node.y - sourcePlanter.y)).toBeCloseTo(2.35, 8);
      expect(Math.sign(node.y)).toBe(Math.sign(sourcePlanter.y));
    });
  });

  it('places yield signs only at bounded entry thresholds and follows cross-slope', () => {
    const points = straightPoints(80);
    const terrain = points.map(() => ({
      centerZ: 10,
      leftZ: 11,
      rightZ: 9,
      halfWidthM: 3,
    }));
    const signs = buildYieldStreetEntrySignPlacements(points, 3, terrain);
    expect(signs).toHaveLength(2);
    expect(signs.map((sign) => sign.stationM)).toEqual([6, 74]);
    expect(signs.map((sign) => sign.side)).toEqual([-1, 1]);
    expect(signs[0].offsetM).toBeCloseTo(-2.52, 8);
    expect(signs[1].offsetM).toBeCloseTo(2.52, 8);
    expect(signs[0].z).toBeLessThan(10);
    expect(signs[1].z).toBeGreaterThan(10);
  });

  it('gives the complete main street its tree-lined, lit, parked-car signature', () => {
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(240),
      profile: mainStreetProfile(),
      sectionScale: 1,
      enabled: true,
    });
    expect(fixtures.trees.every((tree) => tree.canopyClass === 'mature_deciduous')).toBe(true);
    expect(fixtures.lights.every((light) => light.fixtureStyle === 'traditional')).toBe(true);
    expect(fixtures.parkedVehicles.length).toBeGreaterThan(20);
    expect(fixtures.parkedVehicles.length).toBeLessThanOrEqual(MAX_MAIN_STREET_VEHICLES_PER_ZONE);

    const treeStations = [...new Set(fixtures.trees.map((tree) => tree.stationM))];
    treeStations.slice(1).forEach((stationM, index) => {
      expect(stationM - treeStations[index]).toBeCloseTo(MAIN_STREET_TREE_SPACING_M, 8);
    });
    const lightStations = [...new Set(fixtures.lights.map((light) => light.stationM))];
    lightStations.slice(1).forEach((stationM, index) => {
      expect(stationM - lightStations[index])
        .toBeCloseTo(MAIN_STREET_LIGHT_SPACING_M, 8);
    });
    lightStations.forEach((stationM) => {
      const stationLights = fixtures.lights.filter((light) => light.stationM === stationM);
      expect(stationLights).toHaveLength(2);
      expect(stationLights.some((light) => light.offsetM < 0)).toBe(true);
      expect(stationLights.some((light) => light.offsetM > 0)).toBe(true);
    });
    const vehicleStations = [...new Set(fixtures.parkedVehicles.map((vehicle) => vehicle.stationM))];
    vehicleStations.slice(1).forEach((stationM, index) => {
      expect(stationM - vehicleStations[index]).toBeCloseTo(MAIN_STREET_VEHICLE_SPACING_M, 8);
    });
    expect(fixtures.transitShelters).toHaveLength(1);
    const furnishingBand = mainStreetProfile()!.bands.find((band) => (
      band.kind === 'planting'
      && fixtures.transitShelters[0].offsetM >= band.startM
      && fixtures.transitShelters[0].offsetM <= band.endM
    ));
    expect(furnishingBand).toBeDefined();
    expect(fixtures.transitShelters[0].surfaceLiftM).toBe(furnishingBand!.liftM);
    expect(fixtures.transitShelters[0].scale).toBeLessThanOrEqual(0.85);
    expect(fixtures.transitShelters[0].offsetM - fixtures.transitShelters[0].footprintDepthM / 2)
      .toBeGreaterThanOrEqual(
        fixtures.transitShelters[0].bandStartM + STREET_TRANSIT_SHELTER_EDGE_CLEARANCE_M - 1e-8,
      );
    expect(fixtures.transitShelters[0].offsetM + fixtures.transitShelters[0].footprintDepthM / 2)
      .toBeLessThanOrEqual(
        fixtures.transitShelters[0].bandEndM - STREET_TRANSIT_SHELTER_EDGE_CLEARANCE_M + 1e-8,
      );
  });

  it.each([
    ['modern_minimalist_v1', 'columnar_deciduous', 'contemporary'],
    ['european_cobblestone_v1', 'pollarded_deciduous', 'traditional'],
    ['tropical_boulevard_v1', 'tropical_palm', 'contemporary'],
  ] as const)('gives %s an archetype-owned canopy and light silhouette', (
    appearanceKitId,
    canopyClass,
    fixtureStyle,
  ) => {
    const base = mainStreetProfile()!;
    const profile = {
      ...base,
      appearanceKitId,
      appearance: STREET_APPEARANCE_KITS[appearanceKitId as StreetAppearanceKitId],
    };
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(180),
      profile,
      sectionScale: 1,
      enabled: true,
    });
    expect(fixtures.trees.length).toBeGreaterThan(0);
    expect(fixtures.trees.every((tree) => tree.canopyClass === canopyClass)).toBe(true);
    expect(fixtures.lights.every((light) => light.fixtureStyle === fixtureStyle)).toBe(true);
  });

  it('keeps tropical-main furniture and its shelter out of the planted centre median', () => {
    const profile = tropicalMainStreetProfile()!;
    const median = profile.bands.find((band) => band.kind === 'planting')!;
    const sidewalks = profile.bands.filter((band) => band.kind === 'sidewalk');
    expect(profile.appearanceKitId).toBe('tropical_boulevard_v1');
    expect(profile.bands.filter((band) => band.kind === 'planting')).toHaveLength(1);
    expect(median.startM).toBeLessThan(0);
    expect(median.endM).toBeGreaterThan(0);

    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(180),
      profile,
      sectionScale: 1,
      enabled: true,
    });
    expect(fixtures.trees.length).toBeGreaterThan(0);
    expect(fixtures.trees.every((tree) => (
      tree.offsetM >= median.startM && tree.offsetM <= median.endM
    ))).toBe(true);
    expect(fixtures.plantingCells).toEqual([]);
    expect(fixtures.transitShelters).toHaveLength(1);

    const sideFixtures = [
      ...fixtures.benches,
      ...fixtures.lights,
      ...fixtures.wasteBins,
      ...fixtures.bikeRacks,
      ...fixtures.transitShelters,
    ];
    expect(sideFixtures.length).toBeGreaterThan(0);
    sideFixtures.forEach((fixture) => {
      expect(fixture.offsetM < median.startM || fixture.offsetM > median.endM).toBe(true);
      expect(sidewalks.some((band) => (
        fixture.offsetM >= band.startM && fixture.offsetM <= band.endM
      ))).toBe(true);
    });
  });

  it('gives the narrow residential archetype two mature tree rows at a 9-12 m rhythm', () => {
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(240),
      profile: narrowResidentialProfile(),
      sectionScale: 1,
      enabled: true,
    });
    expect(fixtures.trees.length).toBeGreaterThan(30);
    expect(fixtures.trees.length).toBeLessThanOrEqual(MAX_NARROW_RESIDENTIAL_TREES_PER_ZONE);
    expect(fixtures.trees.every((tree) => tree.canopyClass === 'mature_deciduous')).toBe(true);
    const rowOffsets = [...new Set(fixtures.trees.map((tree) => tree.offsetM))].sort((a, b) => a - b);
    expect(rowOffsets).toHaveLength(2);
    rowOffsets.forEach((offsetM) => {
      const row = fixtures.trees
        .filter((tree) => tree.offsetM === offsetM)
        .sort((left, right) => left.stationM - right.stationM);
      expect(row.length).toBeGreaterThan(15);
      row.slice(1).forEach((tree, index) => {
        const spacingM = tree.stationM - row[index].stationM;
        expect(spacingM).toBeGreaterThanOrEqual(9);
        expect(spacingM).toBeLessThanOrEqual(12);
        expect(spacingM).toBeCloseTo(NARROW_RESIDENTIAL_TREE_SPACING_M, 8);
      });
    });
  });

  it('uses a bounded alternating row of traditional residential lights', () => {
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(240),
      profile: narrowResidentialProfile(),
      sectionScale: 1,
      enabled: true,
    });
    expect(fixtures.lights.length).toBeGreaterThan(5);
    expect(fixtures.lights.length).toBeLessThanOrEqual(MAX_NARROW_RESIDENTIAL_LIGHTS_PER_ZONE);
    expect(fixtures.lights.every((light) => light.fixtureStyle === 'traditional')).toBe(true);
    fixtures.lights.slice(1).forEach((light, index) => {
      expect(light.stationM - fixtures.lights[index].stationM)
        .toBeCloseTo(NARROW_RESIDENTIAL_LIGHT_SPACING_M, 8);
      expect(Math.sign(light.offsetM)).not.toBe(Math.sign(fixtures.lights[index].offsetM));
    });
  });

  it('fits deterministic parallel sedans and SUVs wholly inside residential parking bands', () => {
    const options = {
      points: straightPoints(240),
      profile: narrowResidentialProfile(),
      sectionScale: 1,
      enabled: true,
    } as const;
    const fixtures = buildStreetFamilyFixturePlacements(options);
    expect(buildStreetFamilyFixturePlacements(options)).toEqual(fixtures);
    expect(fixtures.parkedVehicles.length).toBeGreaterThan(6);
    expect(fixtures.parkedVehicles.length)
      .toBeLessThanOrEqual(MAX_NARROW_RESIDENTIAL_VEHICLES_PER_ZONE);
    expect(new Set(fixtures.parkedVehicles.map((vehicle) => vehicle.vehicleType)))
      .toEqual(new Set(['sedan', 'suv']));
    fixtures.parkedVehicles.forEach((vehicle) => {
      expect(Math.abs(Math.sin(vehicle.yawRad))).toBeCloseTo(0, 8);
      expect(vehicle.offsetM - vehicle.widthM / 2).toBeGreaterThanOrEqual(
        vehicle.bandStartM + STREET_PARKED_VEHICLE_EDGE_CLEARANCE_M - 1e-8,
      );
      expect(vehicle.offsetM + vehicle.widthM / 2).toBeLessThanOrEqual(
        vehicle.bandEndM - STREET_PARKED_VEHICLE_EDGE_CLEARANCE_M + 1e-8,
      );
    });
  });

  it('keeps the complete parked-vehicle footprint outside the 12 m node clearance', () => {
    const clearance = { x: 80, y: 0 };
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(240),
      profile: narrowResidentialProfile(),
      sectionScale: 1,
      clearancePoints: [clearance],
      enabled: true,
    });
    fixtures.parkedVehicles.forEach((vehicle) => {
      const footprintRadiusM = Math.hypot(vehicle.lengthM, vehicle.widthM) / 2;
      expect(Math.hypot(vehicle.x - clearance.x, vehicle.y - clearance.y))
        .toBeGreaterThanOrEqual(
          STREET_NODE_FIXTURE_CLEARANCE_M + footprintRadiusM - 1e-8,
        );
    });
  });

  it('distributes capped stations across both ends of a long street', () => {
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(1_000),
      profile: mainStreetProfile(),
      sectionScale: 1,
      enabled: true,
    });
    const stations = [...new Set(fixtures.trees.map((tree) => tree.stationM))];
    expect(stations).toHaveLength(MAX_MAIN_STREET_TREES_PER_ZONE / 2);
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

  it('places drainage, joints and tree grates in their engineered bands without invented cycle protection', () => {
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
    expect(profile.bands.some((band) => band.kind === 'buffer' || band.kind === 'cycle')).toBe(false);
    expect(fixtures.bollards).toEqual([]);
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
    expect(fixtures.bollards).toEqual([]);
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
      parkedVehicles: [],
      transitShelters: [],
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
          variant_id: 'green_alley_v0',
          profile_id: 'green-alley-v1',
          profile_version: 1,
          appearance_kit_id: 'green_corridor_v1',
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
