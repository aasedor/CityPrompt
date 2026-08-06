import { describe, expect, it } from 'vitest';
import { BATCH16_PARK_SKINS, batch16ParkSkinForSelection } from './parkBatch16Skins';

describe('Batch 16 park skins', () => {
  it('registers every non-anchor variant for the ten-family closure batch', () => {
    expect(BATCH16_PARK_SKINS).toHaveLength(29);
    expect(new Set(BATCH16_PARK_SKINS.map(({ variantId }) => variantId)).size).toBe(29);
    expect(BATCH16_PARK_SKINS.every(({ people, largeBuildings }) => !people && !largeBuildings)).toBe(true);
  });

  it('resolves a source-card identity without falling back to another variant', () => {
    expect(batch16ParkSkinForSelection('tennis_court_cluster', 'tennis_court_cluster_v2')?.slug)
      .toBe('tennis-court-cluster-naturalized-active-v2');
    expect(batch16ParkSkinForSelection('tennis_court_cluster', 'tennis_court_cluster_v0')).toBeNull();
  });
});
