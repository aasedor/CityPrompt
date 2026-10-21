import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { createPeopleActor } from './peopleAnimation';

function rigFixture() {
  const source = new THREE.Group();
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute([
    0, 0, 0, 0, 1, 0, 0, 2, 0,
  ], 3));
  geometry.setAttribute('skinIndex', new THREE.Uint16BufferAttribute([
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  ], 4));
  geometry.setAttribute('skinWeight', new THREE.Float32BufferAttribute([
    1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0,
  ], 4));
  const texture = new THREE.Texture();
  const material = new THREE.MeshStandardMaterial({ map: texture });
  const mesh = new THREE.SkinnedMesh(geometry, material);
  mesh.name = 'Body';
  const hip = new THREE.Bone();
  hip.name = 'Hip';
  hip.position.y = 1;
  const arm = new THREE.Bone();
  arm.name = 'Arm';
  arm.position.x = 0.25;
  hip.add(arm);
  mesh.add(hip);
  source.add(mesh);
  source.updateMatrixWorld(true);
  mesh.bind(new THREE.Skeleton([hip, arm]));
  const accessory = new THREE.Mesh(geometry, [material, material]);
  accessory.name = 'Accessory';
  source.add(accessory);
  const animations = [
    new THREE.AnimationClip('Walk', 2, [
      new THREE.NumberKeyframeTrack('Hip.rotation[z]', [0, 1, 2], [0, 0.8, 0]),
      new THREE.NumberKeyframeTrack('Arm.position[x]', [0, 1, 2], [0.25, 0.75, 0.25]),
    ]),
    new THREE.AnimationClip('Idle', 1, [
      new THREE.NumberKeyframeTrack('Hip.position[y]', [0, 1], [1, 1.2]),
    ]),
  ];
  const options = { walkClip: 'Walk', idleClip: 'Idle', walkStrideMeters: 2 };
  return { source, mesh, hip, arm, geometry, material, texture, animations, options };
}

function body(root: THREE.Object3D) {
  return root.getObjectByName('Body') as THREE.SkinnedMesh<
    THREE.BufferGeometry, THREE.MeshStandardMaterial
  >;
}

// Mirror GPU arithmetic, including Float32 uniforms and intermediate products,
// rather than hiding cancellation behind Vector3/Matrix4's JS double precision.
function shaderMatrixVector(matrix: ArrayLike<number>, vector: number[]) {
  return [0, 1, 2, 3].map((row) => {
    let result = 0;
    for (let column = 0; column < 4; column++) {
      result = Math.fround(result + Math.fround(Math.fround(matrix[column * 4 + row]) * vector[column]));
    }
    return result;
  });
}

function shaderSkinnedVertex(mesh: THREE.SkinnedMesh, index: number) {
  const position = mesh.geometry.getAttribute('position');
  const skinIndex = mesh.geometry.getAttribute('skinIndex');
  const skinWeight = mesh.geometry.getAttribute('skinWeight');
  const indices = new THREE.Vector4(skinIndex.getX(index), skinIndex.getY(index), skinIndex.getZ(index), skinIndex.getW(index));
  const weights = new THREE.Vector4(skinWeight.getX(index), skinWeight.getY(index), skinWeight.getZ(index), skinWeight.getW(index));
  const vertex = shaderMatrixVector(mesh.bindMatrix.elements, [position.getX(index), position.getY(index), position.getZ(index), 1]);
  const skinned = [0, 0, 0, 0];
  mesh.skeleton.update();
  for (let component = 0; component < 4; component++) {
    const weight = weights.getComponent(component);
    if (weight === 0) continue;
    const matrix = mesh.skeleton.boneMatrices.subarray(indices.getComponent(component) * 16, indices.getComponent(component) * 16 + 16);
    const transformed = shaderMatrixVector(matrix, vertex);
    for (let row = 0; row < 4; row++) {
      skinned[row] = Math.fround(skinned[row] + Math.fround(transformed[row] * weight));
    }
  }
  return new THREE.Vector3().fromArray(shaderMatrixVector(mesh.bindMatrixInverse.elements, skinned));
}

