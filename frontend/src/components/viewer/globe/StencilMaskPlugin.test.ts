import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import {
  createStencilVolume,
  getTileStencilVolumeHeight,
  patchMaterialForStencil,
  resolveTileStencilAnchorHeight,
  shouldCreateTileStencilMask,
  unpatchMaterialStencil,
} from './StencilMaskPlugin';

describe('tile stencil masking', () => {
  it('enables masks for replacement buildings and compiled ground surfaces', () => {
    expect(shouldCreateTileStencilMask('site_boundary')).toBe(false);
    expect(shouldCreateTileStencilMask('building')).toBe(true);
    expect(shouldCreateTileStencilMask('residential')).toBe(true);
    expect(shouldCreateTileStencilMask('road')).toBe(true);
    expect(shouldCreateTileStencilMask('green_space')).toBe(true);
    expect(shouldCreateTileStencilMask('parking')).toBe(true);
    expect(shouldCreateTileStencilMask('water')).toBe(false);
    expect(shouldCreateTileStencilMask(undefined)).toBe(false);
  });

  it('keeps the stencil cap close to the proposed building height', () => {
    expect(getTileStencilVolumeHeight('building', 10)).toBe(20);
    expect(getTileStencilVolumeHeight('residential', 32)).toBe(40);
    expect(getTileStencilVolumeHeight('building', 120)).toBe(128);
  });

  it('uses only a shallow below-grade skirt after self-seating', () => {
    const mesh = createStencilVolume(
      [{ x: 0, y: 0 }, { x: 5, y: 0 }, { x: 0, y: 5 }],
      20,
    );
    const positions = mesh?.geometry.getAttribute('position') as THREE.BufferAttribute;
    const zValues: number[] = [];
    for (let index = 2; index < positions.array.length; index += 3) {
      zValues.push(Number(positions.array[index]));
    }
    expect(Math.min(...zValues)).toBe(-6);
    mesh?.geometry.dispose();
    (mesh?.material as THREE.Material | undefined)?.dispose();
  });

  it('self-seats across elevation datums while rejecting roofs and root tiles', () => {
    expect(resolveTileStencilAnchorHeight([1016, 1017, 1018], null, 1045)).toBe(1016);
    expect(resolveTileStencilAnchorHeight([1145, 1146, 1160, 1162], null, 1045)).toBe(1145);
    expect(resolveTileStencilAnchorHeight([-28090, -28080], null, 1045)).toBe(1045);
    expect(resolveTileStencilAnchorHeight([null, undefined], 1032, 1045)).toBe(1032);
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
