import type { SiteZone } from '@/types';
import { pointInPolygon } from '@/utils/coordTransform';

// Metric planning geometry is projected back to WGS84 before persistence.
// Shared edges can then differ by ~1-3 cm through round-trip precision even
// though they are topologically the same seam. Allow 5.5 cm at Calgary's
// latitude; shifted/stale plans remain metres outside and are still blocked.
const BOUNDARY_EPSILON_DEG = 5e-7;

function normalizeBoundaryRing(coordinates: number[][]): number[][] {
  const ring: number[][] = [];
  for (const coordinate of coordinates) {
    if (!Array.isArray(coordinate) || coordinate.length < 2) continue;
    const point = [Number(coordinate[0]), Number(coordinate[1])];
    if (!Number.isFinite(point[0]) || !Number.isFinite(point[1])) continue;
    const previous = ring[ring.length - 1];
    if (
      !previous
      || Math.abs(point[0] - previous[0]) > BOUNDARY_EPSILON_DEG
      || Math.abs(point[1] - previous[1]) > BOUNDARY_EPSILON_DEG
    ) {
      ring.push(point);
    }
  }
  if (
    ring.length >= 4
    && Math.abs(ring[ring.length - 1][0] - ring[0][0]) <= BOUNDARY_EPSILON_DEG
    && Math.abs(ring[ring.length - 1][1] - ring[0][1]) <= BOUNDARY_EPSILON_DEG
  ) {
    ring.pop();
  }
  return ring;
}

function pointSegmentDistance(
  px: number,
  py: number,
  ax: number,
  ay: number,
  bx: number,
  by: number,
): number {
  const dx = bx - ax;
  const dy = by - ay;
  const length2 = dx * dx + dy * dy;
  if (length2 === 0) return Math.hypot(px - ax, py - ay);
  const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / length2));
  return Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
}

function pointInOrOnBoundary(point: number[], boundary: number[][]): boolean {
  if (pointInPolygon(point[0], point[1], boundary)) return true;
  for (let i = 0; i < boundary.length; i += 1) {
    const a = boundary[i];
    const b = boundary[(i + 1) % boundary.length];
    if (pointSegmentDistance(point[0], point[1], a[0], a[1], b[0], b[1]) <= BOUNDARY_EPSILON_DEG) {
      return true;
    }
  }
  return false;
}

/** Sample vertices and edge quartiles so a chord across a concave notch is
 * rejected even when both of its endpoints happen to lie inside the site. */
export function planZoneFitsBoundary(zone: SiteZone, boundary: SiteZone): boolean {
  const boundaryRing = normalizeBoundaryRing(boundary.coordinates);
  if (zone.coordinates.length < 3 || boundaryRing.length < 3) return false;
  const samples: number[][] = [];
  for (let i = 0; i < zone.coordinates.length; i += 1) {
    const a = zone.coordinates[i];
    const b = zone.coordinates[(i + 1) % zone.coordinates.length];
    samples.push(a);
    for (const t of [0.25, 0.5, 0.75]) {
      samples.push([
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
      ]);
    }
  }
  return samples.every((point) => pointInOrOnBoundary(point, boundaryRing));
}

export interface PlanBoundaryAlignment {
  boundary: SiteZone | null;
  planZones: SiteZone[];
  misalignedZones: SiteZone[];
  /** AI-generated plan zones are meaningful only relative to the boundary
   * that produced them. Hand-drawn buildings/parks/streets do not require a
   * site boundary merely to compile their own persisted footprints. */
  requiresBoundary: boolean;
  isAligned: boolean;
}

/** Detect plan geometry authored against an older site boundary. Framework
 * overlays and hand-drawn zones are excluded; this gate protects paid 3D and
 * render actions for deterministic master-plan proposal zones. */
export function analyzePlanBoundaryAlignment(siteZones: SiteZone[]): PlanBoundaryAlignment {
  const boundary = siteZones.find(
    (zone) => zone.zone_type === 'site_boundary' && zone.coordinates.length >= 3,
  ) ?? null;
  const planZones = siteZones.filter((zone) => {
    const props = zone.properties as Record<string, unknown> | undefined;
    return zone.zone_type !== 'site_boundary'
      && typeof props?._plan_scenario === 'string'
      && props?._plan_role !== 'framework_height';
  });
  const misalignedZones = !boundary
    ? []
    : planZones.filter((zone) => {
      const props = zone.properties as Record<string, unknown> | undefined;
      return props?._plan_boundary_stale === true || !planZoneFitsBoundary(zone, boundary);
    });
  const requiresBoundary = planZones.length > 0;
  return {
    boundary,
    planZones,
    misalignedZones,
    requiresBoundary,
    isAligned: (!requiresBoundary || boundary !== null) && misalignedZones.length === 0,
  };
}
