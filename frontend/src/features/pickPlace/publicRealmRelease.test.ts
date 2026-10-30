import { describe, expect, it } from 'vitest';
import { publicRealmReleaseRows, releaseGateErrors, PUBLIC_REALM_RELEASE_ASSETS, type PublicRealmReleaseRow } from './publicRealmRelease';
import manifest from '@/data/publicRealmRelease20261023.json';
import { browseAssets } from './assetRegistry';

describe('exact fixed public-realm release boundary', () => {
  it.each(manifest.models.filter(row => row.status === 'ready'))('shows $candidate in its browsing category and search', row => {
    expect(browseAssets(row.asset.label, row.asset.calgaryGuide.groupId).map(asset => asset.id)).toContain(row.asset.id);
  });
  it('publishes only the exact twelve reviewed variants and retains disabled saved identities', () => {
    const expected = manifest.models.filter(row => row.status === 'ready').map(row => row.asset.id);
    expect(expected).toHaveLength(12);
    expect(publicRealmReleaseRows(false).map(row => row.asset.id)).toEqual(expected);
    expect(PUBLIC_REALM_RELEASE_ASSETS.map(asset => asset.id)).toEqual(expected);
    expect(publicRealmReleaseRows(true)).toHaveLength(16);
    expect(manifest.models).toHaveLength(19);
  });

  it.each([
    ['clay-halifax-public-gardens-clay-v005-park-only-r001', '9282a9ffd6a31997407cff90ebaea2c95e7ece983746d33e42f1c6e9ae154b79'],
    ['clay-princes-island-park-clay-v005', '498a973435fc8bc077084d3ee630babc55574a7365fdbd978a1cea742525a0ec'],
  ])('keeps raw saved identity %s disabled while rehearsing distinct optimized bytes', (candidate, digest) => {
    const raw = manifest.models.find(row => row.candidate === candidate)! as unknown as PublicRealmReleaseRow;
    const optimized = manifest.models.find(row => row.candidate === candidate+'-gpu-r001')! as unknown as PublicRealmReleaseRow;
    expect(raw.status).toBe('prepared');
    expect(optimized.status).toBe('ready');
    expect(optimized.runtime_sha256).toBe(digest);
    expect(optimized.asset.id).not.toBe(raw.asset.id);
    expect(optimized.fixture.url).not.toBe(raw.fixture.url);
    expect(optimized.source_sha256).toBe(raw.source_sha256);
    expect(optimized.asset.nativeDimensions).toEqual(raw.asset.nativeDimensions);
    expect(publicRealmReleaseRows(true, [raw, optimized])).toEqual([optimized]);
    expect(publicRealmReleaseRows(false, [raw, optimized], true)).toEqual([optimized]);
    expect(publicRealmReleaseRows(false, [{ ...raw, status: 'retired' }], true)).toEqual([]);
  });

  it('requires exact complete visual and runtime review before production acceptance', () => {
    const row = structuredClone(manifest.models.find(row => row.candidate === 'clay-ice-rink-market-square-clay-v007-park-only-r001')!) as unknown as PublicRealmReleaseRow;
    row.status = 'runtime_trial';
    row.visual_review.status = 'pending';
    row.runtime_review.status = 'pending';
    expect(releaseGateErrors(row)).toContain('visual_review_pending');
    expect(releaseGateErrors(row)).toContain('runtime_review_pending');
    row.status = 'ready';
    row.visual_review = { status: 'passed', scope: 'complete_runtime_derivative', runtime_sha256: row.runtime_sha256,
      evidence_sha256: 'a'.repeat(64), unresolved_p0: 0, unresolved_p1: 0 };
    row.runtime_review = { status: 'passed', runtime_sha256: row.runtime_sha256, evidence_sha256: 'b'.repeat(64) };
    expect(releaseGateErrors(row)).toEqual([]);
    expect(publicRealmReleaseRows(false, [row])).toEqual([row]);
    row.visual_review.runtime_sha256 = '0'.repeat(64);
    expect(releaseGateErrors(row)).toContain('visual_review_pending');
    expect(publicRealmReleaseRows(false, [row])).toEqual([]);
  });

  it('rejects a path, variant, revision or native-size substitution', () => {
    const original = manifest.models.find(row => row.candidate === 'clay-ice-rink-market-square-clay-v007-park-only-r001')! as unknown as PublicRealmReleaseRow;
    for (const mutate of [
      (row: typeof original) => { row.fixture.url = '/validation-assets/claude-local/other.glb'; },
      (row: typeof original) => { row.asset.model.revision = '0'.repeat(64); },
      (row: typeof original) => { row.asset.properties.green_space_selected_variant_id = 'other'; },
      (row: typeof original) => { row.asset.width += 1; },
    ]) {
      const row = structuredClone(original); mutate(row);
      expect(releaseGateErrors(row)).toContain('identity_mismatch');
      expect(publicRealmReleaseRows(true, [row])).toEqual([]);
    }
  });
});
