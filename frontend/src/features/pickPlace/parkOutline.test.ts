import { describe, expect, it } from 'vitest';
import { rectangleAt } from './geometry';
import { addParkOutlinePoint, parkOutlineDimensions, parkOutlineProblem, reshapeParkOutline } from './parkOutline';
import { buildNeighborhoodParkLayout, envelopeFits, distanceToSegment, pointInPark } from '@/components/viewer/globe/neighborhoodParkLayout';

describe('editable irregular parks', () => {
  it.each(['triangle', 'l_shape'] as const)('preserves a %s when resized, rotated and saved', shape => {
    const outline = reshapeParkOutline(rectangleAt([-114.13,51.01],80,65),80,65,0,shape);
    const resized = reshapeParkOutline(outline,100,80,27);
    expect(resized).toHaveLength(shape === 'triangle' ? 3 : 6);
    const before = parkOutlineDimensions(outline), after = parkOutlineDimensions(JSON.parse(JSON.stringify(resized)));
    expect(after.width).toBeCloseTo(100,2); expect(after.depth).toBeCloseTo(80,2); expect(after.degrees).toBeCloseTo(27,3);
    before.normalized.forEach((p,i) => p.forEach((value,j) => expect(after.normalized[i][j]).toBeCloseTo(value,4)));
    expect(parkOutlineProblem(resized)).toBeNull();
    expect(parkOutlineProblem(addParkOutlinePoint(resized))).toBeNull();
  });
  it('rejects a crossed outline and duplicate corners without rejecting a concave notch', () => {
    const rect=rectangleAt([-114.13,51.01],60,60);
    expect(parkOutlineProblem([rect[0],rect[2],rect[1],rect[3]])).toContain('crosses');
    expect(parkOutlineProblem([rect[0],rect[0],rect[1],rect[2]])).toContain('space');
    expect(parkOutlineProblem(reshapeParkOutline(rect,60,60,0,'l_shape'))).toBeNull();
  });
  const shapes = [
    {name:'triangle', points:[[0,0],[90,0],[45,85]]},
    {name:'L shape', points:[[0,0],[90,0],[90,38],[50,38],[50,80],[0,80]]},
    {name:'irregular five-sided park', points:[[0,0],[85,0],[100,40],[55,75],[5,55]]},
    {name:'trapezoid', points:[[0,0],[85,0],[65,65],[15,65]]},
    {name:'six-sided wedge', points:[[0,0],[90,0],[85,30],[55,70],[20,65],[5,35]]},
  ];
  it.each(shapes)('keeps the programme inside a $name, including path widths and tree crowns', ({points}) => {
    const ring=points.map(([x,y])=>({x,y}));
    const layout=buildNeighborhoodParkLayout(ring);
    expect(layout.loop.length).toBeGreaterThan(0);
    expect(layout.modules.length).toBeGreaterThan(0);
    expect(envelopeFits(layout.loop,ring,layout.pathWidth/2-.01)).toBe(true);
    for (const module of layout.modules) expect(envelopeFits(module.envelope,ring,.79)).toBe(true);
    for (const tree of layout.trees) expect(Math.min(...ring.map((p,i)=>distanceToSegment(tree,p,ring[(i+1)%ring.length])))).toBeGreaterThan(3.24);
    for (const [a,b] of layout.paths) {
      const dx=b.x-a.x,dy=b.y-a.y,length=Math.hypot(dx,dy),r=layout.pathWidth/2;
      expect(envelopeFits([{x:a.x-dy/length*r,y:a.y+dx/length*r},{x:b.x-dy/length*r,y:b.y+dx/length*r},{x:b.x+dy/length*r,y:b.y-dx/length*r},{x:a.x+dy/length*r,y:a.y-dx/length*r}],ring)).toBe(true);
    }
  });
  it.each([
    {name:'deep concave notch',points:[[0,0],[76,0],[76,30],[28,16],[42,55],[0,55]]},
    {name:'U-shaped park',points:[[0,0],[80,0],[80,65],[60,65],[60,20],[20,20],[20,65],[0,65]]},
    {name:'narrow strip',points:[[0,0],[70,0],[70,12],[0,12]]},
    {name:'small triangular corner',points:[[0,0],[30,0],[2,30]]},
  ])('keeps a $name as usable landscape when the play programme cannot fit',({points})=>{
    for(const reversed of [false,true]) {
      const ring=(reversed?[...points].reverse():points).map(([x,y])=>({x,y}));
      const layout=buildNeighborhoodParkLayout(ring);
      expect(layout.boundary).toEqual(ring); expect(layout.modules).toHaveLength(0);
      expect(layout.trees.length+layout.shrubs.length).toBeGreaterThan(0);
      expect(layout.notes.join(' ')).toContain('you can keep');
      for(const p of [...layout.trees,...layout.shrubs])expect(pointInPark(p,ring)).toBe(true);
      for(const p of layout.trees)expect(Math.min(...ring.map((a,i)=>distanceToSegment(p,a,ring[(i+1)%ring.length])))).toBeGreaterThan(3.24);
    }
  });
});
