import { Group, InstancedMesh, Matrix4, Mesh, type Object3D, type Raycaster, type Intersection } from "three";
import { WGS84_ELLIPSOID } from "3d-tiles-renderer";
import { DIRECT_3D_CAPTURE_CONTEXT_USER_DATA } from "@/components/viewer/globe/direct3dCapture";

export interface DetailPlacement {
  id?: string;
  lng: number;
  lat: number;
  height: number;
  angle: number;
}

/** Pick only authored detail batches; instancing keeps the exact item identity. */
export function pickProjectDetail(root: Object3D, ray: Raycaster): string | null {
  const candidates: { id: string; distance: number }[] = [];
  root.traverseVisible(object => {
    const mesh = object as InstancedMesh;
    const ids = mesh.parent?.userData.projectDetailIds as (string | undefined)[] | undefined;
    if (!mesh.isInstancedMesh || !ids) return;
    const hits: Intersection[] = [];
    InstancedMesh.prototype.raycast.call(mesh, ray, hits);
    for (const hit of hits) {
      const id = hit.instanceId === undefined ? undefined : ids[hit.instanceId];
      if (id && !id.startsWith('detail-preview:')) candidates.push({ id, distance: hit.distance });
    }
  });
  candidates.sort((a, b) => a.distance - b.distance);
  return candidates[0]?.id ?? null;
}

/** Keep instance coordinates near a shared origin to avoid Earth-scale Float32 jitter. */
export function detailPlacementMatrix(
  item: DetailPlacement,
  inverseOrigin: Matrix4,
  offset: readonly number[] = [0, 0, 0],
) {
  return inverseOrigin
    .clone()
    .multiply(
      WGS84_ELLIPSOID.getEastNorthUpFrame(
        (item.lat * Math.PI) / 180,
        (item.lng * Math.PI) / 180,
        item.height,
        new Matrix4(),
      ),
    )
    .multiply(new Matrix4().makeTranslation(0, 0, 0.084))
    .multiply(new Matrix4().makeRotationZ((item.angle * Math.PI) / 180))
    .multiply(new Matrix4().makeRotationX(Math.PI / 2))
    .multiply(new Matrix4().makeTranslation(offset[0], offset[1], offset[2]));
}

/** Static kit models share geometry and materials, with one draw object per source mesh. */
export function buildDetailInstances(
  source: Object3D,
  placements: readonly Matrix4[],
) {
  const group = new Group();
  // Project details live in project metadata, not the server's zone inventory.
  // Preserve their pixels in beauty/context captures without inventing a zone
  // identity or asking the AI to regenerate these fixed metric objects.
  group.userData = { ...DIRECT_3D_CAPTURE_CONTEXT_USER_DATA };
  source.updateMatrixWorld(true);
  source.traverseVisible((object) => {
    const mesh = object as Mesh;
    if (!mesh.isMesh) return;
    const batch = new InstancedMesh(
      mesh.geometry,
      mesh.material,
      placements.length,
    );
    batch.name = mesh.name;
    batch.castShadow = true;
    batch.receiveShadow = true;
    batch.raycast = () => {};
    placements.forEach((matrix, i) =>
      batch.setMatrixAt(i, matrix.clone().multiply(mesh.matrixWorld)),
    );
    batch.instanceMatrix.needsUpdate = true;
    batch.computeBoundingSphere();
    batch.computeBoundingBox();
    group.add(batch);
  });
  return group;
}

/** Dispose only instance buffers: source geometry/materials belong to the shared GLTF cache. */
export function disposeDetailInstances(group: Group) {
  group.traverse((object) => {
    if ((object as InstancedMesh).isInstancedMesh)
      (object as InstancedMesh).dispose();
  });
}
