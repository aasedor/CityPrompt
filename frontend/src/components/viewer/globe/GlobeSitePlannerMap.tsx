/**
 * GlobeSitePlannerMap.tsx â€” Google Earth-style 3D globe with SiteForge tools.
 *
 * Full-screen globe with drawing handled at the DOM level (not inside R3F).
 * GlobeControls always enabled â€” drawing uses click vs drag detection.
 */

import { useContext, useEffect, useRef, useState, useCallback, useMemo } from 'react';
import * as THREE from 'three';
import { Canvas, useThree } from '@react-three/fiber';
import {
  TilesRenderer,
  TilesPlugin,
  GlobeControls,
  TilesAttributionOverlay,
  EastNorthUpFrame,
  TilesRendererContext,
} from '3d-tiles-renderer/r3f';
import {
  GoogleCloudAuthPlugin,
  TileCompressionPlugin,
  UpdateOnChangePlugin,
  UnloadTilesPlugin,
  TilesFadePlugin,
  GLTFExtensionsPlugin,
} from '3d-tiles-renderer/plugins';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { Ellipsoid, WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { Environment, Html } from '@react-three/drei';
import type { Building, SiteZone, SiteZoneType, SiteZoneProperties } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { useViewerStore } from '@/store';
import { GlobeZoneLayer } from './GlobeZoneLayer';
import { GlobeBuildingModelsLayer } from './GlobeBuildingModelsLayer';
import { GlobeLegoAssemblyLayer } from './GlobeLegoAssemblyLayer';
import { excludeLegoStackBuildings, hasLegoRecipe, hasPlannedMassing } from './legoGlobePlacement';
import { GlobeStreetDetailLayer } from './GlobeStreetDetailLayer';
import { GlobeParkKitLayer } from './GlobeParkKitLayer';
import { GlobeResidualLandscapeLayer } from './GlobeResidualLandscapeLayer';
import { getResidualLandscapeRecipe } from './residualLandscape';
import { GlobeEditMode } from './GlobeEditMode';
import { useCreateGlobeDragRef, GlobeDragProvider } from './useGlobeDragRef';
import { GlobePegman } from './GlobePegman';
import { SceneSettledMonitor } from './useSceneSettled';
import {
  type SceneTileRenderer,
  waitForTilesSettled,
} from './tileLoadReadiness';
import {
  estimateProjectFrameHeight,
  PROJECT_FRAME_MAX_HEIGHT_M,
  PROJECT_FRAME_MIN_HEIGHT_M,
  PROJECT_FRAME_TARGET_FRACTION,
} from './projectFrameHeight';
import { TileStencilPatcher } from './TileStencilPatcher';
import { GlobeTileMaskLayer } from './GlobeTileMaskLayer';
import {
  getPreparedSiteBoundaryIds,
  shouldMaskReplacementBuildingTiles,
} from './sitePreparationSurface';
import {
  getCurrentCommunity3DBuildingIds,
  isCommunity3DCompiled,
  shouldMaskCommunityGroundTiles,
} from '@/features/community3d/community3d';
import { useCleanPresentationAfterCommunity3DCompile } from '@/features/community3d/community3dPresentation';
import { getCameraElevationBadge, pitchFromNadirToCameraElevation } from '../cameraAngles';
import {
  getObjectFilteredTerrainHeight,
  getRepresentativeTerrainHeight,
  shouldFilterObjectTerrainHeight,
} from './globeTerrainUtils';
import {
  getToolDisplayLabel,
  isLinearTool,
  minPointsForTool,
  smoothPolyline,
  bufferLineToPolygon,
  computeCentroid,
  haversineDistance,
  geodesicArea,
  polygonAreaM2,
  polylineLength,
  formatDistance,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from '../mapEngine/geoUtils';
import { isWithinPolygonCloseRadius, normalizePolygonDrawing } from './drawingGeometry';
import booleanPointInPolygon from '@turf/boolean-point-in-polygon';
import { polygon as turfPolygon, point as turfPoint } from '@turf/helpers';
import {
  captureDirect3DScene,
  Direct3DCaptureError,
  DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA,
  direct3DInstanceUserData,
  direct3DProposalUserData,
  direct3DZoneInstanceDescriptor,
  type Direct3DCaptureBundle,
} from './direct3dCapture';

import { elevationApi } from '@/services/api';

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
const DEG_TO_RAD = Math.PI / 180;
const RAD_TO_DEG = 180 / Math.PI;

// Default fallback elevation (Calgary) â€” used until dynamic fetch completes
const DEFAULT_TERRAIN_ELEVATION = 1045;
const DEFAULT_INITIAL_CAMERA_HEIGHT_ABOVE_GROUND = 120;
const MIN_INITIAL_CAMERA_HEIGHT_ABOVE_GROUND = DEFAULT_INITIAL_CAMERA_HEIGHT_ABOVE_GROUND;
const MAX_INITIAL_CAMERA_HEIGHT_ABOVE_GROUND = 1800;
const MAX_VIEWPORT_CAMERA_HEIGHT_ABOVE_GROUND = 40000;
const INITIAL_CAMERA_REVEAL_FALLBACK_MS = 2500;

function isBuildingZoneType(zoneType: SiteZoneType | string | null | undefined): boolean {
  return zoneType === 'building' || zoneType === 'residential' || zoneType === 'development_area';
}

function rotateCoordsAroundCentroid(coords: number[][], centroid: [number, number], deltaRad: number): number[][] {
  const cos = Math.cos(deltaRad);
  const sin = Math.sin(deltaRad);
  const [cx, cy] = centroid;
  return coords.map((c) => {
    const rx = c[0] - cx;
    const ry = c[1] - cy;
    return [cx + rx * cos - ry * sin, cy + rx * sin + ry * cos];
  });
}
export const DEFAULT_INITIAL_CAMERA_PITCH_DEGREES = 60;
export const MAX_GLOBE_CAMERA_PITCH_DEGREES = 100;
const ZONE_FIT_INITIAL_CAMERA_MULTIPLIER = 1.15;
const VIEWPORT_FIT_INITIAL_CAMERA_MULTIPLIER = 2;
const DRAWING_FILL_LIFT_METERS = 0.3;
const DRAWING_OUTLINE_LIFT_METERS = 0.6;
const GLOBE_SCENE_HTML_Z_INDEX_RANGE: [number, number] = [1, 0];
const DRAWING_VERTEX_LIFT_METERS = 1;
const DRAWING_VERTEX_RADIUS_METERS = 2.25;
const OBJECT_FILTER_SAMPLE_RADIUS_METERS = 8;
const MEASURE_LINE_LIFT_METERS = 2;
const MEASURE_POINT_RADIUS_METERS = 1.8;
const GLOBE_NAV_MIN_HEIGHT_ABOVE_GROUND = 20;
const GLOBE_NAV_HORIZONTAL_SPEED_FACTOR = 0.02;
const GLOBE_NAV_VERTICAL_SPEED_FACTOR = 0.02;
const GLOBE_NAV_MIN_STEP_METERS = 2;
const GLOBE_NAV_MAX_STEP_METERS = 120;
export const SELECTED_ZONE_KEYBOARD_NUDGE_DELTA = 0.00005; // ~5m in latitude degrees
const WHEEL_DELTA_MODE_PIXEL = 0;
const TRACKPAD_WHEEL_DELTA_THRESHOLD_PX = 50;
const TRACKPAD_ZOOM_MULTIPLIER = 4;
const GLOBE_CONTROLS_WHEEL_ZOOM_SCALE = 0.25;
const MOBILE_DRAWING_MEDIA_QUERY = '(max-width: 639px)';

interface TrackpadZoomControls {
  enabled?: boolean;
  needsUpdate?: boolean;
  zoomDelta?: number;
  pointerTracker?: {
    setHoverEvent?: (event: WheelEvent) => void;
    updatePointer?: (event: WheelEvent) => void;
  };
}

function isLikelyTrackpadWheel(event: WheelEvent): boolean {
  const absY = Math.abs(event.deltaY);
  return event.deltaMode === WHEEL_DELTA_MODE_PIXEL
    && absY > 0
    && absY < TRACKPAD_WHEEL_DELTA_THRESHOLD_PX;
}

function applyTrackpadZoom(event: WheelEvent, controls: TrackpadZoomControls | null): boolean {
  const zoomDelta = controls?.zoomDelta;
  if (!controls?.enabled || typeof zoomDelta !== 'number' || !isLikelyTrackpadWheel(event)) return false;

  controls.pointerTracker?.setHoverEvent?.(event);
  controls.pointerTracker?.updatePointer?.(event);
  controls.zoomDelta = zoomDelta - GLOBE_CONTROLS_WHEEL_ZOOM_SCALE * event.deltaY * TRACKPAD_ZOOM_MULTIPLIER;
  controls.needsUpdate = true;
  return true;
}

function isMobileDrawingViewport(): boolean {
  return typeof window !== 'undefined' && window.matchMedia(MOBILE_DRAWING_MEDIA_QUERY).matches;
}

function formatDrawingArea(squareMeters: number): string {
  return `${Math.round(squareMeters).toLocaleString()} m²`;
}

/** Create a terrain-adjusted ellipsoid for accurate raycasting at a given elevation */
function createTerrainEllipsoid(elevation: number): Ellipsoid {
  return new Ellipsoid(
    6378137.0 + elevation,
    6378137.0 + elevation,
    6356752.3142 + elevation,
  );
}

export function buildZoneCreateProperties(
  tool: SiteZoneType,
  properties: SiteZoneProperties | null | undefined,
  terrainElevation: number,
): SiteZoneProperties {
  return {
    ...ZONE_TYPE_CONFIG[tool].defaultProperties,
    ...(properties ?? {}),
    terrain_elevation_m: terrainElevation,
  };
}

export function shouldMirrorCtrlPointerAsShift(
  event: Pick<PointerEvent, 'button' | 'ctrlKey' | 'shiftKey'>,
): boolean {
  return event.button === 0 && event.ctrlKey && !event.shiftKey;
}

export function getGlobeNavigationMovement(keysDown: ReadonlySet<string>) {
  let forward = 0;
  let strafe = 0;

  if (keysDown.has('w') || keysDown.has('arrowup')) forward += 1;
  if (keysDown.has('s') || keysDown.has('arrowdown')) forward -= 1;
  if (keysDown.has('d') || keysDown.has('arrowright')) strafe += 1;
  if (keysDown.has('a') || keysDown.has('arrowleft')) strafe -= 1;

  return { forward, strafe, vertical: 0 };
}

function hasFiniteQuaternion(camera: THREE.Camera | null | undefined): camera is THREE.Camera & { quaternion: THREE.Quaternion } {
  const quaternion = camera?.quaternion as Partial<THREE.Quaternion> | undefined;
  return !!quaternion && [quaternion.x, quaternion.y, quaternion.z, quaternion.w].every(Number.isFinite);
}

function hasFiniteVector3(vector: Partial<THREE.Vector3> | null | undefined): vector is THREE.Vector3 {
  return !!vector && [vector.x, vector.y, vector.z].every(Number.isFinite);
}

function pointToCartographic(
  point: THREE.Vector3,
  fallbackEllipsoid: Ellipsoid,
): { lon: number; lat: number } {
  const ellipsoidWithCartographic = WGS84_ELLIPSOID as Ellipsoid & {
    getPositionToCartographic?: (point: THREE.Vector3, target: unknown) => { lon: number; lat: number };
  };
  const cartographicSource = typeof ellipsoidWithCartographic.getPositionToCartographic === 'function'
    ? ellipsoidWithCartographic
    : fallbackEllipsoid;
  return cartographicSource.getPositionToCartographic(point, {} as never);
}

function normalizeBearing(bearing: number): number {
  return ((bearing + 180) % 360 + 360) % 360 - 180;
}

function projectOntoTangentPlane(
  vector: THREE.Vector3,
  normal: THREE.Vector3,
  fallback: THREE.Vector3,
) {
  const tangent = vector.clone().addScaledVector(normal, -vector.dot(normal));
  if (tangent.lengthSq() < 1e-10) {
    return fallback.clone();
  }
  return tangent.normalize();
}

function decomposeOnBasis(
  vector: THREE.Vector3,
  east: THREE.Vector3,
  north: THREE.Vector3,
  up: THREE.Vector3,
) {
  return {
    east: vector.dot(east),
    north: vector.dot(north),
    up: vector.dot(up),
  };
}

function composeFromBasis(
  basis: { east: number; north: number; up: number },
  east: THREE.Vector3,
  north: THREE.Vector3,
  up: THREE.Vector3,
) {
  return new THREE.Vector3()
    .addScaledVector(east, basis.east)
    .addScaledVector(north, basis.north)
    .addScaledVector(up, basis.up);
}

export function translateGlobeCamera(
  camera: THREE.Camera,
  controls: { pivotPoint?: THREE.Vector3; update?: () => void } | null | undefined,
  terrainEllipsoid: Ellipsoid,
  movement: {
    forward: number;
    strafe: number;
    vertical: number;
  },
) {
  const pivotPoint = controls?.pivotPoint?.clone();
  if (!pivotPoint) {
    return false;
  }

  const pivotCartographic = pointToCartographic(pivotPoint, terrainEllipsoid);
  if (!Number.isFinite(pivotCartographic.lat) || !Number.isFinite(pivotCartographic.lon)) {
    return false;
  }

  const latRad = pivotCartographic.lat;
  const lngRad = pivotCartographic.lon;
  const latDeg = latRad * RAD_TO_DEG;
  const lngDeg = lngRad * RAD_TO_DEG;

  const up = new THREE.Vector3();
  const east = new THREE.Vector3();
  const north = new THREE.Vector3();
  terrainEllipsoid.getCartographicToNormal(latRad, lngRad, up);
  terrainEllipsoid.getEastNorthUpAxes(latRad, lngRad, east, north, new THREE.Vector3());

  const cameraOffset = camera.position.clone().sub(pivotPoint);
  const offsetBasis = decomposeOnBasis(cameraOffset, east, north, up);
  const currentHeight = Math.max(offsetBasis.up, GLOBE_NAV_MIN_HEIGHT_ABOVE_GROUND);

  const cameraForward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion).normalize();
  const tangentForward = projectOntoTangentPlane(cameraForward, up, north);
  const tangentRight = tangentForward.clone().cross(up).normalize();
  const forwardBasis = decomposeOnBasis(cameraForward, east, north, up);

  const horizontalMagnitude = Math.hypot(movement.forward, movement.strafe);
  const horizontalStep = THREE.MathUtils.clamp(
    currentHeight * GLOBE_NAV_HORIZONTAL_SPEED_FACTOR,
    GLOBE_NAV_MIN_STEP_METERS,
    GLOBE_NAV_MAX_STEP_METERS,
  );
  const verticalStep = THREE.MathUtils.clamp(
    currentHeight * GLOBE_NAV_VERTICAL_SPEED_FACTOR,
    GLOBE_NAV_MIN_STEP_METERS,
    GLOBE_NAV_MAX_STEP_METERS,
  );

  let eastMeters = 0;
  let northMeters = 0;
  if (horizontalMagnitude > 0) {
    const movementScale = 1 / Math.max(1, horizontalMagnitude);
    const horizontalDelta = new THREE.Vector3()
      .addScaledVector(tangentForward, movement.forward * movementScale * horizontalStep)
      .addScaledVector(tangentRight, movement.strafe * movementScale * horizontalStep);
    eastMeters = horizontalDelta.dot(east);
    northMeters = horizontalDelta.dot(north);
  }

  const metersPerLon = Math.max(metersPerDegLon(latDeg), 1e-6);
  const nextLatDeg = latDeg + northMeters / METERS_PER_DEG_LAT;
  const nextLngDeg = lngDeg + eastMeters / metersPerLon;
  const nextLatRad = nextLatDeg * DEG_TO_RAD;
  const nextLngRad = nextLngDeg * DEG_TO_RAD;

  const nextPivotPoint = new THREE.Vector3();
  terrainEllipsoid.getCartographicToPosition(nextLatRad, nextLngRad, 0, nextPivotPoint);

  const nextUp = new THREE.Vector3();
  const nextEast = new THREE.Vector3();
  const nextNorth = new THREE.Vector3();
  terrainEllipsoid.getCartographicToNormal(nextLatRad, nextLngRad, nextUp);
  terrainEllipsoid.getEastNorthUpAxes(nextLatRad, nextLngRad, nextEast, nextNorth, new THREE.Vector3());

  const nextCameraOffset = composeFromBasis(
    {
      east: offsetBasis.east,
      north: offsetBasis.north,
      up: Math.max(
        GLOBE_NAV_MIN_HEIGHT_ABOVE_GROUND,
        offsetBasis.up + movement.vertical * verticalStep,
      ),
    },
    nextEast,
    nextNorth,
    nextUp,
  );

  const nextForward = composeFromBasis(forwardBasis, nextEast, nextNorth, nextUp).normalize();
  if (nextForward.lengthSq() < 1e-10) {
    return false;
  }

  camera.position.copy(nextPivotPoint).add(nextCameraOffset);
  camera.up.copy(nextUp);
  camera.lookAt(camera.position.clone().add(nextForward));
  camera.updateMatrixWorld();

  controls?.pivotPoint?.copy(nextPivotPoint);
  controls?.update?.();

  return true;
}

export function getSelectedZoneKeyboardNudgeDelta(
  latDeg: number,
  lngDeg: number,
  camera: THREE.Camera | null | undefined,
  movement: { forward: number; strafe: number },
) {
  const horizontalMagnitude = Math.hypot(movement.forward, movement.strafe);
  if (horizontalMagnitude === 0) {
    return [0, 0] as const;
  }

  const latRad = latDeg * DEG_TO_RAD;
  const lngRad = lngDeg * DEG_TO_RAD;
  const up = new THREE.Vector3();
  const east = new THREE.Vector3();
  const north = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToNormal(latRad, lngRad, up);
  WGS84_ELLIPSOID.getEastNorthUpAxes(latRad, lngRad, east, north, new THREE.Vector3());

  const tangentForward = hasFiniteQuaternion(camera)
    ? projectOntoTangentPlane(
      new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion).normalize(),
      up,
      north,
    )
    : north.clone();
  const tangentRight = tangentForward.clone().cross(up).normalize();
  const stepMeters = SELECTED_ZONE_KEYBOARD_NUDGE_DELTA * METERS_PER_DEG_LAT;
  const movementScale = 1 / Math.max(1, horizontalMagnitude);
  const horizontalDelta = new THREE.Vector3()
    .addScaledVector(tangentForward, movement.forward * movementScale * stepMeters)
    .addScaledVector(tangentRight, movement.strafe * movementScale * stepMeters);

  const eastMeters = horizontalDelta.dot(east);
  const northMeters = horizontalDelta.dot(north);

  return [
    eastMeters / Math.max(metersPerDegLon(latDeg), 1e-6),
    northMeters / METERS_PER_DEG_LAT,
  ] as const;
}

