import type { SiteZone } from "@/types";
import type { ParkGroundGuide } from "./parkGroundProfiles";
import {
  distanceToSegment,
  envelopeFits,
  envelopesOverlap,
  type ParkPoint,
} from "./neighborhoodParkLayout";
import { METERS_PER_DEG_LAT, metersPerDegLon } from "../mapEngine/geoUtils";

export const PARK_TRIO_REVISION = "park-trio-v3";
export const PARK_TRIO = {
  cinema: {
    parent: "outdoor_cinema_lawn",
    variant: "outdoor_cinema_lawn_v1",
    label: "Outdoor cinema lawn",
    min: [32, 45],
    size: [50, 75],
    image: "/archetypes/openspaces/outdoor-cinema-lawn/variant_1.png",
  },
  garden: {
    parent: "research_garden_teaching_arboretum",
    variant: "research_garden_teaching_arboretum_variant_3",
    label: "Teaching demonstration garden",
    min: [32, 40],
    size: [42, 50],
    image:
      "/archetypes/openspaces/research-garden-teaching-arboretum/variant_3.png",
  },
  concert: {
    parent: "concert_pavilion_lawn",
    variant: "concert_pavilion_lawn_v1",
    label: "Wave-canopy concert lawn",
    min: [80, 80],
    size: [90, 110],
    image: "/archetypes/openspaces/concert-pavilion-lawn/variant_1.png",
  },
} as const;
export type ParkTrioKind = keyof typeof PARK_TRIO;
export interface TrioModule {
  id: string;
  asset: string;
  center: ParkPoint;
  yaw: number;
  width: number;
  depth: number;
  envelope: ParkPoint[];
}
export interface TrioPath {
  points: ParkPoint[];
  width: number;
  closed: boolean;
}
export interface TrioLayout {
  kind: ParkTrioKind;
  boundary: ParkPoint[];
  paths: TrioPath[];
  courtyard?: ParkPoint[];
  modules: TrioModule[];
  trees: ParkPoint[];
  notes: string[];
  status: "full" | "compact" | "constrained";
  center: ParkPoint;
  angle: number;
  width: number;
  depth: number;
}
type Zone = Pick<SiteZone, "properties"> &
  Partial<Pick<SiteZone, "zone_type" | "coordinates">>;
export function parkTrioKind(zone: Zone): ParkTrioKind | null {
  if (
    zone.zone_type !== "green_space" ||
    zone.properties?.park_trio_layout !== PARK_TRIO_REVISION
  )
    return null;
  return (
    (Object.keys(PARK_TRIO) as ParkTrioKind[]).find(
      (kind) =>
        zone.properties?.green_space_archetype_id === PARK_TRIO[kind].parent &&
        zone.properties?.green_space_selected_variant_id ===
          PARK_TRIO[kind].variant,
    ) ?? null
  );
}
export const isParkTrio = (zone: Zone): boolean => parkTrioKind(zone) !== null;
export const rect = (
  x: number,
  y: number,
  w: number,
  d: number,
): ParkPoint[] => [
  { x: x - w / 2, y: y - d / 2 },
  { x: x + w / 2, y: y - d / 2 },
  { x: x + w / 2, y: y + d / 2 },
  { x: x - w / 2, y: y + d / 2 },
];
const rotate = (p: ParkPoint, a: number): ParkPoint => ({
  x: p.x * Math.cos(a) - p.y * Math.sin(a),
  y: p.x * Math.sin(a) + p.y * Math.cos(a),
});

