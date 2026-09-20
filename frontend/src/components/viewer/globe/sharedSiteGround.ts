import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

export type SharedGroundPoint = [number, number];
export interface SharedSiteGroundGrid {
  west: number; south: number; columns: number; rows: number; stepLng: number; stepLat: number;
}
export interface SharedSiteGroundLayout {
  boundaryId: string;
  boundaryUpdatedAt: string;
  boundaryCoordinates: SharedGroundPoint[];
  sourceSignature: string;
  grid: SharedSiteGroundGrid;
}
export interface SharedSiteGroundSnapshot extends SharedSiteGroundLayout {
  version: 1;
  source: 'google_3d_tiles' | 'classified_lidar';
  verticalReference: 'WGS84_ellipsoid';
  /** South-to-north rows, west-to-east columns. No absent samples. Google
   * vertices are measured; classified survey derivation is recorded separately. */
  heights: number[];
  quality: {
    /** Two live mesh passes, or zero for an immutable saved survey source. */
    sampleCount: number; stablePasses: 2 | 0; maxPassDeltaM: number; maxSlope: number; maxLocalResidualM: number;
  };
  signature: string;
}

export const SHARED_SITE_GROUND_LIMITS = Object.freeze({
  maxSamples: 1200, targetSpacingM: 2.5, maxSpacingM: 12,
  maxSlope: 0.45, maxLocalResidualM: 0.6, maxPassDeltaM: 0.08,
  // A broad physical plausibility check rejects the unrefined -28 km root
  // tile seen in Calgary. It never clamps a tile height to an elevation API.
  minHeightM: -1000, maxHeightM: 10000,
});

export function sharedGroundSignature(value: unknown): string {
  const text = JSON.stringify(value); let hash = 2166136261;
  for (let i = 0; i < text.length; i += 1) hash = Math.imul(hash ^ text.charCodeAt(i), 16777619);
  return `ssg1-${(hash >>> 0).toString(16).padStart(8, '0')}`;
}

export function sharedSiteGroundSourceSignature(boundary: SiteZone, spacingM?: number): string {
  // A compiled landscape or label changes the row revision, not the ground.
  // Capture provenance binds the latest row revision separately in the provider.
  return sharedGroundSignature([boundary.id, boundary.coordinates, boundary.is_active_boundary,
    boundary.properties?.community_3d_mask_existing_tiles, ...(spacingM === undefined ? [] : [spacingM])]);
}

/** Boundary-inclusive domain test; a concave notch never becomes terrain. */
export function sharedSiteGroundContains(ring: readonly SharedGroundPoint[], lng: number, lat: number): boolean {
  if (!Number.isFinite(lng) || !Number.isFinite(lat) || ring.length < 3) return false;
  const east = metersPerDegLon(lat);
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [ax, ay] = ring[j], [bx, by] = ring[i];
    const dx = bx - ax, dy = by - ay;
    const t = Math.max(0, Math.min(1, ((lng - ax) * dx + (lat - ay) * dy) / (dx * dx + dy * dy || 1)));
    // Float32 mesh corners and clipped edges can land micrometres beyond the
    // exact polygon. Include a 1 mm seam, including endpoints; never extend
    // the ground across a concave notch or a meaningful off-site distance.
    if (Math.hypot((lng - ax - t * dx) * east, (lat - ay - t * dy) * METERS_PER_DEG_LAT) <= .001) return true;
    if ((ay > lat) !== (by > lat) && lng < (bx - ax) * (lat - ay) / (by - ay) + ax) inside = !inside;
  }
  return inside;
}

/** The rectangular support grid is fully measured, including boundary cells.
 * Interpolation is exposed only within the exact geographic boundary. */
