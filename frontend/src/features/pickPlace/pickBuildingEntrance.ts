import type { SiteZone } from '@/types';
import * as THREE from 'three';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { resolveBuildingGroundContact, type BuildingGroundContact, type GroundPoint } from '@/components/viewer/globe/buildingGroundContact';
import { buildBuildingEntranceApproach } from '@/components/viewer/globe/buildingEntranceApproach';
import { buildingGroundProblemMessage } from '@/components/viewer/globe/buildingGroundProblemMessage';
import type { SharedSiteGroundState } from '@/components/viewer/globe/SharedSiteGroundProvider';
import { rectangleDimensions } from './geometry';
import { readBuildingEntrance, resolvePedestrianConnections, type BuildingEntrance } from './pedestrianConnections';

/** A hit on the real native model, in its displayed foundation's ENU frame. */
export interface NativeEntranceHit {
  point: [number, number, number];
  footprints: GroundPoint[][];
  lng: number;
  lat: number;
  contact: BuildingGroundContact;
  ray?: { origin: [number,number,number]; direction: [number,number,number]; distance: number };
}
export interface EntrancePickResult {
  anchor: BuildingEntrance;
  status: 'ready' | 'unresolved';
  message: string;
}
export interface EntrancePickRequest {
  zoneId: string;
  zoneKey: string;
  properties: SiteZone['properties'];
  finish: (result: EntrancePickResult | null) => void;
}
export const entrancePickZoneKey = (zone: SiteZone) => JSON.stringify([zone.updated_at,zone.coordinates,zone.properties,zone.building_id]);

type TexturePixels = { width: number; height: number; data: Uint8ClampedArray | Uint8Array };
const texturePixels = new WeakMap<THREE.Texture,{version:number;pixels:TexturePixels|null}>();
function textureChannel(texture: THREE.Texture, uv: THREE.Vector2, channel: number): number {
  let cached=texturePixels.get(texture);
  if (!cached || cached.version!==texture.version) {
    let pixels:TexturePixels|null=null;
    try {
      const source=texture.image;
      if (source?.data instanceof Uint8Array && texture.format===THREE.RGBAFormat) pixels=source;
      else if (source?.width && source?.height) {
        const canvas=document.createElement('canvas');canvas.width=source.width;canvas.height=source.height;
        const context=canvas.getContext('2d',{willReadFrequently:true});
        context?.drawImage(source,0,0);
        if(context)pixels=context.getImageData(0,0,canvas.width,canvas.height);
      }
    } catch { /* An unreadable texture remains conservatively opaque. */ }
    cached={version:texture.version,pixels};texturePixels.set(texture,cached);
  }
  if (!cached.pixels) return 1;
  const point=texture.transformUv(uv.clone()),{width,height,data}=cached.pixels;
  const x=Math.max(0,Math.min(width-1,Math.floor(point.x*width))),y=Math.max(0,Math.min(height-1,Math.floor(point.y*height)));
  return data[(y*width+x)*4+channel]/255;
}

/** R3F events intersect interactive meshes only. Check visible scene geometry
 * as well so a tree, terrain ridge, or another house cannot be clicked through. */
export function entrancePickOccluded(scene: THREE.Object3D, hit: NativeEntranceHit): boolean {
  if (!hit.ray) return true;
  const raycaster = new THREE.Raycaster(new THREE.Vector3(...hit.ray.origin),new THREE.Vector3(...hit.ray.direction),0,Math.max(0,hit.ray.distance-.03));
  const meshes: THREE.Object3D[] = [];
  scene.traverseVisible(object => {
    if (!(object instanceof THREE.Mesh)) return;
    for (let cursor: THREE.Object3D|null = object; cursor; cursor=cursor.parent)
      if (cursor.userData.siteforgeExcludeFromDirect3DCapture) return;
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    if (materials.some(m=>m.visible && m.colorWrite && (!m.transparent || m.opacity>.1))) meshes.push(object);
  });
  return raycaster.intersectObjects(meshes,false).some(intersection=>{
    const mesh=intersection.object as THREE.Mesh;
    const material=(Array.isArray(mesh.material)?mesh.material[intersection.face?.materialIndex??0]:mesh.material) as THREE.MeshStandardMaterial;
    if (!material?.visible || !material.colorWrite) return false;
    if (intersection.uv && (material.alphaTest>0 || material.transparent)) {
      const alpha=material.opacity*(material.map?textureChannel(material.map,intersection.uv,3):1)
        *(material.alphaMap?textureChannel(material.alphaMap,intersection.uv,1):1);
      if(alpha<Math.max(material.alphaTest,material.transparent ? .1 : 0))return false;
    }
    return true;
  });
}

