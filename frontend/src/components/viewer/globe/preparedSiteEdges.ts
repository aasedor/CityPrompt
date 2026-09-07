import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { validPreparedLevel, type GroundReview } from './groundReview';
import { SHARED_SITE_GROUND_LIMITS } from './sharedSiteGround';

export interface PreparedEdgeProfile {
  version: 1;
  source: 'google_visible_surface';
  verticalReference: 'WGS84_ellipsoid';
  boundaryCoordinates: number[][];
  /** Densified boundary, in order. Heights interpolate two repeatable mesh passes. */
  samples: Array<[number, number, number]>;
}

const MAX_EDGE_SAMPLES = 512;
function edgePoints(coordinates: number[][]): Array<[number, number]> | null {
  const ring = coordinates.map(p => [p[0], p[1]] as [number, number]);
  if (ring.length > 1 && ring[0][0] === ring[ring.length-1][0] && ring[0][1] === ring[ring.length-1][1]) ring.pop();
  if (ring.length < 3 || ring.length > MAX_EDGE_SAMPLES || ring.some(p => !p.every(Number.isFinite) || Math.abs(p[0]) > 180 || Math.abs(p[1]) > 85)) return null;
  const points: Array<[number, number]> = [];
  for (let i = 0; i < ring.length; i++) {
    const a = ring[i], b = ring[(i + 1) % ring.length];
    const length = Math.hypot((b[0] - a[0]) * metersPerDegLon(a[1]), (b[1] - a[1]) * METERS_PER_DEG_LAT);
    const count = Math.max(1, Math.ceil(length / 2.5));
    if (points.length + count > MAX_EDGE_SAMPLES) return null;
    for (let j = 0; j < count; j++) points.push([a[0] + (b[0] - a[0]) * j / count, a[1] + (b[1] - a[1]) * j / count]);
  }
  return points;
}

export function supportsPreparedEdges(boundary: SiteZone): boolean { return edgePoints(boundary.coordinates) !== null; }

/** Measurements are accepted only when all four support samples are finite and
 * agree between passes. This is a visible-surface profile, never inferred earth. */
export function measurePreparedEdges(boundary: SiteZone, review?: GroundReview | null): PreparedEdgeProfile | null {
  const points = edgePoints(boundary.coordinates);
  if (!points || !review?.previousHeights || JSON.stringify(boundary.coordinates) !== JSON.stringify(review.layout.boundaryCoordinates)) return null;
  const { west, south, columns, rows, stepLng, stepLat } = review.layout.grid;
  if (columns < 2 || rows < 2 || stepLng <= 0 || stepLat <= 0) return null;
  const samples: PreparedEdgeProfile['samples'] = [];
  for (const [lng, lat] of points) {
    const x = (lng - west) / stepLng, y = (lat - south) / stepLat;
    if (x < -1e-6 || y < -1e-6 || x > columns - 1 + 1e-6 || y > rows - 1 + 1e-6) return null;
    const ix = Math.max(0, Math.min(columns - 2, Math.floor(x))), iy = Math.max(0, Math.min(rows - 2, Math.floor(y)));
    const tx = Math.max(0, Math.min(1, x - ix)), ty = Math.max(0, Math.min(1, y - iy));
    const indices = [iy * columns + ix, iy * columns + ix + 1, (iy + 1) * columns + ix, (iy + 1) * columns + ix + 1];
    const heights = indices.map(i => review.heights[i]);
    if (indices.some((i, k) => typeof heights[k] !== 'number' || !validPreparedLevel(heights[k]!)
      || typeof review.previousHeights![i] !== 'number' || !validPreparedLevel(review.previousHeights![i]!)
      || Math.abs(heights[k]! - review.previousHeights![i]!) > SHARED_SITE_GROUND_LIMITS.maxPassDeltaM)) return null;
    const h = (heights[0]! * (1 - tx) + heights[1]! * tx) * (1 - ty) + (heights[2]! * (1 - tx) + heights[3]! * tx) * ty;
    samples.push([lng, lat, h]);
  }
  return { version: 1, source: 'google_visible_surface', verticalReference: 'WGS84_ellipsoid', boundaryCoordinates: boundary.coordinates.map(p => [...p]), samples };
}

/** Reject stale profiles after an outline edit, and malformed imported metadata. */
export function readPreparedEdges(boundary: SiteZone): PreparedEdgeProfile | null {
  const profile = boundary.properties?.terrain_edge_profile as PreparedEdgeProfile | undefined;
  if (!profile || profile.version !== 1 || profile.source !== 'google_visible_surface' || profile.verticalReference !== 'WGS84_ellipsoid'
    || JSON.stringify(profile.boundaryCoordinates) !== JSON.stringify(boundary.coordinates) || !Array.isArray(profile.samples)) return null;
  const points = edgePoints(boundary.coordinates);
  if (!points || points.length !== profile.samples.length) return null;
  if (points.some((p, i) => !Array.isArray(profile.samples[i]) || profile.samples[i].length !== 3
    || !profile.samples[i].every(Number.isFinite) || !validPreparedLevel(profile.samples[i][2])
    || Math.abs(p[0] - profile.samples[i][0]) > 1e-10 || Math.abs(p[1] - profile.samples[i][1]) > 1e-10)) return null;
  return profile;
}

export function preparedEdgeSummary(profile: PreparedEdgeProfile, level: number) {
  const heights = profile.samples.map(p => p[2]);
  return { maximumFill: Math.max(0, level - Math.min(...heights)), maximumCut: Math.max(0, Math.max(...heights) - level) };
}

/** A concept retaining face on the exact boundary. Cut and fill faces split at
 * grade crossings; no inverted bow-tie quads or walls across concave notches. */
export function createPreparedEdgeGeometry(profile: Pick<PreparedEdgeProfile, 'samples'>, level: number, origin: [number, number], closed = true): THREE.BufferGeometry {
  const positions: number[] = [], uvs: number[] = [];
  const local = ([lng, lat, h]: number[]) => [(lng - origin[0]) * metersPerDegLon(origin[1]), (lat - origin[1]) * METERS_PER_DEG_LAT, h - level];
  const face = (a: number[], b: number[]) => {
    if (Math.max(Math.abs(a[2]), Math.abs(b[2])) < 0.03) return;
    const lowA = Math.min(-0.06, a[2] - 0.08), lowB = Math.min(-0.06, b[2] - 0.08);
    const highA = Math.max(0, a[2]), highB = Math.max(0, b[2]);
    const verts = [[a[0],a[1],lowA], [b[0],b[1],lowB], [b[0],b[1],highB], [a[0],a[1],highA]];
    for (const i of [0,1,2,0,2,3]) { positions.push(...verts[i]); uvs.push(i === 0 || i === 3 ? 0 : Math.hypot(b[0]-a[0],b[1]-a[1]), verts[i][2]); }
  };
  for (let i = 0; i < profile.samples.length - (closed ? 0 : 1); i++) {
    const a = local(profile.samples[i]), b = local(profile.samples[(i + 1) % profile.samples.length]);
    if (a[2] * b[2] < 0) {
      const t = a[2] / (a[2] - b[2]), cross = [a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),0];
      face(a,cross); face(cross,b);
    } else face(a,b);
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions,3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs,2));
  geometry.computeVertexNormals(); geometry.computeBoundingSphere();
  return geometry;
}
