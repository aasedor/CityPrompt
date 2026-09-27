import * as THREE from 'three';
import type { NativeParkLayout } from './nativeParkRegistry';
import { verifiedScene } from './nativeParkAssets';

type Point = [number, number];
type PavingProbe = (point: Point) => number | null;
const pavingMeshes = new WeakMap<THREE.Group, THREE.Mesh[]>();

/** Read the verified assembly's actual paving; never infer a path from its bbox. */
export function nativePavingProbe(layout: NativeParkLayout): PavingProbe {
  if (layout.mode === 'module_assembly') return ([x, y]) => {
    let material: string | null = 'grass';
    for (const region of layout.surfaceRegions) {
      if (Math.abs(x - region.x) <= region.width / 2 && Math.abs(y - region.y) <= region.depth / 2) material = region.material;
    }
    return material === 'paving' ? 0 : null;
  };
  const scene = verifiedScene(layout.assets.assembly!);
  let meshes = pavingMeshes.get(scene);
  if (!meshes) {
    scene.updateMatrixWorld(true);
    meshes = [];
    scene.traverse(object => {
      if (!(object instanceof THREE.Mesh)) return;
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      if (materials.some(material => material.name === 'paving')) meshes!.push(object);
    });
    pavingMeshes.set(scene, meshes);
  }
  const ray = new THREE.Raycaster();
  return ([x, y]) => {
    // Source GLBs are Y-up. Runtime plan Y is source -Z.
    ray.set(new THREE.Vector3(x, 100, -y), new THREE.Vector3(0, -1, 0));
    const hit = ray.intersectObjects(meshes!, false).find(candidate => {
      const mesh = candidate.object as THREE.Mesh;
      const material = Array.isArray(mesh.material) ? mesh.material[candidate.face?.materialIndex ?? 0] : mesh.material;
      return material.name === 'paving';
    });
    return hit ? hit.point.y : null;
  };
}

/** Retain the missing approach, then stop at the first full-width native path. */
export function trimAccessAtNativePaving(path: Point[], width: number, probe: PavingProbe): { path: Point[]; endHeight: number } {
  if (path.length < 2) return { path, endHeight: .025 };
  const result = [path[0]];
  for (let i = 1; i < path.length; i++) {
    const a = path[i - 1], b = path[i];
    const dx = b[0] - a[0], dy = b[1] - a[1], length = Math.hypot(dx, dy);
    if (length < .001) continue;
    const at = (t: number): Point => [a[0] + dx * t, a[1] + dy * t];
    const heightAt = (t: number) => {
      const p = at(t), ox = -dy / length * width * .49, oy = dx / length * width * .49;
      const heights = [probe(p), probe([p[0] + ox, p[1] + oy]), probe([p[0] - ox, p[1] - oy])];
      return heights.every(value => value !== null) ? Math.max(...heights as number[]) : null;
    };
    const steps = Math.ceil(length / .25);
    for (let step = 0; step <= steps; step++) {
      const t = step / steps, height = heightAt(t);
      if (height === null) continue;
      let low = Math.max(0, (step - 1) / steps), high = t;
      for (let n = 0; n < 8; n++) {
        const mid = (low + high) / 2;
        if (heightAt(mid) === null) low = mid; else high = mid;
      }
      result.push(at(high));
      return { path: result, endHeight: height + .005 };
    }
    result.push(b);
  }
  return { path: result, endHeight: .025 };
}
