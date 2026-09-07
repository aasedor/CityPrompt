import { envelopeFits, envelopesOverlap } from '@/components/viewer/globe/neighborhoodParkLayout';
import type { SiteZone } from '@/types';
import { computeCentroid, METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import type { PlaceAsset } from './catalogue';

export function rectangleAt(center: number[], width: number, depth: number, degrees = 0): number[][] {
  const yaw = degrees * Math.PI / 180, c = Math.cos(yaw), s = Math.sin(yaw);
  return [[-1,-1],[1,-1],[1,1],[-1,1]].map(([x,y]) => [
    center[0] + (x * width / 2 * c - y * depth / 2 * s) / metersPerDegLon(center[1]),
    center[1] + (x * width / 2 * s + y * depth / 2 * c) / METERS_PER_DEG_LAT,
  ]);
}
export function rectangleDimensions(coords: number[][]) {
  const center = computeCentroid(coords);
  const dx = (coords[1][0] - coords[0][0]) * metersPerDegLon(center[1]);
  const dy = (coords[1][1] - coords[0][1]) * METERS_PER_DEG_LAT;
  const depth = Math.hypot((coords[2][0]-coords[1][0]) * metersPerDegLon(center[1]),
    (coords[2][1]-coords[1][1]) * METERS_PER_DEG_LAT);
  return { center, width: Math.hypot(dx,dy), depth, degrees: Math.atan2(dy,dx)*180/Math.PI };
}

/** Keep the opposite corner fixed, preserve right angles and native-size limits. */
export function resizeRectangleCorner(coords: number[][], corner: number, pointer: number[], asset: PlaceAsset) {
  const { degrees } = rectangleDimensions(coords);
  const fixed = coords[(corner+2)%4], yaw = degrees*Math.PI/180, c=Math.cos(yaw), s=Math.sin(yaw);
  const east=(pointer[0]-fixed[0])*metersPerDegLon(fixed[1]), north=(pointer[1]-fixed[1])*METERS_PER_DEG_LAT;
  const sx = corner===0 || corner===3 ? -1 : 1, sy=corner<2 ? -1 : 1;
  const width=Math.min(asset.maxSize,Math.max(asset.minWidth,sx*(east*c+north*s)));
  const depth=Math.min(asset.maxSize,Math.max(asset.minDepth,sy*(-east*s+north*c)));
  return rectangleAt([
    fixed[0]+(sx*width*c-sy*depth*s)/2/metersPerDegLon(fixed[1]),
    fixed[1]+(sx*width*s+sy*depth*c)/2/METERS_PER_DEG_LAT,
  ],width,depth,degrees);
}
export function placementProblem(coords: number[][], zones: SiteZone[], boundary?: SiteZone | null, ignoreId?: string): string | null {
  try {
    if(coords.length<3 || coords.some(p=>!Number.isFinite(p[0]+p[1]))) return 'Choose a valid area.';
    const origin=coords[0];
    const local=(ring:number[][])=>ring.map(p=>({x:(p[0]-origin[0])*metersPerDegLon(origin[1]),y:(p[1]-origin[1])*METERS_PER_DEG_LAT}));
    const footprint = local(coords);
    if (boundary && !envelopeFits(footprint,local(boundary.coordinates))) return 'Keep the whole object inside your site boundary.';
    for (const zone of zones) {
      if (zone.id===ignoreId || !['building','residential','green_space','parking'].includes(zone.zone_type)) continue;
      if (envelopesOverlap(footprint,local(zone.coordinates))) return 'This overlaps another building plot or park. Plots include the space around buildings. Move it into a clear space.';
    }
    return null;
  } catch { return 'This area cannot be placed yet. Check the site outline.'; }
}
