import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import { legoAssemblyApi } from '@/features/legoAssembly/legoAssemblyApi';
import type { SiteZone } from '@/types';
import { BuildingDesignControls } from './BuildingDesignControls';
import { placementProperties, placeAsset } from './catalogue';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
vi.mock('@/features/legoAssembly/legoAssemblyApi',async importOriginal=>({
  ...await importOriginal<typeof import('@/features/legoAssembly/legoAssemblyApi')>(),
  legoAssemblyApi:{plan:vi.fn()},
}));
beforeEach(()=>{vi.mocked(legoAssemblyApi.plan).mockReset().mockResolvedValue({} as never);});

const zone = { id: 'home', zone_type: 'building', coordinates: [[0, 0], [1, 0], [1, 1], [0, 1]],
  properties: placementProperties(placeAsset('infill_home')) } as SiteZone;

it('checks the detailed Brick Podium assembly before saving supported tower storeys', async () => {
  const tower = placeAsset('claude_trial_brick_podium_condo_tower');
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: placementProperties(tower) }} disabled={false} onSave={onSave}/>);
  expect((screen.getByLabelText('Storeys') as HTMLInputElement).readOnly).toBe(false);
  fireEvent.change(screen.getByLabelText('Storeys'), { target: { value: '25' } });
  expect((screen.getByLabelText('Height (m)') as HTMLInputElement).value).toBe('86.1');
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  await waitFor(() => expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ floor_count: 25, height_m: 86.1,
    pick_place_asset: tower.id, pick_place_model_revision: tower.model.revision })));
  expect(legoAssemblyApi.plan).toHaveBeenCalledWith(expect.objectContaining({ archetype_id: tower.model.variantId, target_floors: 25,
    target_width_m: 54, target_depth_m: 44, target_height_m: 86.1, model_revision: tower.model.revision }));
});

it('does not allow arbitrary storeys or heights for a fixed authored building', () => {
  const onSave = vi.fn(); render(<BuildingDesignControls zone={zone} disabled={false} onSave={onSave} />);
  expect((screen.getByLabelText('Storeys') as HTMLInputElement).readOnly).toBe(true);
  expect((screen.getByLabelText('Height (m)') as HTMLInputElement).readOnly).toBe(true);
  expect((screen.getByLabelText('Storeys') as HTMLInputElement).value).toBe('2');
});

it('changes exact catalogue identity while retaining independent object data', () => {
  const onSave = vi.fn(); render(<BuildingDesignControls zone={{ ...zone, properties: { ...zone.properties, terrain_elevation_m: 1100 } }} disabled={false} onSave={onSave} />);
  const duplex = CANONICAL_CHOICES.find(choice => choice.option.variants?.[0]?.id === 'infill_duplex')!;
  fireEvent.change(screen.getByLabelText('Building type'), { target: { value: duplex.id } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  expect(onSave.mock.calls[0][0]).toMatchObject({ development_archetype_id: 'calgary_modern_infill_house', development_selected_variant_id: 'infill_duplex', terrain_elevation_m: 1100 });
  expect(onSave.mock.calls[0][0].native_home_plot).toBe(false);
  expect(onSave.mock.calls[0][0].pick_place_asset).toBe('clay_side_by_side_duplex');
});

it('keeps the exact side-by-side duplex identity under a shared parent archetype', () => {
  const duplex = placeAsset('clay_side_by_side_duplex');
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: placementProperties(duplex) }} disabled={false} onSave={onSave} />);
  expect((screen.getByLabelText('Building type') as HTMLSelectElement).value).toBe('building:calgary_modern_infill_house:infill_duplex');
  expect((screen.getByLabelText('Building variant') as HTMLSelectElement).value).toBe('infill_duplex');
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
    development_archetype_id: 'calgary_modern_infill_house',
    development_selected_variant_id: 'infill_duplex',
    pick_place_asset: 'clay_side_by_side_duplex',
  }));
});

it('repeats authored Vancouver floors through the reviewed 16–40 storey programme', async () => {
  const tower = placeAsset('clay_vancouver_balcony_podium_tower');
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: placementProperties(tower) }} disabled={false} onSave={onSave} />);
  screen.getByText(/Choose 16–40 storeys/);
  expect((screen.getByLabelText('Height (m)') as HTMLInputElement).readOnly).toBe(true);
  fireEvent.change(screen.getByLabelText('Storeys'), { target: { value: '25' } });
  expect((screen.getByLabelText('Height (m)') as HTMLInputElement).value).toBe('87.6');
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  await waitFor(()=>expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
    floors: 25,
    floor_count: 25,
    height: 87.6,
    height_m: 87.6,
    development_height_override_m: 87.6,
    pick_place_asset: 'clay_vancouver_balcony_podium_tower',
  })));
});

