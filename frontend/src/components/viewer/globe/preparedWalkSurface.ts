import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { sharedSiteGroundContains } from './sharedSiteGround';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';

/** Pick visible prepared ground, retaining authored roof hits for the entry guard. */
export function preparedWalkSurface(raycaster: THREE.Raycaster, zones: SiteZone[], scene: THREE.Object3D | null,
  tiles: THREE.Object3D | null | undefined, fallbackHeight: number): { lngLat: [number, number]; height: number } | null {
  const boundary = getActiveSiteBoundary(zones);
  if (!boundary || boundary.properties?.terrain_strategy === 'landscape') return null;
  const level = resolvePreparedSiteTerrainForZone(boundary, zones, fallbackHeight);
  if (level === null || !boundary.coordinates[0]) return null;
  const [lng, lat] = boundary.coordinates[0], radians = Math.PI / 180;
  const origin = WGS84_ELLIPSOID.getCartographicToPosition(lat*radians, lng*radians, level, new THREE.Vector3());
  const up = WGS84_ELLIPSOID.getCartographicToNormal(lat*radians, lng*radians, new THREE.Vector3());
  const point = raycaster.ray.intersectPlane(new THREE.Plane().setFromNormalAndCoplanarPoint(up, origin), new THREE.Vector3());
  if (!point) return null;
  const position = (p: THREE.Vector3): [number,number] => {
    const c = WGS84_ELLIPSOID.getPositionToCartographic(p, {} as never);
    return [c.lon/radians,c.lat/radians];
  };
  const lngLat = position(point);
  if (!sharedSiteGroundContains(boundary.coordinates as [number,number][], ...lngLat)) return null;
  const meshes: THREE.Object3D[] = [];
  const visit = (object: THREE.Object3D) => {
    if (!object.visible || object === tiles) return;
    if ((object as THREE.Mesh).isMesh) meshes.push(object);
    object.children.forEach(visit);
  };
  if (scene) visit(scene);
  // A foreground off-site roof remains visible even when this ray eventually
  // reaches prepared land. Only tile hits inside the cleared polygon are masked.
  const contextHits = tiles ? raycaster.intersectObject(tiles, true).filter(hit =>
    !sharedSiteGroundContains(boundary.coordinates as [number,number][], ...position(hit.point))) : [];
  const hit = [...raycaster.intersectObjects(meshes, false), ...contextHits]
    .sort((a,b) => a.distance-b.distance)
    .find(hit => hit.distance <= raycaster.ray.origin.distanceTo(point) + .5);
  return hit ? { lngLat: position(hit.point), height: WGS84_ELLIPSOID.getPositionElevation(hit.point) }
    : { lngLat, height: level };
}
