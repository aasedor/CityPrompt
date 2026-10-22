import type { SiteZone } from '@/types';

export const MAX_MAP_CLEANUP_BOXES = 4;
export interface MapCleanupBox {
  id: string;
  lng: number;
  lat: number;
  /** Absolute ellipsoid elevation of the box centre, not ground offset. */
  altitude: number;
  width: number;
  depth: number;
  height: number;
  yaw: number;
  enabled: boolean;
}

/** Malformed or excessive cleanup data must never broaden a map cut. */
export function validMapCleanupBoxes(value: unknown): MapCleanupBox[] {
  if (!Array.isArray(value) || value.length > MAX_MAP_CLEANUP_BOXES) return [];
  const ids = new Set<string>();
  return value.filter((item): item is MapCleanupBox => {
    if (!item || typeof item !== 'object') return false;
    const box = item as MapCleanupBox;
    if (typeof box.id !== 'string' || !/^[\w-]{1,80}$/.test(box.id) || ids.has(box.id)
      || typeof box.enabled !== 'boolean'
      || ![box.lng, box.lat, box.altitude, box.width, box.depth, box.height, box.yaw].every(Number.isFinite)
      || Math.abs(box.lng) > 180 || Math.abs(box.lat) > 85
      || box.altitude < -500 || box.altitude > 9000 || Math.abs(box.yaw) > 360
      || [box.width, box.depth, box.height].some(size => size < 0.2 || size > 20)) return false;
    ids.add(box.id);
    return true;
  });
}

export function readMapCleanupBoxes(zones: readonly SiteZone[]): MapCleanupBox[] {
  const values = zones.filter(zone => zone.zone_type === 'site_boundary')
    .flatMap(zone => {
      const data = zone.properties?.map_cleanup as { version?: unknown; boxes?: unknown } | undefined;
      return data?.version === 1 ? validMapCleanupBoxes(data.boxes) : [];
    });
  return validMapCleanupBoxes(values);
}
