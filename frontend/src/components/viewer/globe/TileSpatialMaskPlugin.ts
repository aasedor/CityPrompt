import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import {
  computeCentroid,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from '../mapEngine/geoUtils';

const MAX_SITE_HALF_SPACES = 32;
const SPATIAL_PATCH_STATE_KEY = '__cityPromptTileSpatialMaskPatch';
const DEG_TO_RAD = Math.PI / 180;

export interface TileSpatialMaskConfig {
  worldToLocal: THREE.Matrix4;
  halfSpaces: THREE.Vector3[];
  minHeight: number;
  maxHeight: number;
  cacheKey: string;
}

/** A single replacement footprint can use true world-coordinate clipping.
 * Unlike the projected stencil volume, this never erases Google context that
 * merely sits behind the new building in the camera view. */
export function shouldUseSpatialTileMask(zone: SiteZone): boolean {
  return [
    'site_boundary',
    'building',
    'residential',
    'development_area',
  ].includes(zone.zone_type) && zone.coordinates.length >= 3;
}

interface SpatialPatchState {
  onBeforeCompile: THREE.Material['onBeforeCompile'];
  customProgramCacheKey: THREE.Material['customProgramCacheKey'];
}

interface Point2 {
  x: number;
  y: number;
}

function cross(origin: Point2, a: Point2, b: Point2): number {
  return (a.x - origin.x) * (b.y - origin.y) - (a.y - origin.y) * (b.x - origin.x);
}

/** Monotonic-chain convex hull. Site boundaries are usually convex parcels;
 * for a concave input the hull deliberately clears the small inflection too,
 * avoiding seams in a redevelopment demolition envelope. */
export function convexHull(points: Point2[]): Point2[] {
  const sorted = [...points]
    .filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y))
    .sort((a, b) => a.x - b.x || a.y - b.y)
    .filter((point, index, all) => (
      index === 0 || point.x !== all[index - 1].x || point.y !== all[index - 1].y
    ));
  if (sorted.length <= 3) return sorted;

  const lower: Point2[] = [];
  for (const point of sorted) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], point) <= 0) {
      lower.pop();
    }
    lower.push(point);
  }
  const upper: Point2[] = [];
  for (let index = sorted.length - 1; index >= 0; index -= 1) {
    const point = sorted[index];
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], point) <= 0) {
      upper.pop();
    }
    upper.push(point);
  }
  lower.pop();
  upper.pop();
  return [...lower, ...upper];
}

export function createTileSpatialMaskConfig(
  boundary: SiteZone,
  terrainHeight: number,
): TileSpatialMaskConfig | null {
  if (!shouldUseSpatialTileMask(boundary)) return null;
  const centroid = computeCentroid(boundary.coordinates);
  const mPerLon = metersPerDegLon(centroid[1]);
  const hull = convexHull(boundary.coordinates.map(([lng, lat]) => ({
    x: (lng - centroid[0]) * mPerLon,
    y: (lat - centroid[1]) * METERS_PER_DEG_LAT,
  })));
  if (hull.length < 3 || hull.length > MAX_SITE_HALF_SPACES) return null;

  // Hull is counter-clockwise. Each left-hand normal points inward, and its
  // dot-product threshold is the half-space boundary used in the shader.
  const halfSpaces = hull.map((point, index) => {
    const next = hull[(index + 1) % hull.length];
    const dx = next.x - point.x;
    const dy = next.y - point.y;
    const length = Math.hypot(dx, dy) || 1;
    const nx = -dy / length;
    const ny = dx / length;
    return new THREE.Vector3(nx, ny, nx * point.x + ny * point.y);
  });

  const localToWorld = new THREE.Matrix4();
  WGS84_ELLIPSOID.getEastNorthUpFrame(
    centroid[1] * DEG_TO_RAD,
    centroid[0] * DEG_TO_RAD,
    terrainHeight,
    localToWorld,
  );
  const worldToLocal = localToWorld.clone().invert();
  // Google photogrammetry and the project terrain can differ by several dozen
  // metres because they do not always use the same vertical datum. World-space
  // fragment clipping does not create the projected side-wall artefacts of the
  // old stencil volume, so a generous band is both safe and more reliable.
  const minHeight = -120;
  const maxHeight = 180;
  const cacheKey = [
    boundary.id,
    terrainHeight.toFixed(2),
    ...halfSpaces.flatMap((space) => [space.x.toFixed(3), space.y.toFixed(3), space.z.toFixed(3)]),
  ].join(':');
  return { worldToLocal, halfSpaces, minHeight, maxHeight, cacheKey };
}

