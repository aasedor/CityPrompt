import * as THREE from 'three';
import type { ZoningFaceRange } from '@/features/referenceLayers/zoningSurfaceGeometry';

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