it('preserves the saved detailed tower when the current runtime cannot build its requested height',async()=>{
  vi.mocked(legoAssemblyApi.plan).mockRejectedValue(new Error('Required floor module is unavailable'));
  const tower=placeAsset('clay_vancouver_balcony_podium_tower');
  const onSave=vi.fn();
  render(<BuildingDesignControls zone={{...zone,properties:placementProperties(tower)}} disabled={false} onSave={onSave}/>);
  fireEvent.change(screen.getByLabelText('Storeys'),{target:{value:'40'}});
  fireEvent.click(screen.getByRole('button',{name:'Apply building'}));
  await waitFor(()=>expect(screen.getByRole('alert').textContent).toContain('Required floor module is unavailable'));
  expect(onSave).not.toHaveBeenCalled();
});

it.each(['storeys','footprint'] as const)('preserves a detailed house when its requested %s assembly is unavailable',async change=>{
  vi.mocked(legoAssemblyApi.plan).mockRejectedValue(new Error('Requested house assembly is unavailable'));
  const onSave=vi.fn();
  render(<BuildingDesignControls zone={{...zone,properties:placementProperties(placeAsset('trial_postwar_bungalow'))}} disabled={false} onSave={onSave}/>);
  fireEvent.change(screen.getByLabelText(change==='storeys'?'Storeys':'Building footprint (%)'),{target:{value:change==='storeys'?'2':'85'}});
  fireEvent.click(screen.getByRole('button',{name:'Apply building'}));
  await waitFor(()=>expect(legoAssemblyApi.plan).toHaveBeenCalledOnce());
  expect(onSave).not.toHaveBeenCalled();
  expect(screen.getByRole('alert').textContent).toContain('The building was not changed.');
});

it.each(['storeys','footprint'] as const)('checks returning an edited house to its native %s before replacing the detailed model',async change=>{
  vi.mocked(legoAssemblyApi.plan).mockRejectedValue(new Error('Native assembly is unavailable'));
  const onSave=vi.fn();
  const properties={...placementProperties(placeAsset('trial_postwar_bungalow')),
    ...(change==='storeys'?{floors:2,floor_count:2,height:9.29,height_m:9.29,development_height_override_m:9.29}:{building_footprint_scale:0.85})};
  render(<BuildingDesignControls zone={{...zone,properties}} disabled={false} onSave={onSave}/>);
  fireEvent.change(screen.getByLabelText(change==='storeys'?'Storeys':'Building footprint (%)'),{target:{value:change==='storeys'?'1':'100'}});
  fireEvent.click(screen.getByRole('button',{name:'Apply building'}));
  await waitFor(()=>expect(legoAssemblyApi.plan).toHaveBeenCalledOnce());
  expect(onSave).not.toHaveBeenCalled();
  expect(screen.getByRole('alert').textContent).toContain('The building was not changed.');
});

it('preflights the saved revision and footprint so stale modules cannot authorize a height edit',async()=>{
  const tower=placeAsset('clay_vancouver_balcony_podium_tower');
  const properties=placementProperties(tower);
  vi.mocked(legoAssemblyApi.plan).mockImplementation(async request=>{
    if(request.model_revision===properties.pick_place_model_revision) throw new Error('Modules do not match saved revision');
    return {} as never;
  });
  const onSave=vi.fn();
  render(<BuildingDesignControls zone={{...zone,project_id:'project',properties}} disabled={false} onSave={onSave}/>);
  fireEvent.change(screen.getByLabelText('Storeys'),{target:{value:'40'}});
  fireEvent.click(screen.getByRole('button',{name:'Apply building'}));
  await waitFor(()=>expect(legoAssemblyApi.plan).toHaveBeenCalledWith(expect.objectContaining({
    model_revision:properties.pick_place_model_revision,project_id:'project',target_floors:40,
    target_height_m:135.6,footprint_profile:'rectangle',footprint_local_m:expect.any(Array),
  })));
  expect(screen.getByRole('alert').textContent).toContain('Modules do not match saved revision');
  expect(onSave).not.toHaveBeenCalled();
});

