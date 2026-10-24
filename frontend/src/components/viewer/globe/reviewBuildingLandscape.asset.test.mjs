import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { GLTFLoader } from 'three-stdlib';
import * as THREE from 'three';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { prepareReviewBuildingLandscape } from './reviewBuildingLandscape';

const bytes = readFileSync(resolve(process.cwd(), '../seed/model-library/objects/claude-five/models/clay-second-empire-city-hall-clay-v010.glb'));
// Ordinary source-only CI may leave the optional asset as an LFS pointer.
// The deterministic geometry tests always run; a hydrated checkout also checks
// the exact reviewed asset. Corrupt binary assets must still fail this check.
const lfsPointer = bytes.subarray(0, 64).toString().startsWith('version https://git-lfs.github.com/spec/v1');

it.skipIf(lfsPointer)('blends the actual v010 GLB streets and sidewalks while preserving its entrance steps, stone walls and bounds', async () => {
  const buffer = new ArrayBuffer(bytes.byteLength);
  new Uint8Array(buffer).set(bytes);
  const gltf = await new GLTFLoader().parseAsync(buffer, '');
  const zone = { id: 'hall', coordinates: rectangleAt([-114, 51], 66, 64, 0), properties: {
    building_archetype_id: 'montreal_second_empire_civic', development_selected_variant_id: 'montreal_civic_city_hall',
    pick_place_model_revision: 'clay-second-empire-city-hall-clay-v010',
  } };
  const boundary = { id: 'site', coordinates: rectangleAt([-114, 51], 200, 200, 0) };
  const originalBounds = new THREE.Box3().setFromObject(gltf.scene);
  const texture = new THREE.Texture();
  const result = prepareReviewBuildingLandscape(gltf.scene, zone, { boundary, texture });
  const materialAt = (x, z) => {
    result.clone.updateMatrixWorld(true);
    const hit = new THREE.Raycaster(new THREE.Vector3(x, 50, z), new THREE.Vector3(0, -1, 0))
      .intersectObject(result.clone, true)[0];
    expect(hit).toBeDefined();
    return Array.isArray(hit.object.material) ? hit.object.material[hit.face.materialIndex] : hit.object.material;
  };
  expect(materialAt(20, 33).map).toBe(texture);
  expect(materialAt(27, 0).map).toBe(texture);
  expect(materialAt(0, 33).name).toBe('CLAY_CONCRETE');
  expect(materialAt(0, 26).name).toBe('CLAY_PALE');
  expect(materialAt(-29, 28.94).map).toBe(texture);
  expect(materialAt(-27.44, 33).map).toBe(texture);
  const beforeStone = gltf.scene.getObjectByName('CLAY_STONE');
  const afterStone = result.clone.getObjectByName('CLAY_STONE');
  const upperTriangles = mesh => {
    const p = mesh.geometry.getAttribute('position'), index = mesh.geometry.getIndex();
    const triangles = [];
    for (let i = 0; i < (index?.count ?? p.count); i += 3) {
      const ids = [0, 1, 2].map(k => index ? index.getX(i + k) : i + k);
      if (ids.every(id => p.getY(id) <= .121)) continue;
      triangles.push(ids.map(id => [p.getX(id), p.getY(id), p.getZ(id)].map(value => value.toFixed(5)).join(',')).sort().join('|'));
    }
    return triangles.sort();
  };
  expect(upperTriangles(afterStone)).toEqual(upperTriangles(beforeStone));
  expect(afterStone.material[0]).toBe(beforeStone.material);
  expect(result.clone.getObjectByName('CLAY_PALE').geometry).toBe(gltf.scene.getObjectByName('CLAY_PALE').geometry);
  const bounds = new THREE.Box3().setFromObject(result.clone);
  expect(bounds.min.distanceTo(originalBounds.min)).toBeLessThan(.00001);
  expect(bounds.max.distanceTo(originalBounds.max)).toBeLessThan(.00001);
});
