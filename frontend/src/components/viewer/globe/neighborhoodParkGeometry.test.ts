import {describe,expect,it} from 'vitest';
import {parkApproachGround,parkPadDatum,roundedParkPad} from './neighborhoodParkGeometry';
import {buildNeighborhoodParkLayout,envelopeFits,type ParkPoint} from './neighborhoodParkLayout';
const boundary:ParkPoint[]=[{x:0,y:0},{x:70,y:0},{x:70,y:55},{x:0,y:55}];
const layout=buildNeighborhoodParkLayout(boundary);
describe('neighbourhood park ground contact',()=>{
  it('keeps rounded pads wholly inside their reserved envelope',()=>{
    for(const module of layout.modules) expect(envelopeFits(roundedParkPad(module),boundary,.7)).toBe(true);
  });
  it('meets each pad across the full path width and returns to sloping terrain',()=>{
    const ground=(x:number,y:number)=>x*.012+y*.016;
    layout.modules.forEach((module,i)=>{
      const path=layout.paths[i], [a,b]=path, dx=b.x-a.x,dy=b.y-a.y,length=Math.hypot(dx,dy);
      const sample=parkApproachGround(module,path,ground), datum=parkPadDatum(module,ground).high+.01;
      for(const side of [-1.3,0,1.3]) expect(sample(a.x-dy/length*side,a.y+dx/length*side)).toBeCloseTo(datum,6);
      expect(sample(b.x,b.y)).toBeCloseTo(ground(b.x,b.y),6);
      for(let j=0;j<=10;j++) {const x=a.x+dx*j/10,y=a.y+dy*j/10;expect(sample(x,y)).toBeGreaterThanOrEqual(ground(x,y));}
    });
  });
  it('includes an interior ground hump when seating a rigid module',()=>{
    const module=layout.modules[0];
    const ground=(x:number,y:number)=>Math.exp(-((x-module.center.x)**2+(y-module.center.y)**2));
    expect(parkPadDatum(module,ground).high).toBeCloseTo(1,6);
  });
});
