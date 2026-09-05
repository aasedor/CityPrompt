import type { OSMContext, OSMContextRoad, SiteZone } from '@/types';
import { resolveCommunity3DKind, type Community3DKind } from '@/features/community3d/community3d';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

type Coordinate = [number, number];
type PublicRealmKind = Extract<Community3DKind, 'park' | 'street'>;

export interface PublicRealmContextNeighbor {
  source: 'proposal' | 'existing_map';
  id: string;
  kind: Community3DKind | 'existing_road';
  label: string;
  distance_m: number;
  relation: 'edge-connected' | 'fronting' | 'nearby';
  direction: string;
  floors?: number;
  height_m?: number;
  width_m?: number;
}
export interface PublicRealmGenerationContext {
  schema_version: 1;
  target_zone_id: string;
  target_kind: PublicRealmKind;
  target_label: string;
  target_elevation_m?: number;
  neighbors: PublicRealmContextNeighbor[];
}

export interface PublicRealmPromptOptions {
  /** The render request includes a live globe frame containing Google tiles. */
  sceneReferenceAttached?: boolean;
  /** Keep a focused per-zone clause short enough for sequential render calls. */
  compact?: boolean;
}

const MAX_PROPOSAL_NEIGHBORS = 8;
const MAX_EXISTING_ROADS = 4;
const PROPOSAL_SEARCH_M = 70;
const EXISTING_ROAD_SEARCH_M = 45;

function asFiniteNumber(value: unknown): number | undefined {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim()) {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return undefined;
}

function cleanCoordinates(value: unknown): Coordinate[] {
  if (!Array.isArray(value)) return [];
  const coordinates = value.flatMap((candidate) => {
    if (!Array.isArray(candidate) || candidate.length < 2) return [];
    const lng = Number(candidate[0]);
    const lat = Number(candidate[1]);
    return Number.isFinite(lng) && Number.isFinite(lat)
      ? [[lng, lat] as Coordinate]
      : [];
  });
  if (
    coordinates.length > 1
    && coordinates[0][0] === coordinates[coordinates.length - 1][0]
    && coordinates[0][1] === coordinates[coordinates.length - 1][1]
  ) {
    coordinates.pop();
  }
  return coordinates;
}

function centroid(ring: Coordinate[]): Coordinate {
  if (ring.length === 0) return [0, 0];
  return [
    ring.reduce((sum, point) => sum + point[0], 0) / ring.length,
    ring.reduce((sum, point) => sum + point[1], 0) / ring.length,
  ];
}

interface MetricProjector {
  toMetric: (point: Coordinate) => Coordinate;
}

function metricProjector(targetRing: Coordinate[]): MetricProjector {
  const [originLng, originLat] = centroid(targetRing);
  const lngScale = metersPerDegLon(originLat);
  return {
    toMetric: ([lng, lat]) => [
      (lng - originLng) * lngScale,
      (lat - originLat) * METERS_PER_DEG_LAT,
    ],
  };
}

function pointInRing(point: Coordinate, ring: Coordinate[]): boolean {
  let inside = false;
  for (let index = 0, previous = ring.length - 1; index < ring.length; previous = index, index += 1) {
    const [x, y] = ring[index];
    const [previousX, previousY] = ring[previous];
    if (
      (y > point[1]) !== (previousY > point[1])
      && point[0] < ((previousX - x) * (point[1] - y)) / (previousY - y) + x
    ) {
      inside = !inside;
    }
  }
  return inside;
}

function pointToSegmentDistance(point: Coordinate, start: Coordinate, end: Coordinate): number {
  const dx = end[0] - start[0];
  const dy = end[1] - start[1];
  if (dx === 0 && dy === 0) return Math.hypot(point[0] - start[0], point[1] - start[1]);
  const position = Math.max(0, Math.min(1, (
    (point[0] - start[0]) * dx + (point[1] - start[1]) * dy
  ) / (dx * dx + dy * dy)));
  return Math.hypot(
    point[0] - (start[0] + position * dx),
    point[1] - (start[1] + position * dy),
  );
}

function orientation(a: Coordinate, b: Coordinate, c: Coordinate): number {
  return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
}

function segmentsIntersect(a: Coordinate, b: Coordinate, c: Coordinate, d: Coordinate): boolean {
  const abC = orientation(a, b, c);
  const abD = orientation(a, b, d);
  const cdA = orientation(c, d, a);
  const cdB = orientation(c, d, b);
  const epsilon = 1e-7;
  if (
    Math.abs(abC) <= epsilon && pointToSegmentDistance(c, a, b) <= epsilon
    || Math.abs(abD) <= epsilon && pointToSegmentDistance(d, a, b) <= epsilon
    || Math.abs(cdA) <= epsilon && pointToSegmentDistance(a, c, d) <= epsilon
    || Math.abs(cdB) <= epsilon && pointToSegmentDistance(b, c, d) <= epsilon
  ) return true;
  return (abC > 0) !== (abD > 0) && (cdA > 0) !== (cdB > 0);
}

