import { describe, expect, it } from 'vitest';

import {
  MAX_PARK_MICRODETAIL_CANDIDATES_PER_KIND,
  MAX_PARK_MICRODETAIL_ELEMENTS_PER_PLACEMENT,
  MAX_PARK_MICRODETAIL_PLACEMENTS,
  MAX_PARK_MICRODETAIL_STATIONS_PER_SOURCE,
  boundedParkMicrodetailStationCount,
  buildParkMicrodetailElementOffsets,
  buildParkMicrodetailFamily,
  mergeParkMicrodetailCandidateTiers,
  parkMicrodetailFootprintFits,
  resolveParkMicrodetailGuideKind,
  type ParkMicrodetailFamilyInput,
  type ParkMicrodetailPlacement,
} from './parkMicrodetailFamilies';
import type { ParkLegoFamilyId } from './parkLegoFamilies';

const boundary = [
  { x: -40, y: -30 },
  { x: 40, y: -30 },
  { x: 40, y: 30 },
  { x: -40, y: 30 },
] as const;

const guides = [
  {
    kind: 'circulation' as const,
    points: [{ x: -34, y: 0 }, { x: 34, y: 0 }],
    widthM: 3.2,
    bufferM: 0.4,
  },
  {
    kind: 'water' as const,
    points: [
      { x: 12, y: 8 },
      { x: 31, y: 8 },
      { x: 31, y: 23 },
      { x: 12, y: 23 },
    ],
    closed: true,
    isArea: true,
    bufferM: 1,
  },
  {
    kind: 'fixed_program' as const,
    points: [
      { x: -30, y: 8 },
      { x: -10, y: 8 },
      { x: -10, y: 23 },
      { x: -30, y: 23 },
    ],
    closed: true,
    isArea: true,
    bufferM: 1.2,
  },
] as const;

const primaryPlacements = [
  { x: -30, y: -18, footprintRadiusM: 1.7, kind: 'tree' as const },
  { x: -15, y: -18, footprintRadiusM: 1.7, kind: 'tree' as const },
  { x: 0, y: -18, footprintRadiusM: 1.7, kind: 'tree' as const },
  { x: 18, y: -18, footprintRadiusM: 1.7, kind: 'tree' as const },
  { x: -3, y: 16, footprintRadiusM: 4.2, kind: 'pavilion' as const },
] as const;

function input(familyId: ParkLegoFamilyId): ParkMicrodetailFamilyInput {
  return {
    zoneId: 'park-a',
    familyId,
    boundary,
    guides,
    primaryPlacements,
  };
}

function kinds(placements: readonly ParkMicrodetailPlacement[]): Set<string> {
  return new Set(placements.map(({ kind }) => kind));
}

