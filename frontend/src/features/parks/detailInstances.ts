import { Group, InstancedMesh, Matrix4, Mesh, type BufferGeometry, type Material, type Object3D, type Raycaster, type Intersection } from "three";
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import { WGS84_ELLIPSOID } from "3d-tiles-renderer";
import { DIRECT_3D_CAPTURE_CONTEXT_USER_DATA } from "@/components/viewer/globe/direct3dCapture";

export interface DetailPlacement {
  id?: string;
  lng: number;
  lat: number;
  height: number;
  angle: number;
}

interface StaticBatch { geometry: BufferGeometry; material: Material; matrix: Matrix4; name: string }
const staticCache = new WeakMap<Object3D, StaticBatch[]>();

/** Only the audited static path opts in. Source GLTF bytes/resources stay immutable. */
function acquireStaticBatches(source: Object3D): StaticBatch[] | null {
  let cached = staticCache.get(source);
  if (!cached) {
    const meshes: Mesh[] = [];
    source.traverseVisible(object => { if ((object as Mesh).isMesh) meshes.push(object as Mesh); });
    if (!meshes.length || source.animations.length || meshes.some(mesh =>
      Array.isArray(mesh.material) || mesh.material.transparent || (mesh as Mesh & {isSkinnedMesh?: boolean}).isSkinnedMesh
      || (mesh as Mesh & {isInstancedMesh?: boolean}).isInstancedMesh
      || Object.keys(mesh.geometry.morphAttributes).length || mesh.matrixWorld.determinant() <= 0
      || mesh.geometry.drawRange.start !== 0 || mesh.geometry.drawRange.count !== Infinity)) return null;
    const grouped = new Map<string, Mesh[]>();
    for (const mesh of meshes) {
      const signature = Object.entries(mesh.geometry.attributes).sort(([a],[b])=>a.localeCompare(b))
        .map(([name,a])=>`${name}:${a.itemSize}:${a.normalized}:${a.array.constructor.name}`).join('|');
      const key = `${(mesh.material as Material).uuid}:${Boolean(mesh.geometry.index)}:${signature}`;
      const row = grouped.get(key) ?? []; row.push(mesh); grouped.set(key,row);
    }
    const batches: StaticBatch[] = [];
    for (const row of grouped.values()) {
      const copies = row.map(mesh=>mesh.geometry.clone().applyMatrix4(mesh.matrixWorld));
      const geometry = mergeGeometries(copies, false);
      copies.forEach(copy=>copy.dispose());
      if (!geometry) { batches.forEach(batch=>batch.geometry.dispose()); return null; }
      batches.push({ geometry, material: row[0].material as Material, matrix: new Matrix4(), name: row[0].name });
    }
    // GLTF-cache lifetime, not React-render lifetime. StrictMode can abandon a
    // render or replay effects; neither event acquires a source resource owner.
    cached = batches; staticCache.set(source,cached);
    const originals = new Set(meshes.map(mesh=>mesh.geometry));
    const clear = () => {
      if (staticCache.get(source) !== batches) return;
      staticCache.delete(source);
      originals.forEach(geometry=>geometry.removeEventListener('dispose',clear));
      batches.forEach(batch=>batch.geometry.dispose());
    };
    originals.forEach(geometry=>geometry.addEventListener('dispose',clear));
  }
  return cached;
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
  datumLift = 0.084,
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
    .multiply(new Matrix4().makeTranslation(0, 0, datumLift))
    .multiply(new Matrix4().makeRotationZ((item.angle * Math.PI) / 180))
    .multiply(new Matrix4().makeRotationX(Math.PI / 2))
    .multiply(new Matrix4().makeTranslation(offset[0], offset[1], offset[2]));
}

/** Static kit models share geometry and materials, with one draw object per source mesh. */
export function buildDetailInstances(
  source: Object3D,
  placements: readonly Matrix4[],
  consolidateStatic = false,
) {
  const group = new Group();
  // Project details live in project metadata, not the server's zone inventory.
  // Preserve their pixels in beauty/context captures without inventing a zone
  // identity or asking the AI to regenerate these fixed metric objects.
  group.userData = { ...DIRECT_3D_CAPTURE_CONTEXT_USER_DATA };
  source.updateMatrixWorld(true);
  const merged = consolidateStatic ? acquireStaticBatches(source) : null;
  const originals: StaticBatch[] = [];
  if (!merged) source.traverseVisible(object=> {
    const mesh = object as Mesh;
    if (mesh.isMesh) originals.push({geometry:mesh.geometry, material:mesh.material as Material, matrix:mesh.matrixWorld, name:mesh.name});
  });
  for (const mesh of merged ?? originals) {
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
      batch.setMatrixAt(i, matrix.clone().multiply(mesh.matrix)),
    );
    batch.instanceMatrix.needsUpdate = true;
    batch.computeBoundingSphere();
    batch.computeBoundingBox();
    group.add(batch);
  }
  return group;
}

/** Dispose only instance buffers: source geometry/materials belong to the shared GLTF cache. */
export function disposeDetailInstances(group: Group) {
  group.traverse((object) => {
    if ((object as InstancedMesh).isInstancedMesh)
      (object as InstancedMesh).dispose();
  });
}
