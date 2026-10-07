import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import type { WalkPose } from '@/components/viewer/globe/walkNavigation';
import { buildingWalkEntrance, buildingWalkRevision } from './buildingWalking';

type UpAxis = 'y' | 'z';
interface Inspection {
  zoneId: string; revision: string; object: THREE.Object3D; bounds: THREE.Box3; up: UpAxis;
  restore: (() => void) | null;
  startPoint?: THREE.Vector3;
  startDirection?: THREE.Vector3;
}
const mounted = new Map<string, Inspection>();
let active: Inspection | null = null;

/** Register actual model geometry for continuous exploration. No inferred
 * rooms or floors are added to exterior-only models. */
export function mountBuildingInspection(id: string, zone: SiteZone, object: THREE.Object3D, up: UpAxis = 'y') {
  if (!object.isObject3D) return () => {};
  object.updateWorldMatrix(true, true);
  const inverse = object.matrixWorld.clone().invert(), bounds = new THREE.Box3();
  object.traverse(child => {
    if (!(child instanceof THREE.Mesh) || !child.visible) return;
    const positions = child.geometry.getAttribute('position');
    if (!positions) return;
    const local = (child.geometry.boundingBox?.clone() ?? new THREE.Box3().setFromBufferAttribute(positions))
      .applyMatrix4(inverse.clone().multiply(child.matrixWorld));
    bounds.union(local);
  });
  const size = bounds.getSize(new THREE.Vector3());
  if (bounds.isEmpty() || ![...bounds.min.toArray(), ...bounds.max.toArray()].every(Number.isFinite)
    || size.x < .5 || size[up === 'y' ? 'z' : 'y'] < .5 || size[up] < 2) return () => {};
  const record: Inspection = { zoneId: zone.id, revision: buildingWalkRevision(zone), object, bounds, up, restore: null };
  mounted.set(id, record);
  return () => {
    record.restore?.(); record.restore = null;
    if (active === record) active = null;
    if (mounted.get(id) === record) mounted.delete(id);
  };
}

function current(zones: SiteZone[], zoneId: string) {
  const zone = zones.find(z => z.id === zoneId);
  if (!zone) return null;
  const revision = buildingWalkRevision(zone);
  return [...mounted.values()].find(record => record.zoneId === zoneId
    && record.revision === revision) ?? null;
}

function world(record: Inspection, point: THREE.Vector3, heading: number): WalkPose {
  record.object.updateWorldMatrix(true, false);
  const p = record.object.localToWorld(point.clone());
  const g = WGS84_ELLIPSOID.getPositionToCartographic(p, { lat: 0, lon: 0, height: 0 });
  return { lng: g.lon * 180 / Math.PI, lat: g.lat * 180 / Math.PI, groundHeight: g.height, heading };
}

function start(record: Inspection): WalkPose {
  // A bounds centre may be inside a party wall or facing furniture. Sample
  // a bounded grid at eye height, using the actual mounted geometry. This
  // chooses a clear inspection viewpoint; it does not infer a walkable route.
  if (!record.startPoint) {
    const depth = record.up === 'y' ? 'z' : 'y';
    const centre = record.bounds.getCenter(new THREE.Vector3());
    centre[record.up] = record.bounds.min[record.up] + .05;
    const directions = [new THREE.Vector3(1, 0, 0), new THREE.Vector3(-1, 0, 0),
      new THREE.Vector3(), new THREE.Vector3()];
    directions[2][depth] = 1; directions[3][depth] = -1;
    record.object.updateWorldMatrix(true, true);
    const ray = new THREE.Raycaster();
    ray.far = Math.max(10, record.bounds.getSize(new THREE.Vector3()).length());
    let best = -Infinity;
    for (const x of [0, -.2, .2, -.35, .35]) for (const y of [0, -.2, .2, -.35, .35]) {
      const point = centre.clone();
      point.x += x * (record.bounds.max.x - record.bounds.min.x);
      point[depth] += y * (record.bounds.max[depth] - record.bounds.min[depth]);
      const eye = point.clone(); eye[record.up] += 1.7;
      record.object.localToWorld(eye);
      const distances = directions.map(direction => {
        ray.set(eye, direction.clone().transformDirection(record.object.matrixWorld));
        return ray.intersectObject(record.object, true)[0]?.distance ?? ray.far;
      });
      const clearance = Math.min(...distances);
      // Landscape and patio geometry can extend the bounds well past the
      // building. Prefer a clear point surrounded by shell surfaces, rather
      // than an unobstructed point outside looking away from the model.
      const enclosed = distances.filter(distance => distance < ray.far).length >= 3;
      const score = Math.min(clearance, 2) + (enclosed && clearance > .45 ? 3 : 0)
        - Math.hypot(x, y) * .2;
      if (score > best) {
        best = score; record.startPoint = point;
        record.startDirection = directions[distances.indexOf(Math.max(...distances))].clone();
      }
    }
  }
  const point = record.startPoint!;
  const origin = world(record, point, 0), inward = point.clone().add(record.startDirection!);
  const next = world(record, inward, 0);
  const east = (next.lng - origin.lng) * Math.cos(origin.lat * Math.PI / 180), north = next.lat - origin.lat;
  return { ...origin, heading: (Math.atan2(east, north) * 180 / Math.PI + 360) % 360 };
}

