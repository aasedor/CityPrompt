import * as THREE from 'three';
import { PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS } from './publicRealmDepthPolicy';
import { drapeSharedGroundGeometry, type SharedGroundTriangulation } from './sharedGroundGeometry';

/** The small external arrival strip joins the authored pedestrian band to the
 * park drape. Ground offsets come from the same terrain frame as the park kit. */
export function buildParkAccessBridgeGeometry(input: {
  start: [number, number]; end: [number, number]; widthM: number;
  streetLiftM: number; startGroundM?: number; endGroundM?: number;
  /** Same shared surface as the road and park, in this local metre frame. */
  groundAt?: (x: number, y: number) => number | null;
  groundGrid?: SharedGroundTriangulation;
}): THREE.BufferGeometry | null {
  const { start, end, widthM, streetLiftM, startGroundM = 0, endGroundM = 0 } = input;
  const dx = end[0] - start[0]; const dy = end[1] - start[1]; const length = Math.hypot(dx, dy);
  if (!Number.isFinite(length) || length < 0.01 || !Number.isFinite(widthM) || widthM <= 0) return null;
  const nx = -dy / length * widthM / 2; const ny = dx / length * widthM / 2;
  const geometry = new THREE.BufferGeometry();
  const startOffset = input.groundAt ? 0 : startGroundM, endOffset = input.groundAt ? 0 : endGroundM;
  geometry.setAttribute('position', new THREE.Float32BufferAttribute([
    start[0] - nx, start[1] - ny, startOffset + streetLiftM + 0.003,
    start[0] + nx, start[1] + ny, startOffset + streetLiftM + 0.003,
    end[0] - nx, end[1] - ny, endOffset + PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS + 0.003,
    end[0] + nx, end[1] + ny, endOffset + PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS + 0.003,
  ], 3));
  geometry.setIndex([0, 2, 1, 1, 2, 3]);
  geometry.computeVertexNormals();
  if (input.groundAt) {
    const draped = drapeSharedGroundGeometry(geometry, input.groundAt, 4, 60000, input.groundGrid);
    geometry.dispose(); return draped;
  }
  return geometry;
}
