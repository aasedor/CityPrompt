import { useEffect, useMemo } from 'react';
import * as THREE from 'three';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { createPreparedEdgeGeometry } from './preparedSiteEdges';
import { cutGeometry, stripFootprint } from './terraceGeometry';
import { buildTerraceScene, type TerracePathResult } from './terraceScene';
import { resolvePreparedSiteTerrainForZone, createSitePreparationGeometry } from './sitePreparationSurface';
import { pedestrianCaptureUserData } from './pedestrianCapture';
import { direct3DProposalUserData, direct3DInstanceUserData, direct3DZoneInstanceDescriptor } from './direct3dCapture';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';
import { buildParkAccessBridgeGeometry } from './parkAccessBridgeGeometry';

export type TerraceScene = ReturnType<typeof buildTerraceScene>;
function OwnedMeshes({geometries,color}:{geometries:THREE.BufferGeometry[];color:string}) {
  useEffect(()=>{
    const releases=geometries.map(g=>retainResourceForDeferredDisposal(g,v=>v.dispose()));
    return ()=>releases.forEach(release=>release());
  },[geometries]);
  return <>{geometries.map((g,i)=><mesh key={i} geometry={g} renderOrder={123}><meshStandardMaterial color={color} roughness={.95} side={THREE.DoubleSide}/></mesh>)}</>;
}
function Terrace({zone,zones,scene}:{zone:SiteZone;zones:SiteZone[];scene:TerraceScene}) {
  const origin=zone.coordinates[0] as [number,number],east=metersPerDegLon(origin[1]);
  const level=resolvePreparedSiteTerrainForZone(zone,zones,scene.base!)!;
  const geometries=useMemo(()=>{
    const local=(p:number[]):[number,number]=>[(p[0]-origin[0])*east,(p[1]-origin[1])*METERS_PER_DEG_LAT];
    const plane=new THREE.ShapeGeometry(new THREE.Shape(zone.coordinates.map(p=>new THREE.Vector2(...local(p)))));
    const pad=createSitePreparationGeometry(plane,zone.id).translate(0,0,-.06);plane.dispose();
    const raw=createPreparedEdgeGeometry({samples:zone.coordinates.map(p=>[p[0],p[1],scene.base!])},level,origin);
    const openings=scene.paths.filter(p=>p.status==='connected'&&(p.ownerId===zone.id||p.targetId===zone.id)).map(p=>p.rampFootprint.map(local));
    const walls=cutGeometry(raw,openings);raw.dispose();
    return [pad,walls];
  },[zone,scene,level,east,origin]);
  return <group userData={{...direct3DProposalUserData('ground'),...direct3DInstanceUserData(direct3DZoneInstanceDescriptor(zone.id,'ground'))}}>
    <EastNorthUpFrame lat={origin[1]*Math.PI/180} lon={origin[0]*Math.PI/180} height={level}>
      <OwnedMeshes geometries={geometries} color="#958d7d"/>
    </EastNorthUpFrame>
  </group>;
}
function Path({path,base}:{path:TerracePathResult;base:number}) {
  const origin=path.points[0],east=metersPerDegLon(origin[1]);
  const geometries=useMemo(()=>{
    const result:THREE.BufferGeometry[]=[],local=(p:number[]):[number,number]=>[(p[0]-origin[0])*east,(p[1]-origin[1])*METERS_PER_DEG_LAT];
    for(let i=1;i<path.points.length;i++) {
      const a=path.points[i-1],b=path.points[i],start=local(a),end=local(b);
      const surface=buildParkAccessBridgeGeometry({start,end,widthM:path.widthM,startGroundM:a[2]-base,endGroundM:b[2]-base,streetLiftM:.087,endLiftM:.087});
      if(surface)result.push(surface);
      if(i===2) {
        const localSides=stripFootprint(start,end,path.widthM);
        const world=(p:[number,number],h:number):[number,number,number]=>[origin[0]+p[0]/east,origin[1]+p[1]/METERS_PER_DEG_LAT,h];
        result.push(createPreparedEdgeGeometry({samples:[world(localSides[0],a[2]),world(localSides[1],b[2])]},base,[origin[0],origin[1]],false));
        result.push(createPreparedEdgeGeometry({samples:[world(localSides[3],a[2]),world(localSides[2],b[2])]},base,[origin[0],origin[1]],false));
      }
    }
    return result;
  },[path,base,east,origin]);
  return <group userData={pedestrianCaptureUserData(path.ownerId)}><EastNorthUpFrame lat={origin[1]*Math.PI/180} lon={origin[0]*Math.PI/180} height={base}>
    <OwnedMeshes geometries={geometries} color="#c3bba9"/>
  </EastNorthUpFrame></group>;
}
export function GlobeTerraces({scene,zones}:{scene:TerraceScene;zones:SiteZone[]}) {
  if(scene.base===null)return null;
  return <group name="proposed-terraces">
    {scene.terraces.map(zone=><Terrace key={zone.id} zone={zone} zones={zones} scene={scene}/>)}
    {scene.paths.filter(p=>p.status==='connected').map(path=><Path key={path.ownerId} path={path} base={scene.base!}/>)}
  </group>;
}