/** Snap a user-selected low step to the measured pad edge. No door inference,
 * scene mutation, network save, or invented elevation is involved. */
export function pickBuildingEntrance(hit: NativeEntranceHit, zone: SiteZone, zones: SiteZone[],
  properties: SiteZone['properties'], visibleIds: string[], ground: SharedSiteGroundState):
  { result: EntrancePickResult } | { error: string } {
  if (ground.status !== 'ready' || ground.isCurrent?.() === false || ground.preview)
    return { error: 'Ground is still being checked. Wait for alignment, then choose the step again.' };
  if (zone.coordinates.length !== 4 || !hit.point.every(Number.isFinite))
    return { error: 'Choose a rectangular catalogue-house plot.' };
  const fresh = resolveBuildingGroundContact(hit.footprints, hit.lng, hit.lat, ground);
  if (fresh.status !== 'ready' || hit.contact.status !== 'ready'
    || Math.abs(fresh.anchorHeight - hit.contact.anchorHeight) > .001)
    return { error: 'The building is still aligning with the ground. Try again once it settles.' };
  const [east, north, height] = hit.point;
  if (height < -.05 || height > .6)
    return { error: 'Choose the lowest entrance step near the building base. Move the camera closer if needed.' };
  let nearest: GroundPoint | null = null, distance = Infinity;
  for (const ring of hit.footprints) for (let i = 0; i < ring.length; i++) {
    const a = ring[i], b = ring[(i + 1) % ring.length], dx = b[0] - a[0], dy = b[1] - a[1];
    const t = Math.max(0, Math.min(1, ((east-a[0])*dx + (north-a[1])*dy) / (dx*dx + dy*dy || 1)));
    const p: GroundPoint = [a[0]+t*dx, a[1]+t*dy], delta = Math.hypot(east-p[0], north-p[1]);
    if (delta < distance) { distance = delta; nearest = p; }
  }
  if (!nearest || distance > .6)
    return { error: 'Choose the outer edge of the lowest entrance step, where the approach should meet the building.' };
  const dimensions = rectangleDimensions(zone.coordinates), yaw = dimensions.degrees * Math.PI / 180;
  const lng = hit.lng + nearest[0]/metersPerDegLon(hit.lat), lat = hit.lat + nearest[1]/METERS_PER_DEG_LAT;
  const x = (lng-dimensions.center[0])*metersPerDegLon(dimensions.center[1]);
  const y = (lat-dimensions.center[1])*METERS_PER_DEG_LAT;
  const previous = readBuildingEntrance({ ...zone, properties });
  if (!previous) return { error: 'Choose a sidewalk target and a valid walkway width before picking the step.' };
  const anchor: BuildingEntrance = { ...previous, xM: Math.round((x*Math.cos(yaw)+y*Math.sin(yaw))*1000)/1000,
    yM: Math.round((-x*Math.sin(yaw)+y*Math.cos(yaw))*1000)/1000, heightAboveBaseM: 0,
    referenceWidthM: dimensions.width, referenceDepthM: dimensions.depth, scaleWithPlot: false };
  const draft = { ...zone, properties: { ...properties, pedestrian_building_entrance: anchor } };
  const next = zones.map(z => z.id === zone.id ? draft : z);
  const route = resolvePedestrianConnections(next, visibleIds).find(r => r.ownerId === zone.id);
  if (route?.status !== 'connected' || route.strips.length !== 1)
    return { result: { anchor, status: 'unresolved', message: route?.reason ?? 'Choose a visible street to connect this entrance.' } };
  const approach = buildBuildingEntranceApproach({ contact: fresh, footprints: hit.footprints,
    lng: hit.lng, lat: hit.lat, ground, strip: route.strips[0], heightAboveBaseM: 0 });
  return { result: { anchor, status: approach.status === 'ready' ? 'ready' : 'unresolved',
    message: approach.status === 'ready' ? 'The approach fits the current ground at this step. Save to keep this entrance.'
      : buildingGroundProblemMessage(approach.reason) } };
}
