import { sharedSiteGroundContains } from './sharedSiteGround';
import { distanceToSegment } from './neighborhoodParkLayout';

export interface PreparedStreetSite { ring: [number, number][]; elevation: number }

/** Conceptual grading at a cleared site's public-road connection. Keep every
 * inside station on the site's declared level; meet surveyed tiles outside.
 * This does not move the site boundary or alter surrounding Google tiles. */
export function preparedStreetElevation(site: PreparedStreetSite | undefined, lng: number, lat: number, measured: number): number {
  if (!site) return measured;
  if (sharedSiteGroundContains(site.ring, lng, lat)) return site.elevation;
  const mx = 111320 * Math.cos(lat * Math.PI / 180);
  const local = site.ring.map(p => ({x:(p[0]-lng)*mx, y:(p[1]-lat)*111320}));
  const distance = Math.min(...local.map((p,i) => distanceToSegment({x:0,y:0},p,local[(i+1)%local.length])));
  const weight = Math.max(0,1-distance/10);
  return measured + (site.elevation-measured)*weight;
}
