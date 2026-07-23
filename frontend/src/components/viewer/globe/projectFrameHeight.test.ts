import { describe, expect, it } from 'vitest';
import {
  estimateProjectFrameHeight,
  PROJECT_FRAME_MIN_HEIGHT_M,
} from './projectFrameHeight';

describe('project camera framing height', () => {
  it('frames a kilometre-scale district substantially closer than the legacy multiplier', () => {
    const height = estimateProjectFrameHeight(1_100);
    expect(height).toBeGreaterThan(400);
    expect(height).toBeLessThan(650);
    expect(height).toBeLessThan(1_100 * 1.6);
  });

  it('frames a small hero park at the close-site safety floor', () => {
    expect(estimateProjectFrameHeight(146)).toBe(PROJECT_FRAME_MIN_HEIGHT_M);
    expect(PROJECT_FRAME_MIN_HEIGHT_M).toBe(70);
  });

  it('backs away monotonically for larger extents and tighter frame targets', () => {
    expect(estimateProjectFrameHeight(2_000)).toBeGreaterThan(
      estimateProjectFrameHeight(1_000),
    );
    expect(estimateProjectFrameHeight(1_000, 75, 60, 0.4)).toBeGreaterThan(
      estimateProjectFrameHeight(1_000, 75, 60, 0.7),
    );
  });
});
