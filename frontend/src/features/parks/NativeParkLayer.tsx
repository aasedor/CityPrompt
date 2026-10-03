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
import { STEP_FREE_PARK_LIFTS, type ParkLiftPlan } from './stepFreeParkAccess';

function StepFreeParkStructure({plan}:{plan:ParkLiftPlan}) {
  const span=Math.abs(plan.bridgeEndY-plan.bridgeStartY);
  const middle=(plan.bridgeEndY+plan.bridgeStartY)/2;
  const width=plan.widthM??2.48,half=width/2;
  const cabinDepth=plan.cabinDepthM??2.6,cabinHalfDepth=cabinDepth/2;
  const height=plan.upperZ-plan.lowerZ;
  const metal='#425255';
  return <group userData={{stepFreeParkAccess:true}}>
    <mesh position={[plan.x,middle,plan.bridgeZ-.105]} castShadow receiveShadow>
      <boxGeometry args={[width,span+.12,.21]}/><meshStandardMaterial color={plan.color} roughness={.88}/>
    </mesh>
    {[-1,1].map(side=><group key={side}>
      <mesh position={[plan.x+side*(half+.04),middle-(plan.connectX!==undefined&&side>0?1.2:0),plan.bridgeZ+.56]} castShadow>
        <boxGeometry args={[.045,span-(plan.connectX!==undefined&&side>0?2.4:0),1.12]}/><meshStandardMaterial color={metal} metalness={.43} roughness={.35} transparent opacity={.65}/>
      </mesh>
      <mesh position={[plan.x+side*(half+.04),middle-(plan.connectX!==undefined&&side>0?1.2:0),plan.bridgeZ+1.12]} castShadow>
        <boxGeometry args={[.085,span-(plan.connectX!==undefined&&side>0?2.4:0),.085]}/><meshStandardMaterial color={metal} metalness={.48} roughness={.34}/>
      </mesh>
    </group>)}
    {plan.connectX!==undefined&&<group>
      <mesh position={[(plan.x+plan.connectX)/2,plan.bridgeEndY,plan.bridgeZ-.105]} castShadow receiveShadow>
        <boxGeometry args={[Math.abs(plan.connectX-plan.x)+.12,width,.21]}/><meshStandardMaterial color={plan.color} roughness={.88}/>
      </mesh>
      <mesh position={[(plan.x+plan.connectX)/2,plan.bridgeEndY-half-.04,plan.bridgeZ+.56]} castShadow>
        <boxGeometry args={[Math.abs(plan.connectX-plan.x),.045,1.12]}/><meshStandardMaterial color={metal} metalness={.43} roughness={.35} transparent opacity={.65}/>
      </mesh>
      <mesh position={[(plan.x+plan.connectX-2.3)/2,plan.bridgeEndY+half+.04,plan.bridgeZ+.56]} castShadow>
        <boxGeometry args={[Math.abs(plan.connectX-2.3-plan.x),.045,1.12]}/><meshStandardMaterial color={metal} metalness={.43} roughness={.35} transparent opacity={.65}/>
      </mesh>
    </group>}
    {Array.from({length:Math.max(1,Math.floor(span/7))},(_,i)=>{
      const y=Math.min(plan.bridgeStartY,plan.bridgeEndY)+(i+1)*span/(Math.floor(span/7)+1);
      const base=plan.lowerZ<0?plan.lowerZ:0;
      return <group key={`support-${i}`}>
        {[-1,1].map(side=><mesh key={side} position={[plan.x+side*(half-.23),y,(plan.bridgeZ+base)/2-.08]} castShadow>
          <boxGeometry args={[.16,.16,Math.max(.16,plan.bridgeZ-base-.16)]}/>
          <meshStandardMaterial color={metal} metalness={.35} roughness={.45}/>
        </mesh>)}
      </group>;
    })}
    {[plan.lowerZ,plan.upperZ].map((z,i)=><mesh key={`landing-${i}`} position={[plan.x,plan.y,z-.055]} receiveShadow>
      <boxGeometry args={[2.5,cabinDepth,.11]}/><meshStandardMaterial color={plan.color} roughness={.88}/>
    </mesh>)}
    {[-1,1].flatMap(dx=>[-1,1].map(dy=><mesh key={`tower-${dx}:${dy}`} position={[plan.x+dx*1.25,plan.y+dy*cabinHalfDepth,plan.lowerZ+height/2+.12]} castShadow>
      <boxGeometry args={[.09,.09,height+.24]}/><meshStandardMaterial color={metal} metalness={.45} roughness={.34}/>
    </mesh>))}
    {[-1,1].map(side=><mesh key={`glass-${side}`} position={[plan.x+side*1.25,plan.y,plan.lowerZ+height/2+.12]} castShadow>
      <boxGeometry args={[.03,cabinDepth-.1,height]}/><meshStandardMaterial color="#84b5b7" transparent opacity={.32} roughness={.2} depthWrite={false}/>
    </mesh>)}
    <mesh position={[plan.x,plan.y,plan.upperZ+.27]} castShadow>
      <boxGeometry args={[2.67,cabinDepth+.16,.2]}/><meshStandardMaterial color={metal} metalness={.43} roughness={.38}/>
    </mesh>
    {[plan.lowerZ+.9,plan.upperZ+1.02].map((z,i)=><mesh key={`sign-${i}`} position={[plan.x,plan.y-cabinHalfDepth-.04,z]}>
      <boxGeometry args={[.68,.04,.28]}/><meshStandardMaterial color="#f6d77e" emissive="#68501d" emissiveIntensity={.4}/>
    </mesh>)}
  </group>;
}

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
  return <group userData={{nativeParkStatus:'ready'}}><NativeParkModel layout={layout}/>
    {STEP_FREE_PARK_LIFTS[layout.variantId] && <StepFreeParkStructure plan={STEP_FREE_PARK_LIFTS[layout.variantId]}/>}
    <NativeParkConnections zone={zone}/></group>;
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
  },[access,resolved.selection,resolved.layout]);
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
