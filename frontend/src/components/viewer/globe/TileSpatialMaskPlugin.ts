import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import {
  computeCentroid,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from '../mapEngine/geoUtils';
import { normalizeTileMaskRing, pointInTileMaskRing } from './tileMaskGeometry';

const MAX_SITE_MASKS = 8;
const MAX_SITE_EDGES = 32;
const SPATIAL_PATCH_STATE_KEY = '__cityPromptTileSpatialMaskPatch';
const DEG_TO_RAD = Math.PI / 180;

export interface TileSpatialMaskConfig {
  worldToLocal: THREE.Matrix4;
  /** Directed polygon edges; ranges preserve concave rings without a hull. */
  edges: THREE.Vector4[];
  maskRanges: THREE.Vector2[];
  maskCount: number;
  minHeight: number;
  maxHeight: number;
  cacheKey: string;
}

/** Replacement footprints use true world-coordinate clipping. Unlike the
 * projected stencil volume, this never erases Google context that merely sits
 * behind a building or authored public-realm surface in the camera view. */
export function shouldUseSpatialTileMask(zone: SiteZone): boolean {
  return [
    'site_boundary',
    'building',
    'residential',
    'development_area',
    'road',
    'street',
    'path',
    'green_space',
    'park',
    'plaza',
    'parking',
  ].includes(zone.zone_type) && zone.coordinates.length >= 3;
}

interface SpatialPatchState {
  onBeforeCompile: THREE.Material['onBeforeCompile'];
  customProgramCacheKey: THREE.Material['customProgramCacheKey'];
  config: TileSpatialMaskConfig;
}

export function createTileSpatialMaskConfig(
  boundary: SiteZone,
  terrainHeight: number,
): TileSpatialMaskConfig | null {
  return createTileSpatialMaskSetConfig([boundary], terrainHeight);
}

/** Build one true world-coordinate clipping shader for several disjoint
 * replacement footprints. All polygons share one ENU frame, so the shader
 * needs only one world transform and can test the union without projected
 * stencil side walls. */
export function createTileSpatialMaskSetConfig(
  boundaries: readonly SiteZone[],
  terrainHeight: number,
): TileSpatialMaskConfig | null {
  const usable = boundaries.filter(shouldUseSpatialTileMask);
  if (usable.length === 0 || usable.length > MAX_SITE_MASKS || !Number.isFinite(terrainHeight)) return null;
  const allCoordinates = usable.flatMap((boundary) => boundary.coordinates);
  if (allCoordinates.some(([lng, lat]) => !Number.isFinite(lng) || !Number.isFinite(lat))) return null;
  const centroid = computeCentroid(allCoordinates);
  const mPerLon = metersPerDegLon(centroid[1]);
  const edges: THREE.Vector4[] = [];
  const maskRanges: THREE.Vector2[] = [];
  for (const boundary of usable) {
    const ring = normalizeTileMaskRing(boundary.coordinates.map(([lng, lat]) => ({
      x: (lng - centroid[0]) * mPerLon,
      y: (lat - centroid[1]) * METERS_PER_DEG_LAT,
    })));
    if (
      !ring
      || edges.length + ring.length > MAX_SITE_EDGES
    ) {
      return null;
    }
    const offset = edges.length;
    ring.forEach((point, index) => {
      const next = ring[(index + 1) % ring.length];
      edges.push(new THREE.Vector4(point.x, point.y, next.x, next.y));
    });
    maskRanges.push(new THREE.Vector2(offset, ring.length));
  }

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
    'exact-polygon-v2',
    ...usable.map((boundary) => boundary.id),
    // Location is part of the mask identity even if a translated site's local
    // shape is unchanged. Reusing its old program otherwise keeps old uniforms.
    ...centroid.map((value) => value.toFixed(10)),
    terrainHeight.toFixed(2),
    ...maskRanges.flatMap((range) => [range.x, range.y]),
    ...edges.flatMap((edge) => [edge.x, edge.y, edge.z, edge.w].map((value) => value.toFixed(6))),
  ].join(':');
  return {
    worldToLocal,
    edges,
    maskRanges,
    maskCount: maskRanges.length,
    minHeight,
    maxHeight,
    cacheKey,
  };
}

