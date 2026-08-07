import { describe, expect, it } from 'vitest';
import { BATCH21_PARK_SKINS, batch21ParkSkinForSelection } from './parkBatch21Skins';

describe('Batch 21 park skins', () => {
  it('provides thirty unique exact variant mappings with six physical material roles', () => {
    expect(BATCH21_PARK_SKINS).toHaveLength(30);
    expect(new Set(BATCH21_PARK_SKINS.map((skin) => `${skin.archetypeId}/${skin.variantId}`)).size).toBe(30);
    expect(new Set(BATCH21_PARK_SKINS.map((skin) => skin.slug)).size).toBe(30);
    for (const skin of BATCH21_PARK_SKINS) {
      expect(skin.roles).toEqual(['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber']);
      expect(skin.people).toBe(false);
      expect(skin.largeBuildings).toBe(false);
    }
  });

  it('resolves only exact Batch 21 selections', () => {
    expect(batch21ParkSkinForSelection('formal_civic_plaza', 'formal_civic_plaza_v2')?.slug)
      .toBe('formal-civic-green-v2');
    expect(batch21ParkSkinForSelection('formal_civic_plaza', 'formal_civic_plaza_v0')).toBeNull();
  });
});
