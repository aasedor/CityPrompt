/**
 * Pure geometry builders for procedural 3D street details on the globe.
 *
 * All inputs/outputs are in local ENU metres (X=East, Y=North, Z=Up),
 * matching the frame convention in GlobeZoneLayer.createLocalGeometry —
 * callers convert lng/lat rings via metersPerDegLon/METERS_PER_DEG_LAT and
 * mount results inside an EastNorthUpFrame.
 *
 * Dimensions come from streetGeometryParams.json (shared with the Python
 * 2D diagram renderer) — image→3D was proven wrong for streets (a plan
 * diagram came back as a melted object, 2026-07-10 pilot); these builders
 * extrude the real vectors instead.
 */
import * as THREE from 'three';

import {
  ROUNDABOUT_PARAMS,
  STREET_DETAIL_3D,
  type RoundaboutParams,
  type StreetDetail3DParams,
} from '@/data/streetGeometryParams';
import {
  PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS,
  PUBLIC_REALM_STREET_MARKING_LIFT_METERS,
  PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_TACTILE_LIFT_METERS,
} from './publicRealmDepthPolicy';
import { samplePlaneOffset, type TerrainContactPlane } from './terrainContactProfile';

export interface LocalPt {
  x: number;
  y: number;
}

/** Cross-section terrain contact at one centreline station. Positive offsets
 * use the left edge, negative offsets the right edge. */
export interface StreetStationTerrain {
  centerZ: number;
  leftZ: number;
  rightZ: number;
  halfWidthM: number;
}

export type StreetStationElevationInput =
  | readonly number[]
  | readonly StreetStationTerrain[];

export function streetStationElevationAt(
  stationElevation: StreetStationElevationInput | undefined,
  stationIndex: number,
  signedOffsetM: number,
): number {
  const entry = stationElevation?.[stationIndex];
  if (typeof entry === 'number') return entry;
  if (!entry) return 0;
  const amount = Math.min(1, Math.abs(signedOffsetM) / Math.max(0.01, entry.halfWidthM));
  const edgeZ = signedOffsetM >= 0 ? entry.leftZ : entry.rightZ;
  return entry.centerZ + (edgeZ - entry.centerZ) * amount;
}

/** Mutate component-owned geometry onto one constructible local terrain plane.
 * Geometry-local x/y can be offset when the mesh mounts inside a translated
 * group (roundabouts use the oriented footprint centre). */
export function applyTerrainPlaneToStreetGeometry(
  geometry: THREE.BufferGeometry,
  plane: TerrainContactPlane | null | undefined,
  frameElevationMeters: number,
  localOriginX = 0,
  localOriginY = 0,
): THREE.BufferGeometry {
  if (!plane) return geometry;
  const positions = geometry.getAttribute('position') as THREE.BufferAttribute | undefined;
  if (!positions) return geometry;
  for (let index = 0; index < positions.count; index += 1) {
    const x = positions.getX(index) + localOriginX;
    const y = positions.getY(index) + localOriginY;
    const groundOffset = plane.originZ
      + samplePlaneOffset(plane, x, y)
      - frameElevationMeters;
    positions.setZ(index, positions.getZ(index) + groundOffset);
  }
  positions.needsUpdate = true;
  geometry.computeVertexNormals();
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();
  return geometry;
}

/** Insert intermediate stations so long spans can follow terrain. */
export function densifyPolyline(pts: LocalPt[], maxStep: number): LocalPt[] {
  if (pts.length < 2) return pts.slice();
  const out: LocalPt[] = [pts[0]];
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1];
    const b = pts[i];
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    const steps = Math.max(1, Math.ceil(len / maxStep));
    for (let s = 1; s <= steps; s++) {
      out.push({ x: a.x + ((b.x - a.x) * s) / steps, y: a.y + ((b.y - a.y) * s) / steps });
    }
  }
  return out;
}

