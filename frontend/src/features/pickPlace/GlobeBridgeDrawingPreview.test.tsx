import { act, cleanup, fireEvent, render } from '@testing-library/react';
import { afterAll, afterEach, expect, it, vi } from 'vitest';
import { Matrix4 } from 'three';
import type { SiteZone } from '@/types';
const harness = vi.hoisted(() => ({ frame: null as null | ((state: { clock: { elapsedTime: number } }) => void),
  canvas: null as HTMLCanvasElement | null, zone: null as SiteZone | null, camera: null as unknown }));
vi.mock('@react-three/fiber', () => ({
  useThree: () => ({gl:{domElement:harness.canvas},camera:harness.camera,invalidate:()=>{}}),
  useFrame: (callback: typeof harness.frame) => { harness.frame=callback; },
}));
vi.mock('@/components/viewer/globe/GlobeStreetDetailLayer', () => ({
  GlobeStreetDraft: ({ zone }: {zone:SiteZone}) => {harness.zone=zone;return <div data-testid="bridge-model"/>;},
}));
vi.mock('./PublicRoadSuggestionMarker', () => ({PublicRoadSuggestionMarker:()=>null}));
vi.stubEnv('DEV',false);vi.stubEnv('MODE','production');
const { GlobeStreetDrawingPreview } = await import('./GlobeStreetDrawingPreview');
const { MODULAR_BRIDGE_ASSETS } = await import('./assetRegistry');
afterEach(cleanup);afterAll(()=>vi.unstubAllEnvs());

it('previews and tracks a mobile crosshair without any pointer event, fitting an approximate narrow span', () => {
  harness.canvas=document.createElement('canvas');
  harness.canvas.getBoundingClientRect=()=>({width:390,height:800,left:0,top:0}) as DOMRect;
  const matrix=new Matrix4(); harness.camera={matrixWorld:matrix};
  const asset=MODULAR_BRIDGE_ASSETS.find(item=>item.id==='weathering_steel_v_footbridge_route_v1')!;
  const boundary={id:'site',zone_type:'site_boundary',coordinates:[[-115,50],[-113,50],[-113,52],[-115,52]],
    properties:{terrain_strategy:'level',community_3d_mask_existing_tiles:true}} as unknown as SiteZone;
  let cursor:[number,number]=[-114,51+12/111320];
  const raycastSurface=vi.fn(()=>({lngLat:cursor,height:1000}));
  const props={points:[[-114,51]],pointHeights:[1000],properties:asset.properties,zones:[boundary],terrainHeight:1000,raycastSurface};
  const view=render(<GlobeStreetDrawingPreview {...props}/>);
  act(()=>harness.frame!({clock:{elapsedTime:1}}));
  expect(raycastSurface).toHaveBeenLastCalledWith(0,0);
  expect(view.queryByTestId('bridge-model')).not.toBeNull();
  fireEvent.pointerLeave(harness.canvas);
  act(()=>harness.frame!({clock:{elapsedTime:1.5}}));
  expect(view.queryByTestId('bridge-model')).not.toBeNull();
  const first=harness.zone?.properties?.plan_route_controls;
  cursor=[-113.998,51]; matrix.makeTranslation(1,0,0);
  act(()=>harness.frame!({clock:{elapsedTime:2}}));
  expect(harness.zone?.properties?.plan_route_controls).not.toEqual(first);
  view.rerender(<GlobeStreetDrawingPreview {...props} points={[]}/>);
  expect(view.queryByTestId('bridge-model')).toBeNull();
});

it.each([
  ['timber_covered_bridge_route_v1',80], ['planted_green_bridge_route_v1',190],
  ['brick_arch_viaduct_route_v1',140], ['rail_through_truss_route_v1',150],
  ['stone_arch_road_bridge_route_v1',120], ['tied_arch_shared_bridge_route_v1',65],
  ['steel_truss_road_bridge_route_v1',35], ['swooping_cycle_flyover_route_v1',350],
  ['cable_stayed_cycle_ring_route_v1',185], ['weathering_steel_v_footbridge_route_v1',55],
] as const)('keeps the production %s preview after the second click when the cursor moves elsewhere', (variant,lengthM) => {
  harness.canvas=document.createElement('canvas');
  harness.canvas.getBoundingClientRect=()=>({width:1000,height:800,left:0,top:0}) as DOMRect;
  harness.camera={matrixWorld:new Matrix4()};
  const points=[[-114,51],[-114,51+lengthM/111320]];
  let cursor=points[1];
  const boundary={id:'site',zone_type:'site_boundary',coordinates:[[-115,50],[-113,50],[-113,52],[-115,52]],
    properties:{terrain_elevation_m:1000,terrain_strategy:'level',community_3d_mask_existing_tiles:true}} as unknown as SiteZone;
  const onStatusChange=vi.fn();
  const asset=MODULAR_BRIDGE_ASSETS.find(item=>item.id===variant);
  if(!asset)throw new Error(`Production bridge missing: ${variant}`);
  const props={points:[points[0]],pointHeights:[1000],properties:asset.properties,
    zones:[boundary],terrainHeight:1000,skipSnapping:true,onStatusChange,
    raycastSurface:()=>({lngLat:cursor as [number,number],height:1000})};
  const view=render(<GlobeStreetDrawingPreview {...props}/>);
  expect(view.queryByTestId('bridge-model')).toBeNull();
  fireEvent.pointerMove(harness.canvas,{clientX:800,clientY:400});
  act(()=>harness.frame!({clock:{elapsedTime:1}}));
  expect(view.queryByTestId('bridge-model')).not.toBeNull();
  expect(harness.zone?.properties?.plan_route_controls).toEqual(points);
  view.rerender(<GlobeStreetDrawingPreview {...props} points={points}/>);
  cursor=[-113.999,51+20/111320];
  fireEvent.pointerMove(harness.canvas,{clientX:900,clientY:450});
  act(()=>harness.frame!({clock:{elapsedTime:2}}));
  expect(view.queryByTestId('bridge-model')).not.toBeNull();
  expect(harness.zone?.properties?.plan_route_controls).toEqual(points);
  expect(onStatusChange).toHaveBeenLastCalledWith(null);
  view.rerender(<GlobeStreetDrawingPreview {...props} points={[points[0]]}/>);
  expect(view.queryByTestId('bridge-model')).toBeNull();
});
