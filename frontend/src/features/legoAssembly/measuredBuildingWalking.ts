import * as THREE from 'three';
import registry from '@/data/buildingWalkDoors.json';
import { parkWalkHeight, nearestParkWalkPoint, type WalkPoint } from '@/features/parks/parkWalking';
import type { BuildingWalkNetwork } from './buildingWalking';

export interface MeasuredDoor {
  origin: number[]; tangent: number[]; inward: number[];
  u: number; z: number; width: number; height: number; inset: number;
}
export interface MeasuredWalkPlan {
  variantId: string; revision: string; floorMaterials: string[]; doors: MeasuredDoor[];
  modelBasename?: string;
  clipSharedGlass?: boolean;
  cutCarrierMaterials?: string[];
  clipLeafMaterials?: string[];
  thresholdBridges?: { center: number[]; size: number[] }[];
}
export function measuredWalkPlan(revision: unknown, modelUrl?: string): MeasuredWalkPlan | null {
  if (typeof revision === 'string') {
    const exact = registry.entries.find(entry => entry.revision === revision);
    if (exact) return exact;
  }
  // Imported library files have an immutable content-version query. A name or
  // archetype match alone cannot authorize a different model's door geometry.
  if (!modelUrl) return null;
  try {
    const url = new URL(modelUrl, 'http://localhost');
    return (registry.entries as MeasuredWalkPlan[]).find(entry =>
      url.searchParams.get('v') === entry.revision.slice(0, 12)
      && decodeURIComponent(url.pathname).endsWith(`/${entry.modelBasename ?? '\0'}`)) ?? null;
  } catch { return null; }
}

const modelPlans = new Map<string, Promise<MeasuredWalkPlan | null>>();
/** Legacy saved recipes may predate content-version URLs and picker stamps.
 * Verify their served bytes before applying any recorded door coordinates. */
export async function resolveMeasuredWalkPlan(revision: unknown, modelUrl: string): Promise<MeasuredWalkPlan | null> {
  const declared = measuredWalkPlan(revision, modelUrl);
  if (declared) return declared;
  let pending = modelPlans.get(modelUrl);
  if (!pending) {
    pending = (async () => {
      try {
        const response = await fetch(modelUrl);
        if (!response.ok) return null;
        const bytes = await response.arrayBuffer();
        const header = new DataView(bytes);
        if (bytes.byteLength < 20 || header.getUint32(0, true) !== 0x46546c67 || header.getUint32(8, true) !== bytes.byteLength) return null;
        const hash = await crypto.subtle.digest('SHA-256', bytes);
        const digest = Array.from(new Uint8Array(hash), value => value.toString(16).padStart(2, '0')).join('');
        return measuredWalkPlan(digest);
      } catch { return null; }
    })();
    modelPlans.set(modelUrl, pending);
  }
  return pending;
}

function doorCoordinates(p: THREE.Vector3, door: MeasuredDoor) {
  const x = p.x - door.origin[0], y = -p.z - door.origin[1];
  return [x * door.tangent[0] + y * door.tangent[1] - door.u,
    x * door.inward[0] + y * door.inward[1], p.y - door.z];
}
/** Only the measured operable leaf, its inset panels and hardware. The cut
 * carrier, fixed jambs, header and threshold remain visible and collidable. */
function onLeaf(p: THREE.Vector3, d: MeasuredDoor) {
  const [u, depth, z] = doorCoordinates(p, d);
  return Math.abs(u) <= d.width / 2 - .02 && depth >= d.inset - .18 && depth <= d.inset + .18
    && z >= -.02 && z <= d.height - .025;
}

/** Clip a large glass panel around a measured leaf while retaining its fixed
 * glazing above and beside the door. Used where the source shares one pane. */
