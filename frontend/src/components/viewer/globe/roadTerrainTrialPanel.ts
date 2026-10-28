import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { rehearseRoadTerrain, type RoadRehearsalInput } from './roadTerrainRehearsal';
import { RoadTerrainTrialController } from './roadTerrainTrialController';

/** Local measured-ground pilot. No route or changed tile geometry is persisted. */
export function mountRoadTerrainTrialPanel(getScene:()=>THREE.Scene|null,
  getTiles:()=>unknown,
  onWalk:(lng:number,lat:number,height:number,heading:number)=>void,
  onSurfaceChanged:()=>void=()=>{}) {
  const name=new URLSearchParams(location.search).get('terrainTrial');
  if(!import.meta.env.DEV || !name || !['field','connection'].includes(name))return ()=>{};
  const panel=document.createElement('aside');panel.dataset.roadTerrainPanel='true';
  panel.style.cssText='position:absolute;right:20px;bottom:85px;z-index:45;width:300px;padding:18px;border:2px solid #252832;border-radius:18px;background:#fff9ed;box-shadow:0 6px 22px #18242226;color:#252832;font:13px/1.5 system-ui';
  const styles=document.createElement('style');styles.textContent='[data-road-terrain-panel] button:disabled{opacity:.4;cursor:not-allowed!important}';
  const title=document.createElement('strong');title.textContent='Natural road edges · local trial';
  const scope=document.createElement('p');scope.textContent='Temporary road preview. Catalogue street drawing still uses its existing ground requirements.';
  scope.style.cssText='margin:6px 0;color:#475569;font-size:12px';
  const widthLabel=document.createElement('label');widthLabel.textContent='Road width ';widthLabel.style.cssText='display:block;margin-top:12px';
  const width=document.createElement('select');width.setAttribute('aria-label','Trial road width');
  width.style.cssText='border:1px solid #252832;border-radius:6px;padding:5px;background:white';
  for(const [value,label] of [['6','6 m'],['5','5 m · compact']]){const option=document.createElement('option');option.value=value;option.textContent=label;width.append(option);}
  widthLabel.append(width);
  const lengthLabel=document.createElement('label');lengthLabel.textContent='Trial route ';lengthLabel.style.cssText='display:block;margin-top:8px';
  const extent=document.createElement('select');extent.setAttribute('aria-label','Trial route extent');extent.style.cssText=width.style.cssText;
  for(const [value,label] of [['0','Full length'],['4','End 4 m earlier']]){const option=document.createElement('option');option.value=value;option.textContent=label;extent.append(option);}
  lengthLabel.append(extent);
  const status=document.createElement('p');status.setAttribute('role','status');status.textContent='Build a measured road and compare it with the original ground.';
  const actions=document.createElement('div');actions.style.cssText='display:flex;gap:8px;flex-wrap:wrap';
  const button=(label:string)=>{const b=document.createElement('button');b.textContent=label;b.style.cssText='border:1px solid #252832;border-radius:9px;padding:8px 12px;background:#eeffbf;font-weight:650;cursor:pointer';actions.append(b);return b;};
  const build=button('Build transition'),toggle=button('Show original'),walk=button('Walk road');toggle.disabled=true;walk.disabled=true;
  panel.append(styles,title,scope,widthLabel,lengthLabel,status,actions);document.body.append(panel);
  let input:RoadRehearsalInput|undefined,wanted=false,pendingScene:THREE.Scene|null=null;
  const owner={};
  const pending=(value:boolean)=>{
    if(pendingScene?.userData.roadTerrainRebuilding===owner)delete pendingScene.userData.roadTerrainRebuilding;
    pendingScene=value?getScene():null;if(pendingScene)pendingScene.userData.roadTerrainRebuilding=owner;
  };
  const controller=new RoadTerrainTrialController(async signal=>{
    const selectedWidth=Number(width.value),shorten=Number(extent.value);
    const response=await fetch(`/__terrain_trial/${name}.json`,{signal});
    if(!response.ok)throw new Error('The local trial data is unavailable.');
    const source=await response.json() as RoadRehearsalInput;
    if(signal.aborted)throw new DOMException('Cancelled','AbortError');
    const length=source.length-shorten;
    input={...source,length,halfWidth:selectedWidth/2,profile:source.profile.filter(p=>p.x<=length),
      ground:source.ground.filter(p=>p.x<=length+source.endBlend)};
    const scene=getScene(),tiles=getTiles() as Parameters<typeof rehearseRoadTerrain>[1]|null;
    if(!scene||!tiles)throw new Error('Wait for the map to load, then try again.');
    if(!(tiles.group instanceof THREE.Object3D)||!(tiles.visibleTiles instanceof Set)||typeof tiles.forEachLoadedModel!=='function')
      throw new Error('This trial requires the Google mesh context.');
    return rehearseRoadTerrain(scene,tiles,input,signal);
  },(state,trial,error)=>{
    const measuring=state==='measuring'||state==='refreshing';pending(measuring);
    build.disabled=measuring;toggle.disabled=state==='error'||state==='idle';walk.disabled=state!=='ready';
    toggle.textContent=wanted?'Show original':'Show proposal';
    if(state==='measuring')status.textContent='Measuring the road and verge. Walking is paused until the checks pass.';
    if(state==='refreshing')status.textContent='Updating the transition for new map detail. Walking is paused briefly.';
    if(state==='original')status.textContent='Original ground shown. Show the proposal to resume the trial.';
    if(state==='ready'&&trial){
      const count=Number(trial.summary.leftEdge==='retaining')+Number(trial.summary.rightEdge==='retaining');
      status.textContent=`Transition ready · ${trial.field.length} m raised road, ${width.value} m wide · ${count?`${count} retaining ${count===1?'edge':'edges'}`:'natural slopes'}.`;
    }
    if(state==='error')status.textContent=error?.message.replace(/\s+[[{][\s\S]*$/,'').replace(/:$/,'')??'The trial could not be built.';
    if(!measuring)onSurfaceChanged();
  });
  build.onclick=()=>{wanted=true;controller.build();};
  width.onchange=()=>{wanted=true;controller.build();};
  extent.onchange=()=>{wanted=true;controller.build();};
  toggle.onclick=()=>{wanted=!wanted;controller.show(wanted);};
  walk.onclick=()=>{
    const trial=controller.trial;if(!trial||!input||!trial.status().active)return;
    const p=new THREE.Vector3(2,0,trial.field.roadHeight(2,0)).applyMatrix4(trial.frame),geo={lat:0,lon:0,height:0};
    WGS84_ELLIPSOID.getPositionToCartographic(p,geo);
    onWalk(geo.lon*180/Math.PI,geo.lat*180/Math.PI,geo.height,input.headingDegrees);
  };
  const timer=setInterval(()=>controller.checkFreshness(),250);
  return()=>{clearInterval(timer);controller.dispose();pending(false);panel.remove();};
}
