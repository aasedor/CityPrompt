import * as THREE from 'three';
import { RESIZE_TRIAL_SETTINGS } from '@/features/pickPlace/buildingResizeTrial';

/**
 * Building resize pilot: keep small free-standing props at their real
 * proportions when the exact model is stretched.
 *
 * A stretch scales the whole model along its width (X) and depth (Z). That is
 * right for walls, but it turns a round shrub into an ellipse. This moves each
 * small prop to where the stretch puts it and cancels the stretch on its
 * shape, so a tree stays a tree. Long runs such as hedges still stretch.
 *
 * Call it on the centred wrapper BEFORE the stretch is applied to that
 * wrapper. The cached GLB is never touched: every changed mesh gets its own
 * geometry, which is returned for the caller to dispose.
 */
export function keepPropsRigidUnderStretch(
  wrapper: THREE.Object3D,
  widthScale: number,
  depthScale: number,
  options: { materialNames: readonly string[]; maxSizeM: number } = {
    materialNames: RESIZE_TRIAL_SETTINGS.rigidPropMaterials, maxSizeM: RESIZE_TRIAL_SETTINGS.rigidPropMaxSizeM },
): THREE.BufferGeometry[] {
  const owned: THREE.BufferGeometry[] = [];
  if (!(widthScale > 0) || !(depthScale > 0) || (Math.abs(widthScale - 1) < 1e-6 && Math.abs(depthScale - 1) < 1e-6)
    || !options.materialNames.length) return owned;
  wrapper.updateMatrixWorld(true);
  const fromWorld = new THREE.Matrix4().copy(wrapper.matrixWorld).invert();
  wrapper.traverse(object => {
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh || !mesh.geometry?.attributes.position) return;
    const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    if (!materials.some(material => options.materialNames.includes(material?.name ?? ''))) return;
    const geometry = rigidGeometry(mesh.geometry, new THREE.Matrix4().multiplyMatrices(fromWorld, mesh.matrixWorld),
      widthScale, depthScale, options.maxSizeM);
    if (geometry) { mesh.geometry = geometry; owned.push(geometry); }
  });
  return owned;
}

/** Touching parts of one prop (a canopy made of several spheres) move as one. */
const TOUCH_M = 0.03;

