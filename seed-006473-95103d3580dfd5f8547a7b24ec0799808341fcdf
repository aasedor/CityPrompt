import { haversineDistance } from '../mapEngine/geoUtils';

// Keep the close gesture local to the visible start marker. A former 30 m
// radius consumed legitimate fourth vertices on ordinary narrow footprints.
export const POLYGON_CLOSE_RADIUS_METERS = 3;

export function isWithinPolygonCloseRadius(distanceMeters: number): boolean {
  return distanceMeters <= POLYGON_CLOSE_RADIUS_METERS;
}

/**
 * Remove the near-duplicate vertex produced when a user clicks the first
 * polygon vertex to close a drawing. The API closes polygon rings itself, so
 * retaining this click creates a tiny spike that can self-intersect after the
 * globe raycast is converted back to longitude/latitude.
 */
export function normalizePolygonDrawing(
  coordinates: number[][],
  closingToleranceMeters = 2,
): number[][] {
  const normalized = coordinates.map((coordinate) => [...coordinate]);
  if (
    normalized.length >= 4
    && haversineDistance(normalized[0], normalized[normalized.length - 1]) <= closingToleranceMeters
  ) {
    normalized.pop();
  }
  return normalized;
}
