import {createContext} from 'react';
import {render, screen, cleanup} from '@testing-library/react';
import {afterEach, expect, it, vi} from 'vitest';
import * as THREE from 'three';
import type {SiteZone} from '@/types';
import {GlobeEditMode} from './GlobeEditMode';
import {GlobeDragProvider} from './useGlobeDragRef';
import {rectangleAt} from '@/features/pickPlace/geometry';

vi.mock('@react-three/fiber',()=>({useThree:()=>({camera:new THREE.PerspectiveCamera(),
  gl:{domElement:document.createElement('canvas')}})}));
vi.mock('3d-tiles-renderer/r3f',()=>({TilesRendererContext:createContext(null),
  EastNorthUpFrame:({children}:{children:React.ReactNode})=>children}));
vi.mock('@react-three/drei',()=>({Html:({children}:{children:React.ReactNode})=>children}));
afterEach(cleanup);

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
