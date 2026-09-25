import * as THREE from 'three';
import { clipStreetGeometryOutsideJunction, streetJunctionContainsPoint } from './streetJunctionGeometry';
import { nativeLocalJunction, type NativeStreetJunction, type NativeStreetPlacement } from './nativeStreetJunction';
import { TRIAL_GROUND_MATERIALS } from './publicRealmTrial';

type LocalCut = ReturnType<typeof nativeLocalJunction>;
const toENU = new THREE.Matrix4().makeRotationX(Math.PI / 2);

/** Native GLBs retain individually authored props, but some exporters merge
 * identical-material props into one mesh. Remove connected geometry islands,
 * rather than deleting every lamp or tree because one intersects the node. */
function clearRigidIslands(source: THREE.BufferGeometry, meshToENU: THREE.Matrix4, cuts: LocalCut[]): THREE.BufferGeometry | null {
  const position = source.getAttribute('position');
  const index = source.getIndex();
  const faceCount = (index?.count ?? position.count) / 3;
  if (!Number.isInteger(faceCount) || faceCount === 0) return null;
  const parent = Array.from({ length: faceCount }, (_, i) => i);
  const find = (n: number): number => parent[n] === n ? n : (parent[n] = find(parent[n]));
  const join = (a: number, b: number) => { const x = find(a), y = find(b); if (x !== y) parent[y] = x; };
  const owner = new Map<string, number>();
  const vertices = new Float64Array(faceCount * 9);
  const point = new THREE.Vector3();
  for (let face = 0; face < faceCount; face++) for (let corner = 0; corner < 3; corner++) {
    const vi = index ? index.getX(face * 3 + corner) : face * 3 + corner;
    point.fromBufferAttribute(position, vi).applyMatrix4(meshToENU);
    const base = face * 9 + corner * 3;
    vertices[base] = point.x; vertices[base + 1] = point.y; vertices[base + 2] = point.z;
    const key = `${Math.round(point.x * 1000)}:${Math.round(point.y * 1000)}:${Math.round(point.z * 1000)}`;
    const previous = owner.get(key);
    if (previous === undefined) owner.set(key, face); else join(face, previous);
  }
  const components = new Map<number, { faces: number[]; minX: number; maxX: number; minY: number; maxY: number }>();
  for (let face = 0; face < faceCount; face++) {
    const root = find(face);
    const component = components.get(root) ?? { faces: [], minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity };
    component.faces.push(face);
    for (let corner = 0; corner < 3; corner++) {
      const base = face * 9 + corner * 3;
      component.minX = Math.min(component.minX, vertices[base]); component.maxX = Math.max(component.maxX, vertices[base]);
      component.minY = Math.min(component.minY, vertices[base + 1]); component.maxY = Math.max(component.maxY, vertices[base + 1]);
    }
    components.set(root, component);
  }
  const keep = new Uint8Array(faceCount);
  let kept = 0;
  for (const component of components.values()) {
    const x = (component.minX + component.maxX) / 2, y = (component.minY + component.maxY) / 2;
    const clear = cuts.some(({ layout, centerX, centerY }) =>
      streetJunctionContainsPoint(layout, x - centerX, y - centerY, 1.25));
    if (!clear) for (const face of component.faces) { keep[face] = 1; kept++; }
  }
  if (kept === faceCount) return null;
  const geometry = new THREE.BufferGeometry();
  for (const [name, attribute] of Object.entries(source.attributes)) {
    const values: number[] = [];
    for (let face = 0; face < faceCount; face++) if (keep[face]) {
      for (let corner = 0; corner < 3; corner++) {
        const vi = index ? index.getX(face * 3 + corner) : face * 3 + corner;
        for (let item = 0; item < attribute.itemSize; item++) values.push(attribute.getComponent(vi, item));
      }
    }
    geometry.setAttribute(name, new THREE.Float32BufferAttribute(values, attribute.itemSize));
  }
  geometry.computeBoundingSphere();
  return geometry;
}

export function trimNativeStreetModel(scene: THREE.Object3D, placement: NativeStreetPlacement['placement'], junctions: NativeStreetJunction[]) {
  const clone = scene.clone(true);
  const owned: THREE.BufferGeometry[] = [];
  const remove: THREE.Object3D[] = [];
  const cuts = junctions.map((junction) => nativeLocalJunction(junction, placement));
  clone.updateMatrixWorld(true);
  clone.traverse((object) => {
    if (!(object instanceof THREE.Mesh)) return;
    const mesh = object as THREE.Mesh;
    const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    if (!('preserveNativeGround' in placement.asset && placement.asset.preserveNativeGround)
      && materials.every((material) => TRIAL_GROUND_MATERIALS.has(material.name))) { remove.push(mesh); return; }
    const source = mesh.geometry;
    if (!source?.getAttribute('position')) return;
    const meshToENU = toENU.clone().multiply(mesh.matrixWorld);
    if (!source.boundingBox) source.computeBoundingBox();
    const worldBox = source.boundingBox!.clone().applyMatrix4(meshToENU);
    if (cuts.length > 0 && worldBox.max.z - worldBox.min.z < .22) {
      let next = source.clone().applyMatrix4(meshToENU);
      for (const { layout, centerX, centerY } of cuts) {
        const clipped = clipStreetGeometryOutsideJunction(next, layout, centerX, centerY);
        next.dispose(); next = clipped;
      }
      next.applyMatrix4(meshToENU.clone().invert());
      mesh.geometry = next; owned.push(next);
    } else if (cuts.length > 0) {
      const next = clearRigidIslands(source, meshToENU, cuts);
      if (next) { mesh.geometry = next; owned.push(next); }
    }
    mesh.castShadow = true; mesh.receiveShadow = true; mesh.renderOrder = 148;
  });
  remove.forEach((object) => object.removeFromParent());
  return { clone, owned };
}
