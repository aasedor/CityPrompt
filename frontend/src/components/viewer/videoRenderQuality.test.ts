import { describe, expect, it } from 'vitest';

import {
  applyVideoFrameProjection,
  buildVideoWarmupFrames,
  restoreVideoFrameProjection,
  validateVideoRenderProfile,
  videoRenderQualityProfile,
} from './videoRenderQuality';
import * as THREE from 'three';

describe('Video Render quality profiles', () => {
  it('renders High Quality above delivery resolution and retains all 192 route poses', () => {
    const profile = videoRenderQualityProfile('high');
    const warmup = buildVideoWarmupFrames(profile);

    expect(profile.renderWidth).toBe(2560);
    expect(profile.renderHeight).toBe(1440);
    expect(profile.outputWidth).toBe(1920);
    expect(profile.outputHeight).toBe(1080);
    expect(profile.tileErrorTarget).toBe(4);
    expect(warmup).toHaveLength(192);
    expect(warmup[0]).toEqual({ index: 0, progress: 0, settleTiles: true });
    expect(warmup[warmup.length - 1]).toEqual({ index: 191, progress: 1, settleTiles: true });
    expect(warmup.filter((frame) => frame.settleTiles)).toHaveLength(25);
  });

  it('keeps Draft bounded to six settled preload views', () => {
    const warmup = buildVideoWarmupFrames(videoRenderQualityProfile('draft'));

    expect(warmup).toHaveLength(6);
    expect(warmup.every((frame) => frame.settleTiles)).toBe(true);
  });

  it('rejects a quality profile larger than the available WebGL surface', () => {
    expect(() => validateVideoRenderProfile(videoRenderQualityProfile('high'), 2048)).toThrow(
      /Use Draft quality/,
    );
    expect(() => validateVideoRenderProfile(videoRenderQualityProfile('high'), 4096)).not.toThrow();
  });

  it('turns the displayed center crop into a true 16:9 camera projection', () => {
    const wide = new THREE.PerspectiveCamera(60, 2, 0.1, 1000);
    const wideState = applyVideoFrameProjection(wide, 2);
    expect(wide.aspect).toBeCloseTo(16 / 9);
    expect(wide.fov).toBeCloseTo(60);
    restoreVideoFrameProjection(wide, wideState);
    expect(wide.aspect).toBe(2);
    expect(wide.fov).toBe(60);

    const tall = new THREE.PerspectiveCamera(60, 4 / 3, 0.1, 1000);
    applyVideoFrameProjection(tall, 4 / 3);
    expect(tall.aspect).toBeCloseTo(16 / 9);
    expect(tall.fov).toBeLessThan(60);
  });
});
