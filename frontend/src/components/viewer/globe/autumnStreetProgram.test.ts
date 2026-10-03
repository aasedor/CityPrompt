import { describe, expect, it } from 'vitest';
import { nativeStreetPilot, placeNativeStreetModules } from './nativeStreetPilot';
import { buildNativeStreetProgram, nativeStreetGroundCells } from './nativeStreetProgram';
import { CLASSROOM_CHOICES } from '@/features/pickPlace/canonicalCatalogue';

describe('autumn drawn streets', () => {
  it.each([
    ['student_london_cobbled_mews_v1', 8, 30, 13],
    ['student_cherry_blossom_street_v1', 20, 40, 10],
    ['student_barcelona_shaded_promenade_v1', 36, 48, 36],
  ] as const)('%s retains metric modules and continuous ground', (id,width,length,count) => {
    const pilot=nativeStreetPilot(id)!;
    expect(pilot.widthM).toBe(width);
    expect(CLASSROOM_CHOICES.some(c=>c.placements[0]?.kind==='street' && c.placements[0].model.variantId===id)).toBe(true);
    expect(nativeStreetGroundCells(width,length,pilot.program!.surfaceRegions)
      .reduce((area,c)=>area+c.width*c.depth,0)).toBeCloseTo(width*length,5);
    for (const repeats of [1,2]) for (const reversed of [false,true]) {
      const route=[{x:0,y:0},{x:0,y:length*repeats}];
      if(reversed)route.reverse();
      const poses=placeNativeStreetModules(pilot,route);
      expect(poses).toHaveLength(count*repeats);
      for(const mesh of buildNativeStreetProgram(pilot.program!,width,length,route)) {
        const {geometry}=mesh;
        expect(Array.from(geometry.attributes.position.array).every(Number.isFinite)).toBe(true);
        geometry.computeBoundingBox();
        expect(geometry.boundingBox!.min.x).toBeGreaterThanOrEqual(-width/2-.001);
        expect(geometry.boundingBox!.max.x).toBeLessThanOrEqual(width/2+.001);
        expect(geometry.boundingBox!.min.y).toBeGreaterThanOrEqual(-.001);
        expect(geometry.boundingBox!.max.y).toBeLessThanOrEqual(length*repeats+.001);
        expect(pilot.program!.palette[mesh.material]).toHaveLength(3);
        geometry.dispose();
      }
    }
    const bend=[{x:0,y:0},{x:0,y:length},{x:length,y:length}];
    for(const {geometry} of buildNativeStreetProgram(pilot.program!,width,length,bend)) {
      expect(Array.from(geometry.attributes.position.array).every(Number.isFinite)).toBe(true);
      geometry.dispose();
    }
  });
});
