import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { detectConnectedStreetIntersections, type ConnectedStreetIntersection } from './streetGraphIntersections';
import { publicRealmTrialAsset, publicRealmTrialPlacement, type PublicRealmTrialAsset } from './publicRealmTrial';
import { type StreetJunctionLayout } from './streetJunctionGeometry';

export interface NativeStreetPlacement {
  zone: SiteZone;
  placement: NonNullable<ReturnType<typeof publicRealmTrialPlacement>>;
}
export interface NativeStreetJunction {
  node: ConnectedStreetIntersection;
  layout: StreetJunctionLayout;
  streets: NativeStreetPlacement[];
  height: number;
}

/** Optional authored finish for a paved native section. New street assets
 * register this alongside dimensions and surfaceRegions; pavers is the safe
 * default for older review packages. */
type JunctionSurface = 'pavers' | 'brick' | 'cobble' | 'timber';
function junctionSurface(asset: PublicRealmTrialAsset): JunctionSurface {
  if ('junctionSurface' in asset && (asset.junctionSurface === 'timber' || asset.junctionSurface === 'cobble'
    || asset.junctionSurface === 'brick')) {
    return asset.junctionSurface;
  }
  return 'pavers';
}

/** The same graph nodes and footprint contract used by the compiled street
 * renderer. Rigid native sections join at straight, orthogonal T/X nodes on
 * one prepared datum; a missing T arm never acquires a fictitious surface. */
export function nativeStreetJunctions(zones: SiteZone[], terrainHeight: number): NativeStreetJunction[] {
  const streets = zones.flatMap((zone): NativeStreetPlacement[] => {
    const asset = publicRealmTrialAsset(zone);
    const placement = asset?.kind === 'street' ? publicRealmTrialPlacement(zone, zones, terrainHeight) : null;
    return placement ? [{ zone, placement }] : [];
  });
  if (streets.length < 2) return [];
  const byId = new Map(streets.map((street) => [street.zone.id, street]));
  return detectConnectedStreetIntersections(streets.map((street) => street.zone)).flatMap((node) => {
    if (!node.orthogonal || node.approachSides[0].length !== 2 || node.zoneIds.length !== 2) return [];
    const connected = node.zoneIds.map((id) => byId.get(id));
    if (connected.some((item) => !item)) return [];
    const pair = connected as NativeStreetPlacement[];
    if (Math.abs(pair[0].placement.height - pair[1].placement.height) > .05) return [];
    const rowA = node.axisAHalfWidthM, rowB = node.axisBHalfWidthM;
    const sidesB = node.approachSides[1];
    const layout: StreetJunctionLayout = {
      bearing: node.axisABearingRad,
      rowA, rowB, roadA: rowA, roadB: rowB, sidesB,
      bounds: [
        { minX: -rowB - 2, maxX: rowB + 2, minY: -rowA, maxY: rowA },
        { minX: -rowB, maxX: rowB,
          minY: sidesB.includes(-1) ? -rowA - 2 : 0,
          maxY: sidesB.includes(1) ? rowA + 2 : 0 },
      ],
    };
    // A T stem legitimately ends at the node. Check the *present* directed
    // approaches against the complete node footprint instead of demanding
    // two metres of model beyond that endpoint (which would invent arm four).
    const reaches = pair.every(({ placement }) => {
      const [width, length] = placement.asset.dimensions;
      const dx = (node.longitude - placement.lng) * metersPerDegLon(node.latitude);
      const dy = (node.latitude - placement.lat) * METERS_PER_DEG_LAT;
      const localX = dx * Math.cos(placement.yaw) + dy * Math.sin(placement.yaw);
      const localY = -dx * Math.sin(placement.yaw) + dy * Math.cos(placement.yaw);
      if (Math.abs(localX) > width / 2 + .05) return false;
      const routeBearing = placement.yaw + Math.PI / 2;
      const axis = Math.abs(Math.cos(routeBearing - node.axisABearingRad)) > .9 ? 0 : 1;
      const bearing = axis === 0 ? node.axisABearingRad : node.axisBBearingRad;
      if (Math.abs(Math.cos(routeBearing - bearing)) < .999) return false;
      const direction = Math.sign(Math.cos(routeBearing - bearing));
      const endpoints = [(-length / 2 - localY) * direction, (length / 2 - localY) * direction];
      const required = (axis === 0 ? rowB : rowA) + 2;
      return node.approachSides[axis].every((side) =>
        Math.max(...endpoints.map((value) => value * side)) >= required - .05);
    });
    return reaches ? [{ node, layout, streets: pair, height: pair[0].placement.height }] : [];
  });
}

/** Convert the graph-owned ENU footprint to the rigid model's local frame. */
export function nativeLocalJunction(junction: NativeStreetJunction, placement: NativeStreetPlacement['placement']) {
  const dx = (junction.node.longitude - placement.lng) * metersPerDegLon(junction.node.latitude);
  const dy = (junction.node.latitude - placement.lat) * METERS_PER_DEG_LAT;
  return {
    centerX: dx * Math.cos(placement.yaw) + dy * Math.sin(placement.yaw),
    centerY: -dx * Math.sin(placement.yaw) + dy * Math.cos(placement.yaw),
    layout: { ...junction.layout, bearing: junction.layout.bearing - placement.yaw },
  };
}

