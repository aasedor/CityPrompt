import { describe, expect, it } from 'vitest';
import buildings from '@/data/buildingArchetypes.json';
import parks from '@/data/openSpaceArchetypes.json';
import streets from '@/data/streetPathArchetypes.json';
import { BUILDING_AESTHETIC_OPTIONS_V2, OPENSPACE_AESTHETIC_OPTIONS_V2, ROADWAY_AESTHETIC_OPTIONS_V2 } from '@/components/viewer/aestheticCatalog';
import { CALGARY_GROUPS, CALGARY_SOURCES, calgaryGroup, classifyCalgaryAsset, filterCalgaryCatalogue, type CatalogueDomain } from './guide';

describe('Calgary catalogue guide', () => {
  it('gives every existing reference a valid group in its own domain', () => {
    for (const [domain, library] of [['building', buildings], ['park_plaza', parks], ['street_pathway', streets]] as const) {
      for (const seed of library.archetypes) {
        expect(calgaryGroup(classifyCalgaryAsset(domain, seed))?.domain, seed.id).toBe(domain);
      }
    }
    expect(new Set(CALGARY_GROUPS.map(group => group.id)).size).toBe(CALGARY_GROUPS.length);
  });

  it.each([
    ['calgary_modern_infill_house', 'detached'],
    ['london_townhouse', 'ground_housing'],
    ['toronto_brick_rowhouse', 'ground_housing'],
    ['montreal_duplex', 'two_home'],
    ['rndsqr_missing_middle_townhomes', 'ground_housing'],
  ])('separates form from legacy development labels for %s', (id, expected) => {
    expect(classifyCalgaryAsset('building', buildings.archetypes.find(item => item.id === id)!).groupId).toBe(expected);
  });

  it('accepts R-C1, RC1 and single-family naming without treating the tag as parcel permission', () => {
    const ids = (query: string) => filterCalgaryCatalogue(BUILDING_AESTHETIC_OPTIONS_V2, '', query).map(item => item.id);
    expect(ids('R-C1')).toEqual(ids('rc1'));
    expect(ids('single family')).toEqual(ids('R-C1'));
    expect(ids('R-C1')).toContain('calgary_modern_infill_house');
    expect(ids('R-C1')).not.toContain('toronto_brick_rowhouse');
    const home = BUILDING_AESTHETIC_OPTIONS_V2.find(item => item.id === 'calgary_modern_infill_house')!;
    expect(home.calgaryGuide?.basis).toBe('form_reference');
    expect(home.propertyPresets ?? {}).not.toHaveProperty('land_use_district');
  });

  it('keeps parking and amenities distinct from park service-area types', () => {
    const groupFor = (id: string) => calgaryGroup(OPENSPACE_AESTHETIC_OPTIONS_V2.find(item => item.id === id)?.calgaryGuide)?.id;
    expect(groupFor('surface_parking_lot')).toBe('space_other');
    expect(groupFor('neighborhood_park')).toBe('neighbourhood');
    expect(groupFor('tennis_court_cluster')).toBe('play_sport');
    expect(groupFor('linear_park_greenway')).toBe('linear');
    expect(groupFor('formal_civic_plaza')).toBe('plazas');
  });

  it('distinguishes draft Calgary manual sections from other street inspiration', () => {
    expect(ROADWAY_AESTHETIC_OPTIONS_V2.find(item => item.id === 'calgary_local')?.calgaryGuide).toEqual({ groupId: 'local', basis: 'draft_manual' });
    expect(ROADWAY_AESTHETIC_OPTIONS_V2.find(item => item.id === 'haussmann_boulevard')?.calgaryGuide?.basis).toBe('design_reference');
    expect(CALGARY_SOURCES.streetManual.status).toContain('Draft');
  });

  it('keeps unmapped concepts accessible and never invents a district for them', () => {
    for (const domain of ['building', 'park_plaza', 'street_pathway'] as CatalogueDomain[]) {
      const classification = classifyCalgaryAsset(domain, { id: 'future_unknown_asset' });
      expect(calgaryGroup(classification)?.districts).toEqual([]);
    }
  });

  it('has linked provenance for every category and no compliance or dimension fields', () => {
    for (const group of CALGARY_GROUPS) {
      expect(group.sources.length).toBeGreaterThan(0);
      for (const id of group.sources) expect(new URL(CALGARY_SOURCES[id].url).hostname).toBe('www.calgary.ca');
      expect(group).not.toHaveProperty('permitted');
      expect(group).not.toHaveProperty('maxFloors');
    }
  });
});
