import {describe,it,expect} from 'vitest';
import {tramFixtures,tramRouteProblem,TRAM_STOP_MODULE} from './tramStreetProgram';

describe('Garden Tram Avenue complete manually placed stops',()=>{
  const route=[{x:0,y:0},{x:0,y:144}];
  const template=[{kind:'grove_tree',x:9.3,y:-18},{kind:TRAM_STOP_MODULE,x:5.2,y:0}];
  it('extends furnishings without creating stations',()=>{
    expect(tramFixtures(template,48,144,[])).toHaveLength(3);
    expect(tramFixtures(template,48,144,[]).some(p=>p.kind===TRAM_STOP_MODULE)).toBe(false);
  });
  it('keeps both full platforms at the explicitly chosen route station',()=>{
    const poses=tramFixtures(template,48,144,[{id:'my-stop',stationM:47}]).filter(p=>p.kind===TRAM_STOP_MODULE);
    expect(poses).toHaveLength(2);
    expect(poses.map(p=>p.x)).toEqual([-5.2,5.2]);
    expect(poses.every(p=>p.y+72===47 && p.scale===1)).toBe(true);
    expect(tramRouteProblem(route,[{id:'a',stationM:47}])).toBeNull();
  });
  it('rejects shortened routes rather than clipping saved stops',()=>{
    expect(tramRouteProblem([{x:0,y:0},{x:0,y:48}],[{id:'a',stationM:47}])).toContain('15 m');
  });
  it('rejects bends, reversals, overlapping stops and duplicate identities',()=>{
    expect(tramRouteProblem([{x:0,y:0},{x:1,y:70},{x:0,y:144}])).toContain('straight');
    expect(tramRouteProblem([{x:0,y:0},{x:0,y:100},{x:0,y:70},{x:0,y:144}])).toContain('straight');
    expect(tramRouteProblem(route,[{id:'a',stationM:40},{id:'b',stationM:60}])).toContain('32 m');
    expect(tramRouteProblem(route,[{id:'a',stationM:40},{id:'a',stationM:90}])).toContain('unique');
  });
  it('accepts rotated straight routes and complete endpoint clearances',()=>{
    expect(tramRouteProblem([{x:30,y:20},{x:78,y:20}],[{id:'a',stationM:24}])).toBeNull();
    expect(tramRouteProblem(route,[{id:'a',stationM:15},{id:'b',stationM:129}])).toBeNull();
  });
});
