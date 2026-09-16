import { expect, it } from 'vitest';
import { BoxGeometry, Group, Mesh, MeshBasicMaterial, Raycaster, Vector3 } from 'three';
import { restoreContextMaterials, setContextMaterialVisibility } from './contextVisibility';

it('changes only context drawing; the same ground remains raycastable and transforms stay exact', () => {
  const root = new Group();
  const material = new MeshBasicMaterial();
  const mesh = new Mesh(new BoxGeometry(10, 10, 1), material); root.add(mesh); root.updateMatrixWorld(true);
  const matrix = mesh.matrixWorld.toArray();
  const ray = new Raycaster(new Vector3(0, 0, 10), new Vector3(0, 0, -1));
  const before = ray.intersectObject(root).map(hit => hit.point.toArray());
  const originals = new Map(); setContextMaterialVisibility(root, false, originals);
  expect(material.visible).toBe(false); expect(mesh.visible).toBe(true);
  expect(ray.intersectObject(root).map(hit => hit.point.toArray())).toEqual(before);
  expect(mesh.matrixWorld.toArray()).toEqual(matrix);
  restoreContextMaterials(originals); expect(material.visible).toBe(true);
  mesh.geometry.dispose(); material.dispose();
});

it('does not reveal an originally hidden material after switching back', () => {
  const root = new Group(), material = new MeshBasicMaterial(); material.visible = false;
  const mesh = new Mesh(new BoxGeometry(), material); root.add(mesh);
  const originals = new Map(); setContextMaterialVisibility(root, false, originals);
  setContextMaterialVisibility(root, true, originals); restoreContextMaterials(originals);
  expect(material.visible).toBe(false); expect(originals.size).toBe(0);
  mesh.geometry.dispose(); material.dispose();
});