it('does not apply a delayed model check after the editor closes',async()=>{
  let finish!:()=>void;
  vi.mocked(legoAssemblyApi.plan).mockImplementationOnce(()=>new Promise(resolve=>{finish=()=>resolve({} as never);}));
  const tower=placeAsset('clay_vancouver_balcony_podium_tower');const onSave=vi.fn();
  const view=render(<BuildingDesignControls zone={{...zone,properties:placementProperties(tower)}} disabled={false} onSave={onSave}/>);
  fireEvent.change(screen.getByLabelText('Storeys'),{target:{value:'40'}});
  fireEvent.click(screen.getByRole('button',{name:'Apply building'}));
  await waitFor(()=>expect(legoAssemblyApi.plan).toHaveBeenCalledOnce());
  view.unmount();await act(async()=>finish());
  expect(onSave).not.toHaveBeenCalled();
});

it.each(['entrance', 'footprint', 'project'] as const)('does not overwrite a newer %s edit after a delayed height check', async change => {
  let finish!: () => void;
  vi.mocked(legoAssemblyApi.plan).mockImplementationOnce(() => new Promise(resolve => {
    finish = () => resolve({} as never);
  }));
  const original = { ...zone, project_id: 'first-project', properties: placementProperties(placeAsset('clay_vancouver_balcony_podium_tower')) };
  const onSave = vi.fn();
  const view = render(<BuildingDesignControls zone={original} disabled={false} onSave={onSave} />);
  fireEvent.change(screen.getByLabelText('Storeys'), { target: { value: '40' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  await waitFor(() => expect(legoAssemblyApi.plan).toHaveBeenCalledOnce());
  const updated = change === 'entrance'
    ? { ...original, properties: { ...original.properties, pedestrian_building_entrance: { edge_index: 2, fraction: 0.6 } } }
    : change === 'footprint'
      ? { ...original, coordinates: [[0, 0], [2, 0], [2, 1], [0, 1]] as SiteZone['coordinates'] }
      : { ...original, project_id: 'second-project' };
  view.rerender(<BuildingDesignControls zone={updated} disabled={false} onSave={onSave} />);
  await act(async () => finish());
  expect(onSave).not.toHaveBeenCalled();
  expect(screen.getByRole('alert').textContent).toContain('apply again');
  // An explicit retry checks the current zone and preserves its independent edit.
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  await waitFor(() => expect(onSave).toHaveBeenCalledOnce());
  expect(onSave.mock.calls[0][0]).toMatchObject({ floor_count: 40 });
  if (change === 'entrance') expect(onSave.mock.calls[0][0].pedestrian_building_entrance).toEqual({ edge_index: 2, fraction: 0.6 });
});

it('allows a checked height edit after an unchanged zone is refetched', async () => {
  let finish!: () => void;
  vi.mocked(legoAssemblyApi.plan).mockImplementationOnce(() => new Promise(resolve => { finish = () => resolve({} as never); }));
  const original = { ...zone, properties: placementProperties(placeAsset('clay_vancouver_balcony_podium_tower')) };
  const onSave = vi.fn();
  const view = render(<BuildingDesignControls zone={original} disabled={false} onSave={onSave} />);
  fireEvent.change(screen.getByLabelText('Storeys'), { target: { value: '40' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  await waitFor(() => expect(legoAssemblyApi.plan).toHaveBeenCalledOnce());
  view.rerender(<BuildingDesignControls zone={{ ...original, properties: { ...original.properties } }} disabled={false} onSave={onSave} />);
  await act(async () => finish());
  expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ floor_count: 40 }));
});

it('does not save a Vancouver height beyond the reviewed storey programme', () => {
  const tower = placeAsset('clay_vancouver_balcony_podium_tower');
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: placementProperties(tower) }} disabled={false} onSave={onSave} />);
  fireEvent.change(screen.getByLabelText('Storeys'), { target: { value: '41' } });
  expect((screen.getByRole('button', { name: 'Apply building' }) as HTMLButtonElement).disabled).toBe(true);
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  expect(onSave).not.toHaveBeenCalled();
});

it('changes a bungalow footprint without changing its selected two-storey height', async () => {
  const bungalow = placeAsset('trial_postwar_bungalow');
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: placementProperties(bungalow) }} disabled={false} onSave={onSave} />);
  screen.getByText(/Each choice uses a complete authored house/);
  fireEvent.change(screen.getByLabelText('Storeys'), { target: { value: '2' } });
  fireEvent.change(screen.getByLabelText('Building footprint (%)'), { target: { value: '115' } });
  expect((screen.getByLabelText('Height (m)') as HTMLInputElement).value).toBe('9.29');
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  await waitFor(()=>expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
    floors: 2,
    floor_count: 2,
    height: 9.29,
    height_m: 9.29,
    building_footprint_scale: 1.15,
    building_footprint_program_id: 'house-flex-pilot-v001',
  })));
});

