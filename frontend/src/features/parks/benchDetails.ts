import type { SiteZone, SiteZoneProperties } from '@/types';
import {
  metersPerDegLon,
  METERS_PER_DEG_LAT,
} from '@/components/viewer/mapEngine/geoUtils';
import {
  neighborhoodParkLayoutForZone,
  envelopeFits,
  envelopesOverlap,
  distanceToSegment,
  pointInPark,
  type NeighborhoodParkLayout,
  type ParkPoint,
} from '@/components/viewer/globe/neighborhoodParkLayout';
import { getDerivedParkAccess } from '@/components/viewer/globe/parkAccessConnections';
import { parkOutlineDimensions } from '@/features/pickPlace/parkOutline';

export const MAX_DETAIL_BENCHES = 32;
export interface DetailBench {
  id: string;
  point: ParkPoint;
  yaw: number;
}
export interface SavedBenchDetails {
  version: 1;
  items: Array<{ id: string; u: number; v: number; angle: number }>;
}

export function readBenchDetails(
  properties?: SiteZoneProperties,
): SavedBenchDetails | null {
  const value = properties?.bench_details as SavedBenchDetails | undefined;
  if (
    !value ||
    value.version !== 1 ||
    !Array.isArray(value.items) ||
    value.items.length > MAX_DETAIL_BENCHES
  )
    return null;
  if (
    value.items.some(
      (p) =>
        !p ||
        typeof p.id !== 'string' ||
        !/^[\w-]{1,80}$/.test(p.id) ||
        ![p.u, p.v, p.angle].every(Number.isFinite) ||
        Math.abs(p.u) > 2 ||
        Math.abs(p.v) > 2 ||
        Math.abs(p.angle) > Math.PI * 4,
    )
  )
    return null;
  if (new Set(value.items.map((p) => p.id)).size !== value.items.length)
    return null;
  return value;
}

/** The renderer and editor share these exact original placements. */
export function automaticRusticDetails(layout: NeighborhoodParkLayout) {
  if (!layout.loop.length) return [];
  const center = layout.loop.reduce(
    (a, p) => ({
      x: a.x + p.x / layout.loop.length,
      y: a.y + p.y / layout.loop.length,
    }),
    { x: 0, y: 0 },
  );
  return [7, 21, 38, 52].flatMap((index, i) => {
    const q = layout.loop[index],
      dx = q.x - center.x,
      dy = q.y - center.y,
      d = Math.hypot(dx, dy) || 1,
      offset = i === 2 ? 4 : 2.8;
    const p = { x: q.x + (dx / d) * offset, y: q.y + (dy / d) * offset },
      radius = i === 2 ? 3 : 1.6;
    const envelope = [
      { x: p.x - radius, y: p.y - radius },
      { x: p.x + radius, y: p.y - radius },
      { x: p.x + radius, y: p.y + radius },
      { x: p.x - radius, y: p.y + radius },
    ];
    if (
      !envelopeFits(envelope, layout.boundary, 0.2) ||
      layout.modules.some((m) =>
        envelope.some((v) => pointInPark(v, m.envelope)),
      )
    )
      return [];
    return [
      {
        id: `auto-${index}`,
        asset: i === 2 ? ('boulders' as const) : ('timber-bench' as const),
        point: p,
        yaw: Math.atan2(dy, dx) - Math.PI / 2,
      },
    ];
  });
}

export function benchContext(
  zone: SiteZone,
  origin = { lng: zone.coordinates[0][0], lat: zone.coordinates[0][1] },
  scope: 'park' | 'project' = 'park',
) {
  const frame = parkOutlineDimensions(zone.coordinates);
  const east = metersPerDegLon(origin.lat),
    angle = (frame.degrees * Math.PI) / 180,
    c = Math.cos(angle),
    s = Math.sin(angle);
  const fromWorld = ([lng, lat]: number[]): ParkPoint => ({
    x: (lng - origin.lng) * east,
    y: (lat - origin.lat) * METERS_PER_DEG_LAT,
  });
  const toWorld = (p: ParkPoint) => [
    origin.lng + p.x / east,
    origin.lat + p.y / METERS_PER_DEG_LAT,
  ];
  const layout: NeighborhoodParkLayout =
    scope === 'park'
      ? neighborhoodParkLayoutForZone(zone, origin)
      : {
          status: 'constrained',
          boundary: zone.coordinates.map(fromWorld),
          lawn: [],
          loop: [],
          paths: [],
          modules: [],
          trees: [],
          shrubs: [],
          pathWidth: 2.6,
          notes: [],
        };
  const center = fromWorld(frame.center),
    eastRatio = east / metersPerDegLon(zone.coordinates[0][1]);
  const toFrame = (p: ParkPoint) => ({
    u:
      0.5 +
      (((p.x - center.x) / eastRatio) * c + (p.y - center.y) * s) / frame.width,
    v:
      0.5 +
      ((-(p.x - center.x) / eastRatio) * s + (p.y - center.y) * c) /
        frame.depth,
  });
  const fromFrame = (u: number, v: number) => ({
    x:
      center.x +
      ((u - 0.5) * frame.width * c - (v - 0.5) * frame.depth * s) * eastRatio,
    y: center.y + (u - 0.5) * frame.width * s + (v - 0.5) * frame.depth * c,
  });
  const entryPaths = (getDerivedParkAccess(zone)?.paths ?? []).map((path) => ({
    points: path.points.map(fromWorld),
    widthM: 2.2,
  }));
  const terraces = (zone.properties?.terrace_access_clearances ?? []) as Array<{
    points: number[][];
    widthM: number;
  }>;
  const accessPaths = [
    ...entryPaths,
    ...terraces.map((path) => ({
      points: path.points.map(fromWorld),
      widthM: path.widthM,
    })),
  ];
  const clearOfEntrances = (p: ParkPoint, clearance: number) =>
    accessPaths.every((path) =>
      path.points.every(
        (q, i) =>
          i === 0 ||
          distanceToSegment(p, path.points[i - 1], q) >
            Math.max(clearance, path.widthM / 2 + 0.5),
      ),
    );
  return {
    scope,
    layout,
    frame,
    angle,
    toWorld,
    fromWorld,
    toFrame,
    fromFrame,
    accessPaths,
    clearOfEntrances,
  };
}
export type BenchContext = ReturnType<typeof benchContext>;

