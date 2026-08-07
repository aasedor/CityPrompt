import { describe, expect, it } from 'vitest';
import { BATCH26_PARK_SKINS, batch26ParkSkinForSelection } from './parkBatch26Skins';

describe('Batch 26 park skins', () => {
  it('owns thirty unique exact-reference packs without people or large buildings', () => {
    expect(BATCH26_PARK_SKINS).toHaveLength(30);
    expect(new Set(BATCH26_PARK_SKINS.map((skin) => `${skin.archetypeId}:${skin.variantId}`)).size).toBe(30);
    expect(new Set(BATCH26_PARK_SKINS.map((skin) => skin.slug)).size).toBe(30);
    for (const skin of BATCH26_PARK_SKINS) {
      expect(skin.roles).toEqual(['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber']);
      expect(skin.people).toBe(false);
      expect(skin.largeBuildings).toBe(false);
    }
  });

  it('does not shadow the ten reviewed anchor variants', () => {
    expect(batch26ParkSkinForSelection('greenbelt_buffer_park', 'greenbelt_buffer_park_v1')).toBeNull();
    expect(batch26ParkSkinForSelection('lake_edge_plaza', 'lake_edge_plaza_v2')).toBeNull();
  });
});
