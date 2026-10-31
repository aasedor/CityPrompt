import clipping, { type MultiPolygon, type Polygon } from 'polygon-clipping';

/** Flat pathways can fold back or cross themselves. Union full-width segment
 * surfaces and round joins instead of saving a self-intersecting miter strip. */
export function pathwaySurfacePolygons(points: readonly number[][], width: number): MultiPolygon {
  if (points.length < 2 || !(width > 0) || !Number.isFinite(width)) return [];
  const pieces: Polygon[] = [];
  const radius = width / 2;
  for (let i = 1; i < points.length; i++) {
    const [x, y] = points[i - 1], [endX, endY] = points[i];
    const length = Math.hypot(endX - x, endY - y);
    if (length < 1e-8) continue;
    const nx = -(endY - y) / length * radius, ny = (endX - x) / length * radius;
    pieces.push([[
      [x + nx, y + ny], [endX + nx, endY + ny],
      [endX - nx, endY - ny], [x - nx, y - ny], [x + nx, y + ny],
    ]]);
  }
  for (const [x, y] of points.slice(1, -1)) {
    const ring: [number, number][] = Array.from({ length: 24 }, (_, i) => {
      const angle = i * Math.PI / 12;
      return [x + Math.cos(angle) * radius, y + Math.sin(angle) * radius];
    });
    pieces.push([[...ring, ring[0]]]);
  }
  return pieces.length ? clipping.union(pieces[0], ...pieces.slice(1)) : [];
}

/** Zone footprints use an exterior ring; source route/controls retain the
 * exact walking route, and the rendered surface also retains enclosed holes. */
export function bufferPathwayToPolygon(points: number[][], width: number): number[][] {
  if (points.length < 2) return points;
  const [lng, lat] = points[0], sx = 111320 * Math.cos(lat * Math.PI / 180), sy = 111320;
  if (!(sx > 1)) return [];
  const polygons = pathwaySurfacePolygons(points.map(([x, y]) => [(x - lng) * sx, (y - lat) * sy]), width);
  if (polygons.length !== 1) return [];
  return polygons[0][0].slice(0, -1).map(([x, y]) => [lng + x / sx, lat + y / sy]);
}
