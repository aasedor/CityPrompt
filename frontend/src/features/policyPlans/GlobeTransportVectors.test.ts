import { describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import { disposeTransportObjects } from './GlobeTransportVectors';

describe('transport vector resource lifetime', () => {
  it('releases hub buffers even when R3F primitive dispose=null shadows the instance method', () => {
    const geometry = new THREE.CircleGeometry(1);
    const material = new THREE.MeshBasicMaterial();
    const hubs = new THREE.InstancedMesh(geometry, material, 2);
    const geometryDisposed = vi.spyOn(geometry, 'dispose');
    const materialDisposed = vi.spyOn(material, 'dispose');
    const instancesDisposed = vi.fn();
    hubs.addEventListener('dispose', instancesDisposed);
    Object.defineProperty(hubs, 'dispose', { value: null });
    expect(() => disposeTransportObjects([hubs])).not.toThrow();
    expect(geometryDisposed).toHaveBeenCalledOnce();
    expect(materialDisposed).toHaveBeenCalledOnce();
    expect(instancesDisposed).toHaveBeenCalledOnce();
  });
});
