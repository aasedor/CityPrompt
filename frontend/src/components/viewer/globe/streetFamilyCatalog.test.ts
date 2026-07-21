import { describe, expect, it } from 'vitest';

import {
  PUBLIC_REALM_STREET_CATALOG_FINGERPRINT,
  PUBLIC_REALM_STREET_FAMILIES,
  fingerprintPublicRealmStreetCatalog,
  resolveStreetAppearanceKit,
} from './streetFamilyCatalog';

describe('Public Realm LEGO street family catalog', () => {
  it('exposes only the four versioned executable pilot families', () => {
    expect(Object.keys(PUBLIC_REALM_STREET_FAMILIES).sort()).toEqual([
      'street_compact_roundabout',
      'street_complete_main_22m',
      'street_four_way_intersection',
      'street_local_public_realm',
    ]);
    expect(Object.values(PUBLIC_REALM_STREET_FAMILIES).every((family) => family.familyVersion === 1)).toBe(true);
  });

  it('keeps local sources multi-profile and makes only the main street native exact 22 m', () => {
    const local = PUBLIC_REALM_STREET_FAMILIES.street_local_public_realm;
    const main = PUBLIC_REALM_STREET_FAMILIES.street_complete_main_22m;
    expect(local.nativeRowM).toBeNull();
    expect(local.crossSection).toEqual([]);
    expect(main.crossSection.reduce((sum, band) => sum + band.widthM, 0)).toBeCloseTo(22, 6);
    expect(local.sourceArchetypeIds).toEqual(expect.arrayContaining([
      'yield_street', 'narrow_residential_street', 'woonerf_shared_street',
      'green_alley', 'toronto_laneway', 'calgary_local', 'multi_use_trail',
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

  it('fingerprints the executable contract deterministically', () => {
    expect(PUBLIC_REALM_STREET_CATALOG_FINGERPRINT).toBe(fingerprintPublicRealmStreetCatalog());
    expect(PUBLIC_REALM_STREET_CATALOG_FINGERPRINT).toMatch(/^street-v1-[0-9a-f]{16}$/);
  });

  it('selects an explicit appearance kit and safely defaults unknown values', () => {
    const family = PUBLIC_REALM_STREET_FAMILIES.street_complete_main_22m;
    expect(resolveStreetAppearanceKit(family, 'industrial_adaptive_reuse').id)
      .toBe('industrial_adaptive_reuse');
    expect(resolveStreetAppearanceKit(family, 'not-installed').id)
      .toBe(family.defaultAppearanceKitId);
  });
});
