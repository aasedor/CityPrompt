import { sharedSiteGroundContains } from './sharedSiteGround';
import { distanceToSegment } from './neighborhoodParkLayout';
import type { LocalPt, StreetStationTerrain } from './streetMesh3D';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

export interface PreparedStreetSite { ring: [number, number][]; elevation: number }

/** Editable preview while the public-road end is measured. Every inside band
 * already has an authoritative level; outside heights remain provisional. */
export function preparedStreetPreview(site: PreparedStreetSite, points: LocalPt[], normals: LocalPt[],
  origin: {lng: number; lat: number}, halfWidth: number, frameElevation: number): StreetStationTerrain[] {
  const mx = metersPerDegLon(origin.lat);
  return points.map((point, index) => {
    const at = (offset: number) => preparedStreetElevation(site,
      origin.lng + (point.x + normals[index].x * offset) / mx,
      origin.lat + (point.y + normals[index].y * offset) / METERS_PER_DEG_LAT,
      frameElevation) - frameElevation;
    return {centerZ: at(0), leftZ: at(halfWidth), rightZ: at(-halfWidth), halfWidthM: halfWidth};
  });
}

/** A centre hit alone cannot establish the two sidewalk edges. */
export function completeStreetStation(sample: {center: number | null; left: number | null; right: number | null}): boolean {
  return Object.values(sample).every(value => value !== null && Number.isFinite(value));
}

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
