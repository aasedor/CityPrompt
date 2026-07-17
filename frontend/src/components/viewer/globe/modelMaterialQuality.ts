import * as THREE from 'three';

const DEFAULT_ENV_INTENSITY = 0.9;
const GLASS_ENV_INTENSITY = 1.25;
const FALLBACK_CLAY = new THREE.Color('#d8cfc0');

export interface ArchitecturalCloneOptions {
  renderOrder: number;
  maxAnisotropy?: number;
  restyleUntextured?: boolean;
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
): THREE.Material {
  const material = source.clone();
  const standard = material as THREE.MeshStandardMaterial;
  if (!standard.isMeshStandardMaterial) return material;

  tuneTexture(standard.map, maxAnisotropy);
  tuneTexture(standard.normalMap, maxAnisotropy);
  tuneTexture(standard.roughnessMap, maxAnisotropy);
  tuneTexture(standard.metalnessMap, maxAnisotropy);
  tuneTexture(standard.aoMap, maxAnisotropy);

  const materialName = standard.name.toLowerCase();
  if (materialName.includes('glass')) {
    // The v5 GLBs carry room backplates behind alpha-blended low-iron glass.
    // Keep the dielectric response and coat; the footprint tile mask prevents
    // the old photogrammetric building from showing through the glazing.
    standard.roughness = Math.min(standard.roughness, 0.18);
    standard.metalness = 0;
    standard.envMapIntensity = GLASS_ENV_INTENSITY;
    standard.depthWrite = false;
    const physical = standard as THREE.MeshPhysicalMaterial;
    if (physical.isMeshPhysicalMaterial) {
      physical.ior = 1.48;
      physical.clearcoat = Math.max(physical.clearcoat, 0.3);
      physical.clearcoatRoughness = Math.min(physical.clearcoatRoughness, 0.12);
    }
  } else if (materialName.includes('interior_shadow')) {
    standard.roughness = 0.92;
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

/** Clone a cached GLTF scene without sharing mutable material instances. */
export function prepareArchitecturalClone(
  source: THREE.Object3D,
  { renderOrder, maxAnisotropy = 8, restyleUntextured = false }: ArchitecturalCloneOptions,
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
      tuneMaterial(material, maxAnisotropy, restyleUntextured)
    ));
    mesh.material = Array.isArray(mesh.material) ? tuned : tuned[0];
  });
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
