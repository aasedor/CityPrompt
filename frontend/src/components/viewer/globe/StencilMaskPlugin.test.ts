import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import {
  patchMaterialForStencil,
  shouldCreateTileStencilMask,
  unpatchMaterialStencil,
} from './StencilMaskPlugin';

describe('tile stencil masking', () => {
  it('only enables masks for replacement-building zone types', () => {
    expect(shouldCreateTileStencilMask('building')).toBe(true);
    expect(shouldCreateTileStencilMask('residential')).toBe(true);
    expect(shouldCreateTileStencilMask('road')).toBe(false);
    expect(shouldCreateTileStencilMask('green_space')).toBe(false);
    expect(shouldCreateTileStencilMask(undefined)).toBe(false);
  });

  it('restores the original tile material stencil state after unpatching', () => {
    const material = new THREE.MeshBasicMaterial();
    const originalFunction = material.stencilFunc;

    patchMaterialForStencil(material);
    expect(material.stencilWrite).toBe(true);
    expect(material.stencilWriteMask).toBe(0);
    expect(material.stencilFunc).toBe(THREE.NotEqualStencilFunc);

    unpatchMaterialStencil(material);
    expect(material.stencilWrite).toBe(false);
    expect(material.stencilFunc).toBe(originalFunction);
  });
});
