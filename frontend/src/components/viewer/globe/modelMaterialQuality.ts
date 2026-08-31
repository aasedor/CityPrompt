import * as THREE from 'three';

const DEFAULT_ENV_INTENSITY = 0.9;
const GLASS_ENV_INTENSITY = 1.25;
const OCCUPIED_GLASS_ENV_INTENSITY = 0.55;
const OCCUPIED_GLASS_MAX_TRANSMISSION = 0.34;
const OCCUPIED_GLASS_TINT = new THREE.Color('#9b9184');
const FACADE_GLASS_ENV_INTENSITY = 0.28;
const FACADE_GLASS_MAX_TRANSMISSION = 0.08;
const FACADE_GLASS_TINT = new THREE.Color('#6d675e');
const FACADE_ENV_INTENSITY = 0.32;
const FALLBACK_CLAY = new THREE.Color('#d8cfc0');

interface LayeredGlazingProfile {
  roughnessMin: number;
  roughnessMax: number;
  ior: number;
  clearcoatMin: number;
  clearcoatRoughnessMax: number;
  transmissionMax: number;
  environmentMax: number;
  attenuationDistance: number;
  attenuationColor: string;
}

const LAYERED_GLAZING_PROFILES: Record<string, LayeredGlazingProfile> = {
  bronze_recessed_occupied: {
    roughnessMin: 0.055,
    roughnessMax: 0.12,
    ior: 1.50,
    clearcoatMin: 0.46,
    clearcoatRoughnessMax: 0.06,
    transmissionMax: 0.58,
    environmentMax: 0.95,
    attenuationDistance: 2.4,
    attenuationColor: '#d5e2df',
  },
  heritage_sash_occupied: {
    roughnessMin: 0.080,
    roughnessMax: 0.14,
    ior: 1.49,
    clearcoatMin: 0.38,
    clearcoatRoughnessMax: 0.10,
    transmissionMax: 0.46,
    environmentMax: 0.78,
    attenuationDistance: 2.0,
    attenuationColor: '#e6d7c6',
  },
  industrial_crittall_occupied: {
    roughnessMin: 0.075,
    roughnessMax: 0.13,
    ior: 1.48,
    clearcoatMin: 0.35,
    clearcoatRoughnessMax: 0.09,
    transmissionMax: 0.50,
    environmentMax: 0.84,
    attenuationDistance: 2.2,
    attenuationColor: '#d3d9d5',
  },
  nordic_clear_occupied: {
    roughnessMin: 0.055,
    roughnessMax: 0.11,
    ior: 1.50,
    clearcoatMin: 0.44,
    clearcoatRoughnessMax: 0.065,
    transmissionMax: 0.52,
    environmentMax: 0.90,
    attenuationDistance: 2.3,
    attenuationColor: '#dbe5e3',
  },
  museum_atrium_low_iron: {
    roughnessMin: 0.035,
    roughnessMax: 0.085,
    ior: 1.52,
    clearcoatMin: 0.62,
    clearcoatRoughnessMax: 0.05,
    transmissionMax: 0.70,
    environmentMax: 1.15,
    attenuationDistance: 4.2,
    attenuationColor: '#dce6e3',
  },
  calgary_library_low_iron_fritted: {
    roughnessMin: 0.045,
    roughnessMax: 0.10,
    ior: 1.52,
    clearcoatMin: 0.60,
    clearcoatRoughnessMax: 0.055,
    transmissionMax: 0.66,
    environmentMax: 1.12,
    attenuationDistance: 4.0,
    attenuationColor: '#d6e2e1',
  },
  fluid_hub_low_iron_curved: {
    roughnessMin: 0.042,
    roughnessMax: 0.095,
    ior: 1.52,
    clearcoatMin: 0.62,
    clearcoatRoughnessMax: 0.052,
    transmissionMax: 0.64,
    environmentMax: 1.12,
    attenuationDistance: 4.2,
    attenuationColor: '#d4e0df',
  },
  timber_station_neutral_low_e: {
    roughnessMin: 0.055,
    roughnessMax: 0.115,
    ior: 1.51,
    clearcoatMin: 0.52,
    clearcoatRoughnessMax: 0.070,
    transmissionMax: 0.52,
    environmentMax: 1.00,
    attenuationDistance: 3.2,
    attenuationColor: '#d9e0dc',
  },
  souk_recessed_amber_glass: {
    roughnessMin: 0.090,
    roughnessMax: 0.15,
    ior: 1.49,
    clearcoatMin: 0.40,
    clearcoatRoughnessMax: 0.095,
    transmissionMax: 0.32,
    environmentMax: 0.78,
    attenuationDistance: 2.1,
    attenuationColor: '#e2d0b7',
  },
  chalet_warm_low_e: {
    roughnessMin: 0.09,
    roughnessMax: 0.15,
    ior: 1.49,
    clearcoatMin: 0.36,
    clearcoatRoughnessMax: 0.10,
    transmissionMax: 0.46,
    environmentMax: 0.82,
    attenuationDistance: 2.0,
    attenuationColor: '#e5d4bf',
  },
  lanehouse_screened_low_e: {
    roughnessMin: 0.06,
    roughnessMax: 0.12,
    ior: 1.50,
    clearcoatMin: 0.50,
    clearcoatRoughnessMax: 0.065,
    transmissionMax: 0.34,
    environmentMax: 0.86,
    attenuationDistance: 2.5,
    attenuationColor: '#d4ddd9',
  },
  villa_recessed_iron_glass: {
    roughnessMin: 0.085,
    roughnessMax: 0.145,
    ior: 1.49,
    clearcoatMin: 0.38,
    clearcoatRoughnessMax: 0.095,
    transmissionMax: 0.40,
    environmentMax: 0.80,
    attenuationDistance: 2.1,
    attenuationColor: '#e2d2bd',
  },
  terracotta_office_low_e: {
    roughnessMin: 0.05,
    roughnessMax: 0.105,
    ior: 1.51,
    clearcoatMin: 0.54,
    clearcoatRoughnessMax: 0.065,
    transmissionMax: 0.54,
    environmentMax: 1.02,
    attenuationDistance: 3.1,
    attenuationColor: '#d8e1de',
  },
  civic_recessed_smoked: {
    roughnessMin: 0.07,
    roughnessMax: 0.13,
    ior: 1.50,
    clearcoatMin: 0.46,
    clearcoatRoughnessMax: 0.085,
    transmissionMax: 0.42,
    environmentMax: 0.88,
    attenuationDistance: 2.7,
    attenuationColor: '#d2d9d4',
  },
};