/** Unit perpendicular (left of travel direction) at each station. */
export function stationNormals(pts: LocalPt[]): LocalPt[] {
  const n = pts.length;
  const normals: LocalPt[] = [];
  for (let i = 0; i < n; i++) {
    const a = pts[Math.max(0, i - 1)];
    const b = pts[Math.min(n - 1, i + 1)];
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const len = Math.hypot(dx, dy) || 1;
    normals.push({ x: -dy / len, y: dx / len });
  }
  return normals;
}

/** Terrain-following surface ribbon between two signed offsets from a
 * centerline. Positive offset is left of travel direction. */
export function buildRibbonBandGeometry(
  centerline: LocalPt[],
  startOffset: number,
  endOffset: number,
  liftM: number = 0.05,
  stationZ?: StreetStationElevationInput,
): THREE.BufferGeometry | null {
  if (centerline.length < 2 || Math.abs(endOffset - startOffset) < 0.01) return null;
  const normals = stationNormals(centerline);
  const positions: number[] = [];
  const indices: number[] = [];
  for (let i = 0; i < centerline.length; i += 1) {
    const point = centerline[i];
    const normal = normals[i];
    const startZ = streetStationElevationAt(stationZ, i, startOffset) + liftM;
    const endZ = streetStationElevationAt(stationZ, i, endOffset) + liftM;
    positions.push(
      point.x + normal.x * startOffset,
      point.y + normal.y * startOffset,
      startZ,
      point.x + normal.x * endOffset,
      point.y + normal.y * endOffset,
      endZ,
    );
  }
  for (let i = 0; i < centerline.length - 1; i += 1) {
    const a = i * 2;
    const b = (i + 1) * 2;
    indices.push(a, b, b + 1, a, b + 1, a + 1);
  }
  return toGeometry(positions, indices);
}

function toGeometry(positions: number[], indices: number[]): THREE.BufferGeometry {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setIndex(indices);
  geo.computeVertexNormals();
  geo.computeBoundingSphere();
  return geo;
}

/**
 * Raised curb prisms along BOTH edges of a road strip.
 *
 * Cross-section per station per side, from road inward->outward:
 *   innerBase (z) — innerTop (z+h) — outerTop (z+h) — outerBase (z)
 * `stationZ[i]` lets the caller drape stations onto terrain (default 0).
 */
export function buildCurbBandGeometry(
  centerline: LocalPt[],
  halfWidth: number,
  params: StreetDetail3DParams = STREET_DETAIL_3D,
  stationZ?: StreetStationElevationInput,
): THREE.BufferGeometry | null {
  if (centerline.length < 2) return null;
  const normals = stationNormals(centerline);
  const h = params.curbHeight_m;
  const inner = Math.max(0.1, halfWidth - params.curbWidth_m);
  const positions: number[] = [];
  const indices: number[] = [];

  for (const side of [1, -1]) {
    const base = positions.length / 3;
    for (let i = 0; i < centerline.length; i++) {
      const p = centerline[i];
      const nrm = normals[i];
      const innerOffset = inner * side;
      const outerOffset = halfWidth * side;
      const innerZ = streetStationElevationAt(stationZ, i, innerOffset)
        + PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS;
      const outerZ = streetStationElevationAt(stationZ, i, outerOffset)
        + PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS;
      const ix = p.x + nrm.x * inner * side;
      const iy = p.y + nrm.y * inner * side;
      const ox = p.x + nrm.x * halfWidth * side;
      const oy = p.y + nrm.y * halfWidth * side;
      positions.push(
        ix, iy, innerZ,
        ix, iy, innerZ + h,
        ox, oy, outerZ + h,
        ox, oy, outerZ,
      );
    }
    for (let i = 0; i < centerline.length - 1; i++) {
      const a = base + i * 4;
      const b = base + (i + 1) * 4;
      // inner wall, top, outer wall — three quads between stations.
      // Mirroring the cross-section across the centerline (side=-1) flips
      // handedness, so that side's triangles must wind the other way or the
      // whole band renders inside-out (backface-culled from above).
      for (const [o0, o1] of [
        [0, 1],
        [1, 2],
        [2, 3],
      ]) {
        if (side === 1) {
          indices.push(a + o0, b + o0, b + o1, a + o0, b + o1, a + o1);
        } else {
          indices.push(a + o1, b + o1, b + o0, a + o1, b + o0, a + o0);
        }
      }
    }
  }
  return toGeometry(positions, indices);
}

