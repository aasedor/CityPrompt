import { describe, expect, it } from 'vitest';
import { nativeStreetPilot, nativeStreetRouteProblem, placeNativeStreetModules } from './nativeStreetPilot';
import { ELEVATED_RAIL_VARIANT as R } from './elevatedRailProgram';
import { buildNativeStreetProgram } from './nativeStreetProgram';
import { specialistRouteProblem, specialistWalkingHeight } from './specialistStreetProgram';
import { specialistConnectionProblem } from '@/features/pickPlace/specialistConnections';
import { addStreetBend } from '@/features/pickPlace/streetPlacement';
import { detectConnectedStreetIntersections } from './streetGraphIntersections';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import type { SiteZone } from '@/types';
import { constrainElevatedRailWalk } from './elevatedRailWalking';

const pilot=nativeStreetPilot(R)!;
const street=(id:string,line:number[][],variant=R,width=26):SiteZone=>{
  const ll=line.map(([x,y])=>[x/111320,y/111320]);
  return {id,project_id:'test',zone_type:'road',coordinates:bufferLineToPolygon(ll,width),color:'#aaa',sort_order:0,created_at:'1',updated_at:'1',properties:{road_selected_variant_id:variant,road_archetype_id:variant===R?'elevated_garden_rail':'local',width,plan_centerline:ll}};
};
describe('elevated rail exact route',()=>{
  it('blocks column penetration but allows retreat, side-sliding and both clear paths',()=>{
    const zone=street('r',[[0,0],[0,100]]);
    const pose=(x:number,y:number)=>({lng:x/111320,lat:y/111320,groundHeight:0,heading:0});
    const stopped=constrainElevatedRailWalk([zone],pose(-3,2),pose(3,2));
    expect(stopped.lng*111320).toBeLessThanOrEqual(-1.2);
    expect(constrainElevatedRailWalk([zone],stopped,pose(-3,2)).lng*111320).toBeCloseTo(-3);
    const slid=constrainElevatedRailWalk([zone],pose(-1.21,1),pose(-.9,1.3));
    expect(slid.lat*111320).toBeCloseTo(1.3);
    for(const x of [-3.25,3.25,11]){
      expect(constrainElevatedRailWalk([zone],pose(x,0),pose(x,100)).lat*111320).toBeCloseTo(100);
      expect(constrainElevatedRailWalk([zone],pose(x,100),pose(x,0)).lat*111320).toBeCloseTo(0);
    }
  });
  it.each([48,49.3,72,103.7,288])('keeps end supports, one train and four buffers at %s m',length=>{
    for(const route of [[{x:0,y:0},{x:0,y:length}],[{x:0,y:length},{x:0,y:0}],[{x:0,y:0},{x:length*.6,y:length*.8}]]){
      const poses=placeNativeStreetModules(pilot,route);
      const piers=poses.filter(p=>p.kind==='rail_pier').sort((a,b)=>a.stationM-b.stationM);
      expect(piers[0].stationM).toBeCloseTo(2);
      expect(piers[piers.length-1].stationM).toBeCloseTo(length-2);
      expect(piers.slice(1).every((p,i)=>p.stationM-piers[i].stationM<=22.001)).toBe(true);
      expect(poses.filter(p=>p.kind==='rail_train')).toHaveLength(1);
      expect(poses.filter(p=>p.kind==='rail_buffer')).toHaveLength(4);
      expect(poses.filter(p=>p.kind==='rail_end')).toHaveLength(2);
      expect(poses.filter(p=>p.kind.startsWith('rail_')).every(p=>p.scale===1)).toBe(true);
      const meshes=buildNativeStreetProgram(pilot.program!,26,48,route);
      for(const m of meshes){
        expect(Array.from(m.geometry.getAttribute('position').array).every(Number.isFinite)).toBe(true);
        m.geometry.dispose();
      }
    }
  });
  it('covers a partial final module with continuous rail heads and deck',()=>{
    const meshes=buildNativeStreetProgram(pilot.program!,26,48,[{x:0,y:0},{x:0,y:103.7}]);
    for(const material of ['concrete','steel']){
      const g=meshes.find(m=>m.material===material)!.geometry;g.computeBoundingBox();
      expect(g.boundingBox!.min.y).toBeCloseTo(0);expect(g.boundingBox!.max.y).toBeCloseTo(103.7,4);
      const positions=g.getAttribute('position');
      for(const y of [47.99,48.01,95.99,96.01,103.69]){
        let covered=false;
        for(let i=0;i<g.index!.count;i+=3){
          const ids=[0,1,2].map(j=>g.index!.getX(i+j));
          if(ids.every(v=>positions.getZ(v)>7.6)&&Math.min(...ids.map(v=>positions.getY(v)))<=y&&Math.max(...ids.map(v=>positions.getY(v)))>=y)covered=true;
        }
        expect(covered).toBe(true);
      }
    }
    meshes.forEach(m=>m.geometry.dispose());
  });
  it('rejects bends, reversed interior stations, wrong lengths and unprepared ground',()=>{
    expect(specialistRouteProblem(R,[{x:0,y:0},{x:1,y:30},{x:0,y:60}])).toMatch(/straight/);
    expect(specialistRouteProblem(R,[{x:0,y:0},{x:0,y:70},{x:0,y:60}])).toMatch(/straight/);
    for(const length of [47,289])expect(specialistRouteProblem(R,[{x:0,y:0},{x:0,y:length}])).toMatch(/48/);
    expect(nativeStreetRouteProblem(street('r',[[0,0],[0,60]]),null)).toMatch(/level/);
    expect(addStreetBend(street('r',[[0,0],[0,60]]))).toBeNull();
  });
  it('keeps walking below the railway throughout all public paths',()=>{
    for(const x of [-3.25,3.25,11])for(let y=0;y<=288;y+=.25)expect(specialistWalkingHeight(R,x,y,288)).toBe(.025);
  });
  it('protects the full corridor symmetrically and creates no asphalt intersection',()=>{
    const rail=street('rail',[[0,0],[0,100]]),cross=street('cross',[[-50,50],[50,50]],'local',8);
    expect(specialistConnectionProblem(cross,[rail])).toMatch(/elevated rail/);
    expect(specialistConnectionProblem(rail,[cross])).toMatch(/elevated rail/);
    expect(specialistConnectionProblem(street('apart',[[20,0],[20,100]],'local',8),[rail])).toBeNull();
    expect(detectConnectedStreetIntersections([rail,cross],true)).toHaveLength(0);
  });
});
