import { createContext } from 'react';
import { render } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { TileStencilPatcher } from './TileStencilPatcher';
import { TilesRendererContext } from '3d-tiles-renderer/r3f';
import { readMapCleanupBoxes } from './mapCleanup';

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
  // Opacity reveals context without changing the prepared height or removing
  // independent outside road cuts. Returning to solid reinstates the site cut.
  const translucent = { ...site, properties: { ...site.properties, site_boundary_opacity: 0.45 } };
  rerender(component([translucent, road]));
  expect(material.userData.__cityPromptTileSpatialMaskPatch.config.maskCount).toBe(1);
  rerender(component([translucent]));
  expect(material.userData.__cityPromptTileSpatialMaskPatch).toBeUndefined();
  rerender(component([{ ...translucent, properties: { ...translucent.properties, site_boundary_opacity: 0 } }]));
  expect(material.userData.__cityPromptTileSpatialMaskPatch).toBeUndefined();
  rerender(component([site]));
  expect(material.userData.__cityPromptTileSpatialMaskPatch.config.maskCount).toBe(1);
  unmount();
  expect(material.userData.__cityPromptTileSpatialMaskPatch).toBeUndefined();
  material.dispose();geometry.dispose();
});

it('applies a saved above-ground cleanup to existing and newly loaded Google tiles, then restores both', () => {
  const first = new THREE.MeshBasicMaterial(), second = new THREE.MeshBasicMaterial();
  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const events = new Map<string, (event: { scene: THREE.Object3D }) => void>();
  const tiles = { forEachLoadedModel: (visit: (scene: THREE.Object3D) => void) => visit(new THREE.Mesh(geometry, first)),
    addEventListener: (name: string, handler: (event: { scene: THREE.Object3D }) => void) => events.set(name, handler),
    removeEventListener: (name: string) => events.delete(name) };
  const owner: SiteZone = { id: 'owner', zone_type: 'site_boundary', project_id: 'p', color: '#888', sort_order: 0,
    created_at: '', updated_at: '', coordinates: [[0, 0], [.001, 0], [0, .001]],
    properties: { map_cleanup: { version: 1, boxes: [{ id: 'fragment', lng: 0, lat: 0,
      altitude: 106, width: 4, depth: 4, height: 3, yaw: 0, enabled: true }] } } };
  const component = (assemblyZones: SiteZone[]) => <TilesRendererContext.Provider value={tiles as unknown as NonNullable<React.ContextType<typeof TilesRendererContext>>}>
    <TileStencilPatcher zones={[]} assemblyZones={assemblyZones} cleanupBoxes={readMapCleanupBoxes(assemblyZones)} terrainHeight={100} />
  </TilesRendererContext.Provider>;
  const { rerender, unmount } = render(component([owner]));
  events.get('load-model')!({ scene: new THREE.Mesh(geometry, second) });
  expect(first.userData.__cityPromptTileSpatialMaskPatch.config.cleanupCenters).toHaveLength(1);
  expect(second.userData.__cityPromptTileSpatialMaskPatch.config.cleanupCenters).toHaveLength(1);
  rerender(component([{ ...owner, properties: {} }]));
  expect(first.userData.__cityPromptTileSpatialMaskPatch).toBeUndefined();
  expect(second.userData.__cityPromptTileSpatialMaskPatch).toBeUndefined();
  unmount(); first.dispose(); second.dispose(); geometry.dispose();
});

it('does not apply Google cleanup metadata to an alternate tile provider without explicit opt-in', () => {
  const material = new THREE.MeshBasicMaterial(), geometry = new THREE.BoxGeometry(1, 1, 1);
  const tiles = { forEachLoadedModel: (visit: (scene: THREE.Object3D) => void) => visit(new THREE.Mesh(geometry, material)),
    addEventListener: vi.fn(), removeEventListener: vi.fn() };
  const site: SiteZone = { id: 'alternate-site', project_id: 'p', zone_type: 'site_boundary', color: '#888', sort_order: 0,
    created_at: '', updated_at: '', coordinates: [[0, 0], [.001, 0], [0, .001]], properties: {
      map_cleanup: { version: 1, boxes: [{ id: 'fragment', lng: 0, lat: 0, altitude: 106,
        width: 4, depth: 4, height: 3, yaw: 0, enabled: true }] } } };
  const { unmount } = render(<TilesRendererContext.Provider value={tiles as unknown as NonNullable<React.ContextType<typeof TilesRendererContext>>}>
    <TileStencilPatcher zones={[site]} terrainHeight={100} />
  </TilesRendererContext.Provider>);
  expect(material.userData.__cityPromptTileSpatialMaskPatch.config.cleanupCenters).toHaveLength(0);
  unmount(); material.dispose(); geometry.dispose();
});
