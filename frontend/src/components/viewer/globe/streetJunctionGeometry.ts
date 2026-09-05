import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { extractZoneCenterline, effectiveRoadWidth } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import type { ConnectedStreetIntersection } from './streetGraphIntersections';
import { resolvePilotStreetSectionProfile } from './streetSectionProfiles';
import { getStreetNetworkGroundMeta } from './streetNetworkGroundTexture';
import {
  PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS as ROAD_Z,
  PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS as WALK_Z,
} from './publicRealmDepthPolicy';

export interface JunctionRect { minX: number; maxX: number; minY: number; maxY: number }
export interface StreetJunctionLayout {
  bearing: number;
  surfaceZoneId?: string;
  uvFrame?: { bearing: number; u: number; v: number };
  rowA: number;
  rowB: number;
  roadA: number;
  roadB: number;
  sidesB: Array<-1 | 1>;
  bounds: JunctionRect[];
}

/** A bounded, symmetric orthogonal section join. Reviewed network atlases retain
 * their existing ground ownership; this helper never silently replaces them. */
export function resolveStreetJunctionLayout(node: ConnectedStreetIntersection, zones: SiteZone[]): StreetJunctionLayout | null {
  if (!node.orthogonal || node.approachSides[0].length !== 2) return null;
  const connected = zones.filter((zone) => node.zoneIds.includes(zone.id));
  if (connected.length !== node.zoneIds.length || connected.some((zone) => getStreetNetworkGroundMeta(zone))) return null;
  const roads = [0, 0];
  let surfaceZoneId: string | undefined;
  let uvFrame: StreetJunctionLayout['uvFrame'];
  const reaches = [[0, 0], [0, 0]];
  for (const zone of connected) {
    const profile = resolvePilotStreetSectionProfile(zone);
    const line = extractZoneCenterline(zone);
    if (!profile || line.length < 2 || !profile.renderCurbs) return null;
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
    const low = Math.min(...profile.curbOffsetsM) * scale;
    const high = Math.max(...profile.curbOffsetsM) * scale;
    // Asymmetric sections need an explicit left/right junction transition.
    if (low >= 0 || high <= 0 || Math.abs(low + high) > 0.05) return null;
    roads[axis] = Math.max(roads[axis], high);
  }
  const rowA = node.axisAHalfWidthM; const rowB = node.axisBHalfWidthM;
  if (roads[0] <= 0 || roads[1] <= 0 || roads[0] + 1.8 > rowA || roads[1] + 1.8 > rowB) return null;
  if (node.approachSides.some((sides, axis) => sides.some((side) =>
    reaches[axis][side === -1 ? 0 : 1] < (axis === 0 ? rowB : rowA) + 4 - 0.01))) return null;
  const orientation = Math.sin(node.axisBBearingRad - node.axisABearingRad) >= 0 ? 1 : -1;
  const sidesB = node.approachSides[1].map((side) => side * orientation as -1 | 1);
  return {
    bearing: node.axisABearingRad, surfaceZoneId, uvFrame, rowA, rowB, roadA: roads[0], roadB: roads[1], sidesB,
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
    return axis === 0 ? x * cos + y * sin : -x * sin + y * cos;
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
