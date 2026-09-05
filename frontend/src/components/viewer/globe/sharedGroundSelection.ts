import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import type { SharedSiteGroundLayout } from './sharedSiteGround';

/** This camera selects terrain tiles; it never renders a view or supplies a
 * ground height. Its bounded footprint keeps the whole grid available when
 * the student's camera is at pedestrian level or facing away from the site. */
export function createGroundSelection(layout: SharedSiteGroundLayout, elevationHint: number) {
  const { west, south, stepLng, stepLat, columns, rows } = layout.grid;
  const lng = west + stepLng * (columns - 1) / 2;
  const lat = south + stepLat * (rows - 1) / 2;
  const width = stepLng * (columns - 1) * metersPerDegLon(lat);
  const depth = stepLat * (rows - 1) * METERS_PER_DEG_LAT;
  const height = Number.isFinite(elevationHint) ? elevationHint : 1500;
  const target = new THREE.Vector3(), normal = new THREE.Vector3(), north = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(lat * Math.PI / 180, lng * Math.PI / 180, height, target);
  WGS84_ELLIPSOID.getCartographicToNormal(lat * Math.PI / 180, lng * Math.PI / 180, normal);
  WGS84_ELLIPSOID.getCartographicToPosition(lat * Math.PI / 180 + 1e-5, lng * Math.PI / 180, height, north);
  const halfWidth = width / 2 + 5, halfDepth = depth / 2 + 5;
  const camera = new THREE.OrthographicCamera(-halfWidth, halfWidth, halfDepth, -halfDepth, 1, 4000);
  camera.name = 'site-ground-selection';
  camera.position.copy(target).addScaledVector(normal, 2000);
  camera.up.copy(north).sub(target).normalize();
  camera.lookAt(target); camera.updateMatrixWorld(true);
  const frustum = new THREE.Frustum().setFromProjectionMatrix(
    new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse));
  // No full-screen second renderer, no tiles for the entire neighbourhood.
  const resolution = [Math.min(1024, Math.max(128, Math.ceil(halfWidth * 16))),
    Math.min(1024, Math.max(128, Math.ceil(halfDepth * 16)))] as const;
  const bounds = new WeakMap<THREE.Object3D, THREE.Box3>();
  return { camera, resolution, intersects(scene: THREE.Object3D): boolean {
    let box = bounds.get(scene);
    if (!box) {
      scene.updateWorldMatrix(true, true);
      box = new THREE.Box3().setFromObject(scene);
      bounds.set(scene, box);
    }
    // Unknown bounds cannot prove irrelevance; preserve fail-closed resampling.
    return box.isEmpty() || frustum.intersectsBox(box);
  } };
}
