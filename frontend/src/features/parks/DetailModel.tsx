import { useMemo } from "react";
import { useGLTF } from "@react-three/drei";
import type { Mesh } from "three";
import { detailAsset, type DetailAssetId } from "./detailCatalogue";

/** Cached metric GLBs, Y-up to the globe's local Z-up. Never pickable outside editor. */
export function DetailModel({
  asset,
  yaw,
}: {
  asset: DetailAssetId;
  yaw: number;
}) {
  const { scene } = useGLTF(detailAsset(asset).url);
  const clone = useMemo(() => {
    const copy = scene.clone(true);
    copy.traverse((object) => {
      if ((object as Mesh).isMesh) {
        object.castShadow = true;
        object.receiveShadow = true;
        object.raycast = () => {};
      }
    });
    return copy;
  }, [scene]);
  return (
    <group
      position={[0, 0, 0.084]}
      rotation={[0, 0, yaw]}
      userData={{ semanticRole: asset, fixedMetricObject: true }}
    >
      <group rotation={[Math.PI / 2, 0, 0]}>
        <primitive object={clone} />
      </group>
    </group>
  );
}
