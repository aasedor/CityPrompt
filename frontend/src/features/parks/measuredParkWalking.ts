import * as THREE from 'three';
import type { NativeParkLayout } from './nativeParkRegistry';
import { verifiedScene } from './nativeParkAssets';
import { nearestParkWalkPoint, type ParkWalkingNetwork } from './parkWalking';

const cache = new WeakMap<THREE.Group, ParkWalkingNetwork | null>();
/** Flat park routes use the verified assembly's actual dry surface faces.
 * Authored multi-level networks continue to own stairs, bridges and lifts. */
export function measuredParkWalking(layout: NativeParkLayout, loadedScene?: THREE.Group): ParkWalkingNetwork | null {
  if (layout.mode === 'module_assembly') {
    const rectangle = (x: number, y: number, width: number, depth: number) => {
      const a = [x - width / 2, y - depth / 2, 0], b = [x + width / 2, y - depth / 2, 0];
      const c = [x + width / 2, y + depth / 2, 0], d = [x - width / 2, y + depth / 2, 0];
      return [[a, b, c], [a, c, d]];
    };
    return { version: 2, groundFloorOnly: true, maxStepM: .2, obstacles: [], routes: [],
      entrance: [0, -layout.depthM / 2 + .6, 0],
      triangles: rectangle(0, 0, layout.widthM, layout.depthM),
      hazards: layout.surfaceRegions.filter(r => /water/i.test(r.material ?? '')).flatMap(r => rectangle(r.x, r.y, r.width, r.depth)) };
  }
  const scene = loadedScene ?? verifiedScene(layout.assets.assembly!);
  if (cache.has(scene)) return cache.get(scene)!;
  scene.updateWorldMatrix(true, true);
  const inverse = scene.matrixWorld.clone().invert(), triangles: number[][][] = [], hazards: number[][][] = [], barriers: number[][] = [];
  const surfaces = new Set(layout.walkSurfaceMaterials ?? ['paving', 'grass']);
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), normal = new THREE.Vector3(), edge = new THREE.Vector3();
  scene.traverse(object => {
    if (!(object instanceof THREE.Mesh)) return;
    const g: THREE.BufferGeometry = object.geometry, positions = g.getAttribute('position'), index = g.index;
    if (!positions) return;
    const matrix = inverse.clone().multiply(object.matrixWorld), materials = Array.isArray(object.material) ? object.material : [object.material];
    for (let i = 0; i < (index?.count ?? positions.count); i += 3) {
      a.fromBufferAttribute(positions, index ? index.getX(i) : i).applyMatrix4(matrix);
      b.fromBufferAttribute(positions, index ? index.getX(i + 1) : i + 1).applyMatrix4(matrix);
      c.fromBufferAttribute(positions, index ? index.getX(i + 2) : i + 2).applyMatrix4(matrix);
      const group = g.groups.find(group => i >= group.start && i < group.start + group.count);
      const name = materials[materials.length === 1 ? 0 : group?.materialIndex ?? 0]?.name ?? '';
      const low = Math.min(a.y, b.y, c.y), high = Math.max(a.y, b.y, c.y);
      normal.subVectors(b, a).cross(edge.subVectors(c, a)).normalize();
      const points = [a, b, c].map(p => [p.x, -p.z, p.y]);
      if (normal.y > .8 && /water/i.test(name))
        hazards.push(points.map(p => [p[0], p[1], Math.max(0, p[2])]));
      if (low > 2 || high < -.4) continue;
      if (normal.y > .8 && surfaces.has(name) && high <= .45 && !/roof|bench|table/i.test(object.name)) triangles.push(points);
      if (Math.abs(normal.y) > .7 || high - low < .025 || /leaf|foliage|flower|grass|water/i.test(name)) continue;
      const pairs = [[a, b], [b, c], [c, a]].sort(([p, q], [r, s]) => Math.hypot(r.x - s.x, r.z - s.z) - Math.hypot(p.x - q.x, p.z - q.z));
      const [p, q] = pairs[0];
      if (Math.hypot(p.x - q.x, p.z - q.z) > .01) barriers.push([p.x, -p.z, q.x, -q.z, low, high]);
    }
  });
  const n: ParkWalkingNetwork = { version: 2, groundFloorOnly: true, waterClearanceM: .02, triangles, hazards, barriers, obstacles: [], routes: [], entrance: [], maxStepM: .2 };
  const entry = nearestParkWalkPoint(n, 0, -layout.depthM / 2 + .6);
  const result = entry ? { ...n, entrance: entry } : null;
  cache.set(scene, result); return result;
}
