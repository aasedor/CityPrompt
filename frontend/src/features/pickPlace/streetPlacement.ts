import streetCatalogue from '@/data/streetPathArchetypes.json';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { bufferLineToPolygon, extractCenterline, extractZoneCenterline } from '@/utils/roadGeometry';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';

const source = streetCatalogue.archetypes.find(entry => entry.id === 'calgary_local')!;
export const CALGARY_LOCAL_PLACEMENT = {
  label: 'Calgary local street',
  description: '16 m wide · sidewalks and tree boulevards',
  properties: {
    ...source.propertyPresets,
    road_archetype_id: source.id,
    road_selected_variant_id: 'calgary_local_v0',
    pick_place_street_section: 'calgary_local_v0',
    pick_place_automatic_3d: true,
    road_standard_citation: 'Street Manual Draft 4.0, Figure 2',
  } as SiteZoneProperties,
};
export const CALGARY_LOCAL_WIDTH_M = source.section!.row_m;

export function isCalgaryLocalRoute(zone: Pick<SiteZone, 'zone_type' | 'properties'>) {
  return zone.zone_type === 'road' && zone.properties?.pick_place_street_section === 'calgary_local_v0'
    && zone.properties.road_archetype_id === 'calgary_local'
    && zone.properties.road_selected_variant_id === 'calgary_local_v0';
}

/** Save the route and its buffer atomically, including move/undo/redo. */
export function streetCoordinateUpdate(zone: SiteZone | undefined, coordinates: number[][]) {
  return zone && isCalgaryLocalRoute(zone)
    ? { coordinates, properties: { ...zone.properties, width: CALGARY_LOCAL_WIDTH_M, plan_centerline: extractCenterline(coordinates) } }
    : { coordinates };
}

export function reshapeStreetPoint(coordinates: number[][], index: number, point: number[]) {
  const line = extractCenterline(coordinates).map((p, i) => i === index ? [...point] : p);
  return bufferLineToPolygon(line, CALGARY_LOCAL_WIDTH_M);
}

export function streetRouteProblem(coordinates: number[][]): string | null {
  const line = extractCenterline(coordinates);
  if (line.length < 2) return 'Place at least two route points.';
  const mLon = metersPerDegLon(line[0][1]);
  const segments = line.slice(1).map((p, i) => [(p[0] - line[i][0]) * mLon, (p[1] - line[i][1]) * METERS_PER_DEG_LAT]);
  if (segments.some(([x, y]) => Math.hypot(x, y) < CALGARY_LOCAL_WIDTH_M)) {
    return 'Keep route points at least 16 m apart so the full street section fits.';
  }
  if (segments.slice(1).some(([x, y], i) => {
    const [a, b] = segments[i];
    return (x*a + y*b) / Math.hypot(x, y) / Math.hypot(a, b) < -.5;
  })) return 'Use a gentler bend. Tight switchbacks need a different street design.';
  return null;
}

export function addStreetBend(zone: SiteZone): number[][] | null {
  const line = extractZoneCenterline(zone);
  const mLon = metersPerDegLon(line[0][1]);
  const lengths = line.slice(1).map((p, i) => Math.hypot((p[0]-line[i][0])*mLon, (p[1]-line[i][1])*METERS_PER_DEG_LAT));
  const longest = Math.max(...lengths);
  if (longest < 2*CALGARY_LOCAL_WIDTH_M) return null;
  const i = lengths.indexOf(longest);
  const next = [...line.slice(0, i+1), [(line[i][0]+line[i+1][0])/2, (line[i][1]+line[i+1][1])/2], ...line.slice(i+1)];
  return bufferLineToPolygon(next, CALGARY_LOCAL_WIDTH_M);
}
