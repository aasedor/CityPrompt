import { describe, expect, it } from 'vitest';
import { BATCH23_PARK_SKINS, batch23ParkSkinForSelection } from './parkBatch23Skins';

describe('Batch 23 park skins', () => {
  it('closes thirty unique city-garden selections with six roles and no people or buildings', () => {
    expect(BATCH23_PARK_SKINS).toHaveLength(30);
    expect(new Set(BATCH23_PARK_SKINS.map((skin) => `${skin.archetypeId}/${skin.variantId}`)).size).toBe(30);
    expect(new Set(BATCH23_PARK_SKINS.map((skin) => skin.slug)).size).toBe(30);
    for (const skin of BATCH23_PARK_SKINS) {
      expect(skin.roles).toEqual(['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber']);
      expect(skin.people).toBe(false);
      expect(skin.largeBuildings).toBe(false);
    }
  });

  it('resolves an exact selection and rejects retained anchors', () => {
    expect(batch23ParkSkinForSelection('barcelona_superilla', 'barcelona_superilla_v3')?.slug)
      .toBe('barcelona-superilla-social-garden-v3');
    expect(batch23ParkSkinForSelection('barcelona_superilla', 'barcelona_superilla_v1')).toBeNull();
  });
});
