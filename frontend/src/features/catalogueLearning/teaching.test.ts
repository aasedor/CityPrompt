import { describe, expect, it } from 'vitest';
import { CANONICAL_CHOICES, filterCanonicalChoices } from '@/features/pickPlace/canonicalCatalogue';
import { availableCatalogueStyles, catalogueStyleIds, choiceMatchesFacets } from '@/features/pickPlace/catalogueFacets';

const choiceFor = (id: string) => CANONICAL_CHOICES.find(c => c.placements.some(a => a.id === id))!;

describe('researched catalogue learning', () => {
  it('discovers a previously unlabelled expressed-structure design without changing its placement', () => {
    const choice = choiceFor('validation_brewery_crystal_brewhouse');
    const before = JSON.stringify(choice);
    expect(catalogueStyleIds(choice)).toEqual(['structural', 'contemporary']);
    expect(choiceMatchesFacets(choice, {styleId:'structural',sizeId:''})).toBe(true);
    expect(JSON.stringify(choice)).toBe(before);
  });

  it('classifies a working concrete warehouse without calling every concrete building Brutalist', () => {
    const choice = choiceFor('clay_industrial_tilt_up_concrete');
    expect(catalogueStyleIds(choice)).toEqual(['industrial','contemporary']);
    expect(choiceMatchesFacets(choice, {styleId:'brutalism',sizeId:''})).toBe(false);
  });

  it.each([
    'validation_clapboard_north_end', 'clay_ecole_republicaine_provincial_brick',
    'community_inglewood_corner_merchants', 'claude_trial_courtyard_primary_school',
    'claude_trial_ctrain_elevated_station', 'claude_trial_halifax_waterfront_warehouse',
    'claude_trial_old_montreal_limestone_commercial',
  ])('withholds a settled architectural style for the disputed identity %s', id => {
    const choice = choiceFor(id);
    expect(choice, id).toBeDefined();
    expect(catalogueStyleIds(choice)).toEqual([]);
    expect(choiceMatchesFacets(choice,{styleId:'unknown',sizeId:''})).toBe(true);
  });

  it('withholds an old classification when the model revision changes', () => {
    const choice = choiceFor('clay_neoclassical_brick_headquarters');
    const changed = {...choice,placements:choice.placements.map(asset => ({...asset,
      model:{...asset.model,revision:'unreviewed-new-geometry'}}))};
    expect(catalogueStyleIds(changed)).toEqual([]);
  });

  it('does not apply a placement lesson to a renamed sibling variant', () => {
    const choice = choiceFor('clay_neoclassical_brick_headquarters');
    const changed = {...choice,placements:choice.placements.map(asset => ({...asset,
      model:{...asset.model,variantId:'unreviewed-sibling'}}))};
    expect(catalogueStyleIds(changed)).toEqual([]);
  });

  it('searches newly classified style names inside the correct domain', () => {
    const brewery = choiceFor('validation_brewery_crystal_brewhouse');
    expect(filterCanonicalChoices('building','expressed structure')).toContain(brewery);
    expect(filterCanonicalChoices('park_plaza','expressed structure')).not.toContain(brewery);
  });

  it('keeps later catalogue entries discoverable when assembling the style menu', () => {
    const office = choiceFor('clay_neoclassical_brick_headquarters');
    const brewery = choiceFor('validation_brewery_crystal_brewhouse');
    expect(availableCatalogueStyles([office, brewery], [])).toContainEqual({id:'structural',label:'Expressed structure'});
  });
});
