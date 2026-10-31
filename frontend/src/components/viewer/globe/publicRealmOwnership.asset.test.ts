// @ts-expect-error -- Node APIs are provided by Vitest.
import { readFileSync } from 'node:fs';
// @ts-expect-error -- Node APIs are provided by Vitest.
import { resolve } from 'node:path';
// @ts-expect-error -- Node APIs are provided by Vitest.
import { createHash } from 'node:crypto';
import { it, expect } from 'vitest';
import { GLTFLoader } from 'three-stdlib';
import * as THREE from 'three';
import contracts from '@/features/pickPlace/publicRealmOwnershipContracts.json';
import manifest from '@/data/publicRealmRelease20261023.json';
import { preparePublicRealmOwnedScene, prepareNativePlacementScene } from './publicRealmOwnership';

const triangles = (scene: THREE.Object3D) => {
  let count = 0; scene.traverse(object => { const mesh = object as THREE.Mesh;
    if (mesh.isMesh) count += (mesh.geometry.getIndex()?.count ?? mesh.geometry.getAttribute('position').count) / 3;
  }); return count;
};

it('retains the stone bridge solid centreline continuously while clipping its source road extension', async () => {
  const row = manifest.models.find(row => row.candidate === 'clay-stone-arch-road-bridge-clay-v003')!;
  const bytes = readFileSync(resolve('public' + row.fixture.url));
  expect(createHash('sha256').update(bytes).digest('hex')).toBe('5300077e633cecc901ef86bb0a78e0b7bd0dce0588c613becbb2195b92337d6d');
  const buffer = new ArrayBuffer(bytes.byteLength); new Uint8Array(buffer).set(bytes);
  const source = (await new GLTFLoader().parseAsync(buffer, '')).scene;
  const result = preparePublicRealmOwnedScene(source, row.fixture);
  result.clone.updateMatrixWorld(true);
  const white = result.clone.getObjectByName('CLAY_WHITE')!;
  const hit = (x: number, z: number) => new THREE.Raycaster(new THREE.Vector3(x, 12, z), new THREE.Vector3(0, -1, 0))
    .intersectObject(white).length > 0;
  for (const x of [-27.4, -20, 0, 20, 40.9]) expect(hit(x, 0), `solid centreline at ${x}`).toBe(true);
  for (const x of [-28, 41.1, 100]) expect(hit(x, 0), `source road excluded at ${x}`).toBe(false);
  expect(hit(-25, 3)).toBe(true);
  expect(hit(-22, 3)).toBe(false);
  expect(createHash('sha256').update(bytes).digest('hex')).toBe(row.runtime_sha256);
});
for (const [candidate, contract] of Object.entries(contracts)) {
  it(candidate + ' retains the measured complete assemblies and exact source bytes', async () => {
    const row = manifest.models.find(row => row.candidate === candidate)!;
    const bytes = readFileSync(resolve('public' + row.fixture.url));
    expect(createHash('sha256').update(bytes).digest('hex')).toBe(contract.sourceSha256);
    const buffer = new ArrayBuffer(bytes.byteLength); new Uint8Array(buffer).set(bytes);
    const gltf = await new GLTFLoader().parseAsync(buffer, '');
    const before = new THREE.Box3().setFromObject(gltf.scene, true);
    expect(triangles(gltf.scene)).toBe(contract.sourceTriangles);
    const result = preparePublicRealmOwnedScene(gltf.scene, row.fixture);
    expect(result.applied).toBe(true);
    const preview = prepareNativePlacementScene(gltf.scene, row.fixture.url, row.asset.id);
    expect(preview.applied).toBe(true);
    expect(triangles(preview.clone)).toBe(triangles(result.clone));
    expect(triangles(result.clone)).toBe('runtimeTriangles' in contract ? contract.runtimeTriangles : contract.retainedTriangles);
    if (candidate === 'clay-stone-arch-road-bridge-clay-v003') {
      const footways = result.clone.getObjectByName('CLAY_PAVING');
      expect(footways, 'both authored raised bridge footways must survive').toBeDefined();
      expect(triangles(footways!)).toBe(24);
      const footwayBox = new THREE.Box3().setFromObject(footways!, true);
      expect(footwayBox.min.x).toBeCloseTo(-27.5);
      expect(footwayBox.max.x).toBeCloseTo(41);
      expect(footwayBox.min.y).toBeCloseTo(10.96);
      expect(footwayBox.max.y).toBeCloseTo(11.15);
      expect(footwayBox.min.z).toBeCloseTo(-8.4);
      expect(footwayBox.max.z).toBeCloseTo(8.4);
      for (const name of ['CLAY_GLASS', 'CLAY_RED', 'CLAY_CAR', 'CLAY_VAN', 'CLAY_DARK']) {
        expect(result.clone.getObjectByName(name), 'no vehicle assembly fragments').toBeUndefined();
      }
      for (const side of ['west', 'east']) {
        const support = result.clone.getObjectByName(`runtime-context-${side}-bank`);
        expect(support, 'outer springings and curved plinths require bounded bank supports').toBeDefined();
        const box = new THREE.Box3().setFromObject(support!, true);
        expect(box.min.y).toBeCloseTo(0);
        expect(box.max.y).toBeCloseTo(10.96);
      }
    }
    for (const [name, count] of Object.entries(contract.meshTriangles)) {
      const mesh = result.clone.getObjectByName(name);
      expect(mesh ? triangles(mesh) : 0, name).toBe(count);
    }
    const bounds = new THREE.Box3().setFromObject(result.clone, true);
    [...bounds.min.toArray(), ...bounds.max.toArray()].forEach((v, i) => expect(v).toBeCloseTo(contract.bounds[i], 3));
    expect(triangles(gltf.scene)).toBe(contract.sourceTriangles);
    expect(new THREE.Box3().setFromObject(gltf.scene, true)).toEqual(before);
    expect(createHash('sha256').update(bytes).digest('hex')).toBe(contract.sourceSha256);
    result.ownedGeometries.forEach(geometry => geometry.dispose());
  });
}
