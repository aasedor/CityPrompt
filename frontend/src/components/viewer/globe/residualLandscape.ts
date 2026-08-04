import * as THREE from 'three';

import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

export type ResidualLandscapeKind =
  | 'foundation_planting'
  | 'boulevard_planting'
  | 'perimeter_planting'
  | 'lawn'
  | 'low_groundcover';

type Position = [number, number];
type PolygonCoordinates = Position[][];

export interface ResidualPolygonGeometry {
  type: 'Polygon';
  coordinates: PolygonCoordinates;
}

export interface ResidualMultiPolygonGeometry {
  type: 'MultiPolygon';
  coordinates: PolygonCoordinates[];
}

export type ResidualLandscapeGeometry = ResidualPolygonGeometry | ResidualMultiPolygonGeometry;

export interface ResidualLandscapeRegion {
  id: string;
  kind: ResidualLandscapeKind;
  area_sqm: number;
  minimum_width_m: number;
  geometry: ResidualLandscapeGeometry;
}

export interface ResidualLandscapePlacement {
  id: string;
  kind: 'tree';
  lng: number;
  lat: number;
  yaw_rad: number;
  scale: number;
}

export interface ResidualLandscapeRecipe {
  schema_version: 1;
  state: 'compiled';
  generator: 'residual_landscape';
  boundary_id: string;
  compiled_at: string;
  source_hash: string;
  metric_crs: string;
  area_sqm: number;
  occupied_area_sqm: number;
  geometry: ResidualLandscapeGeometry;
  regions: ResidualLandscapeRegion[];
  placements: ResidualLandscapePlacement[];
}

export interface ResidualLandscapeClaim {
  boundary_id: string;
  source_hash: string;
}

const REGION_KINDS = new Set<ResidualLandscapeKind>([
  'foundation_planting',
  'boulevard_planting',
  'perimeter_planting',
  'lawn',
  'low_groundcover',
]);

const BASE_PREPARED_GROUND: [number, number, number] = [151, 146, 137];
const REGION_PALETTES: Record<ResidualLandscapeKind, [number, number, number]> = {
  foundation_planting: [99, 116, 78],
  boulevard_planting: [111, 132, 79],
  perimeter_planting: [91, 121, 70],
  lawn: [104, 142, 72],
  low_groundcover: [123, 137, 92],
};

function isFinitePosition(value: unknown): value is Position {
  return Array.isArray(value)
    && value.length >= 2
    && Number.isFinite(value[0])
    && Number.isFinite(value[1]);
}

function isRing(value: unknown): value is Position[] {
  return Array.isArray(value) && value.length >= 4 && value.every(isFinitePosition);
}

function isPolygonCoordinates(value: unknown): value is PolygonCoordinates {
  return Array.isArray(value) && value.length >= 1 && value.every(isRing);
}

function isResidualGeometry(value: unknown): value is ResidualLandscapeGeometry {
  if (!value || typeof value !== 'object') return false;
  const geometry = value as Partial<ResidualLandscapeGeometry>;
  if (geometry.type === 'Polygon') {
    return Array.isArray(geometry.coordinates)
      && (geometry.coordinates.length === 0 || isPolygonCoordinates(geometry.coordinates));
  }
  if (geometry.type === 'MultiPolygon') {
    return Array.isArray(geometry.coordinates)
      && geometry.coordinates.every(isPolygonCoordinates);
  }
  return false;
}

function isRegion(value: unknown): value is ResidualLandscapeRegion {
  if (!value || typeof value !== 'object') return false;
  const region = value as Partial<ResidualLandscapeRegion>;
  return typeof region.id === 'string'
    && REGION_KINDS.has(region.kind as ResidualLandscapeKind)
    && Number.isFinite(region.area_sqm)
    && Number.isFinite(region.minimum_width_m)
    && isResidualGeometry(region.geometry);
}

function isPlacement(value: unknown): value is ResidualLandscapePlacement {
  if (!value || typeof value !== 'object') return false;
  const placement = value as Partial<ResidualLandscapePlacement>;
  return typeof placement.id === 'string'
    && placement.kind === 'tree'
    && Number.isFinite(placement.lng)
    && Number.isFinite(placement.lat)
    && Number.isFinite(placement.yaw_rad)
    && Number.isFinite(placement.scale)
    && Number(placement.scale) > 0;
}