/** Raised curb prisms at arbitrary signed cross-section offsets. Detailed
 * sections use this instead of putting a curb at the full right-of-way edge
 * (which incorrectly stranded curbs behind sidewalks and boulevards). */
export function buildOffsetCurbGeometry(
  centerline: LocalPt[],
  offsetsM: number[],
  params: StreetDetail3DParams = STREET_DETAIL_3D,
  stationZ?: StreetStationElevationInput,
  skipStation?: boolean[],
): THREE.BufferGeometry | null {
  if (centerline.length < 2 || offsetsM.length === 0) return null;
  const normals = stationNormals(centerline);
  const halfWidth = params.curbWidth_m / 2;
  const height = params.curbHeight_m;
  const positions: number[] = [];
  const indices: number[] = [];

  for (const offset of offsetsM) {
    const base = positions.length / 3;
    for (let index = 0; index < centerline.length; index += 1) {
      const point = centerline[index];
      const normal = normals[index];
      const lowZ = streetStationElevationAt(stationZ, index, offset - halfWidth)
        + PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS;
      const highZ = streetStationElevationAt(stationZ, index, offset + halfWidth)
        + PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS;
      const lowX = point.x + normal.x * (offset - halfWidth);
      const lowY = point.y + normal.y * (offset - halfWidth);
      const highX = point.x + normal.x * (offset + halfWidth);
      const highY = point.y + normal.y * (offset + halfWidth);
      positions.push(
        lowX, lowY, lowZ,
        lowX, lowY, lowZ + height,
        highX, highY, highZ + height,
        highX, highY, highZ,
      );
    }
    for (let index = 0; index < centerline.length - 1; index += 1) {
      // Graph-owned intersection assemblies replace this span with a
      // directional curb ramp; do not leave a curb wall through the ramp.
      if (skipStation?.[index] || skipStation?.[index + 1]) continue;
      const a = base + index * 4;
      const b = base + (index + 1) * 4;
      for (const [start, end] of [[0, 1], [1, 2], [2, 3]] as const) {
        indices.push(
          a + start, b + start, b + end,
          a + start, b + end, a + end,
        );
      }
    }
  }

  return toGeometry(positions, indices);
}

/** Dashed centerline marking as flat quads slightly above the surface. */
export function buildDashGeometry(
  centerline: LocalPt[],
  params: StreetDetail3DParams = STREET_DETAIL_3D,
  stationZ?: StreetStationElevationInput,
  offsetM: number = 0,
): THREE.BufferGeometry | null {
  if (centerline.length < 2) return null;
  const normals = stationNormals(centerline);
  // cumulative arc length per station
  const cum: number[] = [0];
  for (let i = 1; i < centerline.length; i++) {
    cum.push(
      cum[i - 1] +
        Math.hypot(centerline[i].x - centerline[i - 1].x, centerline[i].y - centerline[i - 1].y),
    );
  }
  const total = cum[cum.length - 1];
  if (total <= 0) return null;

  const at = (dist: number): { p: LocalPt; n: LocalPt; z: number } => {
    let i = 1;
    while (i < cum.length - 1 && cum[i] < dist) i++;
    const t = (dist - cum[i - 1]) / (cum[i] - cum[i - 1] || 1);
    const a = centerline[i - 1];
    const b = centerline[i];
    const za = streetStationElevationAt(stationZ, i - 1, offsetM);
    const zb = streetStationElevationAt(stationZ, i, offsetM);
    return {
      p: { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t },
      n: normals[i - 1],
      z: za + (zb - za) * t,
    };
  };

  const hw = params.dashWidth_m / 2;
  const positions: number[] = [];
  const indices: number[] = [];
  let pos = 0;
  while (pos < total) {
    const end = Math.min(pos + params.dashLength_m, total);
    const s = at(pos);
    const e = at(end);
    const base = positions.length / 3;
    positions.push(
      s.p.x + s.n.x * (offsetM + hw), s.p.y + s.n.y * (offsetM + hw), s.z + params.dashLift_m,
      s.p.x + s.n.x * (offsetM - hw), s.p.y + s.n.y * (offsetM - hw), s.z + params.dashLift_m,
      e.p.x + e.n.x * (offsetM - hw), e.p.y + e.n.y * (offsetM - hw), e.z + params.dashLift_m,
      e.p.x + e.n.x * (offsetM + hw), e.p.y + e.n.y * (offsetM + hw), e.z + params.dashLift_m,
    );
    indices.push(base, base + 1, base + 2, base, base + 2, base + 3);
    pos += params.dashLength_m + params.dashGap_m;
  }
  return toGeometry(positions, indices);
}

