import { expect, it } from 'vitest';
import { SparkRenderer } from '@sparkjsdev/spark';
import { Matrix4, ShaderMaterial, Vector2, Vector4, type WebGLRenderer } from 'three';
import { applySplatSpatialMask } from './splatSpatialMask';

it('adapts the actual pinned renderer shader once and subtracts ECEF on the CPU', () => {
  // Shader construction needs no WebGL calls; browser QA covers compilation.
  const renderer = new SparkRenderer({ renderer: {} as WebGLRenderer });
  const frame = new Matrix4().makeTranslation(-1643557, -3670025, 4935603);
  const config = { worldToLocal: frame.clone().invert(), edges: [new Vector4(0, 0, 20, 0)],
    maskRanges: [new Vector2(0, 1)], maskCount: 1, minHeight: -120, maxHeight: 180, cacheKey: 'pilot' };
  applySplatSpatialMask(renderer.material, config, frame);
  const shader = renderer.material.vertexShader;
  expect(shader).toContain('out vec3 vSiteMaskLocalPosition');
  expect(renderer.material.fragmentShader).toContain('insideAnySiteMask');
  expect(renderer.material.uniforms.siteMaskWorldToLocal.value.equals(new Matrix4())).toBe(true);
  expect(renderer.material.uniforms.siteMaskEdges.value).toHaveLength(32);
  applySplatSpatialMask(renderer.material, config, frame);
  expect(renderer.material.vertexShader).toBe(shader);
  renderer.defaultView.dispose(); renderer.material.dispose();
});

it('rejects an incompatible shader instead of silently omitting the replacement area', () => {
  const material = new ShaderMaterial();
  expect(() => applySplatSpatialMask(material, { worldToLocal: new Matrix4(), edges: [], maskRanges: [],
    maskCount: 0, minHeight: 0, maxHeight: 1, cacheKey: '' }, new Matrix4())).toThrow('Unsupported');
});