/** Bounded, deterministic planning grammar. Whole objects retain metric scale. */
export function buildParkTrio(
  kind: ParkTrioKind,
  input: readonly ParkPoint[],
): TrioLayout {
  const empty: TrioLayout = {
    kind,
    boundary: [...input],
    paths: [],
    modules: [],
    trees: [],
    notes: [],
    status: "constrained",
    center: { x: 0, y: 0 },
    angle: 0,
    width: 0,
    depth: 0,
  };
  if (
    input.length < 3 ||
    input.length > 128 ||
    input.some((p) => !Number.isFinite(p.x + p.y))
  )
    return { ...empty, notes: ["A finite, simple park boundary is required."] };
  const center = {
    x: input.reduce((s, p) => s + p.x, 0) / input.length,
    y: input.reduce((s, p) => s + p.y, 0) / input.length,
  };
  const angle = Math.atan2(input[1].y - input[0].y, input[1].x - input[0].x);
  const local = input.map((p) =>
    rotate({ x: p.x - center.x, y: p.y - center.y }, -angle),
  );
  const minX = Math.min(...local.map((p) => p.x)),
    maxX = Math.max(...local.map((p) => p.x)),
    minY = Math.min(...local.map((p) => p.y)),
    maxY = Math.max(...local.map((p) => p.y));
  const width = maxX - minX,
    depth = maxY - minY,
    cx = (minX + maxX) / 2,
    cy = (minY + maxY) / 2;
  const toWorld = (p: ParkPoint) => {
    const q = rotate(p, angle);
    return { x: q.x + center.x, y: q.y + center.y };
  };
  const layout = {
    ...empty,
    center: toWorld({ x: cx, y: cy }),
    angle,
    width,
    depth,
  };
  if (
    width < PARK_TRIO[kind].min[0] - 0.01 ||
    depth < PARK_TRIO[kind].min[1] - 0.01 ||
    width > 240 ||
    depth > 240
  )
    return {
      ...layout,
      notes: [
        `Use at least ${PARK_TRIO[kind].min.join(" × ")} m of usable park area. Objects are not squeezed to fit.`,
      ],
    };
  const modules: TrioModule[] = [],
    paths: TrioPath[] = [];
  const add = (
    id: string,
    asset: string,
    x: number,
    y: number,
    w: number,
    d: number,
    yaw = 0,
  ) => {
    const c = { x: cx + x, y: cy + y };
    const envelope = rect(0, 0, w, d).map((p) => {
      const q = rotate(p, yaw);
      return { x: q.x + c.x, y: q.y + c.y };
    });
    if (
      !envelopeFits(envelope, local, 0.4) ||
      modules.some((m) => envelopesOverlap(envelope, m.envelope))
    )
      return false;
    modules.push({ id, asset, center: c, yaw, width: w, depth: d, envelope });
    return true;
  };
  const route = (points: ParkPoint[], w = 2.4, closed = false) => {
    // Prove each complete path corridor, including segment endpoints.
    for (let i = 0; i < points.length - (closed ? 0 : 1); i++) {
      const a = points[i],
        b = points[(i + 1) % points.length],
        len = Math.hypot(b.x - a.x, b.y - a.y);
      if (len < 0.01) continue;
      const nx = ((-(b.y - a.y) / len) * w) / 2,
        ny = (((b.x - a.x) / len) * w) / 2;
      if (
        !envelopeFits(
          [
            { x: a.x + nx, y: a.y + ny },
            { x: b.x + nx, y: b.y + ny },
            { x: b.x - nx, y: b.y - ny },
            { x: a.x - nx, y: a.y - ny },
          ],
          local,
          0.05,
        )
      )
        return false;
    }
    paths.push({ points, width: w, closed });
    return true;
  };
  // A rounded rectangular circulation loop leaves a continuous planted border.
  const rx = width / 2 - 6,
    ry = depth / 2 - 6,
    r = Math.min(5, rx / 3, ry / 3),
    loop: ParkPoint[] = [];
  for (let corner = 0; corner < 4; corner++)
    for (let i = 0; i < 9; i++) {
      const a = (corner * Math.PI) / 2 + (i * Math.PI) / 16;
      const ox = corner === 0 || corner === 3 ? rx - r : -rx + r,
        oy = corner < 2 ? ry - r : -ry + r;
      loop.push({ x: cx + ox + Math.cos(a) * r, y: cy + oy + Math.sin(a) * r });
    }
  if (!route(loop, kind === "concert" ? 3 : 2.4, true))
    return {
      ...layout,
      notes: [
        "The complete connected programme does not fit this concave shape. Use a wider simple plot; no cropped structures were added.",
      ],
    };
  if (kind === "cinema") {
    if (!add("screen", "cinema/screen", -2, ry - 5, 12, 4))
      return {
        ...layout,
        notes: ["The complete screen and its supports need more room."],
      };
    if (width >= 38) add("booth", "cinema/booth", 9, ry - 5, 4, 4.4);
    // Bench rows stay outside the centre sightline; the lawn remains open.
    for (let row = 0; row < Math.min(4, Math.floor((depth - 25) / 8)); row++)
      for (const side of [-1, 1])
        add(
          `bench-${row}-${side}`,
          "shared/bench",
          side * 7,
          ry - 12 - row * 5,
          2.3,
          1.4,
          Math.PI,
        );
  } else if (kind === "garden") {
    if (!add("shelter", "garden/shelter", 0, ry - 6, 7.3, 8.2))
      return { ...layout, notes: ["The whole teaching shelter does not fit."] };
    const rows = Math.min(4, Math.max(2, Math.floor((2 * ry - 18.4) / 5) + 1));
    for (let row = 0; row < rows; row++)
      for (const col of [-1, 0, 1]) {
        add(
          `bed-${row}-${col}`,
          "garden/bed",
          col * 5.2,
          -ry + 6 + row * 5,
          3.1,
          2,
        );
        add(
          `label-${row}-${col}`,
          "garden/label",
          col * 5.2 + 2.1,
          -ry + 6 + row * 5,
          0.85,
          0.7,
        );
      }
    route(
      [
        { x: cx - rx, y: cy + ry - 10 },
        { x: cx, y: cy + ry - 10 },
        { x: cx + rx, y: cy + ry - 10 },
      ],
      2.2,
    );
    for (const side of [-1, 1])
      route(
        [
          { x: cx + side * 10, y: cy - ry },
          { x: cx + side * 10, y: cy + ry - 10 },
        ],
        2.2,
      );
    for (const side of [-1, 1])
      add(
        `bench-${side}`,
        "shared/bench",
        side * 10,
        ry - 3,
        2.3,
        1.4,
        (side * Math.PI) / 2,
      );
  } else {
    // Offset the native asymmetric stage envelope so its side ramp fits too.
    if (!add("stage", "concert/stage", 4, ry - 14, 53, 22))
      return {
        ...layout,
        notes: [
          "The wave canopy, columns and complete side ramp need a wider site.",
        ],
      };
    for (let row = 0; row < 4; row++)
      for (const col of [-2, -1, 1, 2])
        add(
          `seats-${row}-${col}`,
          "concert/seats",
          col * 4.6,
          ry - 28 - row * 1.6,
          4,
          0.95,
          Math.PI,
        );
    for (const side of [-1, 1])
      route(
        [
          { x: cx + side * rx, y: cy - ry },
          { x: cx + side * 15, y: cy + ry - 23 },
        ],
        2.6,
      );
    for (let i = 0; i < 3; i++) {
      const y = -ry + 9 + i * Math.max(7, (depth - 55) / 3);
      const aisleX = rx + ((15 - rx) * (y + ry)) / (2 * ry - 23);
      route(
        [
          { x: cx - aisleX, y: cy + y },
          { x: cx, y: cy + y + 3 },
          { x: cx + aisleX, y: cy + y },
        ],
        1.5,
      );
    }
  }
  // One path system owns all routes. Remove a failed optional route rather than clip it.
  const trees: ParkPoint[] = [];
  const candidates: ParkPoint[] = [];
  const nx = Math.max(1, Math.floor((width - 7.6) / 8)),
    ny = Math.max(1, Math.floor((depth - 7.6) / 8));
  for (let i = 0; i <= nx; i++)
    for (const y of [minY + 3.8, maxY - 3.8])
      candidates.push({ x: minX + 3.8 + ((width - 7.6) * i) / nx, y });
  for (let i = 1; i < ny; i++)
    for (const x of [minX + 3.8, maxX - 3.8])
      candidates.push({ x, y: minY + 3.8 + ((depth - 7.6) * i) / ny });
  for (const p of candidates) {
    if (
      !envelopeFits(rect(p.x, p.y, 6.6, 6.6), local, 0.05) ||
      modules.some((m) =>
        envelopesOverlap(rect(p.x, p.y, 6.6, 6.6), m.envelope),
      ) ||
      paths.some((path) =>
        path.points.some(
          (q, i) =>
            i < path.points.length - 1 &&
            distanceToSegment(p, q, path.points[i + 1]) < path.width / 2 + 0.55,
        ),
      )
    )
      continue;
    if (trees.length < 48) trees.push(p);
  }
  if (kind === "garden")
    layout.courtyard = rect(cx, cy - 5, 18, 2 * ry - 10).map(toWorld);
  layout.modules = modules.map((m) => ({
    ...m,
    center: toWorld(m.center),
    yaw: m.yaw + angle,
    envelope: m.envelope.map(toWorld),
  }));
  layout.paths = paths.map((p) => ({ ...p, points: p.points.map(toWorld) }));
  layout.trees = trees.map(toWorld);
  layout.status =
    width < PARK_TRIO[kind].size[0] - 0.01 ||
    depth < PARK_TRIO[kind].size[1] - 0.01
      ? "compact"
      : "full";
  const counts = Object.entries(
    modules.reduce<Record<string, number>>((a, m) => {
      const key = m.asset.split("/")[1];
      a[key] = (a[key] ?? 0) + 1;
      return a;
    }, {}),
  )
    .map(([name, count]) => `${count} ${name}`)
    .join(", ");
  layout.notes = [
    `${counts}; ${trees.length} perimeter trees. Structures retain native dimensions.`,
    "Lawn and circulation follow site terrain. Confirm structure pads and access in detailed design.",
  ];
  return layout;
}