export function createSharedSiteGroundLayout(boundary: SiteZone, spacingM?: number): SharedSiteGroundLayout | null {
  const ring = boundary.coordinates.map((point): SharedGroundPoint => [point[0], point[1]]);
  if (ring.length < 3 || ring.length > 2048 || ring.some(([lng, lat]) => !Number.isFinite(lng) || !Number.isFinite(lat)
    || Math.abs(lng) > 180 || Math.abs(lat) > 85)) return null;
  const west = Math.min(...ring.map((p) => p[0])), east = Math.max(...ring.map((p) => p[0]));
  const south = Math.min(...ring.map((p) => p[1])), north = Math.max(...ring.map((p) => p[1]));
  const width = (east - west) * metersPerDegLon((north + south) / 2), height = (north - south) * METERS_PER_DEG_LAT;
  if (width < 0.1 || height < 0.1) return null;
  let spacing = spacingM ?? SHARED_SITE_GROUND_LIMITS.targetSpacingM;
  if (!Number.isFinite(spacing) || spacing <= 0 || spacing > SHARED_SITE_GROUND_LIMITS.maxSpacingM) return null;
  let columns = Math.ceil(width / spacing) + 1, rows = Math.ceil(height / spacing) + 1;
  while (columns * rows > SHARED_SITE_GROUND_LIMITS.maxSamples) {
    spacing *= 1.05;
    if (spacing > SHARED_SITE_GROUND_LIMITS.maxSpacingM) return null;
    columns = Math.ceil(width / spacing) + 1; rows = Math.ceil(height / spacing) + 1;
  }
  return { boundaryId: boundary.id, boundaryUpdatedAt: boundary.updated_at, boundaryCoordinates: ring,
    sourceSignature: sharedSiteGroundSourceSignature(boundary, spacingM),
    grid: { west, south, columns, rows, stepLng: (east - west) / (columns - 1), stepLat: (north - south) / (rows - 1) } };
}

export function sharedSiteGroundGridPoint(layout: SharedSiteGroundLayout, index: number): SharedGroundPoint {
  const { west, south, columns, stepLng, stepLat } = layout.grid;
  return [west + index % columns * stepLng, south + Math.floor(index / columns) * stepLat];
}

export interface SharedSiteGroundPassQuality {
  valid: boolean; reason: string | null; maxSlope: number; maxLocalResidualM: number;
}

/** Include every cell touching the boundary, even a thin sliver with no grid
 * vertex inside. Remote corners of the bounding rectangle cannot affect it. */
export function groundCellTouchesBoundary(layout: SharedSiteGroundLayout, x: number, y: number): boolean {
  const { west, south, stepLng, stepLat } = layout.grid;
  const ring = layout.boundaryCoordinates.map(([lng, lat]) => [(lng - west) / stepLng - x, (lat - south) / stepLat - y]);
  const insideBox = ([a, b]: number[]) => a >= -1e-8 && a <= 1 + 1e-8 && b >= -1e-8 && b <= 1 + 1e-8;
  if (ring.some(insideBox)) return true;
  if ([[0,0],[1,0],[1,1],[0,1]].some(([a,b]) => sharedSiteGroundContains(layout.boundaryCoordinates, west+(x+a)*stepLng, south+(y+b)*stepLat))) return true;
  for (let i = 0; i < ring.length; i++) {
    const a = ring[i], b = ring[(i+1)%ring.length];
    let low = 0, high = 1;
    for (let axis = 0; axis < 2; axis++) {
      const delta = b[axis] - a[axis];
      if (Math.abs(delta) < 1e-12) { if (a[axis] < -1e-8 || a[axis] > 1+1e-8) { high = -1; break; } }
      else {
        const t0 = (-1e-8-a[axis])/delta, t1 = (1+1e-8-a[axis])/delta;
        low = Math.max(low, Math.min(t0,t1)); high = Math.min(high, Math.max(t0,t1));
      }
    }
    if (low <= high) return true;
  }
  return false;
}

/** Reject suspicious discontinuities instead of replacing an unobserved ground
 * height. A consistent roof or smooth embankment can still pass: this is tile
 * surface evidence, not a survey or automatic bare-earth classification. */
