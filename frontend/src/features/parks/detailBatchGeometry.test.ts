import { describe, expect, it, vi } from 'vitest';
import { BoxGeometry, BufferAttribute, Group, InstancedMesh, Matrix4, Mesh, MeshStandardMaterial, Raycaster, Vector3 } from 'three';
import { buildDetailInstances, disposeDetailInstances, pickProjectDetail } from './detailInstances';

describe('static safety material batches', () => {
  const placements = [new Matrix4(), new Matrix4().makeTranslation(10, 0, 0)];
  function source() {
    const root = new Group(), material = new MeshStandardMaterial();
    for (const x of [0, 3]) { const mesh = new Mesh(new BoxGeometry(), material); mesh.position.x = x; root.add(mesh); }
    return root;
  }
  it('merges equal materials without changing source vertices or placement picking', () => {
    const root = source();
    const before = (root.children[0] as Mesh).geometry.attributes.position.array.slice();
    const result = buildDetailInstances(root, placements, true);
    expect(result.children).toHaveLength(1);
    const batch = result.children[0] as InstancedMesh;
    expect(batch.count).toBe(2);
    batch.geometry.computeBoundingBox();
    expect(batch.geometry.boundingBox!.min.x).toBeCloseTo(-.5);
    expect(batch.geometry.boundingBox!.max.x).toBeCloseTo(3.5);
    expect(batch.geometry.attributes.position.count).toBe(48);
    expect((root.children[0] as Mesh).geometry.attributes.position.array).toEqual(before);
    result.userData.projectDetailIds = ['first', 'second']; result.updateMatrixWorld(true);
    expect(pickProjectDetail(result, new Raycaster(new Vector3(13,0,5), new Vector3(0,0,-1)))).toBe('second');
    disposeDetailInstances(result);
  });
  it('keeps different materials and UV signatures in separate batches', () => {
    const root = source(), third = new Mesh(new BoxGeometry(), new MeshStandardMaterial({color:'red'}));
    root.add(third);
    const second = root.children[1] as Mesh;
    second.geometry.deleteAttribute('uv');
    const result = buildDetailInstances(root, placements, true);
    expect(result.children).toHaveLength(3);
    expect((result.children[0] as Mesh).material).toBe((root.children[0] as Mesh).material);
    expect((result.children[1] as Mesh).geometry.attributes.uv).toBeUndefined();
    disposeDetailInstances(result);
  });
  it('keeps the cache owned by the GLTF source through effect replay and abandoned renders', async () => {
    const root = source(), original = (root.children[0] as Mesh).geometry;
    const originalDispose = vi.spyOn(original, 'dispose');
    const a = buildDetailInstances(root, placements, true), b = buildDetailInstances(root, placements, true);
    const geometry = (a.children[0] as Mesh).geometry, disposed = vi.spyOn(geometry, 'dispose');
    expect((b.children[0] as Mesh).geometry).toBe(geometry);
    disposeDetailInstances(a); await Promise.resolve(); expect(disposed).not.toHaveBeenCalled();
    disposeDetailInstances(b); await Promise.resolve(); expect(disposed).not.toHaveBeenCalled();
    expect(originalDispose).not.toHaveBeenCalled();
    const replay = buildDetailInstances(root, placements, true);
    expect((replay.children[0] as Mesh).geometry).toBe(geometry);
    disposeDetailInstances(replay);
    original.dispose();
    expect(disposed).toHaveBeenCalledOnce();
  });
  it('preserves negative-scale, animated and transparent models on the original path', () => {
    for (const kind of ['negative', 'animated', 'transparent']) {
      const root = source();
      if (kind === 'negative') root.children[0].scale.x = -1;
      if (kind === 'animated') (root.children[0] as Mesh).geometry.morphAttributes.position = [new BufferAttribute(new Float32Array(72),3)];
      if (kind === 'transparent') ((root.children[0] as Mesh).material as MeshStandardMaterial).transparent = true;
      const result = buildDetailInstances(root, placements, true);
      expect(result.children).toHaveLength(2);
      expect((result.children[0] as Mesh).geometry).toBe((root.children[0] as Mesh).geometry);
      disposeDetailInstances(result);
    }
  });
});
