import * as THREE from 'three';

const finishMaterials = new WeakMap<THREE.Material, THREE.Material>();

/** Some original assemblies place a thin finish exactly on their base cap.
 * Give that finish depth priority without moving vertices or mutating the
 * verified source's materials. Depth testing still preserves other occlusion. */
export function cloneNativeParkScene(source: THREE.Group): THREE.Group {
  const copy = source.clone(true);
  copy.updateMatrixWorld(true);
  copy.traverse(object => {
    if (!(object instanceof THREE.Mesh)) return;
    object.castShadow = true;
    object.receiveShadow = true;
    const materials: THREE.Material[] = Array.isArray(object.material) ? object.material : [object.material];
    if (!materials.some(material => ['paving', 'soil'].includes(material.name))) return;
    const bounds = new THREE.Box3().setFromObject(object);
    if (Math.abs(bounds.min.y) > .00001 || Math.abs(bounds.max.y) > .00001) return;
    const adjusted = materials.map(material => {
      if (!['paving', 'soil'].includes(material.name)) return material;
      let finish = finishMaterials.get(material);
      if (!finish) {
        finish = material.clone();
        finish.polygonOffset = true;
        finish.polygonOffsetFactor = -1;
        finish.polygonOffsetUnits = -4;
        // The globe writes logarithmic fragment depth, which bypasses the
        // ordinary polygon offset. Keep the same sub-millimetre near-view
        // priority in that path without disabling occlusion or moving meshes.
        finish.onBeforeCompile = (shader, renderer) => {
          material.onBeforeCompile(shader, renderer);
          shader.fragmentShader = shader.fragmentShader.replace(
            '#include <logdepthbuf_fragment>',
            `#include <logdepthbuf_fragment>
            #if defined( USE_LOGDEPTHBUF )
              gl_FragDepth = max(0.0, gl_FragDepth - 0.000001);
            #endif`,
          );
        };
        finish.customProgramCacheKey = () => `${material.customProgramCacheKey()}:native-park-finish-depth-v1`;
        finishMaterials.set(material, finish);
      }
      return finish;
    });
    object.material = Array.isArray(object.material) ? adjusted : adjusted[0];
  });
  return copy;
}