export function validateSharedSiteGroundPass(layout: SharedSiteGroundLayout, heights: readonly (number | null)[],
  onDiscontinuity?: (sampleIndices: readonly number[]) => void): SharedSiteGroundPassQuality {
  const { columns, rows, stepLng, stepLat, south } = layout.grid;
  const invalid = (reason: string): SharedSiteGroundPassQuality => ({ valid: false, reason, maxSlope: 0, maxLocalResidualM: 0 });
  if (heights.length !== columns * rows || heights.some((height) => height === null || !Number.isFinite(height))) return invalid('missing_samples');
  const values = heights as readonly number[];
  if (values.some((height) => height < SHARED_SITE_GROUND_LIMITS.minHeightM || height > SHARED_SITE_GROUND_LIMITS.maxHeightM)) return invalid('implausible_height');
  const dx = stepLng * metersPerDegLon(south + stepLat * (rows - 1) / 2), dy = stepLat * METERS_PER_DEG_LAT;
  let maxSlope = 0, maxLocalResidualM = 0;
  const support = new Set<number>();
  for (let y = 0; y < rows - 1; y += 1) for (let x = 0; x < columns - 1; x += 1) {
    if (!groundCellTouchesBoundary(layout, x, y)) continue;
    for (const index of [y*columns+x, y*columns+x+1, (y+1)*columns+x, (y+1)*columns+x+1]) support.add(index);
    const sw = values[y * columns + x], se = values[y * columns + x + 1];
    const nw = values[(y + 1) * columns + x], ne = values[(y + 1) * columns + x + 1];
    // The two actual triangle gradients, split on the SW–NE diagonal.
    const slope = Math.max(Math.hypot((se - sw) / dx, (ne - se) / dy), Math.hypot((ne - nw) / dx, (nw - sw) / dy));
    maxSlope = Math.max(maxSlope, slope);
    if (slope > SHARED_SITE_GROUND_LIMITS.maxSlope)
      onDiscontinuity?.([y*columns+x, y*columns+x+1, (y+1)*columns+x, (y+1)*columns+x+1]);
  }
  for (let y = 1; y < rows - 1; y += 1) for (let x = 1; x < columns - 1; x += 1) {
    const index = y * columns + x;
    if (![index, index-1, index+1, index-columns, index+columns].every(i => support.has(i))) continue;
    const neighbors = (values[index - 1] + values[index + 1] + values[index - columns] + values[index + columns]) / 4;
    const residual = Math.abs(values[index] - neighbors);
    maxLocalResidualM = Math.max(maxLocalResidualM, residual);
    if (residual > SHARED_SITE_GROUND_LIMITS.maxLocalResidualM) onDiscontinuity?.([index]);
  }
  const valid = Number.isFinite(maxSlope) && maxSlope <= SHARED_SITE_GROUND_LIMITS.maxSlope
    && maxLocalResidualM <= SHARED_SITE_GROUND_LIMITS.maxLocalResidualM;
  return { valid, reason: valid ? null : 'discontinuity', maxSlope, maxLocalResidualM };
}

/** Two independent complete passes must agree at every vertex. Never fill a
 * missing cell from neighbours, an API average, or a stored boundary height. */
export function createSharedSiteGroundSnapshot(layout: SharedSiteGroundLayout, previous: readonly (number | null)[], current: readonly (number | null)[]): SharedSiteGroundSnapshot | null {
  const previousQuality = validateSharedSiteGroundPass(layout, previous), quality = validateSharedSiteGroundPass(layout, current);
  if (!previousQuality.valid || !quality.valid) return null;
  const heights = current as readonly number[];
  const maxPassDeltaM = Math.max(...heights.map((height, index) => Math.abs(height - previous[index]!)));
  if (maxPassDeltaM > SHARED_SITE_GROUND_LIMITS.maxPassDeltaM) return null;
  const snapshot = { ...layout, version: 1 as const, source: 'google_3d_tiles' as const, verticalReference: 'WGS84_ellipsoid' as const,
    heights: [...heights], quality: { sampleCount: heights.length, stablePasses: 2 as const, maxPassDeltaM,
      maxSlope: quality.maxSlope, maxLocalResidualM: quality.maxLocalResidualM } };
  return { ...snapshot, signature: sharedGroundSignature(snapshot) };
}

/** Piecewise planar, not bilinear: every consumer samples identical triangles. */
export function sampleSharedSiteGround(snapshot: SharedSiteGroundSnapshot | null | undefined, lng: number, lat: number): number | null {
  if (!snapshot || !sharedSiteGroundContains(snapshot.boundaryCoordinates, lng, lat)) return null;
  const { west, south, columns, rows, stepLng, stepLat } = snapshot.grid;
  const gx = Math.max(0, Math.min(columns - 1, (lng - west) / stepLng)), gy = Math.max(0, Math.min(rows - 1, (lat - south) / stepLat));
  const x = Math.min(columns - 2, Math.floor(gx)), y = Math.min(rows - 2, Math.floor(gy));
  const u = gx - x, v = gy - y;
  const sw = snapshot.heights[y * columns + x], se = snapshot.heights[y * columns + x + 1];
  const nw = snapshot.heights[(y + 1) * columns + x], ne = snapshot.heights[(y + 1) * columns + x + 1];
  if (![sw, se, nw, ne].every(Number.isFinite)) return null;
  return v <= u ? sw * (1 - u) + se * (u - v) + ne * v : sw * (1 - v) + nw * (v - u) + ne * u;
}
