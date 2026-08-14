import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import {
  classifyLegoLayerReadiness,
  hasRenderableLegoGeometry,
  indexRenderableLegoScenes,
  isCompleteLegoModuleStack,
} from './legoModuleReadiness';

function renderedScene(): THREE.Object3D {
  const scene = new THREE.Group();
  scene.add(new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1)));
  return scene;
}

describe('LEGO module readiness', () => {
  it('normalizes a singleton GLTF result for a one-file family', () => {
    const scene = renderedScene();

    expect(indexRenderableLegoScenes(['/one.glb'], { scene })).toEqual(
      new Map([['/one.glb', scene]]),
    );
  });

  it('does not admit resolved-but-empty scenes into the detailed stack', () => {
    const valid = renderedScene();
    const scenes = indexRenderableLegoScenes(
      ['/empty.glb', '/valid.glb'],
      [{ scene: new THREE.Group() }, { scene: valid }],
    );

    expect(hasRenderableLegoGeometry(new THREE.Group())).toBe(false);
    expect(scenes).toEqual(new Map([['/valid.glb', valid]]));
  });

  it('requires every planned instance before declaring the detailed stack ready', () => {
    expect(isCompleteLegoModuleStack(3, 3)).toBe(true);
    expect(isCompleteLegoModuleStack(3, 2)).toBe(false);
    expect(isCompleteLegoModuleStack(0, 0)).toBe(false);
  });

  it('keeps a visible loading fallback distinct from detailed readiness', () => {
    expect(classifyLegoLayerReadiness({
      entryCount: 3,
      visibleRepresentationCount: 3,
      detailedTargetCount: 3,
      detailedReadyCount: 1,
      temporaryFallbackCount: 2,
    })).toBe('fallback-visible');

    expect(classifyLegoLayerReadiness({
      entryCount: 3,
      visibleRepresentationCount: 3,
      detailedTargetCount: 3,
      detailedReadyCount: 3,
      temporaryFallbackCount: 0,
    })).toBe('ready');
  });
});
