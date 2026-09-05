import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import type { ParkGroundGuide } from './parkGroundProfiles';

export const NEIGHBORHOOD_PARK_PILOT = 'adaptive_rustic_v1';
export interface ParkPoint { x: number; y: number }
export type ParkModuleKind = 'pavilion' | 'tower' | 'swing';
export interface ParkModule {
  id: string; kind: ParkModuleKind; center: ParkPoint; yaw: number;
  width: number; depth: number; envelope: ParkPoint[];
  arrival?: ParkPoint;
}
export interface NeighborhoodParkLayout {
  status: 'full' | 'compact' | 'constrained';
  boundary: ParkPoint[]; lawn: ParkPoint[]; loop: ParkPoint[];
  paths: ParkPoint[][]; modules: ParkModule[]; trees: ParkPoint[];
  shrubs: ParkPoint[]; pathWidth: number; notes: string[];
}

export function isNeighborhoodParkPilot(zone: Pick<SiteZone, 'properties'> & Partial<Pick<SiteZone, 'zone_type'>>): boolean {
  return zone.zone_type === 'green_space'
    && zone.properties?.green_space_archetype_id === 'neighborhood_park'
    && zone.properties?.green_space_selected_variant_id === 'neighborhood_park_v0'
    && zone.properties?.neighborhood_park_layout === NEIGHBORHOOD_PARK_PILOT;
}

export function pointInPark(p: ParkPoint, ring: readonly ParkPoint[]): boolean {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const a = ring[i], b = ring[j];
    if ((a.y > p.y) !== (b.y > p.y) && p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y) + a.x) inside = !inside;
  }
  return inside;
}
export function distanceToSegment(p: ParkPoint, a: ParkPoint, b: ParkPoint): number {
  const dx = b.x - a.x, dy = b.y - a.y;
  const t = Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy || 1)));
  return Math.hypot(p.x - a.x - t * dx, p.y - a.y - t * dy);
}
const edgeDistance = (p: ParkPoint, ring: readonly ParkPoint[]) => Math.min(...ring.map((a, i) => distanceToSegment(p, a, ring[(i + 1) % ring.length])));
const cross = (a: ParkPoint, b: ParkPoint, p: ParkPoint) => (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x);
function segmentsCross(a: ParkPoint, b: ParkPoint, c: ParkPoint, d: ParkPoint): boolean {
  return cross(a, b, c) * cross(a, b, d) < -1e-8 && cross(c, d, a) * cross(c, d, b) < -1e-8;
}
export function envelopeFits(envelope: readonly ParkPoint[], boundary: readonly ParkPoint[], clearance = 0): boolean {
  if (!envelope.every(p => pointInPark(p, boundary) && edgeDistance(p, boundary) >= clearance)) return false;
  return envelope.every((a, i) => boundary.every((c, j) => {
    const b = envelope[(i + 1) % envelope.length], d = boundary[(j + 1) % boundary.length];
    return !segmentsCross(a, b, c, d) && distanceToSegment(c, a, b) >= clearance;
  }));
}
export function envelopesOverlap(a: readonly ParkPoint[], b: readonly ParkPoint[]): boolean {
  return a.some(p => pointInPark(p, b)) || b.some(p => pointInPark(p, a))
    || a.some((p, i) => b.some((q, j) => segmentsCross(p, a[(i + 1) % a.length], q, b[(j + 1) % b.length])));
}
const ellipse = (cx: number, cy: number, rx: number, ry: number): ParkPoint[] => Array.from({ length: 64 }, (_, i) => ({ x: cx + Math.cos(i * Math.PI / 32) * rx, y: cy + Math.sin(i * Math.PI / 32) * ry }));
const rect = (x: number, y: number, w: number, d: number): ParkPoint[] => [{ x: x - w / 2, y: y - d / 2 }, { x: x + w / 2, y: y - d / 2 }, { x: x + w / 2, y: y + d / 2 }, { x: x - w / 2, y: y + d / 2 }];
const bounds = (ring: readonly ParkPoint[]) => ({ minX: Math.min(...ring.map(p => p.x)), maxX: Math.max(...ring.map(p => p.x)), minY: Math.min(...ring.map(p => p.y)), maxY: Math.max(...ring.map(p => p.y)) });

/** Finite, deterministic composition. Furniture stays at real metre sizes;
 * the lawn, planting and paths use the remaining land. No provider calls. */