function openGlassPanel(geometry: THREE.BufferGeometry, matrix: THREE.Matrix4, doors: MeasuredDoor[], carrier = false) {
  const names = Object.keys(geometry.attributes), attributes: Record<string, number[]> = {};
  for (const name of names) attributes[name] = [];
  type Vertex = Record<string, number[]>;
  const interpolate = (a: Vertex, b: Vertex, t: number): Vertex => Object.fromEntries(names.map(name =>
    [name, a[name].map((v, i) => v + (b[name][i] - v) * t)]));
  const coordinate = (v: Vertex, door: MeasuredDoor) => doorCoordinates(new THREE.Vector3(...v.position as [number, number, number]).applyMatrix4(matrix), door);
  const emit = (polygon: Vertex[]) => {
    for (let i = 1; i < polygon.length - 1; i++) for (const v of [polygon[0], polygon[i], polygon[i + 1]])
      for (const name of names) attributes[name].push(...v[name]);
  };
  const count = geometry.index?.count ?? geometry.getAttribute('position').count;
  for (let i = 0; i < count; i += 3) {
    let pieces: Vertex[][] = [[0, 1, 2].map(j => {
      const id = geometry.index ? geometry.index.getX(i + j) : i + j;
      return Object.fromEntries(names.map(name => { const a = geometry.getAttribute(name);
        return [name, Array.from({ length: a.itemSize }, (_, k) => a.getComponent(id, k))]; }));
    })];
    for (const door of doors) {
      pieces = pieces.flatMap(polygon => {
        if (!polygon.every(v => { const p = coordinate(v, door); return p[1] >= (carrier ? -.4 : door.inset - .18) && p[1] <= (carrier ? .7 : door.inset + .18); })) return [polygon];
        let inside = polygon;
        const outside: Vertex[][] = [];
        const planes = [[0, 1, door.width / 2 - .02], [0, -1, door.width / 2 - .02], [2, 1, door.height - .025], [2, -1, .02]];
        for (const [axis, sign, bound] of planes) {
          if (!inside.length) break;
          const yes: Vertex[] = [], no: Vertex[] = [];
          for (let k = 0; k < inside.length; k++) {
            const a = inside[k], b = inside[(k + 1) % inside.length];
            const da = coordinate(a, door)[axis] * sign - bound, db = coordinate(b, door)[axis] * sign - bound;
            (da <= 0 ? yes : no).push(a);
            if ((da <= 0) !== (db <= 0)) { const v = interpolate(a, b, da / (da - db)); yes.push(v); no.push(v); }
          }
          if (no.length >= 3) outside.push(no);
          inside = yes;
        }
        return outside;
      });
    }
    pieces.forEach(emit);
  }
  const result = new THREE.BufferGeometry();
  for (const name of names) result.setAttribute(name, new THREE.Float32BufferAttribute(attributes[name], geometry.getAttribute(name).itemSize));
  result.computeBoundingBox(); result.computeBoundingSphere();
  // Positions remain in this mesh's original local coordinates.
  return result;
}

/** Derive ground-floor navigation from the exact mounted GLB, never a proxy
 * rectangle. The source cache and GLB bytes stay immutable. Doors are held
 * open for walking and restored on exit; every edited geometry is owned here. */
