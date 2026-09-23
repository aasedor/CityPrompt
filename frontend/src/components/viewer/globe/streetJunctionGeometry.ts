import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { collapseStraightStreetStations, extractZoneCenterline, effectiveRoadWidth } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import type { ConnectedStreetIntersection } from './streetGraphIntersections';
import { resolvePilotStreetSectionProfile } from './streetSectionProfiles';
import { getStreetNetworkGroundMeta } from './streetNetworkGroundTexture';
import {
  PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS as ROAD_Z,
  PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS as WALK_Z,
} from './publicRealmDepthPolicy';

export interface JunctionRect { minX: number; maxX: number; minY: number; maxY: number }
export interface JunctionSection { low: number; high: number; raised: boolean; roadZ: number; edgeZ: number }
export interface StreetJunctionLayout {
  bearing: number;
  /** x = u + shear*v, y = v in the A-aligned frame. Widths on B are
   * divided by sin(angle), preserving their physical perpendicular width. */
  shear?: number;
  surfaceZoneId?: string;
  uvFrame?: { bearing: number; u: number; v: number };
  rowA: number;
  rowB: number;
  roadA: number;
  roadB: number;
  sidesB: Array<-1 | 1>;
  bounds: JunctionRect[];
  /** Actual carriageway bounds in node-local y (A) and x (B), including
   * asymmetric sections and reversed source centerlines. */
  sections?: [JunctionSection, JunctionSection];
}

/** A bounded section join with 45–135 degree approaches. Reviewed network atlases retain
 * their existing ground ownership; this helper never silently replaces them. */
