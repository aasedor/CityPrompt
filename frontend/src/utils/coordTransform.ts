/**
 * Coordinate transform utilities for converting between geographic coordinates
 * (degrees), meters, and SVG pixel space.
 *
 * Extracted from SitePlanDiagram.tsx for reuse across block editor and diagrams.
 */

export const METERS_PER_DEG_LAT = 111320;

export function metersPerDegLon(lat: number): number {
  return METERS_PER_DEG_LAT * Math.abs(Math.cos((lat * Math.PI) / 180));
}

export interface Transform {
  cx: number;   // centroid longitude
  cy: number;   // centroid latitude
  mlon: number; // meters per degree longitude at centroid
  mlat: number; // meters per degree latitude
  scale: number;
  offsetX: number;
  offsetY: number;
  svgW: number;
  svgH: number;
}

export function computeTransform(
  coords: number[][],
  svgW: number,
  svgH: number,
  padding: number = 20,
): Transform {
  if (coords.length === 0) {
    return { cx: 0, cy: 0, mlon: 1, mlat: METERS_PER_DEG_LAT, scale: 1, offsetX: svgW / 2, offsetY: svgH / 2, svgW, svgH };
  }
  const cx = coords.reduce((s, c) => s + c[0], 0) / coords.length;
  const cy = coords.reduce((s, c) => s + c[1], 0) / coords.length;
  const mlon = metersPerDegLon(cy);
  const mlat = METERS_PER_DEG_LAT;

  const mCoords = coords.map((c) => [(c[0] - cx) * mlon, (c[1] - cy) * mlat]);
  const xs = mCoords.map((c) => c[0]);
  const ys = mCoords.map((c) => c[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const rangeX = maxX - minX || 1;
  const rangeY = maxY - minY || 1;

  const usableW = svgW - padding * 2;
  const usableH = svgH - padding * 2;
  const scale = Math.min(usableW / rangeX, usableH / rangeY);

  const offsetX = svgW / 2 - ((minX + maxX) / 2) * scale;
  const offsetY = svgH / 2 + ((minY + maxY) / 2) * scale; // flip Y

  return { cx, cy, mlon, mlat, scale, offsetX, offsetY, svgW, svgH };
}

/** Convert lon/lat to SVG pixel coordinates */
export function toSVG(lon: number, lat: number, t: Transform): [number, number] {
  const mx = (lon - t.cx) * t.mlon;
  const my = (lat - t.cy) * t.mlat;
  return [mx * t.scale + t.offsetX, -my * t.scale + t.offsetY];
}

/** Convert degree offset from centroid to SVG pixel coordinates */
export function offsetToSVG(dx: number, dy: number, t: Transform): [number, number] {
  const mx = dx * t.mlon;
  const my = dy * t.mlat;
  return [mx * t.scale + t.offsetX, -my * t.scale + t.offsetY];
}

/** Convert SVG pixel coordinates back to degree offsets from centroid (inverse of offsetToSVG) */
export function svgToOffset(px: number, py: number, t: Transform): [number, number] {
  const mx = (px - t.offsetX) / t.scale;
  const my = -(py - t.offsetY) / t.scale;
  const dx = mx / t.mlon;
  const dy = my / t.mlat;
  return [dx, dy];
}

/** Convert meters to degrees longitude at a given latitude */
export function metersToDegreesLon(meters: number, lat: number): number {
  return meters / metersPerDegLon(lat);
}

/** Convert meters to degrees latitude */
export function metersToDegreesLat(meters: number): number {
  return meters / METERS_PER_DEG_LAT;
}

/** Convert degrees longitude to meters at a given latitude */
export function degreesToMetersLon(degrees: number, lat: number): number {
  return degrees * metersPerDegLon(lat);
}

/** Convert degrees latitude to meters */
export function degreesToMetersLat(degrees: number): number {
  return degrees * METERS_PER_DEG_LAT;
}

/** Convert meters to SVG pixel size */
export function metersToPixels(meters: number, t: Transform): number {
  return meters * t.scale;
}

/** Convert SVG pixel size to meters */
export function pixelsToMeters(pixels: number, t: Transform): number {
  return pixels / t.scale;
}

/** Point-in-polygon test (ray casting) */
export function pointInPolygon(px: number, py: number, polygon: number[][]): boolean {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i][0], yi = polygon[i][1];
    const xj = polygon[j][0], yj = polygon[j][1];
    const intersect = ((yi > py) !== (yj > py)) &&
      (px < (xj - xi) * (py - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

/** Get the 4 corners of a rotated rectangle (in SVG space) */
export function getRotatedRectCorners(
  cx: number, cy: number,
  w: number, h: number,
  rotationDeg: number,
): [number, number][] {
  const rad = (-rotationDeg * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  const hw = w / 2;
  const hh = h / 2;
  const corners: [number, number][] = [
    [-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh],
  ];
  return corners.map(([dx, dy]) => [
    cx + dx * cos - dy * sin,
    cy + dx * sin + dy * cos,
  ]);
}