export function prepareMeasuredBuildingWalking(source: THREE.Object3D, plan: MeasuredWalkPlan) {
  // Visible steel thresholds bridge measured gaps at the fourplex and Plateau
  // entries. These are real support geometry and restore on exit.
  const bridges = (plan.thresholdBridges ?? []).map(({ center, size }) => {
    const geometry = new THREE.BoxGeometry(size[0], size[2], size[1]);
    const material = new THREE.MeshStandardMaterial({ color: '#84817a', roughness: .8 }); material.name = 'walking_threshold';
    const mesh = new THREE.Mesh(geometry, material); mesh.name = 'measured-door-threshold';
    mesh.position.set(center[0], center[2], -center[1]); mesh.visible = false; source.add(mesh); return mesh;
  });
  source.updateWorldMatrix(true, true);
  const inverse = source.matrixWorld.clone().invert(), floorMaterials = new Set(plan.floorMaterials);
  floorMaterials.add('walking_threshold');
  const triangles: number[][][] = [], barriers: number[][] = [];
  const edits: { mesh: THREE.Mesh; original: THREE.BufferGeometry; open: THREE.BufferGeometry }[] = [];
  const box = new THREE.Box3(), allMaterials = new Set<string>();
  source.traverse(object => {
    if (object instanceof THREE.Mesh) for (const material of Array.isArray(object.material) ? object.material : [object.material]) allMaterials.add(material.name);
  });
  const z0 = Math.min(...plan.doors.map(d => d.z)), a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
  const normal = new THREE.Vector3(), edge = new THREE.Vector3();
  const point = (p: THREE.Vector3) => [p.x, -p.z, p.y];
  source.traverse(object => {
    if (!(object instanceof THREE.Mesh) || !object.geometry.getAttribute('position')) return;
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    const matrix = inverse.clone().multiply(object.matrixWorld);
    const original: THREE.BufferGeometry = object.geometry;
    // Large, shared panes are clipped only for these explicitly recorded doors.
    const carrier = materials.length === 1 && plan.cutCarrierMaterials?.includes(materials[0].name);
    const clipped = materials.length === 1 && (carrier || plan.clipLeafMaterials?.includes(materials[0].name) || (/glass|glaz/i.test(materials[0].name) && plan.clipSharedGlass))
      ? openGlassPanel(original, matrix, plan.doors, carrier) : null;
    if (clipped) edits.push({ mesh: object, original, open: clipped });
    const geometry = clipped ?? original, positions = geometry.getAttribute('position'), index = geometry.index, keep: number[] = [];
    let removed = 0;
    const count = index?.count ?? positions.count;
    for (let i = 0; i < count; i += 3) {
      const ids = [0, 1, 2].map(j => index ? index.getX(i + j) : i + j);
      a.fromBufferAttribute(positions, ids[0]).applyMatrix4(matrix);
      b.fromBufferAttribute(positions, ids[1]).applyMatrix4(matrix);
      c.fromBufferAttribute(positions, ids[2]).applyMatrix4(matrix);
      box.expandByPoint(a); box.expandByPoint(b); box.expandByPoint(c);
      const group = geometry.groups.find(g => i >= g.start && i < g.start + g.count);
      const name = materials[materials.length === 1 ? 0 : group?.materialIndex ?? 0]?.name ?? '';
      const leaf = plan.doors.some(d => onLeaf(a, d) && onLeaf(b, d) && onLeaf(c, d));
      // Some opaque leaves share their carrier's material. The measured inset
      // aperture, rather than a material name, distinguishes these door faces.
      if (leaf && !['CLAY_FLOOR', 'CLAY_FOUNDATION', 'walking_threshold'].includes(name)) { removed++; continue; }
      keep.push(...ids);
      const low = Math.min(a.y, b.y, c.y), high = Math.max(a.y, b.y, c.y);
      if (high < -.4 || low > z0 + 1.85) continue;
      normal.subVectors(b, a).cross(edge.subVectors(c, a)).normalize();
      if (floorMaterials.has(name) && normal.y > .8 && high <= z0 + .4) triangles.push([point(a), point(b), point(c)]);
      if (Math.abs(normal.y) > .7 || high - low < .025) continue;
      // Dense brick skins cover the same already-cut solid mortar carrier.
      if (name === 'CLAY_WALL' && allMaterials.has('CLAY_MORTAR')) continue;
      const pts = [a, b, c];
      let pair = [a, b], length = -1;
      for (let j = 0; j < 3; j++) {
        const p = pts[j], q = pts[(j + 1) % 3], l = Math.hypot(p.x - q.x, p.z - q.z);
        if (l > length) { pair = [p, q]; length = l; }
      }
      if (length > .01) barriers.push([pair[0].x, -pair[0].z, pair[1].x, -pair[1].z, low, high]);
    }
    if (removed && !clipped) {
      // A filtered index with original attributes avoids duplicating vertex data.
      // Merged source meshes use one material; multi-material groups need explicit
      // remapping and are deliberately left unsupported here.
      if (materials.length !== 1) return;
      const open = geometry.clone(); open.setIndex(keep); open.clearGroups();
      edits.push({ mesh: object, original: geometry, open });
    }
  });
  const door = plan.doors[0], center = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
  const network: BuildingWalkNetwork = { version: 2, footprint: [size.x, size.z], footprintCenter: [center.x, -center.z],
    entryDirection: [door.inward[0], door.inward[1]], entrance: [], maxStepM: .25, groundFloorOnly: true, triangles, barriers, obstacles: [], routes: [],
    portals: plan.doors.map(d => {
      const x = d.origin[0] + d.tangent[0] * d.u, y = d.origin[1] + d.tangent[1] * d.u;
      return [x - d.width / 2, x + d.width / 2, y - d.width / 2, y + d.width / 2];
    }) };
  const x = door.origin[0] + door.tangent[0] * door.u + door.inward[0] * .55;
  const y = door.origin[1] + door.tangent[1] * door.u + door.inward[1] * .55;
  const entrance = nearestParkWalkPoint(network, x, y, .45, door.z);
  if (!entrance || parkWalkHeight(network, entrance[0], entrance[1], entrance[2]) === null) {
    edits.forEach(edit => edit.open.dispose()); bridges.forEach(mesh => { source.remove(mesh); mesh.geometry.dispose(); mesh.material.dispose(); }); return null;
  }
  network.entrance = entrance as WalkPoint;
  return { network, setOpen: (open: boolean) => { edits.forEach(edit => { edit.mesh.geometry = open ? edit.open : edit.original; }); bridges.forEach(mesh => { mesh.visible = open; }); },
    dispose: () => { edits.forEach(edit => { edit.mesh.geometry = edit.original; edit.open.dispose(); }); bridges.forEach(mesh => { source.remove(mesh); mesh.geometry.dispose(); mesh.material.dispose(); }); } };
}