export function syncGlobeControlsFallbackPlane(
  controls:
    | {
        fallbackPlane?: THREE.Plane;
        pivotPoint?: THREE.Vector3;
        getPivotPoint?: (target: THREE.Vector3) => THREE.Vector3 | null | undefined;
        useFallbackPlane?: boolean;
      }
    | null
    | undefined,
  camera: THREE.Camera | null | undefined,
) {
  if (!controls?.fallbackPlane || !camera) {
    return false;
  }

  const planePoint = new THREE.Vector3();
  let hasPlanePoint = false;

  if (hasFiniteVector3(controls.pivotPoint)) {
    planePoint.copy(controls.pivotPoint);
    hasPlanePoint = true;
  } else if (typeof controls.getPivotPoint === 'function') {
    controls.getPivotPoint(planePoint);
    hasPlanePoint = hasFiniteVector3(planePoint);
  }

  if (!hasPlanePoint) {
    return false;
  }

  const planeNormal = hasFiniteQuaternion(camera)
    ? new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion).normalize()
    : hasFiniteVector3(camera.position)
      ? planePoint.clone().sub(camera.position).normalize()
      : new THREE.Vector3(0, 0, -1);

  if (!hasFiniteVector3(planeNormal) || planeNormal.lengthSq() < 1e-10) {
    return false;
  }

  controls.fallbackPlane.setFromNormalAndCoplanarPoint(planeNormal, planePoint);
  if ('useFallbackPlane' in controls) {
    controls.useFallbackPlane = true;
  }
  return true;
}

interface GlobeCameraPose {
  cameraPos: THREE.Vector3;
  surfacePos: THREE.Vector3;
  normal: THREE.Vector3;
  cameraUp?: THREE.Vector3;
}

function applyCameraPoseToCamera(
  camera: THREE.Camera,
  pose: GlobeCameraPose,
  controls?: { pivotPoint?: THREE.Vector3; update?: () => void } | null,
) {
  camera.position.copy(pose.cameraPos);
  camera.up.copy(pose.cameraUp ?? pose.normal);
  camera.lookAt(pose.surfacePos);
  camera.updateMatrixWorld();

  if (controls?.pivotPoint) {
    controls.pivotPoint.copy(pose.surfacePos);
  }
  controls?.update?.();
}

export function computeCameraPose(
  lat: number,
  lng: number,
  heightAboveGroundMeters: number,
  terrainHeightMeters: number = 0,
): GlobeCameraPose {
  const surfacePos = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(
    lat * DEG_TO_RAD,
    lng * DEG_TO_RAD,
    terrainHeightMeters,
    surfacePos,
  );

  const normal = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToNormal(lat * DEG_TO_RAD, lng * DEG_TO_RAD, normal);

  const east = new THREE.Vector3();
  const north = new THREE.Vector3();
  WGS84_ELLIPSOID.getEastNorthUpAxes(
    lat * DEG_TO_RAD,
    lng * DEG_TO_RAD,
    east,
    north,
    new THREE.Vector3(),
  );

  const cameraPos = surfacePos.clone().add(normal.clone().multiplyScalar(heightAboveGroundMeters));
  const eastSkew = 0.25;
  const horizontalOffset = heightAboveGroundMeters * Math.tan(DEFAULT_INITIAL_CAMERA_PITCH_DEGREES * DEG_TO_RAD);
  const northOffset = horizontalOffset / Math.hypot(1, eastSkew);
  cameraPos.add(north.multiplyScalar(-northOffset));
  cameraPos.add(east.multiplyScalar(northOffset * eastSkew));

  // cameraUp defaults to the surface normal when no handoff up-vector is
  // supplied; returning it here keeps the type uniform across all return
  // paths so callers can read pose.cameraUp without TypeScript flagging
  // it as missing on this branch.
  return { cameraPos, surfacePos, normal, cameraUp: normal };
}

function computeBearingFromCamera(
  focusLat: number,
  focusLng: number,
  cameraPosition: THREE.Vector3 | null | undefined,
  terrainHeightMeters: number,
): number | null {
  if (
    !cameraPosition
    || !Number.isFinite(cameraPosition.x)
    || !Number.isFinite(cameraPosition.y)
    || !Number.isFinite(cameraPosition.z)
  ) {
    return null;
  }

  const surfacePos = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(
    focusLat * DEG_TO_RAD,
    focusLng * DEG_TO_RAD,
    terrainHeightMeters,
    surfacePos,
  );

  const normal = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToNormal(focusLat * DEG_TO_RAD, focusLng * DEG_TO_RAD, normal);

  const east = new THREE.Vector3();
  const north = new THREE.Vector3();
  WGS84_ELLIPSOID.getEastNorthUpAxes(
    focusLat * DEG_TO_RAD,
    focusLng * DEG_TO_RAD,
    east,
    north,
    new THREE.Vector3(),
  );

  const focusToCamera = cameraPosition.clone().sub(surfacePos);
  const horizontalOffset = focusToCamera.sub(
    normal.clone().multiplyScalar(focusToCamera.dot(normal)),
  );
  const eastComponent = horizontalOffset.dot(east);
  const northComponent = horizontalOffset.dot(north);

  if (!Number.isFinite(eastComponent) || !Number.isFinite(northComponent)) {
    return null;
  }

  if (Math.hypot(eastComponent, northComponent) < 1e-3) {
    return null;
  }

  return normalizeBearing(Math.atan2(-eastComponent, -northComponent) * RAD_TO_DEG);
}

function computePitchFromCamera(camera: THREE.Camera | null | undefined): number | null {
  const quaternion = camera?.quaternion as Partial<THREE.Quaternion> | undefined;
  const position = camera?.position as Partial<THREE.Vector3> | undefined;
  if (
    !camera
    || !quaternion
    || !position
    || !Number.isFinite(quaternion.x)
    || !Number.isFinite(quaternion.y)
    || !Number.isFinite(quaternion.z)
    || !Number.isFinite(quaternion.w)
    || !Number.isFinite(position.x)
    || !Number.isFinite(position.y)
    || !Number.isFinite(position.z)
  ) {
    return null;
  }

  const lookDirection = new THREE.Vector3(0, 0, -1)
    .applyQuaternion(camera.quaternion)
    .normalize();
  const surfaceNormal = new THREE.Vector3(position.x, position.y, position.z).normalize();

  return Math.acos(THREE.MathUtils.clamp(-lookDirection.dot(surfaceNormal), -1, 1)) * RAD_TO_DEG;
}

function sanitizeCoords(coords: number[][]): number[][] {
  const cleaned: number[][] = [];
  for (const c of coords) {
    if (!Array.isArray(c) || c.length < 2) continue;
    const lng = Number(c[0]);
    const lat = Number(c[1]);
    if (!Number.isFinite(lng) || !Number.isFinite(lat)) continue;
    if (Math.abs(lng) > 180 || Math.abs(lat) > 90) continue;
    if (
      cleaned.length === 0
      || Math.abs(lng - cleaned[cleaned.length - 1][0]) > 1e-7
      || Math.abs(lat - cleaned[cleaned.length - 1][1]) > 1e-7
    ) {
      cleaned.push([lng, lat]);
    }
  }
  return cleaned;
}

function getProjectFocusPoints(siteZones: SiteZone[]): [number, number][] {
  const validZones = siteZones
    .map((zone) => ({
      zoneType: zone.zone_type,
      coordinates: sanitizeCoords(zone.coordinates ?? []),
    }))
    .filter((zone) => zone.coordinates.length >= 3);
  const boundaryZones = validZones.filter((zone) => zone.zoneType === 'site_boundary');
  const focusZones = boundaryZones.length > 0 ? boundaryZones : validZones;

  return focusZones.flatMap((zone) => zone.coordinates as [number, number][]);
}

function getLngLatBounds(points: [number, number][]) {
  if (points.length < 2) return null;

  let west = Infinity;
  let south = Infinity;
  let east = -Infinity;
  let north = -Infinity;

  for (const [lng, lat] of points) {
    west = Math.min(west, lng);
    south = Math.min(south, lat);
    east = Math.max(east, lng);
    north = Math.max(north, lat);
  }

  if (![west, south, east, north].every(Number.isFinite)) {
    return null;
  }

  return { west, south, east, north };
}

function buildInitialViewFromViewport(
  latitude: number,
  longitude: number,
  bounds?: {
    west: number;
    south: number;
    east: number;
    north: number;
  },
) {
  if (!bounds) {
    return {
      lat: latitude,
      lng: longitude,
      altitude: DEFAULT_INITIAL_CAMERA_HEIGHT_ABOVE_GROUND,
    };
  }

  const corners: [number, number][] = [
    [bounds.west, bounds.south],
    [bounds.west, bounds.north],
    [bounds.east, bounds.south],
    [bounds.east, bounds.north],
  ];

  let maxDistMeters = 0;
  for (const corner of corners) {
    const distMeters = haversineDistance([longitude, latitude], corner);
    if (Number.isFinite(distMeters)) {
      maxDistMeters = Math.max(maxDistMeters, distMeters);
    }
  }

  return {
    lat: latitude,
    lng: longitude,
    altitude: Math.min(
      MAX_VIEWPORT_CAMERA_HEIGHT_ABOVE_GROUND,
      Math.max(
        MIN_INITIAL_CAMERA_HEIGHT_ABOVE_GROUND,
        maxDistMeters * VIEWPORT_FIT_INITIAL_CAMERA_MULTIPLIER,
      ),
    ),
  };
}

interface GlobePreferredView {
  latitude: number;
  longitude: number;
  bounds?: {
    west: number;
    south: number;
    east: number;
    north: number;
  };
  cameraPosition?: {
    latitude: number;
    longitude: number;
    altitude: number;
    pitch?: number;
    bearing?: number;
  };
  cameraOrientation?: {
    forward: {
      x: number;
      y: number;
      z: number;
    };
    up?: {
      x: number;
      y: number;
      z: number;
    };
  };
}

function isFiniteOrientationVector(value: unknown): value is { x: number; y: number; z: number } {
  return typeof value === 'object'
    && value !== null
    && 'x' in value
    && 'y' in value
    && 'z' in value
    && Number.isFinite(value.x)
    && Number.isFinite(value.y)
    && Number.isFinite(value.z);
}

function mapboxMercatorVectorToWorldDirection(
  latitude: number,
  longitude: number,
  vector: { x: number; y: number; z: number },
) {
  const east = new THREE.Vector3();
  const north = new THREE.Vector3();
  const up = new THREE.Vector3();
  WGS84_ELLIPSOID.getEastNorthUpAxes(
    latitude * DEG_TO_RAD,
    longitude * DEG_TO_RAD,
    east,
    north,
    up,
  );

  const worldDirection = east.multiplyScalar(vector.x)
    .add(north.multiplyScalar(-vector.y))
    .add(up.multiplyScalar(vector.z));

  if (worldDirection.lengthSq() < 1e-12) {
    return null;
  }

  return worldDirection.normalize();
}

function buildCameraPoseFromPreferredView(
  preferredView: GlobePreferredView,
  terrainHeightMeters: number,
): GlobeCameraPose | null {
  const cameraPosition = preferredView.cameraPosition;
  if (!cameraPosition) {
    return null;
  }

  const rawValues = [
    preferredView.latitude,
    preferredView.longitude,
    cameraPosition.latitude,
    cameraPosition.longitude,
    cameraPosition.altitude,
  ];
  if (rawValues.some((value) => !Number.isFinite(value))) {
    return null;
  }

  const surfacePos = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(
    preferredView.latitude * DEG_TO_RAD,
    preferredView.longitude * DEG_TO_RAD,
    terrainHeightMeters,
    surfacePos,
  );

  const normal = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToNormal(
    preferredView.latitude * DEG_TO_RAD,
    preferredView.longitude * DEG_TO_RAD,
    normal,
  );

  const cameraAltitude = Math.max(cameraPosition.altitude, terrainHeightMeters + 10);
  const rawCameraPos = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(
    cameraPosition.latitude * DEG_TO_RAD,
    cameraPosition.longitude * DEG_TO_RAD,
    cameraAltitude,
    rawCameraPos,
  );

  const cameraNormal = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToNormal(
    cameraPosition.latitude * DEG_TO_RAD,
    cameraPosition.longitude * DEG_TO_RAD,
    cameraNormal,
  );

  const handedOffForward = preferredView.cameraOrientation?.forward;
  if (isFiniteOrientationVector(handedOffForward)) {
    const worldForward = mapboxMercatorVectorToWorldDirection(
      cameraPosition.latitude,
      cameraPosition.longitude,
      handedOffForward,
    );

    if (worldForward) {
      const terrainEllipsoid = createTerrainEllipsoid(terrainHeightMeters);
      const intersection = new THREE.Vector3();
      const hit = terrainEllipsoid.intersectRay(
        new THREE.Ray(rawCameraPos.clone(), worldForward.clone()),
        intersection,
      );
      const fallbackDistance = Math.max(
        rawCameraPos.distanceTo(surfacePos),
        cameraAltitude * 4,
        1000,
      );
      const targetPos = hit
        ? intersection.clone()
        : rawCameraPos.clone().add(worldForward.multiplyScalar(fallbackDistance));
      const handedOffUp = isFiniteOrientationVector(preferredView.cameraOrientation?.up)
        ? mapboxMercatorVectorToWorldDirection(
            cameraPosition.latitude,
            cameraPosition.longitude,
            preferredView.cameraOrientation.up,
          )
        : null;

      return {
        cameraPos: rawCameraPos,
        surfacePos: targetPos,
        normal,
        cameraUp: handedOffUp ?? cameraNormal,
      };
    }
  }

  return { cameraPos: rawCameraPos, surfacePos, normal, cameraUp: cameraNormal };
}

/** Expose R3F camera to parent via ref */
function CameraExposer({ cameraRef }: { cameraRef: React.MutableRefObject<THREE.Camera | null> }) {
  const { camera, scene } = useThree();
  useEffect(() => {
    cameraRef.current = camera;
    // Dev-only handle for e2e/console scene access (see __globeDebug).
    if (import.meta.env.DEV) {
      const dbg = ((window as unknown as Record<string, unknown>).__globeDebug ??= {});
      Object.assign(dbg as object, { camera, scene });
    }
  }, [camera, scene, cameraRef]);
  return null;
}

function TilesExposer({
  tilesRef,
}: {
  tilesRef: React.MutableRefObject<SceneTileRenderer | null>;
}) {
  const tiles = useContext(TilesRendererContext);
  useEffect(() => {
    tilesRef.current = tiles as SceneTileRenderer | null;
  }, [tiles, tilesRef]);
  return null;
}

/** Monitor internal pitch from nadir (0=top-down, 90=horizon). */
function PitchMonitor({ onPitchChange }: { onPitchChange: (pitch: number) => void }) {
  const { camera } = useThree();
  const lastPitchRef = useRef(-1);

  useEffect(() => {
    const interval = setInterval(() => {
      const pitch = computePitchFromCamera(camera);
      if (pitch == null || !Number.isFinite(pitch)) {
        return;
      }

      const roundedPitch = Math.round(pitch);
      if (roundedPitch !== lastPitchRef.current) {
        lastPitchRef.current = roundedPitch;
        onPitchChange(roundedPitch);
      }
    }, 200); // Update 5x per second
    return () => clearInterval(interval);
  }, [camera, onPitchChange]);

  return null;
}

function FallbackPlaneSync({
  controlsRef,
}: {
  controlsRef: React.MutableRefObject<{
    fallbackPlane?: THREE.Plane;
    pivotPoint?: THREE.Vector3;
    getPivotPoint?: (target: THREE.Vector3) => THREE.Vector3 | null | undefined;
    useFallbackPlane?: boolean;
  } | null>;
}) {
  const { camera } = useThree();

  useEffect(() => {
    let rafId = 0;

    const updateFallbackPlane = () => {
      syncGlobeControlsFallbackPlane(controlsRef.current, camera);
      rafId = window.requestAnimationFrame(updateFallbackPlane);
    };

    updateFallbackPlane();
    return () => window.cancelAnimationFrame(rafId);
  }, [camera, controlsRef]);

  return null;
}

