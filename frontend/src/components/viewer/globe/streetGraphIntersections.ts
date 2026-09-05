import type { SiteZone } from '@/types';
import { effectiveRoadWidth, extractZoneCenterline, parsePersistedCenterline } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import {
  PUBLIC_REALM_STREET_CATALOG_FINGERPRINT,
  PUBLIC_REALM_STREET_FAMILY_VERSION,
} from './streetFamilyCatalog';
import { validateStreetRecipeProperties } from './streetLegoContract';

interface LocalPoint {
  x: number;
  y: number;
}

interface StreetAxis {
  zoneId: string;
  widthM: number;
  points: LocalPoint[];
  supportedV1: boolean;
}

interface NodeCandidate {
  x: number;
  y: number;
  zoneIds: [string, string];
}

interface StreetIntersectionBase {
  id: string;
  longitude: number;
  latitude: number;
  axisABearingRad: number;
  axisBBearingRad: number;
  axisAHalfWidthM: number;
  axisBHalfWidthM: number;
  zoneIds: string[];
  familyId: 'street_four_way_intersection' | 'street_t_intersection';
  familyVersion: typeof PUBLIC_REALM_STREET_FAMILY_VERSION;
  archetypeId: 'protected_intersection';
  variantId: 'protected_intersection_v0';
  appearanceKitId: 'dutch_corner_islands_v1';
  rendererFingerprint: string;
}

export interface FourWayStreetIntersection extends StreetIntersectionBase {
  familyId: 'street_four_way_intersection';
}

/** Directed approaches are authoritative: a T never borrows its absent fourth arm. */
export interface ConnectedStreetIntersection extends StreetIntersectionBase {
  armCount: 3 | 4;
  approachSides: [Array<-1 | 1>, Array<-1 | 1>];
  orthogonal: boolean;
}

export function detectFourWayStreetIntersections(zones: SiteZone[]): FourWayStreetIntersection[] {
  return detectStreetIntersections(zones, false) as FourWayStreetIntersection[];
}

/** Bounded connected surface pilot: T nodes must be orthogonal within one degree.
 * Existing skew four-way details remain available, without a new surface patch. */
export function detectConnectedStreetIntersections(zones: SiteZone[]): ConnectedStreetIntersection[] {
  const legacy = detectStreetIntersections(zones, false);
  const tees = detectStreetIntersections(zones, true).filter((node) => node.armCount === 3
    && !legacy.some((existing) => Math.hypot((existing.longitude - node.longitude) * metersPerDegLon(node.latitude),
      (existing.latitude - node.latitude) * METERS_PER_DEG_LAT) < 4));
  return [...legacy, ...tees].sort((a, b) => a.id.localeCompare(b.id));
}

function normalizeAngle(angle: number): number {
  const tau = Math.PI * 2;
  return ((angle % tau) + tau) % tau;
}

function undirectedAngle(angle: number): number {
  const normalized = normalizeAngle(angle);
  return normalized >= Math.PI ? normalized - Math.PI : normalized;
}

function angleDistance(a: number, b: number): number {
  const delta = Math.abs(normalizeAngle(a) - normalizeAngle(b));
  return Math.min(delta, Math.PI * 2 - delta);
}

function undirectedAngleDistance(a: number, b: number): number {
  const delta = Math.abs(undirectedAngle(a) - undirectedAngle(b));
  return Math.min(delta, Math.PI - delta);
}

function closestPointOnSegment(point: LocalPoint, start: LocalPoint, end: LocalPoint) {
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const lengthSquared = dx * dx + dy * dy;
  const t = lengthSquared > 0
    ? Math.max(0, Math.min(1, ((point.x - start.x) * dx + (point.y - start.y) * dy) / lengthSquared))
    : 0;
  const x = start.x + dx * t;
  const y = start.y + dy * t;
  return { x, y, t, distance: Math.hypot(point.x - x, point.y - y) };
}

