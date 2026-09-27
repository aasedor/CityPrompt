import {describe,it,expect} from 'vitest';
import {buildSpecialistStreetProgram,specialistFixtures,specialistRouteProblem,specialistWalkingHeight,CANAL_VARIANT as C,BRIDGE_VARIANT as B} from './specialistStreetProgram';

describe('native specialist streets',()=>{
  const route=(length:number)=>[{x:0,y:0},{x:0,y:length}];
  it('preserves one basin and one original crossing as the canal extends',()=>{
    expect(specialistFixtures(C,80).map(p=>p.kind)).toEqual(['canal_ground','canal_crossing','canal_furnishings']);
    const long=specialistFixtures(C,150);
    expect(long.filter(p=>p.kind==='canal_crossing')).toHaveLength(1);
    expect(long.filter(p=>p.kind==='canal_ground')[0].y).toBe(40);
    expect(long.filter(p=>p.kind==='canal_tree')).toHaveLength(8);
    expect(long.every(p=>p.scale===1)).toBe(true);
  });
  it('rejects short, bent and reversed-back-on-itself routes',()=>{
    expect(specialistRouteProblem(C,route(79))).toMatch(/80/);
    expect(specialistRouteProblem(B,route(259))).toMatch(/260/);
    expect(specialistRouteProblem(C,[{x:0,y:0},{x:2,y:40},{x:0,y:80}])).toMatch(/straight/);
    expect(specialistRouteProblem(C,[{x:0,y:0},{x:0,y:90},{x:0,y:80}])).toMatch(/straight/);
    expect(specialistRouteProblem(C,route(80).reverse())).toBeNull();
  });
  it('keeps canal water level and extension geometry out of the original 80 metres',()=>{
    expect(buildSpecialistStreetProgram(C,route(80))).toHaveLength(0);
    const meshes=buildSpecialistStreetProgram(C,route(116));
    const water=meshes.find(m=>m.material==='water')!.geometry.getAttribute('position');
    for(let i=0;i<water.count;i++)expect(water.getZ(i)).toBeCloseTo(-2.05,5);
    for(const mesh of meshes){const p=mesh.geometry.getAttribute('position');for(let i=0;i<p.count;i++)expect(p.getY(i)).toBeGreaterThanOrEqual(80);mesh.geometry.dispose();}
  });
  it('follows the actual crossing crown and approaches without a walking floor over water',()=>{
    expect(specialistWalkingHeight(C,0,60,116)).toBeCloseTo(1.72);
    expect(specialistWalkingHeight(C,0,30,116)).toBe(-2.05);
    expect(specialistWalkingHeight(C,0,3,116)).toBe(.12);
    expect(specialistWalkingHeight(C,13.5,48,116)).toBeCloseTo(.123);
    expect(specialistWalkingHeight(C,13.5,60,116)).toBeGreaterThan(.5);
  });
  it('keeps one rigid bridge with 80 m minimum approaches meeting source deck heights',()=>{
    expect(specialistFixtures(B,260)).toEqual([{kind:'bridge_structure',x:0,y:130,z:0,yaw:0,scale:1}]);
    expect(specialistWalkingHeight(B,0,0,260)).toBe(0);
    expect(specialistWalkingHeight(B,0,80,260)).toBe(4.3);
    expect(specialistWalkingHeight(B,11,80,260)).toBe(4.482);
    expect(specialistWalkingHeight(B,0,220,260)).toBeCloseTo(2.15);
    expect(specialistWalkingHeight(B,13,130,260)).toBeNull();
  });
});
