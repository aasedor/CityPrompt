import { describe, expect, it } from 'vitest';
import {
  BATCH6_PARK_SKINS,
  batch6ParkSkinForSelection,
  batch6ParkSkinRoot,
} from './parkBatch6Skins';

describe('batch 6 exact park skins', () => {
  it('registers ten distinct exact catalogue selections', () => {
    expect(BATCH6_PARK_SKINS).toHaveLength(10);
    expect(new Set(BATCH6_PARK_SKINS.map(({ archetypeId }) => archetypeId)).size).toBe(10);
    expect(new Set(BATCH6_PARK_SKINS.map(({ slug }) => slug)).size).toBe(10);
    expect(BATCH6_PARK_SKINS.every(({ people, largeBuildings }) => (
      people === false && largeBuildings === false
    ))).toBe(true);
  });

  it.each(BATCH6_PARK_SKINS)('resolves $archetypeId/$variantId without a generic fallback', (definition) => {
    expect(batch6ParkSkinForSelection(definition.archetypeId, definition.variantId))
      .toBe(definition);
    expect(batch6ParkSkinRoot(definition))
      .toBe(`/park-skins/${definition.slug}/adaptive-v1`);
    expect(definition.roles).toEqual([
      'paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber',
    ]);
  });

  it('fails closed for adjacent, unreviewed variants', () => {
    expect(batch6ParkSkinForSelection('outdoor_ice_rink', 'outdoor_ice_rink_v2')).toBeNull();
    expect(batch6ParkSkinForSelection('velodrome_cycling_track', 'velodrome_cycling_track_variant_1')).toBeNull();
    expect(batch6ParkSkinForSelection('mountain_bike_park', 'mountain_bike_park_variant_1')).toBeNull();
  });
});
