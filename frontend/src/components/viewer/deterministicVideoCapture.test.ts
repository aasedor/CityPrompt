import { describe, expect, it } from 'vitest';

import {
  buildDeterministicVideoFrames,
  CITY_PROMPT_VIDEO_FRAME_COUNT,
  getCenterCropRect,
} from './deterministicVideoCapture';

describe('deterministic video frame clock', () => {
  it('creates exactly 192 ordered frames for an eight-second 24 fps render', () => {
    const frames = buildDeterministicVideoFrames();

    expect(frames).toHaveLength(CITY_PROMPT_VIDEO_FRAME_COUNT);
    expect(frames[0]).toEqual({
      index: 0,
      progress: 0,
      timestampMicroseconds: 0,
      durationMicroseconds: 41_667,
    });
    expect(frames[frames.length - 1]?.index).toBe(191);
    expect(frames[frames.length - 1]?.progress).toBe(1);
    expect(frames[frames.length - 1]?.timestampMicroseconds).toBe(7_958_333);
  });

  it('uses index-based path progress even when capture takes longer than playback', () => {
    const frames = buildDeterministicVideoFrames(2, 4);

    expect(frames.map((frame) => frame.progress)).toEqual([
      0,
      1 / 7,
      2 / 7,
      3 / 7,
      4 / 7,
      5 / 7,
      6 / 7,
      1,
    ]);
    expect(frames.map((frame) => frame.timestampMicroseconds)).toEqual([
      0,
      250_000,
      500_000,
      750_000,
      1_000_000,
      1_250_000,
      1_500_000,
      1_750_000,
    ]);
  });
});

describe('video center crop', () => {
  it('crops a wide source at the sides', () => {
    expect(getCenterCropRect(1920, 800)).toEqual({
      sx: 248.8888888888889,
      sy: 0,
      sw: 1422.2222222222222,
      sh: 800,
    });
  });

  it('crops a tall source at the top and bottom', () => {
    expect(getCenterCropRect(1000, 1000)).toEqual({
      sx: 0,
      sy: 218.75,
      sw: 1000,
      sh: 562.5,
    });
  });
});
