import { createContext, useContext, useEffect, useMemo, type ReactNode } from 'react';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { readBuildingEntrance, type ConnectionResult } from '@/features/pickPlace/pedestrianConnections';
import type { BuildingGroundContact, GroundPoint } from './buildingGroundContact';
import type { FootprintFrame } from './buildingPlacement';
import { buildBuildingEntranceApproach, ENTRANCE_REVIEW_RELIEF_M } from './buildingEntranceApproach';
import { useSharedSiteGround } from './SharedSiteGroundProvider';
import { streetConnectionCaptureUserData } from './pedestrianCapture';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';

type Inputs = { zones: SiteZone[]; results: ConnectionResult[] };
const Context = createContext<Inputs | null>(null);

export function BuildingEntranceApproaches({ zones, results, children }: Inputs & { children: ReactNode }) {
  const value=useMemo(()=>({ zones,results }),[zones,results]);
  return <Context.Provider value={value}>{children}</Context.Provider>;
}

/** Runs beside the owning model's contact solver, so the approach uses exactly
 * that model's native pads and displayed base, including retained safe ground.
 * No scene traversal, async registry, or new persistent geometry is involved. */
export function useBuildingEntranceApproach(contact: BuildingGroundContact, footprints: GroundPoint[][],
  frame: FootprintFrame, buildingId: string) {
  const inputs=useContext(Context), ground=useSharedSiteGround();
  const result=useMemo(()=>{
    if (!inputs || contact.status !== 'ready') return { reason:null, geometry:null, userData:undefined };
    const owner=inputs.zones.find(zone=>zone.building_id===buildingId || zone.building_ids?.includes(buildingId));
    if (!owner) return { reason:null, geometry:null, userData:undefined };
    const entrance=readBuildingEntrance(owner);
    if (!entrance) return { reason:owner.properties?.pedestrian_building_entrance || contact.reliefM>ENTRANCE_REVIEW_RELIEF_M
      ? 'entrance_connection_required':null, geometry:null, userData:undefined };
    const plan=inputs.results.find(item=>item.ownerId===owner.id && item.kind==='building');
    const userData=streetConnectionCaptureUserData(owner,inputs.zones);
    if (plan?.status!=='connected' || plan.strips.length!==1 || !userData)
      return { reason:'entrance_approach_obstructed',geometry:null,userData:undefined };
    const approach=buildBuildingEntranceApproach({contact,footprints,lng:frame.centroidLng,lat:frame.centroidLat,
      ground,strip:plan.strips[0],heightAboveBaseM:entrance.heightAboveBaseM??0});
    if (approach.status!=='ready') return {reason:approach.reason,geometry:null,userData:undefined};
    const geometry=new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.Float32BufferAttribute(approach.positions,3));
    geometry.setIndex(approach.indices);geometry.computeVertexNormals();geometry.computeBoundingSphere();
    return {reason:null,geometry,userData:{...userData,entranceApproachSections:approach.sections}};
  },[inputs,contact,footprints,frame.centroidLng,frame.centroidLat,buildingId,ground]);
  useEffect(()=>result.geometry?retainResourceForDeferredDisposal(result.geometry,geometry=>geometry.dispose()):undefined,[result.geometry]);
  return result;
}

export function BuildingEntranceApproachMesh({ approach }: { approach: ReturnType<typeof useBuildingEntranceApproach> }) {
  return approach.geometry ? <mesh name="building-entrance-approach" geometry={approach.geometry} userData={approach.userData} renderOrder={145}>
    <meshStandardMaterial color="#c3baa8" roughness={.94} flatShading side={THREE.DoubleSide} />
  </mesh> : null;
}