describe('deterministic people actors', () => {
  it('refreshes cached idle bounds for walking picks and restores idle bounds after capture', () => {
    const fixture = rigFixture();
    fixture.geometry.setAttribute('position', new THREE.Float32BufferAttribute([
      0.2, 0, 0, 0.4, 0, 0, 0.3, 0.2, 0,
    ], 3));
    for (let index = 0; index < 3; index++) {
      fixture.geometry.getAttribute('skinIndex').setXYZW(index, 1, 0, 0, 0);
    }
    fixture.mesh.computeBoundingBox();
    fixture.mesh.computeBoundingSphere();
    const sourceBox = fixture.mesh.boundingBox.clone();
    const sourceSphere = fixture.mesh.boundingSphere.clone();
    const actor = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    const mesh = body(actor.root);
    actor.pose(0, 'idle');
    mesh.computeBoundingSphere();
    mesh.computeBoundingBox();
    actor.pose(0.5, 'walk', 2);
    // Triangle centroid translated by the arm's 0.5 m extension, then rotated
    // around the hip at y=1 by 0.8 radians. It lies outside the old idle bounds.
    const walkX = 0.8 * Math.cos(0.8) + (14 / 15) * Math.sin(0.8);
    const walkY = 1 + 0.8 * Math.sin(0.8) - (14 / 15) * Math.cos(0.8);
    const walkingRay = new THREE.Raycaster(new THREE.Vector3(walkX, walkY, 1), new THREE.Vector3(0, 0, -1));
    expect(walkingRay.intersectObject(mesh, false)).toHaveLength(1);
    const walkBounds = new THREE.Box3().setFromObject(mesh);
    for (let index = 0; index < 3; index++) {
      const vertex = mesh.getVertexPosition(index, new THREE.Vector3());
      expect(mesh.boundingSphere.distanceToPoint(vertex)).toBeLessThan(1e-7);
      expect(walkBounds.distanceToPoint(vertex)).toBeLessThan(1e-7);
    }
    actor.pose(0, 'idle');
    const idleRay = new THREE.Raycaster(new THREE.Vector3(0.3, 1 / 15, 1), new THREE.Vector3(0, 0, -1));
    expect(idleRay.intersectObject(mesh, false)).toHaveLength(1);
    expect(walkingRay.intersectObject(mesh, false)).toHaveLength(0);
    const idleBounds = new THREE.Box3().setFromObject(mesh);
    expect(idleBounds.min.x).toBeCloseTo(0.2);
    expect(idleBounds.max.x).toBeCloseTo(0.4);
    expect(idleBounds.max.y).toBeCloseTo(0.2);
    expect(fixture.mesh.boundingBox.equals(sourceBox)).toBe(true);
    expect(fixture.mesh.boundingSphere.equals(sourceSphere)).toBe(true);
    actor.dispose();
  });

  it('keeps GPU skinning and CPU bounds local under an Earth-scale translated and rotated parent', () => {
    const fixture = rigFixture();
    const near = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    const far = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    const earth = new THREE.Group();
    earth.position.set(6378137.123, -1245367.654, 3210654.789);
    earth.rotation.set(0.73, -1.15, 0.37);
    const placement = new THREE.Group();
    placement.position.set(3.25, 0.3, -2.65);
    placement.rotation.y = 0.37;
    placement.add(far.root);
    earth.add(placement);
    earth.updateMatrixWorld(true);
    near.pose(0.25, 'walk', 2);
    far.pose(0.25, 'walk', 2);
    const nearBody = body(near.root), farBody = body(far.root);
    const expected = new THREE.Vector3(-Math.sin(0.4), 1 + Math.cos(0.4), 0);
    expect(nearBody.getVertexPosition(2, new THREE.Vector3()).distanceTo(expected)).toBeLessThan(1e-7);
    const nearGpu = shaderSkinnedVertex(nearBody, 2);
    const farGpu = shaderSkinnedVertex(farBody, 2);
    expect(nearGpu.distanceTo(expected)).toBeLessThan(1e-6);
    expect(farGpu.distanceTo(expected)).toBeLessThan(1e-6);
    expect(farBody.getVertexPosition(2, new THREE.Vector3()).distanceTo(expected)).toBeLessThan(1e-7);
    expect(Math.max(...Array.from(farBody.skeleton.boneMatrices, Math.abs))).toBeLessThan(3);
    farBody.computeBoundingBox();
    nearBody.computeBoundingBox();
    expect(farBody.boundingBox.min.distanceTo(nearBody.boundingBox.min)).toBeLessThan(1e-7);
    expect(farBody.boundingBox.max.distanceTo(nearBody.boundingBox.max)).toBeLessThan(1e-7);
    far.pose(0.5, 'walk', 2);
    // Capture moves the placement after posing; the renderer updates the bone
    // palette later. Recompute in the current frame, not the pose's old world.
    placement.position.z += 1.37;
    placement.rotation.y += 0.21;
    earth.updateMatrixWorld(true);
    expect(shaderSkinnedVertex(farBody, 2).distanceTo(
      new THREE.Vector3(-Math.sin(0.8), 1 + Math.cos(0.8), 0),
    )).toBeLessThan(1e-6);
    expect(shaderSkinnedVertex(nearBody, 2).distanceTo(nearGpu)).toBeLessThan(1e-7);
    far.dispose();
    near.dispose();
  });

  it('preserves authored bind transforms and blended weights without modifying cached rigs or Three prototypes', () => {
    const fixture = rigFixture();
    fixture.source.position.set(0.3, 0.1, -0.15);
    fixture.source.rotation.set(-0.2, 0.25, 0.15);
    fixture.source.scale.set(0.75, 1.25, 1.1);
    fixture.mesh.position.set(0.2, 0.05, -0.1);
    fixture.mesh.rotation.set(0.1, 0.2, -0.1);
    fixture.mesh.scale.set(0.8, 1.2, 0.9);
    fixture.geometry.getAttribute('skinIndex').setXYZW(2, 0, 1, 0, 0);
    fixture.geometry.getAttribute('skinWeight').setXYZW(2, 0.25, 0.75, 0, 0);
    fixture.source.updateMatrixWorld(true);
    fixture.mesh.bind(fixture.mesh.skeleton);
    const authoredBind = fixture.mesh.bindMatrix.clone();
    const near = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    const far = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    const earth = new THREE.Group();
    earth.position.set(-2458567.127, -4321765.818, 4356782.265);
    earth.rotation.set(0.3, -0.7, 1.1);
    earth.add(far.root);
    earth.updateMatrixWorld(true);
    near.pose(0.25, 'walk', 2);
    far.pose(0.25, 'walk', 2);
    // Compare with unmodified Three attached skinning at a small origin. This
    // catches losing the authored bind matrix or applying mesh transforms twice.
    const sourceMixer = new THREE.AnimationMixer(fixture.source);
    sourceMixer.clipAction(fixture.animations[0]).play();
    sourceMixer.setTime(0.5);
    fixture.source.updateMatrixWorld(true);
    const expected = fixture.mesh.getVertexPosition(2, new THREE.Vector3());
    const nearBody = body(near.root), farBody = body(far.root);
    expect(nearBody.getVertexPosition(2, new THREE.Vector3()).distanceTo(expected)).toBeLessThan(1e-7);
    expect(farBody.getVertexPosition(2, new THREE.Vector3()).distanceTo(expected)).toBeLessThan(1e-7);
    expect(shaderSkinnedVertex(nearBody, 2).distanceTo(expected)).toBeLessThan(1e-6);
    expect(shaderSkinnedVertex(farBody, 2).distanceTo(expected)).toBeLessThan(1e-6);
    expect(fixture.mesh.bindMatrix.equals(authoredBind)).toBe(true);
    expect(fixture.mesh.bindMode).toBe(THREE.AttachedBindMode);
    expect(fixture.mesh.applyBoneTransform).toBe(THREE.SkinnedMesh.prototype.applyBoneTransform);
    expect(fixture.mesh.skeleton.update).toBe(THREE.Skeleton.prototype.update);
    sourceMixer.stopAllAction();
    sourceMixer.uncacheRoot(fixture.source);
    far.dispose();
    near.dispose();
  });

  it('copies skeleton state so two actors can hold different poses of the same cached rig', () => {
    const fixture = rigFixture();
    const first = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    const second = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    first.pose(0.25, 'walk', 2);
    second.pose(0.75, 'walk', 2);
    const firstBody = body(first.root);
    const secondBody = body(second.root);
    expect(firstBody.skeleton).not.toBe(secondBody.skeleton);
    expect(firstBody.skeleton.bones[0]).not.toBe(fixture.hip);
    expect(firstBody.skeleton.bones[0].rotation.z).toBeCloseTo(0.4);
    expect(secondBody.skeleton.bones[0].rotation.z).toBeCloseTo(0.4);
    expect(firstBody.skeleton.bones[1].position.x).toBeCloseTo(0.5);
    second.pose(0.5, 'walk', 2);
    expect(secondBody.skeleton.bones[0].rotation.z).toBeCloseTo(0.8);
    expect(firstBody.skeleton.bones[0].rotation.z).toBeCloseTo(0.4);
    expect(fixture.hip.rotation.z).toBe(0);
    expect(fixture.arm.position.x).toBe(0.25);
    const vertex = firstBody.getVertexPosition(2, new THREE.Vector3());
    expect(vertex.x).toBeCloseTo(-Math.sin(0.4));
    expect(vertex.y).toBeCloseTo(1 + Math.cos(0.4));
    first.dispose();
    second.dispose();
  });

  it('seeks by distance and source clip duration without accumulating warmup or out-of-order calls', () => {
    const fixture = rigFixture();
    const actor = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    const hip = body(actor.root).skeleton.bones[0];
    actor.pose(0.25, 'walk', 2, 0.25);
    expect(hip.rotation.z).toBeCloseTo(0.6);
    actor.pose(100.75, 'walk', 2, 0.25);
    actor.pose(0, 'walk', 0, 0);
    actor.pose(0.25, 'walk', 2, 0.25);
    expect(hip.rotation.z).toBeCloseTo(0.6);
    actor.pose(0.25, 'walk', 2, 0.25);
    expect(hip.rotation.z).toBeCloseTo(0.6);
    actor.pose(0.5, 'walk'); // Default 1 m/s: half a clip-second for a two-metre stride.
    expect(hip.rotation.z).toBeCloseTo(0.4);
    actor.pose(999, 'walk', 0, -0.5);
    expect(hip.rotation.z).toBeCloseTo(0.4);
    actor.dispose();
  });

  it('freezes idle at its phase and restores properties absent from the next clip', () => {
    const fixture = rigFixture();
    const actor = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    actor.root.position.set(12, 3, 8);
    const [hip, arm] = body(actor.root).skeleton.bones;
    actor.pose(0.5, 'walk', 2);
    expect(hip.rotation.z).toBeCloseTo(0.8);
    actor.pose(0, 'idle', 1, 0.5);
    expect(hip.rotation.z).toBeCloseTo(0);
    expect(arm.position.x).toBe(0.25);
    expect(hip.position.y).toBeCloseTo(1.1);
    actor.pose(400, 'idle', 1, 0.5);
    expect(hip.position.y).toBeCloseTo(1.1);
    actor.pose(0.5, 'walk', 2);
    expect(hip.position.y).toBe(1);
    expect(hip.rotation.z).toBeCloseTo(0.8);
    expect(actor.root.position.toArray()).toEqual([12, 3, 8]);
    actor.dispose();
  });

  it('isolates materials while sharing geometry/textures and disposes only owned resources once', () => {
    const fixture = rigFixture();
    const first = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    const second = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    const firstBody = body(first.root);
    const secondBody = body(second.root);
    const accessory = first.root.getObjectByName('Accessory') as THREE.Mesh;
    expect(firstBody.geometry).toBe(fixture.geometry);
    expect(firstBody.material).not.toBe(fixture.material);
    expect(firstBody.material).not.toBe(secondBody.material);
    expect(accessory.material).toEqual([firstBody.material, firstBody.material]);
    expect(firstBody.material.map).toBe(fixture.texture);
    firstBody.material.color.set('red');
    expect(secondBody.material.color.getHex()).toBe(0xffffff);
    expect(fixture.material.color.getHex()).toBe(0xffffff);
    let clonedDisposals = 0;
    let sharedDisposals = 0;
    firstBody.material.addEventListener('dispose', () => clonedDisposals++);
    fixture.geometry.addEventListener('dispose', () => sharedDisposals++);
    fixture.texture.addEventListener('dispose', () => sharedDisposals++);
    fixture.material.addEventListener('dispose', () => sharedDisposals++);
    first.pose(0.5, 'walk');
    first.dispose();
    first.dispose();
    expect(clonedDisposals).toBe(1);
    expect(sharedDisposals).toBe(0);
    expect(() => first.pose(0, 'walk')).toThrow(/disposed/i);
    second.pose(0.5, 'walk', 2);
    expect(secondBody.skeleton.bones[0].rotation.z).toBeCloseTo(0.8);
    second.dispose();
  });

  it('releases allocated bone textures for every owned skeleton while preserving the cached source and other actors', () => {
    const fixture = rigFixture();
    fixture.mesh.skeleton.computeBoneTexture();
    const sourceBoneTexture = fixture.mesh.skeleton.boneTexture!;
    const clothing = new THREE.SkinnedMesh(fixture.geometry, fixture.material);
    clothing.name = 'Clothing';
    clothing.bind(fixture.mesh.skeleton, fixture.mesh.bindMatrix);
    fixture.source.add(clothing);
    const first = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    const second = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    const ownedSkeletons = [
      body(first.root).skeleton,
      (first.root.getObjectByName('Clothing') as THREE.SkinnedMesh).skeleton,
    ];
    let ownedTextureDisposals = 0;
    let cachedTextureDisposals = 0;
    let secondTextureDisposals = 0;
    sourceBoneTexture.addEventListener('dispose', () => cachedTextureDisposals++);
    for (const skeleton of ownedSkeletons) {
      expect(skeleton.boneTexture).toBeNull();
      skeleton.computeBoneTexture();
      expect(skeleton.boneTexture).not.toBe(sourceBoneTexture);
      skeleton.boneTexture!.addEventListener('dispose', () => ownedTextureDisposals++);
    }
    const secondSkeleton = body(second.root).skeleton;
    secondSkeleton.computeBoneTexture();
    const secondBoneTexture = secondSkeleton.boneTexture;
    secondBoneTexture!.addEventListener('dispose', () => secondTextureDisposals++);
    first.pose(0.5, 'walk', 2);
    first.dispose();
    first.dispose();
    expect(ownedTextureDisposals).toBe(2);
    expect(ownedSkeletons.map((skeleton) => skeleton.boneTexture)).toEqual([null, null]);
    expect(fixture.mesh.skeleton.boneTexture).toBe(sourceBoneTexture);
    expect(cachedTextureDisposals).toBe(0);
    expect(secondSkeleton.boneTexture).toBe(secondBoneTexture);
    expect(secondTextureDisposals).toBe(0);
    second.pose(0.5, 'walk', 2);
    expect(secondSkeleton.bones[0].rotation.z).toBeCloseTo(0.8);
    second.dispose();
    expect(secondTextureDisposals).toBe(1);
    fixture.mesh.skeleton.dispose();
  });

  it.each([0, -1, Number.NaN, Infinity])('rejects invalid metre stride %s', (stride) => {
    const fixture = rigFixture();
    expect(() => createPeopleActor(fixture.source, fixture.animations, {
      ...fixture.options, walkStrideMeters: stride,
    })).toThrow(/walkStrideMeters/);
  });

  it('rejects missing or unusable named clips before creating an actor', () => {
    const fixture = rigFixture();
    expect(() => createPeopleActor(fixture.source, [], fixture.options)).toThrow(/Walk/);
    expect(() => createPeopleActor(fixture.source, fixture.animations, {
      ...fixture.options, idleClip: 'MissingIdle',
    })).toThrow(/MissingIdle/);
    fixture.animations[0].duration = 0;
    expect(() => createPeopleActor(fixture.source, fixture.animations, fixture.options))
      .toThrow(/Walk.*duration/);
  });

  it('rejects invalid absolute times, speed, phase and mode without changing the previous pose', () => {
    const fixture = rigFixture();
    const actor = createPeopleActor(fixture.source, fixture.animations, fixture.options);
    actor.pose(0.5, 'walk', 2);
    for (const time of [-1, Number.NaN, Infinity]) {
      expect(() => actor.pose(time, 'walk')).toThrow(/timeSeconds/);
    }
    for (const speed of [-1, Number.NaN, Infinity]) {
      expect(() => actor.pose(0, 'walk', speed)).toThrow(/speedMetersPerSecond/);
    }
    expect(() => actor.pose(0, 'walk', 1, Number.NaN)).toThrow(/phaseSeconds/);
    expect(() => actor.pose(0, 'fly' as 'walk')).toThrow(/mode/);
    expect(body(actor.root).skeleton.bones[0].rotation.z).toBeCloseTo(0.8);
    actor.dispose();
  });
});
