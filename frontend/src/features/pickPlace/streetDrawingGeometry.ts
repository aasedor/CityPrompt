import type { SiteZone, SiteZoneProperties } from '@/types';
import { bufferLineToPolygon, haversineDistance } from '@/components/viewer/mapEngine/geoUtils';
import { snapRoadEndpoints } from '@/utils/proceduralRoadNetwork';
import { roundAuthoredStreetRoute } from '@/utils/streetRouteCurves';
import { snapStreetEnds } from './streetSnapping';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { snapStreetToBoundary } from './streetBoundarySnapping';
import { suggestPublicRoad, type PublicRoadContext, type PublicRoadSuggestion } from './publicRoadSuggestions';
import { snapStreetBoundaryPlacement } from './streetBoundaryPlacement';

/** One geometry path for the unsaved preview and the final authored road. */
export function streetDrawingGeometry(points: number[][], properties: SiteZoneProperties, zones: SiteZone[], options: {
  publicRoads?: PublicRoadContext; skipSnapping?: boolean;
} = {}): { coordinates: number[][]; properties: SiteZoneProperties; suggestion?: PublicRoadSuggestion } {
  const width = Number(properties.width) || 10;
  const boundary = getActiveSiteBoundary(zones);
  const connection = !options.skipSnapping && suggestPublicRoad(points, properties, zones, boundary, options.publicRoads);
  if (connection) return connection;
  const bounded = options.skipSnapping ? points : snapStreetToBoundary(points, width, boundary, properties);
  const authored = options.skipSnapping ? points : properties.pick_place_street_section
    ? snapStreetEnds(bounded, zones, undefined, width)
    : snapRoadEndpoints(bounded, zones, properties.road_level);
  const centerline = roundAuthoredStreetRoute(authored, width, properties);
  const geometry = { coordinates: bufferLineToPolygon(centerline, width), properties: {
    ...properties, plan_centerline: centerline,
    ...(properties.pick_place_street_section ? { plan_route_controls: authored } : { procedural_road: 1 }),
  } };
  if (options.skipSnapping) return geometry;
  const snapped = snapStreetBoundaryPlacement({
    id: 'boundary-street-preview', zone_type: 'road', project_id: '', color: '',
    sort_order: 0, created_at: '', updated_at: '', ...geometry,
  }, zones, boundary);
  return { coordinates: snapped.coordinates, properties: snapped.properties };
}

export function streetPreviewPoints(points: number[][], cursor: number[] | null) {
  const result = points.filter(p => p.length >= 2 && p.slice(0, 2).every(Number.isFinite)).map(p => [...p]);
  if (result.length && cursor && cursor.slice(0, 2).every(Number.isFinite)
    && haversineDistance(result[result.length - 1], cursor) >= .3) result.push([...cursor]);
  return result;
}
