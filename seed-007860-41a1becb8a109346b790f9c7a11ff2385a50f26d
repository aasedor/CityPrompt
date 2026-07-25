import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import {
  analyzeDirect3DClassPixels,
  computeDirect3DCaptureSize,
  createDirect3DSemanticMaterial,
  DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA,
  DIRECT_3D_CLASS_COLORS,
  DIRECT_3D_CLASS_ID_MANIFEST,
  direct3DGroundRoleForCommunityKind,
  Direct3DCaptureError,
  direct3DProposalUserData,
  disposeDirect3DSemanticMaterial,
  getDirect3DProposalRole,
  getDirect3DTargetSampleCount,
  isExcludedFromDirect3DCapture,
  validateDirect3DMaskCoverage,
} from './direct3dCapture';

function hexRgb(hex: string): [number, number, number] {
  const value = Number.parseInt(hex.slice(1), 16);
  return [(value >> 16) & 0xff, (value >> 8) & 0xff, value & 0xff];
}

describe('Direct 3D capture helpers', () => {
  it('caps the long edge without changing aspect ratio or upscaling', () => {
    expect(computeDirect3DCaptureSize(4096, 2048)).toEqual({ width: 2048, height: 1024 });
    expect(computeDirect3DCaptureSize(1600, 900)).toEqual({ width: 1600, height: 900 });
    expect(() => computeDirect3DCaptureSize(0, 900)).toThrow(Direct3DCaptureError);
  });

  it('uses bounded beauty MSAA and no class-ID multisampling', () => {
    expect(getDirect3DTargetSampleCount(true, 'beauty')).toBe(2);
    expect(getDirect3DTargetSampleCount(true, 'class-id')).toBe(0);
    expect(getDirect3DTargetSampleCount(false, 'beauty')).toBe(0);
    expect(getDirect3DTargetSampleCount(false, 'class-id')).toBe(0);
  });

  it('inherits proposal roles and editor exclusions from named scene roots', () => {
    const proposalRoot = new THREE.Group();
    proposalRoot.userData = direct3DProposalUserData('ground');
    const nested = new THREE.Group();
    nested.userData = direct3DProposalUserData('park');
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshBasicMaterial());
    proposalRoot.add(nested);
    nested.add(mesh);

    expect(getDirect3DProposalRole(mesh)).toBe('park');
    expect(isExcludedFromDirect3DCapture(mesh)).toBe(false);

    nested.userData = { ...DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA };
    expect(isExcludedFromDirect3DCapture(mesh)).toBe(true);
  });

  it('assigns compiled public-realm bases to their exact semantic owner', () => {
    expect(direct3DGroundRoleForCommunityKind('park')).toBe('park');
    expect(direct3DGroundRoleForCommunityKind('street')).toBe('street');
    expect(direct3DGroundRoleForCommunityKind('building')).toBe('ground');
    expect(direct3DGroundRoleForCommunityKind(null)).toBe('ground');
  });

  it('preserves mesh cutouts, transparency, side, polygon offset, and depth policy', () => {
    const map = new THREE.Texture();
    const alphaMap = new THREE.Texture();
    const original = new THREE.MeshStandardMaterial({
      map,
      alphaMap,
      transparent: true,
      opacity: 0.61,
      alphaTest: 0.43,
      side: THREE.DoubleSide,
      depthTest: true,
      depthWrite: false,
      polygonOffset: true,
      polygonOffsetFactor: -4,
      polygonOffsetUnits: -8,
    });
    original.depthFunc = THREE.GreaterEqualDepth;
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(), original);
    const semantic = createDirect3DSemanticMaterial(original, 'landscape', mesh) as THREE.MeshBasicMaterial;

    expect(semantic.color.getHexString()).toBe(DIRECT_3D_CLASS_COLORS.landscape.slice(1));
    expect(semantic.map).toBe(map);
    expect(semantic.alphaMap).toBe(alphaMap);
    expect(semantic.transparent).toBe(true);
    expect(semantic.opacity).toBe(0.61);
    expect(semantic.alphaTest).toBe(0.43);
    expect(semantic.side).toBe(THREE.DoubleSide);
    expect(semantic.depthTest).toBe(true);
    expect(semantic.depthWrite).toBe(false);
    expect(semantic.depthFunc).toBe(THREE.GreaterEqualDepth);
    expect(semantic.polygonOffset).toBe(true);
    expect(semantic.polygonOffsetFactor).toBe(-4);
    expect(semantic.polygonOffsetUnits).toBe(-8);

    const shader = { fragmentShader: '#include <map_fragment>' };
    const compile = semantic.onBeforeCompile as unknown as (value: typeof shader) => void;
    compile(shader);
    expect(shader.fragmentShader).toContain('diffuseColor.a *= sampledDiffuseColor.a');
    expect(shader.fragmentShader).not.toContain('diffuseColor *= sampledDiffuseColor');

    disposeDirect3DSemanticMaterial(semantic);
    original.dispose();
    mesh.geometry.dispose();
    map.dispose();
    alphaMap.dispose();
  });

  it('preserves material-array slots and point-card alpha without beauty RGB', () => {
    const map = new THREE.Texture();
    const first = new THREE.MeshBasicMaterial({ side: THREE.BackSide, depthWrite: false });
    const second = new THREE.MeshBasicMaterial({
      map,
      transparent: true,
      alphaTest: 0.5,
      polygonOffset: true,
      polygonOffsetFactor: -2,
    });
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(), [first, second]);
    const semanticArray = createDirect3DSemanticMaterial(
      [first, second],
      'building',
      mesh,
    ) as THREE.Material[];

    expect(semanticArray).toHaveLength(2);
    expect(semanticArray[0]).toBeInstanceOf(THREE.MeshBasicMaterial);
    expect(semanticArray[0].side).toBe(THREE.BackSide);
    expect(semanticArray[0].depthWrite).toBe(false);
    expect((semanticArray[1] as THREE.MeshBasicMaterial).map).toBe(map);
    expect(semanticArray[1].alphaTest).toBe(0.5);
    expect(semanticArray[1].polygonOffset).toBe(true);
    expect(semanticArray[1].polygonOffsetFactor).toBe(-2);

    const pointsSource = new THREE.PointsMaterial({
      map,
      transparent: true,
      alphaTest: 0.25,
      size: 7,
      sizeAttenuation: true,
    });
    const points = new THREE.Points(new THREE.BufferGeometry(), pointsSource);
    const pointsSemantic = createDirect3DSemanticMaterial(
      pointsSource,
      'landscape',
      points,
    ) as THREE.PointsMaterial;
    const shader = { fragmentShader: '#include <map_particle_fragment>' };
    const compile = pointsSemantic.onBeforeCompile as unknown as (value: typeof shader) => void;
    compile(shader);

    expect(pointsSemantic.size).toBe(7);
    expect(pointsSemantic.sizeAttenuation).toBe(true);
    expect(shader.fragmentShader).toContain('diffuseColor.a *= texture2D( map, uv ).a');
    expect(shader.fragmentShader).not.toContain('diffuseColor *= texture2D( map, uv )');

    disposeDirect3DSemanticMaterial(semanticArray);
    disposeDirect3DSemanticMaterial(pointsSemantic);
    first.dispose();
    second.dispose();
    pointsSource.dispose();
    mesh.geometry.dispose();
    points.geometry.dispose();
    map.dispose();
  });

  it('turns the bottom-up semantic pass into exact top-down mask and class PNG pixels', () => {
    const ground = hexRgb(DIRECT_3D_CLASS_COLORS.ground);
    const landscape = hexRgb(DIRECT_3D_CLASS_COLORS.landscape);
    const building = hexRgb(DIRECT_3D_CLASS_COLORS.building);
    // WebGL readback order: bottom row first, then top row.
    const readback = new Uint8Array([
      ...building, 255, 0, 0, 0, 0,
      ...ground, 255, ...landscape, 255,
    ]);

    const result = analyzeDirect3DClassPixels(readback, 2, 2);

    expect([...result.classIdPixels.slice(0, 3)]).toEqual(ground);
    expect([...result.classIdPixels.slice(4, 7)]).toEqual(landscape);
    expect([...result.classIdPixels.slice(8, 11)]).toEqual(building);
    expect([...result.classIdPixels.slice(12, 15)]).toEqual([0, 0, 0]);
    expect(result.proposalPixelCount).toBe(3);
    expect(result.contextPixelCount).toBe(1);
    expect(result.maskCoverage).toBe(0.75);
    expect(result.classCoverage).toEqual({ ground: 0.25, landscape: 0.25, building: 0.25 });
    expect(result.maskPixels[0]).toBe(255);
    expect(result.maskPixels[12]).toBe(0);
  });

  it('fails closed for empty and context-free proposal masks', () => {
    expect(() => validateDirect3DMaskCoverage(0, 0)).toThrowError(
      expect.objectContaining({ code: 'no_proposal_content' }),
    );
    expect(() => validateDirect3DMaskCoverage(0.99, 10_000)).toThrowError(
      expect.objectContaining({ code: 'invalid_mask_coverage' }),
    );
    expect(() => validateDirect3DMaskCoverage(0.35, 10_000)).not.toThrow();
  });

  it('exports a unique, stable semantic color manifest', () => {
    expect(DIRECT_3D_CLASS_ID_MANIFEST).toEqual({
      '#F4E04D': 'ground',
      '#30C875': 'landscape',
      '#EF6A3A': 'street',
      '#35A7FF': 'park',
      '#B452FF': 'building',
    });
    expect(new Set(Object.keys(DIRECT_3D_CLASS_ID_MANIFEST)).size).toBe(5);
  });
});
