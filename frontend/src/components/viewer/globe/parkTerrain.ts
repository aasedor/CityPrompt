import type { SiteZone } from '@/types';
import type { GroundReview } from './groundReview';
import { sharedSiteGroundContains, validateSharedSiteGroundPass, SHARED_SITE_GROUND_LIMITS, type SharedSiteGroundSnapshot } from './sharedSiteGround';

export interface ParkTerrainProfile { version: 1; snapshot: SharedSiteGroundSnapshot }
// A reviewed landscape can be steeper than a walkable route. Keep the existing
// abrupt-surface and repeatability tests; never classify a tree as bare earth.
function landscapeQuality(snapshot: SharedSiteGroundSnapshot) {
  const q = validateSharedSiteGroundPass(snapshot, snapshot.heights);
  return (q.valid || q.reason === 'discontinuity') && q.maxSlope <= 1
    && q.maxLocalResidualM <= SHARED_SITE_GROUND_LIMITS.maxLocalResidualM;
}
export function measureParkTerrain(zone: SiteZone, review?: GroundReview | null): ParkTerrainProfile | null {
  if (zone.zone_type !== 'green_space' || !review?.previousHeights || zone.coordinates.length < 3) return null;
  const g = review.layout.grid;
  const xs = zone.coordinates.map(p => (p[0] - g.west) / g.stepLng);
  const ys = zone.coordinates.map(p => (p[1] - g.south) / g.stepLat);
  const x0 = Math.max(0, Math.floor(Math.min(...xs))), x1 = Math.min(g.columns - 1, Math.ceil(Math.max(...xs)));
  const y0 = Math.max(0, Math.floor(Math.min(...ys))), y1 = Math.min(g.rows - 1, Math.ceil(Math.max(...ys)));
  if (Math.min(...xs) < 0 || Math.max(...xs) > g.columns - 1 || Math.min(...ys) < 0 || Math.max(...ys) > g.rows - 1 || x1 <= x0 || y1 <= y0) return null;
  const heights: number[] = []; let delta = 0;
  for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
    const i = y * g.columns + x, a = review.heights[i], b = review.previousHeights[i];
    if (a == null || b == null || !Number.isFinite(a) || !Number.isFinite(b)) return null;
    heights.push(a); delta = Math.max(delta, Math.abs(a - b));
  }
  if (delta > SHARED_SITE_GROUND_LIMITS.maxPassDeltaM) return null;
  const snapshot: SharedSiteGroundSnapshot = { ...review.layout, boundaryId: zone.id, boundaryUpdatedAt: zone.updated_at,
    boundaryCoordinates: zone.coordinates.map(p => [p[0], p[1]]), version: 1, source: 'google_3d_tiles', verticalReference: 'WGS84_ellipsoid',
    grid: { ...g, west: g.west + x0 * g.stepLng, south: g.south + y0 * g.stepLat, columns: x1 - x0 + 1, rows: y1 - y0 + 1 }, heights,
    quality: { sampleCount: heights.length, stablePasses: 2, maxPassDeltaM: delta, maxSlope: 0, maxLocalResidualM: 0 }, signature: '' };
  if (!landscapeQuality(snapshot)) return null;
  const quality = validateSharedSiteGroundPass(snapshot, heights);
  snapshot.quality.maxSlope = quality.maxSlope; snapshot.quality.maxLocalResidualM = quality.maxLocalResidualM;
  let hash = 2166136261;
  for (const c of JSON.stringify([snapshot.grid, snapshot.boundaryCoordinates, heights])) hash = Math.imul(hash ^ c.charCodeAt(0), 16777619);
  snapshot.signature = `reviewed-park-${(hash >>> 0).toString(16)}`;
  return { version: 1, snapshot };
}
export function readParkTerrain(zone: SiteZone): SharedSiteGroundSnapshot | null {
  const p = zone.properties?.park_terrain as ParkTerrainProfile | undefined, s = p?.snapshot;
  if (zone.zone_type !== 'green_space' || p?.version !== 1 || !s || s.source !== 'google_3d_tiles' || s.verticalReference !== 'WGS84_ellipsoid'
    || s.boundaryId !== zone.id || !Array.isArray(s.heights) || !s.grid || !Array.isArray(s.boundaryCoordinates)
    || s.heights.length > 1200 || s.heights.length !== s.grid.columns * s.grid.rows
    || !Number.isInteger(s.grid.columns) || !Number.isInteger(s.grid.rows) || s.grid.columns < 2 || s.grid.rows < 2
    || ![s.grid.west,s.grid.south,s.grid.stepLng,s.grid.stepLat].every(Number.isFinite) || s.grid.stepLng <= 0 || s.grid.stepLat <= 0
    || JSON.stringify(s.boundaryCoordinates) !== JSON.stringify(zone.coordinates.map(p => p.slice(0,2)))
    || !s.quality || s.quality.stablePasses !== 2 || !Number.isFinite(s.quality.maxPassDeltaM) || s.quality.maxPassDeltaM > .08
    || !landscapeQuality(s)) return null;
  return s;
}
export function parkTerrainContains(zone: SiteZone, lng: number, lat: number): boolean {
  return sharedSiteGroundContains(zone.coordinates.map(p => [p[0],p[1]]),lng,lat);
}