export interface AccessibleFourWayIntersectionGeometry {
  /** High-contrast zebra bars for all four approaches. */
  crosswalks: THREE.BufferGeometry;
  /** Eight directional wedges bridging road level to sidewalk level. */
  curbRamps: THREE.BufferGeometry;
  /** Detectable-warning pads at the sidewalk end of each ramp. */
  tactilePads: THREE.BufferGeometry;
}

function appendQuad(
  positions: number[],
  indices: number[],
  centerX: number,
  centerY: number,
  axisX: LocalPt,
  axisY: LocalPt,
  halfX: number,
  halfY: number,
  z: number,
): void {
  const base = positions.length / 3;
  positions.push(
    centerX - axisX.x * halfX - axisY.x * halfY,
    centerY - axisX.y * halfX - axisY.y * halfY,
    z,
    centerX + axisX.x * halfX - axisY.x * halfY,
    centerY + axisX.y * halfX - axisY.y * halfY,
    z,
    centerX + axisX.x * halfX + axisY.x * halfY,
    centerY + axisX.y * halfX + axisY.y * halfY,
    z,
    centerX - axisX.x * halfX + axisY.x * halfY,
    centerY - axisX.y * halfX + axisY.y * halfY,
    z,
  );
  indices.push(base, base + 1, base + 2, base, base + 2, base + 3);
}

function appendRampWedge(
  positions: number[],
  indices: number[],
  centerX: number,
  centerY: number,
  along: LocalPt,
  outward: LocalPt,
  halfWidth: number,
  depth: number,
): void {
  const base = positions.length / 3;
  const innerX = centerX - outward.x * depth / 2;
  const innerY = centerY - outward.y * depth / 2;
  const outerX = centerX + outward.x * depth / 2;
  const outerY = centerY + outward.y * depth / 2;
  const lowZ = PUBLIC_REALM_STREET_MARKING_LIFT_METERS;
  const highZ = PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS;
  positions.push(
    innerX - along.x * halfWidth, innerY - along.y * halfWidth, lowZ,
    innerX + along.x * halfWidth, innerY + along.y * halfWidth, lowZ,
    outerX + along.x * halfWidth, outerY + along.y * halfWidth, highZ,
    outerX - along.x * halfWidth, outerY - along.y * halfWidth, highZ,
    innerX - along.x * halfWidth, innerY - along.y * halfWidth, PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS,
    innerX + along.x * halfWidth, innerY + along.y * halfWidth, PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS,
    outerX + along.x * halfWidth, outerY + along.y * halfWidth, PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS,
    outerX - along.x * halfWidth, outerY - along.y * halfWidth, PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS,
  );
  indices.push(
    base, base + 1, base + 2, base, base + 2, base + 3,
    base + 4, base + 5, base + 1, base + 4, base + 1, base,
    base + 5, base + 6, base + 2, base + 5, base + 2, base + 1,
    base + 6, base + 7, base + 3, base + 6, base + 3, base + 2,
    base + 7, base + 4, base, base + 7, base, base + 3,
  );
}

/**
 * Metric, graph-node-owned accessible crossing assembly. Axis A and B are
 * the two undirected street bearings in local ENU radians. Geometry is kept
 * independent from street ribbons so crossing markings are emitted once per
 * graph node rather than once per overlapping zone.
 */
