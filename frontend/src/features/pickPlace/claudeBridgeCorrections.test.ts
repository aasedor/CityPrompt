import { describe, expect, it } from 'vitest';
import release from '@/data/publicRealmRelease20261023.json';
import { releaseGateErrors, publicRealmReleaseRows, type PublicRealmReleaseRow } from './publicRealmRelease';
import { pickerHeroImage } from './pickerHeroImages';

describe('bounded corrected bridge pilots', () => {
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
