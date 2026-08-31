import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import {
  analyzeDirect3DClassPixels,
  analyzeDirect3DInstancePixels,
  analyzeDirect3DMaterialPixels,
  buildDirect3DMaterialColorManifest,
  buildDirect3DInstanceColorManifest,
  computeDirect3DCaptureSize,
  createDirect3DSemanticMaterial,
  DIRECT_3D_CAPTURE_CONTEXT_USER_DATA,
  DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA,
  DIRECT_3D_CLASS_COLORS,
  DIRECT_3D_CLASS_ID_MANIFEST,
  direct3DGroundRoleForCommunityKind,
  direct3DInstanceUserData,
  Direct3DCaptureError,
  direct3DProposalUserData,
  direct3DStreetJunctionInstanceDescriptor,
  direct3DZoneInstanceDescriptor,
  disposeDirect3DSemanticMaterial,
  getDirect3DInstanceDescriptor,
  getDirect3DProposalRole,
  getDirect3DTargetSampleCount,
  isExcludedFromDirect3DCapture,
  MAX_DIRECT_3D_INSTANCES,
  requireDirect3DInstanceDescriptor,
  validateDirect3DInstanceSemanticAgreement,
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
    expect(getDirect3DTargetSampleCount(true, 'instance-id')).toBe(0);
    expect(getDirect3DTargetSampleCount(true, 'depth')).toBe(0);
    expect(getDirect3DTargetSampleCount(true, 'normal')).toBe(0);
    expect(getDirect3DTargetSampleCount(false, 'beauty')).toBe(0);
    expect(getDirect3DTargetSampleCount(false, 'class-id')).toBe(0);
  });

  it('collapses cloned materials into stable source families before the 2,048-color gate', () => {
    const source = new THREE.MeshStandardMaterial({ color: 0xa47f66, roughness: 0.72 });
    source.name = 'RLASM_Source_Stucco';
    source.userData = { source_specific: true };
    const clones = Array.from({ length: MAX_DIRECT_3D_INSTANCES + 1 }, () => source.clone());
    const geometry = new THREE.BoxGeometry();
    const result = buildDirect3DMaterialColorManifest(clones.map((material) => ({
      object: new THREE.Mesh(geometry, material),
      visible: true,
      effectivelyVisible: true,
      material,
      role: 'building' as const,
      instance: null,
      excluded: false,
    })));

    expect(result.assignments).toHaveLength(MAX_DIRECT_3D_INSTANCES + 1);
    expect(Object.keys(result.manifest)).toHaveLength(1);
    expect(Object.values(result.manifest)[0]).toMatchObject({
      label: 'RLASM_Source_Stucco',
      semantic_class: 'building',
      source_specific: true,
    });

    for (const material of clones) material.dispose();
    geometry.dispose();
    source.dispose();
  });

  it('partitions exact material colors by semantic role', () => {
    const material = new THREE.MeshStandardMaterial({ color: 0x777777 });
    material.name = 'Shared neutral';
    const geometry = new THREE.BoxGeometry();
    const result = buildDirect3DMaterialColorManifest((['street', 'building'] as const).map((role) => ({
      object: new THREE.Mesh(geometry, material),
      visible: true,
      effectivelyVisible: true,
      material,
      role,
      instance: null,
      excluded: false,
    })));
    const colors = Object.keys(result.manifest);
    const red = colors.map((color) => Number.parseInt(color.slice(1, 3), 16));

    expect(Object.values(result.manifest).map((entry) => entry.semantic_class).sort()).toEqual([
      'building',
      'street',
    ]);
    expect(Math.abs(red[0] - red[1])).toBeGreaterThan(10);

    geometry.dispose();
    material.dispose();
  });

  it('uses the class pass to disambiguate material-color blends at semantic boundaries', () => {
    const material = new THREE.MeshStandardMaterial({ color: 0x777777 });
    material.name = 'Shared neutral';
    const geometry = new THREE.BoxGeometry();
    const { manifest } = buildDirect3DMaterialColorManifest((['street', 'building'] as const).map((role) => ({
      object: new THREE.Mesh(geometry, material),
      visible: true,
      effectivelyVisible: true,
      material,
      role,
      instance: null,
      excluded: false,
    })));
    const materialColorByRole = new Map(Object.entries(manifest).map(([color, descriptor]) => (
      [descriptor.semantic_class, hexRgb(color)]
    )));
    const streetMaterial = materialColorByRole.get('street') as [number, number, number];
    const buildingMaterial = materialColorByRole.get('building') as [number, number, number];
    const buildingClass = hexRgb(DIRECT_3D_CLASS_COLORS.building);

    const result = analyzeDirect3DMaterialPixels(
      new Uint8Array([...streetMaterial, 255]),
      1,
      1,
      manifest,
      new Uint8ClampedArray([...buildingClass, 255]),
    );

    expect([...result.slice(0, 3)]).toEqual(buildingMaterial);

    geometry.dispose();
    material.dispose();
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

  it('keeps legacy model subtrees visible context without inheriting a proposal role', () => {
    const proposalRoot = new THREE.Group();
    proposalRoot.userData = direct3DProposalUserData('building');
    const legacyModel = new THREE.Group();
    legacyModel.userData = { ...DIRECT_3D_CAPTURE_CONTEXT_USER_DATA };
    const legacyMesh = new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshBasicMaterial());
    proposalRoot.add(legacyModel);
    legacyModel.add(legacyMesh);

    expect(getDirect3DProposalRole(legacyMesh)).toBeNull();
    expect(isExcludedFromDirect3DCapture(legacyMesh)).toBe(false);

    legacyMesh.geometry.dispose();
    (legacyMesh.material as THREE.Material).dispose();
  });

  it('inherits the nearest stable instance tag and clears it in context-only subtrees', () => {
    const proposalRoot = new THREE.Group();
    proposalRoot.userData = direct3DProposalUserData('building');
    const buildingRoot = new THREE.Group();
    buildingRoot.userData = direct3DInstanceUserData(direct3DZoneInstanceDescriptor(
      'zone-a',
      'building',
      { building_id: 'building-a' },
    ));
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshBasicMaterial());
    proposalRoot.add(buildingRoot);
    buildingRoot.add(mesh);

    expect(getDirect3DInstanceDescriptor(mesh)).toEqual({
      instance_id: 'zone:zone-a:building',
      semantic_class: 'building',
      zone_id: 'zone-a',
      building_id: 'building-a',
    });

    mesh.userData = { ...DIRECT_3D_CAPTURE_CONTEXT_USER_DATA };
    expect(getDirect3DInstanceDescriptor(mesh)).toBeNull();

    mesh.geometry.dispose();
    (mesh.material as THREE.Material).dispose();
  });

  it('fails closed when visible proposal geometry is missing or mismatches an instance tag', () => {
    expect(() => requireDirect3DInstanceDescriptor('building', null)).toThrowError(
      expect.objectContaining({ code: 'capture_failed' }),
    );
    expect(() => requireDirect3DInstanceDescriptor('building', {
      instance_id: 'zone:park-a:park',
      semantic_class: 'park',
      zone_id: 'park-a',
    })).toThrowError(expect.objectContaining({ code: 'capture_failed' }));
    expect(requireDirect3DInstanceDescriptor(null, null)).toBeNull();
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

  it('makes physical glazing opaque in exact-color ID passes', () => {
    const glass = new THREE.MeshPhysicalMaterial({
      transparent: true,
      opacity: 0.62,
      transmission: 0.48,
      depthWrite: false,
    });
    glass.name = 'RLASM_Window_Glass';
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(), glass);
    const semantic = createDirect3DSemanticMaterial(glass, 'building', mesh) as THREE.Material;

    expect(semantic.transparent).toBe(false);
    expect(semantic.opacity).toBe(1);
    expect(semantic.depthWrite).toBe(true);

    semantic.dispose();
    glass.dispose();
    mesh.geometry.dispose();
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

  it('keeps touching building instances separate in an exact top-down ID pass', () => {
    const buildingA = direct3DZoneInstanceDescriptor('zone-a', 'building', {
      building_id: 'building-a',
    });
    const buildingB = direct3DZoneInstanceDescriptor('zone-b', 'building', {
      building_id: 'building-b',
    });
    const { assignments, manifest } = buildDirect3DInstanceColorManifest([buildingA, buildingB]);
    const colorById = new Map(assignments.map((entry) => (
      [entry.descriptor.instance_id, hexRgb(entry.color)]
    )));
    const colorA = colorById.get(buildingA.instance_id) as [number, number, number];
    const colorB = colorById.get(buildingB.instance_id) as [number, number, number];
    const readback = new Uint8Array([
      ...colorA, 255,
      ...colorB, 255,
    ]);

    const result = analyzeDirect3DInstancePixels(readback, 2, 1, manifest);

    expect([...result.instanceIdPixels.slice(0, 3)]).toEqual(colorA);
    expect([...result.instanceIdPixels.slice(4, 7)]).toEqual(colorB);
    expect(result.pixelCounts).toEqual({
      [buildingA.instance_id]: 1,
      [buildingB.instance_id]: 1,
    });
  });

  it('uses the class pass to disambiguate transparent instance-color blends', () => {
    const ground = direct3DZoneInstanceDescriptor('zone-a', 'ground');
    const building = direct3DZoneInstanceDescriptor('zone-a', 'building', {
      building_id: 'building-a',
    });
    const { assignments, manifest } = buildDirect3DInstanceColorManifest([ground, building]);
    const colorById = new Map(assignments.map((entry) => (
      [entry.descriptor.instance_id, hexRgb(entry.color)]
    )));
    const groundColor = colorById.get(ground.instance_id) as [number, number, number];
    const buildingColor = colorById.get(building.instance_id) as [number, number, number];
    const buildingClass = hexRgb(DIRECT_3D_CLASS_COLORS.building);

    const result = analyzeDirect3DInstancePixels(
      new Uint8Array([...groundColor, 255]),
      1,
      1,
      manifest,
      new Uint8ClampedArray([...buildingClass, 255]),
    );

    expect([...result.instanceIdPixels.slice(0, 3)]).toEqual(buildingColor);
    expect(result.pixelCounts).toEqual({ [building.instance_id]: 1 });
  });

  it('tags intersecting street segments and their graph-owned junction separately', () => {
    const streetRoot = new THREE.Group();
    streetRoot.userData = direct3DProposalUserData('street');
    const firstStreet = new THREE.Group();
    firstStreet.userData = direct3DInstanceUserData(
      direct3DZoneInstanceDescriptor('street-a', 'street'),
    );
    const secondStreet = new THREE.Group();
    secondStreet.userData = direct3DInstanceUserData(
      direct3DZoneInstanceDescriptor('street-b', 'street'),
    );
    const junction = new THREE.Group();
    const junctionDescriptor = direct3DStreetJunctionInstanceDescriptor([
      'street-b',
      'street-a',
      'street-a',
    ]);
    junction.userData = direct3DInstanceUserData(junctionDescriptor);
    const firstMesh = new THREE.Mesh();
    const secondMesh = new THREE.Mesh();
    const junctionMesh = new THREE.Mesh();
    streetRoot.add(firstStreet, secondStreet, junction);
    firstStreet.add(firstMesh);
    secondStreet.add(secondMesh);
    junction.add(junctionMesh);

    expect(getDirect3DInstanceDescriptor(firstMesh)?.instance_id).toBe('zone:street-a:street');
    expect(getDirect3DInstanceDescriptor(secondMesh)?.instance_id).toBe('zone:street-b:street');
    expect(getDirect3DInstanceDescriptor(junctionMesh)).toEqual({
      instance_id: junctionDescriptor.instance_id,
      semantic_class: 'street',
      source_zone_ids: ['street-a', 'street-b'],
    });
    expect(direct3DStreetJunctionInstanceDescriptor(['street-a', 'street-b'])).toEqual(
      junctionDescriptor,
    );
    expect(() => direct3DStreetJunctionInstanceDescriptor(['street-a'])).toThrow(
      'at least two persisted street sources',
    );
  });

  it('rejects class and instance ownership disagreements before a paid render', () => {
    const descriptor = direct3DZoneInstanceDescriptor('building-a', 'building');
    const { assignments, manifest } = buildDirect3DInstanceColorManifest([descriptor]);
    const instanceRgb = hexRgb(assignments[0].color);
    const buildingRgb = hexRgb(DIRECT_3D_CLASS_COLORS.building);
    const groundRgb = hexRgb(DIRECT_3D_CLASS_COLORS.ground);
    const instancePixels = new Uint8ClampedArray([...instanceRgb, 255]);

    expect(() => validateDirect3DInstanceSemanticAgreement(
      new Uint8ClampedArray([...buildingRgb, 255]),
      instancePixels,
      1,
      1,
      manifest,
    )).not.toThrow();
    expect(() => validateDirect3DInstanceSemanticAgreement(
      new Uint8ClampedArray([...groundRgb, 255]),
      instancePixels,
      1,
      1,
      manifest,
    )).toThrow('conflicts with its semantic class');
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

  it('exports a stable unique instance manifest even when an instance has zero pixels', () => {
    const descriptors = [
      direct3DZoneInstanceDescriptor('park-a', 'park'),
      direct3DZoneInstanceDescriptor('building-a', 'building', { building_id: 'bldg-a' }),
      direct3DZoneInstanceDescriptor('street-a', 'street'),
    ];
    const forward = buildDirect3DInstanceColorManifest(descriptors);
    const reversed = buildDirect3DInstanceColorManifest([...descriptors].reverse());

    expect(forward.manifest).toEqual(reversed.manifest);
    expect(new Set(Object.keys(forward.manifest)).size).toBe(descriptors.length);
    expect(Object.values(forward.manifest).map((entry) => entry.instance_id).sort()).toEqual(
      descriptors.map((entry) => entry.instance_id).sort(),
    );

    const visible = forward.assignments[0];
    const visibleRgb = hexRgb(visible.color);
    const analysis = analyzeDirect3DInstancePixels(
      new Uint8Array([...visibleRgb, 255]),
      1,
      1,
      forward.manifest,
    );
    expect(analysis.pixelCounts[visible.descriptor.instance_id]).toBe(1);
    expect(Object.keys(forward.manifest)).toHaveLength(3);
  });

  it('fails locally at the same 2,048-instance limit as the API schema', () => {
    const descriptors = Array.from({ length: MAX_DIRECT_3D_INSTANCES + 1 }, (_, index) => (
      direct3DZoneInstanceDescriptor(`zone-${index}`, 'building', {
        building_id: `building-${index}`,
      })
    ));

    expect(() => buildDirect3DInstanceColorManifest(descriptors)).toThrowError(
      expect.objectContaining({ code: 'capture_failed' }),
    );
  });
});
