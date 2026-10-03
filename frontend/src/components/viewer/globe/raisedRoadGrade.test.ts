import {it,expect} from 'vitest';
import * as THREE from 'three';
import {createRoadTerrainTransition,type CorridorProbe} from './roadTerrainTransition';
import {raiseRoadAboveGround} from './raisedRoadGrade';
import {createTransitionTileGeometry} from './roadTerrainTransitionMesh';

const make=(ground:(x:number,y:number)=>number)=>{
  const section=(x:number)=>Array.from({length:33},(_,i)=>({y:-4+i*.25,z:ground(x,-4+i*.25)}));
  const base=createRoadTerrainTransition({profile:Array.from({length:21},(_,i)=>({x:i*2,z:ground(i*2,0)})),
    halfWidth:3,shoulderWidth:.6,blendWidth:10,endBlend:4,tieLength:20,
    startHeight:ground(0,0),endHeight:ground(40,0),startCrossSection:section(0),endCrossSection:section(40)});
  const probes:CorridorProbe[]=[];
  for(let x=0;x<=40;x+=.5)for(let y=-3.5;y<=3.5;y+=.5)probes.push({x,y,z:ground(x,y)});
  return {base,probes};
};

it('clears the full width, retains both joins, and keeps road-edge grades bounded',()=>{
  const ground=(x:number,y:number)=>.025*x+.12*Math.sin(Math.PI*x/40)+.01*y;
  const {base,probes}=make(ground),before=JSON.stringify({options:base.options,probes});
  const field=raiseRoadAboveGround(base,probes,ground);
  for(const p of probes) {
    expect(field.roadHeight(p.x,p.y)-p.z!).toBeGreaterThanOrEqual(-1e-8);
    if(p.x>=4&&p.x<=36)expect(field.roadHeight(p.x,p.y)-p.z!).toBeGreaterThanOrEqual(.12-1e-8);
  }
  for(const y of [-3.5,0,3.5]) {
    expect(field.roadHeight(0,y)).toBeCloseTo(ground(0,y),8);
    expect(field.roadHeight(40,y)).toBeCloseTo(ground(40,y),8);
    for(let x=.5;x<=40;x+=.5)expect(Math.abs(field.roadHeight(x,y)-field.roadHeight(x-.5,y))/.5).toBeLessThanOrEqual(.100001);
  }
  expect(field.groundHeight(20,field.outerWidth,2)).toBe(2);
  expect(JSON.stringify({options:base.options,probes})).toBe(before);
});

it('refuses an intervening rise that cannot be reached from a fixed street end',()=>{
  const ground=(x:number)=>x<10?.3*x:x<30?3:3-.2*(x-30);
  const {base,probes}=make(ground);
  expect(()=>raiseRoadAboveGround(base,probes,ground)).toThrow(/Lengthen the approach/);
});

it('does not mistake a canopy or missing surface for a reason to raise the road',()=>{
  const {base,probes}=make(()=>0);
  expect(()=>raiseRoadAboveGround(base,probes.slice(1),()=>0)).toThrow(/complete/);
  probes[100].z=3;expect(()=>raiseRoadAboveGround(base,probes,()=>0)).toThrow(/object|uncertain/i);
  probes[100].z=null;expect(()=>raiseRoadAboveGround(base,probes,()=>0)).toThrow(/incomplete/);
});

it('raises the crown enough to clear high ground under either shoulder',()=>{
  const ground=(x:number,y:number)=>.08*Math.sin(Math.PI*x/40)*(y+3.5);
  const {base,probes}=make(ground),field=raiseRoadAboveGround(base,probes,ground);
  expect(field.roadHeight(20,3.5)).toBeGreaterThanOrEqual(.56+.12-1e-8);
  expect(field.roadHeight(20,0)).toBeGreaterThan(.7);
});

it('rejects a terrain rise between probes instead of cutting it below the road',()=>{
  const {base,probes}=make(()=>0),field=raiseRoadAboveGround(base,probes,()=>0);
  const source=new THREE.PlaneGeometry(.1,.1);source.translate(20,0,.3);
  expect(()=>createTransitionTileGeometry(source,new THREE.Matrix4(),field,300_000,()=>.3)).toThrow(/pierce/);
  source.dispose();
});
