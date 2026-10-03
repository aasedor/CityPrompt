import { describe, expect, it } from 'vitest';
import { advanceParkWalk, nearestParkWalkPoint, parkWalkHeight, type ParkWalkingNetwork, type WalkPoint } from './parkWalking';

const rect = (x0: number, x1: number, y0: number, y1: number, z: number) => [
  [[x0,y0,z],[x1,y0,z],[x1,y1,z]], [[x0,y0,z],[x1,y1,z],[x0,y1,z]],
];
function network(triangles = rect(-2,2,-2,2,0)): ParkWalkingNetwork {
  return { version:1, triangles, entrance:[0,-2,0], maxStepM:.22, obstacles:[], routes:[] };
}
describe('continuous park walking', () => {
  it('walks up and down real treads without being caught on their shared edges', () => {
    const n = network(Array.from({length:12},(_,i)=>rect(-2,2,i*.4,(i+1)*.4,i*.15)).flat());
    let p: WalkPoint = [0,.01,0];
    for(let i=0;i<55;i++)p=advanceParkWalk(n,p,[0,p[1]+.08]);
    expect(p[1]).toBeCloseTo(4.41);expect(p[2]).toBeCloseTo(1.65);
    for(let i=0;i<55;i++)p=advanceParkWalk(n,p,[0,p[1]-.08]);
    expect(p[1]).toBeCloseTo(.01);expect(p[2]).toBe(0);
  });
  it('cannot walk through a pool or teleport down a retaining wall', () => {
    const n=network([...rect(-2,2,-2,0,0),...rect(-2,2,.25,2,-3)]);
    const p=advanceParkWalk(n,[0,-.05,0],[0,1]);
    expect(p[1]).toBeLessThanOrEqual(0);expect(p[2]).toBe(0);
    expect(advanceParkWalk(n,p,[0,-.3])[1]).toBeLessThan(p[1]);
  });
  it('slides along a path edge and can immediately move away again', () => {
    const n=network();let p:WalkPoint=[1.99,0,0];
    for(let i=0;i<10;i++)p=advanceParkWalk(n,p,[p[0]+.04,p[1]+.06]);
    expect(p[0]).toBeLessThanOrEqual(2.00001);expect(p[1]).toBeGreaterThan(.5);
    expect(advanceParkWalk(n,p,[p[0]-.1,p[1]])[0]).toBeLessThan(p[0]);
  });
  it('excludes furniture and recovers a start inside an obstacle to open paving', () => {
    const n=network();n.obstacles=[[-.5,.5,-.5,.5]];
    expect(parkWalkHeight(n,0,0)).toBeNull();
    const p=nearestParkWalkPoint(n,0,0)!;
    expect(parkWalkHeight(n,p[0],p[1])).toBe(0);
    expect(Math.hypot(p[0],p[1])).toBeGreaterThan(.6);
  });
  it('handles a continuously sloping triangle surface in both directions', () => {
    const n=network([[[0,0,0],[3,0,0],[3,10,2]],[[0,0,0],[3,10,2],[0,10,2]]]);
    let p:WalkPoint=[1,0,0];
    for(let i=0;i<100;i++)p=advanceParkWalk(n,p,[1,p[1]+.09]);
    expect(p[2]).toBeCloseTo(1.8);
    for(let i=0;i<100;i++)p=advanceParkWalk(n,p,[1,p[1]-.09]);
    expect(p[2]).toBeCloseTo(0);
  });
});
