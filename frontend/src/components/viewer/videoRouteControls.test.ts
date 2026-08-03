import { describe, expect, it } from 'vitest';

import {
  normalizedVideoPointToNdc,
  resampleVideoRoute,
  selectVideoRecorderMimeType,
} from './videoRouteControls';

describe('video route controls', () => {
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
});
