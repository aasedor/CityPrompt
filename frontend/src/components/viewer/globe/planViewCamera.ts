import * as THREE from 'three';

// Narrow-lens plan mode retains the globe renderer's perspective camera.
// Moving back by the corresponding lens ratio preserves the ground extent.
// This reduces roof parallax; it is not a surveyed orthographic plan.
export const PLAN_VIEW_FOV_DEGREES = 1;
export const WORKING_VIEW_FOV_DEGREES = 75;

export function distanceForFieldOfView(distance: number, fromFov: number, toFov: number): number {
  return distance * Math.tan(THREE.MathUtils.degToRad(fromFov) / 2)
    / Math.tan(THREE.MathUtils.degToRad(toFov) / 2);
}

export function syncPlanCameraClipping(camera: THREE.Camera, distance: number): void {
  if (!(camera instanceof THREE.PerspectiveCamera) || camera.fov !== PLAN_VIEW_FOV_DEGREES) return;
  // The distant lens needs a farther near plane to retain depth precision for
  // paving and junction surfaces separated by just a few centimetres.
  const near = Math.max(1, distance / 4);
  if (Math.abs(camera.near - near) > .01) {
    camera.near = near;
    camera.updateProjectionMatrix();
  }
}

export function setWorkingCameraProjection(camera: THREE.Camera, plan: boolean, distance = 20): void {
  if (!(camera instanceof THREE.PerspectiveCamera)) return;
  camera.fov = plan ? PLAN_VIEW_FOV_DEGREES : WORKING_VIEW_FOV_DEGREES;
  camera.near = plan ? Math.max(1, distance / 4) : 1;
  camera.updateProjectionMatrix();
}

const originalPlanFog = new WeakMap<THREE.Fog, { near: number; far: number }>();

export function syncPlanCameraFog(camera: THREE.Camera, fog: THREE.Fog | THREE.FogExp2 | null): void {
  if (!(fog instanceof THREE.Fog)) return;
  const original = originalPlanFog.get(fog);
  if (camera instanceof THREE.PerspectiveCamera && camera.fov === PLAN_VIEW_FOV_DEGREES) {
    const base = original ?? { near: fog.near, far: fog.far };
    if (!original) originalPlanFog.set(fog, base);
    const ratio = distanceForFieldOfView(1, WORKING_VIEW_FOV_DEGREES, PLAN_VIEW_FOV_DEGREES);
    fog.near = base.near * ratio;
    fog.far = base.far * ratio;
  } else if (original) {
    fog.near = original.near;
    fog.far = original.far;
    originalPlanFog.delete(fog);
  }
}
