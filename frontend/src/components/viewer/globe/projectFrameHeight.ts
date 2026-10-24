const DEG_TO_RAD = Math.PI / 180;

/** Include saved height edits when framing an authored native building. */
export function projectFrameRoofHeight({ nativeHeight, heightM, floorCount, isBuilding }: {
  nativeHeight?: number; heightM?: unknown; floorCount?: unknown; isBuilding: boolean;
}): number {
  const native = typeof nativeHeight === 'number' && Number.isFinite(nativeHeight) ? Math.max(0, nativeHeight) : 0;
  if (!isBuilding) return native;
  const edited = Number(heightM);
  const floors = Number(floorCount);
  return Math.max(native, Number.isFinite(edited) && edited > 0
    ? edited : Number.isFinite(floors) ? Math.max(0, floors * 4) : 0);
}

/** Symmetric extent around the optical centre, including an off-centre roof. */
export function projectedFrameFraction(points: Array<{ x: number; y: number }>, width: number, height: number): number {
  return Math.max(...points.map(p => Math.max(Math.abs(2 * p.x / width - 1), Math.abs(2 * p.y / height - 1))));
}

// Keep a single-site plan visually legible. The previous 55% / 120 m floor
// framed a 150 m parcel like a district overview, making low park structures
// effectively disappear. Larger master plans still scale from their measured
// extent and automatically back away.
export const PROJECT_FRAME_TARGET_FRACTION = 0.7;
export const PROJECT_FRAME_MIN_HEIGHT_M = 70;
export const PROJECT_FRAME_MAX_HEIGHT_M = 20_000;

/**
 * Estimate a useful first camera height for a ground-plane extent.
 *
 * The globe camera is displaced horizontally by `height * tan(pitch)` before
 * looking back at the site, so its slant range is `height / cos(pitch)`. The
 * old `span * 1.6` seed ignored both that range and the 75-degree perspective
 * frustum; kilometre-scale plans opened as a tiny patch and the later
 * projection loop did not visually recover before the controls settled.
 */
export function estimateProjectFrameHeight(
  spanM: number,
  verticalFovDeg = 75,
  pitchFromNadirDeg = 60,
  targetFraction = PROJECT_FRAME_TARGET_FRACTION,
): number {
  const safeSpan = Math.max(30, Number.isFinite(spanM) ? spanM : 30);
  const safeFov = Math.min(150, Math.max(10, verticalFovDeg));
  const safePitch = Math.min(80, Math.max(0, pitchFromNadirDeg));
  const safeTarget = Math.min(0.9, Math.max(0.2, targetFraction));
  const pitchCos = Math.max(0.01, Math.cos(safePitch * DEG_TO_RAD));
  const slantPerHeight = 1 / pitchCos;
  const visibleSpanPerHeight = (
    2
    * slantPerHeight
    * Math.tan((safeFov * DEG_TO_RAD) / 2)
    * safeTarget
  );
  // A ground extent parallel to the viewing direction is foreshortened in an
  // oblique view, while the cross-view extent is not. The square root is the
  // orientation-neutral midpoint between those two projections; a small
  // safety margin then keeps labels and extruded roofs away from the frame.
  const groundProjectionFactor = Math.sqrt(pitchCos);
  const height = (
    safeSpan
    * groundProjectionFactor
    * 1.15
  ) / Math.max(0.01, visibleSpanPerHeight);
  return Math.min(
    PROJECT_FRAME_MAX_HEIGHT_M,
    Math.max(PROJECT_FRAME_MIN_HEIGHT_M, height),
  );
}
