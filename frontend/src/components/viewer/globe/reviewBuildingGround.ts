import * as THREE from 'three';
import { placedNativeFootprints, resolveBuildingGroundContact, type GroundPoint } from './buildingGroundContact';
import type { SharedSiteGroundState } from './SharedSiteGroundProvider';

/** Match centreNativeClayClone and its Y-up → ENU wrapper without changing
 * the cached source, its native dimensions or its modelling origin. The full
 * fixed review plot is occupied, including its paving and landscape. */
export function reviewBuildingFootprints(source: THREE.Object3D, yaw: number): GroundPoint[][] {
  source.updateMatrixWorld(true);
  const bounds = new THREE.Box3().setFromObject(source, true);
  if (bounds.isEmpty() || !Number.isFinite(yaw)
    || ![...bounds.min.toArray(), ...bounds.max.toArray()].every(Number.isFinite)) return [];
  const size = bounds.getSize(new THREE.Vector3());
  if (size.x <= 0 || size.z <= 0) return [];
  const centred = new THREE.Box3(new THREE.Vector3(-size.x / 2, 0, -size.z / 2),
    new THREE.Vector3(size.x / 2, size.y, size.z / 2));
  return placedNativeFootprints([{ bounds: centred,
    transform: { position: [0, 0, 0], scale: [1, 1, 1], rotationYRad: 0 } }], yaw, [0, 0]);
}

export function reviewBuildingGroundContact(footprints: GroundPoint[][], lng: number, lat: number,
  ground: SharedSiteGroundState) {
  // A display draft or an invalidated snapshot cannot authorize walking or
  // clear the shared capture guard, even if its previous heights still exist.
  const current = !ground.preview && (ground.isCurrent?.() ?? true);
  return resolveBuildingGroundContact(footprints, lng, lat,
    current ? ground : { ...ground, status: 'sampling' });
}
