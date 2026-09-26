import { describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';

import {
  createDirect3DGeometryMaterial,
  createDirect3DLinearDepthSession,
  LINEAR_DEPTH_FRAGMENT_ANCHOR,
  LINEAR_DEPTH_VERTEX_ANCHOR,
} from './direct3dCapture';

const WINDOW = { nearMeters: 50, farMeters: 1500 };

interface FakeShader {
  uniforms: Record<string, { value: number }>;
  vertexShader: string;
  fragmentShader: string;
}

type CompileHook = (shader: FakeShader, renderer: unknown) => void;

function compile(material: THREE.Material): FakeShader {
  const shader: FakeShader = {
    uniforms: {},
    vertexShader: `void main() {\n\t${LINEAR_DEPTH_VERTEX_ANCHOR}\n}`,
    fragmentShader: `void main() {\n\t${LINEAR_DEPTH_FRAGMENT_ANCHOR}\n}`,
  };
  (material.onBeforeCompile as unknown as CompileHook)(shader, {});
  return shader;
}

describe('linear depth control pass', () => {
  it('is an 8-bit depth material that keeps the source material policy', () => {
    const source = new THREE.MeshStandardMaterial({ side: THREE.DoubleSide, alphaTest: 0.4, transparent: true });
    const material = createDirect3DGeometryMaterial(source, 'linear_depth', WINDOW) as THREE.MeshDepthMaterial;
    expect(material).toBeInstanceOf(THREE.MeshDepthMaterial);
    expect(material.depthPacking).toBe(THREE.BasicDepthPacking);
    expect(material.side).toBe(THREE.DoubleSide);
    expect(material.alphaTest).toBe(0.4);
    expect(material.transparent).toBe(true);
    expect(material.customProgramCacheKey()).toContain('direct3d-linear-depth-v1-50-1500');
    material.dispose();
    source.dispose();
  });

  it('injects the inverse-depth window into the three.js depth shader', () => {
    const material = createDirect3DGeometryMaterial(new THREE.MeshBasicMaterial(), 'linear_depth', WINDOW);
    const shader = compile(material);
    expect(shader.uniforms.cpInvNear.value).toBeCloseTo(1 / 50);
    expect(shader.uniforms.cpInvFar.value).toBeCloseTo(1 / 1500);
    expect(shader.vertexShader).toContain('varying float vCpViewDepth;');
    expect(shader.vertexShader).toContain('vCpViewDepth = -mvPosition.z;');
    expect(shader.fragmentShader).toContain('uniform float cpInvNear;');
    expect(shader.fragmentShader).not.toContain(LINEAR_DEPTH_FRAGMENT_ANCHOR);
    expect(shader.fragmentShader).toContain('gl_FragColor = vec4( vec3( cpInverse ), opacity );');
    material.dispose();
  });

  it('fails loudly when the three.js depth shader no longer matches', () => {
    const material = createDirect3DGeometryMaterial(new THREE.MeshBasicMaterial(), 'linear_depth', WINDOW);
    const shader: FakeShader = { uniforms: {}, vertexShader: 'void main() {}', fragmentShader: 'void main() {}' };
    expect(() => (material.onBeforeCompile as unknown as CompileHook)(shader, {}))
      .toThrow(/depth shader changed/);
    material.dispose();
  });

  it('renders a session to the default framebuffer and restores the scene afterwards', () => {
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x336699);
    const beautyMaterial = new THREE.MeshStandardMaterial();
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(), beautyMaterial);
    const hidden = new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshBasicMaterial());
    hidden.visible = false;
    scene.add(mesh, hidden);
    const seen: Array<{ material: THREE.Material; background: unknown; clearColor: string }> = [];
    const clearColor = new THREE.Color(0xffffff);
    const renderer = {
      getRenderTarget: () => null,
      getViewport: (target: THREE.Vector4) => target.set(0, 0, 1280, 720),
      getScissor: (target: THREE.Vector4) => target.set(0, 0, 1280, 720),
      getScissorTest: () => false,
      getClearColor: (target: THREE.Color) => target.copy(clearColor),
      getClearAlpha: () => 1,
      autoClear: false,
      setClearColor: (color: THREE.ColorRepresentation) => { clearColor.set(color); },
      setRenderTarget: vi.fn(),
      setScissorTest: vi.fn(),
      setViewport: vi.fn(),
      setScissor: vi.fn(),
      render: vi.fn(() => {
        seen.push({ material: mesh.material as THREE.Material, background: scene.background, clearColor: clearColor.getHexString() });
        expect(hidden.visible).toBe(false);
      }),
    } as unknown as THREE.WebGLRenderer;
    const camera = new THREE.PerspectiveCamera();

    const session = createDirect3DLinearDepthSession(renderer, scene, WINDOW);
    session.render(camera);
    session.render(camera);

    expect(renderer.render).toHaveBeenCalledTimes(2);
    expect(seen[0].material).toBeInstanceOf(THREE.MeshDepthMaterial);
    expect(seen[0].material).toBe(seen[1].material); // cached: one shader per source material
    expect(seen[0].background).toBeNull();
    expect(seen[0].clearColor).toBe('000000');
    expect(mesh.material).toBe(beautyMaterial);
    expect(scene.background).toBeInstanceOf(THREE.Color);
    expect(clearColor.getHexString()).toBe('ffffff');
    expect(renderer.autoClear).toBe(false);

    const disposed = vi.spyOn(seen[0].material, 'dispose');
    session.dispose();
    expect(disposed).toHaveBeenCalled();
  });
});
