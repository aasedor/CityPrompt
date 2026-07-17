import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { disposeArchitecturalCloneMaterials, prepareArchitecturalClone } from './modelMaterialQuality';

describe('prepareArchitecturalClone', () => {
  it('clones cached materials and gives glass a coated architectural response', () => {
    const source = new THREE.Group();
    const sourceMaterial = new THREE.MeshStandardMaterial({ roughness: 0.7 });
    sourceMaterial.name = 'MAT_Glass';
    source.add(new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), sourceMaterial));

    const clone = prepareArchitecturalClone(source, { renderOrder: 150 });
    const clonedMesh = clone.children[0] as THREE.Mesh;
    const clonedMaterial = clonedMesh.material as THREE.MeshStandardMaterial;

    expect(clonedMaterial).not.toBe(sourceMaterial);
    expect(clonedMaterial.roughness).toBeLessThanOrEqual(0.18);
    expect(clonedMaterial.envMapIntensity).toBe(1.25);
    expect(sourceMaterial.roughness).toBe(0.7);
    expect(clonedMesh.castShadow).toBe(true);
    expect(clonedMesh.renderOrder).toBe(150);
  });

  it('increases texture anisotropy on PBR maps', () => {
    const texture = new THREE.Texture();
    const sourceMaterial = new THREE.MeshStandardMaterial({ map: texture });
    const source = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), sourceMaterial);

    const clone = prepareArchitecturalClone(source, {
      renderOrder: 10,
      maxAnisotropy: 12,
      restyleUntextured: true,
    }) as THREE.Mesh;

    expect(texture.anisotropy).toBe(12);
    expect((clone.material as THREE.MeshStandardMaterial).envMapIntensity).toBe(0.9);
  });

  it('uses the photo-baked calibration for facade-sheet materials', () => {
    const albedo = new THREE.Texture();
    const roughness = new THREE.Texture();
    const ao = new THREE.Texture();
    const sourceMaterial = new THREE.MeshStandardMaterial({
      map: albedo,
      roughnessMap: roughness,
      aoMap: ao,
      metalness: 0.4,
    });
    sourceMaterial.name = 'MAT_Sheet_Floor';
    const source = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), sourceMaterial);

    const clone = prepareArchitecturalClone(source, { renderOrder: 150 }) as THREE.Mesh;
    const material = clone.material as THREE.MeshStandardMaterial;

    expect(material.envMapIntensity).toBe(0.18);
    expect(material.aoMap).toBeNull();
    expect(material.roughnessMap).toBeNull();
    expect(material.roughness).toBe(1);
    expect(material.metalness).toBe(0);
    expect(material.color.r).toBeCloseTo(0.5);
    expect(material.map?.colorSpace).toBe(THREE.SRGBColorSpace);
  });

  it('disposes clone-owned materials without disposing cached geometry or textures', () => {
    const texture = new THREE.Texture();
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const source = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ map: texture }));
    const clone = prepareArchitecturalClone(source, { renderOrder: 10 }) as THREE.Mesh;
    const material = clone.material as THREE.Material;
    let materialDisposed = false;
    let textureDisposed = false;
    let geometryDisposed = false;
    material.addEventListener('dispose', () => { materialDisposed = true; });
    texture.addEventListener('dispose', () => { textureDisposed = true; });
    geometry.addEventListener('dispose', () => { geometryDisposed = true; });

    disposeArchitecturalCloneMaterials(clone);

    expect(materialDisposed).toBe(true);
    expect(textureDisposed).toBe(false);
    expect(geometryDisposed).toBe(false);
  });
});
