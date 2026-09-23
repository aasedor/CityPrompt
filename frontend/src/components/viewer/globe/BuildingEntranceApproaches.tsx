import { createContext, useContext, useEffect, useMemo, type ReactNode } from 'react';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { readBuildingEntrance, type ConnectionResult } from '@/features/pickPlace/pedestrianConnections';
import type { BuildingGroundContact, GroundPoint } from './buildingGroundContact';
import type { FootprintFrame } from './buildingPlacement';
import { buildBuildingEntranceApproach, ENTRANCE_REVIEW_RELIEF_M } from './buildingEntranceApproach';
import { useSharedSiteGround, type SharedSiteGroundState } from './SharedSiteGroundProvider';
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
  frame: FootprintFrame, buildingId: string, preparedGround?: SharedSiteGroundState | null) {
  const inputs=useContext(Context), sharedGround=useSharedSiteGround();
  const ground=sharedGround.status === 'inactive' && preparedGround ? preparedGround : sharedGround;
  const result=useMemo(()=>{
    if (!inputs || contact.status !== 'ready') return { reason:null, geometry:null,railGeometry:null,supportGeometry:null, userData:undefined };
    const owner=inputs.zones.find(zone=>zone.building_id===buildingId || zone.building_ids?.includes(buildingId));
    if (!owner) return { reason:null, geometry:null,railGeometry:null,supportGeometry:null, userData:undefined };
    const entrance=readBuildingEntrance(owner, inputs.zones);
    if (!entrance) return { reason:(readBuildingEntrance(owner)?.automatic !== true && owner.properties?.pedestrian_building_entrance) || contact.reliefM>ENTRANCE_REVIEW_RELIEF_M
      ? 'entrance_connection_required':null, geometry:null,railGeometry:null,supportGeometry:null, userData:undefined };
    const plan=inputs.results.find(item=>item.ownerId===owner.id && item.kind==='building');
    const userData=streetConnectionCaptureUserData(owner,inputs.zones);
    if (plan?.status!=='connected' || plan.strips.length!==1 || !userData)
      return { reason:'entrance_approach_obstructed',geometry:null,railGeometry:null,supportGeometry:null,userData:undefined };
    const approach=buildBuildingEntranceApproach({contact,footprints,lng:frame.centroidLng,lat:frame.centroidLat,
      ground,strip:plan.strips[0],heightAboveBaseM:entrance.heightAboveBaseM??0});
    if (approach.status!=='ready') return {reason:approach.reason,geometry:null,railGeometry:null,supportGeometry:null,userData:undefined};
    const toGeometry=(data:{positions:number[];indices:number[]})=>{
      if(!data.positions.length)return null;
      const geometry=new THREE.BufferGeometry();
      geometry.setAttribute('position',new THREE.Float32BufferAttribute(data.positions,3));
      geometry.setIndex(data.indices);geometry.computeVertexNormals();geometry.computeBoundingSphere();
      return geometry;
    };
    const {rails,supports,...detailSummary}=approach.details;
    return {reason:null,geometry:toGeometry(approach),railGeometry:toGeometry(rails),supportGeometry:toGeometry(supports),
      userData:{...userData,entranceApproachSections:approach.sections,entranceApproachDetails:detailSummary,
        entranceApproachStepCount:approach.sections.some(section=>section.kind==='flight')?approach.steps:0}};
  },[inputs,contact,footprints,frame.centroidLng,frame.centroidLat,buildingId,ground]);
  useEffect(()=>{
    const releases=[result.geometry,result.railGeometry,result.supportGeometry].filter(geometry=>geometry!==null)
      .map(geometry=>retainResourceForDeferredDisposal(geometry,geometry=>geometry.dispose()));
    return ()=>releases.forEach(release=>release());
  },[result.geometry,result.railGeometry,result.supportGeometry]);
  return result;
}

export function BuildingEntranceApproachMesh({ approach }: { approach: ReturnType<typeof useBuildingEntranceApproach> }) {
  return approach.geometry ? <group>
    <mesh name="building-entrance-approach" geometry={approach.geometry} userData={approach.userData} renderOrder={145}>
      <meshStandardMaterial color="#c3baa8" roughness={.94} flatShading side={THREE.DoubleSide} />
    </mesh>
    {approach.supportGeometry&&<mesh name="building-entrance-supports" geometry={approach.supportGeometry} userData={approach.userData} renderOrder={145}>
      <meshStandardMaterial color="#a69f91" roughness={.94} flatShading side={THREE.DoubleSide} />
    </mesh>}
    {approach.railGeometry&&<mesh name="building-entrance-rails" geometry={approach.railGeometry} userData={approach.userData} renderOrder={145}>
      <meshStandardMaterial color="#545b58" roughness={.72} flatShading side={THREE.DoubleSide} />
    </mesh>}
  </group> : null;
}
