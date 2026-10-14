import { describe, it, expect } from 'vitest';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { placeAsset, placementPlanRequest } from './catalogue';
import { storeyProgramSupports } from './buildingStoreyProgram';
import trial from '@/data/claudeFiveTrial.json';
import manifest from '../../../../seed/claude-five-trial/library.json';

describe('reviewed Claude hotel trial', () => {
  it('binds every trial card to its reviewed native-size model', () => {
    expect(trial.assets).toHaveLength(manifest.entries.length);
    for (const entry of manifest.entries) {
      const asset = placeAsset(entry.picker.id);
      expect(asset.model.revision).toBe(entry.candidate);
      expect(asset.model.variantId).toBe(entry.variant_id);
      expect(asset.reshapeMode).toBe('fixed_native');
      expect(asset.nativeDimensions).toEqual(['width', 'depth', 'height'].map(axis =>
        entry.model.native_dimensions_m[axis as keyof typeof entry.model.native_dimensions_m]));
      expect(storeyProgramSupports(asset.storeyProgram!, entry.native_floors + 1,
        entry.model.native_dimensions_m.height)).toBe(false);
      expect(CANONICAL_CHOICES.flatMap(c => c.placements).filter(p => p.id === asset.id)).toHaveLength(1);
    }
  });
  it('exposes only the exact reviewed hotel with its source image and native placement', () => {
    const asset = placeAsset('claude_scottish_baronial_hotel');
    const choice = CANONICAL_CHOICES.find(c => c.placements.some(p => p.id === asset.id));
    expect(choice?.option.photoUrl).toBe('/archetypes/buildings/chateauesque-grand-railway-hotel/variant_0.png');
    expect(asset.model.revision).toBe('clay-baronial-railway-hotel-clay-v006');
    expect(asset.reshapeMode).toBe('fixed_native');
    expect(asset.nativeDimensions).toEqual([78, 72, 42.400001525878906]);
    expect(placementPlanRequest(asset,82,76)?.archetype_id).toBe('scottish_baronial_granite_tower');
    expect(storeyProgramSupports(asset.storeyProgram!,5,42.4)).toBe(true);
    expect(storeyProgramSupports(asset.storeyProgram!,6,42.4)).toBe(false);
    expect(CANONICAL_CHOICES.flatMap(c=>c.placements).filter(p=>p.id==='claude_scottish_baronial_hotel')).toHaveLength(1);
  });
});
