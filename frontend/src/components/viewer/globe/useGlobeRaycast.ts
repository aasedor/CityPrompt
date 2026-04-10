/**
 * useGlobeRaycast.ts — Raycast from screen coordinates to globe surface.
 *
 * Primary: intersect WGS84 ellipsoid (O(1), always works)
 * Optional: intersect 3D tile meshes (expensive but terrain-accurate)
 */

import { useCallback, useRef } from 'react';
import * as THREE from 'three';
import { useThree } from '@react-three/fiber';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';

const RAD_TO_DEG = 180 / Math.PI;

export function useGlobeRaycast() {
  const { camera, gl } = useThree();
  const raycasterRef = useRef(new THREE.Raycaster());
  const ndcRef = useRef(new THREE.Vector2());
  const hitRef = useRef(new THREE.Vector3());

  /**
   * Raycast from a mouse/pointer event to get [lng, lat] on the globe.
   * Returns null if the ray misses the globe entirely.
   */
  const raycastToLatLng = useCallback((event: MouseEvent | PointerEvent | React.MouseEvent): [number, number] | null => {
    const rect = gl.domElement.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    ndcRef.current.set(x, y);
    raycasterRef.current.setFromCamera(ndcRef.current, camera);

    // Intersect with WGS84 ellipsoid (fast, O(1))
    const hit = WGS84_ELLIPSOID.intersectRay(raycasterRef.current.ray, hitRef.current);
    if (!hit) return null;

    const cartographic = WGS84_ELLIPSOID.getPositionToCartographic(hit, {} as any);
    return [cartographic.lon * RAD_TO_DEG, cartographic.lat * RAD_TO_DEG];
  }, [camera, gl]);

  /**
   * Raycast against specific Three.js objects (e.g., zone meshes).
   * Returns the first intersection with userData.
   */
  const raycastToObjects = useCallback((
    event: MouseEvent | PointerEvent | React.MouseEvent,
    objects: THREE.Object3D[],
  ): { point: THREE.Vector3; object: THREE.Object3D; zoneId?: string } | null => {
    const rect = gl.domElement.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    ndcRef.current.set(x, y);
    raycasterRef.current.setFromCamera(ndcRef.current, camera);

    const intersections = raycasterRef.current.intersectObjects(objects, true);
    if (intersections.length === 0) return null;

    const hit = intersections[0];
    // Walk up parent chain to find userData.zoneId
    let obj: THREE.Object3D | null = hit.object;
    while (obj) {
      if (obj.userData?.zoneId) {
        return { point: hit.point, object: obj, zoneId: obj.userData.zoneId };
      }
      obj = obj.parent;
    }
    return { point: hit.point, object: hit.object };
  }, [camera, gl]);

  /**
   * Project a [lng, lat] to screen pixels.
   */
  const projectToScreen = useCallback((lngLat: [number, number]): { x: number; y: number } | null => {
    const DEG_TO_RAD = Math.PI / 180;
    const pos = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToPosition(
      lngLat[1] * DEG_TO_RAD,
      lngLat[0] * DEG_TO_RAD,
      0,
      pos,
    );

    pos.project(camera);

    // Check if behind camera
    if (pos.z > 1) return null;

    const rect = gl.domElement.getBoundingClientRect();
    return {
      x: (pos.x + 1) / 2 * rect.width,
      y: (1 - pos.y) / 2 * rect.height,
    };
  }, [camera, gl]);

  return { raycastToLatLng, raycastToObjects, projectToScreen };
}
