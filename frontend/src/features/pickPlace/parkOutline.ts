import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';

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
  if (coords.length < 3 || coords.length > 128 || coords.some(p => p.length < 2 || !p.slice(0,2).every(Number.isFinite))) return 'Use a park outline with 3–128 corners.';
  const lonM = metersPerDegLon(coords[0][1]);
  const points = coords.map(p => [(p[0] - coords[0][0]) * lonM, (p[1] - coords[0][1]) * METERS_PER_DEG_LAT]);
  const cross = (a: number[], b: number[], c: number[]) => (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  const on = (a: number[], b: number[], p: number[]) => Math.abs(cross(a,b,p)) < 1e-7 && p[0] >= Math.min(a[0],b[0])-1e-7 && p[0] <= Math.max(a[0],b[0])+1e-7 && p[1] >= Math.min(a[1],b[1])-1e-7 && p[1] <= Math.max(a[1],b[1])+1e-7;
  for (let i = 0; i < points.length; i++) {
    const a = points[i], b = points[(i + 1) % points.length];
    if (Math.hypot(b[0]-a[0],b[1]-a[1]) < .25) return 'Leave a little space between neighbouring park corners.';
    for (let j = i + 2; j < points.length; j++) {
      if (i === 0 && j === points.length - 1) continue;
      const c = points[j], d = points[(j + 1) % points.length];
      if ((cross(a,b,c)*cross(a,b,d)<0 && cross(c,d,a)*cross(c,d,b)<0) || on(a,b,c) || on(a,b,d) || on(c,d,a) || on(c,d,b)) return 'The park outline crosses itself. Move the corner back so the edges do not cross.';
    }
  }
  const area = Math.abs(points.reduce((sum,p,i) => {const q=points[(i+1)%points.length];return sum+p[0]*q[1]-q[0]*p[1];},0))/2;
  return area < 1 ? 'Give the park a little more area.' : null;
}
