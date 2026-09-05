import * as THREE from 'three';
import type { LegoAssemblyPlan } from './legoAssemblyApi';

export function isNativeClayPlan(plan: { fit?: LegoAssemblyPlan['fit'] | null }): boolean {
  return plan.fit?.native_scale_locked === true && plan.fit.delivery_format === 'architectural_clay';
}

/** Seat an owned clone using its measured geometry. The wrapper takes the
 * planned transform; the cached GLB, its vertices and its native scale remain
 * untouched. Clay sources need not have a centred modelling origin. */
export function centreNativeClayClone(clone: THREE.Object3D): THREE.Group {
  clone.updateMatrixWorld(true);
  const bounds = new THREE.Box3().setFromObject(clone, true);
  const wrapper = new THREE.Group();
  wrapper.name = 'native-clay-placement';
  wrapper.add(clone);
  if (!bounds.isEmpty()) {
    clone.position.sub(new THREE.Vector3(
      (bounds.min.x + bounds.max.x) / 2,
      bounds.min.y,
      (bounds.min.z + bounds.max.z) / 2,
    ));
    clone.updateMatrix();
  }
  wrapper.updateMatrixWorld(true);
  return wrapper;
}
