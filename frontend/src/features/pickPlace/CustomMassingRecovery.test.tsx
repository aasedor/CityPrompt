import '@testing-library/jest-dom/vitest';
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import type { Building, SiteZone } from '@/types';
import { legoAssemblyApi, type LegoAssemblyPlan } from '@/features/legoAssembly/legoAssemblyApi';
import { rectangleAt } from './geometry';
import { CustomMassingRecovery } from './CustomMassingRecovery';

vi.mock('@/features/legoAssembly/legoAssemblyApi', async importOriginal => ({
  ...await importOriginal<typeof import('@/features/legoAssembly/legoAssemblyApi')>(),
  legoAssemblyApi: { plan: vi.fn() },
}));
const plan: LegoAssemblyPlan = {version:1,family:'duplex',archetype_id:'infill_duplex',reuse_keys:['infill_duplex'],
  target:{width_m:30,depth_m:14,floors:2},assembled_height_m:7.4,
  instances:[{asset_id:'duplex',asset_name:'Detailed duplex',model_url:'/duplex.glb',family:'duplex',role:'assembled',
    level:0,position:[0,0,0],rotation_degrees:0,scale:[1,1,1],native_dimensions_m:[12,12,7.4]}],
  fit:{scale_x:1,scale_y:1,score:1}};
beforeEach(() => { vi.mocked(legoAssemblyApi.plan).mockReset().mockResolvedValue(plan); });
afterEach(cleanup);
const zone: SiteZone = {id:'saved-zone', project_id:'project', building_id:'saved-building', zone_type:'building',
  color:'#777777',sort_order:0,created_at:'created',
  coordinates:rectangleAt([-114,51],30,14), updated_at:'saved', properties:{
    floors:3, height:9, development_subcategory:'halifax_painted_clapboard_row',
    custom_style_enabled:true, custom_style_prompt:'A new york style brownhouse',
    community_3d:{schema_version:1,state:'compiled',kind:'building',generator:'planned_massing',
      compiled_at:'now',source_hash:'a'.repeat(64),representation_hash:'b'.repeat(64)},
  }};
const building: Building = {id:'saved-building', project_id:'project', floor_count:3, height_meters:9,
  created_at:'now', specifications:{plannedMassing:{floor_count:3,height_meters:9}}};
const chooseDuplex = () => {
  fireEvent.click(screen.getByRole('button',{name:'Choose a detailed building'}));
  fireEvent.change(screen.getByLabelText('Building type'),{target:{value:'building:calgary_modern_infill_house:infill_duplex'}});
  fireEvent.click(screen.getByRole('button',{name:'Apply building'}));
};

it.each([0,0.000001,-0.000001,-0.002])('treats a %s metre plot inset as boundary contact without allowing meaningful spill',async inset=>{
  const saved:SiteZone={...zone,coordinates:rectangleAt([-114,51],12+2*inset,12+2*inset)};
  const onReplace=vi.fn();
  render(<CustomMassingRecovery zone={saved} buildings={[building]} onReplace={onReplace}/>);
  chooseDuplex();
  fireEvent.click(screen.getByRole('button',{name:'Replace custom massing'}));
  if(inset>=-0.000001){
    await waitFor(()=>expect(onReplace).toHaveBeenCalledOnce());
  }else{
    await waitFor(()=>expect(screen.getByRole('alert')).toHaveTextContent(/outside.*saved plot/i));
    expect(onReplace).not.toHaveBeenCalled();
  }
});

it('rejects an edge crossing a narrow concave notch even when every model corner fits',async()=>{
  const east=111320*Math.cos(51*Math.PI/180);
  const saved:SiteZone={...zone,coordinates:[[-6,-6],[6,-6],[6,6],[2.3,6],[2.3,-3],[2.2,-3],[2.2,6],[-6,6]]
    .map(([x,y])=>[-114+x/east,51+y/111320])};
  vi.mocked(legoAssemblyApi.plan).mockResolvedValue({...plan,instances:[{...plan.instances[0],native_dimensions_m:[6,6,7.4]}]});
  const onReplace=vi.fn();
  render(<CustomMassingRecovery zone={saved} buildings={[building]} onReplace={onReplace}/>);
  chooseDuplex();
  fireEvent.click(screen.getByRole('button',{name:'Replace custom massing'}));
  await waitFor(()=>expect(screen.getByRole('alert')).toHaveTextContent(/outside.*saved plot/i));
  expect(onReplace).not.toHaveBeenCalled();
});