export function isPointInsideSpatialMask(
  point: { x: number; y: number; z: number },
  config: TileSpatialMaskConfig,
): boolean {
  return point.z >= config.minHeight
    && point.z <= config.maxHeight
    && config.maskRanges.some((range) => (
      pointInTileMaskRing(point, config.edges
        .slice(range.x, range.x + range.y)
        .map((edge) => ({ x: edge.x, y: edge.y })))
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
      config,
    };
    material.userData[SPATIAL_PATCH_STATE_KEY] = state;
  }
  state.config = config;

  const previousOnBeforeCompile = state.onBeforeCompile;
  const previousCacheKey = state.customProgramCacheKey;
  material.onBeforeCompile = (shader, renderer) => {
    previousOnBeforeCompile.call(material, shader, renderer);
    shader.uniforms.siteMaskWorldToLocal = { value: config.worldToLocal };
    // Three.js uploads GLSL vector arrays at their declared length. Supplying
    // only the active parcel edges leaves undefined entries and can lose the
    // WebGL context while flattening the uniform, so always pad to the fixed
    // shader capacity and use the count uniform to ignore the padding.
    shader.uniforms.siteMaskEdges = {
      value: Array.from(
        { length: MAX_SITE_EDGES },
        (_, index) => config.edges[index] ?? new THREE.Vector4(),
      ),
    };
    shader.uniforms.siteMaskEdgeCount = { value: config.edges.length };
    shader.uniforms.siteMaskRanges = {
      value: Array.from(
        { length: MAX_SITE_MASKS },
        (_, index) => config.maskRanges[index] ?? new THREE.Vector2(),
      ),
    };
    shader.uniforms.siteMaskCount = { value: config.maskCount };
    shader.uniforms.siteMaskHeightRange = {
      value: new THREE.Vector2(config.minHeight, config.maxHeight),
    };
    shader.vertexShader = shader.vertexShader
      .replace(
        '#include <common>',
        `#include <common>\nuniform mat4 siteMaskWorldToLocal;\nvarying vec3 vSiteMaskLocalPosition;`,
      )
      .replace(
        '#include <project_vertex>',
        `#include <project_vertex>
vec4 siteMaskPosition = vec4(transformed, 1.0);
#ifdef USE_BATCHING
  siteMaskPosition = batchingMatrix * siteMaskPosition;
#endif
#ifdef USE_INSTANCING
  siteMaskPosition = instanceMatrix * siteMaskPosition;
#endif
vSiteMaskLocalPosition = (siteMaskWorldToLocal * modelMatrix * siteMaskPosition).xyz;`,
      );
    const fragmentDeclarations = `#define MAX_SITE_MASKS ${MAX_SITE_MASKS}\n#define MAX_SITE_EDGES ${MAX_SITE_EDGES}\nuniform vec4 siteMaskEdges[MAX_SITE_EDGES];\nuniform int siteMaskEdgeCount;\nuniform vec2 siteMaskRanges[MAX_SITE_MASKS];\nuniform int siteMaskCount;\nuniform vec2 siteMaskHeightRange;\nvarying vec3 vSiteMaskLocalPosition;`;
    // MeshNormalMaterial has no <common> fragment chunk. Prefix declarations
    // so beauty, depth and normal variants all receive the same coverage test.
    shader.fragmentShader = `${fragmentDeclarations}\n${shader.fragmentShader}`
      .replace(
        '#include <clipping_planes_fragment>',
        `#include <clipping_planes_fragment>
bool insideAnySiteMask = false;
vec2 sitePoint = vSiteMaskLocalPosition.xy;
for (int siteMask = 0; siteMask < MAX_SITE_MASKS; siteMask++) {
  if (siteMask < siteMaskCount) {
    vec2 siteRange = siteMaskRanges[siteMask];
    bool insideCurrentSiteMask = false;
    bool onSiteBoundary = false;
    for (int siteEdge = 0; siteEdge < MAX_SITE_EDGES; siteEdge++) {
      float siteEdgeIndex = float(siteEdge);
      if (siteEdge < siteMaskEdgeCount && siteEdgeIndex >= siteRange.x && siteEdgeIndex < siteRange.x + siteRange.y) {
        vec4 edge = siteMaskEdges[siteEdge];
        vec2 a = edge.xy;
        vec2 b = edge.zw;
        vec2 direction = b - a;
        float edgeCross = direction.x * (sitePoint.y - a.y) - direction.y * (sitePoint.x - a.x);
        if (abs(edgeCross) <= 0.000001 * max(1.0, length(direction))
            && all(greaterThanEqual(sitePoint, min(a, b) - vec2(0.000001)))
            && all(lessThanEqual(sitePoint, max(a, b) + vec2(0.000001)))) onSiteBoundary = true;
        // Horizontal edges never divide by zero. The half-open crossing rule
        // counts shared vertices once and preserves re-entrant corners.
        if ((a.y > sitePoint.y) != (b.y > sitePoint.y)) {
          float crossingX = direction.x * (sitePoint.y - a.y) / direction.y + a.x;
          if (sitePoint.x < crossingX) insideCurrentSiteMask = !insideCurrentSiteMask;
        }
      }
    }
    if (insideCurrentSiteMask || onSiteBoundary) insideAnySiteMask = true;
  }
}
if (insideAnySiteMask && vSiteMaskLocalPosition.z >= siteMaskHeightRange.x && vSiteMaskLocalPosition.z <= siteMaskHeightRange.y) discard;`,
      );
  };
  material.customProgramCacheKey = () => `${previousCacheKey.call(material)}|site-mask:${config.cacheKey}`;
  material.needsUpdate = true;
}

/** Capture depth/normal variants must apply the same spatial cut as beauty. */
export function inheritTileSpatialMask(source: THREE.Material, target: THREE.Material): void {
  const state = source.userData[SPATIAL_PATCH_STATE_KEY] as SpatialPatchState | undefined;
  if (state) patchMaterialForSpatialMask(target, state.config);
}

export function unpatchMaterialSpatialMask(material: THREE.Material): void {
  const state = material.userData[SPATIAL_PATCH_STATE_KEY] as SpatialPatchState | undefined;
  if (!state) return;
  material.onBeforeCompile = state.onBeforeCompile;
  material.customProgramCacheKey = state.customProgramCacheKey;
  delete material.userData[SPATIAL_PATCH_STATE_KEY];
  material.needsUpdate = true;
}
