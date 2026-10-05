import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import type { WalkPose } from '@/components/viewer/globe/walkNavigation';
import { buildingWalkRevision } from './buildingWalking';

type UpAxis = 'y' | 'z';
interface Inspection {
  zoneId: string; revision: string; object: THREE.Object3D; bounds: THREE.Box3; up: UpAxis;
  restore: (() => void) | null;
}
const mounted = new Map<string, Inspection>();
let active: Inspection | null = null;

/** Exterior-only models have no signed circulation. This explicitly separate
 * inspection camera adds no rooms/floors and does not authorize a walking route. */
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
  const point = record.bounds.getCenter(new THREE.Vector3());
  point[record.up] = record.bounds.min[record.up] + .05;
  const origin = world(record, point, 0), inward = point.clone();
  if (record.up === 'y') inward.z -= 1; else inward.y += 1;
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