function segmentDistance(a: Coordinate, b: Coordinate, c: Coordinate, d: Coordinate): number {
  if (segmentsIntersect(a, b, c, d)) return 0;
  return Math.min(
    pointToSegmentDistance(a, c, d),
    pointToSegmentDistance(b, c, d),
    pointToSegmentDistance(c, a, b),
    pointToSegmentDistance(d, a, b),
  );
}

function geometryDistanceM(
  targetRingWgs84: Coordinate[],
  otherWgs84: Coordinate[],
  otherIsPolygon: boolean,
): number {
  if (targetRingWgs84.length < 3 || otherWgs84.length < 2) return Number.POSITIVE_INFINITY;
  const projector = metricProjector(targetRingWgs84);
  const target = targetRingWgs84.map(projector.toMetric);
  const other = otherWgs84.map(projector.toMetric);
  if (otherIsPolygon && other.length >= 3) {
    if (pointInRing(target[0], other) || pointInRing(other[0], target)) return 0;
  }
  let minimum = Number.POSITIVE_INFINITY;
  const targetSegmentCount = target.length;
  const otherSegmentCount = otherIsPolygon ? other.length : other.length - 1;
  for (let targetIndex = 0; targetIndex < targetSegmentCount; targetIndex += 1) {
    const targetStart = target[targetIndex];
    const targetEnd = target[(targetIndex + 1) % target.length];
    for (let otherIndex = 0; otherIndex < otherSegmentCount; otherIndex += 1) {
      minimum = Math.min(minimum, segmentDistance(
        targetStart,
        targetEnd,
        other[otherIndex],
        other[(otherIndex + 1) % other.length],
      ));
      if (minimum === 0) return 0;
    }
  }
  return minimum;
}

function directionFromTarget(targetRing: Coordinate[], otherCoordinates: Coordinate[]): string {
  const projector = metricProjector(targetRing);
  const targetCenter = projector.toMetric(centroid(targetRing));
  const otherCenter = projector.toMetric(centroid(otherCoordinates));
  const dx = otherCenter[0] - targetCenter[0];
  const dy = otherCenter[1] - targetCenter[1];
  if (Math.hypot(dx, dy) < 0.5) return 'overlapping the target edge';
  const eastWest = dx >= 0 ? 'east' : 'west';
  const northSouth = dy >= 0 ? 'north' : 'south';
  if (Math.abs(dx) > Math.abs(dy) * 1.7) return `on the ${eastWest} edge`;
  if (Math.abs(dy) > Math.abs(dx) * 1.7) return `on the ${northSouth} edge`;
  return `at the ${northSouth}-${eastWest} corner`;
}

function relationForDistance(distanceM: number): PublicRealmContextNeighbor['relation'] {
  if (distanceM <= 2.5) return 'edge-connected';
  if (distanceM <= 12) return 'fronting';
  return 'nearby';
}