function segmentIntersection(
  a0: LocalPoint,
  a1: LocalPoint,
  b0: LocalPoint,
  b1: LocalPoint,
): LocalPoint | null {
  const adx = a1.x - a0.x;
  const ady = a1.y - a0.y;
  const bdx = b1.x - b0.x;
  const bdy = b1.y - b0.y;
  const denominator = adx * bdy - ady * bdx;
  if (Math.abs(denominator) < 1e-7) return null;
  const qx = b0.x - a0.x;
  const qy = b0.y - a0.y;
  const ta = (qx * bdy - qy * bdx) / denominator;
  const tb = (qx * ady - qy * adx) / denominator;
  if (ta < -1e-6 || ta > 1 + 1e-6 || tb < -1e-6 || tb > 1 + 1e-6) return null;
  return { x: a0.x + adx * ta, y: a0.y + ady * ta };
}

function stableNodeId(longitude: number, latitude: number): string {
  const key = `${longitude.toFixed(7)}:${latitude.toFixed(7)}`;
  let hash = 2166136261;
  for (let index = 0; index < key.length; index += 1) {
    hash ^= key.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return `street-four-way-${(hash >>> 0).toString(16).padStart(8, '0')}`;
}

/**
 * Derive graph-owned four-way nodes from the street polygons currently
 * available to the globe. The plan payload does not yet persist graph node
 * IDs, so this bounded adapter accepts both true centerline crossings and the
 * ordered-subtraction form emitted by the planner (opposing local fragments
 * ending at the edge of a continuous main-street band).
 */
function detectStreetIntersections(
  zones: SiteZone[],
  includeThreeArm: boolean,
): ConnectedStreetIntersection[] {
  const eligibleZones = [...zones].sort((a, b) => a.id.localeCompare(b.id)).filter((zone) => {
    const props = zone.properties as Record<string, unknown> | undefined;
    const lego = props?.public_realm_lego && typeof props.public_realm_lego === 'object'
      ? props.public_realm_lego as Record<string, unknown>
      : undefined;
    const semantic = [props?.street_role, props?.road_archetype_id, lego?.archetype_id, lego?.family_id]
      .map((value) => String(value ?? '').toLowerCase().replace(/-/g, '_'))
      .join(' ');
    return effectiveRoadWidth(zone.properties) >= 6
      && !['trail', 'path', 'laneway', 'alley', 'roundabout'].some((token) => semantic.includes(token));
  });
  if (eligibleZones.length < 2) return [];
  const allCoordinates = eligibleZones.flatMap((zone) => zone.coordinates);
  if (allCoordinates.length === 0) return [];
  const originLng = allCoordinates.reduce((sum, point) => sum + point[0], 0) / allCoordinates.length;
  const originLat = allCoordinates.reduce((sum, point) => sum + point[1], 0) / allCoordinates.length;
  const mPerLon = metersPerDegLon(originLat);
  const axes: StreetAxis[] = eligibleZones.flatMap((zone) => {
    const centerline = extractZoneCenterline(zone);
    if (centerline.length < 2) return [];
    const validation = validateStreetRecipeProperties(zone.properties);
    // Junction anchoring requires a centerline BOTH sides derive identically.
    // Without a valid persisted plan_centerline this detector walks polygon
    // vertices while the server proof takes the minimum-rotated-rectangle
    // axis — for degenerate planner fragments (e.g. a 4 m roundabout access
    // stub whose centerline the AI planner omitted) the two diverge and the
    // server 409s every claim forever. So: a present-but-invalid centerline
    // never anchors a junction, and a planner-authored street (markers
    // below) must carry a valid one. Hand-drawn streets keep the fallback,
    // which both sides derive the same way for line-sourced geometry.
    const props = zone.properties as Record<string, unknown> | undefined;
    const persistedCenterlineValid = parsePersistedCenterline(props?.plan_centerline) !== null;
    const centerlineAnchorsJunction = persistedCenterlineValid
      || (
        props != null
        && !('plan_centerline' in props)
        && !('_plan_snapshot_id' in props)
        && !('_imported_from' in props)
      );
    return [{
      zoneId: zone.id,
      widthM: effectiveRoadWidth(zone.properties),
      supportedV1: validation.valid
        && centerlineAnchorsJunction
        && validation.recipe.targetType === 'street_segment'
        && [
          'street_local_public_realm',
          'street_complete_main_18m',
          'street_complete_main_22m',
        ].includes(validation.recipe.familyId),
      points: centerline.map((point) => ({
        x: (point[0] - originLng) * mPerLon,
        y: (point[1] - originLat) * METERS_PER_DEG_LAT,
      })),
    }];
  });
  const candidates: NodeCandidate[] = [];
  for (let firstIndex = 0; firstIndex < axes.length; firstIndex += 1) {
    const first = axes[firstIndex];
    for (let secondIndex = firstIndex + 1; secondIndex < axes.length; secondIndex += 1) {
      const second = axes[secondIndex];
      const connectionTolerance = Math.max(first.widthM, second.widthM) / 2 + 2;
      for (let a = 0; a < first.points.length - 1; a += 1) {
        const a0 = first.points[a];
        const a1 = first.points[a + 1];
        const aBearing = Math.atan2(a1.y - a0.y, a1.x - a0.x);
        for (let b = 0; b < second.points.length - 1; b += 1) {
          const b0 = second.points[b];
          const b1 = second.points[b + 1];
          const bBearing = Math.atan2(b1.y - b0.y, b1.x - b0.x);
          const crossingAngle = undirectedAngleDistance(aBearing, bBearing);
          if (crossingAngle < Math.PI / 6 || crossingAngle > Math.PI * 5 / 6) continue;
          const crossing = segmentIntersection(a0, a1, b0, b1);
          if (crossing) {
            candidates.push({ x: crossing.x, y: crossing.y, zoneIds: [first.zoneId, second.zoneId] });
            continue;
          }
          for (const endpoint of [a0, a1]) {
            const projection = closestPointOnSegment(endpoint, b0, b1);
            if (projection.distance <= connectionTolerance) {
              candidates.push({ x: projection.x, y: projection.y, zoneIds: [first.zoneId, second.zoneId] });
            }
          }
          for (const endpoint of [b0, b1]) {
            const projection = closestPointOnSegment(endpoint, a0, a1);
            if (projection.distance <= connectionTolerance) {
              candidates.push({ x: projection.x, y: projection.y, zoneIds: [first.zoneId, second.zoneId] });
            }
          }
        }
      }
    }
  }
  const clusters: Array<{ x: number; y: number; count: number; zoneIds: Set<string> }> = [];
  for (const candidate of candidates) {
    const existing = clusters.find((cluster) => Math.hypot(cluster.x - candidate.x, cluster.y - candidate.y) <= 4);
    if (existing) {
      existing.x = (existing.x * existing.count + candidate.x) / (existing.count + 1);
      existing.y = (existing.y * existing.count + candidate.y) / (existing.count + 1);
      existing.count += 1;
      candidate.zoneIds.forEach((id) => existing.zoneIds.add(id));
    } else {
      clusters.push({
        x: candidate.x,
        y: candidate.y,
        count: 1,
        zoneIds: new Set(candidate.zoneIds),
      });
    }
  }

  return clusters.flatMap((cluster) => {
    const arms: Array<{ bearing: number; widthM: number; zoneId: string }> = [];
    const clusterConnectionTolerance = Math.max(
      2,
      ...axes
        .filter((axis) => cluster.zoneIds.has(axis.zoneId))
        .map((axis) => axis.widthM / 2 + 2),
    );
    const contributingAxes: StreetAxis[] = [];
    for (const axis of axes) {
      let best: ReturnType<typeof closestPointOnSegment> & { segmentIndex: number } | null = null;
      for (let index = 0; index < axis.points.length - 1; index += 1) {
        const closest = closestPointOnSegment(cluster, axis.points[index], axis.points[index + 1]);
        if (!best || closest.distance < best.distance) best = { ...closest, segmentIndex: index };
      }
      if (!best || best.distance > Math.max(axis.widthM / 2 + 2, clusterConnectionTolerance)) continue;
      contributingAxes.push(axis);
      const start = axis.points[best.segmentIndex];
      const end = axis.points[best.segmentIndex + 1];
      const bearing = Math.atan2(end.y - start.y, end.x - start.x);
      const length = Math.hypot(end.x - start.x, end.y - start.y);
      const atFirstEnd = best.segmentIndex === 0 && (includeThreeArm ? best.t * length < 2 : best.t < 0.08);
      const atLastEnd = best.segmentIndex === axis.points.length - 2 && (includeThreeArm ? (1 - best.t) * length < 2 : best.t > 0.92);
      if (!atLastEnd) arms.push({ bearing, widthM: axis.widthM, zoneId: axis.zoneId });
      if (!atFirstEnd) arms.push({ bearing: normalizeAngle(bearing + Math.PI), widthM: axis.widthM, zoneId: axis.zoneId });
    }
    // Accessible V1 node geometry is an executable-family feature. A legacy,
    // partial, mismatched, or node-family road near the inferred graph node
    // keeps the entire crossing on the Classic path.
    if (contributingAxes.length < 2 || contributingAxes.some((axis) => !axis.supportedV1)) return [];
    const groupedArms: typeof arms = [];
    for (const arm of arms) {
      const existing = groupedArms.find((candidate) => angleDistance(candidate.bearing, arm.bearing) < Math.PI / 9);
      if (existing) {
        existing.widthM = Math.max(existing.widthM, arm.widthM);
      } else {
        groupedArms.push({ ...arm });
      }
    }
    if (groupedArms.length !== 4 && !(includeThreeArm && groupedArms.length === 3)) return [];
    const orientations: Array<{ bearing: number; halfWidthM: number }> = [];
    for (const arm of groupedArms) {
      const orientation = undirectedAngle(arm.bearing);
      const existing = orientations.find((candidate) => (
        undirectedAngleDistance(candidate.bearing, orientation) < Math.PI / 12
      ));
      if (existing) existing.halfWidthM = Math.max(existing.halfWidthM, arm.widthM / 2);
      else orientations.push({ bearing: orientation, halfWidthM: arm.widthM / 2 });
    }
    if (orientations.length !== 2) return [];
    // For a T, axis A is the through street; this makes its closed back edge explicit.
    orientations.sort((a, b) => {
      const count = (bearing: number) => groupedArms.filter((arm) => undirectedAngleDistance(arm.bearing, bearing) < Math.PI / 12).length;
      return count(b.bearing) - count(a.bearing) || a.bearing - b.bearing;
    });
    const axisA = orientations[0];
    const axisB = orientations.find((candidate) => {
      const separation = undirectedAngleDistance(axisA.bearing, candidate.bearing);
      return separation >= Math.PI / 6 && separation <= Math.PI * 5 / 6;
    });
    if (!axisB) return [];
    const orthogonal = Math.abs(undirectedAngleDistance(axisA.bearing, axisB.bearing) - Math.PI / 2) <= Math.PI / 180;
    if (groupedArms.length === 3 && (!orthogonal || arms.some((arm) =>
      Math.min(undirectedAngleDistance(arm.bearing, axisA.bearing), undirectedAngleDistance(arm.bearing, axisB.bearing)) > Math.PI / 180))) return [];
    const approachSides = [axisA, axisB].map((axis) => ([-1, 1] as const).filter((side) => (
      groupedArms.some((arm) => angleDistance(arm.bearing, axis.bearing + (side === -1 ? Math.PI : 0)) < Math.PI / 12)
    ))) as ConnectedStreetIntersection['approachSides'];
    if (approachSides[0].length + approachSides[1].length !== groupedArms.length) return [];
    const longitude = originLng + cluster.x / mPerLon;
    const latitude = originLat + cluster.y / METERS_PER_DEG_LAT;
    return [{
      id: groupedArms.length === 4 ? stableNodeId(longitude, latitude) : stableNodeId(longitude, latitude).replace('four-way', 'three-way'),
      armCount: groupedArms.length as 3 | 4,
      approachSides,
      orthogonal,
      longitude,
      latitude,
      axisABearingRad: axisA.bearing,
      axisBBearingRad: axisB.bearing,
      axisAHalfWidthM: axisA.halfWidthM,
      axisBHalfWidthM: axisB.halfWidthM,
      zoneIds: [...new Set(contributingAxes.map((axis) => axis.zoneId))].sort(),
      familyId: groupedArms.length === 4 ? 'street_four_way_intersection' as const : 'street_t_intersection' as const,
      familyVersion: PUBLIC_REALM_STREET_FAMILY_VERSION,
      archetypeId: 'protected_intersection' as const,
      variantId: 'protected_intersection_v0' as const,
      appearanceKitId: 'dutch_corner_islands_v1' as const,
      rendererFingerprint: PUBLIC_REALM_STREET_CATALOG_FINGERPRINT,
    }];
  }).sort((left, right) => left.id.localeCompare(right.id));
}