function rigidGeometry(source: THREE.BufferGeometry, toWrapper: THREE.Matrix4, widthScale: number,
  depthScale: number, maxSizeM: number): THREE.BufferGeometry | null {
  const sourcePosition = source.attributes.position;
  const count = sourcePosition.count;
  if (!count) return null;
  // Positions in the wrapper's frame, where the stretch will act.
  const points = new Float32Array(count * 3), point = new THREE.Vector3();
  for (let index = 0; index < count; index += 1) {
    point.fromBufferAttribute(sourcePosition, index).applyMatrix4(toWrapper);
    points[index * 3] = point.x; points[index * 3 + 1] = point.y; points[index * 3 + 2] = point.z;
  }
  // Weld coincident vertices so faces that share a corner count as one part.
  const welded = new Int32Array(count), keys = new Map<string, number>();
  for (let index = 0; index < count; index += 1) {
    const key = `${Math.round(points[index * 3] * 1000)},${Math.round(points[index * 3 + 1] * 1000)},${Math.round(points[index * 3 + 2] * 1000)}`;
    let id = keys.get(key);
    if (id === undefined) { id = keys.size; keys.set(key, id); }
    welded[index] = id;
  }
  const parent = Int32Array.from({ length: keys.size }, (_, index) => index);
  const find = (node: number) => {
    while (parent[node] !== node) { parent[node] = parent[parent[node]]; node = parent[node]; }
    return node;
  };
  const union = (a: number, b: number) => { const ra = find(a), rb = find(b); if (ra !== rb) parent[ra] = rb; };
  const indexAttribute = source.index;
  const corners = indexAttribute ? indexAttribute.count : count;
  for (let corner = 0; corner + 2 < corners; corner += 3) {
    const a = welded[indexAttribute ? indexAttribute.getX(corner) : corner];
    union(a, welded[indexAttribute ? indexAttribute.getX(corner + 1) : corner + 1]);
    union(a, welded[indexAttribute ? indexAttribute.getX(corner + 2) : corner + 2]);
  }
  // Bounding box of every part, then merge parts whose boxes touch.
  const boxes = new Map<number, number[]>();
  for (let index = 0; index < count; index += 1) {
    const root = find(welded[index]), x = points[index * 3], y = points[index * 3 + 1], z = points[index * 3 + 2];
    const box = boxes.get(root);
    if (!box) boxes.set(root, [x, y, z, x, y, z]);
    else {
      box[0] = Math.min(box[0], x); box[1] = Math.min(box[1], y); box[2] = Math.min(box[2], z);
      box[3] = Math.max(box[3], x); box[4] = Math.max(box[4], y); box[5] = Math.max(box[5], z);
    }
  }
  const parts = [...boxes.entries()].sort((a, b) => a[1][0] - b[1][0]);
  for (let i = 0; i < parts.length; i += 1) {
    const a = parts[i][1];
    for (let j = i + 1; j < parts.length && parts[j][1][0] <= a[3] + TOUCH_M; j += 1) {
      const b = parts[j][1];
      if (b[1] <= a[4] + TOUCH_M && a[1] <= b[4] + TOUCH_M && b[2] <= a[5] + TOUCH_M && a[2] <= b[5] + TOUCH_M) {
        union(parts[i][0], parts[j][0]);
      }
    }
  }
  const props = new Map<number, number[]>();
  for (const [root, box] of boxes) {
    const prop = props.get(find(root));
    if (!prop) props.set(find(root), [...box]);
    else for (let axis = 0; axis < 3; axis += 1) {
      prop[axis] = Math.min(prop[axis], box[axis]); prop[axis + 3] = Math.max(prop[axis + 3], box[axis + 3]);
    }
  }
  // Only small props are rigid. A hedge or a planter run stretches with the building.
  const rigid = new Map<number, [number, number]>();
  for (const [root, box] of props) {
    if (Math.max(box[3] - box[0], box[5] - box[2]) <= maxSizeM) rigid.set(root, [(box[0] + box[3]) / 2, (box[2] + box[5]) / 2]);
  }
  if (!rigid.size) return null;

  const geometry = source.clone();
  const position = geometry.attributes.position, normal = geometry.attributes.normal;
  const toLocal = new THREE.Matrix4().copy(toWrapper).invert();
  // Normals travel by the inverse transpose; these undo and redo that for the mesh's own frame.
  const normalToWrapper = new THREE.Matrix3().getNormalMatrix(toWrapper);
  const normalToLocal = new THREE.Matrix3().setFromMatrix4(toWrapper).transpose();
  const direction = new THREE.Vector3();
  for (let index = 0; index < count; index += 1) {
    const centre = rigid.get(find(welded[index]));
    if (!centre) continue;
    point.set(centre[0] + (points[index * 3] - centre[0]) / widthScale, points[index * 3 + 1],
      centre[1] + (points[index * 3 + 2] - centre[1]) / depthScale).applyMatrix4(toLocal);
    position.setXYZ(index, point.x, point.y, point.z);
    if (normal) {
      // The later stretch would skew this prop's shading; pre-correct it.
      direction.fromBufferAttribute(normal, index).applyMatrix3(normalToWrapper).normalize();
      direction.set(direction.x * widthScale, direction.y, direction.z * depthScale).applyMatrix3(normalToLocal).normalize();
      normal.setXYZ(index, direction.x, direction.y, direction.z);
    }
  }
  position.needsUpdate = true;
  if (normal) normal.needsUpdate = true;
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();
  return geometry;
}
