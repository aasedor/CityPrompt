import { describe, expect, it } from 'vitest';
import {
  BATCH7_PARK_SKINS,
  batch7ParkSkinForSelection,
  batch7ParkSkinRoot,
} from './parkBatch7Skins';

describe('batch 7 exact park skins', () => {
  it('registers ten distinct image-reviewed catalogue selections', () => {
    expect(BATCH7_PARK_SKINS).toHaveLength(10);
    expect(new Set(BATCH7_PARK_SKINS.map(({ archetypeId }) => archetypeId)).size).toBe(10);
    expect(new Set(BATCH7_PARK_SKINS.map(({ slug }) => slug)).size).toBe(10);
    expect(BATCH7_PARK_SKINS.every(({ people, largeBuildings }) => (
      people === false && largeBuildings === false
    ))).toBe(true);
  });

  it.each(BATCH7_PARK_SKINS)('resolves $archetypeId/$variantId exactly', (definition) => {
    expect(batch7ParkSkinForSelection(definition.archetypeId, definition.variantId))
      .toBe(definition);
    expect(batch7ParkSkinRoot(definition))
      .toBe(`/park-skins/${definition.slug}/adaptive-v1`);
  });

  it('fails closed for visually different adjacent variants', () => {
    expect(batch7ParkSkinForSelection('regional_park', 'regional_park_v1')).toBeNull();
    expect(batch7ParkSkinForSelection('beer_garden', 'beer_garden_v2')).toBeNull();
    expect(batch7ParkSkinForSelection('stepped_terraced_plaza', 'stepped_terraced_plaza_v2')).toBeNull();
    expect(batch7ParkSkinForSelection('riverfront_park_beach', 'riverfront_park_beach_v0')).toBeNull();
  });
});
