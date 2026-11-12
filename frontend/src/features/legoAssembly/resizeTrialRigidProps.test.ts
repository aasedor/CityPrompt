import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { keepPropsRigidUnderStretch } from './resizeTrialRigidProps';

/** A wrapper holding planting (two shrubs and a hedge) and a wall, like a centred clay model. */
function model() {
  const wrapper = new THREE.Group();
  const boxAt = (width: number, height: number, depth: number, x: number, z: number) =>
    new THREE.BoxGeometry(width, height, depth).translate(x, height / 2, z);
  const merge = (geometries: THREE.BufferGeometry[]) => {
    // One un-welded mesh, as exported clay planting is.
    const merged = new THREE.BufferGeometry();
    const flat = geometries.map(geometry => geometry.toNonIndexed());
    merged.setAttribute('position', new THREE.Float32BufferAttribute(flat.flatMap(g => [...g.attributes.position.array]), 3));
    merged.setAttribute('normal', new THREE.Float32BufferAttribute(flat.flatMap(g => [...g.attributes.normal.array]), 3));
    return merged;
  };
  const plantingGeometry = merge([boxAt(0.8, 1, 0.8, 5, 2), boxAt(0.8, 1, 0.8, -6, -3), boxAt(6, 0.5, 0.7, 0, 7)]);
  const planting = new THREE.Mesh(plantingGeometry, new THREE.MeshStandardMaterial({ name: 'CLAY_PLANTING' }));
  // The exported planting node carries its own offset and scale.
  planting.position.set(1, 0.5, -2); planting.scale.set(0.5, 0.5, 0.5);
  const wallGeometry = boxAt(20, 10, 12, 0, 0);
  const wall = new THREE.Mesh(wallGeometry, new THREE.MeshStandardMaterial({ name: 'CLAY_WALL' }));
  wrapper.add(planting, wall);
  return { wrapper, planting, plantingGeometry, wall, wallGeometry };
}
/** World-space boxes of the three planting parts, by vertex range. */
function partBoxes(planting: THREE.Mesh) {
  planting.updateWorldMatrix(true, false);
  const position = planting.geometry.attributes.position, point = new THREE.Vector3();
  return [0, 1, 2].map(part => {
    const box = new THREE.Box3();
    for (let index = part * 36; index < (part + 1) * 36; index += 1) {
      box.expandByPoint(point.fromBufferAttribute(position, index).applyMatrix4(planting.matrixWorld));
    }
    return { size: box.getSize(new THREE.Vector3()), centre: box.getCenter(new THREE.Vector3()) };
  });
}
const options = { materialNames: ['CLAY_PLANTING'], maxSizeM: 2.5 };

describe('keepPropsRigidUnderStretch', () => {
  it('keeps small props their real size and moves them with the stretch', () => {
    const { wrapper, planting } = model();
    const before = partBoxes(planting);
    const owned = keepPropsRigidUnderStretch(wrapper, 1.4, 0.7, options);
    expect(owned).toHaveLength(1);
    wrapper.scale.set(1.4, 1, 0.7);
    const after = partBoxes(planting);
    for (const shrub of [0, 1]) {
      expect(after[shrub].size.x).toBeCloseTo(before[shrub].size.x, 5);
      expect(after[shrub].size.z).toBeCloseTo(before[shrub].size.z, 5);
      expect(after[shrub].size.y).toBeCloseTo(before[shrub].size.y, 5);
      expect(after[shrub].centre.x).toBeCloseTo(before[shrub].centre.x * 1.4, 5);
      expect(after[shrub].centre.z).toBeCloseTo(before[shrub].centre.z * 0.7, 5);
    }
    // The hedge is longer than a prop: it stretches with the building.
    expect(after[2].size.x).toBeCloseTo(before[2].size.x * 1.4, 5);
    expect(after[2].size.z).toBeCloseTo(before[2].size.z * 0.7, 5);
  });

  it('keeps a rigid prop’s shading true after the stretch', () => {
    const { wrapper, planting } = model();
    keepPropsRigidUnderStretch(wrapper, 1.4, 0.7, options);
    wrapper.scale.set(1.4, 1, 0.7);
    planting.updateWorldMatrix(true, false);
    const normalMatrix = new THREE.Matrix3().getNormalMatrix(planting.matrixWorld);
    const normal = planting.geometry.attributes.normal, direction = new THREE.Vector3();
    for (let index = 0; index < 36; index += 1) {
      direction.fromBufferAttribute(normal, index).applyMatrix3(normalMatrix).normalize();
      // A box face still faces squarely along one axis.
      expect(Math.max(Math.abs(direction.x), Math.abs(direction.y), Math.abs(direction.z))).toBeCloseTo(1, 5);
    }
  });

  it('never touches the cached geometry or any other material', () => {
    const { wrapper, planting, plantingGeometry, wall, wallGeometry } = model();
    const original = [...plantingGeometry.attributes.position.array];
    const owned = keepPropsRigidUnderStretch(wrapper, 0.7, 1.4, options);
    expect(planting.geometry).toBe(owned[0]);
    expect(planting.geometry).not.toBe(plantingGeometry);
    expect([...plantingGeometry.attributes.position.array]).toEqual(original);
    expect(wall.geometry).toBe(wallGeometry);
  });

  it('does nothing at 100%, for unlisted materials, or when every part is too large', () => {
    expect(keepPropsRigidUnderStretch(model().wrapper, 1, 1, options)).toEqual([]);
    expect(keepPropsRigidUnderStretch(model().wrapper, 1.2, 1, { materialNames: [], maxSizeM: 2.5 })).toEqual([]);
    expect(keepPropsRigidUnderStretch(model().wrapper, 1.2, 1, { materialNames: ['CLAY_TIMBER'], maxSizeM: 2.5 })).toEqual([]);
    const { wrapper, planting, plantingGeometry } = model();
    expect(keepPropsRigidUnderStretch(wrapper, 1.2, 1, { materialNames: ['CLAY_PLANTING'], maxSizeM: 0.1 })).toEqual([]);
    expect(planting.geometry).toBe(plantingGeometry);
  });

  it('treats touching parts as one prop so a canopy of several pieces stays together', () => {
    const wrapper = new THREE.Group();
    const a = new THREE.BoxGeometry(1, 1, 1).translate(4, 0.5, 0).toNonIndexed();
    const b = new THREE.BoxGeometry(1, 1, 1).translate(5.01, 0.5, 0).toNonIndexed();
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute([...a.attributes.position.array, ...b.attributes.position.array], 3));
    const tree = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ name: 'CLAY_PLANTING' }));
    wrapper.add(tree);
    keepPropsRigidUnderStretch(wrapper, 1.4, 1, options);
    wrapper.scale.set(1.4, 1, 1);
    tree.updateWorldMatrix(true, false);
    const box = new THREE.Box3().setFromObject(tree, true);
    // Two 1 m pieces 1 cm apart: still 2.01 m together, not pulled apart.
    expect(box.max.x - box.min.x).toBeCloseTo(2.01, 4);
    expect((box.max.x + box.min.x) / 2).toBeCloseTo(4.505 * 1.4, 4);
  });
});
