import { expect, it } from 'vitest';
import { BoxGeometry, Group, Mesh, MeshBasicMaterial, Raycaster, Vector3 } from 'three';
import { pickProjectDetail } from '@/features/parks/detailInstances';

it('selects an individual non-instanced character through its authored wrapper identity', () => {
  const scene = new Group(), wrapper = new Group();
  wrapper.userData.projectDetailId = 'person-1';
  wrapper.add(new Mesh(new BoxGeometry(.5, 1.8, .3), new MeshBasicMaterial())); scene.add(wrapper);
  scene.updateMatrixWorld(true);
  expect(pickProjectDetail(scene, new Raycaster(new Vector3(0, 0, 5), new Vector3(0, 0, -1)))).toBe('person-1');
  wrapper.visible = false;
  expect(pickProjectDetail(scene, new Raycaster(new Vector3(0, 0, 5), new Vector3(0, 0, -1)))).toBeNull();
});
