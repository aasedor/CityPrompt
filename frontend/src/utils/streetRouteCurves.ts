/** Concept-level circular transitions for authored street centreline waypoints.
 * The requested radius is a visual/urban-design preference, not a TAC design
 * value. Engineering review still determines speed, superelevation and width. */
export function roundStreetCenterline(points: number[][], radiusM: number, spacingM = 2): number[][] {
  if (points.length < 3 || !(radiusM > 0)) return points.map(point => [...point]);
  const origin = points[0];
  const sx = 111320 * Math.cos(origin[1] * Math.PI / 180);
  const sy = 111320;
  if (!(sx > 1)) return points.map(point => [...point]);
  const metric = points.map(([lng, lat]) => [(lng - origin[0]) * sx, (lat - origin[1]) * sy]);
  return roundMetricStreetCenterline(metric, radiusM, spacingM)
    .map(([x, y]) => [origin[0] + x / sx, origin[1] + y / sy]);
}

export function roundMetricStreetCenterline(points: number[][], radiusM: number, spacingM = 2): number[][] {
  if (points.length < 3 || !(radiusM > 0)) return points.map(point => [...point]);
  const metric = points.map(([x, y]) => ({ x, y }));
  const result: number[][] = [[...points[0]]];
  const append = (x: number, y: number) => {
    const previous = result[result.length - 1];
    if (Math.hypot(x - previous[0], y - previous[1]) > 1e-5) result.push([x, y]);
  };
  for (let index = 1; index < metric.length - 1; index += 1) {
    const before = metric[index - 1], corner = metric[index], after = metric[index + 1];
    const inLength = Math.hypot(corner.x - before.x, corner.y - before.y);
    const outLength = Math.hypot(after.x - corner.x, after.y - corner.y);
    if (inLength < 1e-4 || outLength < 1e-4) { append(corner.x, corner.y); continue; }
    const ux = (corner.x - before.x) / inLength, uy = (corner.y - before.y) / inLength;
    const vx = (after.x - corner.x) / outLength, vy = (after.y - corner.y) / outLength;
    const turn = Math.acos(Math.max(-1, Math.min(1, ux * vx + uy * vy)));
    const side = Math.sign(ux * vy - uy * vx);
    // Avoid manufacturing an arc for almost-straight stations or a switchback.
    if (turn < Math.PI / 180 || turn > 5 * Math.PI / 6 || !side) {
      append(corner.x, corner.y);
      continue;
    }
    // Reserve at least 10% of each arm; adjacent bends cannot consume the
    // same segment. Short arms get a smaller, honest radius.
    const tangentM = Math.min(radiusM * Math.tan(turn / 2), .45 * inLength, .45 * outLength);
    const actualRadiusM = tangentM / Math.tan(turn / 2);
    const startX = corner.x - ux * tangentM, startY = corner.y - uy * tangentM;
    const centerX = startX - uy * side * actualRadiusM;
    const centerY = startY + ux * side * actualRadiusM;
    const startAngle = Math.atan2(startY - centerY, startX - centerX);
    append(startX, startY);
    const steps = Math.max(2, Math.ceil(actualRadiusM * turn / Math.max(.5, spacingM)));
    for (let step = 1; step <= steps; step += 1) {
      const angle = startAngle + side * turn * step / steps;
      append(centerX + Math.cos(angle) * actualRadiusM, centerY + Math.sin(angle) * actualRadiusM);
    }
  }
  const last = points[points.length - 1];
  result.push([...last]);
  return result;
}

/** A generous conceptual bend is scaled to the authored full ROW. This is not
 * a posted-speed or design-speed check. */
export function conceptStreetRadius(widthM: number, pedestrian = false): number {
  return Math.max(pedestrian ? 8 : 16, widthM * (pedestrian ? 1 : 1.5));
}

export function roundAuthoredStreetRoute(
  points: number[][],
  widthM: number,
  properties: Record<string, unknown> = {},
): number[][] {
  const identity = String(properties.road_archetype_id ?? '').toLowerCase();
  const pedestrian = properties.lane_count === 0 || /pedestrian|path|trail|promenade/.test(identity);
  return roundStreetCenterline(points, conceptStreetRadius(widthM, pedestrian));
}
