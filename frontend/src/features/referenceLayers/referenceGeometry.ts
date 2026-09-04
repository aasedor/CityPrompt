import type { ReferenceGeometry, ReferencePosition } from './api';

export interface ReferencePaths { lines: ReferencePosition[][]; points: ReferencePosition[] }

/** Polygon exteriors and holes are separate outline paths, never solid buildings. */
export function referenceGeometryPaths(geometry: ReferenceGeometry): ReferencePaths {
  switch (geometry.type) {
    case 'Point': return { lines: [], points: [geometry.coordinates] };
    case 'MultiPoint': return { lines: [], points: geometry.coordinates };
    case 'LineString': return { lines: [geometry.coordinates], points: [] };
    case 'MultiLineString': return { lines: geometry.coordinates, points: [] };
    case 'Polygon': return { lines: geometry.coordinates.map(closeRing), points: [] };
    case 'MultiPolygon': return { lines: geometry.coordinates.flatMap((polygon) => polygon.map(closeRing)), points: [] };
    case 'GeometryCollection': {
      const parts = geometry.geometries.map(referenceGeometryPaths);
      return { lines: parts.flatMap((part) => part.lines), points: parts.flatMap((part) => part.points) };
    }
  }
}

function closeRing(ring: ReferencePosition[]): ReferencePosition[] {
  if (ring.length === 0) return [];
  const first = ring[0];
  const last = ring[ring.length - 1];
  return first[0] === last[0] && first[1] === last[1] ? ring : [...ring, first];
}

export function referenceFeatureLabel(properties: Record<string, unknown>, index: number): string {
  const candidates = ['name', 'label', 'district', 'zone', 'zoning', 'land_use', 'designation'];
  for (const wanted of candidates) {
    const entry = Object.entries(properties).find(([key, value]) => key.toLowerCase() === wanted && (typeof value === 'string' || typeof value === 'number'));
    if (entry && String(entry[1]).trim()) return String(entry[1]);
  }
  return `Feature ${index + 1}`;
}
