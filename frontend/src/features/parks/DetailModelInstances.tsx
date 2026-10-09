import { useEffect, useMemo } from "react";
import { useGLTF } from "@react-three/drei";
import { WGS84_ELLIPSOID } from "3d-tiles-renderer";
import { EastNorthUpFrame } from "3d-tiles-renderer/r3f";
import { Matrix4 } from "three";
import { detailAsset } from "./detailCatalogue";
import {
  buildDetailInstances,
  detailPlacementMatrix,
  disposeDetailInstances,
  type DetailPlacement,
} from "./detailInstances";

/** Mounted only for placed assets. Opening the catalogue does not download any GLBs. */
export function DetailModelInstances({
  asset,
  placements,
}: {
  asset: string;
  placements: DetailPlacement[];
}) {
  const model = detailAsset(asset);
  const { scene } = useGLTF(model.url);
  const origin = placements[0];
  const group = useMemo(() => {
    const first = placements[0];
    const inverse = WGS84_ELLIPSOID.getEastNorthUpFrame(
      (first.lat * Math.PI) / 180,
      (first.lng * Math.PI) / 180,
      first.height,
      new Matrix4(),
    ).invert();
    const result = buildDetailInstances(
      scene,
      placements.map((p) => detailPlacementMatrix(p, inverse, model.offset)),
    );
    result.userData = { ...result.userData, semanticRole: asset, fixedMetricObject: true,
      projectDetailIds: placements.map(p => p.id) };
    return result;
  }, [scene, placements, model, asset]);
  useEffect(() => () => disposeDetailInstances(group), [group]);
  return (
    <EastNorthUpFrame
      lat={(origin.lat * Math.PI) / 180}
      lon={(origin.lng * Math.PI) / 180}
      height={origin.height}
    >
      <primitive object={group} dispose={null} />
    </EastNorthUpFrame>
  );
}
