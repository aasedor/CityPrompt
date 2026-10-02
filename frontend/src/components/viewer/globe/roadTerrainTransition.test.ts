import { describe,it,expect } from 'vitest';
import * as THREE from 'three';
import { createRoadTerrainTransition, validateCorridorContext } from './roadTerrainTransition';
import { createTransitionTileGeometry, createTransitionRoadGeometry } from './roadTerrainTransitionMesh';

const options=()=>({profile:Array.from({length:31},(_,i)=>({x:i*2,z:1.5})),halfWidth:3,
  shoulderWidth:.6,blendWidth:12,endBlend:8,tieLength:30,startHeight:0,endHeight:0});
describe('natural road transition',()=>{
  it('meets both real road endpoints, preserves the central source height and does not mutate inputs',()=>{
    const input=options(),before=JSON.stringify(input),f=createRoadTerrainTransition(input);
    expect(f.roadHeight(0,0)).toBeCloseTo(0,10);expect(f.roadHeight(60,0)).toBeCloseTo(0,10);
    expect(f.roadHeight(30,0)).toBeCloseTo(1.5,10);expect(JSON.stringify(input)).toBe(before);
    let maxGrade=0;for(let x=.1;x<=60;x+=.1)maxGrade=Math.max(maxGrade,Math.abs(f.roadHeight(x,0)-f.roadHeight(x-.1,0))/.1);
    expect(maxGrade).toBeLessThan(.095);
  });
  it('has zero displacement and slope change at all outer boundaries',()=>{
    const f=createRoadTerrainTransition(options());
    for(const [x,y] of [[-8,0],[68,0],[30,-15.6],[30,15.6],[30,20]])expect(f.groundHeight(x,y,.27)).toBe(.27);
    expect(Math.abs(f.groundHeight(30,15.599,.27)-.27)).toBeLessThan(1e-9);
    expect(f.groundHeight(30,0,0)).toBeCloseTo(1.49,9);
  });
  it('rejects excessive grades instead of hiding them with short ramps',()=>{
    expect(()=>createRoadTerrainTransition({...options(),startHeight:-12})).toThrow(/grade/);
    expect(()=>createRoadTerrainTransition({...options(),blendWidth:1})).toThrow(/dimensions/);
  });
  it('rejects missing ground, canopy hits and insufficient transition width',()=>{
    const f=createRoadTerrainTransition(options());
    expect(validateCorridorContext(f,[{x:30,y:10,z:null}],()=>0).ok).toBe(false);
    expect(validateCorridorContext(f,[{x:30,y:10,z:8}],()=>0).reason).toMatch(/tree/);
    expect(validateCorridorContext(createRoadTerrainTransition({...options(),blendWidth:4}),[{x:30,y:6,z:0}],()=>0).reason).toMatch(/room/);
    expect(validateCorridorContext(f,[{x:30,y:10,z:0}],()=>0).ok).toBe(true);
  });
  it('preserves source imagery coordinates while refining and grading coarse ground',()=>{
    const f=createRoadTerrainTransition(options());
    const source=new THREE.PlaneGeometry(12,12,1,1);source.translate(30,10,0);
    const before=source.getAttribute('position').array.slice();
    const geometry=createTransitionTileGeometry(source,new THREE.Matrix4(),f)!;
    const p=geometry.getAttribute('position'),uv=geometry.getAttribute('uv');
    expect(p.count).toBeGreaterThan(source.getAttribute('position').count);
    for(let i=0;i<p.count;i++){
      // Original linear map must survive every new vertex, including the seam.
      expect(uv.getX(i)).toBeCloseTo((p.getX(i)-24)/12,5);
      expect(uv.getY(i)).toBeCloseTo((p.getY(i)-4)/12,5);
      expect(p.getZ(i)).toBeCloseTo(f.groundHeight(p.getX(i),p.getY(i),0),5);
      if(p.getY(i)>=15.6)expect(p.getZ(i)).toBe(0);
    }
    expect(source.getAttribute('position').array).toEqual(before);
    geometry.dispose();source.dispose();
  });
  it('does not alter distant geometry and fails within a finite budget',()=>{
    const f=createRoadTerrainTransition(options()),source=new THREE.PlaneGeometry(10,10);source.translate(200,0,0);
    expect(createTransitionTileGeometry(source,new THREE.Matrix4(),f)).toBeNull();
    source.translate(-170,0,0);
    expect(()=>createTransitionTileGeometry(source,new THREE.Matrix4(),f,30)).toThrow(/budget/);
    source.dispose();
  });
  it('uses the same road height for the physical mesh, including the crown',()=>{
    const f=createRoadTerrainTransition(options()),g=createTransitionRoadGeometry(f,-3,3),p=g.getAttribute('position');
    for(let i=0;i<p.count;i++)expect(p.getZ(i)).toBeCloseTo(f.roadHeight(p.getX(i),p.getY(i)),5);
    expect(f.roadHeight(30,0)-f.roadHeight(30,3)).toBeCloseTo(.06,8);g.dispose();
  });
  it('matches measured crossfall across both endpoints instead of just joining the centre',()=>{
    const start=Array.from({length:11},(_,i)=>({y:i-5,z:(i-5)*.015}));
    const end=start.map(p=>({y:p.y,z:-p.y*.012}));
    const f=createRoadTerrainTransition({...options(),startCrossSection:start,endCrossSection:end});
    for(let y=-3;y<=3;y+=.25){expect(f.roadHeight(0,y)).toBeCloseTo(y*.015,9);expect(f.roadHeight(60,y)).toBeCloseTo(-y*.012,9);}
  });
  it('rejects narrow raised objects even when a coarse probe grid could miss them',()=>{
    const f=createRoadTerrainTransition(options()),g=new THREE.PlaneGeometry(.1,.1);g.translate(30,6,4);
    expect(()=>createTransitionTileGeometry(g,new THREE.Matrix4(),f,300_000,()=>0)).toThrow(/narrow object/);
    g.dispose();
  });
});
