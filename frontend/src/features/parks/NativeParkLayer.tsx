import { Component, Suspense, useMemo, useEffect, type ReactNode } from 'react';
import * as THREE from 'three';
import { verifiedScene, verifyParkAssets, type Asset } from './nativeParkAssets';
import { getDerivedParkAccess } from '@/components/viewer/globe/parkAccessConnections';
import { buildParkAccessBridgeGeometry } from '@/components/viewer/globe/parkAccessBridgeGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { retainResourceForDeferredDisposal } from '@/components/viewer/globe/strictModeResourceDisposal';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import type { SiteZone } from '@/types';
import { hasNativePark, nativeParkFitProblem, readNativePark, type NativeParkLayout } from './nativeParkRegistry';
import { resolvePreparedSiteTerrainForZone } from '@/components/viewer/globe/sitePreparationSurface';
import { useOwnParkAssemblyGround } from '@/components/viewer/globe/ParkAssemblyGround';
import { direct3DInstanceUserData, direct3DProposalUserData, direct3DZoneInstanceDescriptor } from '@/components/viewer/globe/direct3dCapture';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { nativePavingProbe, trimAccessAtNativePaving } from './nativeParkAccess';
import { cloneNativeParkScene } from './nativeParkSurfaceDepth';

function Module({asset}:{asset:Asset}) {
  const scene=verifiedScene(asset);
  const clone=useMemo(()=>cloneNativeParkScene(scene),[scene]);
  return <primitive object={clone} dispose={null}/>;
}
/** Whole native modules retain authored transforms, including source vegetation scale. */
export function NativeParkModel({layout}:{layout:NativeParkLayout}) {
  // Resolve all dependencies before mounting any part or claiming readiness.
  verifyParkAssets(Object.values(layout.assets));
  if (layout.mode==='native_assembly') return <group rotation={[Math.PI/2,0,0]}><Module asset={layout.assets.assembly!}/></group>;
  const w=layout.widthM,d=layout.depthM,regions=layout.surfaceRegions;
  const xs=[...new Set([-w/2,w/2,...regions.flatMap(r=>[r.x-r.width/2,r.x+r.width/2])])].sort((a,b)=>a-b);
  const ys=[...new Set([-d/2,d/2,...regions.flatMap(r=>[r.y-r.depth/2,r.y+r.depth/2])])].sort((a,b)=>a-b);
  const cells:ReactNode[]=[];
  for(let i=0;i<xs.length-1;i++) for(let j=0;j<ys.length-1;j++) {
    const x=(xs[i]+xs[i+1])/2,y=(ys[j]+ys[j+1])/2;
    let material:string|null='grass';
    for(const r of regions) if(Math.abs(x-r.x)<r.width/2 && Math.abs(y-r.y)<r.depth/2) material=r.material;
    if(material) cells.push(<mesh key={`${i}:${j}`} position={[x,y,-.04]} receiveShadow><boxGeometry args={[xs[i+1]-xs[i],ys[j+1]-ys[j],.08]}/><meshStandardMaterial color={new THREE.Color(...layout.surfacePalette[material==='grass'?'grass':'paving'] as [number,number,number])} roughness={.86}/></mesh>);
  }
  return <>{cells}{layout.placements.map((p,i)=><group key={i} position={[p.x,p.y,p.z]} rotation={[0,0,p.yaw]} scale={p.scale}>
    <group rotation={[Math.PI/2,0,0]}><Module asset={layout.assets[p.asset as keyof typeof layout.assets]!}/></group>
  </group>)}</>;
}
class ParkBoundary extends Component<{children:ReactNode;zoneId:string;revision:string},{failed:boolean;message:string}> {
  state={failed:false,message:''};
  retry=()=>this.setState({failed:false,message:''});
  componentDidMount(){window.addEventListener('cityprompt:retry-native-parks',this.retry);}
  componentWillUnmount(){window.removeEventListener('cityprompt:retry-native-parks',this.retry);}
  static getDerivedStateFromError(){return {failed:true,message:'The park model could not be loaded or verified. Choose Retry 3D update to load it again.'};}
  componentDidCatch(){window.dispatchEvent(new CustomEvent('cityprompt:native-park-error',{detail:{zoneId:this.props.zoneId,revision:this.props.revision,message:this.state.message}}));}
  render(){return this.state.failed?<group userData={{nativeParkStatus:'error',nativeParkError:this.state.message}}/>:this.props.children;}
}
function LoadedPark({zone,layout}:{zone:SiteZone;layout:NativeParkLayout}) {
  verifyParkAssets(Object.values(layout.assets));
  useOwnParkAssemblyGround(zone);
  return <group userData={{nativeParkStatus:'ready'}}><NativeParkModel layout={layout}/><NativeParkConnections zone={zone}/></group>;
}
function NativeParkConnections({zone}:{zone:SiteZone}) {
  const access=getDerivedParkAccess(zone),resolved=readNativePark(zone)!;
  const geometry=useMemo(()=>{
    const f=resolved.selection.frame,c=Math.cos(f.yaw),s=Math.sin(f.yaw);
    const local=([lng,lat]:number[]):[number,number]=>{const x=(lng-f.longitude)*metersPerDegLon(f.latitude),y=(lat-f.latitude)*METERS_PER_DEG_LAT;return [x*c+y*s,-x*s+y*c];};
    const probe=nativePavingProbe(resolved.layout);
    return (access?.connections??[]).flatMap(connection=>{
      const trimmed=trimAccessAtNativePaving(connection.path.map(local),connection.widthM,probe);
      return trimmed.path.slice(1).flatMap((end,i)=>{
        const piece=buildParkAccessBridgeGeometry({start:trimmed.path[i],end,widthM:connection.widthM,streetLiftM:i===0?connection.streetLiftM:.025,endLiftM:i===trimmed.path.length-2?trimmed.endHeight:.025});
        return piece?[piece]:[];
      });
    });
  },[access,resolved.selection]);
  useEffect(()=>retainResourceForDeferredDisposal(geometry,items=>items.forEach(item=>item.dispose())),[geometry]);
  return <>{geometry.map((g,i)=><mesh key={i} geometry={g} receiveShadow><meshStandardMaterial color="#b4a58c" roughness={.95} side={THREE.DoubleSide}/></mesh>)}</>;
}
export function NativeParkLayer({zones,terrainHeight}:{zones:SiteZone[];terrainHeight:number}) {
  const boundary=getActiveSiteBoundary(zones);
  return <>{zones.filter(hasNativePark).map(zone=>{
    const resolved=readNativePark(zone), frame=resolved?.selection.frame;
    const height=resolvePreparedSiteTerrainForZone(zone,zones,terrainHeight);
    const supported=resolved && !nativeParkFitProblem(zone) && boundary?.properties?.terrain_strategy!=='landscape'
      && boundary?.properties?.community_3d_mask_existing_tiles===true && height!==null && Number.isFinite(height);
    return <group key={`${zone.id}:${zone.updated_at}`} userData={{...direct3DProposalUserData('park'),...direct3DInstanceUserData(direct3DZoneInstanceDescriptor(zone.id,'park')),
      nativeParkZone:zone.id,nativeParkRevision:JSON.stringify(zone.properties?.green_space_native_layout)}}>
      <ParkBoundary zoneId={zone.id} revision={JSON.stringify(zone.properties?.green_space_native_layout ?? null)}><Suspense fallback={<group userData={{nativeParkStatus:'loading'}}/>}>
        {supported && frame?<EastNorthUpFrame lat={frame.latitude*Math.PI/180} lon={frame.longitude*Math.PI/180} height={height}>
          <group rotation={[0,0,frame.yaw]}><LoadedPark zone={zone} layout={resolved.layout}/></group>
        </EastNorthUpFrame>:<group userData={{nativeParkStatus:'unsupported',nativeParkError:'Keep the complete park on a prepared level site. Review ground or enlarge the park parcel.'}}/>}
      </Suspense></ParkBoundary>
    </group>;
  })}</>;
}
export function assertNativeParksReady(scene:THREE.Object3D|null,zones:SiteZone[]) {
  for(const zone of zones.filter(hasNativePark)) {
    let ready=false,failure='';
    scene?.traverse(object=>{
      if(object.userData.nativeParkZone!==zone.id || object.userData.nativeParkRevision!==JSON.stringify(zone.properties?.green_space_native_layout)) return;
      object.traverse(child=>{
        if(child.userData.nativeParkStatus==='ready')ready=true;
        if(child.userData.nativeParkError)failure=child.userData.nativeParkError;
      });
    });
    if(!ready) throw new Error(failure||'Your park is still updating. Wait for its current model to load, then retry.');
  }
}

/** Asset loading is automatic. Wait without charging a provider for an incomplete scene. */
export async function waitForNativeParksReady(scene:THREE.Object3D|null,zones:SiteZone[],timeoutMs=15000) {
  const deadline=Date.now()+timeoutMs;
  for (;;) {
    try {assertNativeParksReady(scene,zones);return;} catch(error) {
      let failed=false;
      scene?.traverse(o=>{if(['error','unsupported'].includes(o.userData.nativeParkStatus))failed=true;});
      if(failed || Date.now()>=deadline) throw error;
      await new Promise(resolve=>setTimeout(resolve,100));
    }
  }
}
