import { afterEach, describe, expect, it, vi } from 'vitest';
import { CANONICAL_CHOICES, filterCanonicalChoices } from './canonicalCatalogue';
import { PARKADE_BUILDING_ASSETS } from './assetRegistry';
import { placeAsset, placementPlanRequest } from './catalogue';
import { storeyProgramSupports } from './buildingStoreyProgram';
import { pickerCategory } from './pickerCategories';
import { reviewedAssetClassification } from './catalogueClassification';
import manifest from '../../../../seed/parkade-family-trial/library.json';

describe('published reviewed parkades', () => {
  afterEach(() => { vi.unstubAllEnvs(); vi.resetModules(); });

  it('binds five building cards to their exact reviewed native assemblies', () => {
    expect(PARKADE_BUILDING_ASSETS).toHaveLength(5);
    expect(manifest.entries).toHaveLength(5);
    expect(new Set(PARKADE_BUILDING_ASSETS.map(asset => asset.model.variantId))).toEqual(new Set([
      'classic-concrete-v1', 'brick-v1', 'green-v1', 'solar-v1', 'courtyard-v1',
    ]));
    for (const entry of manifest.entries) {
      const asset = placeAsset(entry.picker.id);
      expect(asset).toMatchObject({ kind:'object', zoneType:'building', readiness:'ready', reshapeMode:'fixed_native',
        model:{ variantId:entry.variant_id, revision:entry.candidate, method:'RLASM 6.1' },
        calgaryGuide:{ groupId:'parkades' }, properties:{ native_plot_axes:true,
          development_archetype_id:entry.archetype_id, development_selected_variant_id:entry.variant_id,
          floors:entry.native_floors, floor_count:entry.native_floors } });
      expect(asset.properties.native_home_plot).not.toBe(true);
      expect(asset.nativeDimensions).toEqual(['width','depth','height'].map(axis =>
        entry.model.native_dimensions_m[axis as keyof typeof entry.model.native_dimensions_m]));
      expect(asset.footprintProgram).toBeUndefined();
      expect(asset.width*10).toBeCloseTo(Math.round(asset.width*10),8);
      expect(asset.depth*10).toBeCloseTo(Math.round(asset.depth*10),8);
      expect(asset.storeyProgram).toMatchObject({ mode:'fixed_authored_assembly',
        minStoreys:entry.native_floors, nativeStoreys:entry.native_floors, maxStoreys:entry.native_floors });
      expect(storeyProgramSupports(asset.storeyProgram!,entry.native_floors+1,asset.nativeDimensions![2])).toBe(false);
      expect(placementPlanRequest(asset,asset.width,asset.depth)?.archetype_id).toBe(entry.variant_id);
      expect(reviewedAssetClassification(asset).calgaryGuide.groupId).toBe('parkades');
      const choices=CANONICAL_CHOICES.filter(choice => choice.placements.some(p => p.id===asset.id));
      expect(choices).toHaveLength(1);
      expect(choices[0].domain).toBe('building');
      expect(choices[0].option.photoUrl).toBe(asset.thumbnail);
      expect(pickerCategory(choices[0])).toBe('parkades');
    }
    expect(filterCanonicalChoices('building','','parkades')).toHaveLength(5);
    expect(filterCanonicalChoices('street_pathway','','parkades')).toHaveLength(0);
  });

  it('exposes each stable saved ID once in production without trial flags', async () => {
    vi.stubEnv('DEV',false);
    vi.resetModules();
    const registry=await import('./assetRegistry');
    const catalogue=await import('./canonicalCatalogue');
    expect(registry.PARKADE_BUILDING_ASSETS).toHaveLength(5);
    expect(registry.CATALOGUE_ASSETS.filter(asset => asset.calgaryGuide.groupId==='parkades')).toHaveLength(5);
    expect(catalogue.filterCanonicalChoices('building','','parkades')).toHaveLength(5);
    for(const entry of manifest.entries) {
      expect(registry.CATALOGUE_ASSETS.filter(asset=>asset.id===entry.picker.id)).toHaveLength(1);
    }
  });
});
