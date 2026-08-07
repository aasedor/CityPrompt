import { describe, expect, it } from 'vitest';
import { BATCH24_PARK_SKINS, batch24ParkSkinForSelection } from './parkBatch24Skins';

describe('Batch 24 park skin catalogue', () => {
  it('contains thirty unique, exact archetype/variant packs', () => {
    expect(BATCH24_PARK_SKINS).toHaveLength(30);
    expect(new Set(BATCH24_PARK_SKINS.map((skin) => `${skin.archetypeId}:${skin.variantId}`)).size).toBe(30);
    expect(new Set(BATCH24_PARK_SKINS.map((skin) => skin.slug)).size).toBe(30);
  });

  it('forbids people and embedded large buildings', () => {
    for (const skin of BATCH24_PARK_SKINS) {
      expect(skin.people).toBe(false);
      expect(skin.largeBuildings).toBe(false);
      expect(skin.roles).toEqual(['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber']);
    }
  });

  it('does not claim variants outside the bounded Batch 24 schedule', () => {
    expect(batch24ParkSkinForSelection('calgary_prairie_plaza', 'calgary_prairie_plaza_v1')).toBeNull();
    expect(batch24ParkSkinForSelection('newyork_pocket_park', 'newyork_pocket_park_v0')).toBeNull();
  });
});
