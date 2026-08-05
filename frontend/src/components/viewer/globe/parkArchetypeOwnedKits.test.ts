import { describe, expect, it } from 'vitest';

import {
  ARCHETYPE_OWNED_PARK_KITS,
  archetypeOwnedParkKitForSelection,
} from './parkArchetypeOwnedKits';

describe('archetype-owned park kit registry', () => {
  it('contains five exact, non-generic pilot identities', () => {
    const kits = Object.values(ARCHETYPE_OWNED_PARK_KITS);
    expect(kits).toHaveLength(5);
    expect(new Set(kits.map(({ familyId }) => familyId)).size).toBe(5);
    expect(new Set(kits.map(({ appearanceKitId }) => appearanceKitId)).size).toBe(5);
    expect(kits.every(({ people, largeBuildings }) => !people && !largeBuildings)).toBe(true);
  });

  it.each([
    ['skate_park', 'skate_park_v0', 40, 30],
    ['inclusive_playground', 'inclusive_playground_v0', 50, 40],
    ['dog_park', 'dog_park_v0', 80, 50],
    ['splash_pad_area', 'splash_pad_area_v0', 30, 25],
    ['community_garden', 'community_garden_v0', 50, 50],
  ])('locks %s/%s to its authored metric envelope', (archetypeId, variantId, widthM, depthM) => {
    expect(archetypeOwnedParkKitForSelection(archetypeId, variantId)).toMatchObject({
      archetypeId,
      variantId,
      widthM,
      depthM,
      clearanceM: 0.5,
    });
  });
});
