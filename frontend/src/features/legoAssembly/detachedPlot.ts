import { computeFootprintFrame } from '@/components/viewer/globe/buildingPlacement';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';

const DETACHED = new Set([
  'calgary_inner_city_bungalow', 'calgary_modern_infill_house', 'detached_contemporary_infill',
  'mediterranean_villa_estate', 'vancouver_craftsman_bungalow', 'vancouver_laneway_house',
]);
export function isDetachedArchetype(id?: string): boolean {
  return Boolean(id && DETACHED.has(id.replace(/_front_day$/, '').replace(/_variant_\d+$/, '')));
}

/** Exact drawn plot in the same metre frame used to place LEGO instances. */
export function detachedPlotCoordinates(
  archetypeId: string | undefined,
  coordinates: number[][] | undefined,
  target: { width_m: number; depth_m: number },
): number[][] | undefined {
  return isDetachedArchetype(archetypeId) ? assemblyFootprintCoordinates(coordinates, target) : undefined;
}

/** All fixed-native clay families need the actual polygon, including its
 * concavities, rather than only the bounding rectangle's width and depth. */
export function assemblyFootprintCoordinates(
  coordinates: number[][] | undefined,
  target: { width_m: number; depth_m: number },
): number[][] | undefined {
  if (!coordinates?.length) return undefined;
  const ring = coordinates.map((point) => point.slice(0, 2));
  if (ring.some((point) => point.length < 2 || !point.every(Number.isFinite))) return undefined;
  const last = ring[ring.length - 1];
  if (ring.length > 3 && ring[0][0] === last[0] && ring[0][1] === last[1]) ring.pop();
  const frame = computeFootprintFrame(ring);
  if (!frame) return undefined;
  const yaw = frame.bearingRad - (target.width_m >= target.depth_m ? 0 : -Math.PI / 2);
  const cos = Math.cos(yaw); const sin = Math.sin(yaw);
  const lonScale = metersPerDegLon(frame.centroidLat);
  return ring.map(([lon, lat]) => {
    const east = (lon - frame.centroidLng) * lonScale - frame.rectCenterLocal[0];
    const north = (lat - frame.centroidLat) * METERS_PER_DEG_LAT - frame.rectCenterLocal[1];
    return [Number((east * cos + north * sin).toFixed(6)), Number((east * sin - north * cos).toFixed(6))];
  });
}
