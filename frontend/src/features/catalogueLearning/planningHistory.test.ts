import { describe, expect, it } from 'vitest';
import { CANONICAL_CHOICES, filterCanonicalChoices } from '@/features/pickPlace/canonicalCatalogue';
import { choiceMatchesFacets, catalogueStyleIds } from '@/features/pickPlace/catalogueFacets';
import { planningIds, teachingSearchTerms } from './teaching';
import { availableEras, eraIds, formLabel, historyForChoice } from './planningHistory';
import historyData from '@/data/cataloguePlanningHistory.json';
import release from '@/data/claudeBuildingRelease.json';

const choiceFor = (id: string) => CANONICAL_CHOICES.find(choice => choice.placements.some(asset => asset.id === id))!;

describe('historical planning interpretation', () => {
  it('finds the postwar bungalow through the 1950s without assigning a construction year', () => {
    const bungalow = choiceFor('trial_postwar_bungalow');
    expect(eraIds(bungalow)).toEqual(['postwar']);
    expect(historyForChoice(bungalow)?.lesson.constructionYear).toBeNull();
    expect(filterCanonicalChoices('building', '1950s')).toContain(bungalow);
    expect(planningIds(bungalow)).not.toContain('missing_middle');
  });

  it('keeps historic duplexes and contemporary fourplexes distinct within missing middle', () => {
    const duplex = choiceFor('clay_montreal_plateau_duplex');
    const fourplex = choiceFor('validation_reference_charcoal_gable_fourplex_v1');
    expect(eraIds(duplex)).toEqual(['industrial_streetcar', 'reform_interwar']);
    expect(eraIds(fourplex)).toEqual(['contemporary']);
    for (const choice of [duplex, fourplex]) expect(planningIds(choice)).toContain('missing_middle');
    expect(catalogueStyleIds(fourplex)).toContain('contemporary_gabled');
    expect(choiceMatchesFacets(fourplex, { styleId: '', sizeId: '', eraId: 'postwar' })).toBe(false);
    expect(choiceMatchesFacets(fourplex, { styleId: '', sizeId: '', eraId: 'contemporary', planningId: 'missing_middle' })).toBe(true);
  });

  it('teaches Vancouverism through residential tower/podium components, not every glass office', () => {
    expect(planningIds(choiceFor('clay_vancouver_balcony_podium_tower'))).toContain('vancouverism');
    expect(planningIds(choiceFor('claude_trial_brick_podium_condo_tower'))).toContain('vancouverism');
    expect(planningIds(choiceFor('clay_blue_glass_office_tower'))).not.toContain('vancouverism');
  });

  it('does not date a postwar slab from the earlier origins of Modernism', () => {
    expect(eraIds(choiceFor('claude_trial_slab_balcony_tower'))).toEqual(['postwar']);
  });

  it.each([
    'validation_clapboard_north_end', 'clay_ecole_republicaine_provincial_brick',
    'community_inglewood_corner_merchants', 'claude_trial_courtyard_primary_school',
    'claude_trial_ctrain_elevated_station', 'claude_trial_halifax_waterfront_warehouse',
    'claude_trial_old_montreal_limestone_commercial', 'claude_public_realm:rail-through-truss:db0886ff6186',
  ])('withholds era, planning and historical search claims for held identity %s', id => {
    const choice = choiceFor(id);
    expect(choice).toBeDefined();
    expect(historyForChoice(choice)?.status).toBe('review');
    expect(eraIds(choice)).toEqual([]);
    expect(planningIds(choice)).toEqual([]);
    expect(teachingSearchTerms(choice)).toEqual([]);
  });

  it('binds the history to domain, family, variant, method and model revision', () => {
    const original = choiceFor('trial_postwar_bungalow');
    const changed = [
      { ...original, domain: 'park_plaza' as const },
      { ...original, option: { ...original.option, id: 'different-family' } },
      ...['variantId', 'method', 'revision'].map(key => ({ ...original,
        placements: original.placements.map(asset => ({ ...asset, model: { ...asset.model, [key]: 'not-reviewed' } })),
      })),
    ];
    for (const choice of changed) {
      expect(historyForChoice(choice)?.status).toBe('stale');
      expect(eraIds(choice)).toEqual([]);
      expect(catalogueStyleIds(choice)).toEqual([]);
      expect(teachingSearchTerms(choice)).toEqual([]);
    }
  });

  it.each([
    ['clay_ecole_republicaine_provincial_brick', 'classical', 'Provincial Brick School'],
    ['validation_clapboard_north_end', 'historical', 'Halifax Clapboard House'],
    ['community_inglewood_corner_merchants', 'historical', 'Inglewood Corner Merchants'],
  ])('withholds legacy semantic search tags for held %s while retaining name discovery', (id, tag, name) => {
    const choice = choiceFor(id);
    expect(filterCanonicalChoices('building', tag)).not.toContain(choice);
    expect(filterCanonicalChoices('building', name)).toContain(choice);
  });

  it('withholds semantic tags through the full search path after the model revision changes', () => {
    const original = choiceFor('clay_montreal_plateau_duplex');
    const changed = { ...original, placements: original.placements.map(asset => ({ ...asset,
      model: { ...asset.model, revision: 'new-unreviewed-model' } })),
    };
    expect(historyForChoice(changed)?.status).toBe('stale');
    expect(historyForChoice(original)?.status).toBe('classified');
    expect(filterCanonicalChoices('building', 'historical', '', [original])).toEqual([original]);
    expect(filterCanonicalChoices('building', 'historical', '', [changed])).toEqual([]);
    expect(filterCanonicalChoices('building', 'Plateau Stacked Duplex', '', [changed])).toEqual([changed]);
  });

  it('also withholds legacy fallback descriptions and tags when an unreviewed sibling has no presentation', () => {
    const original = choiceFor('trial_postwar_bungalow');
    const changed = { ...original, option: { ...original.option, label: 'Known dwelling',
      description: 'unsupported-era-marker', categoryId: 'unsupported-era-marker',
      generationTags: ['unsupported-era-marker'], variants: [] },
      placements: [
        { ...original.placements[0], label: 'Known dwelling',
          model: { ...original.placements[0].model, revision: 'new-unreviewed-model' } },
        { ...original.placements[0], id: 'unreviewed-sibling-without-presentation', label: 'Known dwelling' },
      ],
    };
    expect(filterCanonicalChoices('building', 'unsupported-era-marker', '', [changed])).toEqual([]);
    expect(filterCanonicalChoices('building', 'Known dwelling', '', [changed])).toEqual([changed]);
  });

  it('only offers eras represented by valid current choices in that domain', () => {
    const bungalow = choiceFor('trial_postwar_bungalow');
    const held = choiceFor('validation_clapboard_north_end');
    expect(availableEras([bungalow, held], 'building')).toEqual([
      { id: 'postwar', label: 'Postwar expansion · c. 1945–1975' },
    ]);
    expect(availableEras([bungalow], 'street_pathway')).toEqual([]);
    expect(Object.keys(historyData.lessons)).toHaveLength(204);
    expect(CANONICAL_CHOICES.filter(choice => !historyForChoice(choice))).toEqual([]);
    expect(CANONICAL_CHOICES.some(choice => choice.id.includes('bauhaus_workshop'))).toBe(false);
  });

  it('binds all seven newly approved models while withholding unreviewed historical claims', () => {
    const additions = release.entries.filter(row => !row.asset_id.startsWith('claude_trial_'));
    expect(additions).toHaveLength(7);
    for (const row of additions) {
      const choice = choiceFor(row.asset_id);
      expect(choice, row.asset_id).toBeDefined();
      expect(historyForChoice(choice), row.asset_id).toMatchObject({
        status: 'review', lesson: { modelRevision: row.candidate, variantId: row.variant_id,
          archetypeId: row.archetype_id, constructionYear: null },
      });
      expect(eraIds(choice)).toEqual([]);
      expect(planningIds(choice)).toEqual([]);
      expect(catalogueStyleIds(choice)).toEqual([]);
    }
  });

  it('names every classified form explicitly without assigning a housing tenure', () => {
    for (const lesson of Object.values(historyData.lessons).filter(row => row.status === 'classified')) {
      expect(formLabel(lesson.formId), lesson.placementId).toBeTruthy();
      expect(lesson).not.toHaveProperty('tenure');
    }
    expect(formLabel('fourplex')).toBe('Fourplex');
    expect(formLabel('residential_tower_podium')).toBe('Residential tower and podium');
    expect(formLabel('unconfirmed')).toBeUndefined();
    expect(formLabel('unreviewed-future-form')).toBeUndefined();
  });

  it('allows discovery by the reviewed form name', () => {
    const tower=choiceFor('clay_vancouver_balcony_podium_tower');
    expect(teachingSearchTerms(tower)).toContain('Residential tower and podium');
  });
});
