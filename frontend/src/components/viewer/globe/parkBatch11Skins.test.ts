import { describe, expect, it } from 'vitest';
import archetypeCatalogue from '@/data/openSpaceArchetypes.json';
import { BATCH11_PARK_SKINS, batch11ParkSkinForSelection } from './parkBatch11Skins';

describe('batch 11 exact-reference park skins', () => {
  it('registers ten unique exact variants without people or large buildings', () => {
    expect(BATCH11_PARK_SKINS).toHaveLength(10);
    expect(new Set(BATCH11_PARK_SKINS.map((item) => `${item.archetypeId}/${item.variantId}`)).size).toBe(10);
    BATCH11_PARK_SKINS.forEach((item) => { expect(item.people).toBe(false); expect(item.largeBuildings).toBe(false); expect(item.roles).toHaveLength(6); });
  });
  it('matches real catalogue variants', () => {
    BATCH11_PARK_SKINS.forEach((item) => {
      const parent = archetypeCatalogue.archetypes.find((candidate) => candidate.id === item.archetypeId);
      expect(parent?.variants.some((variant) => variant.id === item.variantId)).toBe(true);
      expect(batch11ParkSkinForSelection(item.archetypeId, item.variantId)?.slug).toBe(item.slug);
    });
  });
  it.each([
    ['parisian_place','civic_plazas'],['parisian_square','specialty_gardens'],['london_circus','civic_plazas'],
    ['newyork_pocket_park','neighborhood_public_realm'],['newyork_community_garden','specialty_gardens'],
    ['vancouver_seawall','waterfront_spaces'],['vancouver_beach_park','waterfront_spaces'],
    ['toronto_ravine','landscape_parks'],['toronto_urban_square','civic_plazas'],['halifax_coastal_park','landscape_parks'],
  ] as const)('keeps %s reachable in the %s picker', (id, category) => {
    expect(archetypeCatalogue.archetypes.find((candidate) => candidate.id === id)?.aestheticCategory).toBe(category);
  });
});
