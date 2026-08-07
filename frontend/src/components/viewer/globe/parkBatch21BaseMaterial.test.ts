import { describe, expect, it } from 'vitest';
import { resolveBatch21ParkBaseMaterial } from './parkBatch21BaseMaterial';

describe('Batch 21 compiled parcel base material', () => {
  it('uses the exact green civic skin as a metric paver field', () => {
    expect(resolveBatch21ParkBaseMaterial(
      'formal_civic_plaza',
      'formal_civic_plaza_v2',
    )).toEqual({
      slug: 'formal-civic-green-v2',
      role: 'paver',
      metersPerTile: 3.5,
    });
  });

  it('chooses landscape roles for field, greenway, pond, and rooftop families', () => {
    expect(resolveBatch21ParkBaseMaterial(
      'athletics_precinct_sports_fields',
      'athletics_precinct_sports_fields_variant_2',
    )?.role).toBe('lawn');
    expect(resolveBatch21ParkBaseMaterial(
      'linear_park_greenway',
      'linear_park_greenway_v2',
    )?.role).toBe('planting');
    expect(resolveBatch21ParkBaseMaterial('pond_lake', 'pond_lake_v3')?.role).toBe('lawn');
    expect(resolveBatch21ParkBaseMaterial('rooftop_garden', 'rooftop_garden_v2')?.role).toBe('planting');
  });

  it('does not claim variants outside Batch 21', () => {
    expect(resolveBatch21ParkBaseMaterial(
      'formal_civic_plaza',
      'formal_civic_plaza_v0',
    )).toBeNull();
  });
});
