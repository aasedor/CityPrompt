import { describe, expect, it } from 'vitest';
import { BATCH8_PARK_SKINS, batch8ParkSkinForSelection } from './parkBatch8Skins';

describe('Batch 8 park skins', () => {
  it('locks ten exact reviewed selections with no people or large buildings', () => {
    expect(BATCH8_PARK_SKINS).toHaveLength(10);
    expect(new Set(BATCH8_PARK_SKINS.map(({ slug }) => slug)).size).toBe(10);
    for (const skin of BATCH8_PARK_SKINS) {
      expect(skin.roles).toEqual(['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber']);
      expect(skin.people).toBe(false);
      expect(skin.largeBuildings).toBe(false);
      expect(batch8ParkSkinForSelection(skin.archetypeId, skin.variantId)).toBe(skin);
    }
  });

  it('fails closed for adjacent unreviewed variants', () => {
    expect(batch8ParkSkinForSelection('quarry_sunken_garden_park', 'quarry_sunken_garden_park_v3')).toBeNull();
    expect(batch8ParkSkinForSelection('botanical_garden', 'botanical_garden_v0')).toBeNull();
    expect(batch8ParkSkinForSelection('stormwater_resilience_park', 'stormwater_resilience_park_variant_2')).toBeNull();
  });
});