export function resolveStreetJunctionLayout(node: ConnectedStreetIntersection, zones: SiteZone[]): StreetJunctionLayout | null {
  if (node.approachSides[0].length !== 2) return null;
  const angleB = node.axisBBearingRad - node.axisABearingRad;
  const sine = Math.abs(Math.sin(angleB));
  if (sine < Math.SQRT1_2 - .001) return null;
  const shear = node.orthogonal ? 0 : Math.cos(angleB) / Math.sin(angleB);
  const connected = zones.filter((zone) => node.zoneIds.includes(zone.id));
  if (connected.length !== node.zoneIds.length || connected.some((zone) => getStreetNetworkGroundMeta(zone))) return null;
  const roads = [0, 0];
  const sections: Array<JunctionSection | undefined> = [undefined, undefined];
  let surfaceZoneId: string | undefined;
  let uvFrame: StreetJunctionLayout['uvFrame'];
  const reaches = [[0, 0], [0, 0]];
  for (const zone of connected) {
    const profile = resolvePilotStreetSectionProfile(zone);
    const route = collapseStraightStreetStations(extractZoneCenterline(zone));
    if (!profile || route.length < 2) return null;
    // Only the segment entering this node owns the join. A bend farther down
    // the route must not disable an otherwise valid junction.
    const distance = (a: number[], b: number[]) => {
      const ax = (a[0] - node.longitude) * metersPerDegLon(node.latitude), ay = (a[1] - node.latitude) * METERS_PER_DEG_LAT;
      const dx = (b[0] - a[0]) * metersPerDegLon(node.latitude), dy = (b[1] - a[1]) * METERS_PER_DEG_LAT;
      const t = Math.max(0, Math.min(1, -(ax * dx + ay * dy) / (dx * dx + dy * dy || 1)));
      return Math.hypot(ax + t * dx, ay + t * dy);
    };
    const line = route.slice(1).map((p, i) => [route[i], p]).sort((a, b) => distance(a[0], a[1]) - distance(b[0], b[1]))[0];
    if (!node.orthogonal && distance(line[0], line[1]) > .25) return null;
    const first = line[0]; const last = line[line.length - 1];
    const angle = Math.atan2((last[1] - first[1]) * METERS_PER_DEG_LAT, (last[0] - first[0]) * metersPerDegLon(node.latitude));
    const axis = Math.abs(Math.cos(angle - node.axisABearingRad)) > 0.9 ? 0 : 1;
    const expected = axis === 0 ? node.axisABearingRad : node.axisBBearingRad;
    if (axis === 0 && surfaceZoneId === undefined) {
      surfaceZoneId = zone.id;
      const dx = (node.longitude - first[0]) * metersPerDegLon(node.latitude);
      const dy = (node.latitude - first[1]) * METERS_PER_DEG_LAT;
      uvFrame = { bearing: angle, u: dx * Math.cos(angle) + dy * Math.sin(angle), v: -dx * Math.sin(angle) + dy * Math.cos(angle) };
    }
    for (let i = 0; i < line.length - 1; i += 1) {
      const a = line[i]; const b = line[i + 1];
      const segmentAngle = Math.atan2((b[1] - a[1]) * METERS_PER_DEG_LAT, (b[0] - a[0]) * metersPerDegLon(node.latitude));
      if (Math.acos(Math.min(1, Math.abs(Math.cos(segmentAngle - expected)))) > Math.PI / 180) return null;
    }
    for (const point of line) {
      const along = (point[0] - node.longitude) * metersPerDegLon(node.latitude) * Math.cos(expected)
        + (point[1] - node.latitude) * METERS_PER_DEG_LAT * Math.sin(expected);
      reaches[axis][along < 0 ? 0 : 1] = Math.max(reaches[axis][along < 0 ? 0 : 1], Math.abs(along));
    }
    if (Math.acos(Math.min(1, Math.abs(Math.cos(angle - expected)))) > Math.PI / 180) return null;
    const scale = (profile.metricWidthLocked ? profile.targetRowM ?? profile.rowM : effectiveRoadWidth(zone.properties)) / profile.rowM;
    const drive = profile.bands.filter((band) => ['motor', 'parking', 'cycle'].includes(band.kind));
    if (!drive.length) return null;
    // The B axis runs across the node; its normal points towards negative X.
    const direction = axis === 0 ? Math.sign(Math.cos(angle - node.axisABearingRad))
      : -Math.sign(Math.sin(angle - node.axisABearingRad));
    const offsets = drive.flatMap((band) => [band.startM * scale * direction / (axis === 1 ? sine : 1), band.endM * scale * direction / (axis === 1 ? sine : 1)]);
    const low = Math.min(...offsets); const high = Math.max(...offsets);
    if (low >= 0 || high <= 0) return null;
    const section = { low, high, raised: profile.renderCurbs, roadZ: drive[0].liftM,
      edgeZ: profile.renderCurbs ? WALK_Z : (profile.bands.find((band) => band.kind === 'shoulder')?.liftM ?? drive[0].liftM) };
    const previous = sections[axis];
    // Opposing fragments must agree; a change in width needs a transition.
    if (previous && (Math.abs(previous.low - low) > 0.05 || Math.abs(previous.high - high) > 0.05
      || previous.raised !== section.raised || previous.roadZ !== section.roadZ)) return null;
    sections[axis] = section;
    roads[axis] = Math.max(Math.abs(low), high);
  }
  const rowA = node.axisAHalfWidthM; const rowB = node.axisBHalfWidthM / sine;
  if (!sections[0] || !sections[1]) return null;
  if (sections.some((section, axis) => section!.raised &&
    (section!.low - 1.8 < -(axis === 0 ? rowA : rowB) || section!.high + 1.8 > (axis === 0 ? rowA : rowB)))) return null;
  if (node.approachSides.some((sides, axis) => sides.some((side) =>
    reaches[axis][side === -1 ? 0 : 1] < (axis === 0 ? rowB + 4 + Math.abs(shear) * rowA : (rowA + 4) / sine + rowB * Math.abs(Math.cos(angleB))) - 0.01))) return null;
  const orientation = Math.sin(node.axisBBearingRad - node.axisABearingRad) >= 0 ? 1 : -1;
  const sidesB = node.approachSides[1].map((side) => side * orientation as -1 | 1);
  return {
    bearing: node.axisABearingRad, shear, surfaceZoneId, uvFrame, rowA, rowB, roadA: roads[0], roadB: roads[1], sidesB,
    sections: sections as [JunctionSection, JunctionSection],
    bounds: [
      { minX: -rowB - 4, maxX: rowB + 4, minY: -rowA, maxY: rowA },
      { minX: -rowB, maxX: rowB, minY: sidesB.includes(-1) ? -rowA - 4 : 0, maxY: sidesB.includes(1) ? rowA + 4 : 0 },
    ],
  };
}

