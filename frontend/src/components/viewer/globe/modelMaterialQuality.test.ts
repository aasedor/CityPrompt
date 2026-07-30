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
    expect((clone.material as THREE.MeshStandardMaterial).map?.colorSpace).toBe(
      THREE.SRGBColorSpace,
    );
  });

  it('disables legacy near-black AO only for the explicit LEGO policy', () => {
    const ao = new THREE.Texture();
    const sourceMaterial = new THREE.MeshStandardMaterial({
      color: '#b9aa99',
      map: new THREE.Texture(),
      aoMap: ao,
      aoMapIntensity: 1,
    });
    sourceMaterial.name = 'MAT_Facade_Primary';
    const source = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), sourceMaterial);

    const preserved = prepareArchitecturalClone(source, { renderOrder: 10 }) as THREE.Mesh;
    const safeLego = prepareArchitecturalClone(source, {
      renderOrder: 10,
      ambientOcclusion: 'disable',
    }) as THREE.Mesh;

    expect((preserved.material as THREE.MeshStandardMaterial).aoMap).toBe(ao);
    expect((safeLego.material as THREE.MeshStandardMaterial).aoMap).toBeNull();
    expect((safeLego.material as THREE.MeshStandardMaterial).aoMapIntensity).toBe(0);
    expect(sourceMaterial.aoMap).toBe(ao);
    expect(sourceMaterial.aoMapIntensity).toBe(1);
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

  it.each([
    {
      profile: 'bronze_recessed_occupied',
      transmission: 0.58,
      environment: 0.95,
      ior: 1.50,
      clearcoat: 0.46,
    },
    {
      profile: 'heritage_sash_occupied',
      transmission: 0.46,
      environment: 0.78,
      ior: 1.49,
      clearcoat: 0.38,
    },
    {
      profile: 'industrial_crittall_occupied',
      transmission: 0.50,
      environment: 0.84,
      ior: 1.48,
      clearcoat: 0.35,
    },
    {
      profile: 'nordic_clear_occupied',
      transmission: 0.52,
      environment: 0.90,
      ior: 1.50,
      clearcoat: 0.44,
    },
    {
      profile: 'museum_atrium_low_iron',
      transmission: 0.68,
      environment: 1.15,
      ior: 1.52,
      clearcoat: 0.62,
    },
    {
      profile: 'calgary_library_low_iron_fritted',
      transmission: 0.66,
      environment: 1.12,
      ior: 1.52,
      clearcoat: 0.60,
    },
    {
      profile: 'fluid_hub_low_iron_curved',
      transmission: 0.64,
      environment: 1.12,
      ior: 1.52,
      clearcoat: 0.62,
    },
    {
      profile: 'timber_station_neutral_low_e',
      transmission: 0.52,
      environment: 1.00,
      ior: 1.51,
      clearcoat: 0.52,
    },
    {
      profile: 'souk_recessed_amber_glass',
      transmission: 0.32,
      environment: 0.78,
      ior: 1.49,
      clearcoat: 0.40,
    },
    {
      profile: 'chalet_warm_low_e',
      transmission: 0.46,
      environment: 0.82,
      ior: 1.49,
      clearcoat: 0.36,
    },
    {
      profile: 'lanehouse_screened_low_e',
      transmission: 0.34,
      environment: 0.86,
      ior: 1.50,
      clearcoat: 0.50,
    },
    {
      profile: 'villa_recessed_iron_glass',
      transmission: 0.40,
      environment: 0.80,
      ior: 1.49,
      clearcoat: 0.38,
    },
    {
      profile: 'terracotta_office_low_e',
      transmission: 0.54,
      environment: 1.02,
      ior: 1.51,
      clearcoat: 0.54,
    },
    {
      profile: 'civic_recessed_smoked',
      transmission: 0.42,
      environment: 0.88,
      ior: 1.50,
      clearcoat: 0.46,
    },
  ])('preserves $profile as reflective non-emissive glass', ({
    profile,
    transmission,
    environment,
    ior,
    clearcoat,
  }) => {
    const source = new THREE.Group();
    const glass = new THREE.MeshPhysicalMaterial({
      color: '#b7c3c3',
      roughness: 0.072,
      transmission: 0.68,
      emissiveIntensity: 0.12,
    });
    glass.name = `MAT_W4_${profile}_Glass`;
    glass.userData.glazing_profile = profile;
    glass.userData.environment_intensity = 1.28;
    source.add(new THREE.Mesh(new THREE.BoxGeometry(1, 0.026, 1), glass));

    const clone = prepareArchitecturalClone(source, { renderOrder: 150 });
    const tuned = (clone.children[0] as THREE.Mesh).material as THREE.MeshPhysicalMaterial;

    expect(tuned.transmission).toBe(transmission);
    expect(tuned.envMapIntensity).toBe(environment);
    expect(tuned.ior).toBe(ior);
    expect(tuned.clearcoat).toBeGreaterThanOrEqual(clearcoat);
    expect(tuned.thickness).toBeGreaterThanOrEqual(0.026);
    expect(tuned.emissiveIntensity).toBeLessThanOrEqual(0.025);
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
      new THREE.Mesh(new THREE.PlaneGeometry(), [far, near]),
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

  it('keeps a near facade sheet visible at far LOD when no far sheet exists', () => {
    const root = new THREE.Group();
    const near = new THREE.MeshStandardMaterial();
    near.name = 'MAT_Sheet_Near_Floor';
    const sash = new THREE.MeshStandardMaterial();
    sash.name = 'MAT_GlazingFrame_industrial_sash';
    sash.userData.glazing_lod = 'near';
    root.add(
      new THREE.Mesh(new THREE.PlaneGeometry(), near),
      new THREE.Mesh(new THREE.BoxGeometry(), sash),
    );

    setArchitecturalGlazingLod(root, 'far');

    expect(near.visible).toBe(true);
    expect(sash.visible).toBe(false);
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

  it('does not pair unrelated facade roles within a joined mixed-elevation mesh', () => {
    const root = new THREE.Group();
    const nearFloor = new THREE.MeshStandardMaterial();
    nearFloor.name = 'MAT_Sheet_Near_Floor';
    nearFloor.userData.facade_sheet_role = 'floor';
    const farPodium = new THREE.MeshStandardMaterial();
    farPodium.name = 'MAT_Sheet_Far_Podium';
    farPodium.userData.facade_sheet_role = 'podium';
    root.add(new THREE.Mesh(new THREE.BoxGeometry(), [nearFloor, farPodium]));

    setArchitecturalGlazingLod(root, 'far');

    expect(nearFloor.visible).toBe(true);
    expect(farPodium.visible).toBe(true);

    setArchitecturalGlazingLod(root, 'near');

    expect(nearFloor.visible).toBe(true);
    expect(farPodium.visible).toBe(true);
  });

  it('switches only a matching facade role on a mixed material mesh', () => {
    const root = new THREE.Group();
    const farFloor = new THREE.MeshStandardMaterial();
    farFloor.name = 'MAT_Sheet_Far_Floor';
    farFloor.userData.facade_sheet_role = 'floor';
    const nearFloor = new THREE.MeshStandardMaterial();
    nearFloor.name = 'MAT_Sheet_Near_Floor';
    nearFloor.userData.facade_sheet_role = 'floor';
    const farCrown = new THREE.MeshStandardMaterial();
    farCrown.name = 'MAT_Sheet_Far_Crown';
    farCrown.userData.facade_sheet_role = 'crown';
    root.add(new THREE.Mesh(
      new THREE.BoxGeometry(),
      [farFloor, nearFloor, farCrown],
    ));

    setArchitecturalGlazingLod(root, 'near');

    expect(farFloor.visible).toBe(false);
    expect(nearFloor.visible).toBe(true);
    expect(farCrown.visible).toBe(true);

    setArchitecturalGlazingLod(root, 'far');

    expect(farFloor.visible).toBe(true);
    expect(nearFloor.visible).toBe(false);
    expect(farCrown.visible).toBe(true);
  });

  it('does not let a facade sheet on another mesh suppress a near-only elevation', () => {
    const root = new THREE.Group();
    const nearNorth = new THREE.MeshStandardMaterial();
    nearNorth.name = 'MAT_Sheet_Near_Floor';
    nearNorth.userData.facade_sheet_role = 'floor';
    const northSash = new THREE.MeshStandardMaterial();
    northSash.name = 'MAT_GlazingFrame_North';
    northSash.userData.glazing_lod = 'near';
    const farSouth = new THREE.MeshStandardMaterial();
    farSouth.name = 'MAT_Sheet_Far_Floor';
    farSouth.userData.facade_sheet_role = 'floor';
    const north = new THREE.Mesh(new THREE.BoxGeometry(), [nearNorth, northSash]);
    north.name = 'NorthElevation';
    const south = new THREE.Mesh(new THREE.BoxGeometry(), farSouth);
    south.name = 'SouthElevation';
    root.add(north, south);

    setArchitecturalGlazingLod(root, 'far');

    expect(nearNorth.visible).toBe(true);
    expect(northSash.visible).toBe(false);
    expect(farSouth.visible).toBe(true);
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
      new THREE.Mesh(new THREE.PlaneGeometry(), [farFront, nearFront]),
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
