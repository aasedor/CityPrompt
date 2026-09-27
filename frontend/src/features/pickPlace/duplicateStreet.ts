import type { SiteZone, SiteZoneProperties } from '@/types';
import { extractZoneCenterline, parsePersistedCenterline } from '@/utils/roadGeometry';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';

/** Copy authored geometry and selections, never another zone's compiled receipt. */
export function duplicateStreet(zone: SiteZone, eastM: number, northM: number) {
  if (![eastM, northM].every(Number.isFinite) || Math.hypot(eastM, northM) < 1
    || Math.abs(eastM) > 1000 || Math.abs(northM) > 1000) {
    throw new Error('Move the copy at least 1 m, and keep each offset within 1,000 m.');
  }
  const line = extractZoneCenterline(zone);
  if (zone.zone_type !== 'road' || line.length < 2 || zone.properties?.validation_fixed_fixture) {
    throw new Error('Duplicate a drawn street route. Original fixed review models keep their separate bindings.');
  }
  const lngDelta = eastM / metersPerDegLon(line[0][1]), latDelta = northM / METERS_PER_DEG_LAT;
  const move = (points: number[][]) => points.map(([lng, lat]) => [lng + lngDelta, lat + latDelta]);
  const properties: SiteZoneProperties = structuredClone(zone.properties ?? {});
  for (const key of ['community_3d', 'public_realm_lego', '_client_request_id', '_client_request_hash',
    'street_network_ground_texture', 'connect_to_public_road']) delete properties[key];
  properties.plan_centerline = move(line);
  const controls = parsePersistedCenterline(zone.properties?.plan_route_controls);
  if (controls) properties.plan_route_controls = move(controls);
  return { coordinates: move(zone.coordinates), properties, zone_type: 'road' as const };
}
