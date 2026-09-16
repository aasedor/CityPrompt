import { BuildingGroundProblems } from './BuildingGroundProblems';
import { useContextPresentation } from '@/features/context/useContextPresentation';
import { ContextControls } from '@/features/context/ContextControls';
import { SurveyGroundSurface } from '@/features/context/SurveyGroundSurface';
import { GaussianContextLayer } from '@/features/context/GaussianContextLayer';
import { AlternateContextLayer, GoogleContextVisibility } from '@/features/context/ContextLayers';
import { contextPilotCaptureProblem } from '@/features/context/contextProvider';
import { assetForZone } from '@/features/pickPlace/catalogue';
import { projectedFrameFraction } from './projectFrameHeight';
/**
 * GlobeSitePlannerMap.tsx â€” Google Earth-style 3D globe with SiteForge tools.
 *
 * Full-screen globe with drawing handled at the DOM level (not inside R3F).
 * GlobeControls always enabled â€” drawing uses click vs drag detection.
 */

import { useContext, useEffect, useRef, useState, useCallback, useMemo } from 'react';
import * as THREE from 'three';
import { GlobePlacementPreview } from '@/features/pickPlace/GlobePlacementPreview';
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
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { useViewerStore } from '@/store';
import { GlobeReferenceLayer } from '@/features/referenceLayers/GlobeReferenceLayer';
import { EMPTY_TRANSPORT, type ExistingTransport } from '@/features/referenceLayers/existingTransport';
import type { ReferenceLayer } from '@/features/referenceLayers/api';
import { useRoadNetwork } from '@/hooks/useRoadNetwork';
import { roadDisplayZones, snapRoadEndpoints } from '@/utils/proceduralRoadNetwork';
import { GlobeZoneLayer } from './GlobeZoneLayer';
import { streetGroundCaptureStatus } from './streetGroundCapture';
import { streetSurfaceMaskZone } from './streetSurfaceMask';
import { GroundReviewPanel } from './GroundReviewPanel';
import { PlacementControls } from '@/features/pickPlace/PlacementControls';
import { SharedSiteGroundProvider, INACTIVE_SHARED_SITE_GROUND, type SharedSiteGroundState } from './SharedSiteGroundProvider';
import { captureSharedGround, assertSharedGroundUnchanged, groundReadinessMessage } from './sharedGroundCapture';
import { GlobeBuildingModelsLayer } from './GlobeBuildingModelsLayer';
import { GlobeLegoAssemblyLayer, type LegoGroundingIssue } from './GlobeLegoAssemblyLayer';
import { snapStreetEnds } from '@/features/pickPlace/streetSnapping';
import {
  excludeLegoStackBuildings,
  hasLegoRecipe,
  hasPlannedMassing,
  renderableLegoBuildingIds,
} from './legoGlobePlacement';
import { GlobeStreetDetailLayer } from './GlobeStreetDetailLayer';
import { GlobeParkKitLayer } from './GlobeParkKitLayer';
import { applyManualParkAccessSnapshot, resolveManualParkAccess } from './parkAccessConnections';
import { resolvePedestrianConnections } from '@/features/pickPlace/pedestrianConnections';
import { GlobePedestrianConnections } from './GlobePedestrianConnections';
import { GlobeTerraces } from './GlobeTerraces';
import { buildTerraceScene } from './terraceScene';
import { readParkTerrain, type ParkTerrainProfile } from './parkTerrain';
import { ParkAssemblyGroundProvider } from './ParkAssemblyGround';
import { AutomaticParkGround, type SaveParkGround, type ParkAlignment } from './AutomaticParkGround';
import { GlobeResidualLandscapeLayer } from './GlobeResidualLandscapeLayer';
import { GlobeStreetRenderProfile } from './GlobeStreetRenderProfile';
import { getResidualLandscapeRecipe } from './residualLandscape';
import { GlobeEditMode } from './GlobeEditMode';
import { useCreateGlobeDragRef, GlobeDragProvider } from './useGlobeDragRef';
import { GlobePegman } from './GlobePegman';
import { authoredCameraGround } from './authoredCameraGround';
import { SceneSettledMonitor } from './useSceneSettled';
import {
  holdTileQueueUpdates,
  type SceneTileRenderer,
  waitForCaptureTileReadiness,
  waitForVisibleTileCoverage,
} from './tileLoadReadiness';
import {
  estimateProjectFrameHeight,
  PROJECT_FRAME_MAX_HEIGHT_M,
  PROJECT_FRAME_MIN_HEIGHT_M,
  PROJECT_FRAME_TARGET_FRACTION,
} from './projectFrameHeight';
import {
  getFrameableProjectCoordinates,
  runProjectFrameRetry,
  shouldUsePassiveGlobeHeightCorrection,
} from './projectFrameRetry';
import { TileStencilPatcher } from './TileStencilPatcher';
import { GlobeTileMaskLayer } from './GlobeTileMaskLayer';
import {
  getPreparedSiteBoundaryIds,
  getActiveBoundaryTileMaskPreference,
  resolvePreparedSiteTerrainHeight,
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
import {
  buildTerrainRelativeDrawingVertices,
  isWithinPolygonCloseRadius,
  normalizePolygonDrawing,
} from './drawingGeometry';
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
  type Direct3DCaptureOptions,
} from './direct3dCapture';
import {
  cinematicRouteProgress,
  normalizedVideoPointToNdc,
  resampleVideoRoute,
  stableNearFieldTerrainHeight,
  videoRouteSurfaceHeight,
  videoGeometryPassProfile,
  type VideoRouteCaptureRequest,
  type VideoRouteCaptureResult,
} from '../videoRouteControls';
import {
  captureDeterministicVideo,
  getCenterCropRect,
} from '../deterministicVideoCapture';
import { assertNearFieldVideoSourceQuality } from '../videoSourceQuality';
import {
  applyVideoFrameProjection,
  buildVideoWarmupFrames,
  restoreVideoFrameProjection,
  validateVideoRenderProfile,
  videoRenderQualityProfile,
} from '../videoRenderQuality';
import {
  applyStreetCameraProjection,
  applyStreetRoutePose,
  restoreStreetCameraProjection,
} from './streetRenderProfile';
import { inspectStreetRenderReadiness } from './streetRenderReadiness';
import { getArchitecturalLightingProfile } from './rlasmPresentation';

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

interface SceneTilesFadePlugin {
  fadeDuration: number;
}

interface SceneUnloadTilesPlugin {
  delay: number;
  bytesTarget: number;
  estimatedGpuBytes: number;
}

