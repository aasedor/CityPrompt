import { useMemo } from "react";
import { useGLTF } from "@react-three/drei";
import type { Mesh } from "three";
import { detailAsset, type DetailAssetId } from "./detailCatalogue";
import { PeopleDetailModel } from '@/features/people/PeopleModel';

/** Cached metric GLBs, Y-up to the globe's local Z-up. Never pickable outside editor. */
export function DetailModel({
  asset,
  yaw,
  peopleAction,
}: {
  asset: DetailAssetId;
  yaw: number;
  peopleAction?: import('@/features/people/peopleActions').PeopleActionId;
}) {
  return detailAsset(asset).people ? <PeopleDetailModel asset={asset} yaw={yaw} peopleAction={peopleAction} /> : <StaticDetailModel asset={asset} yaw={yaw} />;
}

function StaticDetailModel({ asset, yaw }: { asset: DetailAssetId; yaw: number }) {
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
      position={[0, 0, detailAsset(asset).datumLift ?? 0.084]}
      rotation={[0, 0, yaw]}
      userData={{ semanticRole: asset, fixedMetricObject: true }}
    >
      <group rotation={[Math.PI / 2, 0, 0]}>
        <primitive object={clone} />
      </group>
    </group>
  );
}
