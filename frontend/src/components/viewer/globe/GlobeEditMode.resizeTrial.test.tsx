import {createContext} from 'react';
import {render, screen, cleanup} from '@testing-library/react';
import {afterEach, expect, it, vi} from 'vitest';
import * as THREE from 'three';
import type {SiteZone, SiteZoneProperties} from '@/types';
import {GlobeEditMode} from './GlobeEditMode';
import {GlobeDragProvider} from './useGlobeDragRef';
import {rectangleAt} from '@/features/pickPlace/geometry';
import {placeAsset, placementProperties} from '@/features/pickPlace/catalogue';
import {exactModelProperties, resizeTrialFamilyForAsset, shapeFreelyProperties} from '@/features/pickPlace/buildingResizeTrial';

vi.mock('@react-three/fiber',()=>({useThree:()=>({camera:new THREE.PerspectiveCamera(),
  gl:{domElement:document.createElement('canvas')}})}));
vi.mock('3d-tiles-renderer/r3f',()=>({TilesRendererContext:createContext(null),
  EastNorthUpFrame:({children}:{children:React.ReactNode})=><div>{children}</div>}));
vi.mock('@react-three/drei',()=>({Html:({children}:{children:React.ReactNode})=>children}));
afterEach(()=>{cleanup();vi.unstubAllEnvs();});

const asset=()=>placeAsset('final_seniors_apartments');
const corners=(properties:SiteZoneProperties,coordinates:number[][])=>{
  const zone={id:'midrise',zone_type:'building',properties,coordinates} as SiteZone;
  render(<GlobeDragProvider value={{current:{zoneId:null,type:null,vertexIndex:-1,coords:[],version:0}}}>
    <GlobeEditMode zone={zone} terrainHeight={0} onZoneUpdated={vi.fn()}/>
  </GlobeDragProvider>);
  const count=screen.queryAllByTitle(/^Drag corner/).length;
  expect(screen.getByRole('button',{name:'Move selected object'})).toBeTruthy();
  cleanup();
  return count;
};
const plot=rectangleAt([-114,51],36.4,22);
const lShape=[[-114,51],[-113.9993,51],[-113.9993,51.0001],[-113.9996,51.0001],[-113.9996,51.0003],[-114,51.0003]];

it('keeps the mid-rise without corner handles while the pilot flag is off',()=>{
  expect(corners(placementProperties(asset()),plot)).toBe(0);
  // Saved pilot state is inert too: the fixed plot does not become editable.
  vi.stubEnv('VITE_ENABLE_BUILDING_RESIZE_TRIAL','true');
  const stretched=exactModelProperties(placementProperties(asset()),resizeTrialFamilyForAsset(asset())!,1.2,1,asset());
  vi.unstubAllEnvs();
  expect(corners(stretched,plot)).toBe(0);
});

it('offers plot corners for the exact model and every outline corner for Shape freely',()=>{
  vi.stubEnv('VITE_ENABLE_BUILDING_RESIZE_TRIAL','true');
  expect(corners(placementProperties(asset()),plot)).toBe(4);
  expect(corners(shapeFreelyProperties(placementProperties(asset())),lShape)).toBe(6);
  // Another fixed native building gains nothing from the pilot.
  const other=placeAsset('autumn_timber');
  expect(corners(placementProperties(other),rectangleAt([-114,51],other.width,other.depth))).toBe(0);
});
