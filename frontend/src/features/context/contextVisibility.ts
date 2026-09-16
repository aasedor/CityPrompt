import type { Material, Mesh, Object3D } from 'three';

/** Hide display materials only. Raycast geometry, tile visibility and ground
 * sampling stay intact, so a presentation choice cannot rebase the proposal. */
export function setContextMaterialVisibility(root: Object3D, visible: boolean, originals: Map<Material, boolean>): void {
  root.traverse(object => {
    const mesh = object as Mesh;
    if (!mesh.isMesh && !('isPoints' in object)) return;
    const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    materials.filter(Boolean).forEach(material => {
      if (!originals.has(material)) originals.set(material, material.visible);
      material.visible = visible && originals.get(material)!;
    });
  });
}

export function restoreContextMaterials(originals: Map<Material, boolean>): void {
  originals.forEach((visible, material) => { material.visible = visible; }); originals.clear();
}
