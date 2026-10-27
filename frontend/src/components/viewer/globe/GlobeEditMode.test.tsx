import {createContext} from 'react';
import {render, screen, cleanup, fireEvent} from '@testing-library/react';
import {afterEach, expect, it, vi} from 'vitest';
import * as THREE from 'three';
import {Ellipsoid, WGS84_ELLIPSOID} from '3d-tiles-renderer';
import type {SiteZone} from '@/types';
import {GlobeEditMode} from './GlobeEditMode';
import {GlobeDragProvider} from './useGlobeDragRef';
import {rectangleAt} from '@/features/pickPlace/geometry';
import {placeAsset, placementProperties} from '@/features/pickPlace/catalogue';

vi.mock('@react-three/fiber',()=>({useThree:()=>({camera:new THREE.PerspectiveCamera(),
  gl:{domElement:document.createElement('canvas')}})}));
vi.mock('3d-tiles-renderer/r3f',()=>({TilesRendererContext:createContext(null),
  EastNorthUpFrame:({children,lon}:{children:React.ReactNode;lon:number})=><div data-frame-longitude={lon}>{children}</div>}));
vi.mock('@react-three/drei',()=>({Html:({children}:{children:React.ReactNode})=>children}));
afterEach(()=>{cleanup();vi.restoreAllMocks();});

it.each([
  ['claude_trial_brick_podium_condo_tower', 0],
  ['clay_vancouver_balcony_podium_tower', 4],
] as const)('only offers supported footprint handles for %s', (id, count) => {
  const asset = placeAsset(id);
  const zone = {id:'tower', zone_type:'building', properties:placementProperties(asset),
    coordinates:rectangleAt([-114,51],asset.width,asset.depth)} as SiteZone;
  render(<GlobeDragProvider value={{current:{zoneId:null,type:null,vertexIndex:-1,coords:[],version:0}}}>
    <GlobeEditMode zone={zone} terrainHeight={0} onZoneUpdated={vi.fn()}/>
  </GlobeDragProvider>);
  expect(screen.queryAllByTitle(/^Drag corner/)).toHaveLength(count);
  expect(screen.getByRole('button',{name:'Move selected object'})).toBeTruthy();
  expect(screen.getByTitle('Drag to rotate building')).toBeTruthy();
});

it.each([true,false])('only renders resize vertices when the object can resize (fixed=%s)',fixed=>{
  const zone={id:'selected',zone_type:'building',coordinates:rectangleAt([-114,51],13,16),
    properties:fixed?{validation_fixed_fixture:true}:{}} as SiteZone;
  render(<GlobeDragProvider value={{current:{zoneId:null,type:null,vertexIndex:-1,coords:[],version:0}}}>
    <GlobeEditMode zone={zone} terrainHeight={0} onZoneUpdated={vi.fn()}/>
  </GlobeDragProvider>);
  expect(screen.queryAllByTitle(/^Drag corner/)).toHaveLength(fixed?0:4);
  expect(screen.getByRole('button',{name:'Move selected object'})).toBeTruthy();
  expect(screen.getByTitle('Drag to rotate building')).toBeTruthy();
});

it.each(['none','revision','selection'] as const)('reconciles saved handles and undo/redo with an intervening %s change',changeDuringDrag=>{
  const original=rectangleAt([-114,51],13,16);
  const zone={id:'selected',zone_type:'building',coordinates:original,properties:{},updated_at:'before'} as SiteZone;
  const onZoneUpdated=vi.fn();
  const dragState={current:{zoneId:null,type:null,vertexIndex:-1,coords:[],version:0}};
  const view=(value:SiteZone)=><GlobeDragProvider value={dragState}>
    <GlobeEditMode zone={value} terrainHeight={0} onZoneUpdated={onZoneUpdated}/>
  </GlobeDragProvider>;
  const {rerender}=render(view(zone));
  let pointerLongitude=-114;
  vi.spyOn(Ellipsoid.prototype,'intersectRay').mockImplementation((_ray,target)=>{
    WGS84_ELLIPSOID.getCartographicToPosition(51*Math.PI/180,pointerLongitude*Math.PI/180,0,target);
    return target;
  });
  fireEvent(screen.getByRole('button',{name:'Move selected object'}),new MouseEvent('pointerdown',{bubbles:true,button:0,clientX:20,clientY:20}));
  pointerLongitude=-113.999;
  fireEvent(window,new MouseEvent('pointermove',{clientX:40,clientY:20}));
  if (changeDuringDrag==='revision') rerender(view({...zone,updated_at:'3D finished during drag'}));
  if (changeDuringDrag==='selection') rerender(view({...zone,id:'other',coordinates:rectangleAt([-114.002,51],13,16)}));
  fireEvent(window,new MouseEvent('pointerup'));
  const handleLongitude=()=>Number(screen.getByRole('button',{name:'Move selected object'}).closest('[data-frame-longitude]')?.getAttribute('data-frame-longitude'))*180/Math.PI;
  expect(handleLongitude()).toBeCloseTo(changeDuringDrag==='selection'?-114.002:-113.999,6);
  expect(onZoneUpdated).toHaveBeenCalledOnce();
  expect(onZoneUpdated.mock.calls[0][0]).toBe(zone.id);
  const requested=onZoneUpdated.mock.calls[0][1] as number[][];
  // The save path can apply another site-edge snap before confirming the edit.
  const saved=requested.map(([lng,lat])=>[lng+0.0002,lat]);
  rerender(view({...zone,coordinates:saved,updated_at:'saved'}));
  expect(handleLongitude()).toBeCloseTo(-113.9988,6);
  rerender(view({...zone,updated_at:'undo'}));
  expect(handleLongitude()).toBeCloseTo(-114,6);
  rerender(view({...zone,coordinates:saved,updated_at:'redo'}));
  expect(handleLongitude()).toBeCloseTo(-113.9988,6);
});
