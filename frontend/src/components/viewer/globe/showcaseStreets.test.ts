import {describe,it,expect} from 'vitest';
import {nativeStreetPilot,placeNativeStreetModules} from './nativeStreetPilot';
import {buildNativeStreetProgram,nativeStreetGroundCells} from './nativeStreetProgram';
import {TRAM_STOP_MODULE} from './tramStreetProgram';

describe('showcase source programs',()=>{
  it.each(['student_grass_tram_avenue_v1','student_vine_pergola_promenade_v1','student_grand_haussmann_boulevard_v1'])('%s retains a complete owned section and native modules when extended',id=>{
    const pilot=nativeStreetPilot(id)!;
    for(const factor of [1,2]){
      const length=pilot.fixtureLengthM*factor;
      const route=[{x:0,y:0},{x:0,y:length}];
      const poses=placeNativeStreetModules(pilot,route);
      expect(poses.length).toBeGreaterThan(0);
      expect(poses.every(p=>p.sha256.length===64 && p.scale>0)).toBe(true);
      expect(poses.filter(p=>p.kind===TRAM_STOP_MODULE)).toHaveLength(0);
      const cells=nativeStreetGroundCells(pilot.widthM,pilot.fixtureLengthM,pilot.program!.surfaceRegions);
      expect(cells.reduce((sum,c)=>sum+c.width*c.depth,0)).toBeCloseTo(pilot.widthM*pilot.fixtureLengthM);
      const meshes=buildNativeStreetProgram(pilot.program!,pilot.widthM,pilot.fixtureLengthM,route);
      expect(meshes.length).toBeGreaterThan(1);
      for(const {geometry} of meshes){
        geometry.computeBoundingBox();
        expect(geometry.boundingBox!.min.y).toBeGreaterThanOrEqual(-.001);
        expect(geometry.boundingBox!.max.y).toBeLessThanOrEqual(length+.001);
        geometry.dispose();
      }
    }
  });
  it('keeps the reference brick paving and all four planting-bed edgings',()=>{
    const pilot=nativeStreetPilot('student_vine_pergola_promenade_v1')!;
    expect(pilot.program!.paving).toBe('brick');
    expect(pilot.junctionSurface).toBe('brick');
    expect(pilot.program!.details.filter(d=>d.material==='metal' && d.height===.05)).toHaveLength(4);
  });
});
