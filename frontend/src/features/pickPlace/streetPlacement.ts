import { LOCAL_STREET_ASSET, STREET_ASSETS } from './assetRegistry';
import type { SiteZone } from '@/types';
import { bufferLineToPolygon, extractCenterline, extractZoneCenterline, parsePersistedCenterline } from '@/utils/roadGeometry';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';
import { canonicalStreetForZone } from './canonicalStreetPlacement';
import { roundAuthoredStreetRoute } from '@/utils/streetRouteCurves';

export const CALGARY_LOCAL_PLACEMENT = LOCAL_STREET_ASSET;
export const CALGARY_LOCAL_WIDTH_M = LOCAL_STREET_ASSET.sectionWidth;

export function isCalgaryLocalRoute(zone: Pick<SiteZone, 'zone_type' | 'properties'>) {
  return streetAssetForZone(zone)?.id === LOCAL_STREET_ASSET.id;
}

export function streetAssetForZone(zone: Pick<SiteZone, 'zone_type' | 'properties'>) {
  if (zone.zone_type !== 'road') return undefined;
  return STREET_ASSETS.find(asset => zone.properties?.pick_place_street_section === asset.model.variantId
    && zone.properties.road_archetype_id === asset.properties.road_archetype_id
    && zone.properties.road_selected_variant_id === asset.model.variantId) ?? canonicalStreetForZone(zone);
}
export function isFixedSectionStreet(zone: Pick<SiteZone, 'zone_type' | 'properties'>) {
  return Boolean(streetAssetForZone(zone));
}
export function streetSectionWidth(zone: Pick<SiteZone, 'zone_type' | 'properties'>) {
  return streetAssetForZone(zone)?.sectionWidth ?? CALGARY_LOCAL_WIDTH_M;
}

/** Save the route and its buffer atomically, including move/undo/redo. */
export function streetCoordinateUpdate(zone: SiteZone | undefined, coordinates: number[][]) {
  if (!zone || !isFixedSectionStreet(zone)) return { coordinates };
  const width = streetSectionWidth(zone);
  const controls = extractCenterline(coordinates);
  const previous = zone.coordinates?.length ? extractZoneCenterline(zone) : [];
  const previousControls = parsePersistedCenterline(zone.properties?.plan_route_controls);
  const alreadySampled = previousControls !== null
    && previousControls.length < previous.length && controls.length === previous.length;
  const editingControls = previousControls !== null
    && controls.length <= previousControls.length + 1
    && (previousControls.length === previous.length || controls.length < previous.length);
  if (controls.length >= 3 && !alreadySampled && (editingControls || controls.length <= 6)) {
    const curved = roundAuthoredStreetRoute(controls, width, zone.properties);
    return { coordinates: bufferLineToPolygon(curved, width), properties: {
      ...zone.properties, width, plan_centerline: curved, plan_route_controls: controls,
    } };
  }
  const carried = previousControls ? rigidlyMovedControls(previous, controls, previousControls) : null;
  return { coordinates, properties: {
    ...zone.properties, width, plan_centerline: controls, plan_route_controls: carried ?? undefined,
  } };
}

function rigidlyMovedControls(before: number[][], after: number[][], controls: number[][]): number[][] | null {
  if (before.length !== after.length || before.length < 2) return null;
  const sx = metersPerDegLon(before[0][1]), sy = METERS_PER_DEG_LAT;
  const a = before[0], b = before[before.length - 1];
  const c = after[0], d = after[after.length - 1];
  const oldAngle = Math.atan2((b[1] - a[1]) * sy, (b[0] - a[0]) * sx);
  const newAngle = Math.atan2((d[1] - c[1]) * sy, (d[0] - c[0]) * sx);
  const angle = newAngle - oldAngle, cos = Math.cos(angle), sin = Math.sin(angle);
  const move = ([lng, lat]: number[]) => {
    const x = (lng - a[0]) * sx, y = (lat - a[1]) * sy;
    return [c[0] + (x * cos - y * sin) / sx, c[1] + (x * sin + y * cos) / sy];
  };
  if (before.some((point, index) => {
    const transformed = move(point), target = after[index];
    return Math.hypot((transformed[0] - target[0]) * sx, (transformed[1] - target[1]) * sy) > .02;
  })) return null;
  return controls.map(move);
}

export function reshapeStreetPoint(coordinates: number[][], index: number, point: number[], width = CALGARY_LOCAL_WIDTH_M) {
  const line = extractCenterline(coordinates).map((p, i) => i === index ? [...point] : p);
  return bufferLineToPolygon(line, width);
}

export function streetRouteProblem(
  coordinates: number[][],
  width = CALGARY_LOCAL_WIDTH_M,
  authoredControls?: number[][],
): string | null {
  const line = authoredControls ?? extractCenterline(coordinates);
  if (line.length < 2) return 'Place at least two route points.';
  const mLon = metersPerDegLon(line[0][1]);
  const segments = line.slice(1).map((p, i) => [(p[0] - line[i][0]) * mLon, (p[1] - line[i][1]) * METERS_PER_DEG_LAT]);
  const sampledCurve = !authoredControls && line.length > 6;
  if (sampledCurve ? segments.reduce((sum, [x, y]) => sum + Math.hypot(x, y), 0) < width
    : segments.some(([x, y]) => Math.hypot(x, y) < width)) {
    return `Keep route points at least ${width} m apart so the full street section fits.`;
  }
  if (segments.slice(1).some(([x, y], i) => {
    const [a, b] = segments[i];
    return (x*a + y*b) / Math.hypot(x, y) / Math.hypot(a, b) < -.5;
  })) return 'Use a gentler bend. Tight switchbacks need a different street design.';
  return null;
}

export function addStreetBend(zone: SiteZone): number[][] | null {
  const width = streetSectionWidth(zone);
  const savedControls = parsePersistedCenterline(zone.properties?.plan_route_controls);
  const line = savedControls ?? extractZoneCenterline(zone);
  if (line.length < 2) return null;
  const mLon = metersPerDegLon(line[0][1]);
  const lengths = line.slice(1).map((p, i) => Math.hypot((p[0]-line[i][0])*mLon, (p[1]-line[i][1])*METERS_PER_DEG_LAT));
  const longest = Math.max(...lengths);
  if (longest < 2*width) return null;
  const i = lengths.indexOf(longest);
  const next = [...line.slice(0, i+1), [(line[i][0]+line[i+1][0])/2, (line[i][1]+line[i+1][1])/2], ...line.slice(i+1)];
  return bufferLineToPolygon(next, width);
}
