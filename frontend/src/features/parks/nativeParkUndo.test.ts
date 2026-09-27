import { it,expect,vi } from 'vitest';
import { QueryClient } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { siteZonesApi } from '@/services/api';
import { createZoneCoordinatesAction,createZoneUpdateAction } from '@/store/undoActions';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { nativeParkLayouts,nativeParkProperties,nativeParkEditProperties } from './nativeParkRegistry';
vi.mock('@/services/api',()=>({siteZonesApi:{update:vi.fn()},zoneHistoryApi:{restoreSnapshot:vi.fn()},buildingsApi:{}}));
const original=nativeParkLayouts.find(p=>p.id==='basketball_court_v1--native-v1')!;
const long=nativeParkLayouts.find(p=>p.id==='basketball_court_v1--long-v1')!;
const fixture=()=>{
  const coordinates=rectangleAt([-114,51],52,39);
  return {id:'park',zone_type:'green_space',coordinates,properties:nativeParkProperties({},original,coordinates),updated_at:'r0'} as SiteZone;
};
it('restores the exact native placement frame with move undo and redo',async()=>{
  const before=fixture(),coordinates=rectangleAt([-114.001,51.001],52,39,30);
  const after={...before,coordinates,properties:nativeParkEditProperties(before,coordinates),updated_at:'r1'};
  const client=new QueryClient();client.setQueryData(['site-zones','p'],[after]);
  vi.mocked(siteZonesApi.update).mockResolvedValueOnce({...before,updated_at:'r2'}).mockResolvedValueOnce({...after,updated_at:'r3'});
  const action=createZoneCoordinatesAction('p',before.id,before.coordinates,after.coordinates,client,'r1',before,after);
  await action.undo();await action.redo();
  expect(siteZonesApi.update).toHaveBeenNthCalledWith(1,before.id,expect.objectContaining({coordinates:before.coordinates,properties:expect.objectContaining({green_space_native_layout:before.properties?.green_space_native_layout})}),{skipHistory:true});
  expect(siteZonesApi.update).toHaveBeenNthCalledWith(2,before.id,expect.objectContaining({coordinates:after.coordinates,properties:expect.objectContaining({green_space_native_layout:after.properties?.green_space_native_layout})}),{skipHistory:true});
});
it('undoes layout selection and its parcel enlargement in one write',async()=>{
  vi.clearAllMocks();const before=fixture(),coordinates=rectangleAt([-114,51],92,39);
  const after={coordinates,properties:nativeParkProperties(before.properties!,long,coordinates)};
  const client=new QueryClient();vi.mocked(siteZonesApi.update).mockResolvedValue({...before,updated_at:'r2'});
  const action=createZoneUpdateAction('p','park',{coordinates:before.coordinates,properties:before.properties},after,client,'r1');
  await action.undo();expect(siteZonesApi.update).toHaveBeenCalledTimes(1);
  expect(siteZonesApi.update).toHaveBeenCalledWith('park',expect.objectContaining({coordinates:before.coordinates,properties:before.properties}),{skipHistory:true});
});
