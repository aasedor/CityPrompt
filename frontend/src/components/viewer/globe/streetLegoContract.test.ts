import { describe, expect, it } from 'vitest';

import { PUBLIC_REALM_STREET_SELECTIONS } from './streetFamilyCatalog';
import {
  validatePublicRealmStreetRecipe,
  validateStreetRecipeProperties,
} from './streetLegoContract';

function recipe(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    schema_version: 1,
    family_id: 'street_complete_main_22m',
    family_version: 1,
    kind: 'street',
    generator: 'street_section',
    archetype_id: 'main_street_complete',
    variant_id: 'main_street_complete_v2',
    profile_id: 'complete-main-22m-v1',
    profile_version: 1,
    appearance_kit_id: 'timber_biophilic',
    target: { target_type: 'street_segment', row_width_m: 22, length_m: 80 },
    catalog_fingerprint: 'a'.repeat(64),
    capability_fingerprint: 'b'.repeat(64),
    recipe_hash: 'c'.repeat(64),
    ...overrides,
  };
}

describe('strict Public Realm LEGO street recipe validation', () => {
  it('accepts a structurally compatible compiled V1 street recipe', () => {
    expect(validatePublicRealmStreetRecipe(recipe())).toMatchObject({
      valid: true,
      recipe: {
        familyId: 'street_complete_main_22m',
        archetypeId: 'main_street_complete',
        variantId: 'main_street_complete_v2',
        appearanceKitId: 'european_cobblestone_v1',
        targetRowM: 22,
      },
    });
  });

  it('canonicalizes the exact historical ordinal palette on saved projects', () => {
    expect(validatePublicRealmStreetRecipe(recipe({
      variant_id: 'main_street_complete_v0',
      appearance_kit_id: 'calgary_contemporary_native',
    }))).toMatchObject({
      valid: true,
      recipe: { appearanceKitId: 'classic_tree_lined_v1' },
    });
    expect(validatePublicRealmStreetRecipe(recipe({
      variant_id: 'main_street_complete_v0',
      appearance_kit_id: 'timber_biophilic',
    }))).toMatchObject({ valid: false, code: 'appearance_incompatible' });

    expect(validatePublicRealmStreetRecipe(recipe({
      family_id: 'street_local_public_realm',
      archetype_id: 'narrow_residential_street',
      variant_id: 'narrow_residential_street_v2',
      appearance_kit_id: 'timber_biophilic',
      target: { target_type: 'street_segment', row_width_m: 10, length_m: 80 },
    }))).toMatchObject({
      valid: true,
      recipe: { appearanceKitId: 'european_cobblestone_v1' },
    });
  });

  it.each([
    [
      'trail',
      {
        family_id: 'street_local_public_realm',
        archetype_id: 'multi_use_trail',
        variant_id: 'multi_use_trail_v1',
        appearance_kit_id: 'heritage_brick_stone',
        target: { target_type: 'street_segment', row_width_m: 4, length_m: 80 },
      },
    ],
    [
      'roundabout',
      {
        family_id: 'street_compact_roundabout',
        archetype_id: 'roundabout',
        variant_id: 'roundabout_v0',
        appearance_kit_id: 'calgary_contemporary_native',
        target: {
          target_type: 'street_node', approach_row_width_m: 22, diameter_m: 28, arm_count: 4,
        },
      },
    ],
    [
      'protected intersection',
      {
        family_id: 'street_four_way_intersection',
        archetype_id: 'protected_intersection',
        variant_id: 'protected_intersection_v0',
        appearance_kit_id: 'calgary_contemporary_native',
        target: {
          target_type: 'street_node', approach_row_width_m: 22, diameter_m: 28, arm_count: 4,
        },
      },
    ],
  ])('does not apply ordinal appearance migration to an incompatible %s family', (_, overrides) => {
    expect(validatePublicRealmStreetRecipe(recipe(overrides))).toMatchObject({
      valid: false,
      code: 'appearance_incompatible',
    });
  });

  it('accepts every exact executable selection with its mapped appearance', () => {
    for (const selection of PUBLIC_REALM_STREET_SELECTIONS) {
      const target = selection.targetType === 'street_node'
        ? { target_type: 'street_node', approach_row_width_m: 22, diameter_m: 28, arm_count: 4 }
        : { target_type: 'street_segment', row_width_m: selection.rowWidthM ?? 10, length_m: 80 };
      const result = validatePublicRealmStreetRecipe(recipe({
        family_id: selection.familyId,
        archetype_id: selection.archetypeId,
        variant_id: selection.variantId,
        appearance_kit_id: selection.appearanceKitId,
        ...(selection.componentSetIds ? { component_set_ids: selection.componentSetIds, profile_id: selection.profileId } : {}),
        target,
      }));
      expect(result, `${selection.familyId}/${selection.variantId}`).toMatchObject({ valid: true });
    }
  });

  it.each([
    ['schema_version', 2, 'schema_version_unsupported'],
    ['schema_version', '1', 'schema_version_unsupported'],
    ['family_id', 'not_a_family', 'family_not_found'],
    ['family_id', 'street-complete-main-22m', 'family_not_found'],
    ['family_version', 2, 'family_version_unsupported'],
    ['family_version', '1', 'family_version_unsupported'],
    ['kind', 'park', 'kind_incompatible'],
    ['generator', 'park_kit', 'generator_incompatible'],
    ['archetype_id', 'toronto_victorian_residential_street', 'source_incompatible'],
    ['variant_id', 'main_street_complete_v9', 'variant_incompatible'],
    ['appearance_kit_id', 'heritage_brick_stone', 'appearance_incompatible'],
  ])('fails closed when %s is incompatible', (field, value, code) => {
    expect(validatePublicRealmStreetRecipe(recipe({ [field]: value }))).toMatchObject({
      valid: false,
      code,
    });
  });

  it('requires the exact target type and positive metric width', () => {
    expect(validatePublicRealmStreetRecipe(recipe({
      target: { target_type: 'street_node', approach_row_width_m: 22, arm_count: 4 },
    }))).toMatchObject({ valid: false, code: 'target_incompatible' });
    expect(validatePublicRealmStreetRecipe(recipe({
      target: { target_type: 'street_segment', row_width_m: 0, length_m: 80 },
    }))).toMatchObject({ valid: false, code: 'target_incompatible' });
  });

  it.each([
    ['recipe_hash', undefined],
    ['recipe_hash', 'not-a-sha256'],
    ['capability_fingerprint', 'A'.repeat(64)],
    ['catalog_fingerprint', 'a'.repeat(63)],
  ])('rejects a missing or malformed canonical integrity field %s', (field, value) => {
    expect(validatePublicRealmStreetRecipe(recipe({ [field]: value }))).toMatchObject({
      valid: false,
      code: 'integrity_incompatible',
    });
  });

  it('requires the backend profile identity', () => {
    expect(validatePublicRealmStreetRecipe(recipe({ profile_id: '' }))).toMatchObject({
      valid: false,
      code: 'profile_incompatible',
    });
    expect(validatePublicRealmStreetRecipe(recipe({ profile_version: 0 }))).toMatchObject({
      valid: false,
      code: 'profile_incompatible',
    });
  });

  it('keeps both frontend node families four-arm consistent', () => {
    for (const [familyId, archetypeId, variantId, appearanceKitId] of [
      ['street_four_way_intersection', 'protected_intersection', 'protected_intersection_v0', 'dutch_corner_islands_v1'],
      ['street_compact_roundabout', 'roundabout', 'roundabout_v0', 'classic_tree_lined_v1'],
    ]) {
      const base = recipe({
        family_id: familyId,
        archetype_id: archetypeId,
        variant_id: variantId,
        appearance_kit_id: appearanceKitId,
      });
      expect(validatePublicRealmStreetRecipe({
        ...base,
        target: { target_type: 'street_node', approach_row_width_m: 22, diameter_m: 28, arm_count: 4 },
      })).toMatchObject({ valid: true });
      expect(validatePublicRealmStreetRecipe({
        ...base,
        target: { target_type: 'street_node', approach_row_width_m: 22, diameter_m: 28, arm_count: 5 },
      })).toMatchObject({ valid: false, code: 'target_incompatible' });
    }
  });

  it('can gate Direct readiness against the persisted source identity', () => {
    expect(validateStreetRecipeProperties({
      road_archetype_id: 'main_street_complete',
      road_selected_variant_id: 'main_street_complete_v2',
      public_realm_lego: recipe(),
    })).toMatchObject({ valid: true });
    expect(validateStreetRecipeProperties({
      road_archetype_id: 'yield_street',
      public_realm_lego: recipe(),
    })).toMatchObject({ valid: false, code: 'source_identity_mismatch' });
  });
});
