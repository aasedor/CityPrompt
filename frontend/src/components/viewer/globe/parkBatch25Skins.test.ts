import { describe, expect, it } from 'vitest';
import { BATCH25_PARK_SKINS, batch25ParkSkinForSelection } from './parkBatch25Skins';

describe('Batch 25 park skins', () => {
  it('owns thirty unique exact-reference packs without people or large buildings', () => {
    expect(BATCH25_PARK_SKINS).toHaveLength(30);
    expect(new Set(BATCH25_PARK_SKINS.map((skin) => `${skin.archetypeId}:${skin.variantId}`)).size).toBe(30);
    expect(new Set(BATCH25_PARK_SKINS.map((skin) => skin.slug)).size).toBe(30);
    for (const skin of BATCH25_PARK_SKINS) {
      expect(skin.roles).toEqual(['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber']);
      expect(skin.people).toBe(false);
      expect(skin.largeBuildings).toBe(false);
    }
  });

  it('does not shadow the ten already-reviewed anchor variants', () => {
    expect(batch25ParkSkinForSelection('vancouver_seawall', 'vancouver_seawall_v2')).toBeNull();
    expect(batch25ParkSkinForSelection('reservoir_watershed_park', 'reservoir_watershed_park_v0')).toBeNull();
  });
});
