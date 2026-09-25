import { describe, expect, it } from 'vitest';
import { advanceWalkPose, lookWalkPose, type WalkPose } from './walkNavigation';

const start: WalkPose = { lng: -114, lat: 51, groundHeight: 1045, heading: 0 };

describe('walking camera controls', () => {
  it('moves north at pedestrian speed and keeps eye-level ground fixed', () => {
    const next = advanceWalkPose(start, new Set(['w']), 0.05);
    expect((next.lat - start.lat) * 111_320).toBeCloseTo(0.11, 3);
    expect(next.lng).toBe(start.lng);
    expect(next.groundHeight).toBe(start.groundHeight);
  });

  it('strafe follows the camera heading without changing it', () => {
    const east = { ...start, heading: 90 };
    const next = advanceWalkPose(east, new Set(['d']), 0.05);
    expect(next.lat).toBeLessThan(east.lat);
    expect(next.heading).toBe(90);
  });

  it('turns in small steps and wraps the compass heading', () => {
    const next = advanceWalkPose({ ...start, heading: 359 }, new Set(['arrowright']), 0.05);
    expect(next.heading).toBe(4);
    expect(lookWalkPose(next, -50).heading).toBe(355);
  });
});