function materialAt(asset: PublicRealmTrialAsset, x: number, y: number): string | null {
  if (Math.abs(x) > asset.dimensions[0] / 2 + 1e-4 || Math.abs(y) > asset.dimensions[1] / 2 + 1e-4) return null;
  let material: string | null = 'grass';
  for (const region of asset.surfaceRegions) {
    if (Math.abs(x - region.x) <= region.width / 2 && Math.abs(y - region.y) <= region.depth / 2) material = region.material;
  }
  return material;
}

/** Preserve the authored longitudinal surface bands through the intersection.
 * Hard circulation takes precedence over planting; the first graph arm owns
 * like-for-like overlaps. This also opens planted medians where a path crosses. */
export function buildNativeStreetJunctionGround(junction: NativeStreetJunction): THREE.BufferGeometry {
  const { layout, node, streets } = junction;
  const priority: Record<string, number> = { asphalt: 5, cycle: 4, paving: 3, soil: 2, grass: 1 };
  const positions: number[] = [], colors: number[] = [];
  const palette: Record<string, [number, number, number]> = {
    asphalt: [.10, .115, .11], cycle: [.33, .145, .085], paving: [.53, .50, .43],
    soil: [.105, .073, .045], grass: [.21, .28, .105],
  };
  const cos = Math.cos(layout.bearing), sin = Math.sin(layout.bearing);
  const toWorld = (u: number, v: number): [number, number] => [u * cos - v * sin, u * sin + v * cos];
  const sample = (u: number, v: number) => {
    const [east, north] = toWorld(u, v);
    return streets.map(({ placement }) => {
      const dx = east + (node.longitude - placement.lng) * metersPerDegLon(node.latitude);
      const dy = north + (node.latitude - placement.lat) * METERS_PER_DEG_LAT;
      const x = dx * Math.cos(placement.yaw) + dy * Math.sin(placement.yaw);
      const y = -dx * Math.sin(placement.yaw) + dy * Math.cos(placement.yaw);
      return { material: materialAt(placement.asset, x, y), style: junctionSurface(placement.asset), x, y };
    }).reduce<{ material: string | null; style: JunctionSurface; x: number; y: number } | null>((best, candidate) => {
      if (!candidate.material) return best;
      if (!best?.material || priority[candidate.material] > priority[best.material]) return candidate;
      const rank: Record<JunctionSurface, number> = { pavers: 1, brick: 2, cobble: 3, timber: 4 };
      return priority[candidate.material] === priority[best.material] && rank[candidate.style] > rank[best.style]
        ? candidate : best;
    }, null);
  };
  const xs = [...new Set(layout.bounds.flatMap((rect) => [rect.minX, rect.maxX]))].sort((a, b) => a - b);
  const ys = [...new Set(layout.bounds.flatMap((rect) => [rect.minY, rect.maxY]))].sort((a, b) => a - b);
  const subdivide = (edges: number[]) => edges.flatMap((start, i) => {
    if (i === edges.length - 1) return [start];
    const count = Math.ceil((edges[i + 1] - start) / .5);
    return Array.from({ length: count }, (_, j) => start + (edges[i + 1] - start) * j / count);
  });
  const gridX = subdivide(xs), gridY = subdivide(ys);
  for (let i = 0; i < gridX.length - 1; i++) for (let j = 0; j < gridY.length - 1; j++) {
    const u = (gridX[i] + gridX[i + 1]) / 2, v = (gridY[j] + gridY[j + 1]) / 2;
    if (!layout.bounds.some((rect) => u > rect.minX && u < rect.maxX && v > rect.minY && v < rect.maxY)) continue;
    const surface = sample(u, v);
    if (!surface?.material) continue;
    let color = palette[surface.material];
    if (surface.material === 'paving') {
      if (surface.style === 'timber') color = Math.floor(surface.y / .42) % 2 === 0
        ? [.43, .32, .22] : [.39, .29, .20];
      else if (surface.style === 'cobble') color = (Math.floor(surface.x / .5) + Math.floor(surface.y / .5)) % 3 === 0
        ? [.46, .45, .41] : [.51, .49, .44];
      else if (surface.style === 'brick') color = (Math.floor(surface.x / .5) + Math.floor(surface.y / .5)) % 3 === 0
        ? [.42, .29, .22] : [.48, .34, .26];
      else color = (Math.floor(surface.x / .6) + Math.floor(surface.y / .6)) % 3 === 0
        ? [.50, .47, .41] : [.54, .51, .45];
    }
    const corners = [toWorld(gridX[i], gridY[j]), toWorld(gridX[i + 1], gridY[j]),
      toWorld(gridX[i + 1], gridY[j + 1]), toWorld(gridX[i], gridY[j + 1])];
    for (const index of [0, 1, 2, 0, 2, 3]) {
      positions.push(corners[index][0], corners[index][1], .012);
      colors.push(...color);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geometry.computeVertexNormals();
  return geometry;
}