/** Decode only current, fully compiled recipes. Stale/partial metadata is inert. */
export function getResidualLandscapeRecipe(zone: SiteZone): ResidualLandscapeRecipe | null {
  if (zone.zone_type !== 'site_boundary') return null;
  const raw = (zone.properties as Record<string, unknown> | undefined)?.community_3d_landscape;
  if (!raw || typeof raw !== 'object') return null;
  const recipe = raw as Partial<ResidualLandscapeRecipe>;
  if (
    recipe.schema_version !== 1
    || recipe.state !== 'compiled'
    || recipe.generator !== 'residual_landscape'
    || recipe.boundary_id !== zone.id
    || typeof recipe.compiled_at !== 'string'
    || typeof recipe.source_hash !== 'string'
    || typeof recipe.metric_crs !== 'string'
    || !Number.isFinite(recipe.area_sqm)
    || !Number.isFinite(recipe.occupied_area_sqm)
    || !isResidualGeometry(recipe.geometry)
    || !Array.isArray(recipe.regions)
    || !recipe.regions.every(isRegion)
    || !Array.isArray(recipe.placements)
    || !recipe.placements.every(isPlacement)
  ) {
    return null;
  }
  return recipe as ResidualLandscapeRecipe;
}

/** Direct 3D may spend credits only when an existing site-boundary recipe is
 * current. Boundary-less legacy/single-zone scenes retain their historical
 * direct-render path because they have no residual parcel contract to stale. */
export function hasCurrentResidualLandscapeRecipe(zones: SiteZone[]): boolean {
  const boundaries = zones.filter((zone) => (
    zone.zone_type === 'site_boundary' && zone.is_active_boundary !== false
  ));
  if (boundaries.length === 0) {
    const physicalZones = zones.filter((zone) => (
      zone.zone_type !== 'site_boundary'
      && (zone.properties as Record<string, unknown> | undefined)?._plan_role !== 'framework_height'
    ));
    return physicalZones.length <= 1;
  }
  return boundaries.length === 1 && getResidualLandscapeRecipe(boundaries[0]) !== null;
}

export function getCurrentResidualLandscapeClaim(
  zones: SiteZone[],
): ResidualLandscapeClaim | null {
  const boundaries = zones.filter((zone) => (
    zone.zone_type === 'site_boundary' && zone.is_active_boundary !== false
  ));
  if (boundaries.length !== 1) return null;
  const recipe = getResidualLandscapeRecipe(boundaries[0]);
  return recipe
    ? { boundary_id: boundaries[0].id, source_hash: recipe.source_hash }
    : null;
}

function pointInRingXY(x: number, y: number, ring: Position[]): boolean {
  let inside = false;
  for (let index = 0, previous = ring.length - 1; index < ring.length; previous = index++) {
    const [xi, yi] = ring[index];
    const [xj, yj] = ring[previous];
    const crosses = (yi > y) !== (yj > y)
      && x < ((xj - xi) * (y - yi)) / ((yj - yi) || Number.EPSILON) + xi;
    if (crosses) inside = !inside;
  }
  return inside;
}

export function pointInPolygonWithHoles(point: Position, coordinates: PolygonCoordinates): boolean {
  if (!coordinates.length || !pointInRingXY(point[0], point[1], coordinates[0])) return false;
  for (let index = 1; index < coordinates.length; index += 1) {
    if (pointInRingXY(point[0], point[1], coordinates[index])) return false;
  }
  return true;
}

export function pointInResidualGeometry(
  point: Position,
  geometry: ResidualLandscapeGeometry,
): boolean {
  return geometry.type === 'Polygon'
    ? pointInPolygonWithHoles(point, geometry.coordinates)
    : geometry.coordinates.some((polygon) => pointInPolygonWithHoles(point, polygon));
}

