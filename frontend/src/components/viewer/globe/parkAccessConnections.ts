import { isParkTrio } from './parkTrioLayout';
import type { SiteZone } from '@/types';
import { effectiveRoadWidth, extractRenderableStreetCenterline } from '@/utils/roadGeometry';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { fitParkGroundGuides, resolveParkGroundProfile, resolveParkGuideDimensionsM, type ParkGroundGuide } from './parkGroundProfiles';
import { resolvePilotStreetSectionProfile } from './streetSectionProfiles';
import { computeParkPlacements, resolveParkRecipeForZone } from './parkScatter';
import { isNeighborhoodParkPilot } from './neighborhoodParkLayout';
import { PARK_PROGRAM_MODULE_SPEC, resolveParkProgramAnchorLayout } from './parkLegoFamilies';
import { preparedSiteContainsZone, resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import { EMPTY_TRANSPORT, type ExistingTransport } from '@/features/referenceLayers/existingTransport';

export type ParkAccessPoint = [number, number];
export interface ParkAccessPath { points: ParkAccessPoint[]; widthM: number }
export interface ParkAccessConnection {
  id: string;
  streetZoneId: string;
  streetBand: 'sidewalk' | 'path';
  streetPoint: ParkAccessPoint;
  gateway: ParkAccessPoint;
  /** Street arrival, boundary gateway, then the route into the park network. */
  path: ParkAccessPoint[];
  widthM: number;
  streetLiftM: number;
}
export interface ParkAccessPlan {
  parkZoneId: string;
  status: 'connected' | 'explicit' | 'blocked' | 'unresolved';
  reason?: string;
  connections: ParkAccessConnection[];
  /** Additional internal circulation only; fitted programs are never replaced. */
  paths: ParkAccessPath[];
}
export interface ParkAccessSettings {
  maxGapM: number;
  pathWidthM: number;
  obstacleClearanceM: number;
  maxConnections: number;
  gridStepM: number;
}
export interface ParkAccessSnapshot {
  version: 1;
  sourceSignature: string;
  settings: ParkAccessSettings;
  /** Targets visible in the active scenario; all sources still act as barriers. */
  eligibleStreetZoneIds: string[];
  sources: Array<{ zoneId: string; updatedAt: string; geometrySignature: string }>;
  parks: ParkAccessPlan[];
}
export type DerivedParkAccess = ParkAccessPlan & { version: 1; sourceSignature: string };

const DEFAULTS: ParkAccessSettings = { maxGapM: 8, pathWidthM: 2.2, obstacleClearanceM: 0.25, maxConnections: 2, gridStepM: 2 };
const EPS = 1e-6;
const MAX_ZONES = 256;
const MAX_VERTICES = 512;
const MAX_GRID_NODES = 1024;
type P = ParkAccessPoint;
const add = (a: P, b: P): P => [a[0] + b[0], a[1] + b[1]];
const sub = (a: P, b: P): P => [a[0] - b[0], a[1] - b[1]];
const mul = (a: P, n: number): P => [a[0] * n, a[1] * n];
const dot = (a: P, b: P) => a[0] * b[0] + a[1] * b[1];
const cross = (a: P, b: P) => a[0] * b[1] - a[1] * b[0];
const distance = (a: P, b: P) => Math.hypot(a[0] - b[0], a[1] - b[1]);
const lerp = (a: P, b: P, t: number) => add(a, mul(sub(b, a), t));
const segments = (ring: P[]): Array<[P, P]> => ring.map((p, i) => [p, ring[(i + 1) % ring.length]]);
function project(p: P, a: P, b: P): P {
  const d = sub(b, a);
  return lerp(a, b, Math.max(0, Math.min(1, dot(sub(p, a), d) / Math.max(EPS, dot(d, d)))));
}
function intersects(a: P, b: P, c: P, d: P): boolean {
  const ab = sub(b, a); const cd = sub(d, c); const divisor = cross(ab, cd);
  if (Math.abs(divisor) < EPS) return distance(a, project(a, c, d)) < EPS || distance(c, project(c, a, b)) < EPS;
  const t = cross(sub(c, a), cd) / divisor; const u = cross(sub(c, a), ab) / divisor;
  return t >= -EPS && t <= 1 + EPS && u >= -EPS && u <= 1 + EPS;
}
export function pointInside(p: P, ring: P[]): boolean {
  if (segments(ring).some(([a, b]) => distance(p, project(p, a, b)) < EPS)) return true;
  let inside = false;
  for (const [a, b] of segments(ring)) {
    if ((a[1] > p[1]) !== (b[1] > p[1]) && p[0] < (b[0] - a[0]) * (p[1] - a[1]) / (b[1] - a[1]) + a[0]) inside = !inside;
  }
  return inside;
}
function segmentDistance(a: P, b: P, c: P, d: P): number {
  if (intersects(a, b, c, d)) return 0;
  return Math.min(distance(a, project(a, c, d)), distance(b, project(b, c, d)), distance(c, project(c, a, b)), distance(d, project(d, a, b)));
}
export function hitsObstacle(a: P, b: P, ring: P[], clearance: number): boolean {
  return pointInside(a, ring) || pointInside(b, ring) || segments(ring).some(([c, d]) => segmentDistance(a, b, c, d) < clearance + EPS);
}
/** Check every rectangle edge, not just its corners: concave notches matter. */
function insideSegment(a: P, b: P, ring: P[]): boolean {
  if (!pointInside(a, ring) || !pointInside(b, ring)) return false;
  const ts = [0, 1]; const ab = sub(b, a);
  for (const [c, d] of segments(ring)) {
    const cd = sub(d, c); const divisor = cross(ab, cd);
    if (Math.abs(divisor) < EPS) continue;
    const t = cross(sub(c, a), cd) / divisor; const u = cross(sub(c, a), ab) / divisor;
    if (t > 0 && t < 1 && u >= 0 && u <= 1) ts.push(t);
  }
  ts.sort((x, y) => x - y);
  return ts.slice(1).every((t, i) => pointInside(lerp(a, b, (t + ts[i]) / 2), ring));
}
export function corridorInside(a: P, b: P, ring: P[], halfWidth: number): boolean {
  const delta = sub(b, a); const length = distance(a, b);
  if (length < EPS) return pointInside(a, ring);
  const n = mul([-delta[1], delta[0]], halfWidth / length);
  const quad = [add(a, n), add(b, n), sub(b, n), sub(a, n)];
  return segments(quad).every(([c, d]) => insideSegment(c, d, ring));
}
export function corridorOverlaps(a: P, b: P, ring: P[], halfWidth: number): boolean {
  const delta = sub(b, a); const length = distance(a, b);
  if (length < EPS) return false;
  const n = mul([-delta[1], delta[0]], halfWidth / length);
  const quad = [add(a, n), add(b, n), sub(b, n), sub(a, n)];
  const strictlyInside = (p: P, polygon: P[]) => pointInside(p, polygon) && segments(polygon).every(([c, d]) => distance(p, project(p, c, d)) > EPS);
  return quad.some((p) => strictlyInside(p, ring)) || ring.some((p) => strictlyInside(p, quad))
    || strictlyInside(lerp(a, b, 0.5), ring)
    || segments(quad).some(([c, d]) => segments(ring).some(([e, f]) => (
      cross(sub(d, c), sub(e, c)) * cross(sub(d, c), sub(f, c)) < -EPS
      && cross(sub(f, e), sub(c, e)) * cross(sub(f, e), sub(d, e)) < -EPS
    )));
}
function stable(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stable).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => `${JSON.stringify(k)}:${stable(v)}`).join(',')}}`;
  return JSON.stringify(value) ?? 'null';
}
function hash(value: unknown): string {
  const text = stable(value); let n = 2166136261;
  for (let i = 0; i < text.length; i += 1) n = Math.imul(n ^ text.charCodeAt(i), 16777619);
  return `pac1-${(n >>> 0).toString(16).padStart(8, '0')}`;
}
function source(zone: SiteZone) {
  const properties = Object.fromEntries(Object.entries(zone.properties ?? {}).filter(([key]) => key !== 'park_access_connections'));
  return { id: zone.id, zoneType: zone.zone_type, coordinates: zone.coordinates, isActiveBoundary: zone.is_active_boundary, properties, updatedAt: zone.updated_at };
}
function settingsOf(settings: Partial<ParkAccessSettings>): ParkAccessSettings {
  const bounded = (value: number | undefined, fallback: number, low: number, high: number) => Number.isFinite(value) ? Math.max(low, Math.min(high, value!)) : fallback;
  return { maxGapM: bounded(settings.maxGapM, DEFAULTS.maxGapM, 0, 12), pathWidthM: bounded(settings.pathWidthM, DEFAULTS.pathWidthM, 1.2, 4),
    obstacleClearanceM: bounded(settings.obstacleClearanceM, DEFAULTS.obstacleClearanceM, 0.1, 2), maxConnections: Math.floor(bounded(settings.maxConnections, DEFAULTS.maxConnections, 1, 3)),
    gridStepM: bounded(settings.gridStepM, DEFAULTS.gridStepM, 1, 4) };
}
function validRing(zone: SiteZone): boolean {
  return zone.coordinates.length >= 3 && zone.coordinates.length <= MAX_VERTICES && zone.coordinates.every(([x, y]) => Number.isFinite(x) && Number.isFinite(y) && Math.abs(x) <= 180 && Math.abs(y) <= 85);
}
function supported(zone: SiteZone): boolean {
  if (zone.zone_type !== 'green_space') return false;
  if (isParkTrio(zone)) return true;
  const profile = resolveParkGroundProfile(zone);
  return (profile.archetypeId.startsWith('urban_pocket_park') || profile.archetypeId.startsWith('neighborhood_park'))
    && (isNeighborhoodParkPilot(zone) || (profile.variantId ?? zone.properties?.green_space_selected_variant_id) !== 'neighborhood_park_v0');
}

function solvePark(park: SiteZone, zones: readonly SiteZone[], settings: ParkAccessSettings, eligibleStreetZoneIds: ReadonlySet<string>, transport: ExistingTransport): ParkAccessPlan {
  const empty = (status: ParkAccessPlan['status'], reason: string): ParkAccessPlan => ({ parkZoneId: park.id, status, reason, connections: [], paths: [] });
  // Even an explicitly empty list is authored intent, not permission to invent gates.
  if (Array.isArray(park.properties?.park_access_points)) return empty('explicit', 'Existing authored access points are preserved.');
  const entrance = park.properties?.pedestrian_park_entrance as { version?: number; edge?: number; position?: number; streetId?: string; existingGroundConfirmed?: boolean } | null;
  if (entrance && (entrance.version !== 1 || !Number.isInteger(entrance.edge) || entrance.edge! < 0 || entrance.edge! >= park.coordinates.length
    || !Number.isFinite(entrance.position) || entrance.position! < 0 || entrance.position! > 1 || typeof entrance.streetId !== 'string')) {
    return empty('unresolved', 'Choose a valid park entrance and sidewalk target.');
  }
  if (!validRing(park) || zones.length > MAX_ZONES || zones.some((z) => !validRing(z))) return empty('unresolved', 'Geometry is invalid or exceeds the bounded access-planning limit.');
  const boundary = getActiveSiteBoundary([...zones]);
  if (!boundary || !preparedSiteContainsZone(boundary, park)) {
    return empty('unresolved', 'A common active site boundary is required before a street-to-park connection can be derived.');
  }
  const origin = park.coordinates[0]; const mLon = metersPerDegLon(origin[1]);
  const local = ([lng, lat]: number[]): P => [(lng - origin[0]) * mLon, (lat - origin[1]) * METERS_PER_DEG_LAT];
  const world = ([x, y]: P): P => [origin[0] + x / mLon, origin[1] + y / METERS_PER_DEG_LAT];
  const ring = park.coordinates.map(local);
  const west = Math.min(...ring.map((p) => p[0])); const east = Math.max(...ring.map((p) => p[0]));
  const south = Math.min(...ring.map((p) => p[1])); const north = Math.max(...ring.map((p) => p[1]));
  const size = { width: east - west, height: north - south };
  if (Math.min(size.width, size.height) < settings.pathWidthM * 3) return empty('blocked', 'The whole path width does not fit this park.');
  const normalized = ring.map(([x, y]): P => [(x - west) / size.width, (north - y) / size.height]);
  const profile = resolveParkGroundProfile(park);
  const fit = fitParkGroundGuides(profile.guides, size, normalized);
  const guidePoint = ([x, y]: P): P => [west + x * size.width, north - y * size.height];
  const guidePolygon = (guide: ParkGroundGuide, expansion = 0): P[] => {
    const dimensions = resolveParkGuideDimensionsM(guide, size);
    const rx = dimensions.width / 2 + expansion; const ry = dimensions.height / 2 + expansion;
    const angle = -(guide.rotationDeg ?? 0) * Math.PI / 180; const center = guidePoint([guide.x, guide.y]);
    const points: P[] = guide.kind === 'ellipse'
      ? Array.from({ length: 32 }, (_, i): P => [Math.cos(i * Math.PI / 16) * rx / Math.cos(Math.PI / 32), Math.sin(i * Math.PI / 16) * ry / Math.cos(Math.PI / 32)])
      : [[-rx, -ry], [rx, -ry], [rx, ry], [-rx, ry]];
    return points.map(([x, y]) => add(center, [x * Math.cos(angle) - y * Math.sin(angle), x * Math.sin(angle) + y * Math.cos(angle)]));
  };
  const fixed = fit.guides.filter((g) => !['line', 'axis', 'polyline', 'path_loop'].includes(g.kind)).map((g) => guidePolygon(g));
  for (const placement of (isNeighborhoodParkPilot(park) || isParkTrio(park)) ? [] : computeParkPlacements(park, resolveParkRecipeForZone(park), profile.plantingStructure, resolveParkProgramAnchorLayout(park))) {
    if (placement.propId !== 'playground' && placement.propId !== 'pavilion') continue;
    const radius = placement.propId === 'playground' ? PARK_PROGRAM_MODULE_SPEC.playground.safetyDiameterM / 2
      : Math.hypot(PARK_PROGRAM_MODULE_SPEC.pavilion.widthM, PARK_PROGRAM_MODULE_SPEC.pavilion.depthM) / 2;
    const center = local([placement.lng, placement.lat]);
    fixed.push(Array.from({ length: 24 }, (_, i) => add(center, [Math.cos(i * Math.PI / 12) * radius * placement.scale / Math.cos(Math.PI / 24), Math.sin(i * Math.PI / 12) * radius * placement.scale / Math.cos(Math.PI / 24)])));
  }
  const obstacles = zones.filter((z) => z.id !== park.id && ['building', 'residential', 'development_area', 'water', 'parking'].includes(z.zone_type)).map((z) => z.coordinates.map(local));
  const roadPolygons = zones.filter((z) => z.zone_type === 'road').map((z) => ({ id: z.id, ring: z.coordinates.map(local) }));
  const boundaryRing = boundary.coordinates.map(local);
  const half = settings.pathWidthM / 2;
  const boundaryClearance = (p: P) => Math.min(...segments(ring).map(([a, b]) => distance(p, project(p, a, b))));
  const internalSafe = (a: P, b: P, gatewayStart = false) => corridorInside(a, b, ring, half)
    && (gatewayStart || boundaryClearance(a) + EPS >= half) && boundaryClearance(b) + EPS >= half
    && [...fixed, ...obstacles].every((obstacle) => !hitsObstacle(a, b, obstacle, half + settings.obstacleClearanceM))
    && roadPolygons.every((road) => !corridorOverlaps(a, b, road.ring, half));
  let network: P[][] = fit.guides.filter((g) => g.kind === 'polyline' && g.closed && g.points).map((g) => g.points!.map(guidePoint));
  let extraLoop: P[] | null = null;
  if (profile.archetypeId.startsWith('urban_pocket_park')) {
    const lawn = fit.guides.find((g) => g.kind === 'ellipse');
    if (lawn) {
      extraLoop = guidePolygon(lawn, settings.pathWidthM + settings.obstacleClearanceM + 0.2);
      extraLoop.push(extraLoop[0]);
      if (!extraLoop.slice(1).every((p, i) => internalSafe(extraLoop![i], p))) return empty('blocked', 'A complete path around the fixed lawn does not fit without crossing a barrier.');
      network = [extraLoop];
    }
  }
  if (!network.length) return empty('unresolved', 'This fixed park program has no supported internal route to connect.');
  const routeSegments = network.flatMap((points) => points.slice(1).map((b, i): [P, P] => [points[i], b]));
  const findRoute = (start: P): P[] | null => {
    const targets = routeSegments.map(([a, b]) => project(start, a, b)).sort((a, b) => distance(start, a) - distance(start, b));
    const direct = targets.find((target) => internalSafe(start, target));
    if (direct) return [start, direct];
    const step = Math.max(settings.gridStepM, Math.sqrt(size.width * size.height / (MAX_GRID_NODES - 40)));
    const nodes: P[] = [start, ...targets.slice(0, 32)];
    const goalCount = nodes.length;
    for (let y = south + half; y < north - half; y += step) {
      for (let x = west + half; x < east - half; x += step) {
        const point: P = [x, y];
        if (internalSafe(point, add(point, [EPS * 2, 0]))) nodes.push(point);
        if (nodes.length >= MAX_GRID_NODES) break;
      }
      if (nodes.length >= MAX_GRID_NODES) break;
    }
    const best = new Map([[0, 0]]); const prior = new Map<number, number>(); const open = new Set([0]);
    while (open.size) {
      const current = [...open].sort((a, b) => best.get(a)! - best.get(b)! || a - b)[0]; open.delete(current);
      if (current > 0 && current < goalCount) {
        const result = [nodes[current]]; let cursor = current;
        while (prior.has(cursor)) { cursor = prior.get(cursor)!; result.unshift(nodes[cursor]); }
        return result;
      }
      nodes.forEach((node, index) => {
        const length = distance(nodes[current], node);
        if (!length || length > step * 1.6 || !internalSafe(nodes[current], node)) return;
        const cost = best.get(current)! + length;
        if (cost + EPS >= (best.get(index) ?? Infinity)) return;
        best.set(index, cost); prior.set(index, current); open.add(index);
      });
    }
    return null;
  };
  type Candidate = { street: { id: string }; point: P; gateway: P; ingress: P; band: 'sidewalk' | 'path'; widthM: number; lift: number; gap: number };
  const candidates: Candidate[] = [];
  for (const street of zones.filter((z) => z.zone_type === 'road' && eligibleStreetZoneIds.has(z.id)).sort((a, b) => a.id.localeCompare(b.id))) {
    if (entrance && street.id !== entrance.streetId) continue;
    // Both surfaces must use one site ground contract. Retained sites wait
    // for the shared sampled surface at runtime before showing/capturing paths.
    if (!preparedSiteContainsZone(boundary, street)) continue;
    const section = resolvePilotStreetSectionProfile(street);
    const center = extractRenderableStreetCenterline(street).map(local);
    if (!section || center.length < 2) continue;
    const scale = section.metricWidthLocked ? (section.targetRowM ?? section.rowM) / section.rowM : effectiveRoadWidth(street.properties) / section.rowM;
    const streetRing = street.coordinates.map(local);
    for (const [edgeIndex, [edgeA, edgeB]] of segments(ring).entries()) {
      if (entrance && edgeIndex !== entrance.edge) continue;
      const delta = sub(edgeB, edgeA); const edgeLength = distance(edgeA, edgeB);
      if (edgeLength < settings.pathWidthM * 2) continue;
      let inward: P = [-delta[1] / edgeLength, delta[0] / edgeLength];
      if (!pointInside(add(lerp(edgeA, edgeB, 0.5), mul(inward, 0.05)), ring)) inward = mul(inward, -1);
      for (const t of entrance ? [entrance.position!] : [0.5, 0.25, 0.75]) {
        const gateway = lerp(edgeA, edgeB, t); const ingress = add(gateway, mul(inward, settings.pathWidthM + 0.5));
        if (!internalSafe(gateway, ingress, true)) continue;
        for (let i = 1; i < center.length; i += 1) {
          const a = center[i - 1]; const b = center[i]; const length = distance(a, b);
          if (length < EPS) continue;
          const normal: P = [-(b[1] - a[1]) / length, (b[0] - a[0]) / length];
          for (const band of section.bands.filter((v) => v.kind === 'sidewalk' || v.kind === 'path')) {
            const offset = mul(normal, band.centerM * scale);
            const point = project(gateway, add(a, offset), add(b, offset)); const gap = distance(point, gateway);
            if (gap > settings.maxGapM || !pointInside(point, streetRing)) continue;
            // The near-side pedestrian band must be the last road surface on
            // the approach. Never create an unplanned road/cycle/parking crossing.
            const unsafeBands = center.slice(1).flatMap((end, segmentIndex) => {
              const start = center[segmentIndex]; const segmentLength = distance(start, end);
              if (segmentLength < EPS) return [];
              const segmentNormal: P = [-(end[1] - start[1]) / segmentLength, (end[0] - start[0]) / segmentLength];
              // The Calgary section's 0.3 m outer margin lies beyond its
              // sidewalk. A path may bridge that margin to the park; motor,
              // cycle, parking and planted bands still block an approach.
              return section.bands.filter((other) => other !== band && other.sourceType !== 'setback').map((other) => [
                add(start, mul(segmentNormal, other.startM * scale)), add(end, mul(segmentNormal, other.startM * scale)),
                add(end, mul(segmentNormal, other.endM * scale)), add(start, mul(segmentNormal, other.endM * scale)),
              ]);
            });
            if (unsafeBands.some((unsafe) => corridorOverlaps(point, gateway, unsafe, half))) continue;
            if (!corridorInside(point, gateway, boundaryRing, half)) continue;
            if ([...obstacles, ...roadPolygons.filter((r) => r.id !== street.id).map((r) => r.ring)].some((obstacle) => hitsObstacle(point, gateway, obstacle, half + settings.obstacleClearanceM))) continue;
            candidates.push({ street, point, gateway, ingress, band: band.kind as 'sidewalk' | 'path', widthM: settings.pathWidthM, lift: band.liftM, gap });
          }
        }
      }
    }
  }
  // Existing mapped paths are opt-in targets, never extra design zones. Their
  // overlay can be hidden without changing saved intent or capture geometry.
  if (entrance?.streetId?.startsWith('existing:')) {
    if (!entrance.existingGroundConfirmed) return empty('unresolved', 'Check that the mapped path meets this site at ground level.');
    const target = transport.lines.find(line=>line.id===entrance.streetId && line.kind==='path');
    if (!target) return empty('unresolved', 'The mapped path is missing or no longer eligible. Choose another target.');
    const [a,b] = segments(ring)[entrance.edge!];
    const edgeLength=distance(a,b), gateway=lerp(a,b,entrance.position!);
    if(edgeLength>=settings.pathWidthM*2) {
      let inward:P=[-(b[1]-a[1])/edgeLength,(b[0]-a[0])/edgeLength];
      if(!pointInside(add(gateway,mul(inward,0.05)),ring))inward=mul(inward,-1);
      const ingress=add(gateway,mul(inward,settings.pathWidthM+0.5));
      const line=target.points.map(local);
      for(let i=1;i<line.length;i++) {
        const centre=project(gateway,line[i-1],line[i]),centreGap=distance(centre,gateway);
        // Meet the near edge of a recorded-width path, with a small overlap.
        // Requiring its centreline inside the parcel incorrectly rejects a
        // legitimate connection to a path alongside the boundary.
        const edgeOffset=Math.min(Math.max(0,(target.widthM ?? 0)/2-0.15),Math.max(0,centreGap-0.05));
        const point=add(centre,mul(sub(gateway,centre),edgeOffset/Math.max(EPS,centreGap))),gap=distance(point,gateway);
        if(gap>settings.maxGapM || gap<0.05 || !internalSafe(gateway,ingress,true)
          || !corridorInside(point,gateway,boundaryRing,half))continue;
        if([...obstacles,...roadPolygons.map(r=>r.ring)].some(obstacle=>hitsObstacle(point,gateway,obstacle,half+settings.obstacleClearanceM)))continue;
        if(transport.lines.filter(l=>l.kind==='road').some(road=>road.points.slice(1).some((end,j)=>segmentDistance(point,gateway,local(road.points[j]),local(end))<=half+0.5)))continue;
        candidates.push({street:{id:target.id},point,gateway,ingress,band:'path',widthM:settings.pathWidthM,lift:0.025,gap});
      }
    }
    if(!candidates.length)return empty('unresolved','No clear connection within 8 m. Keep the approach inside the site, on this side of existing roads, and check the entrance edge.');
  }
  const level=resolvePreparedSiteTerrainForZone(park,[...zones],0),base=resolvePreparedSiteTerrainForZone(boundary,[...zones],0);
  if(level!==null&&base!==null&&Math.abs(level-base)>.02)return empty('unresolved','This park has a separate terrace level. Its sidewalk entrance needs a graded approach and retaining-edge opening; the terrace pilot currently connects building and park plots only.');
  const connections: ParkAccessConnection[] = [];
  for (const candidate of candidates.sort((a, b) => a.gap - b.gap || a.street.id.localeCompare(b.street.id) || a.gateway[0] - b.gateway[0] || a.gateway[1] - b.gateway[1]).slice(0, 32)) {
    if (connections.some((c) => c.streetZoneId === candidate.street.id || distance(local(c.gateway), candidate.gateway) < settings.pathWidthM * 3)) continue;
    const route = findRoute(candidate.ingress);
    if (!route) continue;
    connections.push({ id: `${park.id}:${candidate.street.id}:${connections.length}`, streetZoneId: candidate.street.id, streetBand: candidate.band,
      streetPoint: world(candidate.point), gateway: world(candidate.gateway), path: [candidate.point, candidate.gateway, ...route].map(world), widthM: candidate.widthM, streetLiftM: candidate.lift });
    if (connections.length >= settings.maxConnections) break;
  }
  if (!connections.length) return empty(candidates.length ? 'blocked' : 'unresolved', candidates.length ? 'No whole-width route reaches the fixed path network without crossing a barrier.' : 'No safe adjacent authored sidewalk or path was found.');
  return { parkZoneId: park.id, status: 'connected', connections,
    paths: [...(extraLoop ? [{ points: extraLoop.map(world), widthM: settings.pathWidthM }] : []), ...connections.map((c) => ({ points: c.path.slice(1), widthM: c.widthM }))] };
}

export function resolveManualParkAccess(zones: readonly SiteZone[], input: Partial<ParkAccessSettings> = {}, eligibleStreetZoneIds?: readonly string[], transport: ExistingTransport = EMPTY_TRANSPORT): ParkAccessSnapshot {
  const settings = settingsOf(input); const sorted = [...zones].sort((a, b) => a.id.localeCompare(b.id));
  const roads = new Set(sorted.filter((zone) => zone.zone_type === 'road').map((zone) => zone.id));
  const eligible = [...new Set(eligibleStreetZoneIds ?? roads)].filter((id) => roads.has(id)).sort().slice(0, MAX_ZONES);
  return { version: 1, sourceSignature: hash({ zones: sorted.map(source), settings, eligibleStreetZoneIds: eligible, transport }), settings, eligibleStreetZoneIds: eligible,
    sources: sorted.map((z) => ({ zoneId: z.id, updatedAt: z.updated_at, geometrySignature: hash({ coordinates: z.coordinates, type: z.zone_type, isActiveBoundary: z.is_active_boundary }) })),
    parks: sorted.filter(supported).map((park) => solvePark(park, sorted, settings, new Set(eligible), transport)) };
}

/** A view adapter, never a persistence mutation. Reject snapshots from old road edits. */
export function applyManualParkAccessSnapshot(zones: readonly SiteZone[], snapshot: ParkAccessSnapshot, transport: ExistingTransport = EMPTY_TRANSPORT): SiteZone[] {
  const clean = zones.map((zone) => {
    if (!zone.properties?.park_access_connections) return zone;
    const { park_access_connections: _old, ...properties } = zone.properties;
    return { ...zone, properties };
  });
  const current = hash({ zones: [...zones].sort((a, b) => a.id.localeCompare(b.id)).map(source), settings: snapshot.settings,
    eligibleStreetZoneIds: snapshot.eligibleStreetZoneIds, transport });
  if (snapshot.version !== 1 || snapshot.sourceSignature !== current) return clean;
  return clean.map((zone) => {
    const plan = snapshot.parks.find((park) => park.parkZoneId === zone.id);
    if (!plan || plan.status === 'explicit') return zone;
    return { ...zone, properties: { ...zone.properties, park_access_connections: { ...plan, version: 1, sourceSignature: snapshot.sourceSignature } } };
  });
}

export function getDerivedParkAccess(zone: Pick<SiteZone, 'properties'>): DerivedParkAccess | null {
  if (Array.isArray(zone.properties?.park_access_points)) return null;
  const value = zone.properties?.park_access_connections as DerivedParkAccess | undefined;
  const validPoint = (p: unknown): p is P => Array.isArray(p) && p.length === 2 && p.every((n) => typeof n === 'number' && Number.isFinite(n)) && Math.abs(p[0]) <= 180 && Math.abs(p[1]) <= 85;
  const validPath = (p: ParkAccessPath) => p && Array.isArray(p.points) && p.points.length >= 2 && p.points.length <= MAX_GRID_NODES && p.points.every(validPoint) && p.widthM >= 1.2 && p.widthM <= 4;
  return value?.version === 1 && value.status === 'connected' && typeof value.sourceSignature === 'string'
    && Array.isArray(value.paths) && value.paths.length <= 4 && value.paths.every(validPath)
    && Array.isArray(value.connections) && value.connections.length > 0 && value.connections.length <= 3
    && value.connections.every((c) => c && validPoint(c.streetPoint) && validPoint(c.gateway)
      && validPath({ points: c.path, widthM: c.widthM }) && Number.isFinite(c.streetLiftM)) ? value : null;
}

/** Reuse these guides for both visible paths and tree/furniture clearances. */
export function derivedParkAccessGuides(zone: SiteZone): ParkGroundGuide[] {
  const data = getDerivedParkAccess(zone); if (!data) return [];
  const west = Math.min(...zone.coordinates.map((p) => p[0])); const east = Math.max(...zone.coordinates.map((p) => p[0]));
  const south = Math.min(...zone.coordinates.map((p) => p[1])); const north = Math.max(...zone.coordinates.map((p) => p[1]));
  if (east <= west || north <= south) return [];
  return data.paths.map((path) => ({ kind: 'polyline', x: 0.5, y: 0.5, width: 1, height: 1, color: '#a99f86', strokeWidthM: path.widthM,
    points: path.points.map(([lng, lat]) => [(lng - west) / (east - west), (north - lat) / (north - south)] as P), fitPolicy: 'whole', orientationPolicy: 'fixed' }));
}
