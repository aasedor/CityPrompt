import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { preparePublicRealmOwnedScene, publicRealmOwnership } from './publicRealmOwnership';
import manifest from '@/data/publicRealmRelease20261023.json';
import { publicRealmReleaseRows, releaseGateErrors, type PublicRealmReleaseRow } from '@/features/pickPlace/publicRealmRelease';

const candidates = ['clay-barcelona-passatge-clay-v006', 'clay-brick-arch-viaduct-clay-v003', 'clay-stone-arch-road-bridge-clay-v003'];

function markings() {
  const source = new THREE.Group();
  const parts = [[0, 0, 200, .15], [-25, -3, 3, .12], [-25, 3, 3, .12], [0, 8, 200, .15]]
    .map(([x, z, width, depth]) => new THREE.BoxGeometry(width, .006, depth).toNonIndexed().translate(x, 11.003, z));
  const geometry = new THREE.BufferGeometry();
  for (const name of ['position', 'normal', 'uv']) geometry.setAttribute(name,
    new THREE.Float32BufferAttribute(parts.flatMap(part => Array.from(part.getAttribute(name).array)), name === 'uv' ? 2 : 3));
  const white = new THREE.MeshStandardMaterial(); white.name = 'CLAY_WHITE';
  const marking = new THREE.Mesh(geometry, white); marking.name = 'CLAY_WHITE'; source.add(marking);
  // Only material lookup for the existing explicitly declared bank supports.
  for (const name of ['CLAY_QUAY', 'CLAY_ASPHALT']) {
    const material = new THREE.MeshStandardMaterial(); material.name = name;
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(300, .01, 300), material); mesh.name = name; source.add(mesh);
  }
  return { source, marking };
}

function whiteAt(scene: THREE.Object3D, x: number, z: number) {
  scene.updateMatrixWorld(true);
  const mesh = scene.getObjectByName('CLAY_WHITE')!;
  return new THREE.Raycaster(new THREE.Vector3(x, 12, z), new THREE.Vector3(0, -1, 0))
    .intersectObject(mesh).length > 0;
}
describe('compact exact public-realm pilots', () => {
  it.each([false, true])('clips a crossing source centreline without surrounding white context (transformed: %s)', transformed => {
    const row = manifest.models.find(row => row.candidate === candidates[2]) as unknown as PublicRealmReleaseRow;
    const { source, marking } = markings();
    if (transformed) { marking.geometry.translate(-5, -4, -2); marking.position.set(5, 4, 2); }
    const original = marking.geometry.getAttribute('position').array.slice();
    const result = preparePublicRealmOwnedScene(source, row.fixture);
    for (const x of [-27.4, -20, 0, 20, 40.9]) expect(whiteAt(result.clone, x, 0), `centreline at ${x}`).toBe(true);
    for (const x of [-28, 41.1, 90]) expect(whiteAt(result.clone, x, 0), `outside marking envelope at ${x}`).toBe(false);
    expect(whiteAt(result.clone, -25, 3)).toBe(true);
    expect(whiteAt(result.clone, -25, -3)).toBe(true);
    expect(whiteAt(result.clone, -20, 3)).toBe(false);
    expect(whiteAt(result.clone, 0, 8)).toBe(false);
    expect(marking.geometry.getAttribute('position').array).toEqual(original);
    expect((result.clone.getObjectByName('CLAY_WHITE') as THREE.Mesh).material).toBe(marking.material);
    expect(result.clone.getObjectByName('CLAY_ASPHALT')).toBeUndefined();
  });
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
