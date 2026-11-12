import * as THREE from 'three';
import type { LegoAssemblyPlan } from './legoAssemblyApi';

export function isNativeClayPlan(plan: { fit?: LegoAssemblyPlan['fit'] | null }): boolean {
  // Complete authored height choices can use the module delivery format too.
  // The planner marks only whole select-and-place assemblies as native locked;
  // repeated floor stacks retain their common source frame and remain uncentred.
  return (plan.fit?.native_scale_locked === true || isResizeTrialPlan(plan)) && isArchitecturalClayPlan(plan);
}

/** Building resize pilot: the exact clay source stretched in width and depth.
 * It is seated, grounded and picked like the native model; only its plan
 * transform carries the stretch. The server alone can produce this marker. */
export function isResizeTrialPlan(plan: { fit?: LegoAssemblyPlan['fit'] | null }): boolean {
  const trial = plan.fit?.resize_trial;
  return plan.fit?.assembly_mode === 'fixed_landmark' && trial?.vertical_scale === 1
    && Number.isFinite(trial.width_scale) && Number.isFinite(trial.depth_scale);
}

export function isArchitecturalClayPlan(plan: { fit?: LegoAssemblyPlan['fit'] | null }): boolean {
  return plan.fit?.delivery_format === 'architectural_clay'
    || plan.fit?.delivery_format === 'architectural_clay_module_v1';
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
