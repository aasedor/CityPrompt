import { describe, expect, it } from 'vitest';
import {
  BATCH5_PARK_SKINS,
  batch5ParkSkinForSelection,
  batch5ParkSkinRoot,
} from './parkBatch5Skins';

describe('batch 5 park skins', () => {
  it('registers ten distinct exact-v0 stationary PBR libraries', () => {
    expect(BATCH5_PARK_SKINS).toHaveLength(10);
    expect(new Set(BATCH5_PARK_SKINS.map(({ archetypeId }) => archetypeId)).size).toBe(10);
    expect(new Set(BATCH5_PARK_SKINS.map(({ slug }) => slug)).size).toBe(10);
    for (const skin of BATCH5_PARK_SKINS) {
      expect(skin.variantId).toBe(`${skin.archetypeId}_v0`);
      expect(skin.roles).toEqual(['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber']);
      expect(skin.people).toBe(false);
      expect(skin.largeBuildings).toBe(false);
      expect(batch5ParkSkinRoot(skin)).toBe(`/park-skins/${skin.slug}/adaptive-v1`);
    }
  });

  it('fails closed for unreviewed variants', () => {
    expect(batch5ParkSkinForSelection('labyrinth_meditation', 'labyrinth_meditation_v0')).not.toBeNull();
    expect(batch5ParkSkinForSelection('labyrinth_meditation', 'labyrinth_meditation_v1')).toBeNull();
  });
});
