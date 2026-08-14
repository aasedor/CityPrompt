import {
  computeCentroid,
  haversineDistance,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from '../mapEngine/geoUtils';

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

/**
 * Build a live drawing surface in one local ENU frame while preserving the
 * independently sampled height of every click. Photogrammetry is rarely
 * planar: putting the whole preview at its average height buries edges and
 * triangles on sloped or reconstructed terrain even though the point markers
 * themselves remain visible.
 */
export function buildTerrainRelativeDrawingVertices(
  coordinates: number[][],
  pointHeights: number[],
  frameHeight: number,
  liftMeters: number,
  closeLoop = false,
): number[] {
  if (coordinates.length === 0) return [];

  const centroid = computeCentroid(coordinates);
  const metresPerLongitudeDegree = metersPerDegLon(centroid[1]);
  const vertices: number[] = [];
  const appendVertex = (coordinate: number[], index: number) => {
    const pointHeight = Number.isFinite(pointHeights[index])
      ? pointHeights[index]
      : frameHeight;
    vertices.push(
      (coordinate[0] - centroid[0]) * metresPerLongitudeDegree,
      (coordinate[1] - centroid[1]) * METERS_PER_DEG_LAT,
      pointHeight - frameHeight + liftMeters,
    );
  };

  coordinates.forEach(appendVertex);
  if (closeLoop && coordinates.length >= 3) appendVertex(coordinates[0], 0);
  return vertices;
}
