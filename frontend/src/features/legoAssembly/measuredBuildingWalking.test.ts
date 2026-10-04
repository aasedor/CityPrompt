import { afterEach, describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import registry from '@/data/buildingWalkDoors.json';
import validation from '@/data/validationCatalogue.json';
import expansion from '@/data/classroomExpansion.json';
import { advanceParkWalk, parkWalkHeight } from '@/features/parks/parkWalking';
import { measuredWalkPlan, resolveMeasuredWalkPlan, prepareMeasuredBuildingWalking, type MeasuredWalkPlan } from './measuredBuildingWalking';

afterEach(() => vi.restoreAllMocks());

const plan = (): MeasuredWalkPlan => ({ variantId: 'test', revision: 'a'.repeat(64), floorMaterials: ['CLAY_FLOOR'],
  doors: [{ origin: [0, -2, 0], tangent: [1, 0, 0], inward: [0, 1, 0], u: 0, z: .1, width: 1.2, height: 2.5, inset: .2 }] });
function fixture() {
  const source = new THREE.Group();
  const add = (name: string, size: number[], center: number[]) => {
    const material = new THREE.MeshStandardMaterial({ side: THREE.DoubleSide }); material.name = name;
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size as [number, number, number]), material);
    mesh.position.set(...center as [number, number, number]); source.add(mesh); return mesh;
  };
  add('CLAY_FLOOR', [6, .1, 6], [0, .05, 0]);
  add('CLAY_MORTAR', [2.4, 3, .3], [-1.8, 1.6, 2]);
  add('CLAY_MORTAR', [2.4, 3, .3], [1.8, 1.6, 2]);
  const leaf = add('CLAY_MORTAR', [1.07, 2.45, .055], [0, 1.345, 1.8]);
  source.updateMatrixWorld(true);
  const hit = (x: number, z: number) => {
    const ray = new THREE.Raycaster(new THREE.Vector3(x, z, 3), new THREE.Vector3(0, 0, -1), 0, 2);
    source.updateMatrixWorld(true); return ray.intersectObject(source, true).length > 0;
  };
  return { source, add, leaf, hit };
}