/** Preserve a compiler-authored archetype glazing system in every viewer. */
export function applyLayeredGlazingProfile(
  physical: THREE.MeshPhysicalMaterial,
  profileName: string,
): boolean {
  const profile = LAYERED_GLAZING_PROFILES[profileName.toLowerCase()];
  if (!profile) return false;

  physical.roughness = Math.max(
    profile.roughnessMin,
    Math.min(physical.roughness, profile.roughnessMax),
  );
  physical.ior = profile.ior;
  physical.clearcoat = Math.max(physical.clearcoat, profile.clearcoatMin);
  physical.clearcoatRoughness = Math.min(
    physical.clearcoatRoughness,
    profile.clearcoatRoughnessMax,
  );
  physical.transmission = Math.min(
    physical.transmission,
    profile.transmissionMax,
  );
  physical.envMapIntensity = Math.min(
    physical.envMapIntensity,
    profile.environmentMax,
  );
  physical.thickness = Math.max(physical.thickness, 0.026);
  physical.attenuationDistance = profile.attenuationDistance;
  physical.attenuationColor.set(profile.attenuationColor);
  physical.emissiveIntensity = Math.min(physical.emissiveIntensity, 0.025);
  return true;
}

export type ArchitecturalGlazingLod = 'near' | 'far';

/** Enter physical glazing closer than this; leave it beyond the second threshold. */
export const GLAZING_NEAR_DISTANCE_METERS = 180;
export const GLAZING_FAR_DISTANCE_METERS = 230;

