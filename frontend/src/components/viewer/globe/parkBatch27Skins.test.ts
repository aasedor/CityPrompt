import { describe, expect, it } from 'vitest';
import { BATCH27_PARK_SKINS, batch27ParkSkinForSelection } from './parkBatch27Skins';

describe('Batch 27 final park skins', () => {
  it('owns twenty-one unique exact-reference packs without people or large buildings', () => {
    expect(BATCH27_PARK_SKINS).toHaveLength(21);
    expect(new Set(BATCH27_PARK_SKINS.map((skin) => `${skin.archetypeId}:${skin.variantId}`)).size).toBe(21);
    expect(new Set(BATCH27_PARK_SKINS.map((skin) => skin.slug)).size).toBe(21);
    for (const skin of BATCH27_PARK_SKINS) {
      expect(skin.roles).toEqual(['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber']);
      expect(skin.people).toBe(false);
      expect(skin.largeBuildings).toBe(false);
    }
  });

  it('does not shadow the seven reviewed anchor variants', () => {
    expect(batch27ParkSkinForSelection('academic_courtyard', 'academic_courtyard_variant_0')).toBeNull();
    expect(batch27ParkSkinForSelection('stormwater_resilience_park', 'stormwater_resilience_park_variant_3')).toBeNull();
  });
});
