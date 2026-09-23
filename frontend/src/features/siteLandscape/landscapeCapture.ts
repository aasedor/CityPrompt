import type { Material, Object3D, Texture } from "three";
export function assertSiteLandscapeReady(scene: Object3D) {
  scene.traverse((object) => {
    const raw = (object as Object3D & { material?: Material | Material[] })
      .material;
    for (const material of raw ? (Array.isArray(raw) ? raw : [raw]) : []) {
      const status = (material as Material & { map?: Texture }).map?.userData
        .siteLandscapeStatus;
      if (status === "loading")
        throw new Error(
          "Your custom site surface is still loading. Wait a moment before exporting.",
        );
      if (status === "failed")
        throw new Error(
          "Your custom site surface could not load. Reload or remove the custom landscape before exporting.",
        );
    }
  });
}
