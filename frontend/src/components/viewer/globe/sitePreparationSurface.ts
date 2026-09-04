import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { isCommunity3DCompiled } from '@/features/community3d/community3d';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { normalizeTileMaskRing, pointInTileMaskRing, type TileMaskPoint } from './tileMaskGeometry';

/** Whether this scene already contains compiled authored 3D content. */
export function hasCompiledCommunity(zones: SiteZone[]): boolean {
  return zones.some((zone) => isCommunity3DCompiled(zone));
}

export function getPreparedSiteBoundaryIds(zones: SiteZone[]): Set<string> {
  const activeBoundary = getActiveSiteBoundary(zones);
  const properties = activeBoundary?.properties as Record<string, unknown> | undefined;
  return activeBoundary && properties?.community_3d_mask_existing_tiles !== false
    ? new Set([activeBoundary.id])
    : new Set();
}

/** One authoritative elevation for both the whole-site tile mask and its
 * prepared replacement surface. Letting either side independently raycast
 * photogrammetry shifts their projected edges apart and exposes a blue/sky
 * apron that makes the proposal look sunken. */
export function resolvePreparedSiteTerrainHeight(
  boundary: SiteZone,
  fallbackTerrainHeight: number,
): number {
  const properties = boundary.properties as Record<string, unknown> | undefined;
  const stored = Number(
    properties?.terrain_elevation_m
    ?? properties?.terrain_height
    ?? properties?.terrainElevation,
  );
  return Number.isFinite(stored) ? stored : fallbackTerrainHeight;
}

/** Authored objects wholly inside a cleared site share its declared datum.
 * Existing context and zones in a concave notch retain their own terrain. */
export function resolvePreparedSiteTerrainForZone(
  zone: SiteZone | undefined,
  zones: SiteZone[],
  fallbackTerrainHeight: number,
): number | null {
  const boundary = getActiveSiteBoundary(zones);
  if (!zone || !boundary || !getPreparedSiteBoundaryIds(zones).has(boundary.id)) return null;
  if (zone.id !== boundary.id && !preparedSiteContainsZone(boundary, zone)) return null;
  return resolvePreparedSiteTerrainHeight(boundary, fallbackTerrainHeight);
}

/** Split every authored edge at boundary intersections, then test every open
 * interval. Vertex/quartile sampling can miss a narrow concave notch. */
export function preparedSiteContainsZone(boundary: SiteZone, zone: SiteZone): boolean {
  const origin = boundary.coordinates[0];
  if (!origin) return false;
  const east = 111320 * Math.cos(origin[1] * Math.PI / 180);
  const local = (ring: number[][]) => normalizeTileMaskRing(ring.map(([lng, lat]) => ({
    x: (lng - origin[0]) * east, y: (lat - origin[1]) * 111320,
  })));
  const outer = local(boundary.coordinates), inner = local(zone.coordinates);
  if (!outer || !inner || !inner.every((point) => pointInTileMaskRing(point, outer))) return false;
  const cross = (a: TileMaskPoint, b: TileMaskPoint) => a.x * b.y - a.y * b.x;
  for (let index = 0; index < inner.length; index += 1) {
    const a = inner[index], b = inner[(index + 1) % inner.length];
    const r = { x: b.x - a.x, y: b.y - a.y };
    const cuts = [0, 1];
    for (let edge = 0; edge < outer.length; edge += 1) {
      const c = outer[edge], d = outer[(edge + 1) % outer.length];
      const s = { x: d.x - c.x, y: d.y - c.y }, delta = { x: c.x - a.x, y: c.y - a.y };
      const denominator = cross(r, s);
      if (Math.abs(denominator) < 1e-10) continue;
      const t = cross(delta, s) / denominator, u = cross(delta, r) / denominator;
      if (t > 0 && t < 1 && u >= 0 && u <= 1) cuts.push(t);
    }
    cuts.sort((left, right) => left - right);
    for (let cut = 1; cut < cuts.length; cut += 1) {
      const t = (cuts[cut - 1] + cuts[cut]) / 2;
      if (!pointInTileMaskRing({ x: a.x + r.x * t, y: a.y + r.y * t }, outer)) return false;
    }
  }
  return true;
}

export const PREPARED_SITE_BACKING_SEPARATION_METERS = 0.06;

export function createPreparedSiteBackingGeometry(source: THREE.BufferGeometry, seed: string): THREE.BufferGeometry {
  return createSitePreparationGeometry(source, seed).translate(0, 0, -PREPARED_SITE_BACKING_SEPARATION_METERS);
}

/** A standalone replacement building still clips the source Google mesh, but
 * older/manual projects may not have a separate site-boundary zone whose
 * prepared surface can cover the cleared footprint. In that case mount a
 * terrain-toned surface under the model so uncovered setbacks and irregular
 * silhouettes do not reveal the scene background as a white apron. */
