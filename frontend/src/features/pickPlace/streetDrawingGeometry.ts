import type { SiteZone, SiteZoneProperties } from '@/types';
import { modularBridgeProgramFor } from '@/components/viewer/globe/modularBridgeProgram';
import { bufferLineToPolygon, haversineDistance } from '@/components/viewer/mapEngine/geoUtils';
import { snapRoadEndpoints } from '@/utils/proceduralRoadNetwork';
import { roundAuthoredStreetRoute } from '@/utils/streetRouteCurves';
import { snapStreetEnds } from './streetSnapping';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { snapStreetToBoundary } from './streetBoundarySnapping';
import { suggestPublicRoad, type PublicRoadContext, type PublicRoadSuggestion } from './publicRoadSuggestions';
import { snapStreetBoundaryPlacement } from './streetBoundaryPlacement';
import { isSurfacePath } from './surfacePath';
import { bufferPathwayToPolygon } from '@/utils/pathwayFootprint';

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
  const geometry = { coordinates: isSurfacePath({zone_type:'road',properties})
    ? bufferPathwayToPolygon(centerline,width) : bufferLineToPolygon(centerline, width), properties: {
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

export function streetPreviewPoints(points: number[][], cursor: number[] | null, maxPoints = Infinity) {
  const result = points.filter(p => p.length >= 2 && p.slice(0, 2).every(Number.isFinite)).map(p => [...p]);
  if (result.length && result.length < maxPoints && cursor && cursor.slice(0, 2).every(Number.isFinite)
    && haversineDistance(result[result.length - 1], cursor) >= .3) result.push([...cursor]);
  return result;
}

/** Further clicks adjust the end of a two-point bridge rather than adding an unsupported bend.
 * Apply the same operation to the height array to retain its point correspondence. */
export function appendStreetDrawingValue<T>(values: T[], next: T, properties?: SiteZoneProperties | null): T[] {
  return modularBridgeProgramFor(properties?.road_selected_variant_id) && values.length >= 2
    ? [values[0], next] : [...values, next];
}

/** Browser double-click dispatches two click events first. Bridge clicks replace
 * the endpoint, while ordinary drawings append a duplicate that must be removed. */
export function finishDoubleClickValues<T>(values:T[], properties?:SiteZoneProperties|null):T[] {
  return modularBridgeProgramFor(properties?.road_selected_variant_id) ? values : values.slice(0,-1);
}
