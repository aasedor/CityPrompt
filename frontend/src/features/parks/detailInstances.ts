import { Group, InstancedMesh, Matrix4, Mesh, type Object3D } from "three";
import { WGS84_ELLIPSOID } from "3d-tiles-renderer";

export interface DetailPlacement {
  lng: number;
  lat: number;
  height: number;
  angle: number;
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
