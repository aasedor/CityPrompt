import * as THREE from 'three';
import { clone } from 'three/examples/jsm/utils/SkeletonUtils.js';

export interface PeopleActorOptions {
  walkClip: string;
  idleClip: string;
  walkStrideMeters: number;
}

export interface PeopleActor {
  root: THREE.Object3D;
  pose(
    timeSeconds: number,
    mode: 'idle' | 'walk',
    speedMetersPerSecond?: number,
    phaseSeconds?: number,
  ): void;
  dispose(): void;
}

function requireClip(animations: readonly THREE.AnimationClip[], name: string) {
  const matches = animations.filter((clip) => clip.name === name);
  if (!name.trim() || matches.length !== 1) {
    throw new Error(`People actor requires exactly one animation clip named "${name}"`);
  }
  const clip = matches[0];
  if (!Number.isFinite(clip.duration) || clip.duration <= 0) {
    throw new Error(`People animation "${name}" must have a finite positive duration`);
  }
  return clip;
}

/** Keep Earth-centred coordinates out of the Float32 skinning uniforms/palette. */
function localizeSkinning(mesh: THREE.SkinnedMesh) {
  const skeleton = mesh.skeleton;
  const originalBind = mesh.bindMatrix.clone();
  const worldInverse = new THREE.Matrix4();
  const boneMatrix = new THREE.Matrix4();
  const identity = new THREE.Matrix4();
  const base = new THREE.Vector3();
  const weighted = new THREE.Vector3();
  const indices = new THREE.Vector4();
  const weights = new THREE.Vector4();

  function localBoneMatrix(index: number) {
    return boneMatrix.copy(worldInverse)
      .multiply(skeleton.bones[index]?.matrixWorld ?? identity)
      .multiply(skeleton.boneInverses[index])
      .multiply(originalBind);
  }

  // Attached skinning ordinarily subtracts the mesh world transform in the
  // shader, after an Earth-sized bone transform has already been rounded to
  // Float32. Fold that cancellation and the authored bind matrix into each
  // bone in JS doubles first, leaving only mesh-local matrices on the GPU.
  mesh.bindMode = THREE.DetachedBindMode;
  mesh.bindMatrix.identity();
  mesh.bindMatrixInverse.identity();
  skeleton.update = () => {
    worldInverse.copy(mesh.matrixWorld).invert();
    for (let index = 0; index < skeleton.bones.length; index++) {
      localBoneMatrix(index).toArray(skeleton.boneMatrices, index * 16);
    }
    if (skeleton.boneTexture !== null) skeleton.boneTexture.needsUpdate = true;
  };

  // r170 CPU skinning reads bone.matrixWorld directly rather than the palette.
  // Override only this clone so bounds/raycast use the same local convention.
  mesh.applyBoneTransform = (index, vector) => {
    const skinIndex = mesh.geometry.getAttribute('skinIndex');
    const skinWeight = mesh.geometry.getAttribute('skinWeight');
    indices.set(skinIndex.getX(index), skinIndex.getY(index), skinIndex.getZ(index), skinIndex.getW(index));
    weights.set(skinWeight.getX(index), skinWeight.getY(index), skinWeight.getZ(index), skinWeight.getW(index));
    worldInverse.copy(mesh.matrixWorld).invert();
    base.copy(vector);
    vector.set(0, 0, 0);
    for (let component = 0; component < 4; component++) {
      const weight = weights.getComponent(component);
      if (weight !== 0) {
        weighted.copy(base).applyMatrix4(localBoneMatrix(indices.getComponent(component)));
        vector.addScaledVector(weighted, weight);
      }
    }
    return vector;
  };
}

/**
 * Clone a cached, Y-up, metre-scale rig whose authored feet datum is y=0.
 * Walk must be authored in place: all tracks are preserved, including any root
 * motion. Put world placement/heading on a parent group to keep those transforms
 * separate from animation. Geometry, material textures and source clips stay
 * cache-owned. Cloned skeletons and their renderer-allocated bone textures are
 * actor-owned and released by dispose().
 *
 * pose() samples an absolute capture timeline without a render-loop clock.
 * Walk cycles = timeSeconds * speed / stride; phaseSeconds offsets source-clip
 * time (and may be negative). Idle freezes at phaseSeconds regardless of time.
 */
