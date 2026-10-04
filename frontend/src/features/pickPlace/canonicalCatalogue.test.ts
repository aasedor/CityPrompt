import { describe, expect, it } from 'vitest';
import { CANONICAL_CHOICES, CANONICAL_DOMAINS, UNAVAILABLE_CATALOGUE_ENTRIES, resolveCatalogueRoster, catalogueChoices, canonicalDrawing, filterCanonicalChoices, preferredCatalogueVariant } from './canonicalCatalogue';
import validation from '@/data/validationCatalogue.json';
import expansion from '@/data/classroomExpansion.json';
import { CATALOGUE_ASSETS, FLEXIBLE_PARK_ASSETS, MANUAL_STREET_ASSETS } from './assetRegistry';

describe('canonical discovery and identity', () => {
  it('finds a duplex inside an infill parent and opens the matching detailed variant', () => {
    const choice = CANONICAL_CHOICES.find(c => c.option.id === 'calgary_modern_infill_house' && c.placements.some(a => a.model.variantId === 'infill_duplex'))!;
    expect(filterCanonicalChoices('building', '', 'two_home')).toContain(choice);
    expect(preferredCatalogueVariant(choice, '', 'two_home')).toBe('infill_duplex');
    expect(preferredCatalogueVariant(choice, 'side-by-side duplex')).toBe('infill_duplex');
    expect(preferredCatalogueVariant(choice, 'duplex')).toBe('infill_duplex');
    expect(preferredCatalogueVariant(choice)).toBe(choice.placements[0].model.variantId);
  });
  it('discovers exactly the current eligible parents in each domain', () => {
    expect(UNAVAILABLE_CATALOGUE_ENTRIES).toEqual([]);
    const roster = [...validation.entries, ...expansion.entries];
    expect(CANONICAL_CHOICES).toHaveLength(roster.length + MANUAL_STREET_ASSETS.length + FLEXIBLE_PARK_ASSETS.length);
    for (const entry of roster) {
      const choice = CANONICAL_CHOICES.find(c => c.option.id === entry.archetype_id && c.placements[0]?.model.variantId === entry.variant_id);
      expect(choice, entry.variant_id).toBeDefined();
      expect(choice!.option.variants?.map(v => v.id)).toEqual([entry.variant_id]);
    }
    for (const choice of CANONICAL_CHOICES) for (const asset of choice.placements) {
      expect(CATALOGUE_ASSETS).toContain(asset);
    }
  });
  it('accepts renamed native placements but never substitutes another variant for a stale ID', () => {
    const entry = validation.entries.find(row => row.variant_id === 'student_main_street_v1')!;
    const asset = CATALOGUE_ASSETS.find(item => item.model.variantId === entry.variant_id)!;
    const wrongVariant = { ...asset, id: entry.placement_id, model: { ...asset.model, variantId: 'other-variant' } };
    const renamed = { ...asset, id: 'native:renamed-road' };
    expect(resolveCatalogueRoster([entry], [wrongVariant]).unavailable).toEqual([entry]);
    expect(resolveCatalogueRoster([entry], [wrongVariant, renamed]).choices[0].placements).toEqual([renamed]);
    const exact = { ...asset, id: entry.placement_id };
    expect(resolveCatalogueRoster([entry], [renamed, exact]).choices[0].placements).toEqual([exact]);
  });
  it('excludes unready assets, wrong parents, wrong domains and unsupported roster domains', () => {
    const entry = validation.entries.find(row => row.variant_id === 'student_main_street_v1')!;
    const asset = CATALOGUE_ASSETS.find(item => item.model.variantId === entry.variant_id)!;
    expect(resolveCatalogueRoster([entry], [{ ...asset, readiness: 'retired' }]).choices).toEqual([]);
    expect(resolveCatalogueRoster([entry], [{ ...asset, properties: { ...asset.properties, road_archetype_id: 'other' } }]).choices).toEqual([]);
    expect(resolveCatalogueRoster([{ ...entry, domain: 'building' }], [asset]).choices).toEqual([]);
    expect(resolveCatalogueRoster([{ ...entry, domain: 'unknown' }], [asset]).choices).toEqual([]);
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
      const choice = CANONICAL_CHOICES.find(c => c.domain === domain && c.placements.length && c.option.variants?.length)!;
      const variant = choice.option.variants![0];
      const { properties } = canonicalDrawing({ choice, variant });
      const prefix = domain === 'building' ? 'development' : domain === 'park_plaza' ? 'green_space' : 'road';
      expect(properties[`${prefix}_subcategory`]).toBe(choice.option.id);
      expect(properties[`${prefix}_selected_variant_id`]).toBe(variant.id);
      expect(properties.pick_place_automatic_3d).toBe(true);
      expect(properties.pick_place_asset).toBeUndefined();
      expect(properties.native_home_plot).not.toBe(true);
      if (domain === 'building') expect(properties.height).toBe(Number(properties.floors) * Number(properties.floor_height));
    }
  });
});
