import { Vector2, Vector4, type Matrix4, type ShaderMaterial } from 'three';
import type { TileSpatialMaskConfig } from '@/components/viewer/globe/TileSpatialMaskPlugin';
import { siteMaskFragmentDeclarations, siteMaskFragmentTest } from '@/components/viewer/globe/siteMaskShader';

/** Whole-Gaussian suppression by centre; source bytes are never edited. */
export function applySplatSpatialMask(material: ShaderMaterial, config: TileSpatialMaskConfig, localToWorld: Matrix4): void {
  if (!material.userData.citySplatMask) {
    const marker = 'vec3 viewCenter =';
    if (!material.vertexShader.includes(marker)) throw new Error('Unsupported Gaussian shader');
    material.vertexShader = material.vertexShader.replace('void main() {',
      'uniform mat4 siteMaskWorldToLocal;\nout vec3 vSiteMaskLocalPosition;\nvoid main() {')
      .replace(marker, `vSiteMaskLocalPosition = (siteMaskWorldToLocal * vec4(center, 1.0)).xyz;\n${marker}`);
    material.fragmentShader = material.fragmentShader.replace('void main() {',
      `${siteMaskFragmentDeclarations.replace('varying vec3', 'in vec3')}\nvoid main() {\n${siteMaskFragmentTest}`);
    material.userData.citySplatMask = true;
    material.needsUpdate = true;
  }
  Object.assign(material.uniforms, {
    siteMaskWorldToLocal: { value: config.worldToLocal.clone().multiply(localToWorld) },
    siteMaskEdges: { value: Array.from({ length: 32 }, (_, i) => config.edges[i] ?? new Vector4()) },
    siteMaskEdgeCount: { value: config.edges.length },
    siteMaskRanges: { value: Array.from({ length: 8 }, (_, i) => config.maskRanges[i] ?? new Vector2()) },
    siteMaskCount: { value: config.maskCount },
    siteMaskHeightRange: { value: new Vector2(config.minHeight, config.maxHeight) },
  });
}
