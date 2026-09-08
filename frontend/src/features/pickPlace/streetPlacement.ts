import { LOCAL_STREET_ASSET, STREET_ASSETS } from './assetRegistry';
import type { SiteZone } from '@/types';
import { bufferLineToPolygon, extractCenterline, extractZoneCenterline } from '@/utils/roadGeometry';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';

export const CALGARY_LOCAL_PLACEMENT = LOCAL_STREET_ASSET;
export const CALGARY_LOCAL_WIDTH_M = LOCAL_STREET_ASSET.sectionWidth;

export function isCalgaryLocalRoute(zone: Pick<SiteZone, 'zone_type' | 'properties'>) {
  return streetAssetForZone(zone)?.id === LOCAL_STREET_ASSET.id;
}

export function streetAssetForZone(zone: Pick<SiteZone, 'zone_type' | 'properties'>) {
  if (zone.zone_type !== 'road') return undefined;
  return STREET_ASSETS.find(asset => zone.properties?.pick_place_street_section === asset.model.variantId
    && zone.properties.road_archetype_id === asset.properties.road_archetype_id
    && zone.properties.road_selected_variant_id === asset.model.variantId);
}
export function isFixedSectionStreet(zone: Pick<SiteZone, 'zone_type' | 'properties'>) {
  return Boolean(streetAssetForZone(zone));
}
export function streetSectionWidth(zone: Pick<SiteZone, 'zone_type' | 'properties'>) {
  return streetAssetForZone(zone)?.sectionWidth ?? CALGARY_LOCAL_WIDTH_M;
}

/** Save the route and its buffer atomically, including move/undo/redo. */
export function streetCoordinateUpdate(zone: SiteZone | undefined, coordinates: number[][]) {
  return zone && isFixedSectionStreet(zone)
    ? { coordinates, properties: { ...zone.properties, width: streetSectionWidth(zone), plan_centerline: extractCenterline(coordinates) } }
    : { coordinates };
}

export function reshapeStreetPoint(coordinates: number[][], index: number, point: number[], width = CALGARY_LOCAL_WIDTH_M) {
  const line = extractCenterline(coordinates).map((p, i) => i === index ? [...point] : p);
  return bufferLineToPolygon(line, width);
}

export function streetRouteProblem(coordinates: number[][], width = CALGARY_LOCAL_WIDTH_M): string | null {
  const line = extractCenterline(coordinates);
  if (line.length < 2) return 'Place at least two route points.';
  const mLon = metersPerDegLon(line[0][1]);
  const segments = line.slice(1).map((p, i) => [(p[0] - line[i][0]) * mLon, (p[1] - line[i][1]) * METERS_PER_DEG_LAT]);
  if (segments.some(([x, y]) => Math.hypot(x, y) < width)) {
    return `Keep route points at least ${width} m apart so the full street section fits.`;
  }
  if (segments.slice(1).some(([x, y], i) => {
    const [a, b] = segments[i];
    return (x*a + y*b) / Math.hypot(x, y) / Math.hypot(a, b) < -.5;
  })) return 'Use a gentler bend. Tight switchbacks need a different street design.';
  return null;
}

export function addStreetBend(zone: SiteZone): number[][] | null {
  const width = streetSectionWidth(zone);
  const line = extractZoneCenterline(zone);
  if (line.length < 2) return null;
  const mLon = metersPerDegLon(line[0][1]);
  const lengths = line.slice(1).map((p, i) => Math.hypot((p[0]-line[i][0])*mLon, (p[1]-line[i][1])*METERS_PER_DEG_LAT));
  const longest = Math.max(...lengths);
  if (longest < 2*width) return null;
  const i = lengths.indexOf(longest);
  const next = [...line.slice(0, i+1), [(line[i][0]+line[i+1][0])/2, (line[i][1]+line[i+1][1])/2], ...line.slice(i+1)];
  return bufferLineToPolygon(next, width);
}
