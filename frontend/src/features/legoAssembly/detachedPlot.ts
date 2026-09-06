import { computeFootprintFrame } from '@/components/viewer/globe/buildingPlacement';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';

const DETACHED = new Set([
  'calgary_inner_city_bungalow', 'calgary_modern_infill_house', 'detached_contemporary_infill',
  'mediterranean_villa_estate', 'vancouver_craftsman_bungalow', 'vancouver_laneway_house',
]);
export function isDetachedArchetype(id?: string): boolean {
  return Boolean(id && DETACHED.has(id.replace(/_front_day$/, '').replace(/_variant_\d+$/, '')));
}

/** Native landmark frontage is directional too; this does not enable home repetition. */
export function preservesAuthoredPlotAxes(properties?: Record<string, unknown> | null): boolean {
  return properties?.native_home_plot === true || properties?.native_plot_axes === true;
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
  preserveAuthoredAxes = false,
): number[][] | undefined {
  if (!coordinates?.length) return undefined;
  const ring = coordinates.map((point) => point.slice(0, 2));
  if (ring.some((point) => point.length < 2 || !point.every(Number.isFinite))) return undefined;
  const last = ring[ring.length - 1];
  if (ring.length > 3 && ring[0][0] === last[0] && ring[0][1] === last[1]) ring.pop();
  const frame = computeFootprintFrame(ring);
  if (!frame) return undefined;
  const yaw = (preserveAuthoredAxes ? authoredHomePlotFrame(ring)?.yawRad : undefined)
    ?? frame.bearingRad - (target.width_m >= target.depth_m ? 0 : -Math.PI / 2);
  const cos = Math.cos(yaw); const sin = Math.sin(yaw);
  const lonScale = metersPerDegLon(frame.centroidLat);
  return ring.map(([lon, lat]) => {
    const east = (lon - frame.centroidLng) * lonScale - frame.rectCenterLocal[0];
    const north = (lat - frame.centroidLat) * METERS_PER_DEG_LAT - frame.rectCenterLocal[1];
    return [Number((east * cos + north * sin).toFixed(6)), Number((east * sin - north * cos).toFixed(6))];
  });
}

/** A placed home's first edge remains its frontage, even past 90° or when width exceeds depth. */
export function authoredHomePlotFrame(coordinates: number[][]) {
  const ring = coordinates.length === 5 ? coordinates.slice(0, 4) : coordinates;
  if (ring.length !== 4 || ring.some(point => !point.slice(0, 2).every(Number.isFinite))) return undefined;
  const lat = ring.reduce((sum, point) => sum + point[1], 0) / 4;
  const edge = (i: number) => [(ring[(i+1)%4][0]-ring[i][0])*metersPerDegLon(lat),
    (ring[(i+1)%4][1]-ring[i][1])*METERS_PER_DEG_LAT];
  const [x,y] = edge(0), depth = Math.hypot(...edge(1));
  const width = Math.hypot(x,y);
  if (width < 1 || depth < 1) return undefined;
  return { width_m: Math.round(width*10)/10, depth_m: Math.round(depth*10)/10, yawRad: Math.atan2(y,x) };
}
