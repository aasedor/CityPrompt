export interface VideoRoutePoint {
  x: number;
  y: number;
}

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));

export function normalizedRoutePoint(
  clientX: number,
  clientY: number,
  rect: Pick<DOMRect, 'left' | 'top' | 'width' | 'height'>,
): VideoRoutePoint {
  return {
    x: clamp01((clientX - rect.left) / Math.max(1, rect.width)),
    y: clamp01((clientY - rect.top) / Math.max(1, rect.height)),
  };
}

export function appendRoutePoint(
  points: VideoRoutePoint[],
  point: VideoRoutePoint,
  minimumDistance = 0.012,
): VideoRoutePoint[] {
  const previous = points[points.length - 1];
  if (previous && Math.hypot(point.x - previous.x, point.y - previous.y) < minimumDistance) return points;
  return [...points, point];
}

/** Keep route shape while limiting prompt/API payload complexity. */
export function resampleRoute(points: VideoRoutePoint[], maxPoints = 12): VideoRoutePoint[] {
  if (points.length <= maxPoints) return points;
  const result: VideoRoutePoint[] = [];
  for (let index = 0; index < maxPoints; index += 1) {
    const sourceIndex = Math.round((index / (maxPoints - 1)) * (points.length - 1));
    result.push(points[sourceIndex]);
  }
  return result;
}

export function routeSignature(points: VideoRoutePoint[]): string {
  return points.map((point) => `${point.x.toFixed(4)},${point.y.toFixed(4)}`).join('|');
}

export function routeSvgPoints(points: VideoRoutePoint[]): string {
  return points.map((point) => `${(point.x * 100).toFixed(2)},${(point.y * 100).toFixed(2)}`).join(' ');
}

export const DEFAULT_VIDEO_ROUTE: VideoRoutePoint[] = [
  { x: 0.52, y: 0.62 },
  { x: 0.515, y: 0.58 },
  { x: 0.51, y: 0.54 },
  { x: 0.505, y: 0.50 },
  { x: 0.50, y: 0.46 },
];

/** Short pedestrian-height move parallel to the visible frontage. */
export const DEFAULT_STREET_VIDEO_ROUTE: VideoRoutePoint[] = [
  { x: 0.40, y: 0.66 },
  { x: 0.45, y: 0.65 },
  { x: 0.50, y: 0.65 },
  { x: 0.55, y: 0.64 },
  { x: 0.60, y: 0.64 },
];