export interface ArchitecturalCloneOptions {
  renderOrder: number;
  maxAnisotropy?: number;
  restyleUntextured?: boolean;
  /** Keep an externally authored model's complete PBR state authoritative.
   * Materials are still cloned so the GLTF cache cannot be mutated, but no
   * colours, maps, optical values, alpha settings, or visibility are changed. */
  preserveSourcePbr?: boolean;
  /** Legacy LEGO compiler assets can contain effectively black ambient-
   * occlusion maps. Keep AO for authored standalone/Meshy models by default,
   * and disable it only for the LEGO assembly path where the preview already
   * follows this presentation-safe policy. */
  ambientOcclusion?: 'preserve' | 'disable';
}

function tuneTexture(texture: THREE.Texture | null, maxAnisotropy: number): void {
  if (!texture) return;
  texture.anisotropy = Math.max(texture.anisotropy, Math.min(maxAnisotropy, 16));
  texture.needsUpdate = true;
}

function tuneMaterial(
  source: THREE.Material,
  maxAnisotropy: number,
  restyleUntextured: boolean,
  ambientOcclusion: 'preserve' | 'disable',
): THREE.Material {
  const material = source.clone();
  const standard = material as THREE.MeshStandardMaterial;
  if (!standard.isMeshStandardMaterial) return material;

  tuneTexture(standard.map, maxAnisotropy);
  tuneTexture(standard.normalMap, maxAnisotropy);
  tuneTexture(standard.roughnessMap, maxAnisotropy);
  tuneTexture(standard.metalnessMap, maxAnisotropy);
  tuneTexture(standard.aoMap, maxAnisotropy);

  // Base-colour textures exported by older compiler versions do not always
  // carry colour-space metadata. Treating them as linear makes facades much
  // darker than the same module in LEGO Builder.
  if (standard.map) standard.map.colorSpace = THREE.SRGBColorSpace;
  if (ambientOcclusion === 'disable') {
    standard.aoMap = null;
    standard.aoMapIntensity = 0;
  }

  const materialName = standard.name.toLowerCase();
  if (materialName.startsWith('mat_sheet_')) {
    // The sheet supplies albedo + authored roughness. Preserve both: flattening
    // the roughness map and halving the colour was the main cause of dull,
    // computer-generated facades in the Google Tiles scene.
    standard.aoMap = null;
    standard.aoMapIntensity = 0;
    standard.envMapIntensity = FACADE_ENV_INTENSITY;
    standard.color.setScalar(1);
    if (!standard.roughnessMap) standard.roughness = Math.max(standard.roughness, 0.72);
    standard.metalness = 0;
    if (standard.map) standard.map.colorSpace = THREE.SRGBColorSpace;
  } else if (
    materialName.includes('glazinginterior')
    || standard.userData?.glazing_lod === 'interior'
  ) {
    // Occupied room cards are the visual anchor behind the physical pane.
    // Keep their photographed tonal range and warm emission independent of
    // the bright Google Tiles sky so close windows read as deep rooms rather
    // than white holes.
    standard.envMapIntensity = 0.18;
    standard.color.setScalar(1);
    standard.roughness = Math.max(standard.roughness, 0.78);
    standard.emissiveIntensity = Math.max(standard.emissiveIntensity, 0.42);
  } else if (materialName.includes('glass')) {
    // Transmission is a physical dielectric response, not conventional alpha
    // blending. MASK materials retain their semantic cut-out while their glass
    // pixels remain fully opaque to Three's depth sorting.
    standard.roughness = Math.min(standard.roughness, 0.18);
    standard.metalness = 0;
    const authoredEnvironment = Number(standard.userData?.environment_intensity);
    standard.envMapIntensity = Number.isFinite(authoredEnvironment)
      ? authoredEnvironment
      : GLASS_ENV_INTENSITY;
    const physical = standard as THREE.MeshPhysicalMaterial;
    if (physical.isMeshPhysicalMaterial) {
      physical.opacity = 1;
      physical.depthWrite = true;
      physical.ior = 1.48;
      physical.clearcoat = Math.max(physical.clearcoat, 0.3);
      physical.clearcoatRoughness = Math.min(physical.clearcoatRoughness, 0.12);
      const glazingProfile = String(
        standard.userData?.glazing_profile ?? '',
      ).toLowerCase();
      if (applyLayeredGlazingProfile(physical, glazingProfile)) {
        // These profiles export independent panes in front of occupied room
        // cards. The family-specific coated dielectric reflects the sky while
        // warmth remains behind the pane instead of glowing from the glass.
      } else if (materialName.includes('glassoverlay')) {
        // A high-transmission façade card samples the bright globe background
        // and washes the authored window atlas to white. Retain a real coated
        // dielectric response, but let the registered glazing texture and the
        // occupied room card supply most of the pane colour and depth.
        physical.transmission = Math.min(
          physical.transmission,
          FACADE_GLASS_MAX_TRANSMISSION,
        );
        physical.envMapIntensity = Math.min(
          physical.envMapIntensity,
          FACADE_GLASS_ENV_INTENSITY,
        );
        physical.color.multiply(FACADE_GLASS_TINT);
        physical.emissiveIntensity = Math.max(physical.emissiveIntensity, 0.12);
      } else {
        // Standalone attic/oriel panes also sit in front of an occupied room
        // card. Cap the bright globe reflection and transmission so the card
        // remains legible through a coated dielectric instead of bleaching to
        // a flat sky-blue rectangle in Google Tiles.
        physical.transmission = Math.min(
          physical.transmission,
          OCCUPIED_GLASS_MAX_TRANSMISSION,
        );
        physical.envMapIntensity = Math.min(
          physical.envMapIntensity,
          OCCUPIED_GLASS_ENV_INTENSITY,
        );
        physical.color.multiply(OCCUPIED_GLASS_TINT);
        physical.emissiveIntensity = Math.max(physical.emissiveIntensity, 0.08);
      }
    }
  } else if (
    materialName.includes('interior_shadow')
    || (
      standard.userData?.glazing_profile
      && materialName.includes('interiorsolarshade')
    )
  ) {
    standard.roughness = Math.max(standard.roughness, 0.82);
    standard.envMapIntensity = 0.2;
  } else {
    standard.envMapIntensity = DEFAULT_ENV_INTENSITY;
    if (restyleUntextured && !standard.map) {
      standard.color.copy(FALLBACK_CLAY);
      standard.roughness = 0.9;
      standard.metalness = 0;
    }
  }
  standard.needsUpdate = true;
  return standard;
}