export function resolveBenches(
  zone: SiteZone,
  context: BenchContext,
): DetailBench[] {
  const saved = readBenchDetails(zone.properties);
  return saved
    ? saved.items.map((p) => ({
        id: p.id,
        point: context.fromFrame(p.u, p.v),
        yaw: p.angle + context.angle,
      }))
    : automaticRusticDetails(context.layout).filter(
        (p) =>
          p.asset === 'timber-bench' && context.clearOfEntrances(p.point, 3),
      );
}
export function saveBenchDetails(
  zone: SiteZone,
  benches: DetailBench[],
  context: BenchContext,
): SiteZoneProperties {
  const round = (n: number) => Math.round(n * 1e8) / 1e8;
  const value: SavedBenchDetails = {
    version: 1,
    items: benches.map((p) => {
      const q = context.toFrame(p.point);
      return {
        id: p.id,
        u: round(q.u),
        v: round(q.v),
        angle: round(
          Math.atan2(
            Math.sin(p.yaw - context.angle),
            Math.cos(p.yaw - context.angle),
          ),
        ),
      };
    }),
  };
  return { ...zone.properties, bench_details: value };
}

export function benchFootprint(
  bench: DetailBench,
  clearance = 0.1,
): ParkPoint[] {
  const c = Math.cos(bench.yaw),
    s = Math.sin(bench.yaw);
  return [
    [-1, -1],
    [1, -1],
    [1, 1],
    [-1, 1],
  ].map(([x, y]) => ({
    x: bench.point.x + x * (0.95 + clearance) * c - y * (0.293 + clearance) * s,
    y: bench.point.y + x * (0.95 + clearance) * s + y * (0.293 + clearance) * c,
  }));
}

/** Authored furniture takes priority over regenerating automatic planting. */
export function plantingClearOfBenches(
  points: ParkPoint[],
  benches: DetailBench[],
): ParkPoint[] {
  return points.filter((point) =>
    benches.every(
      (bench) =>
        Math.hypot(point.x - bench.point.x, point.y - bench.point.y) >= 1.5,
    ),
  );
}

export function benchPlacementProblem(
  bench: DetailBench,
  others: DetailBench[],
  context: BenchContext,
): string | null {
  const footprint = benchFootprint(bench);
  if (
    context.scope === 'park' &&
    !envelopeFits(footprint, context.layout.boundary, 0.05)
  )
    return 'Keep the whole bench inside the park.';
  if (
    others.some(
      (p) =>
        p.id !== bench.id && envelopesOverlap(footprint, benchFootprint(p)),
    )
  )
    return 'Leave a little space between benches.';
  if (
    context.layout.modules.some((m) => envelopesOverlap(footprint, m.envelope))
  )
    return 'Place the bench outside the play equipment and pavilion space.';
  const paths = [
    {
      points: [...context.layout.loop, context.layout.loop[0]].filter(Boolean),
      widthM: context.layout.pathWidth,
    },
    ...context.layout.paths.map((points) => ({
      points,
      widthM: context.layout.pathWidth,
    })),
    ...context.accessPaths,
  ];
  if (
    paths.some((path) =>
      path.points.some(
        (p, i) =>
          i > 0 &&
          distanceToSegment(bench.point, path.points[i - 1], p) <
            path.widthM / 2 + 1.1,
      ),
    )
  )
    return 'Keep the walking paths clear; place the bench beside the path.';
  return null;
}