it.each([
  ['trial_postwar_bungalow', 1, 6.36],
  ['trial_edwardian_foursquare', 2, 10.81],
  ['validation_clapboard_north_end', 2, 10.48],
])('exposes the reviewed footprint band for %s and preserves the native height', async (assetId, storeys, expectedHeight) => {
  const asset = placeAsset(assetId);
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: placementProperties(asset) }} disabled={false} onSave={onSave} />);
  const control = screen.getByLabelText('Building footprint (%)') as HTMLInputElement;
  expect(control).toMatchObject({ min: '85', max: '115', step: '5' });
  fireEvent.change(control, { target: { value: '85' } });
  expect((screen.getByLabelText('Storeys') as HTMLInputElement).value).toBe(String(storeys));
  expect(Number((screen.getByLabelText('Height (m)') as HTMLInputElement).value)).toBeCloseTo(expectedHeight, 2);
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  await waitFor(()=>expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
    floors: storeys,
    floor_count: storeys,
    height: expectedHeight,
    height_m: expectedHeight,
    building_footprint_scale: 0.85,
  })));
});

it('preserves an existing house scale while changing only its storeys', async () => {
  const bungalow = placeAsset('trial_postwar_bungalow');
  const onSave = vi.fn();
  const properties = {
    ...placementProperties(bungalow),
    building_footprint_scale: 1.15,
  };
  render(<BuildingDesignControls zone={{ ...zone, properties }} disabled={false} onSave={onSave} />);
  expect((screen.getByLabelText('Building footprint (%)') as HTMLInputElement).value).toBe('115');
  fireEvent.change(screen.getByLabelText('Storeys'), { target: { value: '2' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  await waitFor(()=>expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
    floors: 2,
    building_footprint_scale: 1.15,
  })));
});

it('locks buildings without alternate assemblies to their metadata storey count', () => {
  const building = placeAsset('validation_brewery_crystal_brewhouse');
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: {
    ...placementProperties(building), floors: 4, floor_count: 4,
    height: 16, height_m: 16, development_height_override_m: 16,
  } }} disabled={false} onSave={onSave} />);
  expect((screen.getByLabelText('Storeys') as HTMLInputElement).readOnly).toBe(true);
  expect((screen.getByLabelText('Storeys') as HTMLInputElement).value).toBe('1');
  screen.getByText('This exact model is currently available at 1 storey.');
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
    floors: 1,
    floor_count: 1,
    height: Number(building.nativeDimensions![2].toFixed(2)),
    height_m: Number(building.nativeDimensions![2].toFixed(2)),
    development_height_override_m: undefined,
  }));
});

it('clears the house footprint programme when changing to an unrelated building', () => {
  const bungalow = placeAsset('trial_postwar_bungalow');
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: placementProperties(bungalow) }} disabled={false} onSave={onSave} />);
  fireEvent.change(screen.getByLabelText('Building type'), { target: { value: 'building:calgary_modern_infill_house:infill_duplex' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  expect(onSave.mock.calls[0][0]).toEqual(expect.objectContaining({
    development_selected_variant_id: 'infill_duplex',
    building_footprint_scale: undefined,
    building_footprint_program_id: undefined,
    building_footprint_native_width_m: undefined,
    building_footprint_native_depth_m: undefined,
  }));
});


it('retains the saved older model when applying its authored dimensions', () => {
  const asset = placeAsset('validation_minimalist_infill_brick_monolith');
  const revision = '3c7ab81c4db3c2a67ec280788ff84008da0cbd20a16129feba75dffcfcd0d4a6';
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: { ...placementProperties(asset), pick_place_model_revision: revision, height: 30 } }} disabled={false} onSave={onSave} />);
  expect((screen.getByLabelText('Height (m)') as HTMLInputElement).value).toBe('10.48');
  expect((screen.getByLabelText('Height (m)') as HTMLInputElement).readOnly).toBe(true);
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ pick_place_model_revision: revision, height_m: 10.48 }));
});

it('does not apply the current model over an unavailable saved revision', () => {
  const asset = placeAsset('validation_minimalist_infill_brick_monolith');
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: { ...placementProperties(asset), pick_place_model_revision: 'unavailable' } }} disabled={false} onSave={onSave} />);
  expect(screen.getByRole('alert').textContent).toContain('saved model revision is unavailable');
  expect((screen.getByRole('button', { name: 'Apply building' }) as HTMLButtonElement).disabled).toBe(true);
});
