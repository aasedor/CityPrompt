import * as THREE from 'three';
import { DIRECT_3D_CAPTURE_EXCLUDE_KEY, DIRECT_3D_PROPOSAL_ROLE_KEY } from './direct3dCapture';
import { isWorldPointSpatiallyMasked } from './TileSpatialMaskPlugin';

/** Clear near-camera context by changing pitch, retaining the target, azimuth,
 * projection and slant range. This runs only during an explicit/initial frame;
 * it never removes context or takes ownership of an orbit/walking camera. */
export function findUnobstructedProjectFrame(
  camera: THREE.Camera, scene: THREE.Scene, target: THREE.Vector3, up: THREE.Vector3,
  projectSamples: readonly THREE.Vector3[] = [],
): THREE.Vector3 | null {
  if (!(camera instanceof THREE.PerspectiveCamera || camera instanceof THREE.OrthographicCamera)) return null;
  const offset = camera.position.clone().sub(target), distance = offset.length();
  if (!Number.isFinite(distance) || distance < 1) return null;
  const searchRadius = distance * 2 + Math.max(0, ...projectSamples.map(point => point.distanceTo(target)));
  const context: Array<{ mesh: THREE.Mesh; bounds: THREE.Box3 }> = [];
  scene.traverseVisible(object => {
    if (!(object as THREE.Mesh).isMesh) return;
    let existing = false;
    for (let parent: THREE.Object3D | null = object; parent; parent = parent.parent) {
      if (parent.userData[DIRECT_3D_PROPOSAL_ROLE_KEY] || parent.userData[DIRECT_3D_CAPTURE_EXCLUDE_KEY]
        || parent.userData.sceneRole === 'proposal') return;
      existing ||= parent.userData.sceneRole === 'existing';
    }
    if (existing) {
      const mesh = object as THREE.Mesh;
      if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
      const bounds = mesh.geometry.boundingBox!.clone().applyMatrix4(mesh.matrixWorld);
      if (bounds.distanceToPoint(target) <= searchRadius) context.push({ mesh, bounds });
    }
  });
  if (!context.length) return null;
  const normal = up.clone().normalize();
  const vertical = offset.dot(normal), horizontal = offset.clone().addScaledVector(normal, -vertical);
  if (horizontal.lengthSq() < 1e-6 || vertical <= 0) return null;
  horizontal.normalize();
  const preview = camera.clone(), ray = new THREE.Raycaster();
  const boxHit = new THREE.Vector3();
  const rayBlocked = () => {
    // Test cheap cached world boxes first. Narrow-phase only the intersected
    // foreground meshes, nearest first, and stop at the first visible hit.
    const candidates = context.flatMap(entry => {
      const point = ray.ray.intersectBox(entry.bounds, boxHit);
      if (!point) return [];
      const distance = entry.bounds.containsPoint(ray.ray.origin) ? 0 : point.distanceTo(ray.ray.origin);
      return distance <= ray.far ? [{ ...entry, distance }] : [];
    }).sort((a, b) => a.distance - b.distance);
    for (const { mesh } of candidates) {
      if (ray.intersectObject(mesh, false).some(hit => {
        const material = Array.isArray(mesh.material) ? mesh.material[hit.face?.materialIndex ?? 0] : mesh.material;
        return material?.visible && (!material.transparent || material.opacity > .01)
          && !isWorldPointSpatiallyMasked(material, hit.point);
      })) return true;
    }
    return false;
  };
  const blocked = (position: THREE.Vector3) => {
    preview.position.copy(position); preview.up.copy(normal); preview.lookAt(target); preview.updateMatrixWorld(true);
    if (projectSamples.length) {
      // Trace the real ground/roof footprint, including its near edge below
      // the optical centre. A clear centre ray alone can still hide a park.
      for (const sample of projectSamples) {
        ray.set(position, sample.clone().sub(position).normalize());
        ray.near = camera instanceof THREE.PerspectiveCamera ? camera.near : 0;
        ray.far = position.distanceTo(sample) - 1;
        if (ray.far > ray.near && rayBlocked()) return true;
      }
      return false;
    }
    // Only foreground context can engulf this camera. Source tiles near the
    // framed target are owned by its prepared-site mask and must not push it.
    for (const x of [-.7, -.3, 0, .3, .7]) {
      ray.setFromCamera(new THREE.Vector2(x, 0), preview);
      ray.near = camera instanceof THREE.PerspectiveCamera ? camera.near : 0;
      ray.far = distance * .75;
      if (rayBlocked()) return true;
    }
    return false;
  };
  if (!blocked(camera.position)) return null;
  const pitch = Math.acos(THREE.MathUtils.clamp(vertical / distance, -1, 1));
  for (let step = 1; step <= 18; step++) {
    const nextPitch = Math.max(0, pitch - step * Math.PI / 36);
    const position = target.clone().addScaledVector(normal, distance * Math.cos(nextPitch))
      .addScaledVector(horizontal, distance * Math.sin(nextPitch));
    if (!blocked(position)) return position;
    if (nextPitch === 0) break;
  }
  return null;
}
