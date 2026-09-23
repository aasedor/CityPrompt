import { expect, it } from 'vitest';
import { meadowPlantingDrifts } from './meadowPlantingDrifts';
import type { ParkGroundGuide } from './parkGroundProfiles';

it('bounds meadow density and clears a path and existing tree without touching the lawn', () => {
  const boundary=[{x:0,y:0},{x:50,y:0},{x:50,y:50},{x:0,y:50}];
  const filler: ParkGroundGuide={kind:'rectangle',x:.5,y:.5,width:.1,height:.1,color:'#fff'};
  const bed: ParkGroundGuide={kind:'ellipse',x:.2,y:.3,width:.3,height:.3,color:'#687b56'};
  const guides: ParkGroundGuide[]=[filler,filler,filler,filler,filler,bed,{...bed,x:.8},
    {kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[0,.3],[1,.3]],strokeWidthM:3,color:'#fff'}];
  const obstacles=[{x:10,y:30,radius:2}];
  const plants=meadowPlantingDrifts(boundary,guides,obstacles);
  expect(plants.length).toBeGreaterThan(10); expect(plants.length).toBeLessThanOrEqual(96);
  expect(plants).toEqual(meadowPlantingDrifts(boundary,guides,obstacles));
  for (const p of plants) {
    expect(Math.abs(p.y-35)).toBeGreaterThanOrEqual(2.25);
    expect(Math.hypot(p.x-10,p.y-30)).toBeGreaterThanOrEqual(2.55);
    expect(p.x<18||p.x>32).toBe(true);
  }
  expect(meadowPlantingDrifts([],guides,obstacles)).toEqual([]);
});
