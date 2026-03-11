import type { SiteZone, SiteZoneProperties } from '@/types';

/**
 * Extract the centerline from a buffered road polygon.
 * Polygon = [left0, left1, ..., leftN, rightN, ..., right0]
 * centerline[i] = midpoint(polygon[i], polygon[n-1-i])
 */
export function extractCenterline(coords: number[][]): number[][] {
  const n = coords.length;
  const half = Math.floor(n / 2);
  if (half < 2) return coords;
  const center: number[][] = [];
  for (let i = 0; i < half; i++) {
    const a = coords[i];
    const b = coords[n - 1 - i];
    center.push([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]);
  }
  return center;
}

/**
 * Buffer a polyline into a polygon strip of given width in meters.
 * Coordinates are [lng, lat].
 */
export function bufferLineToPolygon(points: number[][], widthMeters: number): number[][] {
  if (points.length < 2) return points;
  const halfWidth = widthMeters / 2;
  const lat = points[0][1];
  const metersPerDegLat = 111320;
  const metersPerDegLon = metersPerDegLat * Math.cos((lat * Math.PI) / 180);
  const left: number[][] = [];
  const right: number[][] = [];
  for (let i = 0; i < points.length; i++) {
    let dx: number, dy: number;
    if (i === 0) {
      dx = points[1][0] - points[0][0];
      dy = points[1][1] - points[0][1];
    } else if (i === points.length - 1) {
      dx = points[i][0] - points[i - 1][0];
      dy = points[i][1] - points[i - 1][1];
    } else {
      dx = points[i + 1][0] - points[i - 1][0];
      dy = points[i + 1][1] - points[i - 1][1];
    }
    const len = Math.sqrt(dx * dx + dy * dy);
    if (len === 0) continue;
    const perpLng = (-dy / len) * (halfWidth / metersPerDegLon);
    const perpLat = (dx / len) * (halfWidth / metersPerDegLat);
    left.push([points[i][0] + perpLng, points[i][1] + perpLat]);
    right.push([points[i][0] - perpLng, points[i][1] - perpLat]);
  }
  return [...left, ...right.reverse()];
}

/**
 * Compute the effective road width from properties (width + lane minimum).
 */
export function effectiveRoadWidth(props: SiteZoneProperties | undefined): number {
  const width = (props?.width as number) || 10;
  const lanes = (props?.lane_count as number) || 2;
  return Math.max(width, lanes * 3.5);
}

/**
 * When road properties change (width / lane_count), regenerate the polygon
 * coordinates by extracting the centerline and re-buffering.
 * Call `handleZoneUpdated` with the new coordinates if they changed.
 */
export function rebufferRoadOnUpdate(
  zoneId: string,
  data: { name?: string; properties?: SiteZoneProperties },
  siteZones: SiteZone[],
  handleZoneUpdated: (zoneId: string, coordinates: number[][]) => void,
): void {
  const zone = siteZones.find((z) => z.id === zoneId);
  if (!zone || zone.zone_type !== 'road' || !data.properties) return;

  const oldEffective = effectiveRoadWidth(zone.properties);
  const newEffective = effectiveRoadWidth(data.properties);

  if (Math.abs(newEffective - oldEffective) > 0.1) {
    const centerline = extractCenterline(zone.coordinates);
    if (centerline.length >= 2) {
      const newCoords = bufferLineToPolygon(centerline, newEffective);
      handleZoneUpdated(zoneId, newCoords);
    }
  }
}
