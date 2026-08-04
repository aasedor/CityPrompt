import * as THREE from 'three';

import type { NormalizedVideoRoutePoint } from '../videoRouteControls';
import { normalizedVideoPointToNdc } from '../videoRouteControls';

export const STREET_RENDER_EYE_HEIGHT_METERS = 1.7;
export const STREET_RENDER_LENS_FOCAL_LENGTH_MM = 35;
export const STREET_RENDER_SENSOR_WIDTH_MM = 36;
export const STREET_RENDER_FRAME_ASPECT = 16 / 9;
export const STREET_RENDER_MAX_ROUTE_DISTANCE_METERS = 80;

/** Three.js PerspectiveCamera.fov is vertical, while photographic 35 mm lens
 * descriptions conventionally refer to a 36 mm-wide full-frame sensor. */
export function verticalFovForHorizontalSensor(
  focalLengthMm: number,
  frameAspect: number,
  sensorWidthMm = STREET_RENDER_SENSOR_WIDTH_MM,
): number {
  if (!(focalLengthMm > 0) || !(frameAspect > 0) || !(sensorWidthMm > 0)) {
    throw new Error('Street-render lens dimensions must be positive.');
  }
  const sensorHeightMm = sensorWidthMm / frameAspect;
  return THREE.MathUtils.radToDeg(2 * Math.atan(sensorHeightMm / (2 * focalLengthMm)));
}

export const STREET_RENDER_VERTICAL_FOV_DEGREES = verticalFovForHorizontalSensor(
  STREET_RENDER_LENS_FOCAL_LENGTH_MM,
  STREET_RENDER_FRAME_ASPECT,
);

export interface StreetCameraProjectionState {
  fov: number;
  near: number;
}

/** Apply the deterministic architectural-photography lens used by still and
 * route capture. Returns the exact projection state required for restoration. */
export function applyStreetCameraProjection(
  camera: THREE.Camera,
): StreetCameraProjectionState | null {
  if (!(camera instanceof THREE.PerspectiveCamera)) return null;
  const previous = { fov: camera.fov, near: camera.near };
  camera.fov = STREET_RENDER_VERTICAL_FOV_DEGREES;
  camera.near = Math.min(camera.near, 0.1);
  camera.updateProjectionMatrix();
  return previous;
}

export function restoreStreetCameraProjection(
  camera: THREE.Camera,
  previous: StreetCameraProjectionState | null,
): void {
  if (!(camera instanceof THREE.PerspectiveCamera) || !previous) return;
  camera.fov = previous.fov;
  camera.near = previous.near;
  camera.updateProjectionMatrix();
}

/**
 * Convert a route drawn over the 16:9 street preview into a metric route on
 * the pedestrian's local ground plane. Google meshes are intentionally not
 * raycast: a facade, car or photogrammetry spike must never become the path.
 */
export function projectStreetRouteToGround(
  camera: THREE.Camera,
  routePoints: NormalizedVideoRoutePoint[],
  sourceAspect: number,
  upDirection: THREE.Vector3,
  {
    eyeHeightMeters = STREET_RENDER_EYE_HEIGHT_METERS,
    maxDistanceMeters = STREET_RENDER_MAX_ROUTE_DISTANCE_METERS,
  }: {
    eyeHeightMeters?: number;
    maxDistanceMeters?: number;
  } = {},
): THREE.Vector3[] {
  if (routePoints.length < 2) throw new Error('A street route needs a start and finish.');
  const up = upDirection.clone().normalize();
  if (up.lengthSq() < 0.99) throw new Error('The street camera does not have a valid up direction.');

  const groundOrigin = camera.position.clone().addScaledVector(up, -eyeHeightMeters);
  const groundPlane = new THREE.Plane().setFromNormalAndCoplanarPoint(up, groundOrigin);
  const raycaster = new THREE.Raycaster();

  const projected = routePoints.map((point) => {
    const ndc = normalizedVideoPointToNdc(point, sourceAspect);
    raycaster.setFromCamera(new THREE.Vector2(ndc.x, ndc.y), camera);
    const hit = raycaster.ray.intersectPlane(groundPlane, new THREE.Vector3());
    if (!hit || raycaster.ray.direction.dot(up) >= -1e-4) {
      throw new Error('Draw the street route over visible ground below the horizon.');
    }
    const distance = hit.distanceTo(groundOrigin);
    if (!Number.isFinite(distance) || distance > maxDistanceMeters) {
      throw new Error(`Keep the street route within ${Math.round(maxDistanceMeters)} metres of the camera.`);
    }
    return hit;
  });

  const routeLength = projected.slice(1).reduce(
    (total, point, index) => total + point.distanceTo(projected[index]),
    0,
  );
  if (routeLength < 0.75) throw new Error('Draw a longer street route before preparing the video.');
  return projected;
}

/** Apply one fixed-timestep pedestrian pose. The camera follows the route
 * tangent, stays at a constant metric eye height, and never inherits a globe
 * orbit offset. */
export function applyStreetRoutePose(
  camera: THREE.Camera,
  pathCurve: THREE.CatmullRomCurve3,
  progress: number,
  upDirection: THREE.Vector3,
  eyeHeightMeters = STREET_RENDER_EYE_HEIGHT_METERS,
  lookTarget?: THREE.Vector3,
): void {
  const clamped = THREE.MathUtils.clamp(progress, 0, 1);
  const up = upDirection.clone().normalize();
  const groundPoint = pathCurve.getPointAt(clamped);
  const tangent = pathCurve.getTangentAt(clamped).projectOnPlane(up).normalize();
  if (tangent.lengthSq() < 1e-6) throw new Error('The street route has no usable travel direction.');

  camera.position.copy(groundPoint).addScaledVector(up, eyeHeightMeters);
  camera.up.copy(up);
  camera.lookAt(lookTarget ?? camera.position.clone().addScaledVector(tangent, 25));
  camera.updateMatrixWorld(true);
}
