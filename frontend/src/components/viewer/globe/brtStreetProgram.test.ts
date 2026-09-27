import {describe,it,expect} from 'vitest';
import {brtRouteProblem,brtStreetLayout,buildBrtStreetProgram,type BrtBox} from './brtStreetProgram';

const route=[{x:0,y:0},{x:0,y:100}];
const sourceStop=[{id:'source-platform',stationM:32}];
describe('BRT original source program',()=>{
  it('reconstructs the exact native stationing and source fixture inventory',()=>{
    const result=brtStreetLayout(100,sourceStop);
    expect(result.fixtures).toHaveLength(35);
    expect(result.fixtures.filter(p=>p.kind==='station_program')).toEqual([{kind:'station_program',x:0,y:32,z:0,yaw:0,scale:1}]);
    expect(result.fixtures.filter(p=>p.kind==='shade_tree' && p.x>0).map(p=>p.y-50)).toEqual([-42,-28,-14,0,28,42]);
    expect(result.fixtures.filter(p=>p.kind==='light' && p.x>0).map(p=>p.y-50)).toEqual([-35,-7,21]);
    expect(result.fixtures.filter(p=>p.kind==='bus_symbol').map(p=>[p.x,p.y-50])).toEqual([[-2.4,-40],[-2.4,38],[2.4,-40],[2.4,38]]);
  });
  it('never introduces a station or a crossing opening automatically',()=>{
    const {fixtures,primitives}=brtStreetLayout(240,[]);
    expect(fixtures.some(p=>p.kind==='station_program')).toBe(false);
    const walks=primitives.filter((p):p is BrtBox=>p.kind==='box' && p.material==='paving' && p.width===2.9 && p.height===.15);
    expect(walks).toHaveLength(2);expect(walks.every(p=>p.depth===240)).toBe(true);
  });
  it('moves the complete ramp opening with a manually chosen station',()=>{
    const {primitives,fixtures}=brtStreetLayout(180,[{id:'chosen',stationM:80}]);
    expect(fixtures.find(p=>p.kind==='station_program')?.y).toBe(80);
    const walks=primitives.filter((p):p is BrtBox=>p.kind==='box' && p.width===2.9 && p.height===.15 && p.x>0);
    expect(walks.map(p=>[p.y-p.depth/2,p.y+p.depth/2])).toEqual([[0,102.5],[113.5,180]]);
    expect(fixtures.filter(p=>p.kind==='tree_well_grate').every(p=>p.y+.95<=99.5 || p.y-.95>=113.5)).toBe(true);
  });
  it('preserves complete stop envelopes and rejects overlapping or unsupported edits',()=>{
    expect(brtRouteProblem(route,sourceStop)).toBeNull();
    expect(brtRouteProblem(route,[{id:'end',stationM:10}])).toMatch(/21 m/);
    expect(brtRouteProblem(route,[{id:'end',stationM:80}])).toMatch(/33.5 m/);
    expect(brtRouteProblem(route,[...sourceStop,{id:'near',stationM:60}])).toMatch(/56.5 m/);
    expect(brtRouteProblem(route,[...sourceStop,...sourceStop])).toMatch(/duplicate/);
    expect(brtRouteProblem([{x:0,y:0},{x:10,y:50},{x:0,y:100}],sourceStop)).toMatch(/straight/);
    expect(brtRouteProblem([{x:0,y:0},{x:0,y:60},{x:0,y:40},{x:0,y:100}],sourceStop)).toMatch(/straight/);
    expect(brtRouteProblem(route,[{id:'bad',stationM:NaN}])).toMatch(/invalid/);
  });
  it('keeps curb and platform ground heights under a rotated ENU frame',()=>{
    const meshes=buildBrtStreetProgram([{x:10,y:20},{x:110,y:20}],sourceStop,.025);
    expect(meshes.map(m=>m.material)).toEqual(expect.arrayContaining(['asphalt','bus_red','soil','paving','paint','curb']));
    for(const {geometry} of meshes){geometry.computeBoundingBox();expect(geometry.boundingBox!.min.x).toBeGreaterThanOrEqual(9.999);expect(geometry.boundingBox!.max.x).toBeLessThanOrEqual(110.001);geometry.dispose();}
    const red=meshes.find(m=>m.material==='bus_red')!;expect(red.geometry.boundingBox!.max.z).toBeCloseTo(.031,5);
  });
});
