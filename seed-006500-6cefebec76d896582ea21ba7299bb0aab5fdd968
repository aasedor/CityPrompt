import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';

import {
  NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS,
  PARK_LEGO_FAMILY_VERSION,
  PARK_PROGRAM_MODULE_SPEC,
  isExecutableParkLegoFamily,
  resolveParkLegoAppearance,
  resolveParkLegoContract,
  resolveParkProgramAnchorLayout,
} from './parkLegoFamilies';

function zone(properties: Record<string, unknown>): Pick<SiteZone, 'properties' | 'zone_type'> {
  return { zone_type: 'green_space', properties };
}

const TRUSTED_CATALOG_FINGERPRINT = 'a'.repeat(64);
const TRUSTED_CAPABILITY_FINGERPRINT = 'b'.repeat(64);
const TRUSTED_RECIPE_HASH = 'c'.repeat(64);

function trustedRecipe(selection: Record<string, unknown>): Record<string, unknown> {
  return {
    schema_version: 1,
    kind: 'park',
    generator: 'park_kit',
    catalog_fingerprint: TRUSTED_CATALOG_FINGERPRINT,
    capability_fingerprint: TRUSTED_CAPABILITY_FINGERPRINT,
    recipe_hash: TRUSTED_RECIPE_HASH,
    ...selection,
  };
}

