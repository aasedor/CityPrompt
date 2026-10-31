import { afterAll, expect, it, vi } from 'vitest';
vi.stubEnv('DEV', true); vi.stubEnv('MODE', 'development');
const geometry = await import('./streetDrawingGeometry');
afterAll(() => vi.unstubAllEnvs());
it('keeps a bridge start and replaces only its endpoint on further clicks, including matched heights', () => {
  const props={road_selected_variant_id:'timber_covered_bridge_route_v1'};
  expect(geometry.appendStreetDrawingValue([[0,0],[1,1]],[2,2],props)).toEqual([[0,0],[2,2]]);
  expect(geometry.appendStreetDrawingValue([1000,1001],1002,props)).toEqual([1000,1002]);
  expect(geometry.appendStreetDrawingValue([[0,0]],[1,1],props)).toEqual([[0,0],[1,1]]);
  expect(geometry.appendStreetDrawingValue([[0,0],[1,1]],[2,2],{})).toEqual([[0,0],[1,1],[2,2]]);
});

it('finishes click plus double-click as two bridge points, preserving matching heights and ordinary duplicate cleanup', () => {
  const props={road_selected_variant_id:'timber_covered_bridge_route_v1'};
  let points:number[][]=[];let heights:number[]=[];
  for(const [point,height] of [[[0,0],1000],[[1,1],1001],[[1,1],1001]] as const){
    points=geometry.appendStreetDrawingValue(points,[...point],props);
    heights=geometry.appendStreetDrawingValue(heights,height,props);
  }
  expect(geometry.finishDoubleClickValues(points,props)).toEqual([[0,0],[1,1]]);
  expect(geometry.finishDoubleClickValues(heights,props)).toEqual([1000,1001]);
  expect(geometry.finishDoubleClickValues([[0,0],[1,1],[1,1]],{})).toEqual([[0,0],[1,1]]);
});