it.each([undefined,'halifax_painted_clapboard_row_variant_0'])('requires an explicit exact model when the saved lighting card is %s',async savedVariant=>{
  const saved:SiteZone={...zone,properties:{...zone.properties,
    development_archetype_id:'halifax_painted_clapboard_row_variant_0',
    development_selected_variant_id:savedVariant,
    generation_style_input:{archetypeId:'halifax_painted_clapboard_row_variant_0'},
  }};
  const onReplace=vi.fn();
  render(<CustomMassingRecovery zone={saved} buildings={[building]} onReplace={onReplace}/>);
  fireEvent.click(screen.getByRole('button',{name:'Choose a detailed building'}));
  expect(screen.getByLabelText('Building type')).toHaveValue('');
  fireEvent.change(screen.getByLabelText('Storeys'),{target:{value:'2'}});
  expect(screen.getByRole('button',{name:'Apply building'})).toBeDisabled();
  expect(onReplace).not.toHaveBeenCalled();
  fireEvent.change(screen.getByLabelText('Building type'),{
    target:{value:'building:halifax_painted_clapboard_row:clapboard_north_end'},
  });
  expect(screen.getByLabelText('Building variant')).toHaveValue('clapboard_north_end');
  fireEvent.click(screen.getByRole('button',{name:'Apply building'}));
  await waitFor(()=>expect(screen.getByRole('button',{name:'Replace custom massing'})).toBeEnabled());
  expect(onReplace).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button',{name:'Replace custom massing'}));
  await waitFor(()=>expect(onReplace).toHaveBeenCalledOnce());
  expect(legoAssemblyApi.plan).toHaveBeenLastCalledWith(expect.objectContaining({archetype_id:'clapboard_north_end',target_floors:2}));
  expect(onReplace.mock.calls[0][0]).toMatchObject({development_selected_variant_id:'clapboard_north_end',
    pick_place_asset:'validation_clapboard_north_end',floor_count:2,custom_style_enabled:false});
  expect(saved.properties?.custom_style_enabled).toBe(true);
});

it.each([100,85])('checks the actual tapered saved plot before replacing it with a %s percent Halifax assembly',async percent=>{
  const saved:SiteZone={...zone,coordinates:[[-114.073806679,51.052045769],[-114.07406689,51.052053808],
    [-114.073975986,51.051931457],[-114.073662263,51.051902337]],properties:{...zone.properties,
    development_archetype_id:'halifax_painted_clapboard_row_variant_0',
  }};
  vi.mocked(legoAssemblyApi.plan).mockImplementation(async request=>({...plan,
    family:'rlasm-clay-halifax-clapboard-north-end',archetype_id:'clapboard_north_end',assembled_height_m:10.48,
    target:{width_m:request.target_width_m,depth_m:request.target_depth_m,floors:2},
    instances:[{...plan.instances[0],model_url:'/api/v1/files/library/rlasm-house-flex/halifax-clapboard-north-end-clay-v003.glb',
      native_dimensions_m:[11,12.275000095367432,10.479999542236328],
      scale:[request.target_width_m/11,request.target_depth_m/12.275000095367432,1]}],
  }));
  const onReplace=vi.fn();
  render(<CustomMassingRecovery zone={saved} buildings={[building]} onReplace={onReplace}/>);
  fireEvent.click(screen.getByRole('button',{name:'Choose a detailed building'}));
  fireEvent.change(screen.getByLabelText('Building type'),{target:{value:'building:halifax_painted_clapboard_row:clapboard_north_end'}});
  if(percent!==100)fireEvent.change(screen.getByLabelText('Building footprint (%)'),{target:{value:String(percent)}});
  fireEvent.click(screen.getByRole('button',{name:'Apply building'}));
  await waitFor(()=>expect(screen.getByRole('button',{name:'Replace custom massing'})).toBeEnabled());
  fireEvent.click(screen.getByRole('button',{name:'Replace custom massing'}));
  if(percent===100){
    await waitFor(()=>expect(screen.getByRole('alert')).toHaveTextContent(/outside.*saved plot/i));
    expect(onReplace).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent(/smaller.*footprint|another building/i);
  }else{
    await waitFor(()=>expect(onReplace).toHaveBeenCalledOnce());
    expect(onReplace.mock.calls[0][0]).toMatchObject({building_footprint_scale:0.85,
      development_selected_variant_id:'clapboard_north_end',floor_count:2,custom_style_enabled:false});
  }
  expect(saved.properties?.custom_style_enabled).toBe(true);
  expect(saved.coordinates).toEqual([[-114.073806679,51.052045769],[-114.07406689,51.052053808],
    [-114.073975986,51.051931457],[-114.073662263,51.051902337]]);
});

