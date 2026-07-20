export interface ProjectedRenderPoint {
  x: number;
  y: number;
}

/** Conservative screen-frustum test for a projected polygon/prism. Bounding
 * boxes intentionally allow some false positives (safe prompt context) while
 * eliminating zones that are wholly outside the captured image. */
export function projectedBoundsIntersectFrame(
  points: ProjectedRenderPoint[],
  width: number,
  height: number,
  marginPx = 32,
): boolean {
  if (!(width > 0) || !(height > 0)) return false;
  const finite = points.filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y));
  if (finite.length === 0) return false;
  const margin = Number.isFinite(marginPx) ? Math.max(0, marginPx) : 0;
  let minX = Number.POSITIVE_INFINITY;
  let minY = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let maxY = Number.NEGATIVE_INFINITY;
  for (const point of finite) {
    minX = Math.min(minX, point.x);
    minY = Math.min(minY, point.y);
    maxX = Math.max(maxX, point.x);
    maxY = Math.max(maxY, point.y);
  }
  return maxX >= -margin
    && minX <= width + margin
    && maxY >= -margin
    && minY <= height + margin;
}
