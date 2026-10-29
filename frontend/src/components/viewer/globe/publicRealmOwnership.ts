import * as THREE from 'three';
import { prepareBuildingOnlyScene, prepareOwnedNativeScene, type NativeSceneOwnershipContract } from '@/features/legoAssembly/buildingOnlyScene';
import type { PublicRealmReleaseFixture } from '@/features/pickPlace/publicRealmRelease';
import { publicRealmReleaseRow } from '@/features/pickPlace/publicRealmRelease';
import { publicRealmOwnership } from '@/features/pickPlace/publicRealmOwnershipContract';
export { publicRealmOwnership } from '@/features/pickPlace/publicRealmOwnershipContract';

interface ContextSupport {
  name: string; polygon: number[][]; bottom: number; top: number; material: string;
}

export function preparePublicRealmOwnedScene(source: THREE.Object3D, fixture: PublicRealmReleaseFixture) {
  const contract = publicRealmOwnership(fixture) as unknown as
    (NativeSceneOwnershipContract & { contextSupports?: ContextSupport[] }) | undefined;
  const result = prepareOwnedNativeScene(source, contract);
  for (const support of contract?.contextSupports ?? []) {
    let material: THREE.Material | undefined;
    source.traverse(object => {
      const mesh = object as THREE.Mesh;
      if (mesh.isMesh) material ??= (Array.isArray(mesh.material) ? mesh.material : [mesh.material])
        .find(value => value.name === support.material);
    });
    if (!material) throw new Error('The compact crossing support material is unavailable.');
    // Source bank footprints are in Blender XY; extrude the bounded, closed
    // bank solid in native metres and convert once to glTF Y-up. Original
    // cached geometry and GLB bytes stay unchanged. These are explicit runtime
    // adaptations, separately bound by the saved ownership revision.
    const shape = new THREE.Shape(support.polygon.map(point => new THREE.Vector2(point[0], point[1])));
    const geometry = new THREE.ExtrudeGeometry(shape, { depth: support.top - support.bottom,
      bevelEnabled: false, steps: 1, curveSegments: 1 });
    geometry.rotateX(-Math.PI / 2).translate(0, support.bottom, 0);
    geometry.applyMatrix4(result.clone.matrixWorld.clone().invert());
    const mesh = new THREE.Mesh(geometry, material);
    mesh.name = `runtime-context-${support.name}`;
    mesh.userData.runtimeContextAdaptation = true;
    result.clone.add(mesh); result.ownedGeometries.push(geometry);
  }
  return result;
}

/** Hover preview and placed objects must display the same retained geometry. */
export function prepareNativePlacementScene(source: THREE.Object3D, url: string, assetId?: string) {
  const row = publicRealmReleaseRow(assetId);
  return row?.fixture.url === url ? preparePublicRealmOwnedScene(source, row.fixture)
    : prepareBuildingOnlyScene(source, url);
}
