import { describe, expect, it } from 'vitest';
import specs from '@/data/sportsParkDimensions.json';
import openSpaces from '@/data/openSpaceArchetypes.json';
import { buildParkTrio, rect, PARK_TRIO } from './parkTrioLayout';
import { distanceToSegment, envelopeFits } from './neighborhoodParkLayout';

describe('metric sports parks', () => {
  it.each([
    {name:'triangle',points:[[0,0],[110,0],[55,100]]},
    {name:'L-shaped park',points:[[0,0],[90,0],[90,30],[50,30],[50,75],[0,75]]},
    {name:'trapezoid',points:[[0,0],[85,0],[70,60],[15,60]]},
  ])('fits a complete basketball precinct inside a $name',({points})=>{
    const boundary=points.map(([x,y])=>({x,y})),layout=buildParkTrio('basketball',boundary);
    const courts=layout.modules.filter(m=>m.asset==='sports/basketball');
    expect(courts).toHaveLength(1);
    expect([courts[0].width,courts[0].depth]).toEqual([36,23]);
    expect(layout.boundary).toEqual(boundary);
    expect(layout.modules.filter(m=>m.asset==='shared/bench').length).toBeGreaterThanOrEqual(4);
    for(const m of layout.modules)expect(envelopeFits(m.envelope,boundary,.39)).toBe(true);
    for(const path of layout.paths)for(let i=1;i<path.points.length;i++){
      const a=path.points[i-1],b=path.points[i],length=Math.hypot(b.x-a.x,b.y-a.y),r=path.width/2;
      if(length<.01)continue;
      const nx=-(b.y-a.y)/length*r,ny=(b.x-a.x)/length*r;
      expect(envelopeFits([{x:a.x+nx,y:a.y+ny},{x:b.x+nx,y:b.y+ny},{x:b.x-nx,y:b.y-ny},{x:a.x-nx,y:a.y-ny}],boundary)).toBe(true);
    }
  });
  it('locks the specified playing dimensions', () => {
    expect(specs.basketball.playing).toEqual([28, 15]);
    expect(specs.tennis.playing).toEqual([23.77, 10.97]);
    expect(specs.soccer.playing).toEqual([105, 68]);
  });
  for (const kind of ['basketball', 'tennis', 'soccer'] as const) {
    it(`${kind} accepts modest independent stretches without changing court dimensions or count`, () => {
      const spec = specs[kind];
      const [w, d] = spec.minimumPark;
      for (const [width, depth] of [[w, d], [w + 6, d], [w, d + 6], [w + 6, d + 6]]) {
        const layout = buildParkTrio(kind, rect(0, 0, width, depth));
        const courts = layout.modules.filter(m => m.asset.startsWith('sports/'));
        expect(courts).toHaveLength(kind === 'tennis' ? 2 : 1);
        for (const court of courts) expect([court.width, court.depth]).toEqual(spec.module);
        expect(layout.modules.filter(m => m.asset === 'shared/bench').length).toBeGreaterThanOrEqual(4);
      }
    });
    it(`${kind} references an authoritative parent and variant for saved compilation`, () => {
      const identity = PARK_TRIO[kind];
      const parent = openSpaces.archetypes.find(a => a.id === identity.parent);
      expect(parent).toBeDefined();
      expect(parent!.variants.some(v => v.id === identity.variant)).toBe(true);
    });
    it(`${kind} adds complete modules and routes paths to every entrance`, () => {
      const spec = specs[kind];
      for (const dims of [spec.minimumPark, [240, 240]]) {
        const layout = buildParkTrio(kind, rect(0, 0, dims[0], dims[1]));
        const courts = layout.modules.filter(m => m.asset.startsWith('sports/'));
        expect(courts.length).toBeGreaterThanOrEqual(kind === 'tennis' ? 2 : 1);
        expect(courts.length).toBeLessThanOrEqual(spec.maxModules);
        for (const court of courts) {
          expect([court.width, court.depth]).toEqual(spec.module);
          const gate = { x: court.center.x, y: court.center.y - court.depth / 2 };
          expect(layout.paths.some(path => path.points.some((b, i) => i > 0 && distanceToSegment(gate, path.points[i - 1], b) < 0.01))).toBe(true);
        }
      }
      expect(buildParkTrio(kind, rect(0, 0, 12, 20)).modules).toEqual([]);
    });
  }
});