export function buildAccessibleFourWayIntersectionGeometry(
  axisABearingRad: number,
  axisBBearingRad: number,
  axisAHalfWidthM: number,
  axisBHalfWidthM: number,
): AccessibleFourWayIntersectionGeometry | null {
  if (
    axisAHalfWidthM < 1.5
    || axisBHalfWidthM < 1.5
    || !Number.isFinite(axisABearingRad)
    || !Number.isFinite(axisBBearingRad)
  ) return null;
  const crosswalkPositions: number[] = [];
  const crosswalkIndices: number[] = [];
  const rampPositions: number[] = [];
  const rampIndices: number[] = [];
  const tactilePositions: number[] = [];
  const tactileIndices: number[] = [];
  const axes = [
    { bearing: axisABearingRad, roadHalfWidth: axisAHalfWidthM, crossingHalfWidth: axisBHalfWidthM },
    { bearing: axisBBearingRad, roadHalfWidth: axisBHalfWidthM, crossingHalfWidth: axisAHalfWidthM },
  ];
  for (const axis of axes) {
    const along = { x: Math.cos(axis.bearing), y: Math.sin(axis.bearing) };
    const across = { x: -along.y, y: along.x };
    for (const approachSide of [-1, 1]) {
      const crosswalkCenterDistance = axis.crossingHalfWidth + 1.8;
      const crosswalkCenterX = along.x * approachSide * crosswalkCenterDistance;
      const crosswalkCenterY = along.y * approachSide * crosswalkCenterDistance;
      // Seven 300 mm zebra bars over a 3 m walking corridor.
      for (let stripe = -3; stripe <= 3; stripe += 1) {
        const stripeOffset = stripe * 0.43;
        appendQuad(
          crosswalkPositions,
          crosswalkIndices,
          crosswalkCenterX + along.x * stripeOffset,
          crosswalkCenterY + along.y * stripeOffset,
          along,
          across,
          0.15,
          axis.roadHalfWidth,
          PUBLIC_REALM_STREET_MARKING_LIFT_METERS,
        );
      }
      for (const curbSide of [-1, 1]) {
        const outward = { x: across.x * curbSide, y: across.y * curbSide };
        const rampCenterDistance = axis.roadHalfWidth + 0.55;
        const rampCenterX = crosswalkCenterX + outward.x * rampCenterDistance;
        const rampCenterY = crosswalkCenterY + outward.y * rampCenterDistance;
        appendRampWedge(
          rampPositions,
          rampIndices,
          rampCenterX,
          rampCenterY,
          along,
          outward,
          0.9,
          1.1,
        );
        appendQuad(
          tactilePositions,
          tactileIndices,
          rampCenterX + outward.x * 0.22,
          rampCenterY + outward.y * 0.22,
          along,
          outward,
          0.62,
          0.27,
          PUBLIC_REALM_STREET_TACTILE_LIFT_METERS,
        );
      }
    }
  }
  return {
    crosswalks: toGeometry(crosswalkPositions, crosswalkIndices),
    curbRamps: toGeometry(rampPositions, rampIndices),
    tactilePads: toGeometry(tactilePositions, tactileIndices),
  };
}

export interface RoundaboutGeometry {
  /** circulatory lane surface (asphalt) */
  ring: THREE.BufferGeometry;
  /** truck apron annulus (concrete) */
  apron: THREE.BufferGeometry;
  /** raised planted central island */
  island: THREE.BufferGeometry;
  /** four splitter-island prisms */
  splitters: THREE.BufferGeometry;
  /** Four setback zebra crossings plus four yield bars. */
  approachMarkings: THREE.BufferGeometry;
  /** applied radial scale (1 = standard 28m ICD) */
  scale: number;
}

/**
 * Parametric compact roundabout — direct 3D port of the 2D diagram math in
 * scripts/_render_diagrams_toscale.py build_roundabout, radii from the same
 * JSON. `inscribedRadius` clamps the standard footprint into the zone;
 * `bearingRad` aligns the four legs (0 = legs along +X/+Y axes).
 */