function inside(x: number, y: number, rect: JunctionRect): boolean {
  return x > rect.minX && x < rect.maxX && y > rect.minY && y < rect.maxY;
}

/** Cell decomposition gives non-overlapping pavement and sidewalk, including
 * one continuous sidewalk behind the closed side of a T. No fourth stub. */
export function buildStreetJunctionSurface(layout: StreetJunctionLayout): { pavement: THREE.BufferGeometry; sidewalks: THREE.BufferGeometry; curbs: THREE.BufferGeometry } {
  if (layout.sections) {
    const { pavement, sidewalks, curbs, crosswalks, curbRamps, tactilePads } = buildSectionJunctionGeometry(layout);
    crosswalks.dispose(); curbRamps.dispose(); tactilePads.dispose();
    return { pavement, sidewalks, curbs };
  }
  const { rowA, rowB, roadA, roadB, sidesB, bounds, bearing } = layout;
  const xs = [...new Set([-rowB - 4, -rowB, -roadB, 0, roadB, rowB, rowB + 4])].sort((a, b) => a - b);
  const ys = [...new Set([-rowA - 4, -rowA, -roadA, 0, roadA, rowA, rowA + 4])].sort((a, b) => a - b);
  const positions: number[][] = [[], [], []];
  const roadAt = (x: number, y: number) => Math.abs(y) < roadA || (Math.abs(x) < roadB && (y > 0 ? sidesB.includes(1) : sidesB.includes(-1)));
  const cos = Math.cos(bearing); const sin = Math.sin(bearing);
  for (let i = 0; i < xs.length - 1; i += 1) for (let j = 0; j < ys.length - 1; j += 1) {
    const x = (xs[i] + xs[i + 1]) / 2; const y = (ys[j] + ys[j + 1]) / 2;
    if (!bounds.some((rect) => inside(x, y, rect))) continue;
    const isRoad = roadAt(x, y);
    if (!isRoad) {
      const edges = [
        [xs[i], ys[j], xs[i + 1], ys[j], x, ys[j] - 0.001],
        [xs[i + 1], ys[j], xs[i + 1], ys[j + 1], xs[i + 1] + 0.001, y],
        [xs[i + 1], ys[j + 1], xs[i], ys[j + 1], x, ys[j + 1] + 0.001],
        [xs[i], ys[j + 1], xs[i], ys[j], xs[i] - 0.001, y],
      ];
      for (const [ax, ay, bx, by, probeX, probeY] of edges) {
        if (!bounds.some((rect) => inside(probeX, probeY, rect)) || !roadAt(probeX, probeY)) continue;
        for (const [px, py, pz] of [[ax, ay, ROAD_Z], [bx, by, ROAD_Z], [bx, by, WALK_Z], [ax, ay, ROAD_Z], [bx, by, WALK_Z], [ax, ay, WALK_Z]]) {
          positions[2].push(px * cos - py * sin, px * sin + py * cos, pz);
        }
      }
    }
    const target = positions[isRoad ? 0 : 1]; const z = isRoad ? ROAD_Z : WALK_Z;
    for (const [px, py] of [[xs[i], ys[j]], [xs[i + 1], ys[j]], [xs[i + 1], ys[j + 1]], [xs[i], ys[j]], [xs[i + 1], ys[j + 1]], [xs[i], ys[j + 1]]]) {
      target.push(px * cos - py * sin, px * sin + py * cos, z);
    }
  }
  const geometry = (values: number[]) => {
    const result = new THREE.BufferGeometry();
    result.setAttribute('position', new THREE.Float32BufferAttribute(values, 3));
    const uv: number[] = [];
    const frame = layout.uvFrame ?? { bearing: 0, u: 0, v: 0 };
    for (let i = 0; i < values.length; i += 3) {
      uv.push(values[i] * Math.cos(frame.bearing) + values[i + 1] * Math.sin(frame.bearing) + frame.u,
        -values[i] * Math.sin(frame.bearing) + values[i + 1] * Math.cos(frame.bearing) + frame.v);
    }
    result.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    result.computeVertexNormals(); result.computeBoundingSphere();
    return result;
  };
  const rampOpenings: JunctionRect[] = [];
  for (const side of [-1, 1]) for (const curbSide of [-1, 1]) {
    const center = side * (roadB + 2.9);
    const y0 = curbSide * roadA; const y1 = curbSide * (roadA + 1.8);
    rampOpenings.push({ minX: center - 0.9, maxX: center + 0.9, minY: Math.min(y0, y1) - 0.001, maxY: Math.max(y0, y1) });
  }
  for (const side of sidesB) for (const curbSide of [-1, 1]) {
    const center = side * (roadA + 2.9);
    const x0 = curbSide * roadB; const x1 = curbSide * (roadB + 1.8);
    rampOpenings.push({ minY: center - 0.9, maxY: center + 0.9, minX: Math.min(x0, x1) - 0.001, maxX: Math.max(x0, x1) });
  }
  const withOpenings = (values: number[]) => {
    const source = geometry(values);
    const result = clipStreetGeometryOutsideJunction(source, { ...layout, bounds: rampOpenings });
    source.dispose();
    return result;
  };
  return { pavement: geometry(positions[0]), sidewalks: withOpenings(positions[1]), curbs: withOpenings(positions[2]) };
}