export function buildNeighborhoodParkLayout(input: readonly ParkPoint[]): NeighborhoodParkLayout {
  const empty: NeighborhoodParkLayout = { status: 'constrained', boundary: [...input], lawn: [], loop: [], paths: [], modules: [], trees: [], shrubs: [], pathWidth: 2.6, notes: [] };
  if (input.length < 3 || input.length > 256 || input.some(p => !Number.isFinite(p.x + p.y))) return { ...empty, notes: ['Draw a valid park boundary with at most 256 vertices.'] };
  const edges = input.map((p, i) => ({ p, q: input[(i + 1) % input.length] })).sort((a, b) => Math.hypot(b.p.x - b.q.x, b.p.y - b.q.y) - Math.hypot(a.p.x - a.q.x, a.p.y - a.q.y));
  let angle = Math.atan2(edges[0].q.y - edges[0].p.y, edges[0].q.x - edges[0].p.x);
  // A reversed or rotated ring must not turn the programme upside down.
  angle = ((angle + Math.PI / 2) % Math.PI + Math.PI) % Math.PI - Math.PI / 2;
  const rotate = (p: ParkPoint, theta: number): ParkPoint => ({ x: Math.cos(theta) * p.x - Math.sin(theta) * p.y, y: Math.sin(theta) * p.x + Math.cos(theta) * p.y });
  const ring = input.map(p => rotate(p, -angle)), box = bounds(ring);
  const w = box.maxX - box.minX, h = box.maxY - box.minY, cx = (box.maxX + box.minX) / 2, cy = (box.maxY + box.minY) / 2;
  if (w < 18 || h < 18) return { ...empty, notes: ['This footprint is too narrow for the neighbourhood park programme. Enlarge it or choose a pocket park.'] };
  const specifications: Array<{ kind: ParkModuleKind; width: number; depth: number; targetX: number; targetY: number }> = [
    { kind: 'pavilion', width: 10, depth: 8, targetX: 0, targetY: .32 },
    { kind: 'tower', width: 12, depth: 7.5, targetX: -.3, targetY: .27 },
    { kind: 'swing', width: 8, depth: 8, targetX: .21, targetY: .3 },
    { kind: 'tower', width: 12, depth: 7.5, targetX: .32, targetY: -.05 },
  ];
  let best: { lawn: ParkPoint[]; loop: ParkPoint[]; modules: ParkModule[]; score: number } | null = null;
  for (const scale of [1, .86, .72, .6]) {
    for (const shift of [0, -.16, .16]) {
      const lx = cx + shift * w, ly = cy - .12 * h, rx = Math.max(4, w * .29 * scale), ry = Math.max(4, h * .26 * scale);
      if (Math.PI * rx * ry < w * h * .20) continue;
      const lawn = ellipse(lx, ly, rx, ry), loop = ellipse(lx, ly, rx + 1.3, ry + 1.3), reserve = ellipse(lx, ly, rx + 3, ry + 3);
      if (!envelopeFits(reserve, ring, .8)) continue;
      const modules: ParkModule[] = [];
      const programme = w * h < 2200 || Math.min(w, h) < 40 ? specifications.slice(0, 3) : specifications;
      for (const spec of programme) {
        const candidates: Array<{ p: ParkPoint; envelope: ParkPoint[]; score: number }> = [];
        for (let x = box.minX + spec.width / 2 + 1; x <= box.maxX - spec.width / 2 - 1; x += Math.max(2,w/40)) {
          for (let y = box.minY + spec.depth / 2 + 1; y <= box.maxY - spec.depth / 2 - 1; y += Math.max(2,h/40)) {
            const envelope = rect(x, y, spec.width, spec.depth);
            if (!envelopeFits(envelope, ring, .8) || envelopesOverlap(envelope, reserve)
              || modules.some(m => envelopesOverlap(envelope, m.envelope))) continue;
            candidates.push({ p: { x, y }, envelope, score: Math.hypot(x - cx - spec.targetX * w, y - cy - spec.targetY * h) });
          }
        }
        candidates.sort((a, b) => a.score - b.score);
        const candidate = candidates[0];
        if (candidate) modules.push({ id: `${spec.kind}-${modules.filter(m => m.kind === spec.kind).length + 1}`, kind: spec.kind, center: candidate.p, yaw: angle, width: spec.width, depth: spec.depth, envelope: candidate.envelope });
      }
      // Keep the source's lawn dominant; never exchange it for extra equipment.
      const score = modules.length * 10000 + rx * ry;
      if (!best || score > best.score) best = { lawn, loop, modules, score };
    }
  }
  if (!best) return { ...empty, notes: ['The lawn and walking loop do not fit inside this shape. Widen the usable park area.'] };
  const paths: ParkPoint[][] = [];
  const connectedModules: ParkModule[] = [];
  for (const module of best.modules) {
    const offsets = module.kind === 'tower' ? [[-module.width / 2, 0], [0, -module.depth / 2], [0, module.depth / 2]]
      : module.kind === 'swing' ? [[-module.width / 2, 0], [module.width / 2, 0]]
        : [[-module.width / 2, 0], [module.width / 2, 0], [0, -module.depth / 2], [0, module.depth / 2]];
    const candidates = offsets.flatMap(([x, y]) => best!.loop.map(target => {
      const arrival = { x: module.center.x + x, y: module.center.y + y };
      return { arrival, target, distance: Math.hypot(target.x - arrival.x, target.y - arrival.y) };
    })).sort((a, b) => a.distance - b.distance);
    const connection = candidates.find(({ arrival, target: p, distance: length }) => {
      if (length < .3) return false;
      const dx = p.x - arrival.x, dy = p.y - arrival.y;
      if (dx * (arrival.x - module.center.x) + dy * (arrival.y - module.center.y) <= 0) return false;
      const corridor = [{ x: arrival.x - dy / length * 1.3, y: arrival.y + dx / length * 1.3 }, { x: p.x - dy / length * 1.3, y: p.y + dx / length * 1.3 }, { x: p.x + dy / length * 1.3, y: p.y - dx / length * 1.3 }, { x: arrival.x + dy / length * 1.3, y: arrival.y - dx / length * 1.3 }];
      return envelopeFits(corridor, ring, .1) && !best!.modules.some(other => other !== module && envelopesOverlap(corridor, other.envelope));
    });
    if (connection) { paths.push([connection.arrival, connection.target]); connectedModules.push({ ...module, arrival: connection.arrival }); }
  }
  const trees: ParkPoint[] = [], shrubs: ParkPoint[] = [];
  for (let x = box.minX + 1; x < box.maxX; x += Math.max(2.2,w/60)) for (let y = box.minY + 1; y < box.maxY; y += Math.max(2.2,h/60)) {
    const seed = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453, jitter = seed - Math.floor(seed);
    const p = { x: x + (jitter - .5), y: y + Math.sin(seed) * .5 }, edge = edgeDistance(p, ring);
    if (!pointInPark(p, ring) || pointInPark(p, best.lawn) || edge < 1.1 || edge > 9
      || best.loop.some((q, i) => distanceToSegment(p, q, best!.loop[(i + 1) % 64]) < 3)
      || connectedModules.some(m => pointInPark(p, m.envelope) || edgeDistance(p, m.envelope) < 2)
      || paths.some(path => distanceToSegment(p, path[0], path[1]) < 2.5)) continue;
    if (edge > 3.1 && trees.length < 70 && trees.every(q => Math.hypot(p.x - q.x, p.y - q.y) > 5.8)) trees.push(p);
    else if (shrubs.length < 260 && jitter > .2) shrubs.push(p);
  }
  const world = (p: ParkPoint) => rotate(p, angle);
  const full = connectedModules.length === 4;
  return { ...empty, status: full ? 'full' : connectedModules.length >= 2 ? 'compact' : 'constrained',
    lawn: best.lawn.map(world), loop: best.loop.map(world), paths: paths.map(path => path.map(world)),
    modules: connectedModules.map(m => ({ ...m, center: world(m.center), arrival: m.arrival ? world(m.arrival) : undefined, envelope: m.envelope.map(world) })),
    trees: trees.map(world), shrubs: shrubs.map(world),
    notes: full ? ['Two play pockets, one pavilion, one swing and a continuous lawn loop.'] : [`Compact arrangement: ${connectedModules.filter(m => m.kind === 'tower').length} play pocket(s), ${connectedModules.filter(m => m.kind === 'pavilion').length} pavilion, ${connectedModules.filter(m => m.kind === 'swing').length} swing. Equipment retains its size; omitted elements are not hidden elsewhere.`] };
}

