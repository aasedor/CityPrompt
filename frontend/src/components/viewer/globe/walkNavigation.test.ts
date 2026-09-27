import { describe, expect, it } from 'vitest';
import { advanceWalkPose, lookWalkPose, walkEntryHeading, type WalkPose } from './walkNavigation';

const start: WalkPose = { lng: -114, lat: 51, groundHeight: 1045, heading: 0 };

describe('walking camera controls', () => {
  it('starts overhead Walk toward map-up despite tiny forward-direction noise', () => {
    expect(walkEntryHeading({ east: 1e-10, north: 0 }, { east: 0, north: 1 })).toBe(0);
    expect(walkEntryHeading({ east: -1e-10, north: 0 }, { east: 1, north: 0 })).toBe(90);
  });

  it('preserves the visible forward bearing when entering from an oblique view', () => {
    expect(walkEntryHeading({ east: -0.7, north: 0 }, { east: 0, north: 1 })).toBe(270);
    expect(walkEntryHeading({ east: 0, north: 0 }, { east: 0, north: 0 })).toBe(0);
  });

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