export function shouldRenderReplacementFootprintGround(
  zone: SiteZone,
  suppressed: boolean,
  sitePrepared: boolean,
): boolean {
  return shouldMaskReplacementBuildingTiles(zone, suppressed)
    && !sitePrepared
    && zone.coordinates.length >= 3;
}

/** Empty or already-cleared parcels can opt out of cutting the Google mesh.
 * Respect that explicit project decision for both the tile mask and its
 * replacement apron; otherwise an unnecessary mask reveals the sky-clear
 * colour around a model that sits on valid existing terrain. */
export function shouldMaskReplacementBuildingTiles(
  zone: SiteZone,
  suppressed: boolean,
): boolean {
  const props = zone.properties as Record<string, unknown> | undefined;
  return suppressed
    && props?.community_3d_mask_existing_tiles !== false
    && ['building', 'residential', 'development_area', 'development'].includes(zone.zone_type);
}

function hashSeed(value: string): number {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0) / 0xffffffff;
}

function clamp01(value: number): number {
  return Math.max(0, Math.min(1, value));
}

function mixChannel(a: number, b: number, amount: number): number {
  return Math.round(a + (b - a) * clamp01(amount));
}

/** Deterministic aerial ground texture for the residual parcel between
 * authored streets, parks and buildings. Dense texture is important here:
 * vertex colours alone interpolate across the site's large terrain triangles
 * and read as one opaque brown planning slab at district scale. */
export function createSitePreparationTexture(seed: string, size = 256): THREE.DataTexture {
  const dimension = Math.max(16, Math.round(size));
  const data = new Uint8Array(dimension * dimension * 4);
  const phase = hashSeed(seed) * Math.PI * 2;
  // Keep residual redevelopment ground close to desaturated aerial imagery.
  // The former vegetation-heavy olive average made a compiled district read
  // as one green planning slab and visually swallowed authored parks.
  const earth = [150, 144, 134];
  const vegetation = [119, 130, 110];
  const aggregate = [171, 168, 160];

  for (let y = 0; y < dimension; y += 1) {
    for (let x = 0; x < dimension; x += 1) {
      const nx = x / dimension;
      const ny = y / dimension;
      const broad = (
        Math.sin(nx * Math.PI * 5.2 + phase)
        + Math.cos(ny * Math.PI * 4.4 - phase * 0.7)
        + Math.sin((nx + ny) * Math.PI * 3.1 + phase * 1.4)
      ) / 6 + 0.5;
      const fine = (
        Math.sin(x * 0.73 + y * 0.31 + phase * 3.7)
        + Math.cos(x * 0.19 - y * 0.67 - phase)
      ) * 0.25 + 0.5;
      // Residual land is mostly neutral retained earth and aggregate. A small
      // amount of seeded cover breaks up the parcel without competing with
      // the authored green-space polygons at district scale.
      const vegetationMix = clamp01(0.08 + broad * 0.22 + (fine - 0.5) * 0.06);
      const aggregateSignal = (
        Math.sin(nx * Math.PI * 8.3 - phase * 0.4)
        + Math.cos(ny * Math.PI * 7.1 + phase)
      ) * 0.25 + 0.5;
      const aggregateMix = clamp01((aggregateSignal - 0.66) * 1.45) * 0.4;

      const r = mixChannel(mixChannel(earth[0], vegetation[0], vegetationMix), aggregate[0], aggregateMix);
      const g = mixChannel(mixChannel(earth[1], vegetation[1], vegetationMix), aggregate[1], aggregateMix);
      const b = mixChannel(mixChannel(earth[2], vegetation[2], vegetationMix), aggregate[2], aggregateMix);
      const offset = (y * dimension + x) * 4;
      data[offset] = r;
      data[offset + 1] = g;
      data[offset + 2] = b;
      data[offset + 3] = 255;
    }
  }

  const texture = new THREE.DataTexture(data, dimension, dimension, THREE.RGBAFormat);
  texture.name = `prepared-site-${seed}`;
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.minFilter = THREE.LinearMipmapLinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.generateMipmaps = true;
  texture.needsUpdate = true;
  return texture;
}

/** Warm unit-paver texture for compiled woonerfs. The live tile scene needs
 * enough small-scale construction evidence to read as a shared street rather
 * than a flat planning polygon, while staying deterministic and credit-free. */
