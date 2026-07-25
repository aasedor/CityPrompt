import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import {
  disposeArchitecturalCloneMaterials,
  prepareArchitecturalClone,
  resolveArchitecturalGlazingLod,
  setArchitecturalGlazingLod,
} from './modelMaterialQuality';

describe('prepareArchitecturalClone', () => {
  it('clones cached materials and gives glass a coated architectural response', () => {
    const source = new THREE.Group();
    const sourceMaterial = new THREE.MeshPhysicalMaterial({
      roughness: 0.7,
      transmission: 0.82,
      emissiveIntensity: 0.02,
      opacity: 1,
      depthWrite: false,
    });
    sourceMaterial.name = 'MAT_Glass';
    source.add(new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), sourceMaterial));

    const clone = prepareArchitecturalClone(source, { renderOrder: 150 });
    const clonedMesh = clone.children[0] as THREE.Mesh;
    const clonedMaterial = clonedMesh.material as THREE.MeshStandardMaterial;

    expect(clonedMaterial).not.toBe(sourceMaterial);
    expect(clonedMaterial.roughness).toBeLessThanOrEqual(0.18);
    expect(clonedMaterial.envMapIntensity).toBe(0.55);
    expect(clonedMaterial.opacity).toBe(1);
    expect(clonedMaterial.depthWrite).toBe(true);
    expect((clonedMaterial as THREE.MeshPhysicalMaterial).transmission).toBe(0.34);
    expect((clonedMaterial as THREE.MeshPhysicalMaterial).emissiveIntensity).toBe(0.08);
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

    expect(material.envMapIntensity).toBe(0.32);
    expect(material.aoMap).toBeNull();
    expect(material.roughnessMap).toBe(roughness);
    expect(material.metalness).toBe(0);
    expect(material.color.r).toBeCloseTo(1);
    expect(material.map?.colorSpace).toBe(THREE.SRGBColorSpace);
  });

  it('keeps physical facade glass while preserving the dark occupied-room read', () => {
    const source = new THREE.Group();
    const glass = new THREE.MeshPhysicalMaterial({
      color: '#ffffff',
      roughness: 0.1,
      transmission: 0.8,
      emissiveIntensity: 0.02,
    });
    glass.name = 'MAT_GlassOverlay_residential_low_e_Floor';
    glass.userData.environment_intensity = 1.2;
    source.add(new THREE.Mesh(new THREE.PlaneGeometry(), glass));

    const clone = prepareArchitecturalClone(source, { renderOrder: 150 });
    const tuned = (clone.children[0] as THREE.Mesh).material as THREE.MeshPhysicalMaterial;

    expect(tuned.transmission).toBe(0.08);
    expect(tuned.envMapIntensity).toBe(0.28);
    expect(tuned.color.r).toBeLessThan(0.5);
    expect(tuned.emissiveIntensity).toBeGreaterThanOrEqual(0.12);
  });

  it('keeps occupied interior cards warm and readable behind the pane', () => {
    const source = new THREE.Group();
    const room = new THREE.MeshStandardMaterial({
      roughness: 0.4,
      emissiveIntensity: 0.1,
    });
    room.name = 'MAT_GlazingInterior_residential_low_e_00';
    room.userData.glazing_lod = 'interior';
    source.add(new THREE.Mesh(new THREE.PlaneGeometry(), room));

    const clone = prepareArchitecturalClone(source, { renderOrder: 150 });
    const tuned = (clone.children[0] as THREE.Mesh).material as THREE.MeshStandardMaterial;

    expect(tuned.envMapIntensity).toBe(0.18);
    expect(tuned.roughness).toBe(0.78);
    expect(tuned.emissiveIntensity).toBe(0.42);
  });

  it('switches complementary physical and baked glazing with distance hysteresis', () => {
    const root = new THREE.Group();
    const far = new THREE.MeshStandardMaterial();
    far.name = 'MAT_Sheet_Far_Floor';
    const near = new THREE.MeshStandardMaterial();
    near.name = 'MAT_Sheet_Near_Floor';
    const physical = new THREE.MeshPhysicalMaterial();
    physical.name = 'MAT_GlassOverlay_reflective_curtain_wall_floor';
    root.add(
      new THREE.Mesh(new THREE.PlaneGeometry(), far),
      new THREE.Mesh(new THREE.PlaneGeometry(), near),
      new THREE.Mesh(new THREE.PlaneGeometry(), physical),
    );

    setArchitecturalGlazingLod(root, 'near');
    expect(far.visible).toBe(false);
    expect(near.visible).toBe(true);
    expect(physical.visible).toBe(true);
    expect(resolveArchitecturalGlazingLod(205, 'near')).toBe('near');
    expect(resolveArchitecturalGlazingLod(240, 'near')).toBe('far');
    expect(resolveArchitecturalGlazingLod(205, 'far')).toBe('far');
    expect(resolveArchitecturalGlazingLod(170, 'far')).toBe('near');
  });

  it('keeps the baked facade visible when a city-detail asset has no near sheet', () => {
    const root = new THREE.Group();
    const far = new THREE.MeshStandardMaterial();
    far.name = 'MAT_Sheet_Far_Floor';
    const physical = new THREE.MeshPhysicalMaterial();
    physical.name = 'MAT_GlassOverlay_heritage_sash_floor';
    root.add(
      new THREE.Mesh(new THREE.PlaneGeometry(), far),
      new THREE.Mesh(new THREE.PlaneGeometry(), physical),
    );

    setArchitecturalGlazingLod(root, 'near');

    expect(far.visible).toBe(true);
    expect(physical.visible).toBe(true);
  });

  it('does not mistake a near-only physical sash for a replacement facade sheet', () => {
    const root = new THREE.Group();
    const far = new THREE.MeshStandardMaterial();
    far.name = 'MAT_Sheet_Far_Floor';
    const sash = new THREE.MeshStandardMaterial();
    sash.name = 'MAT_GlazingFrame_industrial_sash';
    sash.userData.glazing_lod = 'near';
    const physical = new THREE.MeshPhysicalMaterial();
    physical.name = 'MAT_GlassOverlay_industrial_sash_floor';
    root.add(
      new THREE.Mesh(new THREE.PlaneGeometry(), far),
      new THREE.Mesh(new THREE.BoxGeometry(), sash),
      new THREE.Mesh(new THREE.PlaneGeometry(), physical),
    );

    setArchitecturalGlazingLod(root, 'near');

    expect(far.visible).toBe(true);
    expect(sash.visible).toBe(true);
    expect(physical.visible).toBe(true);
  });

  it('keeps wrapped side and rear elevations visible while the near front sheet is active', () => {
    const root = new THREE.Group();
    const farFront = new THREE.MeshStandardMaterial();
    farFront.name = 'MAT_Sheet_Far_Floor';
    const nearFront = new THREE.MeshStandardMaterial();
    nearFront.name = 'MAT_Sheet_Near_Floor';
    const wrappedSide = new THREE.MeshStandardMaterial();
    wrappedSide.name = 'MAT_Sheet_Wrapped_Floor_Right';
    wrappedSide.userData.glazing_lod = 'always';
    root.add(
      new THREE.Mesh(new THREE.PlaneGeometry(), farFront),
      new THREE.Mesh(new THREE.PlaneGeometry(), nearFront),
      new THREE.Mesh(new THREE.PlaneGeometry(), wrappedSide),
    );

    setArchitecturalGlazingLod(root, 'near');

    expect(farFront.visible).toBe(false);
    expect(nearFront.visible).toBe(true);
    expect(wrappedSide.visible).toBe(true);
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