describe('walking on measured model geometry', () => {
  it('opens only the measured leaf and restores shared geometry after walking', () => {
    const { source, leaf, hit } = fixture(), original = leaf.geometry;
    const walking = prepareMeasuredBuildingWalking(source, plan())!;
    expect(hit(0, 1.4)).toBe(true);
    walking.setOpen(true);
    expect(leaf.geometry).not.toBe(original); expect(hit(0, 1.4)).toBe(false); expect(hit(2, 1.4)).toBe(true);
    let p: [number, number, number] = [0, -2.3, .1];
    for (let i = 0; i < 20; i++) p = advanceParkWalk(walking.network, p, [0, p[1] + .08]);
    expect(p[1]).toBeGreaterThan(-1); expect(p[2]).toBeCloseTo(.1);
    expect(parkWalkHeight(walking.network, 2, -2, .1)).toBeNull();
    walking.setOpen(false); expect(leaf.geometry).toBe(original); expect(hit(0, 1.4)).toBe(true);
    walking.dispose(); expect(leaf.geometry).toBe(original);
  });
  it('cuts a doorway in a shared pane while retaining glazing above and beside it', () => {
    const { source, leaf, add, hit } = fixture(); source.remove(leaf);
    const pane = add('CLAY_GLASS', [6, 6, .05], [0, 3.1, 1.8]), original = pane.geometry;
    const walking = prepareMeasuredBuildingWalking(source, { ...plan(), clipSharedGlass: true })!;
    walking.setOpen(true);
    expect(hit(0, 1.4)).toBe(false); expect(hit(0, 4)).toBe(true); expect(hit(2, 1.4)).toBe(true);
    walking.dispose(); expect(pane.geometry).toBe(original); expect(hit(0, 1.4)).toBe(true);
  });
  it('registers the actual top of a visible threshold and removes owned fixtures on disposal', () => {
    const { source } = fixture(), count = source.children.length;
    const walking = prepareMeasuredBuildingWalking(source, { ...plan(), thresholdBridges: [{ center: [0, -2.2, .15], size: [.8, .2, .1] }] })!;
    walking.setOpen(true);
    expect(parkWalkHeight(walking.network, 0, -2.2, .1)).toBeCloseTo(.2);
    const bridge = source.getObjectByName('measured-door-threshold') as THREE.Mesh;
    expect(bridge.visible).toBe(true);
    walking.setOpen(false); expect(bridge.visible).toBe(false);
    walking.dispose(); expect(source.children).toHaveLength(count);
  });
  it('rejects an empty model and a changed content revision', () => {
    expect(prepareMeasuredBuildingWalking(new THREE.Group(), plan())).toBeNull();
    expect(measuredWalkPlan('changed')).toBeNull();
    expect(measuredWalkPlan(null, '/model-library/models/reference-fourplex-v1.glb')).toBeNull();
    expect(measuredWalkPlan('22538e0683d0ee64995c5c24d20972c9b86ca84fa615ca20fec346a908bb1732')).not.toBeNull();
    const entry=registry.entries[0];
    const url=`/api/v1/files/models/${entry.modelBasename}?v=${entry.revision.slice(0,12)}`;
    expect(measuredWalkPlan(null,url)?.revision).toBe(entry.revision);
    expect(measuredWalkPlan(null,url+'wrong')).toBeNull();
    expect(measuredWalkPlan(null,url.replace(entry.modelBasename,'other.glb'))).toBeNull();
  });
  it('requires an exact walking binding for every current catalogue building revision', () => {
    // These five immutable revisions already contain authored walking extras.
    const embedded=new Set([
      'da8ad808774d542d9b4f6216f3c9589b40633a6c56222ab05c9863fe6cdd712b',
      'ca7066e8dc41f1d1e258ec5b162ed832787d576be8ee67d7449ddfa3850741fb',
      'fd009321f395d1d17410997c392805a0bcb5c199f22038377d8cb7e39019faa7',
      '179d762168f9eefe07161b7c6f5b5911f50cc66150c9e4d53fb7f702a13a4add',
      'dd021c969344cf7380320665a431ccacf190bc8a5a5b3967d7a4aaff8d205a8f',
    ]);
    for(const entry of [...validation.entries,...expansion.entries].filter(e=>e.domain==='building'))
      expect(embedded.has(entry.sha256)||measuredWalkPlan(entry.sha256)!==null,entry.variant_id).toBe(true);
    expect(new Set(registry.entries.map(e=>e.revision)).size).toBe(registry.entries.length);
    for(const entry of registry.entries) {
      expect(entry.revision).toMatch(/^[a-f0-9]{64}$/);
      expect(entry.doors.length,entry.variantId).toBeGreaterThan(0);
      for(const door of entry.doors) {
        expect(door.width).toBeGreaterThanOrEqual(.8); expect(door.height).toBeGreaterThanOrEqual(1.85);
        expect(Math.hypot(...door.inward)).toBeCloseTo(1);
        expect(door.inward[0]*door.tangent[0]+door.inward[1]*door.tangent[1]).toBeCloseTo(0);
      }
    }
  });
  it('verifies bytes for legacy recipes and rejects HTML or a changed served model', async () => {
    const entry=registry.entries[0], bytes=new ArrayBuffer(24), header=new DataView(bytes);
    header.setUint32(0,0x46546c67,true); header.setUint32(8,24,true);
    const fetcher=vi.spyOn(globalThis,'fetch').mockResolvedValue(new Response(bytes));
    const digest=Uint8Array.from(entry.revision.match(/../g)!,byte=>parseInt(byte,16));
    vi.spyOn(crypto.subtle,'digest').mockResolvedValueOnce(digest.buffer);
    expect((await resolveMeasuredWalkPlan(null,'/legacy-unversioned.glb'))?.revision).toBe(entry.revision);
    expect((await resolveMeasuredWalkPlan(null,'/legacy-unversioned.glb'))?.revision).toBe(entry.revision);
    expect(fetcher).toHaveBeenCalledTimes(1);
    fetcher.mockResolvedValueOnce(new Response('<html>application fallback</html>'));
    expect(await resolveMeasuredWalkPlan(null,'/legacy-missing.glb')).toBeNull();
    fetcher.mockResolvedValueOnce(new Response(bytes));
    expect(await resolveMeasuredWalkPlan(null,'/legacy-changed.glb')).toBeNull();
  });
});
