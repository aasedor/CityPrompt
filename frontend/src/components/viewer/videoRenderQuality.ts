import {
  buildDeterministicVideoFrames,
  CITY_PROMPT_VIDEO_DURATION_SECONDS,
  CITY_PROMPT_VIDEO_FPS,
} from './deterministicVideoCapture';
import * as THREE from 'three';

export type VideoRenderQuality = 'draft' | 'high';

export interface VideoRenderQualityProfile {
  id: VideoRenderQuality;
  label: string;
  detail: string;
  outputWidth: number;
  outputHeight: number;
  renderWidth: number;
  renderHeight: number;
  bitrate: number;
  tileErrorTarget: number | null;
  tileHoldMilliseconds: number;
  warmupFrameCount: number;
  warmupSettleInterval: number;
  maximumTextureAnisotropy: boolean;
}

export const VIDEO_RENDER_QUALITY_PROFILES: Readonly<Record<VideoRenderQuality, VideoRenderQualityProfile>> = {
  draft: {
    id: 'draft',
    label: 'Draft',
    detail: '720p · quick preparation',
    outputWidth: 1280,
    outputHeight: 720,
    renderWidth: 1280,
    renderHeight: 720,
    bitrate: 12_000_000,
    tileErrorTarget: null,
    tileHoldMilliseconds: 20_000,
    warmupFrameCount: 6,
    warmupSettleInterval: 1,
    maximumTextureAnisotropy: false,
  },
  high: {
    id: 'high',
    label: 'High Quality',
    detail: '1440p render → 1080p · frozen context',
    outputWidth: 1920,
    outputHeight: 1080,
    renderWidth: 2560,
    renderHeight: 1440,
    bitrate: 18_000_000,
    // At the 2560px supersampled backing resolution a 4px tile error is
    // sub-pixel after the 1080p downsample, while avoiding an endless Google
    // photogrammetry refinement stream that can never enter the idle window.
    tileErrorTarget: 4,
    tileHoldMilliseconds: 120_000,
    warmupFrameCount: CITY_PROMPT_VIDEO_DURATION_SECONDS * CITY_PROMPT_VIDEO_FPS,
    // Settle Google Tiles at 24 evenly spaced views during the 192-frame dry
    // traversal. The remaining frames still update tile selection without
    // adding a mandatory 600 ms idle window to every frame.
    warmupSettleInterval: 8,
    maximumTextureAnisotropy: true,
  },
};

export interface VideoWarmupFrame {
  index: number;
  progress: number;
  settleTiles: boolean;
}

export interface VideoCameraProjectionState {
  aspect: number;
  fov: number;
}

/**
 * Convert the live camera's center crop into a real 16:9 projection. The
 * route is resolved against the original view first; this projection then
 * makes the high-resolution backing surface geometrically identical to the
 * 16:9 frame the user drew over instead of stretching the live viewport.
 */
export function applyVideoFrameProjection(
  camera: THREE.Camera,
  sourceAspect: number,
  targetAspect = 16 / 9,
): VideoCameraProjectionState | null {
  if (!(camera instanceof THREE.PerspectiveCamera)) return null;
  const previous = { aspect: camera.aspect, fov: camera.fov };
  if (sourceAspect < targetAspect) {
    const halfVerticalFov = THREE.MathUtils.degToRad(camera.fov) / 2;
    camera.fov = THREE.MathUtils.radToDeg(
      2 * Math.atan(Math.tan(halfVerticalFov) * sourceAspect / targetAspect),
    );
  }
  camera.aspect = targetAspect;
  camera.updateProjectionMatrix();
  return previous;
}

export function restoreVideoFrameProjection(
  camera: THREE.Camera,
  previous: VideoCameraProjectionState | null,
): void {
  if (!(camera instanceof THREE.PerspectiveCamera) || !previous) return;
  camera.aspect = previous.aspect;
  camera.fov = previous.fov;
  camera.updateProjectionMatrix();
}

export function videoRenderQualityProfile(quality: VideoRenderQuality): VideoRenderQualityProfile {
  return VIDEO_RENDER_QUALITY_PROFILES[quality];
}

export function buildVideoWarmupFrames(
  profile: VideoRenderQualityProfile,
): VideoWarmupFrame[] {
  if (profile.warmupFrameCount <= 6) {
    return Array.from({ length: profile.warmupFrameCount }, (_, index) => ({
      index,
      progress: index / Math.max(1, profile.warmupFrameCount - 1),
      settleTiles: true,
    }));
  }

  return buildDeterministicVideoFrames().map((frame) => ({
    index: frame.index,
    progress: frame.progress,
    settleTiles: frame.index === 0
      || frame.index === profile.warmupFrameCount - 1
      || frame.index % profile.warmupSettleInterval === 0,
  }));
}

export function validateVideoRenderProfile(
  profile: VideoRenderQualityProfile,
  maxTextureSize: number,
): void {
  if (
    profile.renderWidth > maxTextureSize
    || profile.renderHeight > maxTextureSize
  ) {
    throw new Error(
      `${profile.label} requires a ${profile.renderWidth}×${profile.renderHeight} WebGL surface, but this GPU supports ${maxTextureSize}px. Use Draft quality on this device.`,
    );
  }
}
