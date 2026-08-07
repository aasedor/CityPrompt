import { describe, expect, it } from 'vitest';
import { BATCH22_PARK_SKINS, batch22ParkSkinForSelection } from './parkBatch22Skins';

describe('Batch 22 park skins', () => {
  it('closes thirty unique selections with six roles and no people or buildings', () => {
    expect(BATCH22_PARK_SKINS).toHaveLength(30);
    expect(new Set(BATCH22_PARK_SKINS.map((skin) => `${skin.archetypeId}/${skin.variantId}`)).size).toBe(30);
    expect(new Set(BATCH22_PARK_SKINS.map((skin) => skin.slug)).size).toBe(30);
    for (const skin of BATCH22_PARK_SKINS) {
      expect(skin.roles).toEqual(['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber']);
      expect(skin.people).toBe(false);
      expect(skin.largeBuildings).toBe(false);
    }
  });

  it('resolves an exact selection and rejects the retained anchor', () => {
    expect(batch22ParkSkinForSelection('nature_preserve', 'nature_preserve_v3')?.slug).toBe('nature-preserve-old-growth-v3');
    expect(batch22ParkSkinForSelection('nature_preserve', 'nature_preserve_v1')).toBeNull();
  });
});
