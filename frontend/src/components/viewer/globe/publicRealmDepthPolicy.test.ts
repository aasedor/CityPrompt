import { describe, expect, it } from 'vitest';

import {
  PUBLIC_REALM_DECAL_DEPTH,
  PUBLIC_REALM_DETAIL_DEPTH,
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
});