function hashText(value: string): number {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function channel(value: number): number {
  return Math.max(0, Math.min(255, Math.round(value)));
}

export function residualLandscapeBounds(coordinates: number[][]) {
  const finite = coordinates.filter((coordinate) => isFinitePosition(coordinate));
  if (!finite.length) return { west: 0, east: 1, south: 0, north: 1 };
  return {
    west: Math.min(...finite.map((coordinate) => coordinate[0])),
    east: Math.max(...finite.map((coordinate) => coordinate[0])),
    south: Math.min(...finite.map((coordinate) => coordinate[1])),
    north: Math.max(...finite.map((coordinate) => coordinate[1])),
  };
}

export interface ResidualLandscapeRegionIndex {
  gridSize: number;
  candidatesAt: (point: Position) => ResidualLandscapeRegion[];
  regionAt: (lng: number, lat: number) => ResidualLandscapeRegion | undefined;
}

interface RingBounds {
  west: number;
  east: number;
  south: number;
  north: number;
}

interface PreparedResidualRegion {
  region: ResidualLandscapeRegion;
  bounds: RingBounds;
  contains: (lng: number, lat: number) => boolean;
}

interface PreparedResidualPolygon {
  bounds: RingBounds;
  contains: (lng: number, lat: number) => boolean;
}

function containsBounds(bounds: RingBounds, lng: number, lat: number): boolean {
  return lng >= bounds.west && lng <= bounds.east
    && lat >= bounds.south && lat <= bounds.north;
}

function prepareResidualPolygon(coordinates: PolygonCoordinates): PreparedResidualPolygon {
  const [exterior = [], ...holeRings] = coordinates;
  const bounds = residualLandscapeBounds(exterior);
  const holes = holeRings.map((ring) => ({ ring, bounds: residualLandscapeBounds(ring) }));
  if (holes.length === 0) {
    return {
      bounds,
      contains: (lng, lat) => containsBounds(bounds, lng, lat)
        && pointInRingXY(lng, lat, exterior),
    };
  }

  // A residual polygon can contain hundreds of authored-building holes. Bin
  // their bounds once so a 1024² texture pixel tests only nearby holes rather
  // than scanning every authored footprint on the main render thread.
  const holeGridSize = Math.max(4, Math.min(24, Math.ceil(Math.sqrt(holes.length))));
  const holeCells = Array.from(
    { length: holeGridSize * holeGridSize },
    () => [] as typeof holes,
  );
  const spanLng = bounds.east - bounds.west || 1;
  const spanLat = bounds.north - bounds.south || 1;
  const longitudeBin = (lng: number) => Math.max(
    0,
    Math.min(holeGridSize - 1, Math.floor(((lng - bounds.west) / spanLng) * holeGridSize)),
  );
  const latitudeBin = (lat: number) => Math.max(
    0,
    Math.min(holeGridSize - 1, Math.floor(((lat - bounds.south) / spanLat) * holeGridSize)),
  );
  holes.forEach((hole) => {
    const minX = longitudeBin(hole.bounds.west);
    const maxX = longitudeBin(hole.bounds.east);
    const minY = latitudeBin(hole.bounds.south);
    const maxY = latitudeBin(hole.bounds.north);
    for (let y = minY; y <= maxY; y += 1) {
      for (let x = minX; x <= maxX; x += 1) {
        holeCells[y * holeGridSize + x].push(hole);
      }
    }
  });

  return {
    bounds,
    contains: (lng, lat) => {
      if (!containsBounds(bounds, lng, lat) || !pointInRingXY(lng, lat, exterior)) return false;
      const candidates = holeCells[latitudeBin(lat) * holeGridSize + longitudeBin(lng)];
      for (const hole of candidates) {
        if (
          containsBounds(hole.bounds, lng, lat)
          && pointInRingXY(lng, lat, hole.ring)
        ) return false;
      }
      return true;
    },
  };
}

function prepareResidualRegion(region: ResidualLandscapeRegion): PreparedResidualRegion {
  const polygonCoordinates = region.geometry.type === 'Polygon'
    ? [region.geometry.coordinates]
    : region.geometry.coordinates;
  const polygons = polygonCoordinates.map(prepareResidualPolygon);
  const bounds = polygons.length > 0
    ? {
      west: Math.min(...polygons.map((polygon) => polygon.bounds.west)),
      east: Math.max(...polygons.map((polygon) => polygon.bounds.east)),
      south: Math.min(...polygons.map((polygon) => polygon.bounds.south)),
      north: Math.max(...polygons.map((polygon) => polygon.bounds.north)),
    }
    : { west: 0, east: 0, south: 0, north: 0 };

  return {
    region,
    bounds,
    contains: (lng, lat) => containsBounds(bounds, lng, lat)
      && polygons.some((polygon) => (
        containsBounds(polygon.bounds, lng, lat) && polygon.contains(lng, lat)
      )),
  };
}

/** Keep narrow planting bands legible without allowing unbounded GPU memory.
 * Parcel views stay at 256²; roughly kilometre-scale districts step up to
 * 1024², which is about one metre per texel at the upper tier. */
export function residualLandscapeTextureSize(boundary: SiteZone): 256 | 512 | 1024 {
  const bounds = residualLandscapeBounds(boundary.coordinates);
  const meanLatitude = (bounds.south + bounds.north) / 2;
  const widthM = Math.abs(bounds.east - bounds.west) * Math.abs(metersPerDegLon(meanLatitude));
  const heightM = Math.abs(bounds.north - bounds.south) * METERS_PER_DEG_LAT;
  const required = Math.ceil(Math.max(widthM, heightM) / 1.25);
  if (required <= 256) return 256;
  if (required <= 512) return 512;
  return 1024;
}

/** Coarse spatial index that keeps texture rasterization bounded on district-
 * scale plans. Exact point-in-polygon tests still decide the winning region;
 * the grid only avoids scanning hundreds of unrelated polygons per pixel. */
export function createResidualLandscapeRegionIndex(
  regions: ResidualLandscapeRegion[],
  bounds: ReturnType<typeof residualLandscapeBounds>,
): ResidualLandscapeRegionIndex {
  const gridSize = Math.max(4, Math.min(32, Math.ceil(Math.sqrt(regions.length || 1))));
  const preparedRegions = regions.map(prepareResidualRegion);
  const cells = Array.from(
    { length: gridSize * gridSize },
    () => [] as PreparedResidualRegion[],
  );
  const spanLng = bounds.east - bounds.west || 1;
  const spanLat = bounds.north - bounds.south || 1;
  const longitudeBin = (lng: number) => Math.max(
    0,
    Math.min(gridSize - 1, Math.floor(((lng - bounds.west) / spanLng) * gridSize)),
  );
  const latitudeBin = (lat: number) => Math.max(
    0,
    Math.min(gridSize - 1, Math.floor(((lat - bounds.south) / spanLat) * gridSize)),
  );

  preparedRegions.forEach((prepared) => {
    const regionBounds = prepared.bounds;
    const minX = longitudeBin(regionBounds.west);
    const maxX = longitudeBin(regionBounds.east);
    const minY = latitudeBin(regionBounds.south);
    const maxY = latitudeBin(regionBounds.north);
    for (let y = minY; y <= maxY; y += 1) {
      for (let x = minX; x <= maxX; x += 1) {
        cells[y * gridSize + x].push(prepared);
      }
    }
  });

  return {
    gridSize,
    candidatesAt: ([lng, lat]) => {
      if (
        lng < bounds.west || lng > bounds.east
        || lat < bounds.south || lat > bounds.north
      ) return [];
      return cells[latitudeBin(lat) * gridSize + longitudeBin(lng)]
        .map((prepared) => prepared.region);
    },
    regionAt: (lng, lat) => {
      if (
        lng < bounds.west || lng > bounds.east
        || lat < bounds.south || lat > bounds.north
      ) return undefined;
      return cells[latitudeBin(lat) * gridSize + longitudeBin(lng)]
        .find((prepared) => prepared.contains(lng, lat))
        ?.region;
    },
  };
}

/** Rasterize classified polygons with an even-odd scanline fill.
 *
 * The former texture loop ran a full point-in-ring walk for every pixel. A
 * 1,000-vertex shapefile boundary therefore performed roughly one billion
 * edge tests at 1024Â² on React's main thread. Scanlines visit each edge only
 * once per intersected row, preserve polygon holes through even-odd pairing,
 * and retain the existing first-region-wins ordering for overlaps.
 */
export function rasterizeResidualLandscapeRegions(
  regions: ResidualLandscapeRegion[],
  bounds: ReturnType<typeof residualLandscapeBounds>,
  dimension: number,
): Int32Array {
  const labels = new Int32Array(dimension * dimension);
  labels.fill(-1);
  const spanLng = bounds.east - bounds.west || 1;
  const spanLat = bounds.north - bounds.south || 1;
  const pixelX = (lng: number) => ((lng - bounds.west) / spanLng) * dimension;
  const pixelY = (lat: number) => ((lat - bounds.south) / spanLat) * dimension;

  regions.forEach((region, regionIndex) => {
    const polygonCoordinates = region.geometry.type === 'Polygon'
      ? [region.geometry.coordinates]
      : region.geometry.coordinates;

    polygonCoordinates.forEach((coordinates) => {
      let vertexCount = 0;
      let minimumVertexY = Number.POSITIVE_INFINITY;
      let maximumVertexY = Number.NEGATIVE_INFINITY;
      const rings = coordinates.map((ring) => ring.map(([lng, lat]) => {
        const point: Position = [pixelX(lng), pixelY(lat)];
        vertexCount += 1;
        minimumVertexY = Math.min(minimumVertexY, point[1]);
        maximumVertexY = Math.max(maximumVertexY, point[1]);
        return point;
      }));
      if (vertexCount < 3) return;
      const minY = Math.max(0, Math.ceil(minimumVertexY - 0.5));
      const maxYExclusive = Math.min(
        dimension,
        Math.ceil(maximumVertexY - 0.5),
      );
      const intersections: number[] = [];

      for (let y = minY; y < maxYExclusive; y += 1) {
        const scanY = y + 0.5;
        intersections.length = 0;
        for (const ring of rings) {
          for (let index = 0, previous = ring.length - 1; index < ring.length; previous = index++) {
            const [x1, y1] = ring[previous];
            const [x2, y2] = ring[index];
            if ((y1 > scanY) === (y2 > scanY)) continue;
            intersections.push(x1 + ((scanY - y1) * (x2 - x1)) / (y2 - y1));
          }
        }
        intersections.sort((left, right) => left - right);
        for (let index = 0; index + 1 < intersections.length; index += 2) {
          const startX = Math.max(0, Math.ceil(intersections[index] - 0.5));
          const endXExclusive = Math.min(
            dimension,
            Math.ceil(intersections[index + 1] - 0.5),
          );
          const rowOffset = y * dimension;
          for (let x = startX; x < endXExclusive; x += 1) {
            const offset = rowOffset + x;
            if (labels[offset] === -1) labels[offset] = regionIndex;
          }
        }
      }
    });
  });

  return labels;
}

/** North-up classified aerial texture. Pixels outside the exact residual stay
 * neutral because the full-boundary mesh remains the Google-tile safety deck. */
export function createResidualLandscapeTexture(
  boundary: SiteZone,
  recipe: ResidualLandscapeRecipe,
  size?: number,
): THREE.DataTexture {
  const dimension = Math.max(16, Math.round(size ?? residualLandscapeTextureSize(boundary)));
  const bounds = residualLandscapeBounds(boundary.coordinates);
  const data = new Uint8Array(dimension * dimension * 4);
  const seed = hashText(recipe.source_hash);
  const regionLabels = rasterizeResidualLandscapeRegions(recipe.regions, bounds, dimension);

  for (let y = 0; y < dimension; y += 1) {
    for (let x = 0; x < dimension; x += 1) {
      const regionLabel = regionLabels[y * dimension + x];
      const region = regionLabel >= 0 ? recipe.regions[regionLabel] : undefined;
      const base = region ? REGION_PALETTES[region.kind] : BASE_PREPARED_GROUND;
      const broad = Math.sin((x + (seed & 255)) * 0.18) * 3.2
        + Math.cos((y + ((seed >>> 8) & 255)) * 0.14) * 2.8;
      const fine = (((Math.imul(x + 31, 1103515245) ^ Math.imul(y + seed, 12345)) >>> 24) - 128) / 32;
      const variation = broad + fine;
      const offset = (y * dimension + x) * 4;
      data[offset] = channel(base[0] + variation);
      data[offset + 1] = channel(base[1] + variation * 0.86);
      data[offset + 2] = channel(base[2] + variation * 0.62);
      data[offset + 3] = 255;
    }
  }

  const texture = new THREE.DataTexture(data, dimension, dimension, THREE.RGBAFormat);
  texture.name = `residual-landscape-${boundary.id}-${recipe.source_hash.slice(0, 10)}`;
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.ClampToEdgeWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  texture.minFilter = THREE.LinearMipmapLinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.generateMipmaps = true;
  texture.needsUpdate = true;
  return texture;
}

/** Map the terrain-grid vertices into the same geographic bbox as the recipe. */
export function applyResidualLandscapeUVs(
  geometry: THREE.BufferGeometry,
  fillCoordinates: number[][],
  boundaryCoordinates: number[][],
): void {
  const bounds = residualLandscapeBounds(boundaryCoordinates);
  const du = 1 / (bounds.east - bounds.west || 1);
  const dv = 1 / (bounds.north - bounds.south || 1);
  const uvs = new Float32Array(fillCoordinates.length * 2);
  fillCoordinates.forEach(([lng, lat], index) => {
    uvs[index * 2] = (lng - bounds.west) * du;
    uvs[index * 2 + 1] = (lat - bounds.south) * dv;
  });
  geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
}