export function createPeopleActor(
  source: THREE.Object3D,
  animations: readonly THREE.AnimationClip[],
  options: PeopleActorOptions,
): PeopleActor {
  const stride = options.walkStrideMeters;
  if (!Number.isFinite(stride) || stride <= 0) {
    throw new Error('People actor walkStrideMeters must be finite and greater than zero');
  }
  const clips = {
    walk: requireClip(animations, options.walkClip),
    idle: requireClip(animations, options.idleClip),
  };
  const root = clone(source);
  const materials = new Map<THREE.Material, THREE.Material>();
  const skeletons = new Set<THREE.Skeleton>();
  // r170 runtime bounds are nullable even though its SkinnedMesh typings omit
  // null. Keep the nullable runtime shape here for lazy renderer/picker refresh.
  const skinnedBounds: Array<{ boundingBox: THREE.Box3 | null; boundingSphere: THREE.Sphere | null }> = [];
  function cloneMaterial(material: THREE.Material) {
    let owned = materials.get(material);
    if (!owned) {
      owned = material.clone();
      materials.set(material, owned);
    }
    return owned;
  }
  root.traverse((object) => {
    if (!(object as THREE.Mesh).isMesh) return;
    const mesh = object as THREE.Mesh;
    if ((mesh as THREE.SkinnedMesh).isSkinnedMesh) {
      const skinned = mesh as THREE.SkinnedMesh;
      skeletons.add(skinned.skeleton);
      skinnedBounds.push(skinned);
      localizeSkinning(skinned);
    }
    mesh.material = Array.isArray(mesh.material)
      ? mesh.material.map(cloneMaterial)
      : cloneMaterial(mesh.material);
  });
  const mixer = new THREE.AnimationMixer(root);
  const actions = {
    walk: mixer.clipAction(clips.walk),
    idle: mixer.clipAction(clips.idle),
  };
  let disposed = false;

  return {
    root,
    pose(timeSeconds, mode, speedMetersPerSecond = 1, phaseSeconds = 0) {
      if (disposed) throw new Error('Cannot pose a disposed people actor');
      if (!Number.isFinite(timeSeconds) || timeSeconds < 0) {
        throw new Error('People pose timeSeconds must be finite and nonnegative');
      }
      if (mode !== 'walk' && mode !== 'idle') {
        throw new Error('People pose mode must be "walk" or "idle"');
      }
      if (!Number.isFinite(speedMetersPerSecond) || speedMetersPerSecond < 0) {
        throw new Error('People pose speedMetersPerSecond must be finite and nonnegative');
      }
      if (!Number.isFinite(phaseSeconds)) {
        throw new Error('People pose phaseSeconds must be finite');
      }
      const duration = clips[mode].duration;
      const sampleTime = mode === 'walk'
        ? timeSeconds * speedMetersPerSecond / stride * duration + phaseSeconds
        : phaseSeconds;
      if (!Number.isFinite(sampleTime)) {
        throw new Error('People pose timeSeconds, speed and stride exceed a finite clip time');
      }
      const wrappedTime = ((sampleTime % duration) + duration) % duration;
      // Stopping restores the previous clip's original property values. Resetting
      // also clears loop counters, so seeks and clip changes cannot retain history.
      mixer.stopAllAction();
      actions[mode].reset().play();
      mixer.setTime(wrappedTime);
      root.updateMatrixWorld(true);
      skinnedBounds.forEach((mesh) => {
        mesh.boundingBox = null;
        mesh.boundingSphere = null;
      });
    },
    dispose() {
      if (disposed) return;
      disposed = true;
      mixer.stopAllAction();
      mixer.uncacheRoot(root);
      skeletons.forEach((skeleton) => skeleton.dispose());
      skeletons.clear();
      skinnedBounds.length = 0;
      materials.forEach((material) => material.dispose());
      materials.clear();
    },
  };
}
