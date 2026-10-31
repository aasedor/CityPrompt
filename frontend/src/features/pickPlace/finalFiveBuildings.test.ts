import { describe, expect, it } from 'vitest';
import batch from '@/data/finalFiveBuildingBatch.json';
import { FINAL_FIVE_BUILDING_ASSETS, validateRegistry } from './assetRegistry';
import { CANONICAL_CHOICES, filterCanonicalChoices } from './canonicalCatalogue';
import { placementPlanRequest } from './catalogue';
import { BUILDING_PROGRAMS } from '@/features/zoningCatalogue/matching';
import { reviewedEntranceForAsset } from './reviewedEntrances';
import { catalogueStyleIds } from './catalogueFacets';

describe('final five neighbourhood building trial', () => {
  it('keeps every enrolled exact revision discoverable, photographed and placeable at native size', () => {
    expect(batch.entries).toHaveLength(5);
    expect(FINAL_FIVE_BUILDING_ASSETS).toHaveLength(batch.entries.length);
    expect(validateRegistry(FINAL_FIVE_BUILDING_ASSETS)).toEqual([]);
    for (const row of batch.entries) {
      const asset = FINAL_FIVE_BUILDING_ASSETS.find(a => a.model.variantId === row.variant_id)!;
      expect(asset.model.revision).toBe(row.candidate);
      expect(asset.properties.development_archetype_id).toBe(row.archetype_id);
      expect(asset.reshapeMode).toBe('fixed_native');
      expect(reviewedEntranceForAsset(asset)).toMatchObject({ fixedNative: true });
      expect(asset.entranceSnap!.widthM).toBeGreaterThanOrEqual(2.5);
      expect(asset.width).toBeGreaterThan(asset.nativeDimensions![0]);
      expect(asset.depth).toBeGreaterThan(asset.nativeDimensions![1]);
      expect(placementPlanRequest(asset, asset.width, asset.depth)).toMatchObject({
        archetype_id: row.variant_id, target_floors: asset.properties.floor_count, allow_forced_fit: false,
      });
      const choice = CANONICAL_CHOICES.find(c => c.placements.some(a => a.id === asset.id))!;
      expect(choice).toBeDefined();
      const styles: Record<string, string[]> = {
        'final-courtyard-block-v1': ['contemporary'],
        'final-seniors-apartments-v1': ['contemporary'],
        'final-transit-pavilion-v1': ['timber_contemporary', 'structural'],
        'final-health-centre-v1': ['contemporary', 'timber_contemporary'],
        'final-urban-grocery-v1': ['contemporary', 'historic_industrial'],
      };
      expect(catalogueStyleIds(choice)).toEqual(styles[row.variant_id]);
      expect(choice.option.photoUrl).toBe(`/archetypes/buildings/${row.archetype_id}/front.png`);
      expect(filterCanonicalChoices('building', asset.label)).toContain(choice);
      expect(BUILDING_PROGRAMS[row.variant_id].revision).toBe(row.candidate);
    }
  });
});
