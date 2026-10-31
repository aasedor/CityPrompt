import { act, cleanup, renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AxiosHeaders, type AxiosResponse } from 'axios';
import type { ReactNode } from 'react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { api } from '@/services/api';
import type { SiteZone } from '@/types';
import type { PublicRoadContext } from './publicRoadSuggestions';
import { usePublicRoadContext } from './usePublicRoadContext';

vi.mock('@/services/api',()=>({api:{get:vi.fn()}}));
const boundary:SiteZone={id:'11111111-1111-4111-8111-111111111111',project_id:'project',zone_type:'site_boundary',
  coordinates:[[-114,51],[-113.999,51],[-113.999,51.001],[-114,51.001]],
  color:'#777777',sort_order:0,created_at:'created',updated_at:'saved',properties:{}};
const context:PublicRoadContext={source:'OpenStreetMap',fetched_at:'now',blockers:[],
  roads:[{id:'osm:way:3',label:'Mapped Road',points:[[-114,51],[-113.999,51]],widthM:6}]};
const response:AxiosResponse<PublicRoadContext>={data:context,status:200,statusText:'OK',headers:{},config:{headers:new AxiosHeaders()}};
const clients:QueryClient[]=[];
function wrapper({children}:{children:ReactNode}) {
  const client=clients[clients.length-1];
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
beforeEach(()=>{
  clients.push(new QueryClient({defaultOptions:{queries:{retry:false,gcTime:Infinity}}}));
  vi.mocked(api.get).mockReset().mockResolvedValue(response);
});
afterEach(()=>{cleanup();clients.forEach(client=>client.clear());clients.length=0;});

it('loads only while requested and only after a boundary has a saved UUID',async()=>{
  const {result,rerender}=renderHook(({zone,enabled})=>usePublicRoadContext(zone,enabled),{
    initialProps:{zone:boundary,enabled:false},wrapper,
  });
  expect(api.get).not.toHaveBeenCalled();
  rerender({zone:{...boundary,id:'temp-new-boundary'},enabled:true});
  expect(api.get).not.toHaveBeenCalled();
  rerender({zone:boundary,enabled:true});
  await waitFor(()=>expect(result.current.data?.roads).toHaveLength(1));
  expect(api.get).toHaveBeenCalledWith(`/api/v1/site-zones/${boundary.id}/public-road-context`,
    expect.objectContaining({signal:expect.any(AbortSignal),timeout:35000}));
});

it('reuses successful cached context and refetches after the boundary shape changes',async()=>{
  const {result,rerender}=renderHook(({zone,enabled})=>usePublicRoadContext(zone,enabled),{
    initialProps:{zone:boundary,enabled:true},wrapper,
  });
  await waitFor(()=>expect(result.current.data?.roads).toHaveLength(1));
  rerender({zone:boundary,enabled:false});rerender({zone:boundary,enabled:true});
  expect(api.get).toHaveBeenCalledTimes(1);
  rerender({zone:{...boundary,coordinates:boundary.coordinates.map(([lng,lat])=>[lng+0.001,lat])},enabled:true});
  await waitFor(()=>expect(api.get).toHaveBeenCalledTimes(2));
});

it('removes stale snap targets on lookup failure and restores real data after retry',async()=>{
  const {result}=renderHook(()=>{
    const query=usePublicRoadContext(boundary,true);
    return {data:query.data,isError:query.isError,refetch:query.refetch};
  },{wrapper});
  await waitFor(()=>expect(result.current.data?.roads).toHaveLength(1));
  vi.mocked(api.get).mockRejectedValueOnce(new Error('Map source unavailable'));
  await act(async()=>{await result.current.refetch();});
  await waitFor(()=>expect(result.current.isError).toBe(true));
  expect(result.current.data).toBeUndefined();
  vi.mocked(api.get).mockResolvedValueOnce(response);
  await act(async()=>{await result.current.refetch();});
  await waitFor(()=>expect(result.current.isError).toBe(false));
  expect(result.current.data?.roads).toHaveLength(1);
});
