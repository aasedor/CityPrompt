import { afterAll, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { modularBridgeProgramFor } from '@/components/viewer/globe/modularBridgeProgram';
import { nativeStreetRouteProblem } from '@/components/viewer/globe/nativeStreetPilot';
import { MODULAR_BRIDGE_ASSETS } from './assetRegistry';
import { placementProblem } from './geometry';
import { fitBridgeDrawingSpan } from './bridgeDrawingSpan';
import { streetRouteProblem } from './streetPlacement';
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

const origin = [-114, 51], sx = metersPerDegLon(origin[1]);
const point = (east: number, north: number) => [origin[0] + east / sx, origin[1] + north / 111320];
const site = { id:'site', zone_type:'site_boundary', coordinates:[point(-600,-600),point(600,-600),point(600,600),point(-600,600)],
  properties:{terrain_strategy:'level',community_3d_mask_existing_tiles:true} } as unknown as SiteZone;

it.each(MODULAR_BRIDGE_ASSETS)('fits approximate endpoints for $id without changing its source or bearing', asset => {
  const program = modularBridgeProgramFor(asset.model.variantId)!;
  for (const skipSnapping of [false, true]) for (const requested of [program.minLengthM / 3, program.maxLengthM * 1.4]) {
    const points = [origin, point(requested * .6, requested * .8)];
    const before = JSON.stringify({points, properties:asset.properties});
    const result = geometry.streetDrawingGeometry(points,asset.properties,[site],{skipSnapping});
    const controls = result.properties.plan_route_controls as number[][];
    const dx = (controls[1][0]-controls[0][0])*sx, dy = (controls[1][1]-controls[0][1])*111320;
    expect(Math.hypot(dx,dy)).toBeGreaterThanOrEqual(program.minLengthM - 1e-6);
    expect(Math.hypot(dx,dy)).toBeLessThanOrEqual(program.maxLengthM + 1e-6);
    expect(Math.abs(dx*.8-dy*.6)).toBeLessThan(.00001);
    expect(controls[0]).toEqual(origin);
    expect(nativeStreetRouteProblem(result,site)).toBeNull();
    expect(streetRouteProblem(result.coordinates,asset.sectionWidth,controls,result.properties)).toBeNull();
    expect(result.properties.road_selected_variant_id).toBe(asset.model.variantId);
    expect(result.properties.public_realm_lego).toBeUndefined();
    expect(JSON.stringify({points,properties:asset.properties})).toBe(before);
    expect(geometry.streetDrawingGeometry(controls,asset.properties,[site],{skipSnapping})).toEqual(result);
  }
});

it.each(MODULAR_BRIDGE_ASSETS)('preserves an in-range $id endpoint exactly', asset => {
  const program=modularBridgeProgramFor(asset.model.variantId)!;
  const length=(program.minLengthM+program.maxLengthM)/2, points=[origin,point(-length,0)];
  expect(geometry.streetDrawingGeometry(points,asset.properties,[],{skipSnapping:true}).properties.plan_route_controls).toEqual(points);
});

it('keeps an oversized bridge outside a small parcel invalid instead of shrinking its structure or clipping it', () => {
  const asset=MODULAR_BRIDGE_ASSETS.find(a=>a.id==='swooping_cycle_flyover_route_v1')!;
  const small={...site,coordinates:[point(-50,-50),point(50,-50),point(50,50),point(-50,50)]};
  const result=geometry.streetDrawingGeometry([origin,point(0,20)],asset.properties,[small]);
  expect(nativeStreetRouteProblem(result,small)).toBeNull();
  expect(placementProblem(result.coordinates,[],small)).not.toBeNull();
});

it('leaves duplicate, malformed and non-bridge inputs unchanged rather than inventing a heading', () => {
  const props={road_selected_variant_id:'weathering_steel_v_footbridge_route_v1'};
  for(const points of [[origin,origin],[origin,point(.01,0)],[[NaN,51],origin],[origin,[]],[origin],[origin,point(20,0),point(20,20)]])
    expect(fitBridgeDrawingSpan(points,props)).toBe(points);
  const ordinary=[origin,point(10,0)];
  expect(fitBridgeDrawingSpan(ordinary,{})).toBe(ordinary);
});


it('keeps a valid near-boundary first anchor fixed while fitting a bridge span', () => {
  const asset=MODULAR_BRIDGE_ASSETS.find(a=>a.id==='weathering_steel_v_footbridge_route_v1')!;
  const boundary={...site,coordinates:[point(0,0),point(300,0),point(300,300),point(0,300)]};
  const points=[point(1,150),point(11,150)];
  const result=geometry.streetDrawingGeometry(points,asset.properties,[boundary]);
  expect((result.properties.plan_route_controls as number[][])[0]).toEqual(points[0]);
  expect(placementProblem(result.coordinates,[],boundary)).toBeNull();
});
