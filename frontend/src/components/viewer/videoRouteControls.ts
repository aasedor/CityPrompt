import type { StreetRenderReadiness } from './globe/streetRenderReadiness';
import type { VideoRenderQuality } from './videoRenderQuality';
import type {
  Direct3DCameraManifest,
  Direct3DInstanceDescriptor,
  Direct3DMaterialDescriptor,
  Direct3DProposalRole,
} from './globe/direct3dCapture';

export type VideoControlMode = 'single_frame' | 'multi_keyframe' | 'preview_video';

export interface NormalizedVideoRoutePoint {
  x: number;
  y: number;
}

export interface VideoRouteCaptureRequest {
  routePoints: NormalizedVideoRoutePoint[];
  cameraMotion: 'path_follow' | 'street_walkby' | 'detail_flythrough';
  renderQuality: VideoRenderQuality;
  durationSeconds: 8;
  keyframeCount?: number;
}

export interface VideoRouteCaptureResult {
  keyframesBase64: string[];
  previewVideoBase64: string;
  previewVideoMimeType: string;
  geometryCheckpoints?: Array<{
    progress: number;
    beautyImageBase64: string;
    classIdImageBase64: string;
    classIdManifest: Readonly<Record<string, Direct3DProposalRole>>;
    instanceIdImageBase64: string;
    instanceIdManifest: Readonly<Record<string, Direct3DInstanceDescriptor>>;
    depthImageBase64: string;
    normalImageBase64: string;
    materialIdImageBase64: string;
    materialIdManifest: Readonly<Record<string, Direct3DMaterialDescriptor>>;
    camera: Direct3DCameraManifest;
  }>;
  previewCaptureProfile?: {
    encoder: 'webcodecs_h264' | 'media_recorder_webm';
    frameCount: number;
    fps: number;
    width: number;
    height: number;
    renderWidth?: number;
    renderHeight?: number;
    tileWarmupFrameCount?: number;
    tileSetHeld?: boolean;
    fixedTimestep: true;
  };
  geometryPassProfile?: {
    checkpointCount: number;
    semanticCheckpointCount: number;
    instanceCheckpointCount: number;
    depthCheckpointCount: number;
    normalCheckpointCount: number;
    materialCheckpointCount: number;
    motionFrameCount: number;
  };
  streetRenderReadiness?: StreetRenderReadiness;
}

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));

/**
 * Convert timeline progress to a restrained ease-in/ease-out camera move.
 * Smoothstep keeps the authored endpoints and midpoint exact while removing
 * the abrupt start and stop of constant-speed spline traversal.
 */
export function cinematicRouteProgress(progress: number): number {
  const time = clamp01(progress);
  return time * time * (3 - 2 * time);
}

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

/** Near-field paths must follow the project's terrain surface, not the first
 * Google-mesh intersection under the cursor. That topmost hit may be a roof,
 * tree canopy, vehicle, or photogrammetry spike and would place a pedestrian
 * or low drone inside geometry. Aerial routes intentionally retain the hit
 * height because roof-to-roof target motion is valid at a high orbit offset. */
export function videoRouteSurfaceHeight(
  hitHeight: number,
  terrainHeight: number,
  cameraMotion: VideoRouteCaptureRequest['cameraMotion'],
): number {
  return cameraMotion === 'path_follow' ? hitHeight : terrainHeight;
}

/** A low quantile rejects an isolated photogrammetry void without allowing
 * roofs/canopies to pull the whole near-field path upward. The user is still
 * expected to click visible ground, so the second-lowest of six route samples
 * is a conservative and stable local terrain estimate. */
export function stableNearFieldTerrainHeight(hitHeights: number[]): number {
  const sorted = hitHeights.filter(Number.isFinite).sort((a, b) => a - b);
  if (sorted.length === 0) throw new Error('The video route has no usable terrain heights.');
  return sorted[Math.floor((sorted.length - 1) * 0.2)];
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
