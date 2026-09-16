import { Component, Suspense, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { useGLTF } from '@react-three/drei';
import { useQuery } from '@tanstack/react-query';
import { EastNorthUpFrame, TilesRendererContext } from '3d-tiles-renderer/r3f';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { legoAssemblyApi } from '@/features/legoAssembly/legoAssemblyApi';
import { centreNativeClayClone } from '@/features/legoAssembly/nativeClayPlacement';
import { createKtx2LoaderExtension } from '@/lib/ktx2GltfLoader';
import { resolveApiFileUrl } from '@/services/api';
import { GlobeNeighborhoodParkPilot } from '@/components/viewer/globe/GlobeNeighborhoodParkPilot';
import { GlobeParkTrioPilot } from '@/components/viewer/globe/GlobeParkTrioPilot';
import { isParkTrio } from '@/components/viewer/globe/parkTrioLayout';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { useSharedSiteGround } from '@/components/viewer/globe/SharedSiteGroundProvider';
import { resolvePreparedSiteTerrainForZone } from '@/components/viewer/globe/sitePreparationSurface';
import { placeAsset, placementPlanRequest, placementProperties, type PlaceAssetId } from './catalogue';
import { placementProblem, rectangleAt } from './geometry';
import { streetFacingDegrees } from './streetFacing';

export interface PlacementDraft {
  assetId: PlaceAssetId; width: number; depth: number; degrees: number;
  faceStreet?: boolean;
  inputError?: string;
  inputValues?: { width: string; depth: string; degrees: string };
}
class PreviewFallback extends Component<{children: ReactNode; fallback: ReactNode}, {failed: boolean}> {
  state = {failed:false};
  static getDerivedStateFromError() { return {failed:true}; }
  render() { return this.state.failed ? this.props.fallback : this.props.children; }
}
function Home({url}: {url: string}) {
  const gl=useThree(state=>state.gl);
  const extension=useMemo(()=>createKtx2LoaderExtension(gl),[gl]);
  const {scene}=useGLTF(resolveApiFileUrl(url),true,true,extension);
  const clone=useMemo(()=>centreNativeClayClone(scene.clone(true)),[scene]);
  return <group rotation={[Math.PI/2,0,0]} dispose={null}><primitive object={clone}/></group>;
}
const ORIGIN = {lng:-114.04677,lat:51.04542};
const flatGround=()=>0;

/** Local preview state avoids rerendering the full globe on every pointer move. */
export function GlobePlacementPreview({ draft, zones, onStatusChange }: {draft: PlacementDraft; zones: SiteZone[]; onStatusChange?: (problem: string | null) => void}) {
  const {gl,camera,invalidate}=useThree();
  const tiles=useContext(TilesRendererContext);
  const ground = useSharedSiteGround();
  const pointer=useRef(new THREE.Vector2(0,0));
  const dirty=useRef(true), last=useRef(0);
  const lastCamera=useRef(new THREE.Matrix4());
  const [surface,setSurface]=useState<{lng:number;lat:number;height:number}|null>(null);
  const asset=placeAsset(draft.assetId);
  const projectId=zones[0]?.project_id;
  const request=placementPlanRequest(asset,draft.width,draft.depth,projectId);
  const {data:plan}=useQuery({queryKey:['placement-home-plan',request],
    queryFn:()=>legoAssemblyApi.plan(request!),
    retry:false,staleTime:300000,enabled:request!==null});
  useEffect(()=>{
    const update=(e:PointerEvent)=>{const rect=gl.domElement.getBoundingClientRect();
      if(rect.width<640) pointer.current.set(0,0);
      else pointer.current.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);
      dirty.current=true;invalidate();};
    gl.domElement.addEventListener('pointermove',update);
    return ()=>gl.domElement.removeEventListener('pointermove',update);
  },[gl,invalidate]);
  useFrame(({clock})=>{
    if ((!dirty.current && lastCamera.current.equals(camera.matrixWorld)) || clock.elapsedTime-last.current<.1 || !tiles?.group) return;
    lastCamera.current.copy(camera.matrixWorld);
    last.current=clock.elapsedTime;dirty.current=false;
    const ray=new THREE.Raycaster();ray.setFromCamera(pointer.current,camera);
    const hit=ray.intersectObjects(tiles.group.children,true)[0]?.point;
    if(!hit) {setSurface(null);return;}
    const geo=WGS84_ELLIPSOID.getPositionToCartographic(hit,{} as never);
    setSurface({lng:geo.lon*180/Math.PI,lat:geo.lat*180/Math.PI,height:WGS84_ELLIPSOID.getPositionElevation(hit)});
  });
  // Composition is fixed in local metres; cursor movement only translates its frame.
  const previewZone=useMemo(()=>({id:'placement-preview',zone_type:asset.zoneType,
    coordinates:rectangleAt([ORIGIN.lng,ORIGIN.lat],draft.width,draft.depth),
    properties:placementProperties(asset)} as SiteZone),[asset,draft.width,draft.depth]);
  const degrees = surface && draft.faceStreet ? streetFacingDegrees([surface.lng,surface.lat], zones, draft.degrees) : draft.degrees;
  const footprint = surface ? rectangleAt([surface.lng,surface.lat],draft.width,draft.depth,degrees) : null;
  const invalid = footprint ? placementProblem(footprint,zones,getActiveSiteBoundary(zones)) : 'Move over the site and wait for the ground to load.';
  // Report only status transitions, not every pointer coordinate, to the planner.
  useEffect(() => { onStatusChange?.(invalid); }, [invalid, onStatusChange]);
  useEffect(() => () => onStatusChange?.(null), [onStatusChange]);
  if(!surface || !footprint) return null;
  const previewHeight = resolvePreparedSiteTerrainForZone({ ...previewZone, coordinates: footprint }, zones, surface.height)
    ?? ground.heightAt(surface.lng, surface.lat) ?? surface.height;
  const envelope=asset.nativeDimensions ?? [draft.width,draft.depth,Number(asset.properties.height) || .1];
  const fallback=<mesh position={[0,0,envelope[2]/2]}><boxGeometry args={[envelope[0],envelope[1],envelope[2]]}/><meshBasicMaterial color="#64748b" wireframe/></mesh>;
  return <EastNorthUpFrame lat={surface.lat*Math.PI/180} lon={surface.lng*Math.PI/180} height={previewHeight+.12}>
    <group rotation={[0,0,degrees*Math.PI/180]} name="placement-preview" raycast={()=>null}>
      <mesh position={[0,0,.1]}><planeGeometry args={[draft.width,draft.depth]}/><meshBasicMaterial color={invalid?'#ef4444':'#c9ff3d'} transparent opacity={.3} side={THREE.DoubleSide} depthWrite={false}/></mesh>
      <PreviewFallback key={asset.id} fallback={fallback}><Suspense fallback={fallback}>
        {asset.zoneType==='building' ? plan ? plan.instances.map((instance,index)=><group key={`${instance.asset_id}-${index}`}
          position={[instance.position[0],-instance.position[1],instance.position[2]]} rotation={[0,0,-instance.rotation_degrees*Math.PI/180]}>
          <Home url={instance.model_url}/></group>) : fallback
          : isParkTrio(previewZone)
            ? <GlobeParkTrioPilot zone={previewZone} centroid={ORIGIN} terrainZ={flatGround}/>
            : asset.id === 'neighbourhood_park'
              ? <GlobeNeighborhoodParkPilot zone={previewZone} centroid={ORIGIN} terrainZ={flatGround}/>
              : fallback}
      </Suspense></PreviewFallback>
    </group>
  </EastNorthUpFrame>;
}
