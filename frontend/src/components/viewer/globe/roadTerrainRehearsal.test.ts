import {it,expect,vi} from 'vitest';
import * as THREE from 'three';
import {WGS84_ELLIPSOID} from '3d-tiles-renderer';
import {rehearseRoadTerrain,type RoadRehearsalInput} from './roadTerrainRehearsal';
import {assertStreetGroundReady} from './streetGroundCapture';

it.each(['load-model','dispose-model','tile-visibility-change'])('restores original resources when relevant tiles change: %s',async(eventName)=>{
  vi.useFakeTimers();
  const scene=new THREE.Scene(),group=new THREE.Group(),root=new THREE.Group();scene.add(group);group.add(root);
  const frame=new THREE.Matrix4();WGS84_ELLIPSOID.getEastNorthUpFrame(51*Math.PI/180,-114*Math.PI/180,1100,frame);
  root.matrixAutoUpdate=false;root.matrix.copy(frame);
  const original=new THREE.PlaneGeometry(52,36,1,1);original.translate(18,0,-1.3);
  const material=new THREE.MeshBasicMaterial(),compile=material.onBeforeCompile,mesh=new THREE.Mesh(original,material);root.add(mesh);scene.updateMatrixWorld(true);
  type Listener=(e:{scene?:THREE.Object3D})=>void;
  const events=new Map<string,Set<Listener>>();
  const tiles={group,visibleTiles:new Set<unknown>(['tile']),forEachLoadedModel:(fn:(s:THREE.Object3D,t:unknown)=>void)=>fn(root,'tile'),
    addEventListener:(name:string,fn:Listener)=>{if(!events.has(name))events.set(name,new Set());events.get(name)!.add(fn);},
    removeEventListener:(name:string,fn:Listener)=>{events.get(name)?.delete(fn);}};
  const input:RoadRehearsalInput={origin:[-114,51,1100],headingDegrees:90,length:36,halfWidth:3,blendWidth:10,endBlend:4,
    profile:Array.from({length:19},(_,i)=>({x:i*2,z:0})),ground:[],label:'synthetic flat ground'};
  for(let x=-4;x<=40;x++)for(let y=-14;y<=14;y++)input.ground.push({x,y,z:0});
  const before=JSON.stringify(input);
  let trial:Awaited<ReturnType<typeof rehearseRoadTerrain>>|undefined;
  try{
    const pending=rehearseRoadTerrain(scene,tiles,input);await vi.runAllTimersAsync();trial=await pending;
    expect(trial.summary.visualAlignmentOffsetM).toBeCloseTo(-1.3,6);
    expect(trial.summary.endpointMaxGapM).toBeLessThan(.001);
    expect(trial.summary.outerSeamMaxGapM).toBeLessThan(.001);
    expect(JSON.stringify(input)).toBe(before);
    expect(mesh.geometry).not.toBe(original);
    expect(()=>assertStreetGroundReady(scene)).toThrow(/local preview/);
    trial.setVisible(false);expect(mesh.geometry).toBe(original);expect(material.onBeforeCompile).toBe(compile);
    expect(scene.userData.roadTerrainRehearsal).toBeUndefined();
    trial.setVisible(true);expect(trial.status().active).toBe(true);
    const far=new THREE.Mesh(new THREE.PlaneGeometry(1,1));far.position.set(0,0,0);far.updateMatrixWorld(true);
    events.get(eventName)!.forEach(fn=>fn({scene:far}));expect(trial.status().active).toBe(true);far.geometry.dispose();
    events.get(eventName)!.forEach(fn=>fn({scene:root}));expect(trial.status()).toEqual({active:false,stale:true});
    expect(mesh.geometry).toBe(original);trial.setVisible(true);expect(trial.status().active).toBe(false);
    trial.dispose();trial.dispose();expect([...events.values()].every(s=>s.size===0)).toBe(true);
  }finally{trial?.dispose();original.dispose();material.dispose();vi.useRealTimers();}
},15000);

it.each(['changed tiles','cancelled build'])('does not install an obsolete proposal: %s',async(reason)=>{
  vi.useFakeTimers();
  const scene=new THREE.Scene(),group=new THREE.Group(),root=new THREE.Group();scene.add(group);group.add(root);
  const input:RoadRehearsalInput={origin:[-114,51,1100],headingDegrees:90,length:36,halfWidth:3,blendWidth:10,endBlend:4,
    profile:[{x:0,z:0},{x:36,z:0}],ground:[],label:'changing tiles'};
  for(let x=-4;x<=40;x++)for(let y=-14;y<=14;y++)input.ground.push({x,y,z:0});
  const tiles={group,visibleTiles:new Set<unknown>(['tile']),forEachLoadedModel:(fn:(s:THREE.Object3D,t:unknown)=>void)=>fn(root,'tile'),
    addEventListener:vi.fn(),removeEventListener:vi.fn()};
  try{
    const abort=new AbortController();
    const result=rehearseRoadTerrain(scene,tiles,input,abort.signal).catch(e=>e);
    if(reason==='cancelled build')abort.abort();else tiles.visibleTiles.clear();
    await vi.runAllTimersAsync();
    expect(await result).toMatchObject(reason==='cancelled build'?{name:'AbortError'}:{message:expect.stringContaining('Visible tiles changed')});
    expect(scene.userData.roadTerrainRehearsal).toBeUndefined();expect(tiles.addEventListener).not.toHaveBeenCalled();
  }finally{vi.useRealTimers();}
});
