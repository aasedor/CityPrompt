import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';

/** Check simple student outlines in a local metric frame, including touching edges. */
export function polygonOutlineProblem(coords: number[][], label: string, maxCorners = Infinity): string | null {
  const outline = label === 'site boundary' ? label : `${label} outline`;
  if (coords.length < 3 || coords.length > maxCorners || coords.some(p => p.length < 2 || !p.slice(0,2).every(Number.isFinite))) {
    return `Use a ${outline} with ${Number.isFinite(maxCorners) ? `3–${maxCorners}` : 'at least 3'} corners.`;
  }
  const lonM = metersPerDegLon(coords[0][1]);
  const points = coords.map(p => [(p[0] - coords[0][0]) * lonM, (p[1] - coords[0][1]) * METERS_PER_DEG_LAT]);
  const cross = (a: number[], b: number[], c: number[]) => (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  const on = (a: number[], b: number[], p: number[]) => Math.abs(cross(a,b,p)) < 1e-7 && p[0] >= Math.min(a[0],b[0])-1e-7 && p[0] <= Math.max(a[0],b[0])+1e-7 && p[1] >= Math.min(a[1],b[1])-1e-7 && p[1] <= Math.max(a[1],b[1])+1e-7;
  for (let i = 0; i < points.length; i++) {
    const a = points[i], b = points[(i + 1) % points.length];
    if (Math.hypot(b[0]-a[0],b[1]-a[1]) < .25) return `Leave a little space between neighbouring ${label} corners.`;
    for (let j = i + 2; j < points.length; j++) {
      if (i === 0 && j === points.length - 1) continue;
      const c = points[j], d = points[(j + 1) % points.length];
      if ((cross(a,b,c)*cross(a,b,d)<0 && cross(c,d,a)*cross(c,d,b)<0) || on(a,b,c) || on(a,b,d) || on(c,d,a) || on(c,d,b)) return `The ${outline} crosses itself. Move the corner back so the edges do not cross.`;
    }
  }
  const area = Math.abs(points.reduce((sum,p,i) => {const q=points[(i+1)%points.length];return sum+p[0]*q[1]-q[0]*p[1];},0))/2;
  return area < 1 ? `Give the ${label} a little more area.` : null;
}
