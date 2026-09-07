import { sharedSiteGroundContains, sharedSiteGroundGridPoint, SHARED_SITE_GROUND_LIMITS, type SharedSiteGroundLayout } from './sharedSiteGround';

export interface GroundReview { layout: SharedSiteGroundLayout; heights: Array<number | null>; previousHeights?: Array<number | null> }
export function describeGround(review: GroundReview) {
  const { layout, heights } = review;
  const { columns, rows } = layout.grid;
  const cells = heights.map((height, index) => {
    const point = sharedSiteGroundGridPoint(layout, index);
    const inside = sharedSiteGroundContains(layout.boundaryCoordinates, ...point);
    const valid = height !== null && Number.isFinite(height) && height >= SHARED_SITE_GROUND_LIMITS.minHeightM && height <= SHARED_SITE_GROUND_LIMITS.maxHeightM;
    const x = index % columns, y = Math.floor(index / columns);
    const neighbors = [x > 0 ? index - 1 : -1, x < columns - 1 ? index + 1 : -1,
      y > 0 ? index - columns : -1, y < rows - 1 ? index + columns : -1]
      .filter(i => i >= 0).map(i => heights[i]).filter((h): h is number => h !== null && Number.isFinite(h));
    // A diagnostic marker, never a bare-earth classifier or replacement sample.
    const jump = valid && neighbors.some(h => Math.abs(h - height!) > 2);
    return { index, point, inside, height: valid ? height : null, jump };
  });
  const values = cells.filter(c => c.inside && c.height !== null).map(c => c.height!);
  return { cells, min: values.length ? Math.min(...values) : null, max: values.length ? Math.max(...values) : null };
}

export function validPreparedLevel(value: number): boolean {
  return Number.isFinite(value) && value >= SHARED_SITE_GROUND_LIMITS.minHeightM && value <= SHARED_SITE_GROUND_LIMITS.maxHeightM;
}
