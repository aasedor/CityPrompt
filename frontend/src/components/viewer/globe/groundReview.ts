import { sharedSiteGroundContains, sharedSiteGroundGridPoint, validateSharedSiteGroundPass, SHARED_SITE_GROUND_LIMITS, type SharedSiteGroundLayout } from './sharedSiteGround';

export interface GroundReview { layout: SharedSiteGroundLayout; heights: Array<number | null>; previousHeights?: Array<number | null> }
export function describeGround(review: GroundReview) {
  const { layout, heights } = review;
  // Explain the actual rejection, including triangle slopes and local residuals.
  // An independent fixed height-jump threshold hid real failures from students.
  const problemSamples = new Set<number>();
  validateSharedSiteGroundPass(layout, heights, indices => indices.forEach(index => problemSamples.add(index)));
  const cells = heights.map((height, index) => {
    const point = sharedSiteGroundGridPoint(layout, index);
    const inside = sharedSiteGroundContains(layout.boundaryCoordinates, ...point);
    const valid = height !== null && Number.isFinite(height) && height >= SHARED_SITE_GROUND_LIMITS.minHeightM && height <= SHARED_SITE_GROUND_LIMITS.maxHeightM;
    const jump = valid && problemSamples.has(index);
    return { index, point, inside, height: valid ? height : null, jump };
  });
  const values = cells.filter(c => c.inside && c.height !== null).map(c => c.height!);
  return { cells, min: values.length ? Math.min(...values) : null, max: values.length ? Math.max(...values) : null };
}

export function validPreparedLevel(value: number): boolean {
  return Number.isFinite(value) && value >= SHARED_SITE_GROUND_LIMITS.minHeightM && value <= SHARED_SITE_GROUND_LIMITS.maxHeightM;
}
