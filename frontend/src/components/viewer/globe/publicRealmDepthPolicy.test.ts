import { describe, expect, it } from 'vitest';

import {
  PUBLIC_REALM_DECAL_DEPTH,
  PUBLIC_REALM_DETAIL_DEPTH,
  PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS,
  PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS,
  resolvePublicRealmGroundDepthPolicy,
} from './publicRealmDepthPolicy';

describe('public-realm depth policy', () => {
  it('always tests proposal ground against tiles and buildings', () => {
    for (const isCompiledGround of [false, true]) {
      for (const hasAuthoredGroundTexture of [false, true]) {
        const policy = resolvePublicRealmGroundDepthPolicy({
          isCompiledGround,
          hasAuthoredGroundTexture,
          isPreparedBoundary: false,
          isSiteBoundary: false,
        });
        expect(policy.depthTest).toBe(true);
      }
    }
  });

  it('makes compiled and textured ground opaque depth-writing geometry without requiring a tile mask', () => {
    expect(resolvePublicRealmGroundDepthPolicy({
      isCompiledGround: true,
      hasAuthoredGroundTexture: false,
      isPreparedBoundary: false,
      isSiteBoundary: false,
    })).toEqual({ depthTest: true, depthWrite: true, transparent: false });

    expect(resolvePublicRealmGroundDepthPolicy({
      isCompiledGround: false,
      hasAuthoredGroundTexture: true,
      isPreparedBoundary: false,
      isSiteBoundary: false,
    }).depthWrite).toBe(true);
  });

  it('keeps only the planning site boundary transparent and non-occluding', () => {
    expect(resolvePublicRealmGroundDepthPolicy({
      isCompiledGround: false,
      hasAuthoredGroundTexture: false,
      isPreparedBoundary: true,
      isSiteBoundary: true,
    })).toEqual({ depthTest: true, depthWrite: false, transparent: true });
  });

  it('depth-tests physical street detail and decal layers', () => {
    expect(PUBLIC_REALM_DETAIL_DEPTH).toEqual({ depthTest: true, depthWrite: true });
    expect(PUBLIC_REALM_DECAL_DEPTH).toEqual({ depthTest: true, depthWrite: false });
  });

  it('seats fixed modules just above the shared authored-ground lift', () => {
    expect(PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS).toBe(0.08);
    expect(PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS).toBeCloseTo(0.1, 8);
    expect(PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS - PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS)
      .toBeLessThanOrEqual(0.02 + Number.EPSILON);
  });
});