export function createWoonerfPaverTexture(seed: string, size = 256): THREE.DataTexture {
  const dimension = Math.max(32, Math.round(size));
  const data = new Uint8Array(dimension * dimension * 4);
  const phase = Math.floor(hashSeed(seed) * 97);
  const brickWidth = 24;
  const brickHeight = 10;
  const mortar = [183, 160, 139];
  const brickA = [156, 92, 65];
  const brickB = [177, 109, 75];

  for (let y = 0; y < dimension; y += 1) {
    const row = Math.floor(y / brickHeight);
    const offsetX = row % 2 === 0 ? 0 : brickWidth / 2;
    for (let x = 0; x < dimension; x += 1) {
      const localX = (x + offsetX + phase) % brickWidth;
      const localY = (y + phase) % brickHeight;
      const isJoint = localX < 1.6 || localY < 1.4;
      const variation = (
        Math.sin((x + phase) * 0.31) + Math.cos((y - phase) * 0.43)
      ) * 4;
      const base = isJoint ? mortar : ((row + Math.floor((x + offsetX) / brickWidth)) % 3 === 0 ? brickB : brickA);
      const pixel = (y * dimension + x) * 4;
      data[pixel] = Math.max(0, Math.min(255, Math.round(base[0] + variation)));
      data[pixel + 1] = Math.max(0, Math.min(255, Math.round(base[1] + variation)));
      data[pixel + 2] = Math.max(0, Math.min(255, Math.round(base[2] + variation)));
      data[pixel + 3] = 255;
    }
  }

  const texture = new THREE.DataTexture(data, dimension, dimension, THREE.RGBAFormat);
  texture.name = `woonerf-pavers-${seed}`;
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.minFilter = THREE.LinearMipmapLinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.generateMipmaps = true;
  texture.needsUpdate = true;
  return texture;
}

/** Clone a terrain grid and give it low-frequency earth/vegetation variation.
 * The residual site surface reads as prepared landscape instead of a flat
 * planning polygon, while roads, parks and buildings render above it. */
export function createSitePreparationGeometry(
  source: THREE.BufferGeometry,
  seed: string,
): THREE.BufferGeometry {
  const geometry = source.clone();
  const positions = geometry.getAttribute('position') as THREE.BufferAttribute | undefined;
  if (!positions) return geometry;

  // Keep the palette compatible with aerial photogrammetry, but separate the
  // three values enough that a cleared parcel reads as soil, retained ground
  // cover and aggregate rather than a single opaque planning slab.
  const earth = new THREE.Color('#968c7e');
  const vegetation = new THREE.Color('#77826e');
  const aggregate = new THREE.Color('#aaa69d');
  const colors = new Float32Array(positions.count * 3);
  const uvs = new Float32Array(positions.count * 2);
  const phase = hashSeed(seed) * Math.PI * 2;
  let minX = Infinity;
  let maxX = -Infinity;
  let minY = Infinity;
  let maxY = -Infinity;

  for (let index = 0; index < positions.count; index += 1) {
    minX = Math.min(minX, positions.getX(index));
    maxX = Math.max(maxX, positions.getX(index));
    minY = Math.min(minY, positions.getY(index));
    maxY = Math.max(maxY, positions.getY(index));
  }
  const spanX = Math.max(1, maxX - minX);
  const spanY = Math.max(1, maxY - minY);
  const shortSpan = Math.min(spanX, spanY);
  const repeatsX = Math.max(4, (spanX / shortSpan) * 4);
  const repeatsY = Math.max(4, (spanY / shortSpan) * 4);

  for (let index = 0; index < positions.count; index += 1) {
    const x = positions.getX(index);
    const y = positions.getY(index);
    const broad = (Math.sin(x * 0.045 + phase) + Math.cos(y * 0.052 - phase)) * 0.25 + 0.5;
    const fine = (Math.sin((x + y) * 0.21 + phase * 1.7) + 1) * 0.5;
    const color = earth.clone().lerp(vegetation, Math.max(0, Math.min(0.28, broad * 0.28)));
    color.lerp(aggregate, fine * 0.18);
    colors[index * 3] = color.r;
    colors[index * 3 + 1] = color.g;
    colors[index * 3 + 2] = color.b;
    uvs[index * 2] = ((x - minX) / spanX) * repeatsX;
    uvs[index * 2 + 1] = ((y - minY) / spanY) * repeatsY;
  }

  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
  return geometry;
}

/** Extend a prepared surface slightly beyond a spatial clipping boundary.
 * The excess remains hidden below surviving Google tiles, while preventing a
 * one-pixel sky/background seam caused by independent shader and mesh edge
 * rasterization. */
export function overlapPreparedGroundEdges(
  geometry: THREE.BufferGeometry,
  overlapMeters = 0.6,
): THREE.BufferGeometry {
  const positions = geometry.getAttribute('position') as THREE.BufferAttribute | undefined;
  if (!positions || positions.count === 0 || overlapMeters <= 0) return geometry;

  geometry.computeBoundingBox();
  const bounds = geometry.boundingBox;
  if (!bounds) return geometry;
  const centerX = (bounds.min.x + bounds.max.x) / 2;
  const centerY = (bounds.min.y + bounds.max.y) / 2;
  const spanX = Math.max(0.01, bounds.max.x - bounds.min.x);
  const spanY = Math.max(0.01, bounds.max.y - bounds.min.y);
  const scaleX = 1 + (overlapMeters * 2) / spanX;
  const scaleY = 1 + (overlapMeters * 2) / spanY;
  for (let index = 0; index < positions.count; index += 1) {
    positions.setX(index, centerX + (positions.getX(index) - centerX) * scaleX);
    positions.setY(index, centerY + (positions.getY(index) - centerY) * scaleY);
  }
  positions.needsUpdate = true;
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();
  return geometry;
}
