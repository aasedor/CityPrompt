import { describe, expect, it } from 'vitest';
import { BATCH18_PARK_SKINS, batch18ParkSkinForSelection } from './parkBatch18Skins';

describe('Batch 18 park skins', () => {
  it('registers thirty non-anchor specialty-park variants', () => {
    expect(BATCH18_PARK_SKINS).toHaveLength(30);
    expect(new Set(BATCH18_PARK_SKINS.map(({ variantId }) => variantId)).size).toBe(30);
    expect(BATCH18_PARK_SKINS.every(({ people, largeBuildings }) => !people && !largeBuildings)).toBe(true);
  });

  it('resolves exact source-card identities only', () => {
    expect(batch18ParkSkinForSelection('labyrinth_meditation', 'labyrinth_meditation_v2')?.slug)
      .toBe('labyrinth-healing-garden-v2');
    expect(batch18ParkSkinForSelection('labyrinth_meditation', 'labyrinth_meditation_v0')).toBeNull();
  });
});