function glazingLodTag(material: THREE.Material): string | undefined {
  const explicit = material.userData?.glazing_lod;
  if (typeof explicit === 'string') return explicit.toLowerCase();
  const name = material.name.toLowerCase();
  if (name.startsWith('mat_sheet_far_')) return 'far';
  if (name.startsWith('mat_sheet_near_')) return 'near';
  if (name.includes('glassoverlay')) return 'physical';
  if (name.includes('glazing_frame')) return 'near';
  if (name.includes('glazinginterior')) return 'interior';
  return undefined;
}

function isNearFacadeSheet(material: THREE.Material): boolean {
  const name = material.name.toLowerCase();
  if (name.startsWith('mat_sheet_near_')) return true;
  return (
    glazingLodTag(material) === 'near'
    && typeof material.userData?.facade_sheet_role === 'string'
  );
}

function isFarFacadeSheet(material: THREE.Material): boolean {
  const name = material.name.toLowerCase();
  if (name.startsWith('mat_sheet_far_')) return true;
  return (
    glazingLodTag(material) === 'far'
    && typeof material.userData?.facade_sheet_role === 'string'
  );
}

function facadeSheetPairingKey(material: THREE.Material): string | undefined {
  if (!isNearFacadeSheet(material) && !isFarFacadeSheet(material)) return undefined;

  const explicitRole = material.userData?.facade_sheet_role;
  if (typeof explicitRole === 'string' && explicitRole.trim()) {
    return `role:${explicitRole.trim().toLowerCase()}`;
  }

  // Older compiler exports did not always copy ``facade_sheet_role`` onto a
  // near PBR material. Recover the standard band identity from its material
  // name. Pairing an unknown name is intentionally conservative: if the two
  // names do not normalize to the same value, both authored sheets remain
  // visible rather than exposing the structural core at either LOD.
  const normalizedName = material.name
    .toLowerCase()
    .replace(/^mat_sheet_(?:near|far)_/, '')
    .trim();
  return normalizedName ? `name:${normalizedName}` : undefined;
}

