import { createContext } from 'react';
import { render } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { TileStencilPatcher } from './TileStencilPatcher';
import { TilesRendererContext } from '3d-tiles-renderer/r3f';

vi.mock('3d-tiles-renderer/r3f', () => ({TilesRendererContext:createContext(null)}));
vi.mock('./ParkAssemblyGround', () => ({useParkAssemblyGroundOwners:()=>[]}));

it('keeps a prepared boundary and its outside road in the live tile shader, then removes the road cut', () => {
  const material=new THREE.MeshBasicMaterial(),geometry=new THREE.PlaneGeometry(1,1),mesh=new THREE.Mesh(geometry,material);
  const tiles={forEachLoadedModel:(visit:(scene:THREE.Object3D)=>void)=>visit(mesh),addEventListener:vi.fn(),removeEventListener:vi.fn()};
  const site: SiteZone={id:'site',zone_type:'site_boundary',is_active_boundary:true,project_id:'p',color:'#888',sort_order:0,created_at:'',updated_at:'',
    coordinates:[[0,0],[.001,0],[.001,.001],[0,.001]],properties:{terrain_elevation_m:100}};
  const road={...site,id:'road',zone_type:'road' as const,is_active_boundary:false,
    coordinates:[[.0004,.0005],[.0006,.0005],[.0006,.0012],[.0004,.0012]]};
  const component=(zones:SiteZone[]) => <TilesRendererContext.Provider value={tiles as unknown as NonNullable<React.ContextType<typeof TilesRendererContext>>}>
    <TileStencilPatcher zones={zones} terrainHeight={99}/>
  </TilesRendererContext.Provider>;
  const {rerender,unmount}=render(component([site,road]));
  expect(material.userData.__cityPromptTileSpatialMaskPatch.config.maskCount).toBe(2);
  rerender(component([site]));
  expect(material.userData.__cityPromptTileSpatialMaskPatch.config.maskCount).toBe(1);
  unmount();
  expect(material.userData.__cityPromptTileSpatialMaskPatch).toBeUndefined();
  material.dispose();geometry.dispose();
});
