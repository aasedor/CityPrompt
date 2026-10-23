import { useEffect, useMemo } from 'react';
import { useGLTF } from '@react-three/drei';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { Box3, BoxGeometry, EdgesGeometry, Group, LineBasicMaterial, LineSegments, Matrix4, Vector3, type Mesh } from 'three';
import { detailAsset } from '@/features/parks/detailCatalogue';
import { detailPlacementMatrix, type DetailPlacement } from '@/features/parks/detailInstances';
import { DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA } from '@/components/viewer/globe/direct3dCapture';
import { createPeopleActor } from './peopleAnimation';
import { PEOPLE_CAPTURE_KEY } from './peopleCapture';
import { createPeopleActionPose } from './peoplePose';
import type { PeopleActionId } from './peopleActions';
import { peopleWalkingProfile } from './peopleWalking';

/** People are loaded only when placed. No per-frame work during normal editing. */
export function PeopleModelInstances({ asset, placements, selectedId }: {
  asset: string; placements: Array<DetailPlacement & {id: string}>; selectedId?: string;
}) {
  const model = detailAsset(asset);
  const { scene, animations } = useGLTF(model.url);
  const host = useMemo(() => new Group(), []);
  const origin = placements[0];
  useEffect(() => {
    if (!model.people || !placements.length) return;
    const inverse = WGS84_ELLIPSOID.getEastNorthUpFrame(origin.lat * Math.PI / 180, origin.lng * Math.PI / 180, origin.height, new Matrix4()).invert();
    const disposers: Array<() => void> = [];
    placements.forEach((placement) => {
      const actor = createPeopleActor(scene, animations, model.people!);
      const actionPose = createPeopleActionPose(actor,peopleWalkingProfile(placement.id));
      actionPose.sample(placement.people_action);
      const localBounds = new Box3().setFromObject(actionPose.root);
      actor.root.traverse(object => { if ((object as Mesh).isMesh) { object.castShadow = true; object.receiveShadow = true; } });
      const wrapper = new Group(), mover = actionPose.root;
      wrapper.matrix.copy(detailPlacementMatrix(placement, inverse, model.offset, model.datumLift));
      wrapper.matrixAutoUpdate = false;
      wrapper.userData = { projectDetailId: placement.id, fixedMetricObject: true, semanticRole: asset };
      let alive = true;
      wrapper.userData[PEOPLE_CAPTURE_KEY] = {
        pose(seconds: number) {
          if (!alive) return;
          actionPose.sample(placement.people_action, seconds, true);
          wrapper.updateMatrixWorld(true);
        },
        restore() {
          if (!alive) return;
          actionPose.sample(placement.people_action); wrapper.updateMatrixWorld(true);
        },
        focus: () => mover.getWorldPosition(new Vector3()),
      };
      wrapper.add(mover); host.add(wrapper);
      let outline: LineSegments<EdgesGeometry, LineBasicMaterial> | null = null;
      if (placement.id === selectedId) {
        const bounds = localBounds, size = bounds.getSize(new Vector3()).addScalar(.08);
        const box = new BoxGeometry(size.x, size.y, size.z);
        outline = new LineSegments(new EdgesGeometry(box), new LineBasicMaterial({ color: '#c9ff3d', depthTest: false, depthWrite: false }));
        box.dispose(); outline.position.copy(bounds.getCenter(new Vector3()));
        outline.userData = { ...DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA };
        outline.raycast = () => {}; outline.renderOrder = 10001; wrapper.add(outline);
      }
      disposers.push(() => { alive = false; host.remove(wrapper); actor.dispose(); outline?.geometry.dispose(); outline?.material.dispose(); });
    });
    return () => disposers.forEach(dispose => dispose());
  }, [scene, animations, model, placements, selectedId, host, origin.lat, origin.lng, origin.height, asset]);
  return <EastNorthUpFrame lat={origin.lat * Math.PI / 180} lon={origin.lng * Math.PI / 180} height={origin.height}>
    <primitive object={host} dispose={null} />
  </EastNorthUpFrame>;
}

export function PeopleDetailModel({ asset, yaw, peopleAction }: { asset: string; yaw: number; peopleAction?: PeopleActionId }) {
  const model = detailAsset(asset), { scene, animations } = useGLTF(model.url);
  const host = useMemo(() => new Group(), []);
  useEffect(() => {
    const actor = createPeopleActor(scene, animations, model.people!);
    const actionPose = createPeopleActionPose(actor); actionPose.sample(peopleAction);
    actor.root.traverse(object => { if ((object as Mesh).isMesh) { object.castShadow = true; object.receiveShadow = true; object.raycast = () => {}; } });
    host.add(actionPose.root);
    return () => { host.remove(actionPose.root); actor.dispose(); };
  }, [scene, animations, model, host, peopleAction]);
  return <group position={[0, 0, model.datumLift ?? 0]} rotation={[0, 0, yaw]}><group rotation={[Math.PI / 2, 0, 0]}><primitive object={host} dispose={null} /></group></group>;
}
