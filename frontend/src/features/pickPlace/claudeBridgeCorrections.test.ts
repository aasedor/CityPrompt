import { describe, expect, it } from 'vitest';
import release from '@/data/publicRealmRelease20261023.json';
import { releaseGateErrors, publicRealmReleaseRows, type PublicRealmReleaseRow } from './publicRealmRelease';
import { pickerHeroImage } from './pickerHeroImages';

describe('bounded corrected bridge pilots', () => {
  it('keeps the planted bridge exact, native and photographic without publishing it', () => {
    const row = release.models.find(r => r.candidate === 'clay-planted-green-bridge-clay-v005') as unknown as PublicRealmReleaseRow | undefined;
    expect(row).toBeDefined();
    if (!row) throw new Error('Missing corrected planted bridge');
    expect(row.runtime_sha256).toBe('d7dddc9371b5cf554bcb372b6d46c8fc0e6256d7335bd47ff542420463f20066');
    expect(row.asset.model.variantId).toBe('landscape_park_pedestrian_bridge_v2');
    expect(row.asset.width).toBeLessThan(40);
    expect(row.asset.depth).toBeLessThan(103);
    expect(row.asset.reshapeMode).toBe('fixed_native');
    expect(row.asset.maxWidth).toBe(row.asset.minWidth);
    expect(row.asset.maxDepth).toBe(row.asset.minDepth);
    expect(row.status).toBe('runtime_trial');
    expect(publicRealmReleaseRows(false).some(r => r.asset.id === row.asset.id)).toBe(false);
    expect(pickerHeroImage(row.asset.id, '')).toBe('/archetypes/streets/landscape-park-pedestrian-bridge/variant_2.png');
  });
  it('keeps the guarded tied-arch exact and photographic without publishing it', () => {
    const row = release.models.find(r => r.candidate === 'clay-tied-arch-shared-bridge-clay-v005') as unknown as PublicRealmReleaseRow | undefined;
    expect(row).toBeDefined();
    if (!row) throw new Error('Missing corrected tied-arch bridge');
    expect(row.runtime_sha256).toBe('7900ce3b41b0a668b4c68e6dc86d55a8ee3e7eb1d06076b637e0114be5ead94e');
    expect(row.asset.model.variantId).toBe('shared_cycle_pedestrian_bridge_v1');
    expect(row.asset.width).toBeLessThan(65);
    expect(row.asset.depth).toBeLessThan(29);
    expect(row.asset.reshapeMode).toBe('fixed_native');
    expect(row.asset.maxWidth).toBe(row.asset.minWidth);
    expect(row.asset.maxDepth).toBe(row.asset.minDepth);
    expect(row.status).toBe('runtime_trial');
    expect(publicRealmReleaseRows(false).some(r => r.asset.id === row.asset.id)).toBe(false);
    expect(pickerHeroImage(row.asset.id, '')).toBe('/archetypes/streets/shared-cycle-pedestrian-bridge/variant_1.png');
  });
  it('keeps the timber correction exact, compact, photographic and local only', () => {
    const row = release.models.find(r => r.candidate === 'clay-timber-covered-footbridge-clay-v004') as unknown as PublicRealmReleaseRow | undefined;
    expect(row).toBeDefined();
    if (!row) throw new Error('Missing timber bridge binding');
    expect(row.runtime_sha256).toBe('0dbeb2731dbe390ead3b053d65853262887454aecaf36fb8a9d16a5b66a195ad');
    expect(row.asset.model.variantId).toBe('urban_pedestrian_footbridge_v2');
    expect(row.asset.width).toBeLessThan(45);
    expect(row.asset.depth).toBeLessThan(10);
    expect(row.asset.maxWidth).toBe(row.asset.width);
    expect(row.asset.maxDepth).toBe(row.asset.depth);
    expect(row.asset.reshapeMode).toBe('fixed_native');
    expect(row.status).toBe('runtime_trial');
    expect(publicRealmReleaseRows(false).some(r => r.asset.id === row.asset.id)).toBe(false);
    expect(publicRealmReleaseRows(true).some(r => r.asset.id === row.asset.id)).toBe(true);
    expect(releaseGateErrors(row)).not.toContain('identity_mismatch');
    expect(pickerHeroImage(row.asset.id, '')).toBe('/archetypes/streets/urban-pedestrian-footbridge/variant_2.png');
  });
});
