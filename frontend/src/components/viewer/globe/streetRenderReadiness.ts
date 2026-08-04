import * as THREE from 'three';

const AUTHORED_ROOT_NAMES = [
  'siteforge-direct3d-ground',
  'siteforge-direct3d-landscape',
  'siteforge-direct3d-street',
  'siteforge-direct3d-park',
  'siteforge-direct3d-building',
] as const;

export interface StreetRenderReadiness {
  authoredMeshCount: number;
  buildingMeshCount: number;
  uniquePbrMaterialCount: number;
  baseColorTextureCount: number;
  normalMapCount: number;
  roughnessMapCount: number;
  aoMapCount: number;
  shadowCasterCount: number;
  instancedDetailMeshCount: number;
  maxBuildingTextureDimension: number | null;
  warnings: string[];
}

function textureDimension(texture: THREE.Texture | null | undefined): number | null {
  if (!texture) return null;
  const candidates = [
    texture.image,
    texture.source?.data,
    texture.mipmaps?.[0],
  ] as Array<{ width?: unknown; height?: unknown } | undefined>;
  for (const candidate of candidates) {
    const width = Number(candidate?.width);
    const height = Number(candidate?.height);
    const maximum = Math.max(width, height);
    if (Number.isFinite(maximum) && maximum > 0) return maximum;
  }
  return null;
}

/**
 * Inspect the actual mounted City Prompt scene immediately before route
 * capture. Google Tiles live outside these authored roots and are therefore
 * retained as context without inflating the proposal readiness measurements.
 */
export function inspectStreetRenderReadiness(scene: THREE.Scene): StreetRenderReadiness {
  const allMaterials = new Set<THREE.Material>();
  const buildingMaterials = new Set<THREE.Material>();
  const pbrMaterials = new Set<THREE.MeshStandardMaterial>();
  const baseColorTextures = new Set<THREE.Texture>();
  const normalTextures = new Set<THREE.Texture>();
  const roughnessTextures = new Set<THREE.Texture>();
  const aoTextures = new Set<THREE.Texture>();
  const buildingBaseColorTextures = new Set<THREE.Texture>();
  const buildingNormalTextures = new Set<THREE.Texture>();
  let authoredMeshCount = 0;
  let buildingMeshCount = 0;
  let shadowCasterCount = 0;
  let buildingShadowCasterCount = 0;
  let instancedDetailMeshCount = 0;
  let maxBuildingTextureDimension: number | null = null;

  AUTHORED_ROOT_NAMES.forEach((rootName) => {
    const root = scene.getObjectByName(rootName);
    if (!root || !root.visible) return;
    const buildingRoot = rootName === 'siteforge-direct3d-building';
    root.traverse((object) => {
      const mesh = object as THREE.Mesh;
      if (!mesh.isMesh || !mesh.visible) return;
      authoredMeshCount += 1;
      if (buildingRoot) buildingMeshCount += 1;
      if (mesh.castShadow) shadowCasterCount += 1;
      if (buildingRoot && mesh.castShadow) buildingShadowCasterCount += 1;
      if ((mesh as THREE.InstancedMesh).isInstancedMesh) instancedDetailMeshCount += 1;

      const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      materials.forEach((material) => {
        if (!material || !material.visible) return;
        allMaterials.add(material);
        if (buildingRoot) buildingMaterials.add(material);
        const standard = material as THREE.MeshStandardMaterial;
        if (!standard.isMeshStandardMaterial) return;
        pbrMaterials.add(standard);
        if (standard.map) baseColorTextures.add(standard.map);
        if (standard.normalMap) normalTextures.add(standard.normalMap);
        if (standard.roughnessMap) roughnessTextures.add(standard.roughnessMap);
        if (standard.aoMap) aoTextures.add(standard.aoMap);
        if (buildingRoot) {
          if (standard.map) buildingBaseColorTextures.add(standard.map);
          if (standard.normalMap) buildingNormalTextures.add(standard.normalMap);
          [standard.map, standard.normalMap, standard.roughnessMap, standard.aoMap]
            .forEach((texture) => {
              const dimension = textureDimension(texture);
              if (dimension !== null) {
                maxBuildingTextureDimension = Math.max(maxBuildingTextureDimension ?? 0, dimension);
              }
            });
        }
      });
    });
  });

  const buildingPbrCount = [...buildingMaterials].filter(
    (material) => (material as THREE.MeshStandardMaterial).isMeshStandardMaterial,
  ).length;
  const warnings: string[] = [];
  if (buildingMeshCount === 0) {
    warnings.push('No mounted authored building meshes were found.');
  } else if (buildingMaterials.size > 0 && buildingPbrCount / buildingMaterials.size < 0.8) {
    warnings.push('Some building materials are not PBR-ready.');
  }
  if (buildingMeshCount > 0 && buildingBaseColorTextures.size === 0) {
    warnings.push('The mounted buildings do not expose a base-colour texture.');
  }
  if (buildingMeshCount > 0 && buildingNormalTextures.size === 0) {
    warnings.push('The mounted buildings do not expose normal-map detail.');
  }
  if (
    maxBuildingTextureDimension !== null
    && maxBuildingTextureDimension < 2048
  ) {
    warnings.push('The largest resolved building texture is below the 2K street-render target.');
  }
  if (buildingMeshCount > 0 && buildingShadowCasterCount === 0) {
    warnings.push('Authored geometry is not participating in the street shadow pass.');
  }
  if (instancedDetailMeshCount === 0) {
    warnings.push('No instanced vegetation or public-realm detail meshes were found.');
  }

  return {
    authoredMeshCount,
    buildingMeshCount,
    uniquePbrMaterialCount: pbrMaterials.size,
    baseColorTextureCount: baseColorTextures.size,
    normalMapCount: normalTextures.size,
    roughnessMapCount: roughnessTextures.size,
    aoMapCount: aoTextures.size,
    shadowCasterCount,
    instancedDetailMeshCount,
    maxBuildingTextureDimension,
    warnings,
  };
}