function applyCaptureTextureAnisotropy(
  scene: THREE.Scene,
  anisotropy: number,
): () => void {
  const previous = new Map<THREE.Texture, number>();
  scene.traverse((object) => {
    const materialValue = (object as THREE.Mesh).material;
    const materials = Array.isArray(materialValue) ? materialValue : materialValue ? [materialValue] : [];
    materials.forEach((material) => {
      Object.values(material).forEach((value) => {
        if (!(value instanceof THREE.Texture) || previous.has(value)) return;
        previous.set(value, value.anisotropy);
        if (value.anisotropy < anisotropy) {
          value.anisotropy = anisotropy;
          value.needsUpdate = true;
        }
      });
    });
  });
  return () => {
    previous.forEach((value, texture) => {
      texture.anisotropy = value;
      texture.needsUpdate = true;
    });
  };
}

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
  pitchDegrees: number = DEFAULT_INITIAL_CAMERA_PITCH_DEGREES,
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
  const cameraUp = pitchDegrees === 0 ? north.clone() : normal;
  const horizontalOffset = heightAboveGroundMeters * Math.tan(pitchDegrees * DEG_TO_RAD);
  const northOffset = horizontalOffset / Math.hypot(1, eastSkew);
  cameraPos.add(north.multiplyScalar(-northOffset));
  cameraPos.add(east.multiplyScalar(northOffset * eastSkew));

  // cameraUp defaults to the surface normal when no handoff up-vector is
  // supplied; returning it here keeps the type uniform across all return
  // paths so callers can read pose.cameraUp without TypeScript flagging
  // it as missing on this branch.
  return { cameraPos, surfacePos, normal, cameraUp };
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
    if (import.meta.env.DEV) {
      const debug = ((window as unknown as Record<string, unknown>).__globeDebug ??= {}) as Record<string, unknown>;
      debug.tiles = tiles;
      return () => { if (debug.tiles === tiles) delete debug.tiles; };
    }
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
function DrawingPreviewFill({
  points,
  pointHeights,
  terrainHeight,
}: {
  points: number[][];
  pointHeights: number[];
  terrainHeight: number;
}) {
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
    const verts = buildTerrainRelativeDrawingVertices(
      points,
      pointHeights,
      terrainHeight,
      DRAWING_FILL_LIFT_METERS,
    );
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
    const idx: number[] = [];
    for (const tri of indices) idx.push(tri[0], tri[1], tri[2]);
    g.setIndex(idx);
    return { geo: g, centroid };
  }, [pointHeights, points, terrainHeight]);

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
      {!linear && (
        <DrawingPreviewFill
          points={points}
          pointHeights={sampledPointHeights}
          terrainHeight={previewHeight}
        />
      )}

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
        const outVerts = buildTerrainRelativeDrawingVertices(
          points,
          sampledPointHeights,
          previewHeight,
          DRAWING_OUTLINE_LIFT_METERS,
          !linear,
        );
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
  onPrepareGround?: (zoneId: string, clear: boolean, height?: number, edges?: import('./preparedSiteEdges').PreparedEdgeProfile | null) => Promise<void>;
  onFollowParkTerrain?: (profiles: Record<string, ParkTerrainProfile>) => Promise<void>;
  onAutoParkTerrain?: SaveParkGround;
  parkGroundPaused?: boolean;
  placementDraft?: import('@/features/pickPlace/GlobePlacementPreview').PlacementDraft | null;
  onPlacementDraftChange?: (draft: import('@/features/pickPlace/GlobePlacementPreview').PlacementDraft) => void;
  onPlaceAsset?: (lngLat: [number, number], height: number) => void;
  onCancelPlacement?: () => void;
  referenceLayers?: ReferenceLayer[];
  transportContext?: ExistingTransport;
  latitude?: number;
  longitude?: number;
  preferredView?: GlobePreferredView;
  siteZones: SiteZone[];
  /** Full editor inventory: hidden objects and local drafts constrain access. */
  allSiteZones?: SiteZone[];
  /** Project buildings — those with generated GLBs get placed on the globe. */
  buildings?: Building[];
  massingFeatures?: unknown[];
  onZoneCreated: (coordinates: number[][], zoneType: SiteZoneType, properties?: SiteZoneProperties) => boolean | void;
  onZoneUpdated: (zoneId: string, coordinates: number[][]) => boolean | void;
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
    captureDirect3D?: (options?: {
      skipTileWait?: boolean;
      includeGeometryPasses?: boolean;
      maxLongEdge?: number;
    }) => Promise<Direct3DCaptureBundle>;
    /** Run a street-level capture with scene hygiene: hides the pegman marker,
     *  and — when authored 3D building models are present ('model3d') — hides
     *  zone overlays, deselects buildings, and forces models visible so the
     *  capture shows the design, not editor affordances. Without models
     *  ('context3d') the zone overlays are forced visible instead, because
     *  they are the intervention markers the prompt references. Restores all
     *  prior visibility state afterwards. */
    withStreetCaptureScene?: <T>(fn: (kind: 'model3d' | 'context3d') => Promise<T>) => Promise<T>;
    /** Full Direct 3D pass stack (beauty/class-ID/instance-ID) from the
     *  CURRENT camera with street-relaxed coverage bounds. Returns null on
     *  failure so callers can fall back to a plain screenshot. */
    captureStreetDirect3D?: (options?: Direct3DCaptureOptions) => Promise<Direct3DCaptureBundle | null>;
    /** Capture six deterministic route views and an exact 8-second browser
     *  preview of the same camera motion for Omni control inputs. */
    captureVideoRouteControls?: (request: VideoRouteCaptureRequest) => Promise<VideoRouteCaptureResult>;
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
  placementDraft,
  onPlacementDraftChange,
  onPrepareGround,
  onFollowParkTerrain,
  onAutoParkTerrain,
  parkGroundPaused = false,
  onPlaceAsset,
  onCancelPlacement,
  referenceLayers = [],
  transportContext = EMPTY_TRANSPORT,
  latitude: _latitude = 51.045,
  longitude: _longitude = -114.07,
  preferredView,
  siteZones,
  allSiteZones = siteZones,
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
  const roadNetwork = useRoadNetwork(siteZones);
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
  const referenceOverlayGroup = useRef<THREE.Group>(null);
  const [isSceneSettled, setIsSceneSettled] = useState(false);
  // The loading badge can release once visible context is usable; capture
  // continues to rely on the stricter scene-settled signal below.
  const [areTilesDisplayReady, setAreTilesDisplayReady] = useState(false);
  const [sharedGroundState, setSharedGroundState] = useState<SharedSiteGroundState>(INACTIVE_SHARED_SITE_GROUND);
  const [showGroundReview, setShowGroundReview] = useState(false);
  const [showBuildingGroundProblems, setShowBuildingGroundProblems] = useState(false);
  const contextPresentation = useContextPresentation(allSiteZones);
  const contextPresentationRef = useRef(contextPresentation);
  contextPresentationRef.current = contextPresentation;
  const [placementProblemMessage, setPlacementProblemMessage] = useState<string | null>(null);
  const sharedGroundRef = useRef(sharedGroundState);
  const [legoGroundingIssues, setLegoGroundingIssues] = useState<LegoGroundingIssue[]>([]);
  const [modelGroundingIssues, setModelGroundingIssues] = useState<LegoGroundingIssue[]>([]);
  const buildingGroundingIssues = useMemo(() => [...legoGroundingIssues, ...modelGroundingIssues], [legoGroundingIssues, modelGroundingIssues]);
  const buildingGroundingIssuesRef = useRef(buildingGroundingIssues);
  buildingGroundingIssuesRef.current = buildingGroundingIssues;
  const pendingGroundBuildingsRef = useRef<string[]>([]);
  const handleGroundingIssuesChange = useCallback((issues: LegoGroundingIssue[]) => {
    setLegoGroundingIssues(issues);
  }, []);
  const handleSharedGroundChange = useCallback((state: SharedSiteGroundState) => {
    sharedGroundRef.current = state;
    setSharedGroundState(state);
  }, []);
  const terrainZonesRef = useRef(siteZones);
  terrainZonesRef.current = siteZones;
  const [parkAlignment, setParkAlignment] = useState<ParkAlignment>({ pending: false, needsAttention: false, retry: () => {} });
  const parkAlignmentRef = useRef(parkAlignment);
  parkAlignmentRef.current = parkAlignment;
  const waitForSharedGround = useCallback(async () => {
    const context = contextPresentationRef.current;
    const contextProblem = contextPilotCaptureProblem(context.provider, context.requested);
    if (contextProblem) throw new Direct3DCaptureError('capture_failed', contextProblem);
    const parkDeadline = performance.now() + 45000;
    while (parkAlignmentRef.current.pending && !parkAlignmentRef.current.needsAttention && performance.now() < parkDeadline) {
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    if (parkAlignmentRef.current.pending) throw new Error('Park alignment is still updating. Your design is safe; keep working and try the render once alignment finishes.');
    if (terrainZonesRef.current.some(zone => zone.properties?.park_terrain && !readParkTerrain(zone))) {
      throw new Error('Park alignment is updating automatically. Your design is safe; try the render once it finishes.');
    }
    const deadline = performance.now() + 45_000;
    while ((sharedGroundRef.current.status === 'sampling'
      || streetGroundCaptureStatus(sceneRef.current) === 'sampling'
      || (sharedGroundRef.current.status === 'ready' && pendingGroundBuildingsRef.current.length > 0
        && !buildingGroundingIssuesRef.current.some((issue) => issue.reason !== 'ground_not_ready')))
      && performance.now() < deadline) {
      await new Promise((resolve) => setTimeout(resolve, 200));
    }
    if (streetGroundCaptureStatus(sceneRef.current) !== 'ready') {
      throw new Error('The road connection is still aligning with the ground. Keep your design; check its position if alignment does not finish.');
    }
    const snapshot = captureSharedGround(sharedGroundRef.current);
    if (snapshot && (pendingGroundBuildingsRef.current.length > 0 || buildingGroundingIssuesRef.current.length > 0)) {
      if (buildingGroundingIssuesRef.current.some((issue) => issue.reason === 'foundation_exceeds_3m')) {
        throw new Error('The site is too uneven beneath a building for automatic grounding. Choose a flatter placement before rendering.');
      }
      throw new Error(`These buildings are not ready at ground level: ${pendingGroundBuildingsRef.current.join(', ') || 'check the marked building'}. Check their placement before rendering.`);
    }
    return snapshot;
  }, []);
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
  const [captureOverlaysHidden, setCaptureOverlaysHidden] = useState(false);
  const zoneOverlaysVisibleRef = useRef(true);
  zoneOverlaysVisibleRef.current = zoneOverlaysVisible;
  const parkAccessSnapshot = useMemo(() => resolveManualParkAccess(
    allSiteZones, {}, siteZones.filter((zone) => zone.zone_type === 'road').map((zone) => zone.id), transportContext,
  ), [allSiteZones, siteZones, transportContext]);
  const parkAccessSnapshotRef = useRef(parkAccessSnapshot);
  const pedestrianConnections = useMemo(() => resolvePedestrianConnections(allSiteZones, siteZones.map(zone=>zone.id)), [allSiteZones, siteZones]);
  parkAccessSnapshotRef.current = parkAccessSnapshot;
  const hasLocalDraftsRef = useRef(false);
  hasLocalDraftsRef.current = allSiteZones.some((zone) => zone.id.startsWith('temp-'));
  const connectedSceneZones = useMemo(() => {
    const visibleIds = new Set(siteZones.map((zone) => zone.id));
    return applyManualParkAccessSnapshot(allSiteZones, parkAccessSnapshot, transportContext).filter((zone) => visibleIds.has(zone.id));
  }, [allSiteZones, parkAccessSnapshot, siteZones, transportContext]);
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
  const buildingModelsVisibleRef = useRef(true);
  buildingModelsVisibleRef.current = buildingModelsVisible;
  const [modeledBuildingIds, setModeledBuildingIds] = useState<Set<string>>(() => new Set());
  const [legoBuildingIds, setLegoBuildingIds] = useState<Set<string>>(() => new Set());
  // Street-level capture hygiene: the pegman marker + view cone sit exactly
  // where the capture camera stands, so they photobomb every street capture
  // unless hidden for the duration.
  const [streetCapturePegmanHidden, setStreetCapturePegmanHidden] = useState(false);
  // A deterministic authored-scene profile. The proposal uses the original
  // GLBs, PBR materials, public realm and vegetation, while Google Tiles stay
  // visible outside the existing project-boundary replacement mask.
  const [streetRenderProfileActive, setStreetRenderProfileActive] = useState(false);
  // Whether the scene holds authored 3D building models (compiled community,
  // LEGO stacks, or placed GLBs) — decides whether a street capture shows the
  // design itself ('model3d') or only existing context + overlays ('context3d').
  const streetCaptureHas3DModelsRef = useRef(false);
  streetCaptureHas3DModelsRef.current =
    hasCompiledCommunity3D || modeledBuildingIds.size > 0 || legoBuildingIds.size > 0;
  const [buildingLayerRecoveryGeneration, setBuildingLayerRecoveryGeneration] = useState(0);
  const [selectedBuildingId, setSelectedBuildingId] = useState<string | null>(null);
  const selectedBuildingIdRef = useRef<string | null>(null);
  selectedBuildingIdRef.current = selectedBuildingId;
  // Zone overlays can legitimately win the pointer race against the model
  // beneath them. Treat the selected zone's generated building as selected
  // for render-detail budgeting too, so inspecting a footprint always
  // promotes its authored LEGO family instead of leaving a massing proxy.
  const selectedRenderedBuildingId = selectedBuildingId
    ?? siteZones.find((zone) => zone.id === selectedZoneId)?.building_id
    ?? null;
  const selectedInspectionZone = useMemo(
    () => siteZones.find((zone) => (
      zone.id === selectedZoneId
      || (selectedRenderedBuildingId != null && zone.building_id === selectedRenderedBuildingId)
    )) ?? null,
    [selectedRenderedBuildingId, selectedZoneId, siteZones],
  );
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
      || hasPlannedMassing(building)
    )),
    [buildings],
  );
  const direct3DProposalBuildingIds = useMemo(
    () => getCurrentCommunity3DBuildingIds(siteZones, buildings ?? []),
    [buildings, siteZones],
  );
  pendingGroundBuildingsRef.current = buildingModelsVisible && sharedGroundState.status !== 'inactive'
    ? [...legoLayerBuildings, ...meshyBuildings.filter((building) => Boolean(building.lod_urls?.['0'] ?? building.model_url))]
      .filter((building) => direct3DProposalBuildingIds.has(building.id)
        && !legoBuildingIds.has(building.id) && !modeledBuildingIds.has(building.id))
      .map((building) => building.name || 'Unnamed building') : [];
  const savedRenderableLegoBuildingIds = useMemo(
    () => renderableLegoBuildingIds(buildings ?? []),
    [buildings],
  );
  const hasPlaceableModels = Boolean(buildings?.some((b) => b.lod_urls?.['0'] ?? b.model_url))
    || legoLayerBuildings.length > 0;
  const architecturalLighting = useMemo(
    () => getArchitecturalLightingProfile(buildings),
    [buildings],
  );
  // Prism suppression + outward "has real 3D massing" set = Meshy ∪ LEGO.
  const suppressedBuildingIds = useMemo(() => {
    const merged = new Set(modeledBuildingIds);
    legoBuildingIds.forEach((id) => merged.add(id));
    // A valid saved recipe durably replaces the planning prism while 3D is
    // enabled. Loader callbacks may reset during hot reload or a WebGL layer
    // handoff, but they must never resurrect an opaque box behind the GLB.
    if (buildingModelsVisible) {
      savedRenderableLegoBuildingIds.forEach((id) => merged.add(id));
    }
    return merged;
  }, [buildingModelsVisible, legoBuildingIds, modeledBuildingIds, savedRenderableLegoBuildingIds]);
  const preparedSiteBoundaryIds = useMemo(
    () => getPreparedSiteBoundaryIds(siteZones),
    [siteZones],
  );
  const tileMaskZones = useMemo(
    () => {
      // A prepared project boundary and its replacement ground now share one
      // persisted elevation datum. The whole-site mask therefore clears old
      // photogrammetry without a parallax apron or terrain tearing beneath
      // parks and streets.
      if (preparedSiteBoundaryIds.size > 0) {
        return siteZones.filter((zone) => preparedSiteBoundaryIds.has(zone.id));
      }
      return siteZones.filter((zone) => (
        shouldMaskReplacementBuildingTiles(
          zone,
          Boolean(zone.building_id && suppressedBuildingIds.has(zone.building_id)),
          getActiveBoundaryTileMaskPreference(siteZones, zone),
        )
        || shouldMaskCommunityGroundTiles(zone, getActiveBoundaryTileMaskPreference(siteZones, zone))
      )).map(streetSurfaceMaskZone);
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
  const roadSurfaceZones = useMemo(() => roadDisplayZones(connectedSceneZones, roadNetwork.data), [connectedSceneZones, roadNetwork.data]);
  const terraceScene = useMemo(() => buildTerraceScene(connectedSceneZones, terrainElevation), [connectedSceneZones, terrainElevation]);
  const preparedGroundCutouts = useMemo(() => [...terraceScene.terraces.map(z => z.coordinates), ...connectedSceneZones.filter(z => readParkTerrain(z)).map(z => z.coordinates), ...terraceScene.paths.filter(p => p.status === 'connected').map(p => p.rampFootprint)], [terraceScene, connectedSceneZones]);
  const terraceParkZones = useMemo(() => connectedSceneZones.map(zone => ({...zone, properties:{...zone.properties,
    terrace_access_clearances: terraceScene.paths.filter(p => p.status === 'connected' && (p.ownerId === zone.id || p.targetId === zone.id)).map(p => ({widthM:p.widthM, points:(p.ownerId === zone.id ? p.points.slice(0,2) : p.points.slice(2)).map(v => v.slice(0,2))}))
  }})), [connectedSceneZones, terraceScene]);
  const preparedSiteTerrainHeight = useMemo(() => {
    const boundary = getActiveSiteBoundary(siteZones);
    return boundary && preparedSiteBoundaryIds.has(boundary.id)
      ? resolvePreparedSiteTerrainHeight(boundary, terrainElevation)
      : null;
  }, [preparedSiteBoundaryIds, siteZones, terrainElevation]);
  const [isTerrainReady, setIsTerrainReady] = useState(false);
  const terrainElevationRef = useRef(DEFAULT_TERRAIN_ELEVATION);
  terrainElevationRef.current = terrainElevation;
  const terrainEllipsoidRef = useRef(createTerrainEllipsoid(DEFAULT_TERRAIN_ELEVATION));
  const tilesRendererRef = useRef<SceneTileRenderer | null>(null);
  const tilesFadePluginRef = useRef<SceneTilesFadePlugin | null>(null);
  const unloadTilesPluginRef = useRef<SceneUnloadTilesPlugin | null>(null);
  // TilesPlugin's public declaration types the forwarded ref as the plugin
  // constructor, although runtime correctly supplies the registered instance.
  const handleTilesFadePluginRef = useCallback((plugin: typeof TilesFadePlugin | null) => {
    tilesFadePluginRef.current = plugin as unknown as SceneTilesFadePlugin | null;
  }, []);
  const handleUnloadTilesPluginRef = useCallback((plugin: typeof UnloadTilesPlugin | null) => {
    unloadTilesPluginRef.current = plugin as unknown as SceneUnloadTilesPlugin | null;
  }, []);
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
  const queuedAutoFrameProjectKeyRef = useRef<string | null>(null);
  const projectFrameRequestGenerationRef = useRef(0);
  const focusedSiteAnchorRef = useRef<{ lngLat: [number, number]; height: number } | null>(null);
  const cameraInteractionGenerationRef = useRef(0);
  const cameraRevealGenerationRef = useRef(0);
  const initialCameraPoseRef = useRef<GlobeCameraPose | null>(null);
  const projectFrameReadinessRef = useRef({
    sceneReady: false,
    terrainReady: false,
    controlsReady: false,
  });
  projectFrameReadinessRef.current = {
    sceneReady,
    terrainReady: isTerrainReady,
    controlsReady: globeControlsReady,
  };

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
  const usePassiveGlobeHeightCorrection = shouldUsePassiveGlobeHeightCorrection({
    hasProjectFrameTargets: Boolean(projectZoneFocus),
    hasPreferredCameraPose: Boolean(preferredView),
  });
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
    renderZones: Array<{ coordinates?: [number, number][]; properties?: SiteZone['properties']; zone_type?: SiteZone['zone_type'] }>,
  ): Promise<boolean> => {
    const canvas = canvasRef.current;
    const camera = cameraRef.current;
    if (!canvas || !camera) return false;
    const coords = getFrameableProjectCoordinates(renderZones);
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
    const samples = renderZones.flatMap(zone => {
      const nativeHeight = assetForZone({ properties: zone.properties ?? {} })?.nativeDimensions?.[2];
      const floors = Number(zone.properties?.floor_count ?? zone.properties?.floors ?? 0);
      const explicitHeight = Number(zone.properties?.height_m ?? 0);
      const roof = nativeHeight ?? (isBuildingZoneType(zone.zone_type ?? '')
        ? Math.max(0, Number.isFinite(explicitHeight) ? explicitHeight : 0, Number.isFinite(floors) ? floors * 4 : 0) : 0);
      return (zone.coordinates ?? []).filter(c => c.length >= 2 && c.every(Number.isFinite))
        .flatMap(c => [{ coordinate: c, altitude: 0 }, { coordinate: c, altitude: roof }]);
    });
    const tallest = Math.max(0, ...samples.map(p => p.altitude));
    heightM = Math.max(heightM, tallest);
    const TARGET = PROJECT_FRAME_TARGET_FRACTION;
    for (let i = 0; i < 6; i++) {
      // Aim halfway up the complete volume, not at its ground footprint.
      applyCameraPose(computeCameraPose(centerLat, centerLng, heightM,
        terrainElevationRef.current + tallest / 2, DEFAULT_INITIAL_CAMERA_PITCH_DEGREES));
      camera.updateMatrixWorld(true);
      const { width, height: viewportH } = getCanvasViewportSize(canvas);
      const points = samples.map(p => projectLngLatToViewport(p.coordinate, p.altitude));
      const frac = projectedFrameFraction(points, width, viewportH);
      if (!Number.isFinite(frac) || frac <= 0) return false;
      if (Math.abs(frac - TARGET) < 0.03) break;
      heightM = Math.min(Math.max(heightM * (frac / TARGET), PROJECT_FRAME_MIN_HEIGHT_M), PROJECT_FRAME_MAX_HEIGHT_M);
    }
    focusedSiteAnchorRef.current = { lngLat: [centerLng, centerLat], height: terrainElevationRef.current };
    // Two settled frames so tiles/props re-render at the new pose before the
    // caller captures the canvas.
    await new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
    return true;
  }, [applyCameraPose, projectLngLatToViewport, getCanvasViewportSize]);

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

  const markUserInteracted = useCallback(() => {
    focusedSiteAnchorRef.current = null;
    // A real pointer/wheel/keyboard gesture must immediately cancel every
    // pending initial/auto-frame retry. Waiting until the delayed canvas reveal
    // flag is set lets a retry move the camera between polygon vertices.
    hasUserInteractedRef.current = true;
    cameraInteractionGenerationRef.current += 1;
    projectFrameRequestGenerationRef.current += 1;
  }, []);

  const requestProjectFrame = useCallback(async (
    renderZones: Array<{ coordinates?: [number, number][]; properties?: SiteZone['properties']; zone_type?: SiteZone['zone_type'] }>,
    source: 'auto' | 'manual',
  ): Promise<boolean> => {
    if (getFrameableProjectCoordinates(renderZones).length < 3) return false;
    if (source === 'manual') markUserInteracted();

    const requestGeneration = projectFrameRequestGenerationRef.current + 1;
    projectFrameRequestGenerationRef.current = requestGeneration;
    const interactionGeneration = cameraInteractionGenerationRef.current;
    const isCancelled = () => (
      projectFrameRequestGenerationRef.current !== requestGeneration
      || cameraInteractionGenerationRef.current !== interactionGeneration
      || (source === 'auto' && hasUserInteractedRef.current)
    );

    const applied = await runProjectFrameRetry({
      isReady: () => {
        const readiness = projectFrameReadinessRef.current;
        const canvas = canvasRef.current;
        const width = canvas?.clientWidth || canvas?.width || 0;
        const height = canvas?.clientHeight || canvas?.height || 0;
        return Boolean(
          readiness.sceneReady
          && readiness.terrainReady
          && readiness.controlsReady
          && cameraRef.current
          && globeControlsRef.current
          && canvas
          && width > 1
          && height > 1,
        );
      },
      isCancelled,
      frame: () => frameZonesForRender(renderZones),
      onFrameApplied: () => {
        hasAppliedSettledViewRef.current = true;
        hasAppliedProjectViewRef.current = true;
        hasVisibleInitialCameraRef.current = true;
        setIsInitialCameraApplied(true);
        revealCanvasAfterPose();
      },
    });

    return applied && !isCancelled();
  }, [frameZonesForRender, revealCanvasAfterPose, markUserInteracted]);

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
    queuedAutoFrameProjectKeyRef.current = null;
    projectFrameRequestGenerationRef.current += 1;
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

  // A healthy WebGL scene can mount proposal models while the external tile
  // renderer never reports a settled frame. Do not leave that usable scene
  // permanently hidden behind the startup overlay: once terrain, controls and
  // the bounded reveal timeout are ready, expose the current camera pose.
  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      hasVisibleInitialCameraRef.current = true;
      setIsInitialCameraApplied(true);
      revealCanvasAfterPose();
    }, INITIAL_CAMERA_REVEAL_FALLBACK_MS * 2);

    return () => window.clearTimeout(timeoutId);
  }, [revealCanvasAfterPose]);

  // The basic initial-pose path can run before asynchronously loaded zones
  // exist, leaving a reopened project at city scale. Queue projection-verified
  // framing as soon as both the zones and base globe controls exist. The
  // bounded runner reapplies after late controls updates without depending on
  // the tile-settled flag, which legitimately toggles throughout refinement.
  useEffect(() => {
    if (!projectZoneFocusKey || siteZones.length === 0) return;
    if (!sceneReady || !isTerrainReady || !globeControlsReady) return;
    if (hasUserInteractedRef.current) return;
    if (lastAutoFramedProjectKeyRef.current === projectZoneFocusKey) return;
    if (queuedAutoFrameProjectKeyRef.current === projectZoneFocusKey) return;

    const activeBoundary = getActiveSiteBoundary(siteZones);
    const focusZones = activeBoundary
      ? [{ coordinates: activeBoundary.coordinates as [number, number][] }]
      : [];
    const renderZones = focusZones.length > 0
      ? [...focusZones, ...siteZones.map(zone => ({ ...zone, coordinates: zone.coordinates as [number, number][] }))]
      : siteZones.map(zone => ({ ...zone, coordinates: zone.coordinates as [number, number][] }));
    queuedAutoFrameProjectKeyRef.current = projectZoneFocusKey;
    void requestProjectFrame(renderZones, 'auto').then((framed) => {
      if (queuedAutoFrameProjectKeyRef.current !== projectZoneFocusKey) return;
      if (framed && !hasUserInteractedRef.current) {
        lastAutoFramedProjectKeyRef.current = projectZoneFocusKey;
      }
    });
  }, [
    globeControlsReady,
    isTerrainReady,
    projectZoneFocusKey,
    requestProjectFrame,
    sceneReady,
    siteZones,
  ]);

  useEffect(() => () => {
    projectFrameRequestGenerationRef.current += 1;
    queuedAutoFrameProjectKeyRef.current = null;
  }, []);

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
    preferredView?.cameraPosition?.bearing,
    projectLngLatToViewport,
    sceneReady,
    unprojectViewportPoint,
  ]);

  const waitForCurrentTiles = useCallback(
    () => waitForCaptureTileReadiness(tilesRendererRef.current),
    [],
  );

  const captureDirect3D = useCallback((options: {
    skipTileWait?: boolean;
    includeGeometryPasses?: boolean;
    maxLongEdge?: number;
  } = {}): Promise<Direct3DCaptureBundle> => {
    if (direct3DCapturePromiseRef.current) {
      return Promise.reject(new Direct3DCaptureError(
        'busy',
        'A Direct 3D capture is already in progress.',
      ));
    }

    const trackedPromise: Promise<Direct3DCaptureBundle> = (async () => {
      if (hasLocalDraftsRef.current) {
        throw new Direct3DCaptureError('capture_failed', 'Save or discard local drawings before capturing your plan.');
      }
      const accessSnapshot = parkAccessSnapshotRef.current;
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

      const tilesSettled = options.skipTileWait || await waitForCurrentTiles();
      if (!tilesSettled) {
        throw new Direct3DCaptureError(
          'capture_failed',
          'The surrounding 3D tiles did not settle in time. Hold the camera still and try again.',
        );
      }
      const sharedGroundSnapshot = await waitForSharedGround();
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

      const previousReferenceVisibility = referenceOverlayGroup.current?.visible;
      const previousOverlaysVisible = zoneOverlaysVisibleRef.current;
      const previousSelectedBuildingId = selectedBuildingIdRef.current;
      try {
        // Direct capture consumes the compiled 3D scene, never editable color
        // polygons or selection affordances. Two frames let React commit the
        // clean state before the deterministic off-screen passes begin.
        setZoneOverlaysVisible(false);
        setCaptureOverlaysHidden(true);
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
        const captured = await captureDirect3DScene(renderer, scene, camera, {
          includeGeometryPasses: options.includeGeometryPasses,
          maxLongEdge: options.maxLongEdge,
          // Close-up scene framing may contain only the proposal. The server
          // applies presentation-specific geometry checks and source fallback.
          maxMaskCoverage: 1,
          minVisibleContextCoverage: 0,
        });
        if (accessSnapshot.sourceSignature !== parkAccessSnapshotRef.current.sourceSignature) {
          throw new Direct3DCaptureError('capture_failed', 'The plan changed during capture. Let the scene settle and try again.');
        }
        assertSharedGroundUnchanged(sharedGroundSnapshot, sharedGroundRef.current);
        return { ...captured, sharedGroundSnapshot, ...(accessSnapshot.parks.length && accessSnapshot.sources.length <= 256
          ? { parkAccessSnapshot: structuredClone(accessSnapshot) } : {}) };
      } finally {
        if (referenceOverlayGroup.current && previousReferenceVisibility !== undefined) referenceOverlayGroup.current.visible = previousReferenceVisibility;
        setZoneOverlaysVisible(previousOverlaysVisible);
        setCaptureOverlaysHidden(false);
        setSelectedBuildingId(previousSelectedBuildingId);
      }
    })().finally(() => {
      if (direct3DCapturePromiseRef.current === trackedPromise) {
        direct3DCapturePromiseRef.current = null;
      }
    });
    direct3DCapturePromiseRef.current = trackedPromise;
    return trackedPromise;
  }, [waitForCurrentTiles, waitForSharedGround]);

  // Street-level Direct 3D capture: the full off-screen pass stack (beauty +
  // class-ID + instance-ID) from the CURRENT camera — the caller parks the
  // camera at street level first. Aerial mask-coverage bounds are relaxed:
  // at eye level the sky legitimately dominates the frame.
  const captureStreetDirect3D = useCallback(async (
    options: Direct3DCaptureOptions = {},
  ): Promise<Direct3DCaptureBundle | null> => {
    const renderer = rendererRef.current;
    const scene = sceneRef.current;
    const camera = cameraRef.current;
    if (!renderer || !scene || !camera || renderer.getContext().isContextLost()) return null;
    if (hasLocalDraftsRef.current) {
      throw new Direct3DCaptureError('capture_failed', 'Save or discard local drawings before capturing your plan.');
    }
    const sharedGroundSnapshot = await waitForSharedGround();
    try {
      const accessSnapshot = parkAccessSnapshotRef.current;
      const captured = await captureDirect3DScene(renderer, scene, camera, {
        ...options,
        // Direct 3D v2 requires the same registered geometry controls at
        // street level as it does for aerial/current-camera renders.  Keep
        // callers free to request a cheaper diagnostic capture explicitly,
        // but make the production street path complete by default.
        includeGeometryPasses: options.includeGeometryPasses ?? true,
        minMaskCoverage: 0,
        maxMaskCoverage: 1,
      });
      if (accessSnapshot.sourceSignature !== parkAccessSnapshotRef.current.sourceSignature) return null;
      assertSharedGroundUnchanged(sharedGroundSnapshot, sharedGroundRef.current);
      return { ...captured, sharedGroundSnapshot, ...(accessSnapshot.parks.length && accessSnapshot.sources.length <= 256
        ? { parkAccessSnapshot: structuredClone(accessSnapshot) } : {}) };
    } catch (err) {
      console.warn('[GlobeSitePlannerMap] Street Direct 3D capture failed — falling back to screenshot:', err);
      return null;
    }
  }, [waitForSharedGround]);

  const captureVideoRouteControls = useCallback(async (
    request: VideoRouteCaptureRequest,
  ): Promise<VideoRouteCaptureResult> => {
    const canvas = canvasRef.current;
    const renderer = rendererRef.current;
    const camera = cameraRef.current;
    const scene = sceneRef.current;
    if (!canvas || !renderer || !camera || !scene || !canvas.isConnected) {
      throw new Error('The 3D globe is not ready to prepare video route controls.');
    }

    const renderProfile = videoRenderQualityProfile(request.renderQuality);
    validateVideoRenderProfile(renderProfile, renderer.capabilities.maxTextureSize);
    const originalRendererSize = renderer.getSize(new THREE.Vector2());
    const originalPixelRatio = renderer.getPixelRatio();
    const originalDrawingBufferSize = renderer.getDrawingBufferSize(new THREE.Vector2());

    const sampledRoute = resampleVideoRoute(request.routePoints, request.keyframeCount ?? 6);
    const sourceAspect = (canvas.clientWidth || canvas.width) / Math.max(1, canvas.clientHeight || canvas.height);
    const streetWalkby = request.cameraMotion === 'street_walkby';
    const detailFlythrough = request.cameraMotion === 'detail_flythrough';
    const nearFieldRoute = streetWalkby || detailFlythrough;
    const streetUp = camera.up.clone().normalize();
    let previousStreetProjection: ReturnType<typeof applyStreetCameraProjection> = null;
    let routeSurfacePoints: THREE.Vector3[];
    let nearFieldTerrainHeight: number | null = null;
    try {
      // The user draws against the captured aerial frame, so resolve every
      // point against that exact scene projection before switching to the
      // pedestrian lens. This anchors a street route to real road/sidewalk
      // elevations instead of an artificial plane beneath the aerial camera.
      const routeHits = sampledRoute.map((point) => {
        const ndc = normalizedVideoPointToNdc(point, sourceAspect);
        const hit = raycastSurfacePoint(ndc.x, ndc.y);
        if (!hit) throw new Error('Part of the drawn route does not intersect the visible 3D city. Draw the route over the ground or buildings.');
        return { ...hit, height: authoredCameraGround(terrainZonesRef.current, hit.lngLat[0], hit.lngLat[1], hit.height) };
      });
      nearFieldTerrainHeight = nearFieldRoute
        ? stableNearFieldTerrainHeight(routeHits.map((hit) => hit.height))
        : null;
      routeSurfacePoints = routeHits.map((hit) => {
        const world = new THREE.Vector3();
        WGS84_ELLIPSOID.getCartographicToPosition(
          hit.lngLat[1] * DEG_TO_RAD,
          hit.lngLat[0] * DEG_TO_RAD,
          videoRouteSurfaceHeight(
            hit.height,
            nearFieldTerrainHeight ?? hit.height,
            request.cameraMotion,
          ),
          world,
        );
        return world;
      });
    } catch (error) {
      restoreStreetCameraProjection(camera, previousStreetProjection);
      throw error;
    }
    const centerHit = raycastSurfacePoint(0, 0);
    if (!centerHit) {
      restoreStreetCameraProjection(camera, previousStreetProjection);
      throw new Error('The center of the captured view does not intersect the city. Reframe the site and try again.');
    }
    const centerWorld = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToPosition(
      centerHit.lngLat[1] * DEG_TO_RAD,
      centerHit.lngLat[0] * DEG_TO_RAD,
      videoRouteSurfaceHeight(
        authoredCameraGround(terrainZonesRef.current, centerHit.lngLat[0], centerHit.lngLat[1], centerHit.height),
        nearFieldTerrainHeight ?? centerHit.height,
        request.cameraMotion,
      ),
      centerWorld,
    );
    if (nearFieldRoute) previousStreetProjection = applyStreetCameraProjection(camera);
    const previousFrameProjection = applyVideoFrameProjection(camera, sourceAspect);

    const originalCamera = {
      position: camera.position.clone(),
      quaternion: camera.quaternion.clone(),
      up: camera.up.clone(),
    };
    const cameraOffset = nearFieldRoute
      ? new THREE.Vector3()
      : camera.position.clone().sub(centerWorld);
    const streetFocusWorld = streetWalkby
      ? centerWorld.clone().addScaledVector(streetUp, 7)
      : null;
    const pathCurve = new THREE.CatmullRomCurve3(routeSurfacePoints, false, 'centripetal');
    const previousReferenceVisibility = referenceOverlayGroup.current?.visible;
    const previousOverlaysVisible = zoneOverlaysVisibleRef.current;
    const previousSelectedBuildingId = selectedBuildingIdRef.current;
    const previousModelsVisible = buildingModelsVisibleRef.current;
    const controls = globeControlsRef.current;
    const controlsTarget = controls?.controls ?? controls;
    const originalPivot = controls?.pivotPoint?.clone?.() as THREE.Vector3 | undefined;
    const previousControlsEnabled = controlsTarget && 'enabled' in controlsTarget
      ? Boolean(controlsTarget.enabled)
      : null;
    const fadePlugin = tilesFadePluginRef.current;
    const previousFadeDuration = fadePlugin?.fadeDuration ?? null;
    const unloadPlugin = unloadTilesPluginRef.current;
    const previousUnloadDelay = unloadPlugin?.delay ?? null;
    const tileRenderer = tilesRendererRef.current;
    const previousTileErrorTarget = tileRenderer?.errorTarget ?? null;
    const previousLoadSiblings = tileRenderer?.loadSiblings ?? null;
    const tileCache = tileRenderer?.lruCache;
    const previousTileCache = tileCache ? {
      minSize: tileCache.minSize,
      maxSize: tileCache.maxSize,
      minBytesSize: tileCache.minBytesSize,
      maxBytesSize: tileCache.maxBytesSize,
    } : null;
    let restoreTextureAnisotropy: (() => void) | null = null;
    let releaseTileQueueHold: (() => void) | null = null;
    let streetRenderReadiness: VideoRouteCaptureResult['streetRenderReadiness'];
    const waitForRouteContext = () => request.renderQuality === 'high'
      ? waitForVisibleTileCoverage(tileRenderer, {
          stableMs: 750,
          timeoutMs: 4_000,
          acceptVisibleCoverageAtTimeout: true,
        })
      : waitForCurrentTiles();

    const applyRoutePose = (progress: number) => {
      if (streetWalkby) {
        applyStreetRoutePose(camera, pathCurve, progress, streetUp, undefined, streetFocusWorld ?? undefined);
        return;
      }
      if (detailFlythrough) {
        applyStreetRoutePose(camera, pathCurve, progress, streetUp, 6);
        return;
      }
      const target = pathCurve.getPointAt(Math.max(0, Math.min(1, progress)));
      camera.position.copy(target).add(cameraOffset);
      camera.up.copy(originalCamera.up);
      camera.lookAt(target);
      camera.updateMatrixWorld(true);
      if (controls?.pivotPoint) controls.pivotPoint.copy(target);
    };
    const twoFrames = () => new Promise<void>((resolve) => {
      requestAnimationFrame(() => requestAnimationFrame(() => resolve()));
    });

    try {
      if (previousControlsEnabled !== null) controlsTarget.enabled = false;
      if (referenceOverlayGroup.current) referenceOverlayGroup.current.visible = false;
      setStreetCapturePegmanHidden(true);
      setCaptureOverlaysHidden(true);
      setZoneOverlaysVisible(false);
      setSelectedBuildingId(null);
      setBuildingModelsVisible(true);
      // Capture one frozen tile selection without cross-fades. This applies to
      // both drone and street routes so context buildings cannot dissolve
      // between the indexed source frames.
      if (fadePlugin) fadePlugin.fadeDuration = 0;
      if (unloadPlugin) unloadPlugin.delay = renderProfile.tileHoldMilliseconds;
      if (tileRenderer && renderProfile.tileErrorTarget !== null) {
        tileRenderer.errorTarget = Math.min(
          tileRenderer.errorTarget ?? renderProfile.tileErrorTarget,
          renderProfile.tileErrorTarget,
        );
        tileRenderer.loadSiblings = true;
      }
      if (tileCache && request.renderQuality === 'high') {
        // Keep the bounded 80 m route resident through both passes. These
        // limits are restored immediately after capture; the Unload plugin's
        // delay prevents GPU disposal while the camera revisits warm views.
        tileCache.minSize = Math.max(tileCache.minSize, 8_000);
        tileCache.maxSize = Math.max(tileCache.maxSize, 12_000);
        tileCache.minBytesSize = Math.max(tileCache.minBytesSize, 0.45 * 1024 ** 3);
        tileCache.maxBytesSize = Math.max(tileCache.maxBytesSize, 0.65 * 1024 ** 3);
      }
      renderer.setPixelRatio(1);
      renderer.setSize(renderProfile.renderWidth, renderProfile.renderHeight, false);
      tileRenderer?.setResolution?.(
        camera,
        renderProfile.renderWidth,
        renderProfile.renderHeight,
      );
      if (renderProfile.maximumTextureAnisotropy) {
        restoreTextureAnisotropy = applyCaptureTextureAnisotropy(
          scene,
          renderer.capabilities.getMaxAnisotropy(),
        );
      }
      if (nearFieldRoute) {
        setStreetRenderProfileActive(true);
      }
      await twoFrames();

      // High Quality is a true two-pass render. The dry traversal visits every
      // final camera pose and waits for a stable tile window at 25 distributed
      // views before any encoded frame is produced.
      const warmupFrames = buildVideoWarmupFrames(renderProfile);
      if (request.renderQuality === 'high') {
        for (const warmup of warmupFrames) {
          applyRoutePose(warmup.progress);
          await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
          if (warmup.settleTiles) {
            const settled = await waitForRouteContext();
            if (!settled) {
              throw new Error(
                `The surrounding Google context did not settle during full-route preload at frame ${warmup.index + 1}. Try a shorter path or Draft quality.`,
              );
            }
          }
        }
        // The entire path is now resident in the enlarged cache. Stop new
        // downloads and parses before source capture so no Google building can
        // switch LOD halfway through the video. The original queue state is
        // restored in the finally block.
        releaseTileQueueHold = holdTileQueueUpdates(tileRenderer);
        await twoFrames();
        const frozenContextReady = await waitForVisibleTileCoverage(tileRenderer);
        if (!frozenContextReady) {
          throw new Error('The preloaded Google context could not be frozen for capture. Try a shorter path.');
        }
      }

      const routeGroundSnapshot = await waitForSharedGround();
      const keyframesBase64: string[] = [];
      const geometryCheckpoints: NonNullable<VideoRouteCaptureResult['geometryCheckpoints']> = [];
      for (let index = 0; index < sampledRoute.length; index += 1) {
        applyRoutePose(cinematicRouteProgress(index / (sampledRoute.length - 1)));
        await twoFrames();
        const settled = await waitForRouteContext();
        if (!settled) {
          throw new Error(`The surrounding Google context did not settle at route view ${index + 1}. Try a shorter path.`);
        }
        await waitForSharedGround();
        assertSharedGroundUnchanged(routeGroundSnapshot, sharedGroundRef.current);
        // Near-field source creation needs a trustworthy beauty checkpoint,
        // not a full semantic/instance pass at every pose. The latter is a
        // metadata product and can fail when a close facade fills the frame;
        // it must never prevent the deterministic route video from rendering.
        const capture = nearFieldRoute
          ? null
          : await captureDirect3D({
              skipTileWait: true,
              includeGeometryPasses: request.renderQuality === 'high',
            });
        if (capture) {
          keyframesBase64.push(capture.beautyImageBase64);
          if (
            capture.depthImageBase64
            && capture.normalImageBase64
            && capture.materialIdImageBase64
            && capture.materialIdManifest
          ) {
            geometryCheckpoints.push({
              progress: index / (sampledRoute.length - 1),
              beautyImageBase64: capture.beautyImageBase64,
              classIdImageBase64: capture.classIdImageBase64,
              classIdManifest: capture.classIdManifest,
              instanceIdImageBase64: capture.instanceIdImageBase64,
              instanceIdManifest: capture.instanceIdManifest,
              depthImageBase64: capture.depthImageBase64,
              normalImageBase64: capture.normalImageBase64,
              materialIdImageBase64: capture.materialIdImageBase64,
              materialIdManifest: capture.materialIdManifest,
              camera: capture.camera,
            });
          }
        } else {
          renderer.setRenderTarget(null);
          renderer.render(scene, camera);
          const beautyImageBase64 = canvas.toDataURL('image/png');
          if (beautyImageBase64.length < 1_024) {
            throw new Error(`The authored route frame ${index + 1} could not be captured.`);
          }
          keyframesBase64.push(beautyImageBase64);
        }
      }
      if (nearFieldRoute) {
        await assertNearFieldVideoSourceQuality(keyframesBase64);
      }
      if (nearFieldRoute) streetRenderReadiness = inspectStreetRenderReadiness(scene);

      // Render a dedicated 16:9, fixed-timestep frame sequence so local output
      // and provider previews share the same crop, camera poses, and timing.
      const previewCanvas = document.createElement('canvas');
      previewCanvas.width = renderProfile.outputWidth;
      previewCanvas.height = renderProfile.outputHeight;
      const previewContext = previewCanvas.getContext('2d');
      if (!previewContext) throw new Error('The browser could not prepare the route preview canvas.');
      const drawPreviewFrame = () => {
        const sourceWidth = canvas.width;
        const sourceHeight = canvas.height;
        const { sx, sy, sw, sh } = getCenterCropRect(
          sourceWidth,
          sourceHeight,
          previewCanvas.width,
          previewCanvas.height,
        );
        previewContext.drawImage(canvas, sx, sy, sw, sh, 0, 0, previewCanvas.width, previewCanvas.height);
      };

      const previewCapture = await captureDeterministicVideo({
        canvas: previewCanvas,
        durationSeconds: request.durationSeconds,
        bitrate: renderProfile.bitrate,
        renderFrame: async (frame) => {
          applyRoutePose(cinematicRouteProgress(frame.progress));
          // Give TilesRenderer and the authored R3F layers one render cycle to
          // respond to this indexed pose, then render that exact camera state.
          await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
          assertSharedGroundUnchanged(routeGroundSnapshot, sharedGroundRef.current);
          renderer.setRenderTarget(null);
          renderer.render(scene, camera);
          drawPreviewFrame();
        },
      });
      const previewBlob = previewCapture.blob;
      const previewVideoBase64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result));
        reader.onerror = () => reject(new Error('The route preview could not be encoded.'));
        reader.readAsDataURL(previewBlob);
      });
      return {
        keyframesBase64,
        previewVideoBase64,
        previewVideoMimeType: previewBlob.type,
        geometryCheckpoints,
        previewCaptureProfile: {
          encoder: previewCapture.encoder,
          frameCount: previewCapture.frameCount,
          fps: previewCapture.fps,
          width: previewCapture.width,
          height: previewCapture.height,
          renderWidth: renderProfile.renderWidth,
          renderHeight: renderProfile.renderHeight,
          tileWarmupFrameCount: warmupFrames.length,
          tileSetHeld: Boolean(unloadPlugin),
          fixedTimestep: true,
        },
        geometryPassProfile: videoGeometryPassProfile(geometryCheckpoints, previewCapture.frameCount),
        streetRenderReadiness,
      };
    } finally {
      releaseTileQueueHold?.();
      restoreTextureAnisotropy?.();
      camera.position.copy(originalCamera.position);
      camera.quaternion.copy(originalCamera.quaternion);
      camera.up.copy(originalCamera.up);
      restoreVideoFrameProjection(camera, previousFrameProjection);
      restoreStreetCameraProjection(camera, previousStreetProjection);
      camera.updateMatrixWorld(true);
      renderer.setRenderTarget(null);
      renderer.setPixelRatio(originalPixelRatio);
      renderer.setSize(originalRendererSize.x, originalRendererSize.y, false);
      tileRenderer?.setResolution?.(
        camera,
        originalDrawingBufferSize.x,
        originalDrawingBufferSize.y,
      );
      if (tileRenderer && previousTileErrorTarget !== null) {
        tileRenderer.errorTarget = previousTileErrorTarget;
      }
      if (tileRenderer && previousLoadSiblings !== null) {
        tileRenderer.loadSiblings = previousLoadSiblings;
      }
      if (tileCache && previousTileCache) {
        tileCache.minSize = previousTileCache.minSize;
        tileCache.maxSize = previousTileCache.maxSize;
        tileCache.minBytesSize = previousTileCache.minBytesSize;
        tileCache.maxBytesSize = previousTileCache.maxBytesSize;
      }
      if (unloadPlugin && previousUnloadDelay !== null) {
        unloadPlugin.delay = previousUnloadDelay;
      }
      if (controls?.pivotPoint && originalPivot) controls.pivotPoint.copy(originalPivot);
      if (previousControlsEnabled !== null) controlsTarget.enabled = previousControlsEnabled;
      controls?.update?.();
      setStreetCapturePegmanHidden(false);
      setCaptureOverlaysHidden(false);
      setStreetRenderProfileActive(false);
      if (referenceOverlayGroup.current && previousReferenceVisibility !== undefined) referenceOverlayGroup.current.visible = previousReferenceVisibility;
      setZoneOverlaysVisible(previousOverlaysVisible);
      setSelectedBuildingId(previousSelectedBuildingId);
      setBuildingModelsVisible(previousModelsVisible);
      if (fadePlugin && previousFadeDuration !== null) fadePlugin.fadeDuration = previousFadeDuration;
    }
  }, [captureDirect3D, raycastSurfacePoint, waitForCurrentTiles, waitForSharedGround]);

  // Scene hygiene for street-level captures (same pattern as captureDirect3D:
  // flip clean state, two frames for React to commit, restore in finally).
  const withStreetCaptureScene = useCallback(async <T,>(
    fn: (kind: 'model3d' | 'context3d') => Promise<T>,
  ): Promise<T> => {
    const kind: 'model3d' | 'context3d' = streetCaptureHas3DModelsRef.current
      ? 'model3d'
      : 'context3d';
    const previousReferenceVisibility = referenceOverlayGroup.current?.visible;
    const previousOverlaysVisible = zoneOverlaysVisibleRef.current;
    const previousSelectedBuildingId = selectedBuildingIdRef.current;
    const previousModelsVisible = buildingModelsVisibleRef.current;
    const camera = cameraRef.current;
    const fadePlugin = tilesFadePluginRef.current;
    const previousFadeDuration = fadePlugin?.fadeDuration ?? null;
    let previousProjection: ReturnType<typeof applyStreetCameraProjection> = null;
    try {
      if (referenceOverlayGroup.current) referenceOverlayGroup.current.visible = false;
      setStreetCapturePegmanHidden(true);
      setCaptureOverlaysHidden(true);
      setSelectedBuildingId(null);
      if (kind === 'model3d') {
        // The authored models carry the design — colored zone overlays would
        // only contaminate the capture. Google Tiles remain as context outside
        // the existing project-boundary mask, where authored City Prompt
        // geometry replaces the underlying photogrammetry.
        setZoneOverlaysVisible(false);
        setBuildingModelsVisible(true);
        setStreetRenderProfileActive(true);
        if (fadePlugin) fadePlugin.fadeDuration = 0;
        if (camera) previousProjection = applyStreetCameraProjection(camera);
      } else {
        // No models: the overlays ARE the intervention markers the prompt
        // references, so they must be in frame even if the user hid them.
        setZoneOverlaysVisible(true);
      }
      await new Promise<void>((resolve) => {
        requestAnimationFrame(() => requestAnimationFrame(() => resolve()));
      });
      return await fn(kind);
    } finally {
      setStreetCapturePegmanHidden(false);
      setCaptureOverlaysHidden(false);
      setStreetRenderProfileActive(false);
      setSelectedBuildingId(previousSelectedBuildingId);
      if (referenceOverlayGroup.current && previousReferenceVisibility !== undefined) referenceOverlayGroup.current.visible = previousReferenceVisibility;
      setZoneOverlaysVisible(previousOverlaysVisible);
      setBuildingModelsVisible(previousModelsVisible);
      if (fadePlugin && previousFadeDuration !== null) fadePlugin.fadeDuration = previousFadeDuration;
      if (camera) restoreStreetCameraProjection(camera, previousProjection);
    }
  }, []);

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
      withStreetCaptureScene,
      captureStreetDirect3D,
      captureVideoRouteControls,
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
        sharedGround: sharedGroundState,
        groundingIssues: buildingGroundingIssues,
        renderInfo: () => {
          const info = rendererRef.current?.info;
          return info ? { render: { ...info.render }, memory: { ...info.memory } } : null;
        },
      });
    }
  }, [buildingGroundingIssues, captureDirect3D, captureStreetDirect3D, captureVideoRouteControls, globeAIRenderViewport, isSceneSettled, onGlobeReady, sharedGroundState, terrainElevation, waitForCurrentTiles, withStreetCaptureScene]);

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
      const procedural = activeSitePlannerTool === 'road' && !zoneProperties.pick_place_street_section;
      const smoothed = zoneProperties.pick_place_street_section
        ? snapStreetEnds(pts, siteZones)
        : smoothPolyline(procedural ? snapRoadEndpoints(pts, siteZones, zoneProperties.road_level) : pts);
      const width = (zoneProperties.width as number) || 10;
      finalCoords = sanitizeCoords(bufferLineToPolygon(smoothed, width));
      if (zoneProperties.pick_place_street_section || procedural) zoneProperties.plan_centerline = smoothed;
      if (procedural) zoneProperties.procedural_road = 1;
    } else {
      finalCoords = [...pts];
    }

    if (finalCoords.length < 3) {
      console.warn('[Globe] Zone create skipped: not enough valid unique vertices', finalCoords.length);
      return;
    }

    if (onZoneCreated(finalCoords, activeSitePlannerTool, zoneProperties) === false) return;
    setDrawingPoints([]);
    setDrawingPointHeights([]);
    setCenterNearStartVertex(false);
    drawingPointsRef.current = [];
    drawingPointHeightsRef.current = [];
    if (isMobileDrawingViewport() || zoneProperties.pick_place_street_section) {
      setActiveSitePlannerTool(null);
    }
  }, [activeSitePlannerTool, activeToolProperties, linear, onZoneCreated, setActiveSitePlannerTool, terrainElevation, siteZones]);
  finishDrawingRef.current = finishDrawing;

  // Keyboard handler for drawing
  useEffect(() => {
    if (interactionPaused) return;
    if (!hasDrawingTool) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
      if ((e.target as HTMLElement)?.isContentEditable) return;

      if (e.key === 'Enter' && drawingPointsRef.current.length > 0) {
        // Canvas clicks leave toolbar focus in place. Consume Enter so finishing
        // cannot also reopen Guide or toggle the active drawing tool off.
        e.preventDefault();
        e.stopImmediatePropagation();
        finishDrawing();
      }
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
  }, [canPasteZone, hasDrawingTool, interactionPaused, markUserInteracted, measureModeActive, onBuildingDeleted, onCopyZone, onPasteZone, onZoneCreated, onZoneSelected, onZoneUpdated, selectedBuildingId, selectedZoneId, setStreetViewActive, setStreetViewAngle, siteZones, streetViewPegman?.angle, streetViewPegman?.position, _onZoneDeleted]);

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

    if (placementDraft) {
      // Touch users position the map under the preview, then confirm explicitly.
      if (rect.width >= 640 && !placementDraft.inputError) onPlaceAsset?.(clickLngLat, clickHeight);
      return;
    }

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
      setStreetViewPosition(clickLngLat, authoredCameraGround(terrainZonesRef.current, clickLngLat[0], clickLngLat[1], clickHeight));
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
  }, [placementDraft, onPlaceAsset, activeSitePlannerTool, cancelDrawing, hasDrawingTool, interactionPaused, linear, markUserInteracted, measureModeActive, onZoneSelected, raycastSurfacePoint, setStreetViewPosition, siteZones, streetViewPegman, updateCenterConnectionState]);

  const handleZoneMeshClick = useCallback((zoneId: string) => {
    if (placementDraft) return;
    if (interactionPaused) return;
    if (hasDrawingTool || measureModeActive) return;
    // Street View pegman-drop mode: let the click fall through to the canvas
    // handler so the pin drops on the zone instead of selecting it.
    if (streetViewPegman !== null) return;
    ignoreNextCanvasClickRef.current = true;
    setSelectedBuildingId(null);
    onZoneSelected(zoneId);
  }, [placementDraft, hasDrawingTool, interactionPaused, measureModeActive, onZoneSelected, streetViewPegman]);

  const handleBuildingModelClick = useCallback((buildingId: string) => {
    if (placementDraft) return;
    if (interactionPaused || hasDrawingTool || measureModeActive) return;
    // Street View pegman-drop mode owns the canvas click. Generated building
    // meshes must not select themselves and swallow placement when the user
    // intentionally drops a close-up camera on or beside the authored model.
    if (streetViewPegman !== null) return;
    ignoreNextCanvasClickRef.current = true;
    // A generated model is a first-class handle onto its zone: select both so
    // the properties panel (type/floors/Quick Regenerate) and the polygon
    // transform affordances (move/reshape/rotate) light up together.
    const owningZone = siteZones.find((zone) => zone.building_id === buildingId);
    onZoneSelected(owningZone ? owningZone.id : null);
    setSelectedBuildingId(buildingId);
  }, [placementDraft, hasDrawingTool, interactionPaused, measureModeActive, onZoneSelected, siteZones, streetViewPegman]);

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

  if (!API_KEY) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-900 text-white">
        <p className="text-sm text-gray-400">Missing VITE_GOOGLE_MAPS_API_KEY</p>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="relative h-full w-full bg-black" style={{ overflow: 'hidden' }}>
      <Canvas
        aria-label="3D city map"
        role="application"
        style={{ visibility: isInitialCameraApplied ? 'visible' : 'hidden' }}
        camera={initialThreeCamera}
        dpr={[1, 2]}
        shadows
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
          cvs.setAttribute('role', 'application');
          cvs.setAttribute('aria-label', '3D city map');

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
        <color attach="background" args={[streetRenderProfileActive ? '#cfdae4' : '#dbeafe']} />
        {streetRenderProfileActive ? (
          <GlobeStreetRenderProfile
            latitude={focusLatitude}
            longitude={focusLongitude}
            terrainHeight={terrainElevation}
          />
        ) : (
          <>
            <ambientLight intensity={architecturalLighting.ambientIntensity} />
            <hemisphereLight args={['#f8fbff', '#5b6775', architecturalLighting.hemisphereIntensity]} />
            <directionalLight
              position={[8_000_000, 10_000_000, 7_000_000]}
              intensity={architecturalLighting.directionalIntensity}
              color="#fff7d6"
            />
          </>
        )}
        {/* Street mode uses a near architectural atmosphere; globe mode keeps
            the existing horizon-scale fog. */}
        <fog
          attach="fog"
          args={streetRenderProfileActive
            ? ['#cfdae4', 180, 900]
            : ['#b8c8d8', 8000, 80000]}
        />
        {/* IBL for placed GLB models (PBR materials only) — tiles and zone
            overlays are unlit basic materials, so they're unaffected. */}
        {hasPlaceableModels && (
          <Environment
            preset="city"
            background={false}
            environmentIntensity={architecturalLighting.environmentIntensity}
          />
        )}
        <TilesRenderer>
          <GoogleContextVisibility visible={contextPresentation.visible === 'google'} />
          {/* autoRefreshToken: Google 3D Tiles sessions expire after a few hours;
              without it every tile fetch 400s (pale background polygons through
              the holes) until a full reload. Refreshes the session on 4xx. */}
          <TilesPlugin plugin={GoogleCloudAuthPlugin} args={{ apiToken: API_KEY, useRecommendedSettings: true, autoRefreshToken: true } as any} />
          <TilesPlugin plugin={TileCompressionPlugin} />
          <TilesPlugin plugin={GLTFExtensionsPlugin} args={{ dracoLoader: new DRACOLoader().setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.7/') } as any} />
          <TilesPlugin plugin={UpdateOnChangePlugin} />
          <TilesPlugin ref={handleUnloadTilesPluginRef} plugin={UnloadTilesPlugin} />
          <TilesPlugin ref={handleTilesFadePluginRef} plugin={TilesFadePlugin} />
          <TilesExposer tilesRef={tilesRendererRef} />
          <GlobeControls
            ref={handleGlobeControlsRef}
            // The close project/preferred camera already owns a geodetic
            // height. Passive scene collision sees late Google tile meshes as
            // new ground and can lift that camera kilometres after framing.
            // Keep passive correction only for the unframed empty-city entry;
            // pointer/zoom raycasts remain enabled for normal navigation.
            adjustHeight={usePassiveGlobeHeightCorrection}
            maxAltitude={MAX_GLOBE_CAMERA_PITCH_DEGREES * DEG_TO_RAD}
            useFallbackPlane
          />
          <TilesAttributionOverlay />
          <SceneSettledMonitor
            onSettledChange={setIsSceneSettled}
            onDisplayReadyChange={setAreTilesDisplayReady}
          />
          <SharedSiteGroundProvider zones={allSiteZones} onChange={handleSharedGroundChange} inspectPrepared={showGroundReview}>
          <SurveyGroundSurface visible={contextPresentation.visible === 'terrain'} />
          <ParkAssemblyGroundProvider>
          <AutomaticParkGround zones={allSiteZones} paused={parkGroundPaused} onSave={onAutoParkTerrain} onChange={setParkAlignment} fallback={terrainElevation}>
          <group ref={referenceOverlayGroup}><GlobeReferenceLayer layers={referenceLayers} terrainHeight={terrainElevation} /></group>
          <TileStencilPatcher zones={tileMaskZones} assemblyZones={allSiteZones} terrainHeight={terrainElevation} />
          <GlobeTileMaskLayer zones={tileMaskZones} terrainHeight={terrainElevation} />
          {/* Camera starts at project location via Canvas camera prop */}

          {/* Editable fills/outlines/labels can hide for a clean AI capture,
              while a generated park orthophoto stays mounted as authored
              proposal ground (alongside models, street sections and props). */}
          <group name="siteforge-direct3d-ground" userData={direct3DProposalUserData('ground')}>
            <GlobeZoneLayer
              preparedGroundCutouts={preparedGroundCutouts}
              zones={roadSurfaceZones}
              selectedZoneId={interactionPaused ? null : selectedZoneId}
              terrainHeight={terrainElevation}
              onZoneClick={handleZoneMeshClick}
              selectionEnabled={!interactionPaused && !hasDrawingTool && !measureModeActive}
              suppressedBuildingIds={suppressedBuildingIds}
              planningOverlaysVisible={zoneOverlaysVisible}
              placementBoundaryVisible={!captureOverlaysHidden && (Boolean(placementDraft) || activeSitePlannerTool === 'road')}
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
            <GlobePedestrianConnections results={pedestrianConnections} zones={connectedSceneZones} terrainHeight={terrainElevation} />
            <GlobeTerraces scene={terraceScene} zones={connectedSceneZones} />
          </group>

          {/* Park-program structures (playgrounds/pavilions/bridges) — sibling
              of the zone-overlay group like the building models. Trees and
              benches stay render-only so they cannot collide with paths. */}
          <group name="siteforge-direct3d-park" userData={direct3DProposalUserData('park')}>
            <GlobeParkKitLayer zones={terraceParkZones} terrainHeight={terrainElevation} />
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
                preparedSiteTerrainHeight={preparedSiteTerrainHeight}
                onLoadedIdsChange={handleModeledIdsChange}
                onGroundingIssuesChange={setModelGroundingIssues}
                selectedBuildingId={selectedRenderedBuildingId}
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
                onGroundingIssuesChange={handleGroundingIssuesChange}
                selectedBuildingId={selectedRenderedBuildingId}
                onBuildingClick={handleBuildingModelClick}
              />
            )}
          </group>

          <group name="siteforge-direct3d-editor-ui" userData={DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA}>
            {placementDraft && !placementDraft.inputError && !interactionPaused && !captureOverlaysHidden && <GlobePlacementPreview draft={placementDraft} zones={allSiteZones} onStatusChange={setPlacementProblemMessage} />}
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
            {!placementDraft && !interactionPaused && !hasDrawingTool && !measureModeActive && selectedZoneId && (() => {
              const zone = siteZones.find(z => z.id === selectedZoneId);
              return zone ? (
                <GlobeEditMode
                  zone={zone}
                  zones={siteZones}
                  terrainHeight={terrainElevation}
                  onZoneUpdated={onZoneUpdated}
                  globeControlsRef={globeControlsRef}
                  onInteractionStart={markUserInteracted}
                />
              ) : null;
            })()}

          {/* Street view pegman — hidden while a street capture is in flight
              (the marker + cone sit exactly where the capture camera stands) */}
            {streetViewPegman?.position && !streetCapturePegmanHidden && (
              <GlobePegman
                position={streetViewPegman?.position as [number, number]}
                angle={streetViewPegman.angle}
                terrainHeight={authoredCameraGround(siteZones, streetViewPegman.position[0], streetViewPegman.position[1], streetViewPegman.terrainHeight ?? terrainElevation)}
              />
            )}
          </group>
          </AutomaticParkGround>
          </ParkAssemblyGroundProvider>
          </SharedSiteGroundProvider>
        </TilesRenderer>

        {contextPresentation.loadCapture && contextPresentation.provider?.kind === '3d-tiles' && <AlternateContextLayer
          provider={contextPresentation.provider} zones={tileMaskZones} terrainHeight={terrainElevation}
          onReady={contextPresentation.onReady} onFailure={contextPresentation.onFailure} />}
        {contextPresentation.provider?.kind === 'gaussian-splat' && <GaussianContextLayer
          zones={allSiteZones} enabled={contextPresentation.loadCapture} onReady={contextPresentation.onReady} onFailure={contextPresentation.onFailure} />}

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

      {showBuildingGroundProblems && <BuildingGroundProblems issues={buildingGroundingIssues} zones={siteZones}
        onClose={() => setShowBuildingGroundProblems(false)} onSelect={zone => {
          setShowBuildingGroundProblems(false); onZoneSelected(zone.id);
          void requestProjectFrame([{ ...zone, coordinates: zone.coordinates as [number, number][] }], 'manual');
        }} />}
      {contextPresentation.provider &&
        <ContextControls requested={contextPresentation.requested} onChange={contextPresentation.select}
          geographic={contextPresentation.provider.registration === 'geographic-pilot'}
          loading={contextPresentation.loading} failed={contextPresentation.failed}>
        {contextPresentation.visible === 'capture' && <p className="mt-2 text-xs text-slate-700">
          {contextPresentation.provider.attribution} · <a className="underline" href={contextPresentation.provider.licenseUrl} target="_blank" rel="noreferrer">{contextPresentation.provider.groundAuthority === 'classified-lidar' ? 'Source and use terms' : 'CC BY 4.0'}</a>
        </p>}
        </ContextControls>}
      {showGroundReview && getActiveSiteBoundary(allSiteZones) && onPrepareGround && <GroundReviewPanel
        parks={allSiteZones.filter(z => z.zone_type === 'green_space')} onFollowParks={onFollowParkTerrain}
        boundary={getActiveSiteBoundary(allSiteZones)!} ground={sharedGroundState} onClose={() => setShowGroundReview(false)}
        onApply={(clear, height, edges) => onPrepareGround(getActiveSiteBoundary(allSiteZones)!.id, clear, height, edges)} />}
      {parkAlignment.pending&&<div role="status" className="absolute bottom-14 left-1/2 z-40 max-w-sm -translate-x-1/2 rounded-lg bg-white/95 px-3 py-2 text-sm text-slate-800 shadow">
        {parkAlignment.needsAttention?'Ground detail is difficult here. Your park is kept as a draft.':'Aligning park to ground… You can keep designing.'}
        {parkAlignment.needsAttention&&<button className="ml-2 min-h-11 underline" onClick={parkAlignment.retry}>Retry alignment</button>}
      </div>}
      {placementDraft && !interactionPaused && <>
        <div aria-hidden className="pointer-events-none absolute left-1/2 top-1/2 z-30 -translate-x-1/2 -translate-y-1/2 text-3xl font-light text-white drop-shadow sm:hidden">+</div>
        <div className="absolute bottom-6 left-1/2 z-40 w-80 max-w-[90vw] -translate-x-1/2 rounded-xl bg-white p-3 text-center text-sm text-slate-900 shadow-xl sm:bottom-auto sm:left-auto sm:right-4 sm:top-28 sm:w-72 sm:translate-x-0">
          {onPlacementDraftChange && <PlacementControls key={placementDraft.assetId} draft={placementDraft} onChange={onPlacementDraftChange} />}
          {!placementDraft.inputError && (placementProblemMessage
            ? <p role="status" className="mt-2 text-xs text-red-700">{placementProblemMessage}</p>
            : <><p className="hidden sm:block">Click a clear space to place.</p><p className="sm:hidden">Move the map to position your object.</p></>)}
          <div className="mt-2 flex justify-center gap-2"><button disabled={Boolean(placementDraft.inputError)} className="min-h-11 rounded-lg bg-lime-200 px-3 disabled:opacity-40 sm:hidden" onClick={()=>{if(placementDraft.inputError) return;const surface=raycastSurfacePoint(0,0);if(surface) onPlaceAsset?.(surface.lngLat,surface.height);}}>Place at centre</button><button className="min-h-11 rounded-lg border px-3" onClick={onCancelPlacement}>Cancel</button></div>
        </div>
      </>}
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
          desktopHint = `Click to place first ${label} point | Drag to pan | Right-drag to orbit | Scroll to zoom`;
        } else if (n < min) {
          desktopHint = `${n} point${n > 1 ? 's' : ''} - need ${min} min - Drag to pan - Backspace to undo`;
        } else {
          desktopHint = `${n} points${measurement ? ` - ${measurement}` : ''} - Drag to pan - Double-click or Enter to finish - Esc to cancel`;
        }

        return (
          <>
            <div className="pointer-events-none absolute left-1/2 top-20 z-30 max-w-[90vw] -translate-x-1/2 rounded-lg bg-gray-900/90 px-4 py-2 text-center text-xs text-white backdrop-blur-sm border border-amber-500/30 sm:hidden">
              {mobileHint}
            </div>
            <div className="pointer-events-none absolute left-1/2 bottom-24 z-30 hidden -translate-x-1/2 rounded-lg bg-gray-900/90 px-4 py-2 text-center text-xs text-white backdrop-blur-sm border border-amber-500/30 sm:block">
              {desktopHint}
              {drawingPoints.length >= min && (
                <button type="button" onClick={finishDrawing} className="pointer-events-auto ml-3 rounded bg-[#c9ff3d] px-3 py-1 font-bold text-black">
                  Finish drawing
                </button>
              )}
            </div>
          </>
        );
      })()}

      {!hasDrawingTool && streetViewPegman && (
        <div className="absolute left-1/2 top-28 z-30 max-w-[min(38rem,calc(100%-2rem))] -translate-x-1/2 rounded-xl border-2 border-[#151515] bg-[#fff9ec]/95 px-3 py-1.5 text-center text-xs font-semibold text-[#151515] shadow-[4px_4px_0_0_#151515] backdrop-blur-xl">
          {streetViewPegman?.position
            ? 'Arrow keys to rotate view | Esc to remove pegman'
            : 'Click to place street view camera'}
        </div>
      )}

      {/* 3D Globe badge + pitch + LOD status â€” offset below back button */}
      {!hasDrawingTool && !streetViewPegman && !measureModeActive && (
        <div className="pointer-events-none absolute bottom-4 left-1/2 z-20 hidden max-w-[min(38rem,calc(100%-36rem))] -translate-x-1/2 rounded-xl border border-slate-300 bg-white/95 px-3 py-2 text-center text-xs font-medium text-slate-700 shadow-lg backdrop-blur-xl select-none lg:block">
          {siteZones.some(zone => zone.id === selectedZoneId && zone.properties?.pick_place_asset)
            ? 'Drag to move | Use the reshape panel to resize or rotate | 3D updates automatically after saving | Esc to deselect'
            : selectedBuildingId && selectedZoneId
            ? '3D model selected | Edit type/floors in the panel, then Regenerate | Drag body/vertices or amber handle to move/reshape/rotate | Delete removes the model | Esc to deselect'
            : selectedBuildingId
            ? '3D model selected | Delete/Backspace to remove | Esc to deselect'
            : selectedZoneId
            ? 'Drag body to move | Drag vertices to reshape | Drag amber handle or Q/E to rotate buildings | WASD/Arrows to nudge relative to view | Ctrl+C/Ctrl+V or toolbar Copy/Paste | Delete to remove'
            : 'Click to select · Drag to pan · Right-drag to orbit · Scroll to zoom · Arrow keys to move'}
        </div>
      )}

      <div className="absolute top-32 left-4 right-4 z-20 flex items-center gap-2 overflow-x-auto [&>*]:shrink-0 sm:top-16 sm:right-4">
        <div className="rounded-full border-2 border-[#151515] bg-[#c9ff3d] px-3 py-1.5 shadow-[3px_3px_0_0_#151515] backdrop-blur-xl">
          <span className="text-[11px] font-black uppercase text-[#151515]">3D Globe</span>
        </div>
        <div className={`rounded-full border-2 border-[#151515] bg-[#fff9ec]/95 px-3 py-1.5 text-[11px] font-black uppercase shadow-[3px_3px_0_0_#151515] backdrop-blur-xl ${cameraElevationBadge.textClass}`}>
          {cameraElevation}° {cameraElevationBadge.label}
        </div>
        <button
          type="button"
          onClick={() => {
            const camera = cameraRef.current;
            const hit = focusedSiteAnchorRef.current ?? raycastSurfacePoint(0, 0);
            if (!camera || !hit) return;
            markUserInteracted();
            const [lng, lat] = hit.lngLat;
            const surface = new THREE.Vector3();
            WGS84_ELLIPSOID.getCartographicToPosition(lat * DEG_TO_RAD, lng * DEG_TO_RAD, hit.height, surface);
            const nextPitch = cameraElevation >= 85 ? DEFAULT_INITIAL_CAMERA_PITCH_DEGREES : 0;
            const height = Math.max(20, camera.position.distanceTo(surface) * Math.cos(nextPitch * DEG_TO_RAD));
            applyCameraPose(computeCameraPose(lat, lng, height, hit.height, nextPitch));
            hasAppliedSettledViewRef.current = true;
            setIsInitialCameraApplied(true);
            revealCanvasAfterPose();
          }}
          className="rounded-full border-2 border-[#151515] bg-[#fff9ec]/95 px-3 py-1.5 text-[11px] font-black uppercase shadow-[3px_3px_0_0_#151515] hover:bg-white"
          title={cameraElevation >= 85 ? 'See your community from an angle' : 'Look straight down to draw and resize footprints'}
        >
          {cameraElevation >= 85 ? '3D view' : 'Top view'}
        </button>
        {!areTilesDisplayReady && (
          <div className="flex items-center gap-1.5 rounded-full border-2 border-[#151515] bg-[#fff9ec]/95 px-3 py-1.5 shadow-[3px_3px_0_0_#151515] backdrop-blur-xl">
            <div className="h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
            <span className="text-[10px] font-black uppercase text-[#151515]/70">Loading tiles...</span>
          </div>
        )}
        {selectedInspectionZone && isBuildingZoneType(selectedInspectionZone.zone_type) && (
          <button
            type="button"
            onClick={() => {
              setZoneOverlaysVisible(false);
              void requestProjectFrame([{ ...selectedInspectionZone, coordinates: selectedInspectionZone.coordinates as [number, number][] }], 'manual');
            }}
            className="rounded-full border-2 border-[#151515] bg-[#c9ff3d] px-3 py-1.5 text-[11px] font-black uppercase text-[#151515] shadow-[3px_3px_0_0_#151515] backdrop-blur-xl transition hover:bg-[#d8ff72]"
            title="Hide planning polygons and focus on the selected building"
          >
            Focus building
          </button>
        )}
        {siteZones.length > 0 && (
          <button
            type="button"
            onClick={() => {
              void requestProjectFrame(siteZones.map(zone => ({ ...zone, coordinates: zone.coordinates as [number, number][] })), 'manual');
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
        {getActiveSiteBoundary(allSiteZones) && onPrepareGround && <button className="min-h-11 rounded-full border-2 border-[#151515] bg-[#fff9ec] px-3 text-xs font-bold" onClick={() => setShowGroundReview(true)}>Review ground</button>}
        {(sharedGroundState.status === 'sampling' || sharedGroundState.status === 'unavailable') && (
          <span role="status" className="max-w-sm rounded-xl border-2 border-[#151515] bg-[#fff9ec]/95 px-3 py-1.5 text-[11px] font-bold text-[#151515]">
            {groundReadinessMessage(sharedGroundState)}
          </span>
        )}
        {sharedGroundState.status === 'ready' && buildingGroundingIssues.some((issue) => issue.reason !== 'ground_not_ready') && (
          <button type="button" onClick={() => setShowBuildingGroundProblems(true)} className="min-h-11 rounded-full border-2 border-amber-700 bg-amber-50 px-3 py-1.5 text-[11px] font-bold text-slate-900">
            Check building ground
          </button>
        )}
      </div>
    </div>
  );
}
