import { Component, Suspense, useMemo, useEffect, type ReactNode } from 'react';
import type { SiteZone } from '@/types';
import type { NativeStreetPose } from './nativeStreetPilot';
import { verifyStreetAssets, verifiedStreetScene } from './nativeStreetAssets';
import { disposeStreetInstances, instanceStreetModule } from './nativeStreetInstances';
import { nativeStreetRevision } from './nativeStreetReadiness';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';

class ModuleBoundary extends Component<{ children: ReactNode; zone: SiteZone }, { failed: boolean }> {
  state = { failed: false };
  retry=()=>this.setState({failed:false});
  componentDidMount(){window.addEventListener('cityprompt:retry-native-streets',this.retry);}
  componentWillUnmount(){window.removeEventListener('cityprompt:retry-native-streets',this.retry);}
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(){window.dispatchEvent(new CustomEvent('cityprompt:native-street-error',{detail:{
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
    {poses.filter(p=>p.wellWidthM && p.wellDepthM).map((pose,index)=><mesh key={`soil-${index}`} position={[pose.x,pose.y,pose.z+pose.surfaceLiftM-.015]} rotation={[0,0,pose.yaw]} receiveShadow renderOrder={149}>
      <planeGeometry args={[pose.wellWidthM!-.08,pose.wellDepthM!-.08]}/>
      <meshStandardMaterial color="#392e25" roughness={1} side={2}/>
    </mesh>)}
  </group>;
}

export function GlobeNativeStreetPilotModules({zone,poses,expectedCount}:{zone:SiteZone;poses:NativeStreetPose[];expectedCount:number}) {
  const revision=nativeStreetRevision(zone);
  return <group userData={{nativeStreetZone:zone.id,nativeStreetRevision:revision,nativeStreetExpectedCount:expectedCount}}>
    <ModuleBoundary key={revision} zone={zone}><Suspense fallback={<group userData={{nativeStreetStatus:'loading'}}/>}>
      <LoadedModules poses={poses}/>
    </Suspense></ModuleBoundary>
  </group>;
}
