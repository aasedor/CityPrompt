import type { SiteZone } from '@/types';
import { extractZoneCenterline } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';

/** The building front is local -Y (the compiler's coordinate contract).
 * Resolve once at placement; later context refinement must not rotate a design. */
export function streetFacingDegrees(point: number[], zones: SiteZone[], fallback = 0): number {
  const routes = new Map<string, number[][]>();
  for (const zone of zones) {
    if (zone.zone_type === 'road' && !zone.properties?._imported_from) routes.set(`proposal:${zone.id}`, extractZoneCenterline(zone));
    for (const road of zone.properties?._osm_context?.roads ?? []) {
      if (['motorway', 'motorway_link', 'trunk', 'trunk_link', 'footway', 'path', 'cycleway', 'steps', 'bridleway'].includes(road.road_type)) continue;
      routes.set(`existing:${road.osm_id}`, road.coordinates);
    }
  }
  const lonM = metersPerDegLon(point[1]);
  let best: { distance: number; x: number; y: number; proposal: boolean } | undefined;
  for (const [id, route] of [...routes].sort(([a], [b]) => a.localeCompare(b))) {
    const proposal = id.startsWith('proposal:');
    for (let i = 1; i < route.length; i++) {
      const a = [(route[i - 1][0] - point[0]) * lonM, (route[i - 1][1] - point[1]) * METERS_PER_DEG_LAT];
      const b = [(route[i][0] - point[0]) * lonM, (route[i][1] - point[1]) * METERS_PER_DEG_LAT];
      const dx = b[0] - a[0], dy = b[1] - a[1], lengthSquared = dx * dx + dy * dy;
      if (!Number.isFinite(lengthSquared) || lengthSquared < 1) continue;
      const t = Math.min(1, Math.max(0, -(a[0] * dx + a[1] * dy) / lengthSquared));
      const x = a[0] + t * dx, y = a[1] + t * dy, distance = Math.hypot(x, y);
      if (distance < .5 || distance > 100 || (best && (best.proposal && !proposal || best.proposal === proposal && distance >= best.distance - .001))) continue;
      best = { distance, x, y, proposal };
    }
  }
  return best ? (Math.atan2(best.x, -best.y) * 180 / Math.PI + 360) % 360 : fallback;
}
