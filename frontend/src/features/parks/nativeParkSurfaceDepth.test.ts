import { describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import { cloneNativeParkScene } from './nativeParkSurfaceDepth';

describe('native park coplanar finishes', () => {
  it.each(['paving', 'soil'])('prioritizes zero-height %s while preserving original geometry and material appearance', name => {
    const source = new THREE.Group();
    const finish = new THREE.MeshStandardMaterial({ name, color: '#b4a58c', roughness: .9 });
    const sourceCompile = vi.fn();
    finish.onBeforeCompile = sourceCompile;
    const geometry = new THREE.PlaneGeometry(20, 30).rotateX(-Math.PI / 2);
    const paving = new THREE.Mesh(geometry, finish);
    const base = new THREE.Mesh(new THREE.BoxGeometry(30, .2, 44), new THREE.MeshStandardMaterial({ name: 'edge' }));
    base.position.y = -.1;
    source.add(base, paving);
    const copy = cloneNativeParkScene(source);
    const clone = copy.children[1] as THREE.Mesh;
    const material = clone.material as THREE.MeshStandardMaterial;
    expect(clone.geometry).toBe(geometry);
    expect(clone.position).toEqual(paving.position);
    expect(material).not.toBe(finish);
    expect(material.color).toEqual(finish.color);
    expect(material.roughness).toBe(finish.roughness);
    expect(material.polygonOffset).toBe(true);
    expect(material.polygonOffsetFactor).toBeLessThan(0);
    expect(material.depthTest).toBe(true);
    expect(finish.polygonOffset).toBe(false);
    const shader = { fragmentShader: THREE.ShaderLib.standard.fragmentShader } as Parameters<THREE.Material['onBeforeCompile']>[0];
    material.onBeforeCompile(shader, {} as THREE.WebGLRenderer);
    expect(sourceCompile).toHaveBeenCalledOnce();
    expect(shader.fragmentShader).toContain('#include <logdepthbuf_fragment>');
    expect(shader.fragmentShader).toContain('gl_FragDepth - 0.000001');
    expect(shader.fragmentShader).toContain('#if defined( USE_LOGDEPTHBUF )');
    expect(material.customProgramCacheKey()).not.toBe(finish.customProgramCacheKey());
    expect((copy.children[0] as THREE.Mesh).material).toBe(base.material);
    expect((cloneNativeParkScene(source).children[1] as THREE.Mesh).material).toBe(material);
  });

  it('leaves raised paving, solid stairs and unrelated ground materials unchanged', () => {
    const source = new THREE.Group();
    const plane = new THREE.PlaneGeometry(3, 3).rotateX(-Math.PI / 2);
    const raised = new THREE.Mesh(plane, new THREE.MeshStandardMaterial({ name: 'paving' }));
    raised.position.y = .22;
    const stair = new THREE.Mesh(new THREE.BoxGeometry(3, 1, 3), new THREE.MeshStandardMaterial({ name: 'paving' }));
    const grass = new THREE.Mesh(plane, new THREE.MeshStandardMaterial({ name: 'grass' }));
    source.add(raised, stair, grass);
    const copy = cloneNativeParkScene(source);
    copy.children.forEach((mesh, i) => expect((mesh as THREE.Mesh).material).toBe((source.children[i] as THREE.Mesh).material));
  });
});
