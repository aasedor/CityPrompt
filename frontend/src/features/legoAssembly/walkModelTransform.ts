import * as THREE from 'three';

const transforms = new WeakMap<THREE.Object3D, { world: THREE.Matrix4; inverse: THREE.Matrix4 }>();

/** Placement matrices are normally static while walking. Update ancestors so
 * edits are visible immediately, then invert only when the actual matrix changes.
 * No zone data is cached: even in-place metadata edits still get validated. */
export function walkModelLocal(object: THREE.Object3D, worldPoint: THREE.Vector3, target: THREE.Vector3): THREE.Vector3 {
  object.updateWorldMatrix(true, false);
  let cached = transforms.get(object);
  if (!cached) {
    cached = { world: object.matrixWorld.clone(), inverse: object.matrixWorld.clone().invert() };
    transforms.set(object, cached);
  } else if (!cached.world.equals(object.matrixWorld)) {
    cached.world.copy(object.matrixWorld);
    cached.inverse.copy(object.matrixWorld).invert();
  }
  return target.copy(worldPoint).applyMatrix4(cached.inverse);
}
