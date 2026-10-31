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
import { advanceDerivedZoneRevision } from '@/store/undoActions';
import streetRecipes from '@/components/viewer/globe/__fixtures__/classroomStreetRecipes.json';
import { placeAsset, placementProperties } from './catalogue';
vi.mock('@/features/legoAssembly/communityCompiler',()=>({compileMixedCommunity3D:vi.fn()}));
vi.mock('@/services/api',()=>({siteZonesApi:{list:vi.fn()},getApiErrorMessage:(e:Error)=>e.message}));
vi.mock('@/store/undoActions',()=>({advanceDerivedZoneRevision:vi.fn()}));
const zone=(x=0,compiled=false):SiteZone=>({id:'zone',project_id:'p',zone_type:'building',color:'#777777',sort_order:0,created_at:'r1',updated_at:'r1',coordinates:[[x,0],[x+1,0],[x+1,1],[x,1]],properties:{pick_place_asset:'validation_minimalist_infill_brick_monolith',...(compiled?{community_3d:{schema_version:1,state:'compiled',kind:'building',generator:'lego_assembly',compiled_at:'now',source_hash:'a'.repeat(64),representation_hash:'b'.repeat(64)}}:{})}});
const boundary=(state:'compiled'|'stale'):SiteZone=>({id:'boundary',project_id:'p',zone_type:'site_boundary',color:'#777777',sort_order:1,created_at:'r1',updated_at:'r1',coordinates:[[0,0],[4,0],[4,4],[0,4]],properties:{community_3d_landscape:{schema_version:1,state,boundary_id:'boundary',source_hash:'c'.repeat(64)}}});
const wrapper=({children}:{children:ReactNode})=><QueryClientProvider client={new QueryClient({defaultOptions:{queries:{retry:false}}})}>{children}</QueryClientProvider>;
const advance=()=>act(async()=>{await vi.advanceTimersByTimeAsync(750)});
describe('automatic placement compilation',()=>{
  it('upgrades an older saved massing recipe once when its exact catalogue model is installed',async()=>{
    const asset=placeAsset('clay_vancouver_balcony_podium_tower');
    const saved=zone(0,true);
    const massing={...saved,properties:{...placementProperties(asset),community_3d:{
      schema_version:1,state:'compiled',kind:'building',generator:'planned_massing',compiled_at:'now',source_hash:'a'.repeat(64),representation_hash:'b'.repeat(64),
    }}} as SiteZone;
    vi.mocked(siteZonesApi.list).mockResolvedValue([massing]);
    const {unmount}=renderHook(()=>useAutomatic3D('p',[massing],false),{wrapper});
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    unmount();
  });
  it('surfaces a failed detailed building and lets Retry restart its loader',async()=>{
    const saved=zone(0,true);
    const {result,unmount}=renderHook(()=>useAutomatic3D('p',[saved],false),{wrapper});
    await advance();
    const retried=vi.fn(); window.addEventListener('cityprompt:retry-native-buildings',retried);
    act(()=>window.dispatchEvent(new CustomEvent('cityprompt:native-building-error',{detail:{
      zoneId:saved.id,revision:JSON.stringify([saved.updated_at,saved.properties?.pick_place_model_revision ?? null]),message:'Building model interrupted. Retry 3D update.',
    }})));
    expect(result.current.status).toBe('error');
    expect(result.current.message).toMatch(/Building model interrupted/);
    act(()=>result.current.retry());
    expect(retried).toHaveBeenCalledOnce();
    window.removeEventListener('cityprompt:retry-native-buildings',retried);unmount();
  });
  it('clears a failed added object after undo restores the already compiled scene',async()=>{
    const ready=zone(0,true);
    const broken={...zone(2),id:'broken'};
    const {result,rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false),{
      initialProps:{zones:[ready]},wrapper,
    });
    await advance();
    vi.mocked(compileMixedCommunity3D).mockRejectedValueOnce(new Error('Unsupported street'));
    rerender({zones:[ready,broken]});await advance();
    expect(result.current.status).toBe('error');
    rerender({zones:[ready]});await advance();
    expect(result.current.status).toBe('ready');
    expect(result.current.message).not.toContain('Unsupported street');
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    unmount();
  });
  it('clears a failed update when the last physical object is removed',async()=>{
    vi.mocked(compileMixedCommunity3D).mockRejectedValueOnce(new Error('Unsupported street'));
    const {result,rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false),{
      initialProps:{zones:[zone()]},wrapper,
    });
    await advance();expect(result.current.status).toBe('error');
    rerender({zones:[]});await advance();
    expect(result.current.status).toBe('idle');
    expect(result.current.busy).toBe(false);
    expect(result.current.message).toBe('');
    unmount();
  });
  it('does not strand an empty scene updating after an obsolete request completes',async()=>{
    let finish!:()=>void;
    vi.mocked(compileMixedCommunity3D).mockImplementationOnce(()=>new Promise(resolve=>{
      finish=()=>resolve({plannedMasses:0} as never);
    }));
    const {result,rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false),{
      initialProps:{zones:[zone()]},wrapper,
    });
    await advance();rerender({zones:[]});
    vi.mocked(siteZonesApi.list).mockResolvedValue([]);
    await act(async()=>{finish()});await advance();
    expect(result.current.status).toBe('idle');
    expect(result.current.busy).toBe(false);
    unmount();
  });
  it.each([false, true])('ignores a rejected temporary boundary with saved boundary=%s', async hasSavedBoundary => {
    const saved = [zone(0, true), ...(hasSavedBoundary ? [boundary('compiled')] : [])];
    const draft = {...boundary('stale'), id:'temp-rejected', is_active_boundary:true,
      coordinates:[[0,0],[4,4],[0,4],[4,0]]} as SiteZone;
    vi.mocked(siteZonesApi.list).mockResolvedValue(saved);
    const {result,rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false), {
      initialProps:{zones:saved},wrapper,
    });
    await advance();
    rerender({zones:[...saved,draft]});
    await act(async()=>{await vi.advanceTimersByTimeAsync(60_000)});
    expect(compileMixedCommunity3D).not.toHaveBeenCalled();
    expect(result.current.status).toBe('ready');
    unmount();
  });
  it('rebuilds once when a boundary draft becomes persisted',async()=>{
    const draft={...boundary('stale'),id:'temp-boundary'};
    const saved=zone(0,true);
    vi.mocked(siteZonesApi.list).mockResolvedValue([saved,boundary('compiled')]);
    const {rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false),{
      initialProps:{zones:[saved,draft]},wrapper,
    });
    await advance();expect(compileMixedCommunity3D).not.toHaveBeenCalled();
    rerender({zones:[saved,boundary('stale')]});await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    rerender({zones:[saved,boundary('compiled')]});await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();unmount();
  });
  it('leaves a new site without automatic trees and respects saved opt-in after reload',async()=>{
    const bare={...boundary('compiled'),properties:{}};
    const off={...bare,properties:{community_3d_landscape_mode:'placed_objects_only'}};
    vi.mocked(siteZonesApi.list).mockResolvedValue([zone(0,true),off]);
    const view=renderHook(({zones})=>useAutomatic3D('p',zones,false),{initialProps:{zones:[zone(),bare]},wrapper});
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenLastCalledWith([zone()],undefined,expect.objectContaining({includeResidualLandscape:false}));
    view.rerender({zones:[zone(0,true),off]});await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    const on={...bare,updated_at:'on-revision',properties:{community_3d_automatic_trees:true,community_3d_landscape_mode:'automatic'}};
    const ready={...boundary('compiled'),updated_at:'compiled-revision',properties:{...boundary('compiled').properties,community_3d_automatic_trees:true}};
    vi.mocked(siteZonesApi.list).mockResolvedValue([zone(0,true),ready]);
    view.rerender({zones:[zone(0,true),on]});await advance();
    expect(compileMixedCommunity3D).toHaveBeenLastCalledWith([zone(0,true)],undefined,expect.objectContaining({includeResidualLandscape:true}));
    expect(advanceDerivedZoneRevision).toHaveBeenCalledWith(expect.anything(),'p','boundary','on-revision','compiled-revision');
    view.rerender({zones:[zone(0,true),ready]});await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledTimes(2);
    view.unmount();
    const reloaded=renderHook(()=>useAutomatic3D('p',[zone(1),ready],false),{wrapper});await advance();
    expect(compileMixedCommunity3D).toHaveBeenLastCalledWith([zone(1)],undefined,expect.objectContaining({includeResidualLandscape:true}));
    reloaded.unmount();
    const disabled={...off,properties:{...off.properties,community_3d_automatic_trees:false}};
    const offReload=renderHook(()=>useAutomatic3D('p',[zone(2),disabled],false),{wrapper});await advance();
    expect(compileMixedCommunity3D).toHaveBeenLastCalledWith([zone(2)],undefined,expect.objectContaining({includeResidualLandscape:false}));
    offReload.unmount();
  });
  it('rebuilds a native street after unchanged Apply removes only its compiled recipe',async()=>{
    const recipe=streetRecipes[0];
    const native:SiteZone={...zone(0,true),zone_type:'road',properties:{
      road_archetype_id:recipe.archetype_id,road_selected_variant_id:recipe.variant_id,
      width:recipe.target.row_width_m,public_realm_lego:recipe,
      community_3d:{schema_version:1,state:'compiled',kind:'street',generator:'street_section',compiled_at:'now',source_hash:'a'.repeat(64),representation_hash:'b'.repeat(64)},
    }};
    const damaged={...native,properties:{...native.properties,public_realm_lego:undefined}};
    expect(authoredPlacementKey([damaged])).toBe(authoredPlacementKey([native]));
    vi.mocked(siteZonesApi.list).mockResolvedValue([native]);
    const view=renderHook(({zones})=>useAutomatic3D('p',zones,false),{initialProps:{zones:[native]},wrapper});
    await advance();expect(compileMixedCommunity3D).not.toHaveBeenCalled();
    view.rerender({zones:[damaged]});await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    view.rerender({zones:[native]});await advance();
    expect(view.result.current.status).toBe('ready');view.unmount();
  });
  it.each(['custom-only', 'mixed'] as const)('prepares a previously uncompiled %s scene without a generation button', async kind => {
    const custom = { ...zone(), id: 'custom', properties: { height: 12, floors: 3 } };
    const zones = kind === 'mixed' ? [custom, zone()] : [custom];
    const view = renderHook(() => useAutomatic3D('p', zones, false), { wrapper });
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledWith(zones, undefined, expect.objectContaining({ scopeMode: 'project', includeResidualLandscape: false }));
    view.unmount();
  });
  it('compiles only the selected scenario even when the query cache contains hidden alternatives', async () => {
    const shown = { ...zone(), id: 'shown', properties: { _imported_from: 'scenario-a' } };
    const hidden = { ...zone(), id: 'hidden', properties: { _imported_from: 'scenario-b' } };
    const client = new QueryClient({defaultOptions:{queries:{retry:false}}});
    client.setQueryData(['site-zones','p'], [shown,hidden]);
    const wrap = ({children}:{children:ReactNode}) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;
    const view = renderHook(() => useAutomatic3D('p', [shown], false, {hiddenLayers: new Set(['scenario-b']), comparingPlans: false}), {wrapper:wrap});
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledWith([shown], undefined, {includeResidualLandscape:false,scopeMode:'selection',scopeZoneIds:['shown']});
    view.unmount();
  });
  it('waits for one scenario when alternatives are being compared', async () => {
    const {result,rerender,unmount} = renderHook(({comparingPlans}) => useAutomatic3D('p',[zone()],false,{hiddenLayers:new Set<string>(),comparingPlans}), {initialProps:{comparingPlans:true},wrapper});
    await advance();
    expect(compileMixedCommunity3D).not.toHaveBeenCalled();
    expect(result.current.message).toContain('one scenario');
    rerender({comparingPlans:false}); await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    unmount();
  });
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
      includeResidualLandscape:false,scopeMode:'project',scopeZoneIds:['zone','water'],
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
  it('stops after successful compilation leaves the saved scene unready', async () => {
    const unfinished={...zone(),name:'Unfinished home'};
    vi.mocked(siteZonesApi.list).mockResolvedValue([unfinished]);
    const {result,unmount} = renderHook(() => useAutomatic3D('p',[unfinished],false), {wrapper});
    await advance(); await advance(); await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    expect(result.current.status).toBe('error');
    expect(result.current.message).toContain('Retry 3D update');
    expect(result.current.message).toContain('Unfinished home');
    unmount();
  });
  it.each([false,true])('invalidates objects and buildings before landscape recovery (previously ready: %s)', async previouslyReady => {
    const generated:SiteZone={...boundary('stale'),properties:{
      ...boundary('stale').properties,community_3d_landscape_mode:'generated',
    }};
    const applied:SiteZone={...generated,properties:{...generated.properties,
      community_3d_landscape:boundary('compiled').properties!.community_3d_landscape,
    }};
    const edited=zone(1),saved=zone(1,true);
    const initialZones=previouslyReady ? [zone(0,true),applied] : [edited,generated];
    const client=new QueryClient({defaultOptions:{queries:{retry:false}}});
    client.setQueryData(['site-zones','p'],initialZones);
    client.setQueryData(['project','p'],{id:'p',buildings:[]});
    const wrap=({children}:{children:ReactNode})=><QueryClientProvider client={client}>{children}</QueryClientProvider>;
    vi.mocked(siteZonesApi.list).mockResolvedValue([saved,generated]);
    const {result,rerender,unmount}=renderHook(({zones})=>useAutomatic3D('p',zones,false),{
      initialProps:{zones:initialZones},wrapper:wrap,
    });
    if(previouslyReady){
      await advance();
      expect(result.current.status).toBe('ready');
      expect(compileMixedCommunity3D).not.toHaveBeenCalled();
      client.setQueryData(['site-zones','p'],[edited,generated]);
      rerender({zones:[edited,generated]});
    }
    await advance();
    expect(result.current.status).toBe('error');
    expect(client.getQueryData(['site-zones','p'])).toEqual([saved,generated]);
    expect(client.getQueryState(['site-zones','p'])?.isInvalidated).toBe(true);
    expect(client.getQueryState(['project','p'])?.isInvalidated).toBe(true);
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();

    client.setQueryData(['site-zones','p'],[saved,applied]);
    rerender({zones:[saved,applied]});
    await advance();
    expect(result.current.status).toBe('ready');
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    unmount();
  });
  it.each(['plaza_archetype_id', 'generation_style_inputs'])('retries a failed custom plaza when %s changes', async field => {
    vi.mocked(compileMixedCommunity3D).mockRejectedValueOnce(new Error('bad archetype'));
    const plaza = {...zone(),zone_type:'parking',properties:{[field]:'old'}} as SiteZone;
    const {result,rerender,unmount} = renderHook(({zones}) => useAutomatic3D('p',zones,false), {initialProps:{zones:[plaza]},wrapper});
    await advance(); expect(result.current.status).toBe('error');
    rerender({zones:[{...plaza,properties:{[field]:'new'}}]}); await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledTimes(2);
    unmount();
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
  it('refreshes saved design massing only when explicitly requested',async()=>{
    const saved=zone(0,true);
    const massing={...saved,properties:{...saved.properties,pick_place_model_revision:'unavailable-saved-revision',community_3d:{
      schema_version:1,state:'compiled',kind:'building',generator:'planned_massing',
      compiled_at:'now',source_hash:'a'.repeat(64),representation_hash:'b'.repeat(64),
    }}} as SiteZone;
    const {result,unmount}=renderHook(()=>useAutomatic3D('p',[massing],false),{wrapper});
    await advance();
    expect(result.current.canRefreshDetail).toBe(true);
    expect(compileMixedCommunity3D).not.toHaveBeenCalled();
    act(()=>result.current.retry());
    await advance();
    expect(compileMixedCommunity3D).toHaveBeenCalledOnce();
    unmount();
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
      includeResidualLandscape:true,scopeMode:'project',scopeZoneIds:['zone'],
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
