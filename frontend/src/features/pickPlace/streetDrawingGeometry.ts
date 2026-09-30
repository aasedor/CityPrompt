import type { SiteZone, SiteZoneProperties } from '@/types';
import { bufferLineToPolygon, haversineDistance } from '@/components/viewer/mapEngine/geoUtils';
import { snapRoadEndpoints } from '@/utils/proceduralRoadNetwork';
import { roundAuthoredStreetRoute } from '@/utils/streetRouteCurves';
import { snapStreetEnds } from './streetSnapping';

/** One geometry path for the unsaved preview and the final authored road. */
export function streetDrawingGeometry(points: number[][], properties: SiteZoneProperties, zones: SiteZone[]): { coordinates: number[][]; properties: SiteZoneProperties } {
  const width = Number(properties.width) || 10;
  const authored = properties.pick_place_street_section
    ? snapStreetEnds(points, zones, undefined, width)
    : snapRoadEndpoints(points, zones, properties.road_level);
  const centerline = roundAuthoredStreetRoute(authored, width, properties);
  return { coordinates: bufferLineToPolygon(centerline, width), properties: {
    ...properties, plan_centerline: centerline,
    ...(properties.pick_place_street_section ? { plan_route_controls: authored } : { procedural_road: 1 }),
  } };
}

export function streetPreviewPoints(points: number[][], cursor: number[] | null) {
  const result = points.filter(p => p.length >= 2 && p.slice(0, 2).every(Number.isFinite)).map(p => [...p]);
  if (result.length && cursor && cursor.slice(0, 2).every(Number.isFinite)
    && haversineDistance(result[result.length - 1], cursor) >= .3) result.push([...cursor]);
  return result;
}
