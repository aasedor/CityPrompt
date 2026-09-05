import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import type { SiteZone } from '@/types';
import { compileMixedCommunity3D } from '@/features/legoAssembly/communityCompiler';
import { siteZonesApi } from '@/services/api';
import { useAutomatic3D } from './useAutomatic3D';
vi.mock('@/features/legoAssembly/communityCompiler',()=>({compileMixedCommunity3D:vi.fn()}));
vi.mock('@/services/api',()=>({siteZonesApi:{list:vi.fn()},getApiErrorMessage:(e:Error)=>e.message}));
vi.mock('@/store/undoActions',()=>({advanceDerivedZoneRevision:vi.fn()}));
const zone=(x=0,compiled=false):SiteZone=>({id:'zone',project_id:'p',zone_type:'building',color:'#777777',sort_order:0,created_at:'r1',updated_at:'r1',coordinates:[[x,0],[x+1,0],[x+1,1],[x,1]],properties:{pick_place_asset:'infill_home',...(compiled?{community_3d:{schema_version:1,state:'compiled',kind:'building',generator:'lego_assembly',compiled_at:'now'}}:{})}});
const wrapper=({children}:{children:ReactNode})=><QueryClientProvider client={new QueryClient({defaultOptions:{queries:{retry:false}}})}>{children}</QueryClientProvider>;
const advance=()=>act(async()=>{await vi.advanceTimersByTimeAsync(750)});
describe('automatic placement compilation',()=>{
  beforeEach(()=>{vi.useFakeTimers();vi.clearAllMocks();vi.mocked(siteZonesApi.list).mockResolvedValue([zone(0,true)]);vi.mocked(compileMixedCommunity3D).mockResolvedValue({plannedMasses:0} as never)});
  afterEach(()=>{vi.useRealTimers()});
  it('debounces changes, waits for saves and does not recompile its own metadata',async()=>{
    const {result,rerender,unmount}=renderHook(({zones,saving})=>useAutomatic3D('p',zones,saving),{initialProps:{zones:[zone()],saving:true},wrapper});
    await advance();expect(compileMixedCommunity3D).not.toHaveBeenCalled();
    rerender({zones:[zone(1)],saving:false});
    rerender({zones:[zone(2)],saving:false});await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledTimes(1);
    expect(vi.mocked(compileMixedCommunity3D).mock.calls[0][0][0].coordinates[0][0]).toBe(2);
    rerender({zones:[zone(2,true)],saving:false});await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledTimes(1);expect(result.current.status).toBe('ready');unmount();
  });
  it('queues the newest edit behind an in-flight request',async()=>{
    let finish!:()=>void;
    vi.mocked(compileMixedCommunity3D).mockImplementationOnce(()=>new Promise(resolve=>{finish=()=>resolve({plannedMasses:0} as never)}));
    const {rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false),{initialProps:{zones:[zone()]},wrapper});
    await advance();rerender({zones:[zone(1)]});rerender({zones:[zone(3)]});await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledTimes(1);
    await act(async()=>{finish()});await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledTimes(2);
    expect(vi.mocked(compileMixedCommunity3D).mock.calls[1][0][0].coordinates[0][0]).toBe(3);unmount();
  });
  it('stops after an error and retries only on request',async()=>{
    vi.mocked(compileMixedCommunity3D).mockRejectedValue(new Error('Offline'));
    const {result,unmount}=renderHook(()=>useAutomatic3D('p',[zone()],false),{wrapper});
    await advance();await advance();expect(compileMixedCommunity3D).toHaveBeenCalledTimes(1);expect(result.current.status).toBe('error');
    act(()=>result.current.retry());await advance();expect(compileMixedCommunity3D).toHaveBeenCalledTimes(2);unmount();
  });
  it('does not compile an already saved project on reopen or when no edit permission exists',async()=>{
    const saved=renderHook(()=>useAutomatic3D('p',[zone(0,true)],false),{wrapper});await advance();saved.unmount();
    const viewer=renderHook(()=>useAutomatic3D(undefined,[zone()],false),{wrapper});await advance();viewer.unmount();
    expect(compileMixedCommunity3D).not.toHaveBeenCalled();
  });
});
