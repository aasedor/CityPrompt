import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { prepareReviewBuildingLandscape } from './reviewBuildingLandscape';

const zone: SiteZone = { id: 'hall', project_id: 'qa', color: '#ffffff', sort_order: 0, created_at: '', updated_at: '',
  zone_type: 'building', coordinates: rectangleAt([-114, 51], 66, 64, 0),
  properties: { building_archetype_id: 'montreal_second_empire_civic',
    development_selected_variant_id: 'montreal_civic_city_hall',
    pick_place_model_revision: 'clay-second-empire-city-hall-clay-v010' } };
const boundary = { id: 'site', coordinates: rectangleAt([-114, 51], 200, 200, 0) } as SiteZone;

function fixture() {
  const scene = new THREE.Group();
  const paving = new THREE.MeshStandardMaterial({ color: '#a39e94' });
  paving.name = 'CLAY_CONCRETE';
  const pad = new THREE.Mesh(new THREE.BoxGeometry(62, .008, 60), paving);
  pad.geometry.translate(-2.5, .004, 5);
  pad.name = 'CLAY_CONCRETE';
  const stone = new THREE.MeshStandardMaterial({ color: '#a8a394' });
  stone.name = 'CLAY_STONE';
  const building = new THREE.Mesh(new THREE.BoxGeometry(44, 39, 37), stone);
  building.position.y = 19.5;
  const steps = new THREE.Mesh(new THREE.BoxGeometry(6.4, .2, 4), stone);
  steps.position.set(0, .1, 26);
  scene.add(pad, building, steps);
  return { scene, pad, building, steps, texture: new THREE.Texture() };
}

function materialAt(scene: THREE.Object3D, x: number, z: number) {
  scene.updateMatrixWorld(true);
  const ray = new THREE.Raycaster(new THREE.Vector3(x, 50, z), new THREE.Vector3(0, -1, 0));
  const hit = ray.intersectObject(scene, true)[0];
  expect(hit).toBeDefined();
  const mesh = hit.object as THREE.Mesh;
  return Array.isArray(mesh.material) ? mesh.material[hit.face!.materialIndex] : mesh.material;
}

describe('authored city hall ground finish', () => {
  it('removes the broad grey surround while retaining the measured entrance approach', () => {
    const { scene, texture } = fixture();
    const result = prepareReviewBuildingLandscape(scene, zone, { boundary, texture });
    expect((materialAt(result.clone, 20, 33) as THREE.MeshStandardMaterial).map).toBe(texture);
    expect(materialAt(result.clone, 0, 33).name).toBe('CLAY_CONCRETE');
    expect(materialAt(result.clone, 0, 26).name).toBe('CLAY_STONE');
  });

  it('shares the site texture with geographically aligned UVs, including a rotated plot', () => {
    const { scene, texture } = fixture();
    const result = prepareReviewBuildingLandscape(scene, { ...zone,
      coordinates: rectangleAt([-114, 51], 66, 64, 90) }, { boundary, texture });
    result.clone.updateMatrixWorld(true);
    const hit = new THREE.Raycaster(new THREE.Vector3(20, 50, 33), new THREE.Vector3(0, -1, 0))
      .intersectObject(result.clone, true)[0];
    // Original bounds centre is (-2.5, 5). Native (20,33) becomes
    // east/north (28,22.5) at 90 degrees on this 200 m square site.
    expect(hit.uv!.x).toBeCloseTo(2.56, 4);
    expect(hit.uv!.y).toBeCloseTo(2.45, 4);
  });
  it('keeps grass phase aligned after the compiled instance rotates and offsets inside its plot', () => {
    const { scene, texture } = fixture();
    const matrix = new THREE.Matrix4().makeTranslation(4, 7, 0)
      .multiply(new THREE.Matrix4().makeRotationZ(-Math.PI / 2))
      .multiply(new THREE.Matrix4().makeRotationX(Math.PI / 2))
      .multiply(new THREE.Matrix4().makeTranslation(2.5, 0, -5));
    const result = prepareReviewBuildingLandscape(scene, zone, { boundary, texture }, { matrix, origin: [-114, 51] });
    result.clone.updateMatrixWorld(true);
    const hit = new THREE.Raycaster(new THREE.Vector3(20, 50, 33), new THREE.Vector3(0, -1, 0))
      .intersectObject(result.clone, true)[0];
    // Native (20,33) -> centred (22.5,-28) -> turned/offset (-24,-15.5).
    expect(hit.uv!.x).toBeCloseTo(1.52, 4);
    expect(hit.uv!.y).toBeCloseTo(1.69, 4);
  });

  it('owns only changed buffers/materials and leaves source assets, architecture and bounds intact', () => {
    const { scene, pad, building, steps, texture } = fixture();
    const sourceBounds = new THREE.Box3().setFromObject(scene);
    const result = prepareReviewBuildingLandscape(scene, zone, { boundary, texture });
    expect(pad.material.name).toBe('CLAY_CONCRETE');
    expect((pad.material as THREE.MeshStandardMaterial).map).toBeNull();
    expect(result.clone.children[0]).not.toBe(pad);
    expect((result.clone.children[1] as THREE.Mesh).geometry).toBe(building.geometry);
    expect((result.clone.children[1] as THREE.Mesh).material).toBe(building.material);
    expect((result.clone.children[2] as THREE.Mesh).geometry).toBe(steps.geometry);
    const bounds = new THREE.Box3().setFromObject(result.clone);
    expect(bounds.min.distanceTo(sourceBounds.min)).toBeLessThan(.00001);
    expect(bounds.max.distanceTo(sourceBounds.max)).toBeLessThan(.00001);
    expect(result.ownedGeometries).toHaveLength(1);
    expect(result.ownedMaterials).toHaveLength(1);
    expect(result.ownedMaterials[0]).not.toBe(pad.material);
  });

  it('does not recolour a different candidate or an unprepared natural site', () => {
    const { scene, texture, pad } = fixture();
    const unknown = { ...zone, properties: { ...zone.properties, pick_place_model_revision: 'another-candidate' } };
    for (const result of [prepareReviewBuildingLandscape(scene, unknown, { boundary, texture }),
      prepareReviewBuildingLandscape(scene, zone, null)]) {
      expect((result.clone.children[0] as THREE.Mesh).geometry).toBe(pad.geometry);
      expect(result.ownedGeometries).toEqual([]);
      expect(result.ownedMaterials).toEqual([]);
    }
  });
});
