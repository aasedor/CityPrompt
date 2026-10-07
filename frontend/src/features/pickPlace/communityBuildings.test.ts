import { describe, expect, it } from 'vitest';
import batch from '@/data/communityBuildingBatch.json';
import { COMMUNITY_BUILDING_ASSETS, validateRegistry } from './assetRegistry';
import { CANONICAL_CHOICES, filterCanonicalChoices } from './canonicalCatalogue';
import { placementPlanRequest } from './catalogue';
import { BUILDING_PROGRAMS, matchBuilding } from '@/features/zoningCatalogue/matching';

describe('five community buildings', () => {
  it('discovers each exact model with its reference photo and native dimensions', () => {
    expect(batch.entries).toHaveLength(5);
    expect(COMMUNITY_BUILDING_ASSETS).toHaveLength(5);
    expect(validateRegistry(COMMUNITY_BUILDING_ASSETS)).toEqual([]);
    for (const row of batch.entries) {
      const asset = COMMUNITY_BUILDING_ASSETS.find(a => a.model.variantId === row.variant_id)!;
      expect(asset.model.revision).toBe(row.candidate);
      expect(asset.properties.development_archetype_id).toBe(row.archetype_id);
      expect(asset.reshapeMode).toBe('fixed_native');
      expect(asset.width).toBeGreaterThan(asset.nativeDimensions![0]);
      expect(asset.depth).toBeGreaterThan(asset.nativeDimensions![1]);
      expect(placementPlanRequest(asset, asset.width, asset.depth)).toMatchObject({
        archetype_id: row.variant_id, target_floors: asset.properties.floor_count, allow_forced_fit: false,
      });
      const choice = CANONICAL_CHOICES.find(c => c.placements.some(a => a.id === asset.id && a.model.revision === row.candidate))!;
      expect(choice).toBeDefined();
      expect(choice.option.photoUrl).toMatch(/^\/archetypes\/buildings\/.+\/variant_\d+\.png$/);
      expect(filterCanonicalChoices('building', asset.label)).toContain(choice);
      expect(BUILDING_PROGRAMS[row.variant_id].revision).toBe(row.candidate);
    }
  });
  it('screens all occupancies and holds the unscreened liquor tenancy for review', () => {
    expect(BUILDING_PROGRAMS.montreal_depanneur_modern.components).toEqual([['Retail and Consumer Service'], ['Dwelling Unit']]);
    expect(BUILDING_PROGRAMS.inglewood_deco_infill.components).toEqual([['Retail and Consumer Service'], ['Office']]);
    const shops = COMMUNITY_BUILDING_ASSETS.find(a => a.model.variantId === 'strip_weathered_1980s')!;
    const match = matchBuilding(shops, { id: 'z', label: 'C-C1', source: 'test', district: { designation: 'C-C1' } });
    expect(match.status).toBe('review');
    expect(match.reasons.join(' ')).toContain('liquor');
    for (const id of ['rec_clerestory_modern', 'rec_log_cabin_vernacular']) {
      expect(BUILDING_PROGRAMS[id].components).toEqual([['Community Recreation Facility']]);
      expect(BUILDING_PROGRAMS[id].classification?.basis).toBe('teaching');
    }
  });
});