describe('park microdetail families', () => {
  it.each([
    'park_skate_archetype_v0',
    'park_inclusive_playground_v0',
    'park_dog_archetype_v0',
    'park_splash_pad_v0',
    'park_community_garden_v0',
    'park_tennis_cluster_v0',
    'park_nature_play_v0',
    'park_pump_track_v0',
    'park_outdoor_fitness_v0',
    'park_memorial_garden_v0',
  ] as const)('leaves exact kit %s free of generic microdetail', (familyId) => {
    expect(buildParkMicrodetailFamily(input(familyId))).toEqual([]);
  });

  it.each([
    ['park_basketball_court_v0', ['light', 'bin', 'bike_rack', 'picnic_table', 'drinking_fountain']],
    ['park_pocket_courtyard', ['shrub', 'perennial', 'light', 'bin', 'bike_rack', 'bollard', 'tree_grate']],
    ['park_neighborhood_community', ['shrub', 'ornamental_grass', 'boulder', 'light', 'bike_rack', 'picnic_table', 'drinking_fountain']],
    ['park_civic_plaza', ['perennial', 'light', 'bin', 'bike_rack', 'bollard', 'tree_grate']],
    ['park_linear_greenway', ['shrub', 'ornamental_grass', 'boulder', 'light', 'bollard', 'picnic_table']],
    ['park_water_ecology', ['reed', 'ornamental_grass', 'riprap', 'boulder', 'bollard']],
    ['park_ice_rink_multipurpose_v3', ['light', 'bollard', 'bin', 'bike_rack']],
    ['park_kayak_river_launch_v0', ['shrub', 'ornamental_grass', 'riprap', 'picnic_table', 'bollard']],
    ['park_tidal_marsh_cordgrass_v0', ['reed', 'ornamental_grass', 'shrub', 'riprap']],
    ['park_cinema_lawn_projection_v1', ['light', 'bollard', 'bin', 'bike_rack']],
    ['park_food_truck_permanent_v1', ['perennial', 'ornamental_grass', 'light', 'bin', 'bike_rack']],
    ['park_great_lawn_v2', ['shrub', 'ornamental_grass', 'picnic_table', 'bin', 'drinking_fountain']],
    ['park_campus_meadow_quad_v0', ['perennial', 'ornamental_grass', 'boulder', 'picnic_table', 'bike_rack']],
    ['park_urban_beach_family_v2', ['ornamental_grass', 'picnic_table', 'bin', 'bike_rack', 'drinking_fountain']],
    ['park_velodrome_open_air_v0', ['light', 'bollard', 'bin', 'bike_rack', 'drinking_fountain']],
    ['park_mtb_skills_dirt_v2', ['boulder', 'riprap', 'picnic_table', 'bin', 'bike_rack', 'drinking_fountain']],
  ] as const)('gives %s a recognizable, bounded signature', (familyId, expectedKinds) => {
    const placements = buildParkMicrodetailFamily(input(familyId));
    const actualKinds = kinds(placements);
    expect(placements.length).toBeGreaterThan(expectedKinds.length);
    expect(placements.length).toBeLessThanOrEqual(MAX_PARK_MICRODETAIL_PLACEMENTS);
    expect(expectedKinds.every((kind) => actualKinds.has(kind))).toBe(true);
    expect(placements.every((placement) => parkMicrodetailFootprintFits(
      placement,
      placement.footprintRadiusM,
      boundary,
      guides,
    ))).toBe(true);
  });

  it('is stable across rerenders and independent of input array identity', () => {
    const first = buildParkMicrodetailFamily(input('park_neighborhood_community'));
    const second = buildParkMicrodetailFamily({
      ...input('park_neighborhood_community'),
      boundary: boundary.map((point) => ({ ...point })),
      guides: guides.map((guide) => ({ ...guide, points: guide.points.map((point) => ({ ...point })) })),
      primaryPlacements: primaryPlacements.map((placement) => ({ ...placement })),
    });
    expect(second).toEqual(first);
  });

  it('honors device budgets and the global hard cap', () => {
    expect(buildParkMicrodetailFamily({
      ...input('park_water_ecology'),
      maxPlacements: 12,
    })).toHaveLength(12);
    expect(buildParkMicrodetailFamily({
      ...input('park_water_ecology'),
      maxPlacements: 10_000,
    }).length).toBeLessThanOrEqual(MAX_PARK_MICRODETAIL_PLACEMENTS);
  });

  it('keeps stormwater infrastructure ecological rather than recreational', () => {
    const placements = buildParkMicrodetailFamily(input('park_water_ecology'));
    expect(placements.some(({ kind }) => (
      kind === 'light' || kind === 'bin' || kind === 'picnic_table'
    ))).toBe(false);
  });

  it('reserves water, outlet/weir and route guides with explicit semantics', () => {
    expect(resolveParkMicrodetailGuideKind('park_water_ecology', 'ellipse')).toBe('water');
    expect(resolveParkMicrodetailGuideKind('park_water_ecology', 'rectangle'))
      .toBe('fixed_program');
    expect(resolveParkMicrodetailGuideKind('park_water_ecology', 'polyline'))
      .toBe('fixed_program');
    expect(resolveParkMicrodetailGuideKind('park_neighborhood_community', 'rectangle'))
      .toBeNull();
    expect(resolveParkMicrodetailGuideKind('park_neighborhood_community', 'basketball_court'))
      .toBe('fixed_program');
  });

  it('preserves preferred candidate tiers while bounding huge candidate sets', () => {
    const first = Array.from({ length: 500 }, (_, index) => `water-${index}`);
    const second = Array.from({ length: 500 }, (_, index) => `boundary-${index}`);
    const merged = mergeParkMicrodetailCandidateTiers([first, second], () => 0.37);
    expect(merged).toHaveLength(MAX_PARK_MICRODETAIL_CANDIDATES_PER_KIND);
    expect(merged.slice(0, 384).every((entry) => entry.startsWith('water-'))).toBe(true);
    expect(merged.slice(384).every((entry) => entry.startsWith('boundary-'))).toBe(true);
    expect(boundedParkMicrodetailStationCount(1_000_000, 0.5))
      .toBe(MAX_PARK_MICRODETAIL_STATIONS_PER_SOURCE);
  });

  it('reserves the rendered scaled assembly footprint, including rack triplets', () => {
    const placements = buildParkMicrodetailFamily(input('park_civic_plaza'));
    for (const placement of placements) {
      if (placement.kind === 'bike_rack') {
        expect(placement.footprintRadiusM)
          .toBeGreaterThanOrEqual(0.62 + 0.4 * placement.scale - 1e-7);
      } else if (placement.kind !== 'tree_grate') {
        expect(placement.footprintRadiusM).toBeGreaterThanOrEqual(0.22 * placement.scale);
      }
    }
  });

  it('expands clump elementCount deterministically within one bounded footprint', () => {
    const reed = buildParkMicrodetailFamily(input('park_water_ecology'))
      .find(({ kind }) => kind === 'reed');
    expect(reed).toBeDefined();
    const elements = buildParkMicrodetailElementOffsets(reed!);
    expect(elements).toHaveLength(Math.min(
      reed!.elementCount,
      MAX_PARK_MICRODETAIL_ELEMENTS_PER_PLACEMENT,
    ));
    expect(buildParkMicrodetailElementOffsets(reed!)).toEqual(elements);
    expect(elements.every(({ x, y }) => Math.hypot(x, y) <= reed!.footprintRadiusM * 0.54 + 1e-7))
      .toBe(true);
  });

  it('keeps ordinary details clear of primary objects and peer footprints', () => {
    const clearanceM = 0.25;
    const placements = buildParkMicrodetailFamily({
      ...input('park_neighborhood_community'),
      collisionClearanceM: clearanceM,
    });
    for (let index = 0; index < placements.length; index += 1) {
      const first = placements[index];
      for (let otherIndex = index + 1; otherIndex < placements.length; otherIndex += 1) {
        const second = placements[otherIndex];
        expect(Math.hypot(first.x - second.x, first.y - second.y) + 1e-7)
          .toBeGreaterThanOrEqual(first.footprintRadiusM + second.footprintRadiusM + clearanceM);
      }
      for (let primaryIndex = 0; primaryIndex < primaryPlacements.length; primaryIndex += 1) {
        if (first.sourcePrimaryIndex === primaryIndex) continue;
        const primary = primaryPlacements[primaryIndex];
        expect(Math.hypot(first.x - primary.x, first.y - primary.y) + 1e-7)
          .toBeGreaterThanOrEqual(first.footprintRadiusM + primary.footprintRadiusM + clearanceM);
      }
    }
  });

  it('rejects a circle whose centre fits but whose edge crosses the parcel or a guide buffer', () => {
    expect(parkMicrodetailFootprintFits({ x: 39.5, y: -5 }, 1, boundary, guides)).toBe(false);
    expect(parkMicrodetailFootprintFits({ x: 0, y: 2.2 }, 0.5, boundary, guides)).toBe(false);
    expect(parkMicrodetailFootprintFits({ x: 20, y: 15 }, 0.5, boundary, guides)).toBe(false);
    expect(parkMicrodetailFootprintFits({ x: 0, y: -10 }, 0.5, boundary, guides)).toBe(true);
  });
});
