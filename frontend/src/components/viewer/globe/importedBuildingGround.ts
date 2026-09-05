import * as THREE from 'three';
import type { FootprintFrame, ModelPlacement } from './buildingPlacement';
import { placedNativeFootprints, type GroundPoint } from './buildingGroundContact';

/** The loaded model's transformed bounding footprint, not its larger parcel.
 * Mirrors recenter → uniform scale → Y-up swizzle → yaw → rectangle offset. */
export function importedModelGroundFootprints(
  bounds: THREE.Box3, placement: ModelPlacement | null, frame: FootprintFrame,
): GroundPoint[][] {
  if (!placement || bounds.isEmpty()) return [];
  const center = bounds.getCenter(new THREE.Vector3());
  const centered = bounds.clone().translate(new THREE.Vector3(-center.x, -bounds.min.y, -center.z));
  return placedNativeFootprints([{ bounds: centered, transform: {
    position: [0, 0, 0], scale: [placement.scale, placement.scale, placement.scale], rotationYRad: 0,
  } }], placement.yawRad, frame.rectCenterLocal);
}
