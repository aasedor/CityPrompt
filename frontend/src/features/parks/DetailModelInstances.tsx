import { useEffect, useMemo } from "react";
import { useGLTF } from "@react-three/drei";
import { WGS84_ELLIPSOID } from "3d-tiles-renderer";
import { EastNorthUpFrame } from "3d-tiles-renderer/r3f";
import { Box3, BoxGeometry, EdgesGeometry, LineBasicMaterial, LineSegments, Matrix4, Vector3 } from "three";
import { DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA } from "@/components/viewer/globe/direct3dCapture";
import { detailAsset } from "./detailCatalogue";
import { registerDetailWalkSurfaces } from "./detailWalking";
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
  selectedId,
}: {
  asset: string;
  placements: DetailPlacement[];
  selectedId?: string;
}) {
  const model = detailAsset(asset);
  const { scene, animations } = useGLTF(model.url);
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
      placements.map((p) => detailPlacementMatrix(p, inverse, model.offset, model.datumLift)),
      Boolean(model.safety) && animations.length === 0,
    );
    delete result.userData.siteforgeDirect3DContextOnly;
    result.userData = { ...result.userData, semanticRole: asset, fixedMetricObject: true,
      projectDetailIds: placements.map(p => p.id) };
    return result;
  }, [scene, animations, placements, model, asset]);
  const selectedIndex = placements.findIndex(p => p.id === selectedId);
  const outline = useMemo(() => {
    if (selectedIndex < 0) return null;
    const bounds = new Box3().setFromObject(scene);
    if (bounds.isEmpty()) return null;
    const size = bounds.getSize(new Vector3()).addScalar(0.08);
    const box = new BoxGeometry(size.x, size.y, size.z);
    const edges = new EdgesGeometry(box); box.dispose();
    const line = new LineSegments(edges, new LineBasicMaterial({color:'#c9ff3d',depthTest:false,depthWrite:false}));
    const inverse = WGS84_ELLIPSOID.getEastNorthUpFrame(origin.lat*Math.PI/180,origin.lng*Math.PI/180,origin.height,new Matrix4()).invert();
    const centre = bounds.getCenter(new Vector3());
    line.matrix.copy(detailPlacementMatrix(placements[selectedIndex],inverse,model.offset,model.datumLift))
      .multiply(new Matrix4().makeTranslation(centre.x,centre.y,centre.z));
    line.matrixAutoUpdate = false;
    line.renderOrder = 10001;
    line.raycast = () => {};
    line.userData = {...DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA};
    return line;
  }, [scene, selectedIndex, placements, model, origin.lat, origin.lng, origin.height]);
  useEffect(() => () => { outline?.geometry.dispose(); outline?.material.dispose(); }, [outline]);
  useEffect(() => () => disposeDetailInstances(group), [group]);
  useEffect(() => model.walkSurface
    ? registerDetailWalkSurfaces(model.walkSurface, placements, model.offset)
    : undefined, [model, placements]);
  return (
    <EastNorthUpFrame
      lat={(origin.lat * Math.PI) / 180}
      lon={(origin.lng * Math.PI) / 180}
      height={origin.height}
    >
      <primitive object={group} dispose={null} />
      {outline && <primitive object={outline} dispose={null} />}
    </EastNorthUpFrame>
  );
}
