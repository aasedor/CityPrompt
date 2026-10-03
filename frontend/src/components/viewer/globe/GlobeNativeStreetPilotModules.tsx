import { Component, Suspense, useMemo, useEffect, type ReactNode } from 'react';
import type { SiteZone } from '@/types';
import type { NativeStreetPose } from './nativeStreetPilot';
import { verifyStreetAssets, verifiedStreetScene } from './nativeStreetAssets';
import { disposeStreetInstances, instanceStreetModule } from './nativeStreetInstances';
import { nativeStreetRevision } from './nativeStreetReadiness';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';
import { RAIL_LIFT_X_M, RAIL_LIFT_Y_M, RAIL_PLATFORM_HEIGHT_M } from './elevatedRailProgram';

function RailStationLifts({poses}:{poses:NativeStreetPose[]}) {
  return <>{poses.filter(p=>p.kind==='rail_station').flatMap((pose,i)=>[-1,1].map(side=>{
    const x=side*RAIL_LIFT_X_M, y=RAIL_LIFT_Y_M;
    const metal='#394c52',glass='#78b5c2',paving='#bcb8a9';
    return <group key={`${i}:${side}`} position={[pose.x,pose.y,pose.z+pose.surfaceLiftM]} rotation={[0,0,pose.yaw]} userData={{stepFreeStationLift:true}}>
      {/* The bridge meets the protected platform through its existing glazing gap. */}
      <mesh position={[side*9.32,y,RAIL_PLATFORM_HEIGHT_M-.09]} receiveShadow castShadow>
        <boxGeometry args={[3.55,2.25,.18]}/><meshStandardMaterial color={paving} roughness={.87}/>
      </mesh>
      {[y-1.13,y+1.13].map((edge,j)=><mesh key={`bridge-rail-${j}`} position={[side*9.45,edge,RAIL_PLATFORM_HEIGHT_M+.55]} castShadow>
        <boxGeometry args={[2.45,.045,1.1]}/><meshStandardMaterial color={metal} metalness={.48} roughness={.34} transparent opacity={.7}/>
      </mesh>)}
      {[.025,RAIL_PLATFORM_HEIGHT_M].map((z,j)=><mesh key={`landing-${j}`} position={[x,y,z-.055]} receiveShadow>
        <boxGeometry args={[2.35,2.45,.11]}/><meshStandardMaterial color={paving} roughness={.9}/>
      </mesh>)}
      {[-1,1].flatMap(dx=>[-1,1].map(dy=><mesh key={`post-${dx}:${dy}`} position={[x+dx*1.17,y+dy*1.23,4.03]} castShadow>
        <boxGeometry args={[.08,.08,8.08]}/><meshStandardMaterial color={metal} metalness={.5} roughness={.35}/>
      </mesh>))}
      {[-1,1].map(dx=><mesh key={`glass-${dx}`} position={[x+dx*1.17,y,4.02]} castShadow>
        <boxGeometry args={[.028,2.32,7.7]}/><meshStandardMaterial color={glass} transparent opacity={.32} metalness={.1} roughness={.18} depthWrite={false}/>
      </mesh>)}
      <mesh position={[x,y,8.14]} castShadow><boxGeometry args={[2.55,2.55,.16]}/><meshStandardMaterial color={metal} metalness={.43} roughness={.38}/></mesh>
      {[.95,8.92].map((z,j)=><mesh key={`lift-sign-${j}`} position={[x,y-1.27,z]}>
        <boxGeometry args={[.72,.035,.36]}/><meshStandardMaterial color="#f2d065" emissive="#806321" emissiveIntensity={.35}/>
      </mesh>)}
    </group>;
  }))}</>;
}

class ModuleBoundary extends Component<{ children: ReactNode; zone: SiteZone; preview?: boolean }, { failed: boolean }> {
  state = { failed: false };
  retry=()=>this.setState({failed:false});
  componentDidMount(){window.addEventListener('cityprompt:retry-native-streets',this.retry);}
  componentWillUnmount(){window.removeEventListener('cityprompt:retry-native-streets',this.retry);}
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(){if (this.props.preview) return; window.dispatchEvent(new CustomEvent('cityprompt:native-street-error',{detail:{
    zoneId:this.props.zone.id,revision:nativeStreetRevision(this.props.zone),
    message:'A street component could not be loaded or verified. Choose Retry 3D update.',
  }}));}
  render() { return this.state.failed
    ? <group userData={{ nativeStreetStatus: 'error' }} /> : this.props.children; }
}

function ModuleBatch({poses}:{poses:NativeStreetPose[]}) {
  const scene=verifiedStreetScene(poses[0]);
  const instances=useMemo(()=>instanceStreetModule(scene,poses),[scene,poses]);
  useEffect(()=>retainResourceForDeferredDisposal(instances,disposeStreetInstances),[instances]);
  return <primitive object={instances} dispose={null}/>;
}

function LoadedModules({poses}:{poses:NativeStreetPose[]}) {
  const batches=useMemo(()=>{
    const groups=new Map<string,NativeStreetPose[]>();
    for(const pose of poses){const key=`${pose.sha256}:${pose.url}`; const items=groups.get(key)??[];items.push(pose);groups.set(key,items);}
    return [...groups.entries()];
  },[poses]);
  verifyStreetAssets(batches.map(([,items])=>items[0]));
  return <group userData={{nativeStreetStatus:'ready'}}>
    {batches.map(([key,items])=><ModuleBatch key={key} poses={items}/>)}
    <RailStationLifts poses={poses}/>
    {poses.filter(p=>p.wellWidthM && p.wellDepthM).map((pose,index)=><mesh key={`soil-${index}`} position={[pose.x,pose.y,pose.z+pose.surfaceLiftM-.015]} rotation={[0,0,pose.yaw]} receiveShadow renderOrder={149}>
      <planeGeometry args={[pose.wellWidthM!-.08,pose.wellDepthM!-.08]}/>
      <meshStandardMaterial color="#392e25" roughness={1} side={2}/>
    </mesh>)}
  </group>;
}

export function GlobeNativeStreetPilotModules({zone,poses,expectedCount,clearanceKey='[]',preview=false}:{zone:SiteZone;poses:NativeStreetPose[];expectedCount:number;clearanceKey?:string;preview?:boolean}) {
  const revision=nativeStreetRevision(zone);
  return <group userData={{nativeStreetZone:zone.id,nativeStreetRevision:revision,nativeStreetExpectedCount:expectedCount,nativeStreetClearanceKey:clearanceKey}}>
    <ModuleBoundary key={revision} zone={zone} preview={preview}><Suspense fallback={<group userData={{nativeStreetStatus:'loading'}}/>}>
      <LoadedModules poses={poses}/>
    </Suspense></ModuleBoundary>
  </group>;
}
