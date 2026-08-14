import * as THREE from 'three';

export interface LegoGltfSceneLike {
  scene?: THREE.Object3D | null;
}

/** A resolved GLTF can still be unusable (for example an empty cached scene
 * after a development-time renderer handoff). Treat only scenes with actual
 * mesh geometry as detailed-building sources. */
export function hasRenderableLegoGeometry(
  scene: THREE.Object3D | null | undefined,
): scene is THREE.Object3D {
  if (!scene) return false;
  let renderable = false;
  scene.traverse((object) => {
    if (renderable) return;
    const mesh = object as THREE.Mesh;
    if (mesh.isMesh && Boolean(mesh.geometry)) renderable = true;
  });
  return renderable;
}

/** Drei preserves array shape for array requests, but normalize the singleton
 * form as well so a one-file LEGO family cannot silently resolve to zero
 * modules if a loader/cache version returns the scalar overload. */
export function indexRenderableLegoScenes(
  urls: readonly string[],
  loaded: LegoGltfSceneLike | readonly LegoGltfSceneLike[] | null | undefined,
): Map<string, THREE.Object3D> {
  const results = Array.isArray(loaded) ? loaded : loaded ? [loaded] : [];
  const scenes = new Map<string, THREE.Object3D>();
  urls.forEach((url, index) => {
    const scene = results[index]?.scene;
    if (hasRenderableLegoGeometry(scene)) scenes.set(url, scene);
  });
  return scenes;
}

/** The stack handoff is atomic: every saved instance must have a prepared
 * module before the detailed model replaces its height-bearing massing. */
export function isCompleteLegoModuleStack(
  expectedInstanceCount: number,
  preparedModuleCount: number,
): boolean {
  return expectedInstanceCount > 0 && preparedModuleCount === expectedInstanceCount;
}

export type LegoLayerReadiness = 'mounting' | 'fallback-visible' | 'ready';

/** Keep visible-representation readiness distinct from authored-detail
 * readiness. A full-height fallback is a valid visible handoff, but it must
 * never produce the final "detailed ready" signal used during reload QA. */
export function classifyLegoLayerReadiness({
  entryCount,
  visibleRepresentationCount,
  detailedTargetCount,
  detailedReadyCount,
  temporaryFallbackCount,
}: {
  entryCount: number;
  visibleRepresentationCount: number;
  detailedTargetCount: number;
  detailedReadyCount: number;
  temporaryFallbackCount: number;
}): LegoLayerReadiness {
  if (temporaryFallbackCount > 0) return 'fallback-visible';
  if (
    entryCount > 0
    && visibleRepresentationCount === entryCount
    && detailedReadyCount === detailedTargetCount
  ) return 'ready';
  return 'mounting';
}
