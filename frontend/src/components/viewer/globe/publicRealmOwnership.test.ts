import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { preparePublicRealmOwnedScene, publicRealmOwnership } from './publicRealmOwnership';
import manifest from '@/data/publicRealmRelease20261023.json';
import { publicRealmReleaseRows, releaseGateErrors, type PublicRealmReleaseRow } from '@/features/pickPlace/publicRealmRelease';

const candidates = ['clay-barcelona-passatge-clay-v006', 'clay-brick-arch-viaduct-clay-v003', 'clay-stone-arch-road-bridge-clay-v003'];
describe('compact exact public-realm pilots', () => {
  it.each(candidates)('%s keeps a snug native plot and stays behind the production review gate', candidate => {
    const row = manifest.models.find(row => row.candidate === candidate) as unknown as PublicRealmReleaseRow;
    expect(row).toBeDefined();
    expect(row.status).toBe('runtime_trial');
    expect(releaseGateErrors(row)).not.toContain('identity_mismatch');
    expect(publicRealmReleaseRows(false, [row])).toEqual([]);
    expect(publicRealmReleaseRows(true, [row])).toEqual([row]);
    const contract = publicRealmOwnership(row.fixture);
    expect(contract).toBeDefined();
    expect(row.asset.width - row.asset.nativeDimensions![0]).toBeLessThan(1);
    expect(row.asset.depth - row.asset.nativeDimensions![1]).toBeLessThan(1);
    expect(row.asset.width * row.asset.depth).toBeLessThan(3500);
  });
  it('does not crop an unregistered upload or a mismatched source/contract identity', () => {
    const row = manifest.models.find(row => row.candidate === candidates[0]) as unknown as PublicRealmReleaseRow;
    expect(row).toBeDefined();
    for (const fixture of [{ ...row.fixture, sha256: '0'.repeat(64) },
      { ...row.fixture, url: '/api/v1/files/imported/' + candidates[0] + '.glb' },
      { ...row.fixture, ownershipSha256: '0'.repeat(64) }]) {
      const source = new THREE.Group(); source.add(new THREE.Mesh(new THREE.BoxGeometry(100, 1, 100)));
      const result = preparePublicRealmOwnedScene(source, fixture);
      expect(result.applied).toBe(false);
      expect(new THREE.Box3().setFromObject(result.clone)).toEqual(new THREE.Box3().setFromObject(source));
    }
  });
});
