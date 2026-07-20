import { haversineDistance } from '../mapEngine/geoUtils';

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
