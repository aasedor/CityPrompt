import * as THREE from 'three';
import type { ZoningFaceRange } from '@/features/referenceLayers/zoningSurfaceGeometry';
import { getDirect3DInstanceDescriptor } from '@/components/viewer/globe/direct3dCapture';

/** A reference map must not consume clicks on the student's visible design.
 * Reuse the scene's zone identity, and raycast only owned, visible meshes on
 * click (never per frame). The prepared boundary is background, not a model.
 */
export function pickEditableZoneBeforePolicy(
  root: THREE.Object3D,
  ray: THREE.Raycaster,
  zones: ReadonlyArray<{ id: string; zone_type: string }>,
): string | null {
  const editableIds = new Set(zones.filter(zone => zone.zone_type !== 'site_boundary').map(zone => zone.id));
  let nearestId: string | null = null;
  let nearestDistance = Infinity;
  root.traverseVisible(object => {
    if (!(object as THREE.Mesh).isMesh) return;
    const id = getDirect3DInstanceDescriptor(object)?.zone_id;
    if (!id || !editableIds.has(id)) return;
    const hits = ray.intersectObject(object, false);
    const hit = hits[0];
    if (hit && hit.distance < nearestDistance) {
      nearestId = id;
      nearestDistance = hit.distance;
    }
  });
  return nearestId;
}

export function policyInspectionAllowed(state: {
  enabled: boolean; opacity: number; paused: boolean; drawing: boolean;
  placing: boolean; measuring: boolean; streetView: boolean; dragged: boolean;
}) {
  return state.enabled && state.opacity > 0 && !state.paused && !state.drawing
    && !state.placing && !state.measuring && !state.streetView && !state.dragged;
}

/** Raycast only the drawn cartographic surface, not the terrain/roofs beneath.
 * Native raycasting remains disabled for ground sampling and editing tools.
 */
export function pickPolicyMesh(mesh: THREE.Mesh, raycaster: THREE.Raycaster): string | null {
  for (let parent: THREE.Object3D | null = mesh; parent; parent = parent.parent) if (!parent.visible) return null;
  mesh.updateWorldMatrix(true, false);
  const intersections: THREE.Intersection[] = [];
  THREE.Mesh.prototype.raycast.call(mesh, raycaster, intersections);
  intersections.sort((a, b) => a.distance - b.distance);
  const face = intersections[0]?.faceIndex;
  if (face == null) return null;
  const ranges = mesh.geometry.userData.zoningFaceRanges as ZoningFaceRange[] | undefined;
  return ranges?.find(range => face >= range.firstFace && face < range.endFace)?.id ?? null;
}