function readableId(value: unknown): string | undefined {
  if (typeof value !== 'string' || !value.trim()) return undefined;
  return value
    .replace(/\*variant\*\d+$/i, '')
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function zoneLabel(zone: SiteZone, kind: Community3DKind): string {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const identity = kind === 'building'
    ? props.development_archetype_id ?? props.generation_archetype_id
    : kind === 'street'
      ? props.road_archetype_id
      : props.green_space_archetype_id ?? props.plaza_archetype_id;
  return zone.name?.trim() || readableId(identity) || `${kind} zone`;
}

function neighborMetrics(zone: SiteZone): Pick<PublicRealmContextNeighbor, 'floors' | 'height_m' | 'width_m'> {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const floors = asFiniteNumber(props.floors ?? props.floor_count);
  const height = asFiniteNumber(props.height_m ?? props.height);
  const width = asFiniteNumber(props.width_m ?? props.width ?? props.road_width_m);
  return {
    ...(floors && floors > 0 ? { floors: Math.round(floors) } : {}),
    ...(height && height > 0 ? { height_m: Math.round(height * 10) / 10 } : {}),
    ...(width && width > 0 ? { width_m: Math.round(width * 10) / 10 } : {}),
  };
}

function osmContexts(zones: SiteZone[]): OSMContext[] {
  const seen = new Set<OSMContext>();
  const contexts: OSMContext[] = [];
  for (const zone of zones) {
    const candidate = (zone.properties as Record<string, unknown> | undefined)?._osm_context;
    if (!candidate || typeof candidate !== 'object' || seen.has(candidate as OSMContext)) continue;
    seen.add(candidate as OSMContext);
    contexts.push(candidate as OSMContext);
  }
  return contexts;
}

function existingRoadNeighbors(targetRing: Coordinate[], zones: SiteZone[]): PublicRealmContextNeighbor[] {
  const roads = new Map<string, OSMContextRoad>();
  for (const context of osmContexts(zones)) {
    for (const road of Array.isArray(context.roads) ? context.roads : []) {
      roads.set(String(road.osm_id), road);
    }
  }
  return [...roads.values()].flatMap((road) => {
    const coordinates = cleanCoordinates(road.coordinates);
    const distanceM = geometryDistanceM(targetRing, coordinates, false);
    if (!Number.isFinite(distanceM) || distanceM > EXISTING_ROAD_SEARCH_M) return [];
    return [{
      source: 'existing_map' as const,
      id: `osm-road-${road.osm_id}`,
      kind: 'existing_road' as const,
      label: road.name?.trim() || readableId(road.road_type) || 'existing mapped roadway',
      distance_m: Math.round(distanceM * 10) / 10,
      relation: relationForDistance(distanceM),
      direction: directionFromTarget(targetRing, coordinates),
      ...(asFiniteNumber(road.width_m) ? { width_m: Math.round(Number(road.width_m) * 10) / 10 } : {}),
    }];
  }).sort(compareNeighbors).slice(0, MAX_EXISTING_ROADS);
}

function neighborPriority(neighbor: PublicRealmContextNeighbor): number {
  const relation = neighbor.relation === 'edge-connected' ? 300 : neighbor.relation === 'fronting' ? 200 : 100;
  const kind = neighbor.kind === 'street' || neighbor.kind === 'existing_road'
    ? 30
    : neighbor.kind === 'building'
      ? 20
      : 10;
  return relation + kind;
}

function compareNeighbors(left: PublicRealmContextNeighbor, right: PublicRealmContextNeighbor): number {
  return neighborPriority(right) - neighborPriority(left)
    || left.distance_m - right.distance_m
    || left.kind.localeCompare(right.kind)
    || left.id.localeCompare(right.id);
}

export function buildPublicRealmGenerationContext(
  target: SiteZone,
  allZones: SiteZone[],
): PublicRealmGenerationContext | null {
  const targetKind = resolveCommunity3DKind(target);
  const targetRing = cleanCoordinates(target.coordinates);
  if ((targetKind !== 'park' && targetKind !== 'street') || targetRing.length < 3) return null;

  const proposalNeighbors = allZones.flatMap((candidate) => {
    if (candidate.id === target.id) return [];
    const kind = resolveCommunity3DKind(candidate);
    const coordinates = cleanCoordinates(candidate.coordinates);
    if (!kind || coordinates.length < 3) return [];
    const distanceM = geometryDistanceM(targetRing, coordinates, true);
    if (!Number.isFinite(distanceM) || distanceM > PROPOSAL_SEARCH_M) return [];
    return [{
      source: 'proposal' as const,
      id: candidate.id,
      kind,
      label: zoneLabel(candidate, kind),
      distance_m: Math.round(distanceM * 10) / 10,
      relation: relationForDistance(distanceM),
      direction: directionFromTarget(targetRing, coordinates),
      ...neighborMetrics(candidate),
    }];
  }).sort(compareNeighbors).slice(0, MAX_PROPOSAL_NEIGHBORS);

  const props = (target.properties ?? {}) as Record<string, unknown>;
  const elevation = asFiniteNumber(
    props.terrain_elevation_m ?? props.ground_elevation_m ?? props.elevation_m,
  );
  return {
    schema_version: 1,
    target_zone_id: target.id,
    target_kind: targetKind,
    target_label: zoneLabel(target, targetKind),
    ...(elevation !== undefined ? { target_elevation_m: Math.round(elevation * 10) / 10 } : {}),
    neighbors: [...proposalNeighbors, ...existingRoadNeighbors(targetRing, allZones)]
      .sort(compareNeighbors),
  };
}

function metricDescription(neighbor: PublicRealmContextNeighbor): string {
  const metrics: string[] = [];
  if (neighbor.floors) metrics.push(`${neighbor.floors} floors`);
  if (neighbor.height_m) metrics.push(`${neighbor.height_m} m high`);
  if (neighbor.width_m) metrics.push(`${neighbor.width_m} m wide`);
  return metrics.length > 0 ? ` (${metrics.join(', ')})` : '';
}

function neighborDescription(neighbor: PublicRealmContextNeighbor): string {
  const source = neighbor.source === 'existing_map' ? 'existing mapped road' : `proposed ${neighbor.kind}`;
  const spacing = neighbor.relation === 'edge-connected'
    ? 'touches'
    : neighbor.relation === 'fronting'
      ? `fronts at ${Math.round(neighbor.distance_m)} m`
      : `is ${Math.round(neighbor.distance_m)} m away`;
  return `${source} "${neighbor.label}"${metricDescription(neighbor)} ${spacing} ${neighbor.direction}`;
}

function edgeResponseRule(kind: PublicRealmKind): string {
  return kind === 'park'
    ? 'Put primary park gateways on street/path-facing edges, align paths and accessible grades to those approaches, protect clear building entrances, and use planting or seating to mediate building-facing edges. Do not invent a gateway where the locked diagram has none.'
    : 'Keep carriageways, paths, curbs and cycle tracks continuous into connected corridors; align sidewalks and crossings with park gates and building entrances; keep doors, driveways, sight triangles and accessible routes unobstructed.';
}

export function buildPublicRealmContextPrompt(
  target: SiteZone,
  allZones: SiteZone[],
  options: PublicRealmPromptOptions = {},
): string {
  const context = buildPublicRealmGenerationContext(target, allZones);
  if (!context) return '';
  const limit = options.compact ? 4 : context.neighbors.length;
  const neighborLines = context.neighbors.slice(0, limit).map(neighborDescription);
  const omitted = Math.max(0, context.neighbors.length - limit);
  const sceneClause = options.sceneReferenceAttached
    ? 'The input/live-scene reference shows the current Google photogrammetry, terrain and mounted 3D buildings; use it to match grade, curb seams, façade scale, lighting and material transitions. It is context evidence only and may not override the target polygon or locked internal geometry.'
    : 'No live Google-tile frame is attached, so use the measured relationships below conservatively and do not invent off-site geometry.';
  return [
    'SURROUNDING-SITE CONTEXT (authoritative for boundary interfaces; target geometry remains locked):',
    ...(neighborLines.length > 0
      ? neighborLines.map((line) => `- ${line}`)
      : ['- No proposed or mapped public-realm neighbor lies within the bounded context radius.']),
    ...(omitted > 0 ? [`- ${omitted} lower-priority nearby feature${omitted === 1 ? '' : 's'} omitted from this compact prompt.`] : []),
    `EDGE RESPONSE: ${edgeResponseRule(context.target_kind)}`,
    `GOOGLE/TERRAIN EVIDENCE: ${sceneClause}`,
  ].join('\n');
}

/** Bounded scene-wide clause shared by Classic and Direct 3D render calls. */
export function buildPublicRealmSceneContextPrompt(
  zones: SiteZone[],
  options: PublicRealmPromptOptions = {},
  maxTargets = 12,
): string {
  const targets = zones
    .filter((zone) => {
      const kind = resolveCommunity3DKind(zone);
      return kind === 'park' || kind === 'street';
    })
    .sort((left, right) => left.id.localeCompare(right.id));
  if (targets.length === 0) return '';
  const selected = targets.slice(0, Math.max(0, maxTargets));
  const lines = selected.flatMap((target) => {
    const context = buildPublicRealmGenerationContext(target, zones);
    if (!context) return [];
    const relationships = context.neighbors.slice(0, 4).map(neighborDescription);
    return [`- ${context.target_kind} "${context.target_label}": ${relationships.length > 0 ? relationships.join('; ') : 'no nearby measured interface'}.`];
  });
  const omitted = Math.max(0, targets.length - selected.length);
  return [
    'PUBLIC-REALM EDGE COORDINATION:',
    ...lines,
    ...(omitted > 0 ? [`- ${omitted} additional public-realm zone${omitted === 1 ? '' : 's'} remain governed by the same edge rules and visible image geometry.`] : []),
    'Use these measured relationships to identify the captured interfaces. Preserve existing park gates, sidewalks, crossings, curbs, paths and building entrances in their captured positions. Missing connections remain missing: recommend them in the planning report rather than drawing them into this render.',
    options.sceneReferenceAttached
      ? 'The captured Google-tile scene and mounted 3D buildings are the visual authority for existing grade, adjacent roadway position, façade scale, lighting and edge materials.'
      : 'No live Google-tile scene is attached; do not invent existing off-site features.',
  ].join('\n');
}
