import { describe, expect, it } from 'vitest';

import type { SiteZone } from '@/types';
import {
  MAX_STREET_BENCHES_PER_ZONE,
  MAX_STREET_FIXTURE_STATIONS,
  MAX_STREET_LIGHTS_PER_ZONE,
  MAX_STREET_TREES_PER_ZONE,
  STREET_BENCH_EDGE_CLEARANCE_M,
  buildStreetFamilyFixturePlacements,
  resolveBenchCenterInBand,
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

describe('street family furniture placement', () => {
  it('keeps the complete bench footprint inside its boulevard band', () => {
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(160),
      profile: mainStreetProfile(),
      sectionScale: 1,
      enabled: true,
    });
    expect(fixtures.benches.length).toBeGreaterThan(0);
    fixtures.benches.forEach((bench) => {
      const centerM = bench.y;
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
    const negativeSide = fixtures.benches.find((bench) => bench.y < 0);
    const positiveSide = fixtures.benches.find((bench) => bench.y > 0);
    expect(negativeSide).toBeDefined();
    expect(positiveSide).toBeDefined();
    const delta = Math.abs((negativeSide!.yawRad - positiveSide!.yawRad) % (Math.PI * 2));
    expect(Math.min(delta, Math.PI * 2 - delta)).toBeCloseTo(Math.PI, 8);
  });

  it('is deterministic and enforces per-station and per-fixture caps', () => {
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
  });

  it('reserves the accessible intersection core before selecting stations', () => {
    const fixtures = buildStreetFamilyFixturePlacements({
      points: straightPoints(180),
      profile: mainStreetProfile(),
      sectionScale: 1,
      clearancePoints: [{ x: 48, y: 0 }],
      enabled: true,
    });
    expect(fixtures.trees.some((tree) => Math.abs(tree.x - 48) < 12)).toBe(false);
    expect(fixtures.benches.some((bench) => Math.abs(bench.x - 48) < 10.8)).toBe(false);
  });

  it('does not force a bench into a furnishing band that is too narrow', () => {
    expect(resolveBenchCenterInBand(0, 0.5, 0.25, 0.9)).toBeNull();
    expect(resolveBenchCenterInBand(0, 1.2, 1.1, 0.9)).toBeCloseTo(0.832, 6);
  });

  it('does not add the generic family furniture pass to trails', () => {
    const trail = resolvePilotStreetSectionProfile('multi_use_trail');
    expect(buildStreetFamilyFixturePlacements({
      points: straightPoints(160),
      profile: trail,
      sectionScale: 1,
      enabled: true,
    })).toMatchObject({ trees: [], benches: [], lights: [], stationCount: 0 });
  });
});
