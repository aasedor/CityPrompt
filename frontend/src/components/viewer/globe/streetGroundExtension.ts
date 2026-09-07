import type { SharedSiteGroundLayout, SharedSiteGroundSnapshot } from './sharedSiteGround';
import { SHARED_SITE_GROUND_LIMITS } from './sharedSiteGround';

/** Extend coverage without shifting the site's existing samples or diagonals.
 * This prevents a short public-road connection from re-gridding all buildings. */
export function alignStreetGroundLayout(layout: SharedSiteGroundLayout, anchor: SharedSiteGroundSnapshot): SharedSiteGroundLayout | null {
  const g = anchor.grid;
  const lngs = layout.boundaryCoordinates.map(p => p[0]), lats = layout.boundaryCoordinates.map(p => p[1]);
  const x0 = Math.floor((Math.min(...lngs) - g.west) / g.stepLng);
  const y0 = Math.floor((Math.min(...lats) - g.south) / g.stepLat);
  const x1 = Math.ceil((Math.max(...lngs) - g.west) / g.stepLng);
  const y1 = Math.ceil((Math.max(...lats) - g.south) / g.stepLat);
  const columns = x1 - x0 + 1, rows = y1 - y0 + 1;
  if (columns < 2 || rows < 2 || columns * rows > SHARED_SITE_GROUND_LIMITS.maxSamples) return null;
  return { ...layout, sourceSignature: `${layout.sourceSignature}:${anchor.signature}`,
    grid: { ...g, west: g.west + x0 * g.stepLng, south: g.south + y0 * g.stepLat, columns, rows } };
}

/** Reuse an actual, already verified shared-grid vertex, including its support
 * cell beyond the site outline. Never interpolate/extrapolate missing ground. */
export function anchoredStreetGroundHeight(anchor: SharedSiteGroundSnapshot, lng: number, lat: number): number | null {
  const g = anchor.grid, x = (lng - g.west) / g.stepLng, y = (lat - g.south) / g.stepLat;
  const column = Math.round(x), row = Math.round(y);
  if (Math.abs(x - column) > 1e-6 || Math.abs(y - row) > 1e-6
    || column < 0 || row < 0 || column >= g.columns || row >= g.rows) return null;
  const height = anchor.heights[row * g.columns + column];
  return Number.isFinite(height) ? height : null;
}