const cache = new Map<string, TrioLayout>();
export function parkTrioLayout(
  zone: Zone,
  centroid: { lng: number; lat: number },
): TrioLayout {
  const kind = parkTrioKind(zone) ?? "cinema";
  const key = JSON.stringify([kind, centroid, zone.coordinates]);
  const found = cache.get(key);
  if (found) return found;
  const result = buildParkTrio(
    kind,
    (zone.coordinates ?? []).map(([lng, lat]) => ({
      x: (lng - centroid.lng) * metersPerDegLon(centroid.lat),
      y: (lat - centroid.lat) * METERS_PER_DEG_LAT,
    })),
  );
  if (cache.size >= 64) cache.delete(cache.keys().next().value!);
  cache.set(key, result);
  return result;
}

export function parkTrioGuides(zone: Zone): ParkGroundGuide[] {
  if (!zone.coordinates?.length) return [];
  const layout = parkTrioLayout(zone, {
    lng: zone.coordinates[0][0],
    lat: zone.coordinates[0][1],
  });
  const minX = Math.min(...layout.boundary.map((p) => p.x)),
    maxX = Math.max(...layout.boundary.map((p) => p.x)),
    minY = Math.min(...layout.boundary.map((p) => p.y)),
    maxY = Math.max(...layout.boundary.map((p) => p.y)),
    w = maxX - minX,
    d = maxY - minY;
  if (w <= 0 || d <= 0) return [];
  return [
    ...layout.paths.map((path) => ({
      kind: "polyline" as const,
      x: 0.5,
      y: 0.5,
      width: 1,
      height: 1,
      color: "#b8ad92",
      strokeWidthM: path.width,
      closed: path.closed,
      points: path.points.map(
        (p) => [(p.x - minX) / w, (maxY - p.y) / d] as [number, number],
      ),
    })),
    ...layout.modules.map((m) => ({
      kind: "rectangle" as const,
      x: (m.center.x - minX) / w,
      y: (maxY - m.center.y) / d,
      width: m.width / w,
      height: m.depth / d,
      color: "#aaa08b",
      rotationDeg: (-m.yaw * 180) / Math.PI,
      fitPolicy: "clip" as const,
    })),
  ];
}