describe('Public Realm LEGO V1 park families', () => {
  it('prefers and validates the canonical nested compiler contract', () => {
    const candidate = zone({
      green_space_archetype_id: 'community_park',
      green_space_selected_variant_id: 'community_park_v0',
      public_realm_lego: trustedRecipe({
        family_id: 'park_neighborhood_community',
        family_version: 1,
        archetype_id: 'community_park',
        variant_id: 'community_park_v3',
        planting_structure: 'naturalistic_grove',
        appearance_kit_id: 'tropical_lush_v1',
      }),
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId: 'park_neighborhood_community',
      familyVersion: PARK_LEGO_FAMILY_VERSION,
      archetypeId: 'community_park',
      variantId: 'community_park_v3',
      plantingStructure: 'naturalistic_grove',
      source: 'public_realm_lego',
      supported: true,
    });
    expect(resolveParkLegoAppearance(candidate)).toMatchObject({
      label: 'Tropical Lush',
      materialPattern: 'tropical_lush',
      shadeStyle: 'thatched',
    });
  });

  it('normalizes legacy variant aliases without losing visual selection', () => {
    const candidate = zone({
      green_space_archetype_id: 'neighborhood_park',
      green_space_selected_variant_id: 'neighborhood_park_variant_2',
    });
    expect(resolveParkLegoContract(candidate)?.variantId).toBe('neighborhood_park_v2');
    expect(resolveParkLegoAppearance(candidate)).toMatchObject({
      familyId: 'park_neighborhood_community',
      variantIndex: 2,
      label: 'Natural Meadow',
      plantingStructure: 'naturalistic_grove',
      materialPattern: 'native_meadow',
    });
  });

  it('compiles a courtyard role to the approved pocket-park family', () => {
    const candidate = {
      zone_type: 'development_area' as const,
      properties: { _plan_role: 'courtyard' },
    };
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId: 'park_pocket_courtyard',
      archetypeId: 'urban_pocket_park',
      variantId: 'urban_pocket_park_v0',
    });
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
  });

  it('does not execute an unknown future family version', () => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: 'park_pocket_courtyard',
        family_version: 2,
        archetype_id: 'urban_pocket_park',
        variant_id: 'urban_pocket_park_v1',
        planting_structure: 'formal_quad',
        appearance_kit_id: 'modern_steel_turf_v1',
      }),
    });
    expect(resolveParkLegoContract(candidate)?.supported).toBe(false);
    expect(resolveParkLegoAppearance(candidate)).toBeNull();
    expect(isExecutableParkLegoFamily(candidate)).toBe(false);
  });

  it('rejects rather than repairing an incompatible nested selection', () => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: 'park_neighborhood_community',
        family_version: 1,
        archetype_id: 'neighborhood_park',
        variant_id: 'neighborhood_park_v0',
        planting_structure: 'formal_quad',
        appearance_kit_id: 'rustic_timber_gravel_v1',
      }),
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      archetypeId: 'neighborhood_park',
      variantId: 'neighborhood_park_v0',
      supported: false,
    });
    expect(resolveParkLegoAppearance(candidate)).toBeNull();
  });

  it.each([
    ['park_pocket_courtyard', 'urban_pocket_park', 'urban_pocket_park_v0', 'rustic_timber_gravel_v1', 'garden_courtyard'],
    ['park_neighborhood_community', 'neighborhood_park', 'neighborhood_park_v0', 'rustic_timber_gravel_v1', 'active_recreation'],
    ['park_civic_plaza', 'formal_civic_plaza', 'formal_civic_plaza_v0', 'neoclassical_stone_v1', 'paved_plaza'],
    ['park_linear_greenway', 'linear_park_greenway', 'linear_park_greenway_v0', 'rail_trail_v1', 'naturalistic_grove'],
    ['park_water_ecology', 'stormwater_retention_pond', 'stormwater_retention_pond_v0', 'naturalistic_pond_v1', 'reservoir_perimeter'],
  ])('recognizes exact backend family mapping %s', (
    familyId,
    archetypeId,
    variantId,
    appearanceKitId,
    plantingStructure,
  ) => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: familyId,
        family_version: 1,
        archetype_id: archetypeId,
        variant_id: variantId,
        appearance_kit_id: appearanceKitId,
        planting_structure: plantingStructure,
      }),
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId,
      archetypeId,
      variantId,
      appearanceKitId,
      plantingStructure,
      supported: true,
      source: 'public_realm_lego',
    });
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
  });

  it('does not coerce a civic family carrying a neighborhood archetype', () => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: 'park_civic_plaza',
        family_version: 1,
        archetype_id: 'neighborhood_park',
        variant_id: 'neighborhood_park_v0',
        appearance_kit_id: 'rustic_timber_gravel_v1',
        planting_structure: 'active_recreation',
      }),
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId: 'park_civic_plaza',
      archetypeId: 'neighborhood_park',
      supported: false,
    });
    expect(resolveParkLegoAppearance(candidate)).toBeNull();
  });

  it('does not normalize nested compiler identities or fall back to legacy fields', () => {
    const candidate = zone({
      green_space_archetype_id: 'urban_pocket_park',
      public_realm_lego: trustedRecipe({
        family_id: 'park-pocket-courtyard',
        family_version: 1,
        archetype_id: 'urban_pocket_park',
        variant_id: 'urban_pocket_park_v0',
        appearance_kit_id: 'rustic_timber_gravel_v1',
        planting_structure: 'garden_courtyard',
      }),
    });
    expect(resolveParkLegoContract(candidate)).toBeNull();
    expect(resolveParkLegoAppearance(candidate)).toBeNull();
    expect(isExecutableParkLegoFamily(candidate)).toBe(false);
  });

  it.each([
    ['schema version', { schema_version: '1' }],
    ['family version', { family_version: '1' }],
    ['kind', { kind: 'Park' }],
    ['generator', { generator: 'park-kit' }],
    ['catalog fingerprint', { catalog_fingerprint: 'A'.repeat(64) }],
    ['capability fingerprint', { capability_fingerprint: 'short' }],
    ['recipe hash', { recipe_hash: `${'d'.repeat(63)}g` }],
  ])('rejects a nested recipe with an untrusted %s', (_label, override) => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: 'park_pocket_courtyard',
        family_version: 1,
        archetype_id: 'urban_pocket_park',
        variant_id: 'urban_pocket_park_v0',
        appearance_kit_id: 'rustic_timber_gravel_v1',
        planting_structure: 'garden_courtyard',
        ...override,
      }),
    });
    expect(resolveParkLegoContract(candidate)?.supported).toBe(false);
    expect(isExecutableParkLegoFamily(candidate)).toBe(false);
  });

  it('gives every visual variant a materially distinct palette or pattern', () => {
    const appearances = Array.from({ length: 4 }, (_, index) => resolveParkLegoAppearance(zone({
      green_space_archetype_id: 'urban_pocket_park',
      green_space_selected_variant_id: `urban_pocket_park_v${index}`,
    }))!);
    expect(new Set(appearances.map((entry) => entry.materialPattern)).size).toBe(4);
    expect(new Set(appearances.map((entry) => entry.palette.path)).size).toBe(4);
    expect(new Set(appearances.map((entry) => entry.palette.benchSeat)).size).toBe(4);
  });

  it('locks playground, shade and pavilion modules to real metre dimensions', () => {
    expect(PARK_PROGRAM_MODULE_SPEC.playground.safetyDiameterM).toBe(12);
    expect(PARK_PROGRAM_MODULE_SPEC.playground.towerHeightM).toBe(3.2);
    expect(PARK_PROGRAM_MODULE_SPEC.playground.slideLengthM).toBe(3.4);
    expect(PARK_PROGRAM_MODULE_SPEC.shade).toEqual({
      spanM: 7.2,
      lowEdgeHeightM: 3,
      highEdgeHeightM: 3.7,
    });
    expect(PARK_PROGRAM_MODULE_SPEC.pavilion).toEqual({
      widthM: 6,
      depthM: 5,
      clearHeightM: 2.8,
      roofHeightM: 1.15,
    });
  });

  it('shares exact program anchors with the neighborhood ground profile', () => {
    const candidate = zone({ green_space_archetype_id: 'neighborhood_park' });
    expect(resolveParkProgramAnchorLayout(candidate))
      .toBe(NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS);
    expect(resolveParkProgramAnchorLayout(zone({ green_space_archetype_id: 'urban_pocket_park' })))
      .toBeUndefined();
  });
});