it('explains saved custom massing and saves a checked replacement only after explicit confirmation', async () => {
  const onReplace=vi.fn();
  render(<CustomMassingRecovery zone={zone} buildings={[building]} onReplace={onReplace}/>);
  expect(screen.getByText(/custom design.*simple building volume/i)).toBeTruthy();
  expect(screen.getByText(/no detailed model was saved.*refresh/i)).toBeTruthy();
  chooseDuplex();
  expect(onReplace).not.toHaveBeenCalled();
  expect(legoAssemblyApi.plan).not.toHaveBeenCalled();
  expect(screen.getByText(/3 storeys.*2 storeys/i)).toBeTruthy();
  fireEvent.click(screen.getByRole('button',{name:'Replace custom massing'}));
  await waitFor(()=>expect(onReplace).toHaveBeenCalledOnce());
  expect(legoAssemblyApi.plan).toHaveBeenLastCalledWith(expect.objectContaining({
    project_id:'project', archetype_id:'infill_duplex', target_floors:2,
  }));
  expect(onReplace.mock.calls[0][0]).toMatchObject({
    custom_style_enabled:false, custom_style_prompt:'A new york style brownhouse',
    development_selected_variant_id:'infill_duplex', pick_place_asset:'clay_side_by_side_duplex',
  });
  expect(zone.properties?.custom_style_enabled).toBe(true);
});

it('keeps the original editable when the selected detailed model does not fit', async () => {
  vi.mocked(legoAssemblyApi.plan).mockRejectedValue(new Error('Detailed assembly does not fit this plot'));
  const onReplace=vi.fn();
  render(<CustomMassingRecovery zone={zone} buildings={[building]} onReplace={onReplace}/>);
  chooseDuplex();
  fireEvent.click(screen.getByRole('button',{name:'Replace custom massing'}));
  await waitFor(()=>expect(screen.getByRole('alert')).toHaveTextContent(/unchanged.*does not fit/i));
  expect(onReplace).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button',{name:'Keep custom design'}));
  expect(screen.getByRole('button',{name:'Choose a detailed building'})).toBeEnabled();
});

it('does not save a delayed replacement after the student cancels', async () => {
  let finish!:()=>void;
  vi.mocked(legoAssemblyApi.plan).mockImplementation(()=>new Promise(resolve=>{finish=()=>resolve(plan);}));
  const onReplace=vi.fn();
  render(<CustomMassingRecovery zone={zone} buildings={[building]} onReplace={onReplace}/>);
  chooseDuplex();
  fireEvent.click(screen.getByRole('button',{name:'Replace custom massing'}));
  await waitFor(()=>expect(legoAssemblyApi.plan).toHaveBeenCalledOnce());
  fireEvent.click(screen.getByRole('button',{name:'Keep custom design'}));
  await act(async()=>finish());
  expect(onReplace).not.toHaveBeenCalled();
});

it('discards a checked replacement after the saved plot changes', async () => {
  let finish!:()=>void;
  vi.mocked(legoAssemblyApi.plan).mockImplementation(()=>new Promise(resolve=>{finish=()=>resolve(plan);}));
  const onReplace=vi.fn();
  const {rerender}=render(<CustomMassingRecovery zone={zone} buildings={[building]} onReplace={onReplace}/>);
  chooseDuplex();
  fireEvent.click(screen.getByRole('button',{name:'Replace custom massing'}));
  await waitFor(()=>expect(legoAssemblyApi.plan).toHaveBeenCalledOnce());
  rerender(<CustomMassingRecovery zone={{...zone,updated_at:'moved',coordinates:rectangleAt([-114.001,51],30,14)}} buildings={[building]} onReplace={onReplace}/>);
  await act(async()=>finish());
  expect(onReplace).not.toHaveBeenCalled();
  expect(screen.getByRole('button',{name:'Choose a detailed building'})).toBeEnabled();
});

it.each([
  {model_url:'/saved.glb'}, {lod_urls:{'0':'/saved-lod.glb'}}, {generation_status:'processing'},
] as const)('does not label an existing or pending model as absent: %j', detail => {
  render(<CustomMassingRecovery zone={zone} buildings={[{...building,...detail}]} onReplace={vi.fn()}/>);
  expect(screen.queryByRole('button',{name:'Choose a detailed building'})).toBeNull();
});
