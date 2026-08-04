import { describe, expect, it } from 'vitest';
import * as THREE from 'three';

import { inspectStreetRenderReadiness } from './streetRenderReadiness';

function texture(size: number): THREE.DataTexture {
  // The audit reads metadata only; avoid allocating a full 2K pixel payload.
  return new THREE.DataTexture(new Uint8Array(4), size, size);
}

describe('inspectStreetRenderReadiness', () => {
  it('measures only authored roots and reports their PBR resources', () => {
    const scene = new THREE.Scene();
    const buildingRoot = new THREE.Group();
    buildingRoot.name = 'siteforge-direct3d-building';
    const material = new THREE.MeshStandardMaterial({ map: texture(2048) });
    material.normalMap = texture(2048);
    material.roughnessMap = texture(2048);
    const building = new THREE.Mesh(new THREE.BoxGeometry(), material);
    building.castShadow = true;
    buildingRoot.add(building);
    scene.add(buildingRoot);

    const parkRoot = new THREE.Group();
    parkRoot.name = 'siteforge-direct3d-park';
    parkRoot.add(new THREE.InstancedMesh(
      new THREE.PlaneGeometry(),
      new THREE.MeshStandardMaterial(),
      2,
    ));
    scene.add(parkRoot);

    // Google/context geometry is deliberately outside the authored roots.
    scene.add(new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshBasicMaterial()));

    const result = inspectStreetRenderReadiness(scene);
    expect(result.authoredMeshCount).toBe(2);
    expect(result.buildingMeshCount).toBe(1);
    expect(result.uniquePbrMaterialCount).toBe(2);
    expect(result.baseColorTextureCount).toBe(1);
    expect(result.normalMapCount).toBe(1);
    expect(result.roughnessMapCount).toBe(1);
    expect(result.maxBuildingTextureDimension).toBe(2048);
    expect(result.shadowCasterCount).toBe(1);
    expect(result.instancedDetailMeshCount).toBe(1);
    expect(result.warnings).toEqual([]);
  });

  it('returns actionable warnings for a flat or incomplete street scene', () => {
    const scene = new THREE.Scene();
    const buildingRoot = new THREE.Group();
    buildingRoot.name = 'siteforge-direct3d-building';
    buildingRoot.add(new THREE.Mesh(
      new THREE.BoxGeometry(),
      new THREE.MeshBasicMaterial(),
    ));
    scene.add(buildingRoot);

    const result = inspectStreetRenderReadiness(scene);
    expect(result.warnings).toContain('Some building materials are not PBR-ready.');
    expect(result.warnings).toContain('The mounted buildings do not expose a base-colour texture.');
    expect(result.warnings).toContain('The mounted buildings do not expose normal-map detail.');
    expect(result.warnings).toContain('Authored geometry is not participating in the street shadow pass.');
    expect(result.warnings).toContain('No instanced vegetation or public-realm detail meshes were found.');
  });
});