/** Toggle the complementary materials exported in a semantic-glazing GLB. */
export function setArchitecturalGlazingLod(
  root: THREE.Object3D,
  mode: ArchitecturalGlazingLod,
): void {
  root.traverse((object) => {
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh) return;
    const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    // Pair only facade sheets authored for the same band on the same joined
    // mesh. A root-level flag is unsafe for mixed GLBs: a far podium material
    // on one module must not suppress a near-only floor/elevation elsewhere.
    // Frames and sashes have no facade pairing key and therefore still follow
    // their normal near-only culling policy.
    const nearFacadeKeys = new Set(
      materials
        .filter((material) => isNearFacadeSheet(material))
        .map((material) => facadeSheetPairingKey(material))
        .filter((key): key is string => Boolean(key)),
    );
    const farFacadeKeys = new Set(
      materials
        .filter((material) => isFarFacadeSheet(material))
        .map((material) => facadeSheetPairingKey(material))
        .filter((key): key is string => Boolean(key)),
    );

    materials.forEach((material) => {
      const tag = glazingLodTag(material);
      const facadeKey = facadeSheetPairingKey(material);
      // City-detail exports intentionally contain the baked far sheet plus
      // physical glazing overlays, but no duplicate near facade sheet. Keep
      // the baked facade visible in that case so entering the close-range LOD
      // does not expose the untextured wall substrate.
      if (tag === 'far') {
        material.visible = mode === 'far'
          || !facadeKey
          || !nearFacadeKeys.has(facadeKey);
      }
      if (tag === 'near') {
        // A few valid compiler assets contain only a near facade sheet. Keep
        // that authored sheet at city distance rather than hiding it and
        // exposing the dark structural substrate. Near-only frames/sashes are
        // still culled normally because they are not facade sheets.
        material.visible = mode === 'near'
          || (facadeKey !== undefined && !farFacadeKeys.has(facadeKey));
      }
      if (tag === 'physical' || tag === 'interior') {
        material.visible = mode === 'near';
      }
    });
  });
}

/** Hysteresis prevents rapid material flicker while orbiting near the cutoff. */
export function resolveArchitecturalGlazingLod(
  distanceMeters: number,
  current: ArchitecturalGlazingLod = 'far',
): ArchitecturalGlazingLod {
  if (current === 'near') {
    return distanceMeters > GLAZING_FAR_DISTANCE_METERS ? 'far' : 'near';
  }
  return distanceMeters < GLAZING_NEAR_DISTANCE_METERS ? 'near' : 'far';
}

/** Clone a cached GLTF scene without sharing mutable material instances. */
export function prepareArchitecturalClone(
  source: THREE.Object3D,
  {
    renderOrder,
    maxAnisotropy = 8,
    restyleUntextured = false,
    preserveSourcePbr = false,
    ambientOcclusion = 'preserve',
  }: ArchitecturalCloneOptions,
): THREE.Object3D {
  const clone = source.clone(true);
  clone.traverse((object) => {
    object.renderOrder = renderOrder;
    object.frustumCulled = false;
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh) return;

    mesh.castShadow = true;
    mesh.receiveShadow = true;
    const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    const tuned = materials.map((material) => (
      preserveSourcePbr
        ? material.clone()
        : tuneMaterial(material, maxAnisotropy, restyleUntextured, ambientOcclusion)
    ));
    mesh.material = Array.isArray(mesh.material) ? tuned : tuned[0];
  });
  if (!preserveSourcePbr) setArchitecturalGlazingLod(clone, 'far');
  return clone;
}

/** Dispose only clone-owned materials; geometry and textures belong to the GLTF cache. */
export function disposeArchitecturalCloneMaterials(clone: THREE.Object3D): void {
  clone.traverse((object) => {
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh) return;
    const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    materials.forEach((material) => material.dispose());
  });
}
