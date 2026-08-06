import { describe, expect, it } from 'vitest';
import { BATCH17_PARK_SKINS, batch17ParkSkinForSelection, parkGlbMaterialRole } from './parkBatch17Skins';

describe('Batch 17 park skins', () => {
  it('registers every non-anchor variant for the ten-family activity batch', () => {
    expect(BATCH17_PARK_SKINS).toHaveLength(30);
    expect(new Set(BATCH17_PARK_SKINS.map(({ variantId }) => variantId)).size).toBe(30);
    expect(BATCH17_PARK_SKINS.every(({ people, largeBuildings }) => !people && !largeBuildings)).toBe(true);
  });

  it('resolves a source-card identity without falling back to the anchor variant', () => {
    expect(batch17ParkSkinForSelection('baseball_softball_diamond', 'baseball_softball_diamond_v3')?.slug)
      .toBe('baseball-softball-vintage-sandlot-v3');
    expect(batch17ParkSkinForSelection('baseball_softball_diamond', 'baseball_softball_diamond_v1')).toBeNull();
  });

  it('maps authored full-park GLB material names onto the six-role skin pack', () => {
    expect(parkGlbMaterialRole('baseball-youth-pinwheel planting')).toBe('planting');
    expect(parkGlbMaterialRole('track-oval-school-athletic lawn')).toBe('lawn');
    expect(parkGlbMaterialRole('pickleball-community-bank rubber blue')).toBe('safety');
    expect(parkGlbMaterialRole('cricket-village-green court surround')).toBe('paver');
    expect(parkGlbMaterialRole('Court marking white')).toBeNull();
    expect(parkGlbMaterialRole('Galvanized steel')).toBeNull();
  });
});
