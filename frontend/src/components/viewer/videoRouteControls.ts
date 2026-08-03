export type VideoControlMode = 'single_frame' | 'multi_keyframe' | 'preview_video';

export interface NormalizedVideoRoutePoint {
  x: number;
  y: number;
}

export interface VideoRouteCaptureRequest {
  routePoints: NormalizedVideoRoutePoint[];
  cameraMotion: 'path_follow' | 'street_walkby';
  durationSeconds: 8;
  keyframeCount?: number;
}

export interface VideoRouteCaptureResult {
  keyframesBase64: string[];
  previewVideoBase64: string;
  previewVideoMimeType: string;
}

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));

/** Sample a hand-drawn route at equal travelled-distance intervals. */
export function resampleVideoRoute(
  points: NormalizedVideoRoutePoint[],
  count = 6,
): NormalizedVideoRoutePoint[] {
  if (points.length < 2) throw new Error('A video route needs a start and finish.');
  if (count < 2) throw new Error('A video route needs at least two control frames.');

  const distances = [0];
  for (let index = 1; index < points.length; index += 1) {
    const previous = points[index - 1];
    const current = points[index];
    distances.push(distances[index - 1] + Math.hypot(current.x - previous.x, current.y - previous.y));
  }
  const total = distances[distances.length - 1];
  if (total <= 1e-6) throw new Error('Draw a longer video route before preparing controls.');

  return Array.from({ length: count }, (_, sampleIndex) => {
    const target = (sampleIndex / (count - 1)) * total;
    let segment = 1;
    while (segment < distances.length - 1 && distances[segment] < target) segment += 1;
    const segmentStart = distances[segment - 1];
    const segmentLength = Math.max(1e-9, distances[segment] - segmentStart);
    const mix = (target - segmentStart) / segmentLength;
    const start = points[segment - 1];
    const finish = points[segment];
    return {
      x: clamp01(start.x + (finish.x - start.x) * mix),
      y: clamp01(start.y + (finish.y - start.y) * mix),
    };
  });
}

/**
 * Convert a point drawn on the normalized 16:9 capture back into the source
 * WebGL viewport's NDC. Video frames are center-cropped, so the crop has to be
 * reversed before raycasting against Google Tiles.
 */
export function normalizedVideoPointToNdc(
  point: NormalizedVideoRoutePoint,
  sourceAspect: number,
  frameAspect = 16 / 9,
): { x: number; y: number } {
  let sourceX = clamp01(point.x);
  let sourceY = clamp01(point.y);

  if (sourceAspect > frameAspect) {
    const visibleFraction = frameAspect / sourceAspect;
    sourceX = (1 - visibleFraction) / 2 + sourceX * visibleFraction;
  } else if (sourceAspect < frameAspect) {
    const visibleFraction = sourceAspect / frameAspect;
    sourceY = (1 - visibleFraction) / 2 + sourceY * visibleFraction;
  }

  return {
    x: sourceX * 2 - 1,
    y: 1 - sourceY * 2,
  };
}

export function selectVideoRecorderMimeType(
  isTypeSupported: (mimeType: string) => boolean,
): string {
  return [
    'video/webm;codecs=vp9',
    'video/webm;codecs=vp8',
    'video/webm',
  ].find(isTypeSupported) ?? '';
}