export function isPointInsideSpatialMask(
  point: { x: number; y: number; z: number },
  config: TileSpatialMaskConfig,
): boolean {
  return point.z >= config.minHeight
    && point.z <= config.maxHeight
    && config.halfSpaces.every((space) => (
      space.x * point.x + space.y * point.y >= space.z - 1e-6
    ));
}

export function patchMaterialForSpatialMask(
  material: THREE.Material,
  config: TileSpatialMaskConfig,
): void {
  let state = material.userData[SPATIAL_PATCH_STATE_KEY] as SpatialPatchState | undefined;
  if (!state) {
    state = {
      onBeforeCompile: material.onBeforeCompile,
      customProgramCacheKey: material.customProgramCacheKey,
    };
    material.userData[SPATIAL_PATCH_STATE_KEY] = state;
  }

  const previousOnBeforeCompile = state.onBeforeCompile;
  const previousCacheKey = state.customProgramCacheKey;
  material.onBeforeCompile = (shader, renderer) => {
    previousOnBeforeCompile.call(material, shader, renderer);
    shader.uniforms.siteMaskWorldToLocal = { value: config.worldToLocal };
    // Three.js uploads GLSL vector arrays at their declared length. Supplying
    // only the active parcel edges leaves undefined entries and can lose the
    // WebGL context while flattening the uniform, so always pad to the fixed
    // shader capacity and use the count uniform to ignore the padding.
    shader.uniforms.siteMaskHalfSpaces = {
      value: Array.from(
        { length: MAX_SITE_HALF_SPACES },
        (_, index) => config.halfSpaces[index] ?? new THREE.Vector3(),
      ),
    };
    shader.uniforms.siteMaskHalfSpaceCount = { value: config.halfSpaces.length };
    shader.uniforms.siteMaskHeightRange = {
      value: new THREE.Vector2(config.minHeight, config.maxHeight),
    };
    shader.vertexShader = shader.vertexShader
      .replace(
        '#include <common>',
        `#include <common>\nuniform mat4 siteMaskWorldToLocal;\nvarying vec3 vSiteMaskLocalPosition;`,
      )
      .replace(
        '#include <worldpos_vertex>',
        `#include <worldpos_vertex>\nvSiteMaskLocalPosition = (siteMaskWorldToLocal * modelMatrix * vec4(transformed, 1.0)).xyz;`,
      );
    shader.fragmentShader = shader.fragmentShader
      .replace(
        '#include <common>',
        `#include <common>\n#define MAX_SITE_HALF_SPACES ${MAX_SITE_HALF_SPACES}\nuniform vec3 siteMaskHalfSpaces[MAX_SITE_HALF_SPACES];\nuniform int siteMaskHalfSpaceCount;\nuniform vec2 siteMaskHeightRange;\nvarying vec3 vSiteMaskLocalPosition;`,
      )
      .replace(
        '#include <clipping_planes_fragment>',
        `#include <clipping_planes_fragment>\nbool insideSiteMask = true;\nfor (int sitePlane = 0; sitePlane < MAX_SITE_HALF_SPACES; sitePlane++) {\n  if (sitePlane < siteMaskHalfSpaceCount) {\n    vec3 halfSpace = siteMaskHalfSpaces[sitePlane];\n    if (dot(halfSpace.xy, vSiteMaskLocalPosition.xy) < halfSpace.z) insideSiteMask = false;\n  }\n}\nif (insideSiteMask && vSiteMaskLocalPosition.z >= siteMaskHeightRange.x && vSiteMaskLocalPosition.z <= siteMaskHeightRange.y) discard;`,
      );
  };
  material.customProgramCacheKey = () => `${previousCacheKey.call(material)}|site-mask:${config.cacheKey}`;
  material.needsUpdate = true;
}

export function unpatchMaterialSpatialMask(material: THREE.Material): void {
  const state = material.userData[SPATIAL_PATCH_STATE_KEY] as SpatialPatchState | undefined;
  if (!state) return;
  material.onBeforeCompile = state.onBeforeCompile;
  material.customProgramCacheKey = state.customProgramCacheKey;
  delete material.userData[SPATIAL_PATCH_STATE_KEY];
  material.needsUpdate = true;
}
