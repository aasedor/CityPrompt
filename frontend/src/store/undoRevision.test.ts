import { beforeEach, describe, expect, it, vi } from 'vitest';
import { QueryClient } from '@tanstack/react-query';
import { siteZonesApi } from '@/services/api';
import { createZoneUpdateAction, createZoneCreateAction, createZoneDeleteAction, createZoneCoordinatesAction, advanceDerivedZoneRevision } from './undoActions';
import type { SiteZone } from '@/types';
import { CALGARY_LOCAL_PLACEMENT } from '@/features/pickPlace/streetPlacement';
import { bufferLineToPolygon, extractCenterline } from '@/utils/roadGeometry';
import { measureParkTerrain, readParkTerrain } from '@/components/viewer/globe/parkTerrain';
import { createSharedSiteGroundLayout } from '@/components/viewer/globe/sharedSiteGround';
import { rectangleAt } from '@/features/pickPlace/geometry';

vi.mock('@/services/api', () => ({ siteZonesApi: { create: vi.fn(), update: vi.fn(), delete: vi.fn() }, buildingsApi: {} }));
describe('zone undo revision checks', () => {
  it('restores street type, width, centreline and footprint together', async () => {
    const client = new QueryClient(), line = [[-114, 51], [-113.999, 51]];
    const before = { coordinates: bufferLineToPolygon(line, 16), properties: { width: 16, road_archetype_id: 'calgary_local', plan_centerline: line } };
    const after = { coordinates: bufferLineToPolygon(line, 20), properties: { width: 20, road_archetype_id: 'calgary_collector', plan_centerline: line } };
    const action = createZoneUpdateAction('project', 'street', before, after, client, 'r1');
    vi.mocked(siteZonesApi.update).mockResolvedValueOnce({ updated_at: 'r2' } as SiteZone).mockResolvedValueOnce({ updated_at: 'r3' } as SiteZone);
    await action.undo(); await action.redo();
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(1, 'street', { ...before, expected_updated_at: 'r1' }, { skipHistory: true });
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(2, 'street', { ...after, expected_updated_at: 'r2' }, { skipHistory: true });
  });
  it('restores each park outline with its own measured ground through undo and redo', async () => {
    const client=new QueryClient(), center:[number,number]=[-114,51];
    const original={id:'park',project_id:'project',zone_type:'green_space',coordinates:rectangleAt(center,70,60),properties:{name:'keep'},updated_at:'r0'} as unknown as SiteZone;
    const layout=createSharedSiteGroundLayout({...original,id:'site',zone_type:'site_boundary',is_active_boundary:true,coordinates:rectangleAt(center,80,70),properties:{terrain_elevation_m:1000}})!;
    const heights=Array(layout.grid.columns*layout.grid.rows).fill(1000);
    const review={layout,heights,previousHeights:heights};
    const before={...original,properties:{...original.properties,park_terrain:measureParkTerrain(original,review)!}};
    const small={...original,coordinates:rectangleAt(center,30,30),updated_at:'r2'};
    const after={...small,properties:{name:'latest',park_terrain:measureParkTerrain(small,review)!}};
    expect(readParkTerrain(before)).not.toBeNull();
    expect(readParkTerrain(after)).not.toBeNull();
    const action=createZoneCoordinatesAction('project','park',before.coordinates,after.coordinates,client,'r1',before);
    advanceDerivedZoneRevision(client,'project','park','r1','r2');
    client.setQueryData(['site-zones','project'],[after]);
    vi.mocked(siteZonesApi.update).mockImplementation(async(_id,data)=>{
      const saved={...original,...data,updated_at:data.expected_updated_at==='r2'?'r3':'r4'} as SiteZone;
      client.setQueryData(['site-zones','project'],[saved]);
      return saved;
    });
    await action.undo();
    let saved=client.getQueryData<SiteZone[]>(['site-zones','project'])![0];
    expect(saved.coordinates).toEqual(before.coordinates);
    expect(saved.properties?.name).toBe('latest');
    expect(readParkTerrain(saved)?.signature).toBe(readParkTerrain(before)?.signature);
    await action.redo();
    saved=client.getQueryData<SiteZone[]>(['site-zones','project'])![0];
    expect(saved.coordinates).toEqual(after.coordinates);
    expect(readParkTerrain(saved)?.signature).toBe(readParkTerrain(after)?.signature);
  });
  it('undoes and redoes a native street route and its centreline in the same revision-checked request',async()=>{
    const client=new QueryClient();
    const before=bufferLineToPolygon([[-114,51],[-113.999,51]],16);
    const after=before.map(([x,y])=>[x,y+.0002]);
    client.setQueryData(['site-zones','project'],[{id:'zone',zone_type:'road',properties:CALGARY_LOCAL_PLACEMENT.properties}]);
    const action=createZoneCoordinatesAction('project','zone',before,after,client,'r1');
    vi.mocked(siteZonesApi.update).mockResolvedValueOnce({updated_at:'r2'} as SiteZone).mockResolvedValueOnce({updated_at:'r3'} as SiteZone);
    await action.undo();await action.redo();
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(1,'zone',expect.objectContaining({coordinates:before,expected_updated_at:'r1',properties:expect.objectContaining({plan_centerline:extractCenterline(before),width:16})}),{skipHistory:true});
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(2,'zone',expect.objectContaining({coordinates:after,expected_updated_at:'r2',properties:expect.objectContaining({plan_centerline:extractCenterline(after),width:16})}),{skipHistory:true});
  });
  it('accepts our derived compile revision but not a compile over a teammate edit', async () => {
    const client = new QueryClient();
    const action = createZoneCoordinatesAction('project','zone',[[1,2]],[[3,4]],client,'ours');
    advanceDerivedZoneRevision(client,'project','zone','teammate','foreign-compile');
    advanceDerivedZoneRevision(client,'project','zone','ours','our-compile');
    vi.mocked(siteZonesApi.update).mockResolvedValue({updated_at:'undone'} as SiteZone);
    await action.undo();
    expect(siteZonesApi.update).toHaveBeenCalledWith('zone',{coordinates:[[1,2]],expected_updated_at:'our-compile'},{skipHistory:true});
  });
  beforeEach(() => vi.clearAllMocks());
  it('follows revisions produced by successive local undos', async () => {
    const client = new QueryClient();
    const first = createZoneUpdateAction('project', 'zone', { name: 'A' }, { name: 'B' }, client, 'r2');
    const second = createZoneUpdateAction('project', 'zone', { name: 'B' }, { name: 'C' }, client, 'r3');
    vi.mocked(siteZonesApi.update).mockResolvedValueOnce({ updated_at: 'r4' } as SiteZone).mockResolvedValueOnce({ updated_at: 'r5' } as SiteZone);
    await second.undo();
    await first.undo();
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(1, 'zone', { name: 'B', expected_updated_at: 'r3' }, { skipHistory: true });
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(2, 'zone', { name: 'A', expected_updated_at: 'r4' }, { skipHistory: true });
  });
  it('does not adopt a teammate revision from a background refetch', async () => {
    const client = new QueryClient();
    const action = createZoneUpdateAction('project', 'zone', { name: 'A' }, { name: 'B' }, client, 'ours');
    client.setQueryData(['site-zones', 'project'], [{ id: 'zone', updated_at: 'teammate' }]);
    vi.mocked(siteZonesApi.update).mockRejectedValueOnce(new Error('Conflict'));
    await expect(action.undo()).rejects.toThrow('Conflict');
    expect(siteZonesApi.update).toHaveBeenCalledWith('zone', { name: 'A', expected_updated_at: 'ours' }, { skipHistory: true });
  });
  it('checks the saved revision before undoing a creation by deletion', async () => {
    const action = createZoneCreateAction('project', { id: 'zone', updated_at: 'created' } as SiteZone, new QueryClient());
    await action.undo();
    expect(siteZonesApi.delete).toHaveBeenCalledWith('zone', 'created', { skipHistory: true });
  });

  it.each(['create', 'delete'] as const)('keeps %s undo and redo history suppression on each request', async (kind) => {
    const original = { id: 'zone', updated_at: 'r1' } as SiteZone;
    const client = new QueryClient();
    const action = kind === 'create'
      ? createZoneCreateAction('project', original, client)
      : createZoneDeleteAction('project', original, client);
    vi.mocked(siteZonesApi.create).mockResolvedValue({ id: 'recreated', updated_at: 'r2' } as SiteZone);
    await action.undo();
    await action.redo();
    expect(siteZonesApi.create).toHaveBeenCalledWith('project', expect.any(Object), { skipHistory: true });
    expect(siteZonesApi.delete).toHaveBeenCalledWith(expect.any(String), expect.any(String), { skipHistory: true });
  });

  it('keeps coordinate undo/redo revisions and request history options together', async () => {
    const action = createZoneCoordinatesAction('project', 'zone', [[1, 2]], [[3, 4]], new QueryClient(), 'r1');
    vi.mocked(siteZonesApi.update).mockResolvedValueOnce({ updated_at: 'r2' } as SiteZone).mockResolvedValueOnce({ updated_at: 'r3' } as SiteZone);
    await action.undo();
    await action.redo();
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(1, 'zone', { coordinates: [[1, 2]], expected_updated_at: 'r1' }, { skipHistory: true });
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(2, 'zone', { coordinates: [[3, 4]], expected_updated_at: 'r2' }, { skipHistory: true });
  });
});