const layoutCache = new Map<string, NeighborhoodParkLayout>();
export function neighborhoodParkLayoutForZone(zone: SiteZone, origin: { lng: number; lat: number }): NeighborhoodParkLayout {
  const key = JSON.stringify([zone.coordinates, origin.lng, origin.lat]);
  const cached = layoutCache.get(key);
  if (cached) return cached;
  const east = metersPerDegLon(origin.lat);
  const result = buildNeighborhoodParkLayout(zone.coordinates.map(([lng, lat]) => ({ x: (lng - origin.lng) * east, y: (lat - origin.lat) * METERS_PER_DEG_LAT })));
  if (layoutCache.size >= 32) layoutCache.delete(layoutCache.keys().next().value!);
  layoutCache.set(key, result);
  return result;
}

/** Diagram guides describe the SAME composed objects, not a second scatter. */
export function neighborhoodParkGuides(zone: SiteZone): ParkGroundGuide[] {
  const origin = { lng: zone.coordinates[0][0], lat: zone.coordinates[0][1] };
  const layout = neighborhoodParkLayoutForZone(zone, origin), box = bounds(layout.boundary);
  const w = box.maxX - box.minX, h = box.maxY - box.minY;
  const guide = (points: ParkPoint[], color: string, closed: boolean, strokeWidthM?: number): ParkGroundGuide => ({ kind: 'polyline', x: .5, y: .5, width: 1, height: 1, color, points: points.map(p => [(p.x - box.minX) / w, (box.maxY - p.y) / h]), closed, strokeWidthM, strokeColor: color, fitPolicy: 'clip' });
  return [ ...(layout.loop.length ? [guide(layout.loop, '#c9bda5', true, layout.pathWidth)] : []),
    ...layout.paths.map(path => guide(path, '#c9bda5', false, layout.pathWidth)),
    ...layout.modules.map(m => ({ kind: 'rounded_rectangle' as const, x: (m.center.x - box.minX) / w, y: (box.maxY - m.center.y) / h, width: m.width / w, height: m.depth / h, color: m.kind === 'pavilion' ? '#b6aa8d' : '#cbb996', rotationDeg: -m.yaw * 180 / Math.PI, fitPolicy: 'clip' as const })) ];
}
