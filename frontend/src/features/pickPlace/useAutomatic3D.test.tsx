import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import type { SiteZone } from '@/types';
import { compileMixedCommunity3D } from '@/features/legoAssembly/communityCompiler';
import { siteZonesApi } from '@/services/api';
import { authoredPlacementKey, useAutomatic3D } from './useAutomatic3D';
import { nativeParkLayouts, nativeParkProperties } from '@/features/parks/nativeParkRegistry';
import { rectangleAt } from './geometry';
vi.mock('@/features/legoAssembly/communityCompiler',()=>({compileMixedCommunity3D:vi.fn()}));
vi.mock('@/services/api',()=>({siteZonesApi:{list:vi.fn()},getApiErrorMessage:(e:Error)=>e.message}));
vi.mock('@/store/undoActions',()=>({advanceDerivedZoneRevision:vi.fn()}));
const zone=(x=0,compiled=false):SiteZone=>({id:'zone',project_id:'p',zone_type:'building',color:'#777777',sort_order:0,created_at:'r1',updated_at:'r1',coordinates:[[x,0],[x+1,0],[x+1,1],[x,1]],properties:{pick_place_asset:'validation_minimalist_infill_brick_monolith',...(compiled?{community_3d:{schema_version:1,state:'compiled',kind:'building',generator:'lego_assembly',compiled_at:'now',source_hash:'a'.repeat(64),representation_hash:'b'.repeat(64)}}:{})}});
const boundary=(state:'compiled'|'stale'):SiteZone=>({id:'boundary',project_id:'p',zone_type:'site_boundary',color:'#777777',sort_order:1,created_at:'r1',updated_at:'r1',coordinates:[[0,0],[4,0],[4,4],[0,4]],properties:{community_3d_landscape:{schema_version:1,state,boundary_id:'boundary',source_hash:'c'.repeat(64)}}});
const wrapper=({children}:{children:ReactNode})=><QueryClientProvider client={new QueryClient({defaultOptions:{queries:{retry:false}}})}>{children}</QueryClientProvider>;
const advance=()=>act(async()=>{await vi.advanceTimersByTimeAsync(750)});
describe('automatic placement compilation',()=>{
  beforeEach(()=>{vi.useFakeTimers();vi.clearAllMocks();vi.mocked(siteZonesApi.list).mockResolvedValue([zone(0,true)]);vi.mocked(compileMixedCommunity3D).mockResolvedValue({plannedMasses:0} as never)});
  afterEach(()=>{vi.useRealTimers()});
  it('rejects late asset errors after a native layout change or deletion',()=>{
    const native=nativeParkLayouts.find(p=>p.id==='basketball_court_v1--native-v1')!;
    const long=nativeParkLayouts.find(p=>p.id==='basketball_court_v1--long-v1')!;
    const coordinates=rectangleAt([-114,51],100,50);
    const park={...zone(),zone_type:'green_space',coordinates,properties:{...nativeParkProperties({},native,coordinates),pick_place_asset:'native-park:basketball_court_v1--native-v1'}} as SiteZone;
    const changed={...park,properties:nativeParkProperties(park.properties!,long,coordinates)};
    const error=(source:SiteZone)=>act(()=>window.dispatchEvent(new CustomEvent('cityprompt:native-park-error',{detail:{zoneId:source.id,revision:JSON.stringify(source.properties?.green_space_native_layout),message:'Failed model'}})));
    const {result,rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,true),{initialProps:{zones:[park]},wrapper});
    error(park);expect(result.current.status).toBe('error');
    rerender({zones:[changed]});expect(result.current.status).not.toBe('error');
    error(park);expect(result.current.status).not.toBe('error');
    error(changed);expect(result.current.status).toBe('error');
    rerender({zones:[]});error(changed);expect(result.current.status).not.toBe('error');
    unmount();
  });
  it('offers asset recovery even when compilation is already saved',async()=>{
    const {result,unmount}=renderHook(()=>useAutomatic3D('p',[zone(0,true)],false),{wrapper});
    await advance();expect(result.current.status).toBe('ready');
    act(()=>window.dispatchEvent(new CustomEvent('cityprompt:native-park-error',{detail:{zoneId:'zone',revision:'null',message:'The park model could not be verified. Retry 3D update.'}})));
    expect(result.current.status).toBe('error');expect(result.current.message).toContain('Retry 3D update');
    act(()=>result.current.retry());await advance();expect(result.current.status).toBe('ready');
    unmount();
  });
  it('keeps asset recovery visible when an in-flight compilation finishes',async()=>{
    let finish!:()=>void;
    vi.mocked(compileMixedCommunity3D).mockImplementationOnce(()=>new Promise(resolve=>{finish=()=>resolve({plannedMasses:0} as never)}));
    const {result,rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false),{initialProps:{zones:[zone()]},wrapper});
    await advance();
    act(()=>window.dispatchEvent(new CustomEvent('cityprompt:native-park-error',{detail:{zoneId:'zone',revision:'null',message:'Retry 3D update'}})));
    await act(async()=>{finish()});await advance();
    expect(result.current.status).toBe('error');
    rerender({zones:[]});expect(result.current.status).not.toBe('error');
    unmount();
  });
  it('coalesces native layout/frame changes and excludes derived recipe metadata from its trigger',async()=>{
    const native=nativeParkLayouts.find(p=>p.id==='basketball_court_v1--native-v1')!;
    const long=nativeParkLayouts.find(p=>p.id==='basketball_court_v1--long-v1')!;
    const coordinates=rectangleAt([-114.05,51.04],100,60);
    const park={...zone(),zone_type:'green_space',coordinates,properties:{...nativeParkProperties({},native,coordinates),pick_place_asset:'native-park:basketball_court_v1--native-v1'}} as SiteZone;
    const edited={...park,properties:{...nativeParkProperties(park.properties!,long,coordinates)}};
    const {rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false),{initialProps:{zones:[park]},wrapper});
    rerender({zones:[edited]});await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    expect(vi.mocked(compileMixedCommunity3D).mock.calls[0][0][0].properties?.green_space_native_layout).toEqual(edited.properties.green_space_native_layout);
    const {authoredPlacementKey}=await import('./useAutomatic3D');
    expect(authoredPlacementKey([edited])).toBe(authoredPlacementKey([{...edited,properties:{...edited.properties,public_realm_lego:{recipe_hash:'a'.repeat(64)}}}]));
    expect(authoredPlacementKey([edited])).not.toBe(authoredPlacementKey([park]));
    unmount();
  });
  it('includes drawn water in the server-verified scope and rebuilds after a water edit',async()=>{
    const water={...zone(),id:'water',zone_type:'water',properties:{},coordinates:[[0,0],[1,0],[1,1],[0,1]]} as SiteZone;
    vi.mocked(siteZonesApi.list).mockResolvedValue([zone(0,true),water]);
    const {rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false),{
      initialProps:{zones:[zone(),water]},wrapper,
    });
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledWith([zone()],undefined,{
      includeResidualLandscape:true,scopeZoneIds:['zone','water'],
    });
    const movedWater={...water,coordinates:[[2,0],[3,0],[3,1],[2,1]]};
    rerender({zones:[zone(),movedWater]});
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledTimes(2);
    unmount();
  });
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
  it('silently supersedes a failed in-flight request when a newer authored edit is waiting',async()=>{
    let fail!:()=>void;
    vi.mocked(compileMixedCommunity3D).mockImplementationOnce(()=>new Promise((_resolve,reject)=>{fail=()=>reject(new Error('stale source'));}));
    const {result,rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false),{initialProps:{zones:[zone()]},wrapper});
    await advance();
    rerender({zones:[zone(2)]});
    await act(async()=>{fail()});
    expect(result.current.status).toBe('updating');
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledTimes(2);
    expect(vi.mocked(compileMixedCommunity3D).mock.calls[1][0][0].coordinates[0][0]).toBe(2);
    expect(result.current.status).not.toBe('error');
    unmount();
  });
  it('treats a footprint-only scale change as an authored 3D change',()=>{
    const original={...zone(),properties:{...zone().properties,building_footprint_scale:1}};
    const scaled={...original,properties:{...original.properties,building_footprint_scale:1.15}};
    expect(authoredPlacementKey([scaled])).not.toBe(authoredPlacementKey([original]));
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
  it('keeps runtime building entrance edits and Undo from recompiling the saved native house',async()=>{
    const saved=zone(0,true);
    const {rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false),{initialProps:{zones:[saved]},wrapper});
    await advance();
    const edited={...saved,properties:{...saved.properties,pedestrian_building_entrance:{version:1,widthM:1.2}}};
    rerender({zones:[edited]});await advance();
    rerender({zones:[saved]});await advance();
    expect(compileMixedCommunity3D).not.toHaveBeenCalled();
    rerender({zones:[{...edited,coordinates:zone(2).coordinates}]});await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();unmount();
  });
  it('rebuilds a moved fixed fixture and its stale site landscape together',async()=>{
    const fixture={...zone(1),zone_type:'green_space',properties:{pick_place_asset:'validation_sculpture_garden_v0',validation_fixed_fixture:true}} as SiteZone;
    vi.mocked(siteZonesApi.list).mockResolvedValue([zone(1,true),boundary('compiled')]);
    const {rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false),{
      initialProps:{zones:[fixture,boundary('stale')]},wrapper,
    });
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledWith([fixture],undefined,{
      includeResidualLandscape:true,scopeZoneIds:['zone'],
    });
    rerender({zones:[{...fixture,properties:{...fixture.properties,community_3d:{schema_version:1,state:'compiled',kind:'park',generator:'park_kit',compiled_at:'now',source_hash:'a'.repeat(64),representation_hash:'b'.repeat(64)}}},boundary('compiled')]});
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    unmount();
  });
  it('refreshes a stale landscape even when all physical models are current',async()=>{
    const saved=zone(0,true);
    vi.mocked(siteZonesApi.list).mockResolvedValue([saved,boundary('compiled')]);
    const {unmount}=renderHook(()=>useAutomatic3D('p',[saved,boundary('stale')],false),{wrapper});
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    unmount();
  });
});
