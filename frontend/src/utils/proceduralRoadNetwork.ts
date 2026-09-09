import type { SiteZone } from '@/types';
import { parsePersistedCenterline } from './roadGeometry';

/** Same terminal-to-segment rule as the metric kernel; also usable for a
 * cursor ring before committing the road. Terrain altitude is not a layer. */
export function roadSnapTarget(point: number[], zones: SiteZone[], level: unknown = 0, tolerance = 1.5): number[] | null {
  const sx = 111320 * Math.cos(point[1] * Math.PI / 180);
  const sy = 111320;
  let best: number[] | null = null;
  let distance = tolerance;
  for (const zone of [...zones].sort((a, b) => a.id.localeCompare(b.id))) {
    if (zone.zone_type !== 'road' || zone.properties?.procedural_road !== 1
      || String(zone.properties?.road_level ?? 0) !== String(level)) continue;
    const line = parsePersistedCenterline(zone.properties?.plan_centerline);
    if (!line) continue;
    for (let i = 1; i < line.length; i += 1) {
      const ax = (line[i - 1][0] - point[0]) * sx;
      const ay = (line[i - 1][1] - point[1]) * sy;
      const dx = (line[i][0] - line[i - 1][0]) * sx;
      const dy = (line[i][1] - line[i - 1][1]) * sy;
      const length2 = dx * dx + dy * dy;
      if (!length2) continue;
      const t = Math.max(0, Math.min(1, -(ax * dx + ay * dy) / length2));
      const x = ax + t * dx;
      const y = ay + t * dy;
      const d = Math.hypot(x, y);
      if (d <= distance && (!best || d < distance)) {
        distance = d;
        best = [line[i - 1][0] + t * (line[i][0] - line[i - 1][0]),
          line[i - 1][1] + t * (line[i][1] - line[i - 1][1])];
      }
    }
  }
  return best;
}

export function snapRoadEndpoints(points: number[][], zones: SiteZone[], level: unknown = 0): number[][] {
  return points.map((p, i) => i === 0 || i === points.length - 1 ? roadSnapTarget(p, zones, level) ?? p : p);
}

export interface RoadNetworkSnapshot {
  version: number;
  features: GeoJSON.FeatureCollection;
  warnings: string[];
}

/** Display-only polygons. Never pass these to CRUD, history or the planner.
 * Parent IDs remain the picking IDs; multipart pieces have separate render keys.
 */
export function roadDisplayZones(zones: SiteZone[], network?: RoadNetworkSnapshot): SiteZone[] {
  if (!network) return zones;
  const byId = new Map(zones.map((zone) => [zone.id, zone]));
  const managed = new Set(network.features.features
    .filter((f) => f.properties?.kind === 'road_surface')
    .map((f) => String(f.properties?.parentRoadId)));
  const surfaces: SiteZone[] = [];
  for (const feature of network.features.features) {
    if (!['road_surface', 'intersection'].includes(String(feature.properties?.kind))) continue;
    const parent = byId.get(String(feature.properties?.parentRoadId));
    if (!parent) continue;
    const polygons = feature.geometry.type === 'Polygon' ? [feature.geometry.coordinates]
      : feature.geometry.type === 'MultiPolygon' ? feature.geometry.coordinates : [];
    for (const [index, polygon] of polygons.entries()) {
      if (!polygon[0]?.length) continue;
      // Network pieces are simple ribbons/junction patches. Do not silently
      // fill a hole if a future resolver emits a polygon with interior rings.
      if (polygon.length !== 1) return zones;
      surfaces.push({ ...parent,
        coordinates: polygon[0], properties: { ...parent.properties,
          _road_parent_id: parent.id, _road_surface: true,
          _road_surface_key: `${feature.properties?.id}:${index}` } });
    }
  }
  return [...zones.filter((zone) => !managed.has(zone.id)), ...surfaces];
}
