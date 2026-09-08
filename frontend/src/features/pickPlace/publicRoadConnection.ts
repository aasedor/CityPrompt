import type { SiteZone } from '@/types';
import { extractCenterline } from '@/utils/roadGeometry';
import { sharedSiteGroundContains } from '@/components/viewer/globe/sharedSiteGround';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';

/** Early editing feedback; the server independently validates the whole buffer,
 * outside length, width and parcel overlap before persisting a connection. */
export function publicRoadConnectionFits(zone: SiteZone, coordinates: number[][], boundary?: SiteZone | null): boolean {
  if (zone.zone_type !== 'road' || zone.properties?.connect_to_public_road !== true || !boundary) return false;
  const ring = boundary.coordinates as [number, number][];
  const contains = (point: number[]) => sharedSiteGroundContains(ring, point[0], point[1]);
  const line = extractCenterline(coordinates);
  if (line.length < 2 || contains(line[0]) === contains(line[line.length - 1])) return false;
  const mLon = metersPerDegLon(line[0][1]);
  let outsideLength = 0, total = 0, transitions = 0, previous = contains(line[0]);
  for (let i = 1; i < line.length; i++) {
    const a = line[i - 1], b = line[i];
    const length = Math.hypot((b[0] - a[0]) * mLon, (b[1] - a[1]) * METERS_PER_DEG_LAT);
    if (!Number.isFinite(length) || length > 2000) return false;
    const steps = Math.max(1, Math.ceil(length / 0.25)); total += length;
    for (let j = 1; j <= steps; j++) {
      const inside = contains([a[0] + (b[0] - a[0]) * j / steps, a[1] + (b[1] - a[1]) * j / steps]);
      if (!inside) outsideLength += length / steps;
      if (inside !== previous) transitions++;
      previous = inside;
    }
  }
  return transitions === 1 && outsideLength <= 30 && outsideLength < total / 2;
}