/** Render drawing preview dots inside R3F */
function DrawingPreviewFill({ points, terrainHeight }: { points: number[][]; terrainHeight: number }) {
  const geo = useMemo(() => {
    if (points.length < 3) return null;
    const centroid = computeCentroid(points);
    const mPerDegLon = metersPerDegLon(centroid[1]);
    // ENU: X=East, Y=North, Z=Up
    const localPts = points.map(c => new THREE.Vector2(
      (c[0] - centroid[0]) * mPerDegLon,
      (c[1] - centroid[1]) * METERS_PER_DEG_LAT,
    ));
    const indices = THREE.ShapeUtils.triangulateShape(localPts, []);
    const verts: number[] = [];
    for (const p of localPts) verts.push(p.x, p.y, DRAWING_FILL_LIFT_METERS);
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
    const idx: number[] = [];
    for (const tri of indices) idx.push(tri[0], tri[1], tri[2]);
    g.setIndex(idx);
    return { geo: g, centroid };
  }, [points]);

  if (!geo) return null;
  return (
    <EastNorthUpFrame lat={geo.centroid[1] * DEG_TO_RAD} lon={geo.centroid[0] * DEG_TO_RAD} height={terrainHeight}>
      <mesh geometry={geo.geo} renderOrder={98} frustumCulled={false}>
        <meshBasicMaterial color="#f59e0b" transparent opacity={0.25} side={THREE.DoubleSide} depthTest={false} depthWrite={false} />
      </mesh>
    </EastNorthUpFrame>
  );
}

function raycastTerrainHeightAtLngLat(
  lng: number,
  lat: number,
  tilesGroup: THREE.Object3D,
  raycaster: THREE.Raycaster,
): number | null {
  const origin = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(lat * DEG_TO_RAD, lng * DEG_TO_RAD, 50000, origin);
  const normal = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToNormal(lat * DEG_TO_RAD, lng * DEG_TO_RAD, normal);
  raycaster.set(origin, normal.negate());
  raycaster.far = 100000;

  const hit = raycaster.intersectObjects(tilesGroup.children, true)[0]?.point;
  return hit ? WGS84_ELLIPSOID.getPositionElevation(hit) : null;
}

function raycastObjectFilteredTerrainHeightAtLngLat(
  lng: number,
  lat: number,
  tilesGroup: THREE.Object3D,
  raycaster: THREE.Raycaster,
  fallback: number | null | undefined,
): number | null {
  const mPerDegLon = Math.max(1, Math.abs(metersPerDegLon(lat)));
  const diagonal = OBJECT_FILTER_SAMPLE_RADIUS_METERS * 0.7;
  const offsets: Array<[number, number]> = [
    [0, 0],
    [OBJECT_FILTER_SAMPLE_RADIUS_METERS, 0],
    [-OBJECT_FILTER_SAMPLE_RADIUS_METERS, 0],
    [0, OBJECT_FILTER_SAMPLE_RADIUS_METERS],
    [0, -OBJECT_FILTER_SAMPLE_RADIUS_METERS],
    [diagonal, diagonal],
    [diagonal, -diagonal],
    [-diagonal, diagonal],
    [-diagonal, -diagonal],
  ];
  const samples = offsets.map(([eastMeters, northMeters]) => (
    raycastTerrainHeightAtLngLat(
      lng + eastMeters / mPerDegLon,
      lat + northMeters / METERS_PER_DEG_LAT,
      tilesGroup,
      raycaster,
    )
  ));

  return getObjectFilteredTerrainHeight(samples, samples[0] ?? fallback);
}

function DrawingDots({
  points,
  pointHeights,
  terrainHeight,
  linear,
  filterObjectHeights,
}: {
  points: number[][];
  pointHeights: number[];
  terrainHeight: number;
  linear: boolean;
  filterObjectHeights: boolean;
}) {
  const tiles = useContext(TilesRendererContext);
  const sampledPointHeights = useMemo(() => {
    const tilesGroup = tiles?.group;
    if (!tilesGroup?.children?.length) {
      return points.map((_, index) => pointHeights[index] ?? terrainHeight);
    }

    const raycaster = new THREE.Raycaster();
    if (filterObjectHeights) {
      return points.map((point, index) => (
        raycastObjectFilteredTerrainHeightAtLngLat(
          point[0],
          point[1],
          tilesGroup,
          raycaster,
          pointHeights[index] ?? terrainHeight,
        )
        ?? pointHeights[index]
        ?? terrainHeight
      ));
    }

    return points.map((point, index) => (
      pointHeights[index]
      ?? raycastTerrainHeightAtLngLat(point[0], point[1], tilesGroup, raycaster)
      ?? terrainHeight
    ));
  }, [filterObjectHeights, pointHeights, points, terrainHeight, tiles]);
  const previewHeight = useMemo(() => {
    const finiteHeights = sampledPointHeights.filter(Number.isFinite);
    if (finiteHeights.length === 0) {
      return terrainHeight;
    }
    return finiteHeights.reduce((sum, height) => sum + height, 0) / finiteHeights.length;
  }, [sampledPointHeights, terrainHeight]);
  const liveArea = useMemo(() => (
    !linear && points.length >= 3 ? polygonAreaM2(points) : 0
  ), [linear, points]);

  if (points.length === 0) return null;
  return (
    <>
      {/* Preview fill polygon */}
      {!linear && <DrawingPreviewFill points={points} terrainHeight={previewHeight} />}

      {/* Live polygon area */}
      {liveArea > 0 && (() => {
        const centroid = computeCentroid(points);
        return (
          <EastNorthUpFrame lat={centroid[1] * DEG_TO_RAD} lon={centroid[0] * DEG_TO_RAD} height={previewHeight}>
            <group position={[0, 0, DRAWING_VERTEX_LIFT_METERS + 6]}>
              <Html center zIndexRange={GLOBE_SCENE_HTML_Z_INDEX_RANGE} style={{ pointerEvents: 'none' }}>
                <div className="pointer-events-none whitespace-nowrap rounded-full border border-white/70 bg-blue-600/95 px-3 py-1 text-xs font-semibold text-white shadow-lg backdrop-blur-sm">
                  {formatDrawingArea(liveArea)}
                </div>
              </Html>
            </group>
          </EastNorthUpFrame>
        );
      })()}

      {/* Vertex dots */}
      {points.map((pt, i) => {
        const pointHeight = sampledPointHeights[i] ?? terrainHeight;
        return (
          <EastNorthUpFrame key={`dot-${i}-${pt[0]}-${pt[1]}`} lat={pt[1] * DEG_TO_RAD} lon={pt[0] * DEG_TO_RAD} height={pointHeight}>
            <mesh position={[0, 0, DRAWING_VERTEX_LIFT_METERS * 0.45]} renderOrder={998} frustumCulled={false}>
              <cylinderGeometry args={[0.22, 0.22, DRAWING_VERTEX_LIFT_METERS * 0.9, 10]} />
              <meshBasicMaterial color="#fbbf24" transparent opacity={0.45} depthTest={false} depthWrite={false} />
            </mesh>
            <group position={[0, 0, DRAWING_VERTEX_LIFT_METERS]}>
              <mesh renderOrder={999} frustumCulled={false}>
                <sphereGeometry args={[i === points.length - 1 ? DRAWING_VERTEX_RADIUS_METERS + 0.45 : DRAWING_VERTEX_RADIUS_METERS, 16, 16]} />
                <meshBasicMaterial color={i === points.length - 1 ? '#f59e0b' : '#fbbf24'} depthTest={false} depthWrite={false} />
              </mesh>
              <Html center zIndexRange={GLOBE_SCENE_HTML_Z_INDEX_RANGE} style={{ pointerEvents: 'none' }}>
                <div
                  className={`pointer-events-none flex items-center justify-center rounded-full border-2 font-semibold text-white shadow-lg ${
                    i === points.length - 1
                      ? 'h-6 w-6 border-white bg-amber-500 text-[10px]'
                      : 'h-5 w-5 border-white/90 bg-amber-400 text-[9px]'
                  }`}
                >
                  {i + 1}
                </div>
              </Html>
            </group>
          </EastNorthUpFrame>
        );
      })}

      {/* Outline connecting dots */}
      {points.length >= 2 && (() => {
        const centroid = computeCentroid(points);
        const mPerDegLon = metersPerDegLon(centroid[1]);
        const outVerts: number[] = [];
        for (const c of points) {
          outVerts.push(
            (c[0] - centroid[0]) * mPerDegLon,
            (c[1] - centroid[1]) * METERS_PER_DEG_LAT,
            DRAWING_OUTLINE_LIFT_METERS,
          );
        }
        // Close the loop for polygons only. Linear tools stay open while placing waypoints.
        if (!linear && points.length >= 3) {
          outVerts.push(
            (points[0][0] - centroid[0]) * mPerDegLon,
            (points[0][1] - centroid[1]) * METERS_PER_DEG_LAT,
            DRAWING_OUTLINE_LIFT_METERS,
          );
        }
        const lineGeo = new THREE.BufferGeometry();
        lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(outVerts, 3));
        return (
          <EastNorthUpFrame lat={centroid[1] * DEG_TO_RAD} lon={centroid[0] * DEG_TO_RAD} height={previewHeight}>
            {/* @ts-expect-error R3F line type conflict */}
            <line geometry={lineGeo} renderOrder={999} frustumCulled={false}>
              <lineBasicMaterial color="#f59e0b" linewidth={2} depthTest={false} depthWrite={false} />
            </line>
          </EastNorthUpFrame>
        );
      })()}
    </>
  );
}

function MeasurementOverlay({
  points,
  pointHeights,
  terrainHeight,
}: {
  points: number[][];
  pointHeights: number[];
  terrainHeight: number;
}) {
  const totalDistance = useMemo(() => polylineLength(points), [points]);
  const lineHeight = useMemo(() => {
    const finiteHeights = pointHeights.filter(Number.isFinite);
    if (finiteHeights.length === 0) return terrainHeight;
    return finiteHeights.reduce((sum, height) => sum + height, 0) / finiteHeights.length;
  }, [pointHeights, terrainHeight]);
  const segments = useMemo(() => {
    const result: Array<{ key: string; midpoint: [number, number]; height: number; distance: number }> = [];
    for (let index = 1; index < points.length; index += 1) {
      const start = points[index - 1];
      const end = points[index];
      const startHeight = pointHeights[index - 1] ?? terrainHeight;
      const endHeight = pointHeights[index] ?? terrainHeight;
      result.push({
        key: `${index}-${start[0]}-${start[1]}-${end[0]}-${end[1]}`,
        midpoint: [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2],
        height: (startHeight + endHeight) / 2,
        distance: haversineDistance([start[0], start[1]], [end[0], end[1]]),
      });
    }
    return result;
  }, [pointHeights, points, terrainHeight]);

  if (points.length === 0) return null;

  const lastPoint = points[points.length - 1];
  const lastPointHeight = pointHeights[points.length - 1] ?? terrainHeight;

  return (
    <>
      {points.length >= 2 && (() => {
        const centroid = computeCentroid(points);
        const mPerDegLon = metersPerDegLon(centroid[1]);
        const verts: number[] = [];
        for (const c of points) {
          verts.push(
            (c[0] - centroid[0]) * mPerDegLon,
            (c[1] - centroid[1]) * METERS_PER_DEG_LAT,
            MEASURE_LINE_LIFT_METERS,
          );
        }
        const lineGeo = new THREE.BufferGeometry();
        lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
        return (
          <EastNorthUpFrame lat={centroid[1] * DEG_TO_RAD} lon={centroid[0] * DEG_TO_RAD} height={lineHeight}>
            {/* @ts-expect-error R3F line type conflict */}
            <line geometry={lineGeo} renderOrder={1002} frustumCulled={false}>
              <lineBasicMaterial color="#38bdf8" linewidth={3} depthTest={false} depthWrite={false} />
            </line>
          </EastNorthUpFrame>
        );
      })()}

      {points.map((point, index) => (
        <EastNorthUpFrame
          key={`measure-point-${index}-${point[0]}-${point[1]}`}
          lat={point[1] * DEG_TO_RAD}
          lon={point[0] * DEG_TO_RAD}
          height={pointHeights[index] ?? terrainHeight}
        >
          <mesh position={[0, 0, MEASURE_LINE_LIFT_METERS]} renderOrder={1003} frustumCulled={false}>
            <sphereGeometry args={[MEASURE_POINT_RADIUS_METERS, 16, 16]} />
            <meshBasicMaterial color="#38bdf8" depthTest={false} depthWrite={false} />
          </mesh>
          <group position={[0, 0, MEASURE_LINE_LIFT_METERS + 0.4]}>
            <Html center zIndexRange={GLOBE_SCENE_HTML_Z_INDEX_RANGE} style={{ pointerEvents: 'none' }}>
              <div className="pointer-events-none flex h-5 min-w-5 items-center justify-center rounded-full border border-white/80 bg-sky-500 px-1.5 text-[10px] font-bold text-white shadow-lg">
                {index + 1}
              </div>
            </Html>
          </group>
        </EastNorthUpFrame>
      ))}

      {segments.map((segment) => (
        <EastNorthUpFrame
          key={`measure-segment-${segment.key}`}
          lat={segment.midpoint[1] * DEG_TO_RAD}
          lon={segment.midpoint[0] * DEG_TO_RAD}
          height={segment.height}
        >
          <group position={[0, 0, MEASURE_LINE_LIFT_METERS + 2.5]}>
            <Html center zIndexRange={GLOBE_SCENE_HTML_Z_INDEX_RANGE} style={{ pointerEvents: 'none' }}>
              <div className="pointer-events-none whitespace-nowrap rounded-full border border-sky-200/80 bg-gray-950/85 px-2 py-0.5 text-[11px] font-semibold text-sky-100 shadow-lg backdrop-blur-sm">
                {formatDistance(segment.distance)}
              </div>
            </Html>
          </group>
        </EastNorthUpFrame>
      ))}

      {points.length >= 2 && (
        <EastNorthUpFrame lat={lastPoint[1] * DEG_TO_RAD} lon={lastPoint[0] * DEG_TO_RAD} height={lastPointHeight}>
          <group position={[0, 0, MEASURE_LINE_LIFT_METERS + 7]}>
            <Html center zIndexRange={GLOBE_SCENE_HTML_Z_INDEX_RANGE} style={{ pointerEvents: 'none' }}>
              <div className="pointer-events-none whitespace-nowrap rounded-full border border-white/80 bg-sky-600 px-3 py-1 text-xs font-bold text-white shadow-lg">
                Total {formatDistance(totalDistance)}
              </div>
            </Html>
          </group>
        </EastNorthUpFrame>
      )}
    </>
  );
}

interface GlobeSitePlannerMapProps {
  latitude?: number;
  longitude?: number;
  preferredView?: GlobePreferredView;
  siteZones: SiteZone[];
  /** Project buildings — those with generated GLBs get placed on the globe. */
  buildings?: Building[];
  massingFeatures?: unknown[];
  onZoneCreated: (coordinates: number[][], zoneType: SiteZoneType, properties?: SiteZoneProperties) => void;
  onZoneUpdated: (zoneId: string, coordinates: number[][]) => void;
  onZoneSelected: (zoneId: string | null) => void;
  onZoneDeleted?: (zoneId: string) => void;
  onBuildingDeleted?: (buildingId: string) => void;
  onCopyZone?: (zoneId: string) => void;
  onPasteZone?: () => void;
  canPasteZone?: boolean;
  measureModeActive?: boolean;
  interactionPaused?: boolean;
  onMeasureModeChange?: (active: boolean) => void;
  /**
   * Emitted when the R3F canvas, THREE camera, and terrain elevation are all
   * available. Downstream `GlobeAIRenderPanel` consumes `{canvas, camera,
   * terrainHeight}` directly (stable's contract, not codex's Mapbox-shim
   * viewport). The Mapbox-shim `GlobeAIRenderViewport` is preserved below as
   * dead code for any future code that wants to adapt the globe to that API.
   */
  onGlobeReady?: (refs: {
    canvas: HTMLCanvasElement;
    camera: THREE.Camera;
    terrainHeight: number;
    isSettled?: boolean;
    /** Waits for a stable Google-tile window before a paid screenshot. */
    waitForTilesSettled?: () => Promise<boolean>;
    /** Show/hide placed GLB building models — the render pipeline uses this
     *  for polygon-only captures when "Render with 3D models" is off. */
    setBuildingModelsVisible?: (visible: boolean) => void;
    /** Capture a clean, current-camera 3D beauty frame plus exact proposal
     *  mask and semantic class-ID frame. This is isolated from Classic. */
    captureDirect3D?: () => Promise<Direct3DCaptureBundle>;
  }) => void;
  /** Fired with the ids of buildings whose GLB is currently mounted on the
   *  globe — the render panel keys preserve-the-massing prompts off it. */
  onModeledBuildingsChange?: (ids: Set<string>) => void;
}

