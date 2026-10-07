import * as THREE from 'three';

/** The local RLASM review exports use one fully transmissive, double-sided
 * CLAY_GLASS material. On the globe this produces dense refraction striping.
 * Replace only that material on an owned runtime clone. Geometry, textures,
 * source GLB and all other materials keep their exact authored values. */
export function prepareReviewBuildingGlass(source: THREE.Object3D): {
  clone: THREE.Object3D; ownedMaterials: THREE.MeshPhysicalMaterial[];
} {
  const clone = source.clone(true);
  const replacements = new Map<THREE.Material, THREE.MeshPhysicalMaterial>();
  clone.traverse(object => {
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh) return;
    const replace = (material: THREE.Material): THREE.Material => {
      if (material.name !== 'CLAY_GLASS' || !(material as THREE.MeshPhysicalMaterial).isMeshPhysicalMaterial) return material;
      let result = replacements.get(material);
      if (!result) {
        result = (material as THREE.MeshPhysicalMaterial).clone();
        result.name = 'CLAY_GLASS_globe_review';
        result.transmission = 0;
        result.transparent = true;
        result.opacity = 0.42;
        result.depthWrite = false;
        result.side = THREE.DoubleSide;
        result.forceSinglePass = true;
        result.roughness = Math.max(result.roughness, 0.16);
        result.userData = { ...result.userData, globe_review_glass: true };
        result.needsUpdate = true;
        replacements.set(material, result);
      }
      return result;
    };
    mesh.material = Array.isArray(mesh.material) ? mesh.material.map(replace) : replace(mesh.material);
  });
  return { clone, ownedMaterials: [...replacements.values()] };
}