/** One connected surface, crossings and real openings for metric catalogue
 * streets. Flush shared surfaces do not acquire fictitious raised sidewalks. */
export function buildSectionJunctionGeometry(layout: StreetJunctionLayout) {
  const [a, b] = layout.sections!;
  const { rowA, rowB, sidesB, bounds, bearing } = layout;
  const xs = [...new Set([-rowB - 4, -rowB, b.low, 0, b.high, rowB, rowB + 4])].sort((x, y) => x - y);
  const ys = [...new Set([-rowA - 4, -rowA, a.low, 0, a.high, rowA, rowA + 4])].sort((x, y) => x - y);
  const data = { pavement: [] as number[], sidewalks: [] as number[], curbs: [] as number[],
    crosswalks: [] as number[], curbRamps: [] as number[], tactilePads: [] as number[] };
  const inBounds = (x: number, y: number) => bounds.some((r) => inside(x, y, r));
  const roadAt = (x: number, y: number) => (y > a.low && y < a.high)
    || (x > b.low && x < b.high && sidesB.includes(y > 0 ? 1 : -1));
  const blendB = (y: number) => Math.min(1, Math.max(0, y > a.high ? (y - a.high) / (rowA + 4 - a.high)
    : y < a.low ? (a.low - y) / (rowA + 4 + a.low) : 0));
  const roadZ = (_x: number, y: number) => a.roadZ + (b.roadZ - a.roadZ) * blendB(y);
  const walkZ = (_x: number, y: number) => {
    const t = Math.min(1, Math.max(0, (Math.abs(y) - rowA) / 4));
    return a.edgeZ + (b.edgeZ - a.edgeZ) * t;
  };
  const cos = Math.cos(bearing); const sin = Math.sin(bearing);
  const quad = (target: number[], points: number[][]) => {
    // All horizontal/sloped tops face up, independently of approach direction.
    const cross = (points[1][0] - points[0][0]) * (points[2][1] - points[0][1])
      - (points[1][1] - points[0][1]) * (points[2][0] - points[0][0]);
    const order = cross < 0 ? [0, 2, 1, 0, 3, 2] : [0, 1, 2, 0, 2, 3];
    for (const i of order) {
      const [u, y, z] = points[i], x = u + (layout.shear ?? 0) * y;
      target.push(x * cos - y * sin, x * sin + y * cos, z);
    }
  };
  const rectangle = (target: number[], x0: number, y0: number, x1: number, y1: number, z: (x: number, y: number) => number) =>
    quad(target, [[x0, y0, z(x0, y0)], [x1, y0, z(x1, y0)], [x1, y1, z(x1, y1)], [x0, y1, z(x0, y1)]]);
  for (let i = 0; i < xs.length - 1; i++) for (let j = 0; j < ys.length - 1; j++) {
    const x = (xs[i] + xs[i + 1]) / 2; const y = (ys[j] + ys[j + 1]) / 2;
    if (!inBounds(x, y)) continue;
    const road = roadAt(x, y);
    rectangle(road ? data.pavement : data.sidewalks, xs[i], ys[j], xs[i + 1], ys[j + 1], road ? roadZ : walkZ);
    if (road) continue;
    const edges = [[xs[i], ys[j], xs[i + 1], ys[j], x, ys[j] - 0.001],
      [xs[i + 1], ys[j], xs[i + 1], ys[j + 1], xs[i + 1] + 0.001, y],
      [xs[i + 1], ys[j + 1], xs[i], ys[j + 1], x, ys[j + 1] + 0.001],
      [xs[i], ys[j + 1], xs[i], ys[j], xs[i] - 0.001, y]];
    for (const [x0, y0, x1, y1, px, py] of edges) {
      if (!inBounds(px, py) || !roadAt(px, py)) continue;
      quad(data.curbs, [[x0, y0, roadZ(x0, y0)], [x1, y1, roadZ(x1, y1)],
        [x1, y1, walkZ(x1, y1)], [x0, y0, walkZ(x0, y0)]]);
    }
  }
  const openings: JunctionRect[] = [];
  for (const axis of [0, 1]) for (const side of axis === 0 ? [-1, 1] : sidesB) {
    const cross = axis === 0 ? b : a; const section = axis === 0 ? a : b;
    const center = (side < 0 ? cross.low : cross.high) + side * 2.9;
    const point = (along: number, across: number) => axis === 0 ? [along, across] : [across, along];
    for (let stripe = -3; stripe <= 3; stripe++) {
      const lo = center + stripe * 0.43 - 0.15; const hi = lo + 0.3;
      const p = [point(lo, section.low), point(hi, section.low), point(hi, section.high), point(lo, section.high)];
      quad(data.crosswalks, p.map(([x, y]) => [x, y, roadZ(x, y) + 0.006]));
    }
    for (const curbSide of [-1, 1]) {
      const edge = curbSide < 0 ? section.low : section.high;
      const back = edge + curbSide * 1.8;
      const p = [point(center - 0.9, edge), point(center + 0.9, edge), point(center + 0.9, back), point(center - 0.9, back)];
      // Ramps are only needed at a real raised edge and must fit the owned ROW.
      const [mx, my] = point(center, edge); const [bx, by] = point(center, back);
      if (walkZ(bx, by) - roadZ(mx, my) < 0.05
        || p.slice(2).some(([x, y]) => !inBounds(x, y) || roadAt(x, y))) continue;
      openings.push({ minX: Math.min(...p.map(v => v[0])) - 0.001, maxX: Math.max(...p.map(v => v[0])) + 0.001,
        minY: Math.min(...p.map(v => v[1])) - 0.001, maxY: Math.max(...p.map(v => v[1])) + 0.001 });
      quad(data.curbRamps, p.map(([x, y], index) => [x, y, index < 2 ? roadZ(x, y) : walkZ(x, y)]));
      // Side cheeks close the cut sidewalk, without a vertical lip at the toe.
      for (const index of [0, 1]) {
        const [x0, y0] = p[index]; const [x1, y1] = p[index === 0 ? 3 : 2];
        quad(data.curbRamps, [[x0, y0, roadZ(x0, y0)], [x1, y1, walkZ(x1, y1)],
          [x1, y1, walkZ(x1, y1)], [x0, y0, walkZ(x0, y0)]]);
      }
      // Detectable warning follows the ramp slope instead of floating above it.
      const pad = [point(center - 0.62, edge + curbSide * 0.12), point(center + 0.62, edge + curbSide * 0.12),
        point(center + 0.62, edge + curbSide * 0.66), point(center - 0.62, edge + curbSide * 0.66)];
      quad(data.tactilePads, pad.map(([x, y]) => {
        const t = Math.abs((axis === 0 ? y : x) - edge) / 1.8;
        const [tx, ty] = point(axis === 0 ? x : y, edge); const [ux, uy] = point(axis === 0 ? x : y, back);
        return [x, y, roadZ(tx, ty) * (1 - t) + walkZ(ux, uy) * t + 0.006];
      }));
    }
  }
  const make = (values: number[]) => {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(values, 3));
    const uv: number[] = []; const frame = layout.uvFrame ?? { bearing: 0, u: 0, v: 0 };
    for (let i = 0; i < values.length; i += 3) uv.push(values[i] * Math.cos(frame.bearing) + values[i + 1] * Math.sin(frame.bearing) + frame.u,
      -values[i] * Math.sin(frame.bearing) + values[i + 1] * Math.cos(frame.bearing) + frame.v);
    geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    geometry.computeVertexNormals(); geometry.computeBoundingSphere(); return geometry;
  };
  const result = Object.fromEntries(Object.entries(data).map(([key, values]) => [key, make(values)])) as Record<keyof typeof data, THREE.BufferGeometry>;
  for (const key of ['sidewalks', 'curbs'] as const) {
    const source = result[key]; result[key] = clipStreetGeometryOutsideJunction(source, { ...layout, bounds: openings }); source.dispose();
  }
  return result;
}

