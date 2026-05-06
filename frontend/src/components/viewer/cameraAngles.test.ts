import { describe, expect, it } from 'vitest';
import {
  describeCameraAngleForPrompt,
  getAngleFromNadirLabelValue,
  getCameraElevationBadge,
  pitchFromNadirToCameraElevation,
} from './cameraAngles';

describe('camera angle convention helpers', () => {
  it('converts pitch from nadir to camera elevation', () => {
    expect(pitchFromNadirToCameraElevation(0)).toBe(90);
    expect(pitchFromNadirToCameraElevation(45)).toBe(45);
    expect(pitchFromNadirToCameraElevation(90)).toBe(0);
  });

  it('clamps out-of-range pitch values', () => {
    expect(pitchFromNadirToCameraElevation(-10)).toBe(90);
    expect(pitchFromNadirToCameraElevation(100)).toBe(0);
    expect(getAngleFromNadirLabelValue(100)).toBe(90);
  });

  it('labels display bands using camera elevation', () => {
    expect(getCameraElevationBadge(90).label).toBe('overhead');
    expect(getCameraElevationBadge(45).label).toBe('oblique');
    expect(getCameraElevationBadge(0).label).toBe('ground');
  });

  it('includes both angle conventions in prompt descriptions', () => {
    expect(describeCameraAngleForPrompt(0)).toContain('~90deg camera elevation');
    expect(describeCameraAngleForPrompt(0)).toContain('~0deg from nadir');
    expect(describeCameraAngleForPrompt(90)).toContain('~0deg camera elevation');
    expect(describeCameraAngleForPrompt(90)).toContain('~90deg from nadir');
  });
});
