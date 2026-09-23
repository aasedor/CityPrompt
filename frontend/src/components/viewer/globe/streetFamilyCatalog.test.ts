import { describe, expect, it } from 'vitest';

import {
  PUBLIC_REALM_STREET_CATALOG_FINGERPRINT,
  PUBLIC_REALM_STREET_FAMILIES,
  PUBLIC_REALM_STREET_SELECTIONS,
  fingerprintPublicRealmStreetCatalog,
  resolveStreetAppearanceKit,
} from './streetFamilyCatalog';

describe('Public Realm LEGO street family catalog', () => {
  it('exposes the canonical families plus the saved-project main-street envelope', () => {
    expect(Object.keys(PUBLIC_REALM_STREET_FAMILIES).sort()).toEqual([
      'street_compact_roundabout',
      'street_complete_main_18m',
      'street_complete_main_22m',
      'street_four_way_intersection',
      'street_local_public_realm',
    ]);
    expect(Object.values(PUBLIC_REALM_STREET_FAMILIES).every((family) => family.familyVersion === 1)).toBe(true);
  });

  it('keeps local sources multi-profile and locks both main envelopes to the approved 18 m program', () => {
    const local = PUBLIC_REALM_STREET_FAMILIES.street_local_public_realm;
    const main = PUBLIC_REALM_STREET_FAMILIES.street_complete_main_18m;
    const savedEnvelope = PUBLIC_REALM_STREET_FAMILIES.street_complete_main_22m;
    expect(local.nativeRowM).toBeNull();
    expect(local.crossSection).toEqual([]);
    expect(main.crossSection.reduce((sum, band) => sum + band.widthM, 0)).toBeCloseTo(18, 6);
    expect(savedEnvelope.crossSection).toEqual(main.crossSection);
    expect(main.crossSection.some((band) => band.type === 'cycle_track')).toBe(false);
    expect(local.sourceArchetypeIds).toEqual(expect.arrayContaining([
      'yield_street', 'narrow_residential_street', 'woonerf_shared_street',
      'green_alley', 'toronto_laneway', 'calgary_local', 'multi_use_trail',
      'neighborhood_greenway',
    ]));
    expect(local.sourceArchetypeIds).not.toContain('toronto_victorian_residential_street');
  });

  it('aligns node and special-program appearance identities with the server contract', () => {
    expect(PUBLIC_REALM_STREET_FAMILIES.street_four_way_intersection.sourceArchetypeIds)
      .toEqual(['protected_intersection']);
    expect(PUBLIC_REALM_STREET_FAMILIES.street_four_way_intersection.defaultAppearanceKitId)
      .toBe('dutch_corner_islands_v1');
    expect(PUBLIC_REALM_STREET_FAMILIES.street_compact_roundabout.defaultAppearanceKitId)
      .toBe('classic_tree_lined_v1');
    expect(PUBLIC_REALM_STREET_FAMILIES.street_compact_roundabout.sourceArchetypeIds)
      .toEqual(['roundabout']);
    expect(PUBLIC_REALM_STREET_FAMILIES.street_compact_roundabout.supportedNodeArmCounts)
      .toEqual([4]);
  });

  it('maps card-owned v0 identities instead of a generic ordinal palette', () => {
    const appearanceFor = (familyId: string, variantId: string) => (
      PUBLIC_REALM_STREET_SELECTIONS.find((selection) => (
        selection.familyId === familyId && selection.variantId === variantId
      ))?.appearanceKitId
    );
    expect(appearanceFor('street_local_public_realm', 'narrow_residential_street_v0'))
      .toBe('classic_tree_lined_v1');
    expect(appearanceFor('street_local_public_realm', 'woonerf_shared_street_v0'))
      .toBe('dutch_woonerf_v1');
    expect(appearanceFor('street_complete_main_18m', 'main_street_complete_v0'))
      .toBe('classic_tree_lined_v1');
    expect(appearanceFor('street_local_public_realm', 'green_alley_v0'))
      .toBe('green_corridor_v1');
    expect(appearanceFor('street_local_public_realm', 'toronto_laneway_v0'))
      .toBe('calgary_contemporary_native');
    expect(appearanceFor('street_local_public_realm', 'neighborhood_greenway_v0'))
      .toBe('green_corridor_v1');
    for (const archetypeId of [
      'yield_street',
      'woonerf_shared_street',
      'calgary_local',
      'green_alley',
      'toronto_laneway',
    ]) {
      expect(PUBLIC_REALM_STREET_SELECTIONS
        .filter((selection) => selection.archetypeId === archetypeId)
        .map((selection) => selection.variantId))
        .toEqual([`${archetypeId}_v0`]);
    }
  });

  it('fingerprints the executable contract deterministically', () => {
    expect(PUBLIC_REALM_STREET_CATALOG_FINGERPRINT).toBe(fingerprintPublicRealmStreetCatalog());
    expect(PUBLIC_REALM_STREET_CATALOG_FINGERPRINT).toMatch(/^street-v1-[0-9a-f]{16}$/);
  });

  it('selects an explicit appearance kit and safely defaults unknown values', () => {
    const family = PUBLIC_REALM_STREET_FAMILIES.street_complete_main_18m;
    expect(resolveStreetAppearanceKit(family, 'european_cobblestone_v1').id)
      .toBe('european_cobblestone_v1');
    expect(resolveStreetAppearanceKit(family, 'not-installed').id)
      .toBe(family.defaultAppearanceKitId);
  });
});
