import { LOCAL_STREET_ASSET, STREET_ASSETS, LEGACY_SECTION_STREET_ASSETS } from './assetRegistry';
import type { SiteZone } from '@/types';
import { bufferLineToPolygon, extractCenterline, extractZoneCenterline, parsePersistedCenterline } from '@/utils/roadGeometry';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';
import { canonicalStreetForZone } from './canonicalStreetPlacement';
import { roundAuthoredStreetRoute } from '@/utils/streetRouteCurves';
import { isSpecialistStreet } from '@/components/viewer/globe/specialistStreetProgram';
import { isFixedNativeScene } from './fixedNativeScene';
import { isSurfacePath } from './surfacePath';
import { bufferPathwayToPolygon } from '@/utils/pathwayFootprint';
import { modularBridgeProgramFor, modularBridgeRouteProblem } from '@/components/viewer/globe/modularBridgeProgram';

export const CALGARY_LOCAL_PLACEMENT = LOCAL_STREET_ASSET;
export const CALGARY_LOCAL_WIDTH_M = LOCAL_STREET_ASSET.sectionWidth;

export function isCalgaryLocalRoute(zone: Pick<SiteZone, 'zone_type' | 'properties'>) {
  return streetAssetForZone(zone)?.id === LOCAL_STREET_ASSET.id;
}

export function streetAssetForZone(zone: Pick<SiteZone, 'zone_type' | 'properties'>) {
  if (zone.zone_type !== 'road' || isFixedNativeScene(zone.properties)) return undefined;
  // A finite classroom picker must not remove editing support from an existing
  // Calgary Local route saved before the candidate-only catalogue was enabled.
  return [...STREET_ASSETS, ...LEGACY_SECTION_STREET_ASSETS].find(asset => zone.properties?.pick_place_street_section === asset.model.variantId
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
  if (!zone) return { coordinates };
  if (!isFixedSectionStreet(zone)) {
    const line = zone.zone_type === 'road' ? parsePersistedCenterline(zone.properties?.plan_centerline) : null;
    if (!line || !zone.coordinates.length || zone.coordinates.length !== coordinates.length) return { coordinates };
    // Legacy/procedural streets also carry their source route when a whole
    // footprint is translated. An irregular outline edit cannot imply a route.
    const dx = coordinates[0][0] - zone.coordinates[0][0], dy = coordinates[0][1] - zone.coordinates[0][1];
    const sx = metersPerDegLon(zone.coordinates[0][1]), sy = METERS_PER_DEG_LAT;
    if (coordinates.some((p, i) => Math.hypot(
      (p[0] - zone.coordinates[i][0] - dx) * sx,
      (p[1] - zone.coordinates[i][1] - dy) * sy,
    ) > .02)) return { coordinates };
    const move = (points: number[][]) => points.map(p => [p[0] + dx, p[1] + dy]);
    const controls = parsePersistedCenterline(zone.properties?.plan_route_controls);
    return { coordinates, properties: {
      ...zone.properties, plan_centerline: move(line), ...(controls ? { plan_route_controls: move(controls) } : {}),
    } };
  }
  const width = streetSectionWidth(zone);
  const path = isSurfacePath(zone);
  if (path) {
    const movedLine = rigidlyMovedControls(zone.coordinates, coordinates, extractZoneCenterline(zone));
    if (movedLine) {
      const storedControls = parsePersistedCenterline(zone.properties?.plan_route_controls);
      return { coordinates, properties: { ...zone.properties, width, plan_centerline: movedLine,
        plan_route_controls: storedControls ? rigidlyMovedControls(zone.coordinates,coordinates,storedControls) ?? undefined : undefined } };
    }
  }
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
    return { coordinates: path ? bufferPathwayToPolygon(curved,width) : bufferLineToPolygon(curved, width), properties: {
      ...zone.properties, width, plan_centerline: curved, plan_route_controls: controls,
    } };
  }
  const carried = previousControls ? rigidlyMovedControls(previous, controls, previousControls) : null;
  return { coordinates: path ? bufferPathwayToPolygon(controls,width) : coordinates, properties: {
    ...zone.properties, width, plan_centerline: controls, plan_route_controls: carried ?? undefined,
  } };
}

function rigidlyMovedControls(before: number[][], after: number[][], controls: number[][]): number[][] | null {
  const open = (points:number[][]) => points.length>2 && Math.abs(points[0][0]-points[points.length-1][0])<1e-10
    && Math.abs(points[0][1]-points[points.length-1][1])<1e-10 ? points.slice(0,-1) : points;
  before = open(before); after = open(after);
  if (before.length !== after.length || before.length < 2) return null;
  const sx = metersPerDegLon(before[0][1]), sy = METERS_PER_DEG_LAT;
  const a = before[0], c = after[0];
  // An exterior footprint may be closed. Use a well-separated matching vertex
  // rather than treating its repeated closing vertex as a direction vector.
  const farthest = before.reduce((best,p,i) => Math.hypot((p[0]-a[0])*sx,(p[1]-a[1])*sy)
    > Math.hypot((before[best][0]-a[0])*sx,(before[best][1]-a[1])*sy) ? i : best, 1);
  const b = before[farthest], d = after[farthest];
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
  properties?: SiteZone['properties'],
): string | null {
  const line = authoredControls ?? extractCenterline(coordinates);
  if (line.length < 2) return 'Place at least two route points.';
  const mLon = metersPerDegLon(line[0][1]);
  const bridge = modularBridgeProgramFor(properties?.road_selected_variant_id);
  if (bridge) return modularBridgeRouteProblem(bridge, line.map(p => ({
    x: (p[0] - line[0][0]) * mLon, y: (p[1] - line[0][1]) * METERS_PER_DEG_LAT,
  })));
  const segments = line.slice(1).map((p, i) => [(p[0] - line[i][0]) * mLon, (p[1] - line[i][1]) * METERS_PER_DEG_LAT]);
  // Flat path finishes do not need the approach length or turning envelope of
  // a complete vehicle street section. Keep only distinct drawing stations.
  if (isSurfacePath({zone_type:'road',properties})) {
    return segments.some(([x,y]) => !Number.isFinite(x+y) || Math.hypot(x,y) < .05)
      ? 'Place the next pathway point a little farther from the previous point.' : null;
  }
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
  if((isSpecialistStreet(zone.properties?.road_selected_variant_id) && zone.properties?.road_selected_variant_id !== 'amsterdam_gracht_v1') || zone.properties?.road_selected_variant_id==='brt_bus_rapid_transit_corridor_v0')return null;
  const width = streetSectionWidth(zone);
  const savedControls = parsePersistedCenterline(zone.properties?.plan_route_controls);
  const line = savedControls ?? extractZoneCenterline(zone);
  if (line.length < 2) return null;
  const mLon = metersPerDegLon(line[0][1]);
  const lengths = line.slice(1).map((p, i) => Math.hypot((p[0]-line[i][0])*mLon, (p[1]-line[i][1])*METERS_PER_DEG_LAT));
  const longest = Math.max(...lengths);
  if (longest < (isSurfacePath(zone) ? .2 : 2*width)) return null;
  const i = lengths.indexOf(longest);
  const next = [...line.slice(0, i+1), [(line[i][0]+line[i+1][0])/2, (line[i][1]+line[i+1][1])/2], ...line.slice(i+1)];
  return bufferLineToPolygon(next, width);
}
