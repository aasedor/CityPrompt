import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { rehearseRoadTerrain, type RoadRehearsalInput } from './roadTerrainRehearsal';

/** Disposable development UI for a finite, locally supplied DEM rehearsal.
 * It cannot fetch arbitrary files, save a route, or enable itself in production. */
export function mountRoadTerrainTrialPanel(getScene:()=>THREE.Scene|null,
  getTiles:()=>unknown,
  onWalk:(lng:number,lat:number,height:number,heading:number)=>void) {
  const name=new URLSearchParams(location.search).get('terrainTrial');
  if(!import.meta.env.DEV || !name || !['field','connection'].includes(name))return ()=>{};
  const panel=document.createElement('aside');panel.dataset.roadTerrainPanel='true';
  panel.style.cssText='position:absolute;right:20px;bottom:85px;z-index:45;width:300px;padding:18px;border:2px solid #252832;border-radius:18px;background:#fff9ed;box-shadow:0 6px 22px #18242226;color:#252832;font:13px/1.5 system-ui';
  const title=document.createElement('strong');title.textContent='Natural road edges · local trial';
  const status=document.createElement('p');status.textContent='Build a measured road and compare it with the original ground.';
  const actions=document.createElement('div');actions.style.cssText='display:flex;gap:8px;flex-wrap:wrap';
  const button=(label:string)=>{const b=document.createElement('button');b.textContent=label;b.style.cssText='border:1px solid #252832;border-radius:9px;padding:8px 12px;background:#eeffbf;font-weight:650;cursor:pointer';actions.append(b);return b;};
  const build=button('Build transition'),toggle=button('Show original'),walk=button('Walk road');toggle.disabled=true;walk.disabled=true;
  panel.append(title,status,actions);document.body.append(panel);
  let rehearsal:Awaited<ReturnType<typeof rehearseRoadTerrain>>|undefined,input:RoadRehearsalInput|undefined;
  let disposed=false,generation=0;
  const report=(s:string)=>{status.textContent=s;};
  build.onclick=async()=>{
    const current=++generation;build.disabled=true;toggle.disabled=true;walk.disabled=true;rehearsal?.dispose();rehearsal=undefined;
    report('Measuring the complete road and verge. Google tiles stay visible until the checks pass.');
    try{
      const response=await fetch(`/__terrain_trial/${name}.json`);if(!response.ok)throw new Error('The local trial data is unavailable.');
      input=await response.json() as RoadRehearsalInput;
      const scene=getScene(),tiles=getTiles() as Parameters<typeof rehearseRoadTerrain>[1]|null;
      if(!scene||!tiles)throw new Error('Wait for the map to load, then try again.');
      if(!(tiles.group instanceof THREE.Object3D)||!(tiles.visibleTiles instanceof Set)||typeof tiles.forEachLoadedModel!=='function')
        throw new Error('This trial requires the Google mesh context.');
      const result=await rehearseRoadTerrain(scene,tiles,input);
      if(disposed||generation!==current){result.dispose();return;}
      rehearsal=result;toggle.disabled=false;walk.disabled=false;toggle.textContent='Show original';
      report(`Transition ready · ${result.summary.probes.toLocaleString()} ground checks. Original imagery is preserved around the road.`);
    }catch(e){if(!disposed)report(e instanceof Error
      ? e.message.replace(/\s+[\[{][\s\S]*$/,'').replace(/:$/,'') : 'The trial could not be built.');}
    finally{if(!disposed)build.disabled=false;}
  };
  toggle.onclick=()=>{if(!rehearsal)return;const show=!rehearsal.status().active;rehearsal.setVisible(show);toggle.textContent=show?'Show original':'Show proposal';walk.disabled=!show;};
  walk.onclick=()=>{if(!rehearsal||!input)return;
    const x=2,p=new THREE.Vector3(x,0,rehearsal.field.roadHeight(x,0)).applyMatrix4(rehearsal.frame);
    const geo={lat:0,lon:0,height:0};WGS84_ELLIPSOID.getPositionToCartographic(p,geo);
    onWalk(geo.lon*180/Math.PI,geo.lat*180/Math.PI,geo.height,input.headingDegrees);
  };
  const timer=setInterval(()=>{if(rehearsal?.status().stale){rehearsal.dispose();rehearsal=undefined;toggle.disabled=true;walk.disabled=true;
    report('Google loaded new detail here. Rebuild the transition to check the refined ground.');}},500);
  return()=>{disposed=true;generation++;clearInterval(timer);rehearsal?.dispose();panel.remove();};
}