/** Own temporary material copies: the cached GLB and exterior materials stay
 * unchanged. Interior sides are visible only for the selected inspection. */
function showInteriorSides(record: Inspection) {
  const originals: { mesh: THREE.Mesh; material: THREE.Material | THREE.Material[] }[] = [];
  const copies = new Map<THREE.Material, THREE.Material>();
  // A massing cap already occupies its foundation datum. Its sibling ground
  // finish would compete with that same surface in a logarithmic depth buffer.
  const foundations = record.up === 'z' && record.object instanceof THREE.Mesh
    ? (record.object.parent?.children ?? []).filter(child => child.name === 'landscaped-building-foundation')
      .map(object => ({ object, visible: object.visible })) : [];
  foundations.forEach(item => { item.object.visible = false; });
  record.object.traverse(child => {
    if (!(child instanceof THREE.Mesh)) return;
    originals.push({ mesh: child, material: child.material });
    const copy = (material: THREE.Material) => {
      let owned = copies.get(material);
      if (!owned) {
        owned = material.clone();
        owned.side = THREE.DoubleSide;
        owned.needsUpdate = true;
        copies.set(material, owned);
      }
      return owned;
    };
    child.material = Array.isArray(child.material) ? child.material.map(copy) : copy(child.material);
  });
  return () => {
    originals.forEach(item => { item.mesh.material = item.material; });
    foundations.forEach(item => { item.object.visible = item.visible; });
    copies.forEach(material => material.dispose());
  };
}

export function endBuildingInspection() {
  active?.restore?.();
  if (active) active.restore = null;
  active = null;
}

export function beginBuildingInspection(zones: SiteZone[], zoneId: string): WalkPose | null {
  const record = current(zones, zoneId);
  if (!record) return null;
  endBuildingInspection(); active = record;
  record.restore = showInteriorSides(record);
  return start(record);
}

export function buildingInspectionStart(zones: SiteZone[], zoneId: string): WalkPose | null {
  const record = current(zones, zoneId);
  return record && record === active ? start(record) : null;
}

/** Free shell inspection stays at the model base and inside its measured
 * extents. This is an inspection envelope, not inferred interior circulation. */
export function constrainBuildingInspection(zones: SiteZone[], zoneId: string, pose: WalkPose): WalkPose | null {
  const record = current(zones, zoneId);
  if (!record || record !== active) return null;
  const point = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(pose.lat * Math.PI / 180, pose.lng * Math.PI / 180, pose.groundHeight, point);
  record.object.updateWorldMatrix(true, false); record.object.worldToLocal(point);
  for (const axis of ['x', 'y', 'z'] as const) {
    point[axis] = axis === record.up ? record.bounds.min[axis] + .05
      : THREE.MathUtils.clamp(point[axis], record.bounds.min[axis] + .2, record.bounds.max[axis] - .2);
  }
  return world(record, point, pose.heading);
}

/** Follow existing steps/slopes without jumping onto a roof above the walker.
 * Downward-facing undersides and vertical walls are not ground surfaces. */
function explorationGround(record: Inspection, point: THREE.Vector3): number {
  const up = new THREE.Vector3(); up[record.up] = 1;
  up.transformDirection(record.object.matrixWorld);
  const origin = point.clone(); origin[record.up] += .65;
  record.object.localToWorld(origin);
  const ray = new THREE.Raycaster(origin, up.clone().negate());
  const normalMatrix = new THREE.Matrix3();
  for (const hit of ray.intersectObject(record.object, true)) {
    if (!hit.face || !hit.object.visible) continue;
    const normal = hit.face.normal.clone().applyNormalMatrix(normalMatrix.getNormalMatrix(hit.object.matrixWorld));
    if (normal.dot(up) < .45) continue;
    const surface = record.object.worldToLocal(hit.point.clone())[record.up];
    return Math.max(record.bounds.min[record.up] + .05, surface + .02);
  }
  return record.bounds.min[record.up] + .05;
}

/** Walking across a model boundary is enough to show its inside faces. Keep
 * the same horizontal position and heading, and release the model immediately
 * on exit. Models with verified circulation retain their own floors/doors.
 * This supports exploration of existing geometry; it does not invent rooms. */
export function updateWalkBuildingInspection(zones: SiteZone[], pose: WalkPose): { zoneId: string; pose: WalkPose } | null {
  if (buildingWalkEntrance(zones, pose)) { endBuildingInspection(); return null; }
  for (const record of mounted.values()) {
    if (current(zones, record.zoneId) !== record) continue;
    const point = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToPosition(pose.lat * Math.PI / 180, pose.lng * Math.PI / 180, pose.groundHeight, point);
    record.object.updateWorldMatrix(true, false); record.object.worldToLocal(point);
    const depth = record.up === 'y' ? 'z' : 'y';
    if (point.x < record.bounds.min.x || point.x > record.bounds.max.x
      || point[depth] < record.bounds.min[depth] || point[depth] > record.bounds.max[depth]
      || point[record.up] > record.bounds.max[record.up] + 1) continue;
    if (active !== record) {
      endBuildingInspection(); active = record;
      record.restore = showInteriorSides(record);
    }
    point[record.up] = explorationGround(record, point);
    const groundHeight = world(record, point, pose.heading).groundHeight;
    return { zoneId: record.zoneId, pose: { ...pose, groundHeight } };
  }
  endBuildingInspection();
  return null;
}
