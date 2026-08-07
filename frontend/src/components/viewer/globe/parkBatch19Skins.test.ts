import { describe, expect, it } from 'vitest';
import { BATCH19_PARK_SKINS, batch19ParkSkinForSelection } from './parkBatch19Skins';

describe('Batch 19 park skins', () => {
  it('registers thirty non-anchor destination-park variants', () => {
    expect(BATCH19_PARK_SKINS).toHaveLength(30);
    expect(new Set(BATCH19_PARK_SKINS.map(({ variantId }) => variantId)).size).toBe(30);
    expect(BATCH19_PARK_SKINS.every(({ people, largeBuildings }) => !people && !largeBuildings)).toBe(true);
  });

  it('resolves exact named catalogue identities only', () => {
    expect(batch19ParkSkinForSelection('velodrome_cycling_track', 'velodrome_cycling_track_variant_2')?.slug)
      .toBe('velodrome-parkland-v2');
    expect(batch19ParkSkinForSelection('velodrome_cycling_track', 'velodrome_cycling_track_variant_0')).toBeNull();
  });
});
