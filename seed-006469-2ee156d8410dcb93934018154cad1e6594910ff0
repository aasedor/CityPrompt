/**
 * buildingPlacement.ts — pure math for seating a generated .glb on the globe.
 *
 * Meshy models arrive at arbitrary scale/origin in glTF Y-up space; the globe
 * places content in EastNorthUpFrame local meters (X=East, Y=North, Z=Up).
 * These functions derive, from a building's WGS84 footprint ring, everything
 * the layer needs: where the model goes (oriented-rect center), how big it is
 * (uniform contain-fit — never overhangs the parcel), and which way it faces
 * (long axis of the footprint plus the user's rotation_degrees offset).
 */

import type { Vector3 } from 'three';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

const DEG_TO_RAD = Math.PI / 180;

export interface FootprintFrame {
  centroidLng: number;
  centroidLat: number;
  /** Long-axis angle, CCW from East in the ENU ground plane, folded to [-PI/2, PI/2). */
  bearingRad: number;
  /** Oriented-bounding-rect dimensions in meters. */
  longDim: number;
  shortDim: number;
  /** Oriented-rect center in ENU meters relative to the vertex centroid —
   *  irregular rings put the visual center away from the vertex mean. */
  rectCenterLocal: [number, number];
}

export interface ModelPlacement {
  /** Uniform scale factor: model native units -> meters, contain-fit. */
  scale: number;
  /** Rotation about ENU Up to align the model with the parcel. */
  yawRad: number;
  /** True when the scaled model height misses height_meters by >40%. */
  heightWarning: boolean;
}

function foldToAxis(theta: number): number {
  // An axis has no direction: fold to [-PI/2, PI/2).
  const folded = ((theta + Math.PI / 2) % Math.PI + Math.PI) % Math.PI - Math.PI / 2;
  return folded;
}

export function computeFootprintFrame(ring: number[][]): FootprintFrame | null {
  const pts = (ring ?? []).filter((c) => Array.isArray(c) && c.length >= 2);
  if (pts.length < 3) return null;

  const centroidLng = pts.reduce((s, c) => s + c[0], 0) / pts.length;
  const centroidLat = pts.reduce((s, c) => s + c[1], 0) / pts.length;
  const mPerDegLon = metersPerDegLon(centroidLat);

  // Local ENU meters relative to the vertex centroid (same conversion as
  // GlobeZoneLayer.createLocalGeometry).
  const local = pts.map((c) => ({
    x: (c[0] - centroidLng) * mPerDegLon,          // East
    y: (c[1] - centroidLat) * METERS_PER_DEG_LAT,  // North
  }));

  // Long-axis bearing = angle of the longest ring edge (closing edge included).
  let bestLen = 0;
  let theta = 0;
  for (let i = 0; i < local.length; i += 1) {
    const a = local[i];
    const b = local[(i + 1) % local.length];
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    if (len > bestLen) {
      bestLen = len;
      theta = Math.atan2(b.y - a.y, b.x - a.x);
    }
  }
  theta = foldToAxis(theta);

  // Oriented bounding rect in the axis-rotated frame.
  const cos = Math.cos(theta);
  const sin = Math.sin(theta);
  let uMin = Infinity; let uMax = -Infinity; let vMin = Infinity; let vMax = -Infinity;
  for (const p of local) {
    const u = p.x * cos + p.y * sin;
    const v = -p.x * sin + p.y * cos;
    if (u < uMin) uMin = u;
    if (u > uMax) uMax = u;
    if (v < vMin) vMin = v;
    if (v > vMax) vMax = v;
  }
  let longDim = uMax - uMin;
  let shortDim = vMax - vMin;
  let bearingRad = theta;
  if (shortDim > longDim) {
    [longDim, shortDim] = [shortDim, longDim];
    bearingRad = foldToAxis(theta + Math.PI / 2);
  }
  if (longDim < 1.0 || shortDim < 0.5) return null; // degenerate ring

  const cu = (uMin + uMax) / 2;
  const cv = (vMin + vMax) / 2;
  return {
    centroidLng,
    centroidLat,
    bearingRad,
    longDim,
    shortDim,
    rectCenterLocal: [cu * cos - cv * sin, cu * sin + cv * cos],
  };
}

export function computeModelPlacement(
  frame: FootprintFrame,
  modelSize: Pick<Vector3, 'x' | 'y' | 'z'>,
  heightMeters: number | null | undefined,
  rotationDegrees: number | null | undefined,
): ModelPlacement | null {
  // Model footprint lives in XZ (glTF Y-up). After the layer's Rx(+90°)
  // swizzle, model X lands on ENU East and model Z on ENU -North.
  const modelLong = Math.max(modelSize.x, modelSize.z);
  const modelShort = Math.min(modelSize.x, modelSize.z);
  if (!(modelLong > 1e-3) || !(modelShort > 1e-6)) return null;

  // Height-anchored, parcel-clamped: Meshy normalizes every model to roughly
  // a unit cube regardless of the footprint the prompt asks for, so pure
  // contain-fit gives same-block siblings wildly different scales (measured:
  // 9.3 m vs 14.9 m on one 3-storey block — the small one reads as a
  // miniature). Anchoring to the building's target height makes the block a
  // uniform streetwall; contain-fit remains as the never-overhang clamp.
  const containFit = Math.min(frame.longDim / modelLong, frame.shortDim / modelShort);
  const heightFit = heightMeters && heightMeters > 0 && modelSize.y > 1e-3
    ? heightMeters / modelSize.y
    : null;
  const scale = Math.min(
    Math.max(heightFit !== null ? Math.min(heightFit, containFit) : containFit, 0.01),
    1000,
  );

  const modelAxisAngle = modelSize.x >= modelSize.z ? 0 : -Math.PI / 2;
  const yawRad = frame.bearingRad - modelAxisAngle + (rotationDegrees ?? 0) * DEG_TO_RAD;

  const scaledHeight = scale * modelSize.y;
  const heightWarning = Boolean(
    heightMeters && heightMeters > 0
    && Math.abs(scaledHeight - heightMeters) / heightMeters > 0.4,
  );

  return { scale, yawRad, heightWarning };
}
