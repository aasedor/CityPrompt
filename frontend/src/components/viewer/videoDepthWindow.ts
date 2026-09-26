import type { VideoRouteCaptureRequest } from './videoRouteControls';

/** Distances (metres) mapped to white (near) and black (far) in the depth track. */
export interface VideoDepthWindow {
  nearMeters: number;
  farMeters: number;
}

/** Smooth grey gradients compress far below this; it is a ceiling, not a target. */
export const VIDEO_DEPTH_TRACK_BITRATE = 6_000_000;

const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));

/**
 * Choose one inverse-depth window for a whole route.
 *
 * The depth track encodes normalised inverse depth, bright = near, the same
 * convention depth-control video models are trained on. The window is fixed
 * for all 192 frames so the encoding never flickers between frames; it is
 * centred on the authored site so the buildings, parks and streets use most of
 * the 8-bit range while the far city fades to black.
 *
 * `cameraOffsetMeters` is the distance from the aerial camera to the centre of
 * the drawn route. Near-field routes sit on the ground, so they take a fixed
 * pedestrian window instead.
 */
export function videoDepthWindow(
  cameraMotion: VideoRouteCaptureRequest['cameraMotion'],
  cameraOffsetMeters: number,
): VideoDepthWindow {
  if (cameraMotion !== 'path_follow') {
    return { nearMeters: 2, farMeters: 400 };
  }
  const offset = Number.isFinite(cameraOffsetMeters) && cameraOffsetMeters > 0 ? cameraOffsetMeters : 300;
  const nearMeters = clamp(0.35 * offset, 3, 300);
  const farMeters = clamp(5 * offset, Math.max(200, nearMeters * 4), 8000);
  return { nearMeters, farMeters };
}

/** The grey level (0-1) a surface at `distanceMeters` receives inside a window. */
export function inverseDepthValue(window: VideoDepthWindow, distanceMeters: number): number {
  const invNear = 1 / window.nearMeters;
  const invFar = 1 / window.farMeters;
  const invDistance = 1 / Math.max(distanceMeters, 1e-3);
  return clamp((invDistance - invFar) / (invNear - invFar), 0, 1);
}
