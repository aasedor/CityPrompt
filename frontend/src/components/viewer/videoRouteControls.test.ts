import { describe, expect, it } from 'vitest';

import {
  cinematicRouteProgress,
  normalizedVideoPointToNdc,
  resampleVideoRoute,
  selectVideoRecorderMimeType,
  stableNearFieldTerrainHeight,
  videoRouteSurfaceHeight,
  videoGeometryPassProfile,
  type VideoRouteCaptureResult,
} from './videoRouteControls';

describe('video route controls', () => {
  it('does not claim geometry bundles for a beauty-only draft video', () => {
    expect(videoGeometryPassProfile([], 192)).toEqual({
      checkpointCount: 0, semanticCheckpointCount: 0, instanceCheckpointCount: 0,
      depthCheckpointCount: 0, normalCheckpointCount: 0, materialCheckpointCount: 0,
      motionFrameCount: 192,
    });
  });

  it('counts only the complete checkpoint bundles accompanying the video', () => {
    const checkpoint = {} as NonNullable<VideoRouteCaptureResult['geometryCheckpoints']>[number];
    const profile = videoGeometryPassProfile([checkpoint, checkpoint], 192);
    expect(profile.checkpointCount).toBe(2);
    expect(profile.semanticCheckpointCount).toBe(profile.depthCheckpointCount);
    expect(profile.materialCheckpointCount).toBe(2);
  });
  it('eases camera motion into the route and into the final hold', () => {
    expect(cinematicRouteProgress(-1)).toBe(0);
    expect(cinematicRouteProgress(0)).toBe(0);
    expect(cinematicRouteProgress(0.25)).toBeCloseTo(0.15625);
    expect(cinematicRouteProgress(0.5)).toBe(0.5);
    expect(cinematicRouteProgress(0.75)).toBeCloseTo(0.84375);
    expect(cinematicRouteProgress(1)).toBe(1);
    expect(cinematicRouteProgress(2)).toBe(1);
  });

  it('resamples a drawn path by travelled distance and preserves its endpoints', () => {
    const samples = resampleVideoRoute([
      { x: 0.1, y: 0.2 },
      { x: 0.5, y: 0.2 },
      { x: 0.5, y: 0.8 },
    ], 6);

    expect(samples).toHaveLength(6);
    expect(samples[0]).toEqual({ x: 0.1, y: 0.2 });
    expect(samples[5]).toEqual({ x: 0.5, y: 0.8 });
    expect(samples[2].x).toBeCloseTo(0.5);
  });

  it('reverses the center crop before converting route points to NDC', () => {
    expect(normalizedVideoPointToNdc({ x: 0.5, y: 0.5 }, 16 / 9)).toEqual({ x: 0, y: 0 });
    expect(normalizedVideoPointToNdc({ x: 0, y: 0.5 }, 2).x).toBeCloseTo(-8 / 9);
    expect(normalizedVideoPointToNdc({ x: 0.5, y: 0 }, 4 / 3).y).toBeCloseTo(0.75);
  });

  it('selects the best browser recorder codec with safe fallbacks', () => {
    expect(selectVideoRecorderMimeType((mime) => mime.includes('vp8'))).toBe('video/webm;codecs=vp8');
    expect(selectVideoRecorderMimeType(() => false)).toBe('');
  });

  it('keeps pedestrian and low-drone routes on terrain instead of roofs', () => {
    expect(videoRouteSurfaceHeight(1045, 1002, 'street_walkby')).toBe(1002);
    expect(videoRouteSurfaceHeight(1045, 1002, 'detail_flythrough')).toBe(1002);
    expect(videoRouteSurfaceHeight(1045, 1002, 'path_follow')).toBe(1045);
    expect(stableNearFieldTerrainHeight([990, 1000, 1001, 1045, 1046, 1047])).toBe(1000);
  });
});
