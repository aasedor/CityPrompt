import * as THREE from 'three';
import { prepareBuildingOnlyScene, prepareOwnedNativeScene, type NativeSceneOwnershipContract } from '@/features/legoAssembly/buildingOnlyScene';
import type { PublicRealmReleaseFixture } from '@/features/pickPlace/publicRealmRelease';
import { publicRealmReleaseRow } from '@/features/pickPlace/publicRealmRelease';
import { publicRealmOwnership } from '@/features/pickPlace/publicRealmOwnershipContract';
export { publicRealmOwnership } from '@/features/pickPlace/publicRealmOwnershipContract';

interface ContextSupport {
  name: string; polygon: number[][]; bottom: number; top: number; material: string;
}

/** A source marking may continue onto an excluded road. Intersect its actual
 * triangles with the explicitly declared marking prism, interpolating source
 * attributes; do not extend component ownership to the surrounding scene. */
function clipMarking(geometry: THREE.BufferGeometry, matrix: THREE.Matrix4, region: readonly number[]) {
  type Vertex = Record<string, number[]>;
  const names = Object.keys(geometry.attributes), output: Record<string, number[]> = {};
  for (const name of names) output[name] = [];
  const result = new THREE.BufferGeometry(), index = geometry.getIndex();
  const count = index?.count ?? geometry.getAttribute('position').count;
  const coordinate = (vertex: Vertex, axis: number) => new THREE.Vector3()
    .fromArray(vertex.position).applyMatrix4(matrix).getComponent(axis);
  for (let offset = 0; offset < count; offset += 3) {
    let polygon: Vertex[] = [0, 1, 2].map(k => {
      const id = index ? index.getX(offset + k) : offset + k;
      return Object.fromEntries(names.map(name => {
        const attribute = geometry.getAttribute(name);
        return [name, Array.from({ length: attribute.itemSize }, (_, axis) => attribute.getComponent(id, axis))];
      }));
    });
    for (let axis = 0; axis < 3 && polygon.length; axis++) for (const sign of [1, -1]) {
      const bound = region[axis + (sign === 1 ? 0 : 3)], clipped: Vertex[] = [];
      for (let i = 0; i < polygon.length; i++) {
        const a = polygon[i], b = polygon[(i + 1) % polygon.length];
        const da = (coordinate(a, axis) - bound) * sign, db = (coordinate(b, axis) - bound) * sign;
        if (da >= 0) clipped.push(a);
        if ((da >= 0) !== (db >= 0)) {
          const t = da / (da - db);
          clipped.push(Object.fromEntries(names.map(name => [name, a[name].map((value, k) => value + (b[name][k] - value) * t)])));
        }
      }
      polygon = clipped;
    }
    const start = output.position.length / 3;
    for (let i = 1; i < polygon.length - 1; i++) {
      const vertices = [polygon[0], polygon[i], polygon[i + 1]];
      const [a, b, c] = vertices.map(vertex => new THREE.Vector3().fromArray(vertex.position));
      if (b.sub(a).cross(c.sub(a)).lengthSq() <= 1e-16) continue;
      for (const vertex of vertices) for (const name of names) output[name].push(...vertex[name]);
    }
    const added = output.position.length / 3 - start;
    if (added && geometry.groups.length) result.addGroup(start, added,
      geometry.groups.find(group => offset >= group.start && offset < group.start + group.count)?.materialIndex ?? 0);
  }
  for (const name of names) result.setAttribute(name, new THREE.Float32BufferAttribute(output[name], geometry.getAttribute(name).itemSize));
  result.computeBoundingBox(); result.computeBoundingSphere();
  return result;
}

export function preparePublicRealmOwnedScene(source: THREE.Object3D, fixture: PublicRealmReleaseFixture) {
  const contract = publicRealmOwnership(fixture) as unknown as
    (NativeSceneOwnershipContract & { contextSupports?: ContextSupport[] }) | undefined;
  const result = prepareOwnedNativeScene(source, contract);
  const markingRegions = contract?.meshRegions?.CLAY_WHITE;
  if (markingRegions?.length === 1) {
    const isMarking = (object: THREE.Object3D): object is THREE.Mesh => {
      const mesh = object as THREE.Mesh;
      return mesh.isMesh && mesh.name === 'CLAY_WHITE'
        && (Array.isArray(mesh.material) ? mesh.material : [mesh.material]).every(material => material.name === 'CLAY_WHITE');
    };
    // Work from a disposable clone: cached source matrices and buffers stay
    // immutable, including when a loader supplied non-identity node transforms.
    const original = source.clone(true); original.updateMatrixWorld(true);
    const inverse = result.clone.matrixWorld.clone().invert(), remove: THREE.Object3D[] = [];
    result.clone.traverse(object => { if (isMarking(object)) remove.push(object); });
    remove.forEach(object => object.removeFromParent());
    original.traverse(object => {
      if (!isMarking(object)) return;
      const geometry = clipMarking(object.geometry, object.matrixWorld, markingRegions[0]);
      result.ownedGeometries.push(geometry);
      if (!geometry.getAttribute('position').count) return;
      const mesh = object.clone(false); mesh.geometry = geometry;
      mesh.matrixAutoUpdate = false; mesh.matrix.copy(inverse.clone().multiply(object.matrixWorld));
      result.clone.add(mesh);
    });
  }
  for (const support of contract?.contextSupports ?? []) {
    let material: THREE.Material | undefined;
    source.traverse(object => {
      const mesh = object as THREE.Mesh;
      if (mesh.isMesh) material ??= (Array.isArray(mesh.material) ? mesh.material : [mesh.material])
        .find(value => value.name === support.material);
    });
    if (!material) throw new Error('The compact crossing support material is unavailable.');
    // Source bank footprints are in Blender XY; extrude the bounded, closed
    // bank solid in native metres and convert once to glTF Y-up. Original
    // cached geometry and GLB bytes stay unchanged. These are explicit runtime
    // adaptations, separately bound by the saved ownership revision.
    const shape = new THREE.Shape(support.polygon.map(point => new THREE.Vector2(point[0], point[1])));
    const geometry = new THREE.ExtrudeGeometry(shape, { depth: support.top - support.bottom,
      bevelEnabled: false, steps: 1, curveSegments: 1 });
    geometry.rotateX(-Math.PI / 2).translate(0, support.bottom, 0);
    geometry.applyMatrix4(result.clone.matrixWorld.clone().invert());
    const mesh = new THREE.Mesh(geometry, material);
    mesh.name = `runtime-context-${support.name}`;
    mesh.userData.runtimeContextAdaptation = true;
    result.clone.add(mesh); result.ownedGeometries.push(geometry);
  }
  return result;
}

/** Hover preview and placed objects must display the same retained geometry. */
export function prepareNativePlacementScene(source: THREE.Object3D, url: string, assetId?: string) {
  const row = publicRealmReleaseRow(assetId);
  return row?.fixture.url === url ? preparePublicRealmOwnedScene(source, row.fixture)
    : prepareBuildingOnlyScene(source, url);
}