export interface GlobeAIRenderViewport {
  getCanvas: () => HTMLCanvasElement;
  getBounds: () => {
    getWest: () => number;
    getSouth: () => number;
    getEast: () => number;
    getNorth: () => number;
  };
  getCenter: () => { lng: number; lat: number };
  getPitch: () => number;
  getBearing: () => number;
  project: (lngLat: [number, number] | { lng: number; lat: number }, altitudeAboveTerrain?: number) => { x: number; y: number };
  unproject: (point: [number, number]) => { lng: number; lat: number };
  getLayer: (_id: string) => null;
  setLayoutProperty: (_id: string, _name: string, _value: string) => void;
  /**
   * Toggle visibility of the user-drawn zone overlays (colored fills,
   * outlines, labels). Used by the AI render capture pipeline to grab
   * a clean satellite screenshot without the colored polygon fills
   * bleeding through into Gemini's output.
   */
  setZoneOverlaysVisible: (visible: boolean) => void;
}

export function GlobeSitePlannerMap({
  latitude: _latitude = 51.045,
  longitude: _longitude = -114.07,
  preferredView,
  siteZones,
  buildings,
  onZoneCreated,
  onZoneUpdated,
  onZoneSelected,
  onZoneDeleted: _onZoneDeleted,
  onBuildingDeleted,
  onCopyZone,
  onPasteZone,
  canPasteZone = false,
  measureModeActive = false,
  interactionPaused = false,
  onMeasureModeChange,
  onGlobeReady,
  onModeledBuildingsChange,
}: GlobeSitePlannerMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cameraRef = useRef<THREE.Camera | null>(null);
  const globeControlsRef = useRef<any>(null);
  const globeDragRef = useCreateGlobeDragRef();
  const isRedispatchingCtrlPointerRef = useRef(false);
  const {
    selectedZoneId, activeSitePlannerTool, activeToolProperties,
    setActiveSitePlannerTool,
    streetViewPegman, setStreetViewPosition, setStreetViewAngle, setStreetViewActive,
  } = useViewerStore();

  const hasDrawingTool = activeSitePlannerTool !== null;
  const linear = isLinearTool(activeSitePlannerTool);

  // LOD settlement state â€” true when 3D tiles have fully loaded
  const [isSceneSettled, setIsSceneSettled] = useState(false);
  // Internal camera pitch from nadir (0=top-down, 90=horizon).
  // UI and render prompts convert this to camera elevation (0=ground, 90=overhead).
  const [pitchAngle, setPitchAngle] = useState(0);
  const pitchAngleRef = useRef(0);
  pitchAngleRef.current = pitchAngle;
  const cameraElevation = pitchFromNadirToCameraElevation(pitchAngle);
  const cameraElevationBadge = getCameraElevationBadge(cameraElevation);

  // Zone overlay visibility â€” flipped off by the AI render pipeline
  // so the captured screenshot contains only the real satellite/3D tiles,
  // without colored polygon fills baked into it. Default true so users
  // normally see their drawn zones.
  const [zoneOverlaysVisible, setZoneOverlaysVisible] = useState(true);
  const zoneOverlaysVisibleRef = useRef(true);
  zoneOverlaysVisibleRef.current = zoneOverlaysVisible;
  const hasCompiledCommunity3D = useMemo(
    () => siteZones.some(isCommunity3DCompiled),
    [siteZones],
  );
  useCleanPresentationAfterCommunity3DCompile(
    setZoneOverlaysVisible,
    hasCompiledCommunity3D,
  );

  // Placed 3D building models (generated GLBs). Deliberately OUTSIDE the
  // zone-overlay toggle: models are real massing and belong in AI-render
  // captures. modeledBuildingIds suppresses the matching zone prisms only
  // while a model is actually mounted.
  const [buildingModelsVisible, setBuildingModelsVisible] = useState(true);
  const [modeledBuildingIds, setModeledBuildingIds] = useState<Set<string>>(() => new Set());
  const [legoBuildingIds, setLegoBuildingIds] = useState<Set<string>>(() => new Set());
  const [buildingLayerRecoveryGeneration, setBuildingLayerRecoveryGeneration] = useState(0);
  const [selectedBuildingId, setSelectedBuildingId] = useState<string | null>(null);
  const selectedBuildingIdRef = useRef<string | null>(null);
  selectedBuildingIdRef.current = selectedBuildingId;
  // Coexistence: a building with a renderable LEGO recipe renders as a module
  // stack — it is excluded from the Meshy model layer (the stack wins).
  // Buildings with a saved recipe or an honest planned-massing fallback mount
  // the LEGO layer, which itself skips + debug-counts footprint-less records.
  const meshyBuildings = useMemo(
    () => excludeLegoStackBuildings(buildings ?? []),
    [buildings],
  );
  const legoLayerBuildings = useMemo(
    () => (buildings ?? []).filter((building) => (
      hasLegoRecipe(building)
      || (hasPlannedMassing(building) && !(building.lod_urls?.['0'] ?? building.model_url))
    )),
    [buildings],
  );
  const direct3DProposalBuildingIds = useMemo(
    () => getCurrentCommunity3DBuildingIds(siteZones, buildings ?? []),
    [buildings, siteZones],
  );
  const hasPlaceableModels = Boolean(buildings?.some((b) => b.lod_urls?.['0'] ?? b.model_url))
    || legoLayerBuildings.length > 0;
  // Prism suppression + outward "has real 3D massing" set = Meshy ∪ LEGO.
  const suppressedBuildingIds = useMemo(() => {
    if (legoBuildingIds.size === 0) return modeledBuildingIds;
    const merged = new Set(modeledBuildingIds);
    legoBuildingIds.forEach((id) => merged.add(id));
    return merged;
  }, [modeledBuildingIds, legoBuildingIds]);
  const preparedSiteBoundaryIds = useMemo(
    () => getPreparedSiteBoundaryIds(siteZones),
    [siteZones],
  );
  const tileMaskZones = useMemo(
    () => {
      // A compiled project boundary uses true world-coordinate clipping. Do
      // not combine it with projected stencil volumes; the spatial mask owns
      // the whole demolition envelope and correctly reveals context behind it.
      if (preparedSiteBoundaryIds.size > 0) {
        return siteZones.filter((zone) => preparedSiteBoundaryIds.has(zone.id));
      }
      return siteZones.filter((zone) => (
        shouldMaskReplacementBuildingTiles(
          zone,
          Boolean(zone.building_id && suppressedBuildingIds.has(zone.building_id)),
        )
        || shouldMaskCommunityGroundTiles(zone)
      ));
    },
    [preparedSiteBoundaryIds, siteZones, suppressedBuildingIds],
  );
  useEffect(() => {
    onModeledBuildingsChange?.(suppressedBuildingIds);
  }, [suppressedBuildingIds, onModeledBuildingsChange]);
  const handleModeledIdsChange = useCallback((ids: Set<string>) => setModeledBuildingIds(ids), []);
  const handleLegoIdsChange = useCallback((ids: Set<string>) => setLegoBuildingIds(ids), []);
  const handleBuildingModelsVisibilityToggle = useCallback(() => {
    if (buildingModelsVisible) {
      // Clear prism suppression in the same event as the model-layer unmount.
      // Child cleanup also reports an empty set, but waiting for that effect can
      // produce a frame where neither the detailed models nor fallback massing
      // is visible (and Fast Refresh can preserve that confusing state).
      setModeledBuildingIds(new Set());
      setLegoBuildingIds(new Set());
      setSelectedBuildingId(null);
    }
    setBuildingModelsVisible((visible) => !visible);
  }, [buildingModelsVisible]);

  // Dynamic terrain elevation â€” fetched from Google Elevation API on mount
  const [terrainElevation, setTerrainElevation] = useState(DEFAULT_TERRAIN_ELEVATION);
  const [isTerrainReady, setIsTerrainReady] = useState(false);
  const terrainElevationRef = useRef(DEFAULT_TERRAIN_ELEVATION);
  terrainElevationRef.current = terrainElevation;
  const terrainEllipsoidRef = useRef(createTerrainEllipsoid(DEFAULT_TERRAIN_ELEVATION));
  const tilesRendererRef = useRef<SceneTileRenderer | null>(null);
  const [sceneReady, setSceneReady] = useState(false);
  const [globeControlsReady, setGlobeControlsReady] = useState(false);
  const [isInitialCameraApplied, setIsInitialCameraApplied] = useState(false);
  const [initialRevealFallbackReady, setInitialRevealFallbackReady] = useState(false);
  const hasAppliedProjectViewRef = useRef(false);
  const lastAppliedZoneViewKeyRef = useRef<string | null>(null);
  const hasUserInteractedRef = useRef(false);
  const hasAppliedSettledViewRef = useRef(false);
  const hasVisibleInitialCameraRef = useRef(false);
  const lastAutoFramedProjectKeyRef = useRef<string | null>(null);
  const cameraRevealGenerationRef = useRef(0);
  const initialCameraPoseRef = useRef<GlobeCameraPose | null>(null);

  const projectZonePoints = useMemo(() => {
    const points = getProjectFocusPoints(siteZones);
    for (const building of buildings ?? []) {
      if (building.footprint_coordinates && building.footprint_coordinates.length >= 3) {
        for (const coordinate of building.footprint_coordinates) {
          if (
            coordinate.length >= 2
            && Number.isFinite(coordinate[0])
            && Number.isFinite(coordinate[1])
          ) {
            points.push([coordinate[0], coordinate[1]]);
          }
        }
      }
    }
    return points;
  }, [buildings, siteZones]);

  const projectZoneFocus = useMemo(() => {
    if (projectZonePoints.length < 3) return null;
    const bounds = getLngLatBounds(projectZonePoints);
    if (!bounds) return null;

    const focusLng = (bounds.west + bounds.east) / 2;
    const focusLat = (bounds.south + bounds.north) / 2;
    let maxDistMeters = 0;

    const corners: [number, number][] = [
      [bounds.west, bounds.south],
      [bounds.west, bounds.north],
      [bounds.east, bounds.south],
      [bounds.east, bounds.north],
    ];
    for (const corner of corners) {
      const distMeters = haversineDistance([focusLng, focusLat], corner);
      if (Number.isFinite(distMeters)) {
        maxDistMeters = Math.max(maxDistMeters, distMeters);
      }
    }

    return {
      lat: focusLat,
      lng: focusLng,
      maxDistMeters,
    };
  }, [projectZonePoints]);

  const shouldFitProjectZones = Boolean(!preferredView && projectZoneFocus);
  const projectZoneFocusKey = projectZoneFocus
    ? `${projectZoneFocus.lat.toFixed(7)}:${projectZoneFocus.lng.toFixed(7)}:${Math.round(projectZoneFocus.maxDistMeters)}`
    : null;

  const focusLatitude = preferredView?.latitude ?? _latitude;
  const focusLongitude = preferredView?.longitude ?? _longitude;
  const fallbackRenderBounds = useMemo(() => {
    if (preferredView?.bounds) {
      return preferredView.bounds;
    }

    if (shouldFitProjectZones && projectZonePoints.length >= 3) {
      const bounds = getLngLatBounds(projectZonePoints);
      if (!bounds) {
        return {
          west: focusLongitude - 0.01,
          south: focusLatitude - 0.01,
          east: focusLongitude + 0.01,
          north: focusLatitude + 0.01,
        };
      }

      const lngPad = Math.max((bounds.east - bounds.west) * 0.18, 0.0015);
      const latPad = Math.max((bounds.north - bounds.south) * 0.18, 0.0015);
      return {
        west: bounds.west - lngPad,
        south: bounds.south - latPad,
        east: bounds.east + lngPad,
        north: bounds.north + latPad,
      };
    }

    return {
      west: focusLongitude - 0.01,
      south: focusLatitude - 0.01,
      east: focusLongitude + 0.01,
      north: focusLatitude + 0.01,
    };
  }, [focusLatitude, focusLongitude, preferredView?.bounds, projectZonePoints, shouldFitProjectZones]);

  const initialView = useMemo(() => {
    if (preferredView) {
      return buildInitialViewFromViewport(
        preferredView.latitude,
        preferredView.longitude,
        preferredView.bounds,
      );
    }

    if (shouldFitProjectZones && projectZoneFocus) {
      return {
        lat: projectZoneFocus.lat,
        lng: projectZoneFocus.lng,
        altitude: Math.min(
          MAX_INITIAL_CAMERA_HEIGHT_ABOVE_GROUND,
          Math.max(MIN_INITIAL_CAMERA_HEIGHT_ABOVE_GROUND, projectZoneFocus.maxDistMeters * ZONE_FIT_INITIAL_CAMERA_MULTIPLIER),
        ),
      };
    }

    return {
      lat: _latitude,
      lng: _longitude,
      altitude: DEFAULT_INITIAL_CAMERA_HEIGHT_ABOVE_GROUND,
    };
  }, [_latitude, _longitude, preferredView, projectZoneFocus, shouldFitProjectZones]);

  const preferredCameraPose = useMemo(() => (
    preferredView
      ? buildCameraPoseFromPreferredView(preferredView, terrainElevation)
      : null
  ), [preferredView, terrainElevation]);

  const getCanvasViewportSize = useCallback((canvas: HTMLCanvasElement) => ({
    width: canvas.clientWidth || canvas.width || 1,
    height: canvas.clientHeight || canvas.height || 1,
  }), []);

  const projectLngLatToViewport = useCallback((
    lngLat: [number, number] | { lng: number; lat: number },
    altitudeAboveTerrain?: number,
  ) => {
    const canvas = canvasRef.current;
    const camera = cameraRef.current;
    const { lng, lat } = Array.isArray(lngLat)
      ? { lng: lngLat[0], lat: lngLat[1] }
      : lngLat;

    if (!canvas || !camera) {
      return { x: 0, y: 0 };
    }

    const world = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToPosition(
      lat * DEG_TO_RAD,
      lng * DEG_TO_RAD,
      terrainElevationRef.current + (altitudeAboveTerrain ?? 0),
      world,
    );
    world.project(camera as THREE.Camera);

    const { width, height } = getCanvasViewportSize(canvas);
    return {
      x: ((world.x + 1) / 2) * width,
      y: ((1 - world.y) / 2) * height,
    };
  }, [getCanvasViewportSize]);

  const raycastSurfacePoint = useCallback((ndcX: number, ndcY: number): {
    lngLat: [number, number];
    height: number;
  } | null => {
    const camera = cameraRef.current;
    if (!camera) return null;

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera as THREE.Camera);

    const tilesGroup = tilesRendererRef.current?.group;
    if (tilesGroup && tilesGroup.children.length > 0) {
      const hits = raycaster.intersectObjects(tilesGroup.children, true);
      if (hits.length > 0) {
        const cartographic = pointToCartographic(hits[0].point, terrainEllipsoidRef.current);
        return {
          lngLat: [cartographic.lon * RAD_TO_DEG, cartographic.lat * RAD_TO_DEG],
          height: WGS84_ELLIPSOID.getPositionElevation(hits[0].point),
        };
      }
    }

    const hit = new THREE.Vector3();
    const result = terrainEllipsoidRef.current.intersectRay(raycaster.ray, hit);
    if (!result) return null;

    const cartographic = pointToCartographic(hit, terrainEllipsoidRef.current);
    return {
      lngLat: [cartographic.lon * RAD_TO_DEG, cartographic.lat * RAD_TO_DEG],
      height: terrainElevationRef.current,
    };
  }, []);
  const raycastLngLat = useCallback((ndcX: number, ndcY: number): [number, number] | null => (
    raycastSurfacePoint(ndcX, ndcY)?.lngLat ?? null
  ), [raycastSurfacePoint]);

  const unprojectViewportPoint = useCallback((point: [number, number]) => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return { lng: focusLongitude, lat: focusLatitude };
    }

    const { width, height } = getCanvasViewportSize(canvas);
    const clampedX = Math.min(Math.max(point[0], 0), width);
    const clampedY = Math.min(Math.max(point[1], 0), height);
    const ndcX = (clampedX / width) * 2 - 1;
    const ndcY = -(clampedY / height) * 2 + 1;
    const lngLat = raycastLngLat(ndcX, ndcY);
    if (!lngLat) {
      return { lng: focusLongitude, lat: focusLatitude };
    }
    return {
      lng: lngLat[0],
      lat: lngLat[1],
    };
  }, [focusLatitude, focusLongitude, getCanvasViewportSize, raycastLngLat]);

  const applyCameraPose = useCallback((pose: {
    cameraPos: THREE.Vector3;
    surfacePos: THREE.Vector3;
    normal: THREE.Vector3;
    cameraUp?: THREE.Vector3;
  }) => {
    const camera = cameraRef.current;
    if (!camera) return;

    applyCameraPoseToCamera(camera, pose, globeControlsRef.current);
  }, []);

  const applyCameraView = useCallback((lat: number, lng: number, altitudeMeters: number) => {
    applyCameraPose(
      computeCameraPose(
        lat,
        lng,
        altitudeMeters,
        terrainElevation,
      ),
    );
  }, [applyCameraPose, terrainElevation]);

  // Auto-frame pilot (cc_auto_frame): fly the camera so the given zones fill
  // ~70% of the frame at the default oblique pitch — close enough to inspect
  // park/building detail while retaining a safe context margin. This is the
  // empirically reliable
  // manual-zoom containment fix, automated. Iterates apply-pose -> project ->
  // adjust height, so it needs no closed-form frustum math. Pilot limitation:
  // does not restore the previous camera pose.
  const frameZonesForRender = useCallback(async (
    renderZones: Array<{ coordinates?: [number, number][] }>,
  ): Promise<boolean> => {
    const canvas = canvasRef.current;
    const camera = cameraRef.current;
    if (!canvas || !camera) return false;
    const coords = renderZones.flatMap(z => z.coordinates ?? []);
    if (coords.length < 3) return false;
    let minLng = Infinity; let maxLng = -Infinity;
    let minLat = Infinity; let maxLat = -Infinity;
    for (const [lng, lat] of coords) {
      minLng = Math.min(minLng, lng); maxLng = Math.max(maxLng, lng);
      minLat = Math.min(minLat, lat); maxLat = Math.max(maxLat, lat);
    }
    const centerLng = (minLng + maxLng) / 2;
    const centerLat = (minLat + maxLat) / 2;
    const spanNorthM = (maxLat - minLat) * 111320;
    const spanEastM = (maxLng - minLng) * 111320 * Math.cos(centerLat * DEG_TO_RAD);
    const spanM = Math.max(spanNorthM, spanEastM, 30);
    const cameraFov = camera instanceof THREE.PerspectiveCamera ? camera.fov : 75;
    let heightM = estimateProjectFrameHeight(
      spanM,
      cameraFov,
      DEFAULT_INITIAL_CAMERA_PITCH_DEGREES,
      PROJECT_FRAME_TARGET_FRACTION,
    );
    const TARGET = PROJECT_FRAME_TARGET_FRACTION;
    for (let i = 0; i < 3; i++) {
      applyCameraView(centerLat, centerLng, heightM);
      (camera as THREE.PerspectiveCamera).updateMatrixWorld?.(true);
      const { width, height: viewportH } = getCanvasViewportSize(canvas);
      let minX = Infinity; let maxX = -Infinity;
      let minY = Infinity; let maxY = -Infinity;
      for (const c of coords) {
        const p = projectLngLatToViewport(c as [number, number]);
        minX = Math.min(minX, p.x); maxX = Math.max(maxX, p.x);
        minY = Math.min(minY, p.y); maxY = Math.max(maxY, p.y);
      }
      const frac = Math.max((maxX - minX) / width, (maxY - minY) / viewportH);
      if (!Number.isFinite(frac) || frac <= 0) return false;
      if (Math.abs(frac - TARGET) < 0.06) break;
      heightM = Math.min(
        Math.max(heightM * (frac / TARGET), PROJECT_FRAME_MIN_HEIGHT_M),
        PROJECT_FRAME_MAX_HEIGHT_M,
      );
    }
    // Two settled frames so tiles/props re-render at the new pose before the
    // caller captures the canvas.
    await new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
    return true;
  }, [applyCameraView, projectLngLatToViewport, getCanvasViewportSize]);

  useEffect(() => {
    if (!import.meta.env.DEV) return;
    const dbg = ((window as unknown as Record<string, unknown>).__globeDebug ??= {}) as Record<string, unknown>;
    dbg.frameZonesForRender = frameZonesForRender;
  }, [frameZonesForRender]);

  const hideCanvasUntilPose = useCallback(() => {
    cameraRevealGenerationRef.current += 1;
    const canvas = canvasRef.current;
    if (!canvas) return;
    canvas.style.visibility = 'hidden';
    canvas.style.opacity = '0';
  }, []);

  const revealCanvasAfterPose = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const revealGeneration = cameraRevealGenerationRef.current;

    const reveal = () => {
      if (cameraRevealGenerationRef.current !== revealGeneration) return;
      if (canvasRef.current !== canvas) return;
      canvas.style.visibility = 'visible';
      canvas.style.opacity = '1';
    };

    if (typeof window !== 'undefined') {
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(reveal);
      });
    } else {
      reveal();
    }
  }, []);

  const handleGlobeControlsRef = useCallback((controls: any | null) => {
    globeControlsRef.current = controls;
    if (controls) {
      syncGlobeControlsFallbackPlane(controls, cameraRef.current);
      if (isTerrainReady && !hasUserInteractedRef.current && cameraRef.current && initialCameraPoseRef.current) {
        applyCameraPoseToCamera(cameraRef.current, initialCameraPoseRef.current, controls);
      }
    }
    setGlobeControlsReady(Boolean(controls));
  }, [isTerrainReady]);

  const markUserInteracted = useCallback(() => {
    // A real pointer/wheel/keyboard gesture must immediately cancel every
    // pending initial/auto-frame retry. Waiting until the delayed canvas reveal
    // flag is set lets a retry move the camera between polygon vertices.
    hasUserInteractedRef.current = true;
  }, []);

  useEffect(() => {
    let cancelled = false;
    setIsTerrainReady(false);
    elevationApi.get(focusLatitude, focusLongitude)
      .then((data) => {
        if (!cancelled && Number.isFinite(data.ellipsoidal_height)) {
          const lowFidelityFallback = data.elevation === 0 && data.resolution >= 900;
          if (lowFidelityFallback) {
            console.warn(
              '[Globe] Elevation fallback detected; keeping default terrain elevation:',
              DEFAULT_TERRAIN_ELEVATION,
            );
            return;
          }
          // 3D tiles are positioned in WGS84/ECEF space, so ellipsoidal height
          // grounds overlays better than orthometric (MSL) height.
          const terrainHeight = data.ellipsoidal_height;
          console.log('[Globe] Elevation fetched:', terrainHeight, 'm for', focusLatitude, focusLongitude);
          setTerrainElevation(terrainHeight);
          terrainEllipsoidRef.current = createTerrainEllipsoid(terrainHeight);
        }
      })
      .catch((err) => {
        console.warn('[Globe] Elevation API failed, using default:', DEFAULT_TERRAIN_ELEVATION, err);
      })
      .finally(() => {
        if (!cancelled) {
          setIsTerrainReady(true);
        }
      });
    return () => { cancelled = true; };
  }, [focusLatitude, focusLongitude]);

  useEffect(() => {
    hasUserInteractedRef.current = false;
    hasVisibleInitialCameraRef.current = false;
    hasAppliedProjectViewRef.current = false;
    lastAutoFramedProjectKeyRef.current = null;
    lastAppliedZoneViewKeyRef.current = null;
    setIsInitialCameraApplied(false);
    setInitialRevealFallbackReady(false);
    hideCanvasUntilPose();
  }, [_latitude, _longitude, hideCanvasUntilPose, preferredView]);

  useEffect(() => {
    setInitialRevealFallbackReady(false);
    const timeoutId = window.setTimeout(
      () => setInitialRevealFallbackReady(true),
      INITIAL_CAMERA_REVEAL_FALLBACK_MS,
    );
    return () => window.clearTimeout(timeoutId);
  }, [_latitude, _longitude, initialView, preferredCameraPose]);

  useEffect(() => {
    hasAppliedSettledViewRef.current = false;
  }, [initialView, preferredCameraPose]);

  useEffect(() => {
    if (!sceneReady) return;
    if (hasUserInteractedRef.current) return;
    if (!isTerrainReady || !globeControlsReady) return;

    if (preferredCameraPose) {
      if (hasAppliedProjectViewRef.current) return;
      applyCameraPose(preferredCameraPose);
      hasAppliedProjectViewRef.current = true;
      return;
    }

    if (shouldFitProjectZones) {
      if (projectZoneFocusKey && lastAppliedZoneViewKeyRef.current === projectZoneFocusKey) return;
      applyCameraView(initialView.lat, initialView.lng, initialView.altitude);
      lastAppliedZoneViewKeyRef.current = projectZoneFocusKey;
      return;
    }

    if (hasAppliedProjectViewRef.current) return;
    applyCameraView(initialView.lat, initialView.lng, initialView.altitude);
    hasAppliedProjectViewRef.current = true;
  }, [applyCameraPose, applyCameraView, globeControlsReady, initialView, isTerrainReady, preferredCameraPose, projectZoneFocusKey, preferredView, sceneReady, shouldFitProjectZones]);

  useEffect(() => {
    if (!sceneReady) return;
    if (hasUserInteractedRef.current || hasAppliedSettledViewRef.current) return;
    if (!isTerrainReady || !globeControlsReady) return;
    if (!isSceneSettled && !initialRevealFallbackReady) return;

    let cancelled = false;
    const reapply = () => {
      if (cancelled || hasUserInteractedRef.current || hasAppliedSettledViewRef.current) return;
      if (preferredCameraPose) {
        applyCameraPose(preferredCameraPose);
      } else {
        applyCameraView(initialView.lat, initialView.lng, initialView.altitude);
      }
      hasAppliedSettledViewRef.current = true;
      hasVisibleInitialCameraRef.current = true;
      setIsInitialCameraApplied(true);
      revealCanvasAfterPose();
    };

    const timeoutId = window.setTimeout(reapply, 0);
    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [applyCameraPose, applyCameraView, globeControlsReady, initialRevealFallbackReady, initialView, isSceneSettled, isTerrainReady, preferredCameraPose, preferredView, revealCanvasAfterPose, sceneReady]);

  // The basic initial-pose path can run before asynchronously loaded zones
  // exist, leaving a reopened project at city scale. Run the projection-
  // verified framing after the coarse settled pose has finished. Never steal
  // the camera after a real user interaction.
  useEffect(() => {
    if (!projectZoneFocusKey || siteZones.length === 0) return;
    if (!sceneReady || !isTerrainReady || !globeControlsReady) return;
    if (!isSceneSettled && !initialRevealFallbackReady) return;
    if (hasUserInteractedRef.current) return;
    if (lastAutoFramedProjectKeyRef.current === projectZoneFocusKey) return;

    const focusZones = siteZones
      .filter((zone) => zone.zone_type === 'site_boundary')
      .map((zone) => ({ coordinates: zone.coordinates as [number, number][] }));
    const renderZones = focusZones.length > 0
      ? focusZones
      : siteZones.map((zone) => ({ coordinates: zone.coordinates as [number, number][] }));

    let cancelled = false;
    let timeoutId: number | undefined;
    let attemptIndex = 0;
    const retryDelaysMs = [750, 3500, 7500, 12000];
    // Tile controls finish one more internal camera update just after their
    // settled flag flips. Let that update drain, then own the final pose. Tile
    // streams can temporarily become unsettled without another useful React
    // transition, so retry on a bounded backoff until the pose sticks.
    const attemptFrame = () => {
      if (cancelled || hasUserInteractedRef.current) return;
      hasAppliedSettledViewRef.current = true;
      void frameZonesForRender(renderZones).then((framed) => {
        if (cancelled || hasUserInteractedRef.current) return;
        const isFinalAttempt = attemptIndex === retryDelaysMs.length - 1;
        if (framed && (isSceneSettled || isFinalAttempt)) {
          lastAutoFramedProjectKeyRef.current = projectZoneFocusKey;
          hasAppliedProjectViewRef.current = true;
          hasVisibleInitialCameraRef.current = true;
          setIsInitialCameraApplied(true);
          revealCanvasAfterPose();
          return;
        }
        if (isFinalAttempt) return;
        attemptIndex += 1;
        timeoutId = window.setTimeout(attemptFrame, retryDelaysMs[attemptIndex]);
      });
    };
    timeoutId = window.setTimeout(attemptFrame, retryDelaysMs[attemptIndex]);
    return () => {
      cancelled = true;
      if (timeoutId !== undefined) window.clearTimeout(timeoutId);
    };
  }, [
    frameZonesForRender,
    globeControlsReady,
    initialRevealFallbackReady,
    isSceneSettled,
    isTerrainReady,
    projectZoneFocusKey,
    revealCanvasAfterPose,
    sceneReady,
    siteZones,
  ]);

  // Drawing state â€” managed at DOM level
  const [drawingPoints, setDrawingPoints] = useState<number[][]>([]);
  const [drawingPointHeights, setDrawingPointHeights] = useState<number[]>([]);
  const [centerNearStartVertex, setCenterNearStartVertex] = useState(false);
  const [measurePoints, setMeasurePoints] = useState<number[][]>([]);
  const [measurePointHeights, setMeasurePointHeights] = useState<number[]>([]);
  const drawingPointsRef = useRef<number[][]>([]);
  const drawingPointHeightsRef = useRef<number[]>([]);
  const measurePointsRef = useRef<number[][]>([]);
  const measurePointHeightsRef = useRef<number[]>([]);
  const handleCanvasClickRef = useRef<((e: MouseEvent) => void) | null>(null);
  const finishDrawingRef = useRef<(() => void) | null>(null);
  const cleanupCanvasListenersRef = useRef<(() => void) | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const direct3DContextLostRef = useRef(false);
  const direct3DCapturePromiseRef = useRef<Promise<Direct3DCaptureBundle> | null>(null);
  const ignoreNextCanvasClickRef = useRef(false);
  const pointerDownRef = useRef<{ x: number; y: number } | null>(null);
  const draggedSincePointerDownRef = useRef(false);

  // Sync ref
  useEffect(() => { drawingPointsRef.current = drawingPoints; }, [drawingPoints]);
  useEffect(() => { drawingPointHeightsRef.current = drawingPointHeights; }, [drawingPointHeights]);
  useEffect(() => { measurePointsRef.current = measurePoints; }, [measurePoints]);
  useEffect(() => { measurePointHeightsRef.current = measurePointHeights; }, [measurePointHeights]);

  const clearMeasurePoints = useCallback(() => {
    measurePointsRef.current = [];
    measurePointHeightsRef.current = [];
    setMeasurePoints([]);
    setMeasurePointHeights([]);
  }, []);

  // Clear drawing when tool changes
  useEffect(() => {
    setDrawingPoints([]);
    setDrawingPointHeights([]);
    setCenterNearStartVertex(false);
    drawingPointsRef.current = [];
    drawingPointHeightsRef.current = [];
  }, [activeSitePlannerTool]);

  useEffect(() => {
    if (!measureModeActive) {
      clearMeasurePoints();
    }
  }, [clearMeasurePoints, measureModeActive]);

  // Cursor styling based on mode
  useEffect(() => {
    const cvs = canvasRef.current;
    if (!cvs) return;
    cvs.style.cursor = hasDrawingTool || measureModeActive ? 'crosshair' : '';
    return () => { cvs.style.cursor = ''; };
  }, [hasDrawingTool, measureModeActive]);

  const globeAIRenderViewport = useMemo<GlobeAIRenderViewport | null>(() => {
    if (!sceneReady || !canvasRef.current || !cameraRef.current) {
      return null;
    }

    const getViewportBounds = () => {
      const canvas = canvasRef.current;
      if (!canvas) {
        return fallbackRenderBounds;
      }

      const { width, height } = getCanvasViewportSize(canvas);
      const maxX = Math.max(width - 1, 0);
      const maxY = Math.max(height - 1, 0);
      const samplePoints: [number, number][] = [
        [0, 0],
        [width / 2, 0],
        [maxX, 0],
        [0, height / 2],
        [maxX, height / 2],
        [0, maxY],
        [width / 2, maxY],
        [maxX, maxY],
      ];
      const samples = samplePoints
        .map((point) => unprojectViewportPoint(point))
        .filter(
          (sample): sample is { lng: number; lat: number } => (
            Number.isFinite(sample.lng) && Number.isFinite(sample.lat)
          ),
        );

      if (samples.length < 2) {
        return fallbackRenderBounds;
      }

      let west = Infinity;
      let south = Infinity;
      let east = -Infinity;
      let north = -Infinity;

      for (const sample of samples) {
        west = Math.min(west, sample.lng);
        south = Math.min(south, sample.lat);
        east = Math.max(east, sample.lng);
        north = Math.max(north, sample.lat);
      }

      if (![west, south, east, north].every(Number.isFinite)) {
        return fallbackRenderBounds;
      }

      return { west, south, east, north };
    };

    return {
      getCanvas: () => canvasRef.current ?? document.createElement('canvas'),
      getBounds: () => {
        const bounds = getViewportBounds();
        return {
          getWest: () => bounds.west,
          getSouth: () => bounds.south,
          getEast: () => bounds.east,
          getNorth: () => bounds.north,
        };
      },
        getCenter: () => {
          const canvas = canvasRef.current;
          if (!canvas) {
            return { lng: focusLongitude, lat: focusLatitude };
          }

          const { width, height } = getCanvasViewportSize(canvas);
          return unprojectViewportPoint([width / 2, height / 2]);
        },
        getPitch: () => {
          const camera = cameraRef.current;
          if (!camera) {
            return pitchAngleRef.current;
          }

          const pitch = computePitchFromCamera(camera);
          return pitch ?? pitchAngleRef.current;
        },
        getBearing: () => {
          const canvas = canvasRef.current;
          const camera = cameraRef.current;
          if (!canvas || !camera) {
            return preferredView?.cameraPosition?.bearing ?? 0;
        }

        const { width, height } = getCanvasViewportSize(canvas);
        const center = unprojectViewportPoint([width / 2, height / 2]);
        const bearing = computeBearingFromCamera(
          center.lat,
          center.lng,
          camera.position,
          terrainElevationRef.current,
        );
        return bearing ?? preferredView?.cameraPosition?.bearing ?? 0;
      },
      project: projectLngLatToViewport,
      unproject: unprojectViewportPoint,
      getLayer: () => null,
      setLayoutProperty: () => undefined,
      setZoneOverlaysVisible: (visible: boolean) => setZoneOverlaysVisible(visible),
    };
  }, [
    fallbackRenderBounds,
    focusLatitude,
    focusLongitude,
    getCanvasViewportSize,
    projectLngLatToViewport,
    sceneReady,
    unprojectViewportPoint,
  ]);

  const waitForCurrentTiles = useCallback(
    () => waitForTilesSettled(tilesRendererRef.current),
    [],
  );

  const captureDirect3D = useCallback((): Promise<Direct3DCaptureBundle> => {
    if (direct3DCapturePromiseRef.current) {
      return Promise.reject(new Direct3DCaptureError(
        'busy',
        'A Direct 3D capture is already in progress.',
      ));
    }

    let trackedPromise: Promise<Direct3DCaptureBundle>;
    trackedPromise = (async () => {
      const renderer = rendererRef.current;
      const scene = sceneRef.current;
      const camera = cameraRef.current;
      const canvas = canvasRef.current;
      if (!renderer || !scene || !camera || !canvas || !canvas.isConnected) {
        throw new Direct3DCaptureError(
          'capture_failed',
          'The 3D globe is not ready for Direct capture.',
        );
      }
      if (direct3DContextLostRef.current || renderer.getContext().isContextLost()) {
        throw new Direct3DCaptureError(
          'context_lost',
          'The WebGL context is recovering. Wait for the 3D models to return, then capture again.',
        );
      }

      const tilesSettled = await waitForCurrentTiles();
      if (!tilesSettled) {
        throw new Direct3DCaptureError(
          'capture_failed',
          'The surrounding 3D tiles did not settle in time. Hold the camera still and try again.',
        );
      }
      if (
        rendererRef.current !== renderer
        || sceneRef.current !== scene
        || cameraRef.current !== camera
        || !canvas.isConnected
      ) {
        throw new Direct3DCaptureError(
          'capture_failed',
          'The 3D globe changed while preparing the capture. Try again after it stabilizes.',
        );
      }

      const previousOverlaysVisible = zoneOverlaysVisibleRef.current;
      const previousSelectedBuildingId = selectedBuildingIdRef.current;
      try {
        // Direct capture consumes the compiled 3D scene, never editable color
        // polygons or selection affordances. Two frames let React commit the
        // clean state before the deterministic off-screen passes begin.
        setZoneOverlaysVisible(false);
        setSelectedBuildingId(null);
        await new Promise<void>((resolve) => {
          requestAnimationFrame(() => requestAnimationFrame(() => resolve()));
        });
        if (direct3DContextLostRef.current || renderer.getContext().isContextLost()) {
          throw new Direct3DCaptureError(
            'context_lost',
            'The WebGL context was lost while preparing the Direct 3D capture.',
          );
        }
        return await captureDirect3DScene(renderer, scene, camera);
      } finally {
        setZoneOverlaysVisible(previousOverlaysVisible);
        setSelectedBuildingId(previousSelectedBuildingId);
      }
    })().finally(() => {
      if (direct3DCapturePromiseRef.current === trackedPromise) {
        direct3DCapturePromiseRef.current = null;
      }
    });
    direct3DCapturePromiseRef.current = trackedPromise;
    return trackedPromise;
  }, [waitForCurrentTiles]);

  // Emit stable's {canvas, camera, terrainHeight} contract when all three refs
  // are populated. Gated on globeAIRenderViewport so we only fire once the
  // scene is ready (the viewport memo guards on sceneReady + both refs).
  useEffect(() => {
    if (!onGlobeReady || !globeAIRenderViewport) return;
    const canvas = canvasRef.current;
    const camera = cameraRef.current;
    if (!canvas || !camera) return;
    onGlobeReady({
      canvas,
      camera,
      terrainHeight: terrainElevation,
      isSettled: isSceneSettled,
      waitForTilesSettled: waitForCurrentTiles,
      setBuildingModelsVisible,
      captureDirect3D,
    });
    // Dev-only handle for e2e/console camera control (hidden browser pane
    // can't reach React state; see memory: e2e browser pane tricks).
    if (import.meta.env.DEV) {
      const dbg = ((window as unknown as Record<string, unknown>).__globeDebug ??= {});
      Object.assign(dbg as object, {
        canvas,
        camera,
        terrainHeight: terrainElevation,
        isSceneSettled,
        waitForTilesSettled: waitForCurrentTiles,
        captureDirect3D,
      });
    }
  }, [captureDirect3D, globeAIRenderViewport, isSceneSettled, onGlobeReady, terrainElevation, waitForCurrentTiles]);

  // Prevent page scroll
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const handler = (e: WheelEvent) => { e.preventDefault(); };
    el.addEventListener('wheel', handler, { passive: false });
    return () => el.removeEventListener('wheel', handler);
  }, []);

  useEffect(() => {
    const el = containerRef.current;
    if (!el || typeof PointerEvent === 'undefined') return;

    const handlePointerDownCapture = (event: PointerEvent) => {
      if (isRedispatchingCtrlPointerRef.current || !shouldMirrorCtrlPointerAsShift(event)) {
        return;
      }

      const target = event.target;
      if (!(target instanceof EventTarget)) {
        return;
      }

      const mirroredEvent = new PointerEvent(event.type, {
        bubbles: true,
        cancelable: event.cancelable,
        composed: true,
        pointerId: event.pointerId,
        width: event.width,
        height: event.height,
        pressure: event.pressure,
        tangentialPressure: event.tangentialPressure,
        tiltX: event.tiltX,
        tiltY: event.tiltY,
        twist: event.twist,
        pointerType: event.pointerType,
        isPrimary: event.isPrimary,
        button: event.button,
        buttons: event.buttons,
        clientX: event.clientX,
        clientY: event.clientY,
        screenX: event.screenX,
        screenY: event.screenY,
        altKey: event.altKey,
        ctrlKey: event.ctrlKey,
        metaKey: event.metaKey,
        shiftKey: true,
      });

      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation?.();

      isRedispatchingCtrlPointerRef.current = true;
      try {
        target.dispatchEvent(mirroredEvent);
      } finally {
        isRedispatchingCtrlPointerRef.current = false;
      }
    };

    el.addEventListener('pointerdown', handlePointerDownCapture, { capture: true });
    return () => el.removeEventListener('pointerdown', handlePointerDownCapture, { capture: true });
  }, []);

  // Finish drawing
  const finishDrawing = useCallback(() => {
    const sanitized = sanitizeCoords(drawingPointsRef.current);
    const pts = linear ? sanitized : normalizePolygonDrawing(sanitized);
    if (!activeSitePlannerTool || pts.length < minPointsForTool(activeSitePlannerTool)) return;
    const drawnTerrainElevation = getRepresentativeTerrainHeight(
      drawingPointHeightsRef.current,
      terrainElevation,
    );
    const zoneProperties = buildZoneCreateProperties(
      activeSitePlannerTool,
      activeToolProperties,
      drawnTerrainElevation,
    );

    let finalCoords: number[][];
    if (linear) {
      const smoothed = smoothPolyline(pts);
      const width = (zoneProperties.width as number) || 10;
      finalCoords = sanitizeCoords(bufferLineToPolygon(smoothed, width));
    } else {
      finalCoords = [...pts];
    }

    if (finalCoords.length < 3) {
      console.warn('[Globe] Zone create skipped: not enough valid unique vertices', finalCoords.length);
      return;
    }

    onZoneCreated(finalCoords, activeSitePlannerTool, zoneProperties);
    setDrawingPoints([]);
    setDrawingPointHeights([]);
    setCenterNearStartVertex(false);
    drawingPointsRef.current = [];
    drawingPointHeightsRef.current = [];
    if (isMobileDrawingViewport()) {
      setActiveSitePlannerTool(null);
    }
  }, [activeSitePlannerTool, activeToolProperties, linear, onZoneCreated, setActiveSitePlannerTool, terrainElevation]);
  finishDrawingRef.current = finishDrawing;

  // Keyboard handler for drawing
  useEffect(() => {
    if (interactionPaused) return;
    if (!hasDrawingTool) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
      if ((e.target as HTMLElement)?.isContentEditable) return;

      if (e.key === 'Enter') finishDrawing();
      else if (e.key === 'Escape') {
        e.preventDefault();
        setDrawingPoints([]);
        setDrawingPointHeights([]);
        setCenterNearStartVertex(false);
        drawingPointsRef.current = [];
        drawingPointHeightsRef.current = [];
        if (isMobileDrawingViewport()) {
          setActiveSitePlannerTool(null);
        }
      }
      else if (
        (e.key === 'Backspace' || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z' && !e.shiftKey)) &&
        drawingPointsRef.current.length > 0
      ) {
        e.preventDefault();
        e.stopImmediatePropagation();
        const newPts = drawingPointsRef.current.slice(0, -1);
        const newHeights = drawingPointHeightsRef.current.slice(0, -1);
        drawingPointsRef.current = newPts;
        drawingPointHeightsRef.current = newHeights;
        setDrawingPoints(newPts);
        setDrawingPointHeights(newHeights);
      }
    };

    window.addEventListener('keydown', handleKeyDown, true);
    return () => window.removeEventListener('keydown', handleKeyDown, true);
  }, [finishDrawing, hasDrawingTool, interactionPaused, setActiveSitePlannerTool]);

  // Keyboard handler for quick measuring
  useEffect(() => {
    if (interactionPaused) return;
    if (!measureModeActive) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

      if (e.key === 'Escape') {
        e.preventDefault();
        clearMeasurePoints();
        onMeasureModeChange?.(false);
      } else if (e.key === 'Backspace' && measurePointsRef.current.length > 0) {
        e.preventDefault();
        const newPts = measurePointsRef.current.slice(0, -1);
        const newHeights = measurePointHeightsRef.current.slice(0, -1);
        measurePointsRef.current = newPts;
        measurePointHeightsRef.current = newHeights;
        setMeasurePoints(newPts);
        setMeasurePointHeights(newHeights);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [clearMeasurePoints, interactionPaused, measureModeActive, onMeasureModeChange]);

  // Selection-mode keyboard shortcuts (delete, escape, copy/paste, zone nudging)
  useEffect(() => {
    if (interactionPaused) return;
    if (hasDrawingTool || measureModeActive) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

      // Delete the selected generated 3D model, else the planning zone. Model
      // selection now co-selects its zone, so the model branch must win first —
      // Delete on a clicked model removes the model, never the zone under it.
      if (e.key === 'Delete' || (e.key === 'Backspace' && !e.metaKey && !e.ctrlKey)) {
        if (selectedBuildingId) {
          e.preventDefault();
          onBuildingDeleted?.(selectedBuildingId);
          setSelectedBuildingId(null);
        } else if (selectedZoneId) {
          e.preventDefault();
          _onZoneDeleted?.(selectedZoneId);
          onZoneSelected(null);
        }
        return;
      }

      // Escape â€” remove pegman or deselect zone
      if (e.key === 'Escape') {
        if (streetViewPegman?.position) {
          setStreetViewActive(false);
        } else if (selectedBuildingId) {
          setSelectedBuildingId(null);
        } else {
          onZoneSelected(null);
        }
        return;
      }

      // Arrow keys rotate street view pegman (when placed)
      if (streetViewPegman?.position) {
        if (e.key === 'ArrowLeft') {
          e.preventDefault();
          setStreetViewAngle((streetViewPegman.angle - 45 + 360) % 360);
          return;
        }
        if (e.key === 'ArrowRight') {
          e.preventDefault();
          setStreetViewAngle((streetViewPegman.angle + 45) % 360);
          return;
        }
      }

      // Copy (Ctrl+C / Cmd+C)
      if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
        if (selectedZoneId) {
          onCopyZone?.(selectedZoneId);
        }
        return;
      }

      // Paste (Ctrl+V / Cmd+V)
      if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
        if (canPasteZone) {
          onPasteZone?.();
        }
        return;
      }

      // Q/E rotate selected buildable zones around their centroid.
      const key = e.key.toLowerCase();
      if ((key === 'q' || key === 'e') && selectedZoneId) {
        const zone = siteZones.find(z => z.id === selectedZoneId);
        const coords = zone?.coordinates;
        if (zone && coords && coords.length >= 3 && isBuildingZoneType(zone.zone_type)) {
          e.preventDefault();
          markUserInteracted();
          const rotationDeg = key === 'e' ? 5 : -5;
          const newCoords = rotateCoordsAroundCentroid(
            coords,
            computeCentroid(coords),
            rotationDeg * DEG_TO_RAD,
          );
          onZoneUpdated(selectedZoneId, newCoords);
          return;
        }
      }

      // WASD / Arrow keys â€” nudge selected zone relative to the current view heading.
      const movement = getGlobeNavigationMovement(new Set([key]));
      if ((movement.forward !== 0 || movement.strafe !== 0) && selectedZoneId) {
        e.preventDefault();
        markUserInteracted();
        const zone = siteZones.find(z => z.id === selectedZoneId);
        if (zone) {
          const [centroidLng, centroidLat] = computeCentroid(zone.coordinates);
          const [lngDelta, latDelta] = getSelectedZoneKeyboardNudgeDelta(
            centroidLat,
            centroidLng,
            cameraRef.current,
            movement,
          );
          const newCoords = zone.coordinates.map(c => [c[0] + lngDelta, c[1] + latDelta]);
          onZoneUpdated(selectedZoneId, newCoords);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [canPasteZone, hasDrawingTool, interactionPaused, markUserInteracted, measureModeActive, onBuildingDeleted, onCopyZone, onPasteZone, onZoneCreated, onZoneSelected, onZoneUpdated, selectedBuildingId, selectedZoneId, siteZones, streetViewPegman?.angle, streetViewPegman?.position, _onZoneDeleted]);

  useEffect(() => {
    if (interactionPaused) return;
    if ((!hasDrawingTool && selectedZoneId) || streetViewPegman?.position) return;

    const navigationKeys = new Set([
      'w', 'a', 's', 'd',
      'arrowup', 'arrowdown', 'arrowleft', 'arrowright',
    ]);
    const keysDown = new Set<string>();
    let rafId = 0;

    const isEditableTarget = (target: EventTarget | null) => {
      const element = target as HTMLElement | null;
      const tag = element?.tagName;
      return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || !!element?.isContentEditable;
    };

    const tick = () => {
      const camera = cameraRef.current;
      if (!camera || keysDown.size === 0) {
        rafId = 0;
        return;
      }

      const { forward, strafe, vertical } = getGlobeNavigationMovement(keysDown);

      const didMove = translateGlobeCamera(
        camera,
        globeControlsRef.current,
        terrainEllipsoidRef.current,
        { forward, strafe, vertical },
      );

      if (didMove) {
        markUserInteracted();
      }

      rafId = requestAnimationFrame(tick);
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (isEditableTarget(e.target)) return;

      const key = e.key.toLowerCase();
      if (!navigationKeys.has(key)) return;

      if (key.startsWith('arrow') || ['w', 'a', 's', 'd'].includes(key)) {
        e.preventDefault();
      }

      keysDown.add(key);
      if (!rafId) {
        rafId = requestAnimationFrame(tick);
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      const key = e.key.toLowerCase();
      if (!navigationKeys.has(key)) return;
      keysDown.delete(key);
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
      if (rafId) {
        cancelAnimationFrame(rafId);
      }
    };
  }, [hasDrawingTool, interactionPaused, markUserInteracted, selectedZoneId, streetViewPegman?.position]);

  const updateCenterConnectionState = useCallback(() => {
    if (!hasDrawingTool || linear || !activeSitePlannerTool) {
      setCenterNearStartVertex(false);
      return;
    }

    const pts = drawingPointsRef.current;
    if (pts.length < minPointsForTool(activeSitePlannerTool)) {
      setCenterNearStartVertex(false);
      return;
    }

    const centerSurface = raycastSurfacePoint(0, 0);
    if (!centerSurface) {
      setCenterNearStartVertex(false);
      return;
    }

    setCenterNearStartVertex(isWithinPolygonCloseRadius(haversineDistance(centerSurface.lngLat, pts[0])));
  }, [activeSitePlannerTool, hasDrawingTool, linear, raycastSurfacePoint]);

  const addDrawingPointFromSurface = useCallback((surface: { lngLat: [number, number]; height: number }) => {
    if (!activeSitePlannerTool) return;

    const newPts = [...drawingPointsRef.current, surface.lngLat];
    const shouldFilterHeight = shouldFilterObjectTerrainHeight(activeSitePlannerTool);
    const tilesGroup = tilesRendererRef.current?.group;
    const drawingHeight = shouldFilterHeight && tilesGroup?.children?.length
      ? raycastObjectFilteredTerrainHeightAtLngLat(
        surface.lngLat[0],
        surface.lngLat[1],
        tilesGroup,
        new THREE.Raycaster(),
        surface.height,
      ) ?? surface.height
      : surface.height;
    const newHeights = [...drawingPointHeightsRef.current, drawingHeight];

    drawingPointsRef.current = newPts;
    drawingPointHeightsRef.current = newHeights;
    setDrawingPoints(newPts);
    setDrawingPointHeights(newHeights);
    requestAnimationFrame(updateCenterConnectionState);
  }, [activeSitePlannerTool, updateCenterConnectionState]);

  const placeCenterVertex = useCallback(() => {
    if (!activeSitePlannerTool) return;

    if (centerNearStartVertex && drawingPointsRef.current.length >= minPointsForTool(activeSitePlannerTool)) {
      finishDrawingRef.current?.();
      return;
    }

    const centerSurface = raycastSurfacePoint(0, 0);
    if (centerSurface) addDrawingPointFromSurface(centerSurface);
  }, [activeSitePlannerTool, addDrawingPointFromSurface, centerNearStartVertex, raycastSurfacePoint]);

  const undoDrawingPoint = useCallback(() => {
    if (drawingPointsRef.current.length === 0) return;
    const newPts = drawingPointsRef.current.slice(0, -1);
    const newHeights = drawingPointHeightsRef.current.slice(0, -1);
    drawingPointsRef.current = newPts;
    drawingPointHeightsRef.current = newHeights;
    setDrawingPoints(newPts);
    setDrawingPointHeights(newHeights);
    requestAnimationFrame(updateCenterConnectionState);
  }, [updateCenterConnectionState]);

  const cancelDrawing = useCallback(() => {
    setDrawingPoints([]);
    setDrawingPointHeights([]);
    setCenterNearStartVertex(false);
    drawingPointsRef.current = [];
    drawingPointHeightsRef.current = [];
    setActiveSitePlannerTool(null);
  }, [setActiveSitePlannerTool]);

  useEffect(() => {
    if (!hasDrawingTool) {
      setCenterNearStartVertex(false);
      return;
    }

    updateCenterConnectionState();
    const interval = window.setInterval(updateCenterConnectionState, 150);
    return () => window.clearInterval(interval);
  }, [drawingPoints.length, hasDrawingTool, updateCenterConnectionState]);

  // Canvas onPointerMissed â€” fires when click doesn't hit any R3F mesh
  // We use this + onCreated to handle globe clicks at the Canvas level
  const handleCanvasClick = useCallback((e: MouseEvent) => {
    if (interactionPaused) return;
    markUserInteracted();
    if (ignoreNextCanvasClickRef.current) {
      ignoreNextCanvasClickRef.current = false;
      return;
    }

    // Get canvas rect for NDC calculation
    const canvas = canvasRef.current ?? containerRef.current?.querySelector('canvas');
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const ndcX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const ndcY = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    const clickSurface = raycastSurfacePoint(ndcX, ndcY);
    if (!clickSurface) return;
    const { lngLat: clickLngLat, height: clickHeight } = clickSurface;

    if (measureModeActive) {
      const newPts = [...measurePointsRef.current, clickLngLat];
      const newHeights = [...measurePointHeightsRef.current, clickHeight];
      measurePointsRef.current = newPts;
      measurePointHeightsRef.current = newHeights;
      setMeasurePoints(newPts);
      setMeasurePointHeights(newHeights);
      return;
    }

    // Street view mode: place pegman on click
    if (!hasDrawingTool && streetViewPegman !== null) {
      setStreetViewPosition(clickLngLat, clickHeight);
      return;
    }

    // In select mode: check if click is inside any zone polygon using turf.js
    if (!hasDrawingTool) {
      const clickPt = turfPoint(clickLngLat);
      let hitZoneId: string | null = null;
      let hitZoneArea = Infinity;

      for (const zone of siteZones) {
        if (!zone.coordinates || zone.coordinates.length < 3) continue;
        try {
          const closed = [...zone.coordinates, zone.coordinates[0]];
          const poly = turfPolygon([closed]);
          if (booleanPointInPolygon(clickPt, poly)) {
            // Pick smallest zone if overlapping
            const area = geodesicArea(zone.coordinates);
            if (area < hitZoneArea) {
              hitZoneArea = area;
              hitZoneId = zone.id;
            }
          }
        } catch { /* skip invalid polygons */ }
      }

      if (hitZoneId) {
        // Zone selected
        onZoneSelected(hitZoneId);
      } else {
        onZoneSelected(null);
      }
      return;
    }

    if (isBuildingZoneType(activeSitePlannerTool)) {
      const clickPt = turfPoint(clickLngLat);
      let hitZoneId: string | null = null;
      let hitZoneArea = Infinity;

      for (const zone of siteZones) {
        if (!isBuildingZoneType(zone.zone_type) || !zone.coordinates || zone.coordinates.length < 3) continue;
        try {
          const closed = [...zone.coordinates, zone.coordinates[0]];
          const poly = turfPolygon([closed]);
          if (booleanPointInPolygon(clickPt, poly)) {
            const area = geodesicArea(zone.coordinates);
            if (area < hitZoneArea) {
              hitZoneArea = area;
              hitZoneId = zone.id;
            }
          }
        } catch { /* skip invalid polygons */ }
      }

      if (hitZoneId) {
        cancelDrawing();
        onZoneSelected(hitZoneId);
        return;
      }
    }

    // Clicking the visible first-vertex marker is the natural desktop gesture
    // for closing a polygon. Finish before appending another raycast point so
    // the stored ring cannot contain a tiny self-intersecting closing spike.
    if (
      !linear
      && drawingPointsRef.current.length >= minPointsForTool(activeSitePlannerTool)
      && isWithinPolygonCloseRadius(haversineDistance(clickLngLat, drawingPointsRef.current[0]))
    ) {
      finishDrawingRef.current?.();
      return;
    }

    const newPts = [...drawingPointsRef.current, clickLngLat];
    const shouldFilterHeight = shouldFilterObjectTerrainHeight(activeSitePlannerTool);
    const tilesGroup = tilesRendererRef.current?.group;
    const drawingHeight = shouldFilterHeight && tilesGroup?.children?.length
      ? raycastObjectFilteredTerrainHeightAtLngLat(
        clickLngLat[0],
        clickLngLat[1],
        tilesGroup,
        new THREE.Raycaster(),
        clickHeight,
      ) ?? clickHeight
      : clickHeight;
    const newHeights = [...drawingPointHeightsRef.current, drawingHeight];
    drawingPointsRef.current = newPts;
    drawingPointHeightsRef.current = newHeights;
    setDrawingPoints(newPts);
    setDrawingPointHeights(newHeights);
    requestAnimationFrame(updateCenterConnectionState);
  }, [activeSitePlannerTool, cancelDrawing, hasDrawingTool, interactionPaused, linear, markUserInteracted, measureModeActive, onZoneSelected, raycastSurfacePoint, setStreetViewPosition, siteZones, streetViewPegman, updateCenterConnectionState]);

  const handleZoneMeshClick = useCallback((zoneId: string) => {
    if (interactionPaused) return;
    if (hasDrawingTool || measureModeActive) return;
    // Street View pegman-drop mode: let the click fall through to the canvas
    // handler so the pin drops on the zone instead of selecting it.
    if (streetViewPegman !== null) return;
    ignoreNextCanvasClickRef.current = true;
    setSelectedBuildingId(null);
    onZoneSelected(zoneId);
  }, [hasDrawingTool, interactionPaused, measureModeActive, onZoneSelected, streetViewPegman]);

  const handleBuildingModelClick = useCallback((buildingId: string) => {
    if (interactionPaused || hasDrawingTool || measureModeActive) return;
    ignoreNextCanvasClickRef.current = true;
    // A generated model is a first-class handle onto its zone: select both so
    // the properties panel (type/floors/Quick Regenerate) and the polygon
    // transform affordances (move/reshape/rotate) light up together.
    const owningZone = siteZones.find((zone) => zone.building_id === buildingId);
    onZoneSelected(owningZone ? owningZone.id : null);
    setSelectedBuildingId(buildingId);
  }, [hasDrawingTool, interactionPaused, measureModeActive, onZoneSelected, siteZones]);

  useEffect(() => {
    if (!selectedBuildingId) return;
    if (!(buildings ?? []).some((building) => building.id === selectedBuildingId)) {
      setSelectedBuildingId(null);
    }
  }, [buildings, selectedBuildingId]);

  // Keep ref updated so onCreated closure always calls latest version
  handleCanvasClickRef.current = handleCanvasClick;

  // Cleanup canvas listeners on unmount/re-init
  useEffect(() => {
    return () => {
      if (cleanupCanvasListenersRef.current) {
        cleanupCanvasListenersRef.current();
        cleanupCanvasListenersRef.current = null;
      }
    };
  }, []);

  if (!API_KEY) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-900 text-white">
        <p className="text-sm text-gray-400">Missing VITE_GOOGLE_MAPS_API_KEY</p>
      </div>
    );
  }

  const initialCameraPose = useMemo(
    () => preferredCameraPose ?? computeCameraPose(initialView.lat, initialView.lng, initialView.altitude, terrainElevation),
    [initialView, preferredCameraPose, terrainElevation],
  );
  initialCameraPoseRef.current = initialCameraPose;
  const initialThreeCameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  if (!initialThreeCameraRef.current) {
    const camera = new THREE.PerspectiveCamera(75, 1, 1, 1e11);
    applyCameraPoseToCamera(camera, initialCameraPose);
    initialThreeCameraRef.current = camera;
  } else if (!cameraRef.current) {
    applyCameraPoseToCamera(initialThreeCameraRef.current, initialCameraPose);
  }
  const initialThreeCamera = initialThreeCameraRef.current;

  return (
    <div ref={containerRef} className="relative h-full w-full bg-black" style={{ overflow: 'hidden' }}>
      <Canvas
        style={{ visibility: isInitialCameraApplied ? 'visible' : 'hidden' }}
        camera={initialThreeCamera}
        gl={{ antialias: true, logarithmicDepthBuffer: true, preserveDrawingBuffer: true, stencil: true }}
        onPointerMissed={() => {
          if (!hasDrawingTool && !measureModeActive && !interactionPaused) {
            setSelectedBuildingId(null);
          }
        }}
        onCreated={({ gl, camera, scene }) => {
          canvasRef.current = gl.domElement;
          rendererRef.current = gl;
          sceneRef.current = scene;
          direct3DContextLostRef.current = gl.getContext().isContextLost();
          hideCanvasUntilPose();
          cameraRef.current = camera;
          applyCameraPoseToCamera(camera, initialCameraPoseRef.current ?? initialCameraPose, globeControlsRef.current);
          setSceneReady(true);

          // Attach pointer handlers directly to WebGL canvas for drawing
          const cvs = gl.domElement;

          // Remove previous listeners first (React StrictMode / hot-reload safety)
          if (cleanupCanvasListenersRef.current) {
            cleanupCanvasListenersRef.current();
            cleanupCanvasListenersRef.current = null;
          }

          const handleClick = (e: MouseEvent) => {
            if (draggedSincePointerDownRef.current) {
              draggedSincePointerDownRef.current = false;
              return;
            }
            // Every click adds a point â€” dblclick handler will pop the duplicate
            handleCanvasClickRef.current?.(e);
          };

          const handleDblClick = (e: MouseEvent) => {
            const isDrawingNow = useViewerStore.getState().activeSitePlannerTool !== null
              && drawingPointsRef.current.length > 0;
            if (!isDrawingNow) return;
            e.preventDefault();
            e.stopPropagation();
            // Remove the duplicate point added by the first click of the double-click
            if (drawingPointsRef.current.length > 0) {
              drawingPointsRef.current = drawingPointsRef.current.slice(0, -1);
              drawingPointHeightsRef.current = drawingPointHeightsRef.current.slice(0, -1);
              setDrawingPoints(drawingPointsRef.current);
              setDrawingPointHeights(drawingPointHeightsRef.current);
            }
            finishDrawingRef.current?.();
          };

          const handlePointerDown = (e: PointerEvent) => {
            markUserInteracted();
            pointerDownRef.current = { x: e.clientX, y: e.clientY };
            draggedSincePointerDownRef.current = false;
          };

          const handlePointerMove = (e: PointerEvent) => {
            const start = pointerDownRef.current;
            if (!start || draggedSincePointerDownRef.current) return;
            const dx = e.clientX - start.x;
            const dy = e.clientY - start.y;
            if ((dx * dx + dy * dy) > 36) draggedSincePointerDownRef.current = true; // 6px threshold â€” forgiving for globe orbiting
          };

          const handlePointerUp = () => {
            pointerDownRef.current = null;
          };

          const handleTrackpadWheel = (e: WheelEvent) => {
            if (!applyTrackpadZoom(e, globeControlsRef.current)) return;
            markUserInteracted();
            e.preventDefault();
            e.stopImmediatePropagation();
          };

          const handleWebGlContextLost = () => {
            direct3DContextLostRef.current = true;
            // Never suppress the editable massing while the GPU context is
            // unavailable. A second photoreal globe tab can exhaust the
            // browser's WebGL budget and otherwise leave only labels/outlines.
            setModeledBuildingIds(new Set());
            setLegoBuildingIds(new Set());
            setSelectedBuildingId(null);
          };

          const handleWebGlContextRestored = () => {
            direct3DContextLostRef.current = false;
            // Force fresh scene clones so cached LEGO/GLB resources are
            // uploaded into the restored context rather than retaining a
            // logically mounted but visually blank layer.
            setBuildingLayerRecoveryGeneration((generation) => generation + 1);
          };

          cvs.addEventListener('wheel', handleTrackpadWheel, { capture: true, passive: false });
          cvs.addEventListener('pointerdown', handlePointerDown);
          cvs.addEventListener('pointermove', handlePointerMove);
          cvs.addEventListener('pointerup', handlePointerUp);
          cvs.addEventListener('click', handleClick);
          cvs.addEventListener('dblclick', handleDblClick);
          cvs.addEventListener('webglcontextlost', handleWebGlContextLost);
          cvs.addEventListener('webglcontextrestored', handleWebGlContextRestored);

          cleanupCanvasListenersRef.current = () => {
            cvs.removeEventListener('wheel', handleTrackpadWheel, { capture: true });
            cvs.removeEventListener('pointerdown', handlePointerDown);
            cvs.removeEventListener('pointermove', handlePointerMove);
            cvs.removeEventListener('pointerup', handlePointerUp);
            cvs.removeEventListener('click', handleClick);
            cvs.removeEventListener('dblclick', handleDblClick);
            cvs.removeEventListener('webglcontextlost', handleWebGlContextLost);
            cvs.removeEventListener('webglcontextrestored', handleWebGlContextRestored);
          };
        }}
      >
        <GlobeDragProvider value={globeDragRef}>
        <CameraExposer cameraRef={cameraRef} />
        <PitchMonitor onPitchChange={setPitchAngle} />
        <FallbackPlaneSync controlsRef={globeControlsRef} />
        <color attach="background" args={['#dbeafe']} />
        <ambientLight intensity={1.35} />
        <hemisphereLight args={['#f8fbff', '#5b6775', 1.5]} />
        <directionalLight
          position={[8_000_000, 10_000_000, 7_000_000]}
          intensity={1.8}
          color="#fff7d6"
        />
        {/* Atmospheric fog — grounds the horizon and hides the infinite void */}
        <fog attach="fog" args={['#b8c8d8', 8000, 80000]} />
        {/* IBL for placed GLB models (PBR materials only) — tiles and zone
            overlays are unlit basic materials, so they're unaffected. */}
        {hasPlaceableModels && <Environment preset="city" background={false} />}
        <TilesRenderer>
          {/* autoRefreshToken: Google 3D Tiles sessions expire after a few hours;
              without it every tile fetch 400s (pale background polygons through
              the holes) until a full reload. Refreshes the session on 4xx. */}
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          <TilesPlugin plugin={GoogleCloudAuthPlugin} args={{ apiToken: API_KEY, useRecommendedSettings: true, autoRefreshToken: true } as any} />
          <TilesPlugin plugin={TileCompressionPlugin} />
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          <TilesPlugin plugin={GLTFExtensionsPlugin} args={{ dracoLoader: new DRACOLoader().setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.7/') } as any} />
          <TilesPlugin plugin={UpdateOnChangePlugin} />
          <TilesPlugin plugin={UnloadTilesPlugin} />
          <TilesPlugin plugin={TilesFadePlugin} />
          <TilesExposer tilesRef={tilesRendererRef} />
          <GlobeControls
            ref={handleGlobeControlsRef}
            maxAltitude={MAX_GLOBE_CAMERA_PITCH_DEGREES * DEG_TO_RAD}
            useFallbackPlane
          />
          <TilesAttributionOverlay />
          <SceneSettledMonitor onSettledChange={setIsSceneSettled} />
          <TileStencilPatcher zones={tileMaskZones} terrainHeight={terrainElevation} />
          <GlobeTileMaskLayer zones={tileMaskZones} terrainHeight={terrainElevation} />
          {/* Camera starts at project location via Canvas camera prop */}

          {/* Editable fills/outlines/labels can hide for a clean AI capture,
              while a generated park orthophoto stays mounted as authored
              proposal ground (alongside models, street sections and props). */}
          <group name="siteforge-direct3d-ground" userData={direct3DProposalUserData('ground')}>
            <GlobeZoneLayer
              zones={siteZones}
              selectedZoneId={interactionPaused ? null : selectedZoneId}
              terrainHeight={terrainElevation}
              onZoneClick={handleZoneMeshClick}
              selectionEnabled={!interactionPaused && !hasDrawingTool && !measureModeActive}
              suppressedBuildingIds={suppressedBuildingIds}
              legoPlacedBuildingIds={legoBuildingIds}
              planningOverlaysVisible={zoneOverlaysVisible}
            />
          </group>

          {/* The compiled site-boundary remainder is generated proposal
              content, not an editable polygon. Its classified ground lives on
              the prepared boundary surface; this layer adds the deterministic
              canopy placements that are safe outside every authored zone. */}
          <group name="siteforge-direct3d-landscape" userData={direct3DProposalUserData('landscape')}>
            {siteZones.flatMap((zone) => {
              const recipe = getResidualLandscapeRecipe(zone);
              if (!recipe?.placements.length) return [];
              return [(
                <group
                  key={`${zone.id}-${recipe.source_hash}`}
                  name={`siteforge-direct3d-landscape-${zone.id}`}
                  userData={direct3DInstanceUserData(
                    direct3DZoneInstanceDescriptor(zone.id, 'landscape'),
                  )}
                >
                  <GlobeResidualLandscapeLayer
                    zones={[zone]}
                    terrainHeight={terrainElevation}
                  />
                </group>
              )];
            })}
          </group>

          {/* Generated street sections are proposal content, not planning
              overlays. Keep them in clean captures alongside building models
              and park props so mixed plans retain their exact lane geometry. */}
          <group name="siteforge-direct3d-street" userData={direct3DProposalUserData('street')}>
            <GlobeStreetDetailLayer zones={siteZones} terrainHeight={terrainElevation} />
          </group>

          {/* Park-program structures (playgrounds/pavilions/bridges) — sibling
              of the zone-overlay group like the building models. Trees and
              benches stay render-only so they cannot collide with paths. */}
          <group name="siteforge-direct3d-park" userData={direct3DProposalUserData('park')}>
            <GlobeParkKitLayer zones={siteZones} terrainHeight={terrainElevation} />
          </group>

          {/* Generated 3D building models — sibling of the zone-overlay group
              on purpose: they're real massing and stay visible in AI-render
              captures. Conditional render (not `visible`) so toggling off
              unmounts the models and the prisms return automatically. */}
          <group name="siteforge-direct3d-building" userData={direct3DProposalUserData('building')}>
            {buildingModelsVisible && meshyBuildings.length > 0 && (
              <GlobeBuildingModelsLayer
                key={`meshy-models-${buildingLayerRecoveryGeneration}`}
                buildings={meshyBuildings}
                zones={siteZones}
                direct3DProposalBuildingIds={direct3DProposalBuildingIds}
                terrainHeight={terrainElevation}
                onLoadedIdsChange={handleModeledIdsChange}
                selectedBuildingId={selectedBuildingId}
                onBuildingClick={handleBuildingModelClick}
              />
            )}

            {/* Saved LEGO recipes and family-pending planned masses at the real
                footprint. Shares the 3D Models toggle with Meshy; real GLBs and
                LEGO recipes retain priority when a fallback is upgraded. */}
            {buildingModelsVisible && legoLayerBuildings.length > 0 && (
              <GlobeLegoAssemblyLayer
                key={`lego-models-${buildingLayerRecoveryGeneration}`}
                buildings={legoLayerBuildings}
                zones={siteZones}
                direct3DProposalBuildingIds={direct3DProposalBuildingIds}
                terrainHeight={terrainElevation}
                onLoadedIdsChange={handleLegoIdsChange}
                selectedBuildingId={selectedBuildingId}
                onBuildingClick={handleBuildingModelClick}
              />
            )}
          </group>

          <group name="siteforge-direct3d-editor-ui" userData={DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA}>
            {/* Drawing preview dots */}
            <DrawingDots
              points={drawingPoints}
              pointHeights={drawingPointHeights}
              terrainHeight={terrainElevation}
              linear={linear}
              filterObjectHeights={shouldFilterObjectTerrainHeight(activeSitePlannerTool)}
            />

            <MeasurementOverlay
              points={measurePoints}
              pointHeights={measurePointHeights}
              terrainHeight={terrainElevation}
            />

          {/* Edit mode â€” vertex handles when zone selected in Select mode */}
            {!interactionPaused && !hasDrawingTool && !measureModeActive && selectedZoneId && (() => {
              const zone = siteZones.find(z => z.id === selectedZoneId);
              return zone ? (
                <GlobeEditMode
                  zone={zone}
                  terrainHeight={terrainElevation}
                  onZoneUpdated={onZoneUpdated}
                  globeControlsRef={globeControlsRef}
                  onInteractionStart={markUserInteracted}
                />
              ) : null;
            })()}

          {/* Street view pegman */}
            {streetViewPegman?.position && (
              <GlobePegman
                position={streetViewPegman?.position as [number, number]}
                angle={streetViewPegman.angle}
                terrainHeight={streetViewPegman.terrainHeight ?? terrainElevation}
              />
            )}
          </group>
        </TilesRenderer>

        {/* Click handling is attached in onCreated (canvas click + dblclick listeners) */}
        </GlobeDragProvider>
      </Canvas>

      {!isInitialCameraApplied && (
        <div className="absolute inset-0 z-40 flex items-center justify-center bg-black text-white">
          <div className="flex flex-col items-center gap-3 rounded-xl border border-white/10 bg-gray-950/80 px-5 py-4 shadow-2xl backdrop-blur-sm">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-amber-400/25 border-t-amber-300" />
            <div className="text-center">
              <p className="text-sm font-semibold text-white">Preparing project view...</p>
              <p className="mt-1 text-xs text-white/55">
                {!isTerrainReady
                  ? 'Checking terrain height'
                  : !globeControlsReady
                    ? 'Starting globe controls'
                    : 'Loading nearby 3D tiles'}
              </p>
            </div>
          </div>
        </div>
      )}

      {measureModeActive && (
        <div className="absolute left-1/2 bottom-24 z-30 -translate-x-1/2 rounded-lg border border-sky-400/40 bg-gray-900/90 px-3 py-2 text-center text-xs text-white shadow-lg backdrop-blur-sm">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sky-200">Measure</span>
            <span className="text-white/75">
              {measurePoints.length >= 2
                ? `Total ${formatDistance(polylineLength(measurePoints))}`
                : measurePoints.length === 1
                  ? 'Place next point'
                  : 'Place first point'}
            </span>
            {measurePoints.length > 0 && (
              <button
                type="button"
                onClick={clearMeasurePoints}
                className="pointer-events-auto rounded-md bg-white/10 px-2 py-0.5 text-[11px] text-white/80 hover:bg-white/20 hover:text-white"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      )}

      {hasDrawingTool && (() => {
        const n = drawingPoints.length;
        const tool = activeSitePlannerTool!;
        const min = minPointsForTool(tool);
        const isLineTool = isLinearTool(tool);
        const canFinish = n >= min;
        const canConnect = !isLineTool && canFinish && centerNearStartVertex;
        const placeLabel = canConnect
          ? 'Connect & Finish'
          : n === 0
            ? 'Place First Vertex'
            : isLineTool
              ? 'Place Waypoint'
              : 'Place Vertex';

        return (
          <>
            <div className="pointer-events-none absolute left-1/2 top-1/2 z-40 -translate-x-1/2 -translate-y-1/2 sm:hidden">
              <div className={`h-8 w-8 rounded-full border-2 ${canConnect ? 'border-emerald-300 bg-emerald-400/20' : 'border-white/90 bg-black/15'} shadow-[0_0_0_1px_rgba(0,0,0,0.35),0_8px_24px_rgba(0,0,0,0.35)]`}>
                <div className="absolute left-1/2 top-[-10px] h-8 w-px -translate-x-1/2 bg-white/90" />
                <div className="absolute left-[-10px] top-1/2 h-px w-8 -translate-y-1/2 bg-white/90" />
              </div>
            </div>
            <div className="absolute inset-x-3 bottom-4 z-50 mx-auto max-w-[34rem] sm:hidden">
              <div
                className="grid grid-cols-3 gap-2 rounded-2xl border border-white/15 bg-gray-950/80 p-2 shadow-2xl backdrop-blur-md"
                onPointerDown={(event) => event.stopPropagation()}
                onPointerUp={(event) => event.stopPropagation()}
              >
                <button
                  type="button"
                  onClick={placeCenterVertex}
                  className={`col-span-3 min-h-12 rounded-xl px-3 py-2 text-sm font-black shadow-lg ${canConnect ? 'bg-emerald-400 text-slate-950 shadow-emerald-500/25' : 'bg-amber-500 text-slate-950 shadow-amber-500/25'}`}
                >
                  {placeLabel}
                </button>
                <button
                  type="button"
                  onClick={undoDrawingPoint}
                  disabled={n === 0}
                  className="min-h-11 rounded-xl bg-white px-3 py-2 text-xs font-semibold text-slate-950 shadow-lg disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-white/50"
                >
                  Undo
                </button>
                <button
                  type="button"
                  onClick={cancelDrawing}
                  className="min-h-11 rounded-xl bg-slate-800 px-3 py-2 text-xs font-semibold text-white shadow-lg ring-1 ring-white/10"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={finishDrawing}
                  disabled={!canFinish}
                  className="min-h-11 rounded-xl bg-amber-500 px-3 py-2 text-xs font-semibold text-slate-950 shadow-lg shadow-amber-500/25 disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-white/50 disabled:shadow-none"
                >
                  Finish
                </button>
              </div>
            </div>
          </>
        );
      })()}

      {/* Context-sensitive hints bar */}
      {hasDrawingTool && (() => {
        const n = drawingPoints.length;
        const tool = activeSitePlannerTool!;
        const label = getToolDisplayLabel(tool);
        const min = minPointsForTool(tool);
        const linear = isLinearTool(tool);

        let measurement = '';
        if (n >= 2 && linear) {
          measurement = formatDistance(polylineLength(drawingPoints));
        } else if (n >= 3 && !linear) {
          measurement = formatDrawingArea(polygonAreaM2(drawingPoints));
        }

        let mobileHint: string;
        if (n === 0) {
          mobileHint = `Center the crosshair, then tap Place First Vertex`;
        } else if (n < min) {
          mobileHint = linear
            ? `${n} waypoint${n > 1 ? 's' : ''} - need ${min} min - move under crosshair`
            : `${n} point${n > 1 ? 's' : ''} - need ${min} min - move under crosshair`;
        } else if (!linear && centerNearStartVertex) {
          mobileHint = `${n} points${measurement ? ` - ${measurement}` : ''} - near start vertex - connect to finish`;
        } else if (linear) {
          mobileHint = `${n} waypoint${n > 1 ? 's' : ''}${measurement ? ` - ${measurement}` : ''} - tap Finish when ready`;
        } else {
          mobileHint = `${n} points${measurement ? ` - ${measurement}` : ''} - move crosshair near start or tap Finish`;
        }

        let desktopHint: string;
        if (n === 0) {
          desktopHint = `Click to place first ${label} point | Drag to orbit | Scroll to zoom`;
        } else if (n < min) {
          desktopHint = `${n} point${n > 1 ? 's' : ''} - need ${min} min - Drag to orbit - Backspace to undo`;
        } else {
          desktopHint = `${n} points${measurement ? ` - ${measurement}` : ''} - Drag to orbit - Double-click or Enter to finish - Esc to cancel`;
        }

        return (
          <>
            <div className="absolute left-1/2 top-20 z-30 max-w-[90vw] -translate-x-1/2 rounded-lg bg-gray-900/90 px-4 py-2 text-center text-xs text-white backdrop-blur-sm border border-amber-500/30 sm:hidden">
              {mobileHint}
            </div>
            <div className="absolute left-1/2 bottom-24 z-30 hidden -translate-x-1/2 rounded-lg bg-gray-900/90 px-4 py-2 text-center text-xs text-white backdrop-blur-sm border border-amber-500/30 sm:block">
              {desktopHint}
            </div>
          </>
        );
      })()}

      {/* Street view hint */}
      {false && !hasDrawingTool && streetViewPegman && (
        <div className="absolute left-1/2 top-4 z-30 -translate-x-1/2 rounded-lg bg-amber-900/80 px-3 py-1.5 text-center text-[11px] text-amber-100 backdrop-blur-sm border border-amber-500/30">
          {streetViewPegman?.position
            ? 'Arrow keys to rotate view - Esc to remove pegman'
            : 'Click to place street view camera'}
        </div>
      )}

      {!hasDrawingTool && streetViewPegman && (
        <div className="absolute left-1/2 top-4 z-30 -translate-x-1/2 rounded-full border-2 border-[#151515] bg-[#fff9ec]/95 px-3 py-1.5 text-center text-[11px] font-black uppercase text-[#151515] shadow-[4px_4px_0_0_#151515] backdrop-blur-xl">
          {streetViewPegman?.position
            ? 'Arrow keys to rotate view | Esc to remove pegman'
            : 'Click to place street view camera'}
        </div>
      )}

      {/* Select mode hint */}
      {false && !hasDrawingTool && !streetViewPegman && (
        <div className="absolute left-1/2 top-4 z-30 -translate-x-1/2 rounded-lg bg-gray-900/70 px-3 py-1.5 text-center text-[11px] text-white/70 backdrop-blur-sm">
          {selectedZoneId
            ? 'Drag body to move - Drag vertices to reshape - Del to delete - Ctrl+C to copy'
            : 'Click zone to select - Scroll to zoom - Drag to orbit'}
        </div>
      )}

      {/* 3D Globe badge + pitch + LOD status â€” offset below back button */}
      {!hasDrawingTool && !streetViewPegman && !measureModeActive && (
        <div className="pointer-events-none absolute left-1/2 top-4 z-30 hidden -translate-x-1/2 rounded-full border-2 border-[#151515] bg-[#fff9ec]/95 px-3 py-1.5 text-center text-[11px] font-black text-[#151515]/70 shadow-[4px_4px_0_0_#151515] backdrop-blur-xl select-none sm:block">
          {selectedBuildingId && selectedZoneId
            ? '3D model selected | Edit type/floors in the panel, then Regenerate | Drag body/vertices or amber handle to move/reshape/rotate | Delete removes the model | Esc to deselect'
            : selectedBuildingId
            ? '3D model selected | Delete/Backspace to remove | Esc to deselect'
            : selectedZoneId
            ? 'Drag body to move | Drag vertices to reshape | Drag amber handle or Q/E to rotate buildings | WASD/Arrows to nudge relative to view | Ctrl+C/Ctrl+V or toolbar Copy/Paste | Delete to remove'
            : 'Click a zone or 3D model to select | Drag to orbit | Scroll to zoom | WASD/Arrows to move | Shift/Ctrl to rise/lower'}
        </div>
      )}

      <div className="absolute top-14 left-4 z-20 flex items-center gap-2">
        <div className="rounded-full border-2 border-[#151515] bg-[#c9ff3d] px-3 py-1.5 shadow-[3px_3px_0_0_#151515] backdrop-blur-xl">
          <span className="text-[11px] font-black uppercase text-[#151515]">3D Globe</span>
        </div>
        <div className={`rounded-full border-2 border-[#151515] bg-[#fff9ec]/95 px-3 py-1.5 text-[11px] font-black uppercase shadow-[3px_3px_0_0_#151515] backdrop-blur-xl ${cameraElevationBadge.textClass}`}>
          {cameraElevation}° {cameraElevationBadge.label}
        </div>
        {!isSceneSettled && (
          <div className="flex items-center gap-1.5 rounded-full border-2 border-[#151515] bg-[#fff9ec]/95 px-3 py-1.5 shadow-[3px_3px_0_0_#151515] backdrop-blur-xl">
            <div className="h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
            <span className="text-[10px] font-black uppercase text-[#151515]/70">Loading tiles...</span>
          </div>
        )}
        {siteZones.length > 0 && (
          <button
            type="button"
            onClick={() => {
              void frameZonesForRender(siteZones.map((zone) => ({
                coordinates: zone.coordinates as [number, number][],
              })));
            }}
            className="rounded-full border-2 border-[#151515] bg-[#fff9ec]/95 px-3 py-1.5 text-[11px] font-black uppercase text-[#151515] shadow-[3px_3px_0_0_#151515] backdrop-blur-xl transition hover:bg-white"
            title="Focus the camera on this development"
          >
            Focus plan
          </button>
        )}
        {hasPlaceableModels && (
          <button
            type="button"
            onClick={handleBuildingModelsVisibilityToggle}
            aria-pressed={buildingModelsVisible}
            className={`rounded-full border-2 border-[#151515] px-3 py-1.5 text-[11px] font-black uppercase shadow-[3px_3px_0_0_#151515] backdrop-blur-xl transition ${
              buildingModelsVisible
                ? 'bg-[#c9ff3d] text-[#151515]'
                : 'bg-[#fff9ec]/95 text-[#151515]/50'
            }`}
            title={buildingModelsVisible ? 'Hide generated 3D models' : 'Show generated 3D models'}
          >
            {buildingModelsVisible ? '3D Models On' : 'Show 3D Models'}
          </button>
        )}
        {siteZones.some((zone) => zone.zone_type !== 'site_boundary') && (
          <button
            type="button"
            onClick={() => setZoneOverlaysVisible((visible) => !visible)}
            className={`rounded-full border-2 border-[#151515] px-3 py-1.5 text-[11px] font-black uppercase shadow-[3px_3px_0_0_#151515] backdrop-blur-xl transition ${
              zoneOverlaysVisible
                ? 'bg-[#fff9ec]/95 text-[#151515]'
                : 'bg-[#c9ff3d] text-[#151515]'
            }`}
            title={zoneOverlaysVisible ? 'Hide planning polygons for a clean 3D view' : 'Show editable planning polygons'}
          >
            {zoneOverlaysVisible ? 'Plan Overlay' : 'Clean 3D'}
          </button>
        )}
      </div>
    </div>
  );
}