export function streetJunctionContainsPoint(layout: StreetJunctionLayout, x: number, y: number, padding = 0): boolean {
  const localY = -x * Math.sin(layout.bearing) + y * Math.cos(layout.bearing);
  const localX = x * Math.cos(layout.bearing) + y * Math.sin(layout.bearing) - (layout.shear ?? 0) * localY;
  return layout.bounds.some(rect => localX >= rect.minX - padding && localX <= rect.maxX + padding
    && localY >= rect.minY - padding && localY <= rect.maxY + padding);
}

type Vertex = Record<string, number[]>;
/** Exact triangle clipping, including vertical curb faces. Interpolates all
 * attributes and leaves its source unmodified. Unlike station deletion this
 * cannot erase a long adjacent street or leave a band through the junction. */
export function clipStreetGeometryOutsideJunction(
  source: THREE.BufferGeometry, layout: StreetJunctionLayout, centerX = 0, centerY = 0,
): THREE.BufferGeometry {
  const names = Object.keys(source.attributes);
  const cos = Math.cos(layout.bearing); const sin = Math.sin(layout.bearing);
  const coordinate = (vertex: Vertex, axis: number) => {
    const x = vertex.position[0] - centerX; const y = vertex.position[1] - centerY;
    const v = -x * sin + y * cos;
    return axis === 0 ? x * cos + y * sin - (layout.shear ?? 0) * v : v;
  };
  const clip = (polygon: Vertex[], axis: number, edge: number, sign: number): Vertex[] => {
    const output: Vertex[] = [];
    for (let i = 0; i < polygon.length; i += 1) {
      const a = polygon[i]; const b = polygon[(i + 1) % polygon.length];
      const da = (coordinate(a, axis) - edge) * sign; const db = (coordinate(b, axis) - edge) * sign;
      if (da >= 0) output.push(a);
      if ((da >= 0) !== (db >= 0)) {
        const t = da / (da - db);
        output.push(Object.fromEntries(names.map((name) => [name, a[name].map((v, k) => v + (b[name][k] - v) * t)])));
      }
    }
    return output;
  };
  const index = source.getIndex(); const count = index?.count ?? source.getAttribute('position').count;
  let polygons: Vertex[][] = [];
  for (let i = 0; i < count; i += 3) polygons.push([0, 1, 2].map((offset) => {
    const vertexIndex = index ? index.getX(i + offset) : i + offset;
    return Object.fromEntries(names.map((name) => {
      const attribute = source.getAttribute(name);
      return [name, Array.from({ length: attribute.itemSize }, (_, k) => attribute.getComponent(vertexIndex, k))];
    }));
  }));
  for (const rect of layout.bounds) {
    const outside: Vertex[][] = [];
    for (const polygon of polygons) {
      let remainder = polygon;
      for (const [axis, edge, sign] of [[0, rect.minX, 1], [0, rect.maxX, -1], [1, rect.minY, 1], [1, rect.maxY, -1]]) {
        const piece = clip(remainder, axis, edge, -sign);
        if (piece.length >= 3) outside.push(piece);
        remainder = clip(remainder, axis, edge, sign);
        if (remainder.length < 3) break;
      }
    }
    polygons = outside;
  }
  const output: Record<string, number[]> = Object.fromEntries(names.map((name) => [name, []]));
  for (const polygon of polygons) for (let i = 1; i < polygon.length - 1; i += 1) {
    for (const vertex of [polygon[0], polygon[i], polygon[i + 1]]) for (const name of names) output[name].push(...vertex[name]);
  }
  const result = new THREE.BufferGeometry();
  for (const name of names) result.setAttribute(name, new THREE.Float32BufferAttribute(output[name], source.getAttribute(name).itemSize));
  result.computeBoundingSphere();
  return result;
}
