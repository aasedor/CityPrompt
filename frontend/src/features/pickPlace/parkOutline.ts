import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { polygonOutlineProblem } from '@/utils/polygonOutline';

export type ParkOutlineShape = 'rectangle' | 'triangle' | 'l_shape';

/** Measure the whole outline, not just its first three corners. */
export function parkOutlineDimensions(coords: number[][]) {
  const origin = coords[0];
  const lonM = metersPerDegLon(origin[1]);
  const angle = Math.atan2((coords[1][1] - origin[1]) * METERS_PER_DEG_LAT, (coords[1][0] - origin[0]) * lonM);
  const c = Math.cos(angle), s = Math.sin(angle);
  const local = coords.map(([lng, lat]) => {
    const x = (lng - origin[0]) * lonM, y = (lat - origin[1]) * METERS_PER_DEG_LAT;
    return [x * c + y * s, -x * s + y * c];
  });
  const minX = Math.min(...local.map(p => p[0])), maxX = Math.max(...local.map(p => p[0]));
  const minY = Math.min(...local.map(p => p[1])), maxY = Math.max(...local.map(p => p[1]));
  const x = (minX + maxX) / 2, y = (minY + maxY) / 2;
  return { width: maxX - minX, depth: maxY - minY, degrees: angle * 180 / Math.PI,
    center: [origin[0] + (x * c - y * s) / lonM, origin[1] + (x * s + y * c) / METERS_PER_DEG_LAT],
    normalized: local.map(p => [(p[0] - minX) / (maxX - minX), (p[1] - minY) / (maxY - minY)]) };
}

export function reshapeParkOutline(coords: number[][], width: number, depth: number, degrees: number, shape?: ParkOutlineShape) {
  const frame = parkOutlineDimensions(coords);
  const points = shape === 'rectangle' ? [[0,0],[1,0],[1,1],[0,1]]
    : shape === 'triangle' ? [[0,0],[1,0],[.5,1]]
    : shape === 'l_shape' ? [[0,0],[1,0],[1,.55],[.55,.55],[.55,1],[0,1]]
    : frame.normalized;
  const angle = degrees * Math.PI / 180, c = Math.cos(angle), s = Math.sin(angle);
  return points.map(([u,v]) => {
    const x = (u - .5) * width, y = (v - .5) * depth;
    return [frame.center[0] + (x * c - y * s) / metersPerDegLon(coords[0][1]), frame.center[1] + (x * s + y * c) / METERS_PER_DEG_LAT];
  });
}

export function addParkOutlinePoint(coords: number[][]) {
  const lonM = metersPerDegLon(coords[0][1]);
  const lengths = coords.map((p, i) => {
    const q = coords[(i + 1) % coords.length];
    return Math.hypot((q[0] - p[0]) * lonM, (q[1] - p[1]) * METERS_PER_DEG_LAT);
  });
  const index = lengths.indexOf(Math.max(...lengths));
  const a = coords[index], b = coords[(index + 1) % coords.length];
  return [...coords.slice(0, index + 1), [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], ...coords.slice(index + 1)];
}

export function parkOutlineProblem(coords: number[][]): string | null {
  return polygonOutlineProblem(coords, 'park', 128);
}
