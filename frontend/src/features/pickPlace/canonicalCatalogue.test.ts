import { describe, expect, it } from 'vitest';
import { CANONICAL_CHOICES, CANONICAL_DOMAINS, catalogueChoices, canonicalDrawing, filterCanonicalChoices } from './canonicalCatalogue';
import { CATALOGUE_ASSETS } from './assetRegistry';

describe('canonical discovery and identity', () => {
  it('discovers exactly the current eligible parents in each domain', () => {
    for (const [domain, options] of Object.entries(CANONICAL_DOMAINS)) {
      expect(CANONICAL_CHOICES.filter(c => c.domain === domain).map(c => c.option.id).sort()).toEqual(options.map(o => o.id).sort());
    }
    for (const choice of CANONICAL_CHOICES) for (const asset of choice.placements) {
      expect(CATALOGUE_ASSETS).toContain(asset);
    }
  });
  it('rejects duplicate parents and malformed entries before browsing', () => {
    const option = CANONICAL_DOMAINS.building[0];
    expect(() => catalogueChoices({ ...CANONICAL_DOMAINS, building: [option, option] })).toThrow(/Duplicate/);
    expect(() => catalogueChoices({ ...CANONICAL_DOMAINS, building: [{ ...option, photoUrl: '' }] })).toThrow(/Incomplete/);
    const variant = option.variants![0];
    expect(() => catalogueChoices({ ...CANONICAL_DOMAINS, building: [{ ...option, variants: [variant, variant] }] })).toThrow(/Invalid canonical variants/);
  });
  it('searches names, variants and categories without losing domain boundaries', () => {
    const choice = CANONICAL_CHOICES.find(c => c.domain === 'building' && c.option.id === 'calgary_modern_infill_house')!;
    expect(filterCanonicalChoices('building', 'infill', choice.option.calgaryGuide!.groupId)).toContain(choice);
    expect(filterCanonicalChoices('park_plaza', 'infill')).not.toContain(choice);
    expect(filterCanonicalChoices('building', 'impossible-zzzzzz')).toEqual([]);
  });
  it('keeps the exact selected variant and parent contract through drawing', () => {
    for (const domain of ['building', 'park_plaza', 'street_pathway'] as const) {
      const choice = CANONICAL_CHOICES.find(c => c.domain === domain && !c.placements.length && c.option.variants?.length)!;
      const variant = choice.option.variants![0];
      const { properties } = canonicalDrawing({ choice, variant });
      const prefix = domain === 'building' ? 'development' : domain === 'park_plaza' ? 'green_space' : 'road';
      expect(properties[`${prefix}_subcategory`]).toBe(choice.option.id);
      expect(properties[`${prefix}_selected_variant_id`]).toBe(variant.id);
      expect(properties.pick_place_automatic_3d).toBe(true);
      expect(properties.pick_place_asset).toBeUndefined();
      expect(properties.native_home_plot).toBeUndefined();
      if (domain === 'building') expect(properties.height).toBe(Number(properties.floors) * Number(properties.floor_height));
    }
  });
});