export function buildRoundaboutGeometry(
  inscribedRadius: number,
  bearingRad: number = 0,
  ra: RoundaboutParams = ROUNDABOUT_PARAMS,
  detail: StreetDetail3DParams = STREET_DETAIL_3D,
): RoundaboutGeometry | null {
  const standardReach = ra.ICD / 2 + ra.SLEN;
  if (inscribedRadius <= 2) return null;
  const scale = Math.min(1, inscribedRadius / standardReach);

  const rIcd = (ra.ICD / 2) * scale;
  const rApron = (ra.ICD / 2 - ra.CIRC) * scale;
  const rCentral = (ra.ICD / 2 - ra.CIRC - ra.APRON) * scale;

  const ring = new THREE.RingGeometry(rApron, rIcd, 64);
  ring.translate(0, 0, PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS);

  const apron = new THREE.RingGeometry(rCentral, rApron, 64);
  apron.translate(0, 0, detail.apronLift_m);

  const island = new THREE.CylinderGeometry(rCentral, rCentral, detail.islandHeight_m, 48);
  island.rotateX(Math.PI / 2); // cylinder axis Y -> Z (ENU up)
  island.translate(
    0,
    0,
    PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS + detail.islandHeight_m / 2,
  );

  // Splitter islands: triangle (tip toward circle, base outward) extruded
  // to curb height, one per leg at bearing + 0/90/180/270.
  const positions: number[] = [];
  const indices: number[] = [];
  const tip = (ra.ICD / 2 + 0.5) * scale;
  const back = (ra.ICD / 2 + ra.SLEN) * scale;
  const wb = ((ra.REFUGE / 2) * scale);
  const h = detail.curbHeight_m;
  for (let leg = 0; leg < 4; leg++) {
    const a = bearingRad + (leg * Math.PI) / 2;
    const ux = Math.cos(a);
    const uy = Math.sin(a);
    const px = -uy;
    const py = ux;
    // CCW viewed from +Z (tip, base-right, base-left) — the (3,4,5) top face
    // and the wall pattern below both face outward only with this winding.
    const tri: [number, number][] = [
      [ux * tip, uy * tip],
      [ux * back - px * wb, uy * back - py * wb],
      [ux * back + px * wb, uy * back + py * wb],
    ];
    const base = positions.length / 3;
    for (const [x, y] of tri) positions.push(x, y, PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS);
    for (const [x, y] of tri) positions.push(
      x,
      y,
      PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS + h,
    );
    indices.push(base + 3, base + 4, base + 5); // top
    for (let i = 0; i < 3; i++) {
      const j = (i + 1) % 3;
      indices.push(base + i, base + j, base + 3 + j, base + i, base + 3 + j, base + 3 + i);
    }
  }
  const splitters = toGeometry(positions, indices);

  const markingPositions: number[] = [];
  const markingIndices: number[] = [];
  for (let leg = 0; leg < 4; leg += 1) {
    const angle = bearingRad + (leg * Math.PI) / 2;
    const along = { x: Math.cos(angle), y: Math.sin(angle) };
    const across = { x: -along.y, y: along.x };
    const crosswalkCenter = rIcd + (ra.SETBK + ra.CW / 2) * scale;
    for (let stripe = -3; stripe <= 3; stripe += 1) {
      const stripeOffset = stripe * (ra.CW * scale / 7);
      appendQuad(
        markingPositions,
        markingIndices,
        along.x * (crosswalkCenter + stripeOffset),
        along.y * (crosswalkCenter + stripeOffset),
        along,
        across,
        0.13 * scale,
        (ra.APP * 0.46) * scale,
        PUBLIC_REALM_STREET_MARKING_LIFT_METERS,
      );
    }
    const yieldDistance = rIcd + 1.35 * scale;
    appendQuad(
      markingPositions,
      markingIndices,
      along.x * yieldDistance,
      along.y * yieldDistance,
      along,
      across,
      0.09 * scale,
      Math.max(0.65, (ra.APP - ra.REFUGE) * 0.22 * scale),
      PUBLIC_REALM_STREET_MARKING_LIFT_METERS,
    );
  }
  const approachMarkings = toGeometry(markingPositions, markingIndices);

  return { ring, apron, island, splitters, approachMarkings, scale };
}
