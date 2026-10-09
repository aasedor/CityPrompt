import { describe, expect, it } from 'vitest';
import metadata from '@/data/cataloguePresentation.json';
import { CANONICAL_CHOICES, filterCanonicalChoices } from './canonicalCatalogue';
import { CATALOGUE_ASSETS } from './assetRegistry';
import { cataloguePresentationFor } from './cataloguePresentation';
import { catalogueStyleIds } from './catalogueFacets';

const choiceFor = (id: string) => CANONICAL_CHOICES.find(choice => choice.placements.some(asset => asset.id === id))!;

describe('catalogue presentation metadata', () => {
  it('covers the exact active placement roster without stale entries or internal status copy', () => {
    const active = CANONICAL_CHOICES.flatMap(choice => choice.placements.map(asset => asset.id));
    expect(new Set(active).size).toBe(active.length);
    expect(Object.keys(metadata).sort()).toEqual([...active].sort());
    for (const id of active) {
      const entry = cataloguePresentationFor(id)!;
      expect(entry.label.trim(), id).not.toBe('');
      expect(entry.description.trim(), id).not.toBe('');
      expect(entry.description, id).not.toMatch(/validation pending|fixed native|source.locked|upgrade candidate|complete native/i);
      expect(new Set(entry.styleIds).size, id).toBe(entry.styleIds.length);
      expect(new Set(entry.searchTags).size, id).toBe(entry.searchTags.length);
    }
    expect(cataloguePresentationFor(undefined)).toBeUndefined();
    expect(cataloguePresentationFor('unregistered-future-placement')).toBeUndefined();
  });

  it('uses exact variant style evidence while keeping unclassified buildings unknown', () => {
    expect(catalogueStyleIds(choiceFor('clay_neoclassical_brick_headquarters'))).toEqual(['neoclassical']);
    expect(catalogueStyleIds(choiceFor('clay_mediterranean_resort_courtyard'))).toEqual(['mediterranean']);
    expect(catalogueStyleIds(choiceFor('validation_gothic_community_church_single_spire'))).toEqual(['gothic']);
    expect(catalogueStyleIds(choiceFor('validation_brewery_crystal_brewhouse'))).toEqual([]);
  });

  it('finds revised description terms and styles in the correct domain', () => {
    const museum = choiceFor('validation_museum_earth_sheltered');
    expect(filterCanonicalChoices('building', 'projecting skylights')).toContain(museum);
    const office = choiceFor('clay_neoclassical_brick_headquarters');
    expect(filterCanonicalChoices('building', 'neoclassical')).toContain(office);
    expect(filterCanonicalChoices('park_plaza', 'neoclassical')).not.toContain(office);
  });

  it('does not revive superseded parent styles in presentation searches', () => {
    const office = choiceFor('clay_neoclassical_brick_headquarters');
    const hotel = choiceFor('clay_mediterranean_resort_courtyard');
    const loft = choiceFor('validation_cast_iron_italianate');
    expect(filterCanonicalChoices('building', 'contemporary urban')).not.toContain(office);
    expect(filterCanonicalChoices('building', 'contemporary urban')).not.toContain(hotel);
    expect(filterCanonicalChoices('building', 'industrial brick')).not.toContain(loft);
    expect(filterCanonicalChoices('building', 'historical')).toContain(loft);
    expect(filterCanonicalChoices('building', office.option.id)).toContain(office);
    const future = { ...office, option: { ...office.option, categoryId: 'future_style', generationTags: ['future_search_tag'] },
      placements: [{ ...office.placements[0], id: 'future-placement-without-presentation' }] };
    expect(filterCanonicalChoices('building', 'future style', '', [future])).toEqual([future]);
    expect(filterCanonicalChoices('building', 'future search tag', '', [future])).toEqual([future]);
  });

  it('retains evidence-backed programme terms without restoring parent appearance tags', () => {
    const affordable = CANONICAL_CHOICES.filter(choice => choice.placements[0].id.startsWith('clay_affordable_'));
    expect(affordable).toHaveLength(5);
    for (const query of ['affordable housing', 'non market', 'compact housing']) {
      for (const choice of affordable) expect(filterCanonicalChoices('building', query)).toContain(choice);
    }
    expect(filterCanonicalChoices('building', 'modular')).toContain(choiceFor('clay_affordable_switchback_original'));
    expect(filterCanonicalChoices('building', 'community centre')).toContain(choiceFor('validation_rec_centre_timber_hall'));
    expect(filterCanonicalChoices('building', 'higher education')).toContain(choiceFor('clay_biophilic_mass_timber_campus'));
    expect(filterCanonicalChoices('building', 'non market')).not.toContain(choiceFor('clay_neoclassical_brick_headquarters'));
  });

  it('leaves placement objects, rendering metadata and classifications untouched', () => {
    const choice = choiceFor('clay_neoclassical_brick_headquarters');
    const before = JSON.stringify(choice);
    const placement = choice.placements[0];
    cataloguePresentationFor(placement.id);
    catalogueStyleIds(choice);
    filterCanonicalChoices('building', 'neoclassical');
    expect(JSON.stringify(choice)).toBe(before);
    expect(CATALOGUE_ASSETS.find(asset => asset.id === placement.id)).toBe(placement);
    expect(choice.option.categoryId).toBe('contemporary_urban');
    expect(placement.description).toContain('source-locked');
  });
});
