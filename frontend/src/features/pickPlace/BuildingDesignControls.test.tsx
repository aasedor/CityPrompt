import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { BuildingDesignControls } from './BuildingDesignControls';
import { placementProperties, placeAsset } from './catalogue';
import { CANONICAL_CHOICES } from './canonicalCatalogue';

const zone = { id: 'home', zone_type: 'building', coordinates: [[0, 0], [1, 0], [1, 1], [0, 1]],
  properties: placementProperties(placeAsset('infill_home')) } as SiteZone;

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

it('repeats authored Vancouver floors through the reviewed 16–40 storey programme', () => {
  const tower = placeAsset('clay_vancouver_balcony_podium_tower');
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: placementProperties(tower) }} disabled={false} onSave={onSave} />);
  screen.getByText(/Choose 16–40 storeys/);
  expect((screen.getByLabelText('Height (m)') as HTMLInputElement).readOnly).toBe(true);
  fireEvent.change(screen.getByLabelText('Storeys'), { target: { value: '25' } });
  expect((screen.getByLabelText('Height (m)') as HTMLInputElement).value).toBe('87.6');
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
    floors: 25,
    floor_count: 25,
    height: 87.6,
    height_m: 87.6,
    development_height_override_m: 87.6,
    pick_place_asset: 'clay_vancouver_balcony_podium_tower',
  }));
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

it('changes a bungalow footprint without changing its selected two-storey height', () => {
  const bungalow = placeAsset('trial_postwar_bungalow');
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: placementProperties(bungalow) }} disabled={false} onSave={onSave} />);
  screen.getByText(/Each choice uses a complete authored house/);
  fireEvent.change(screen.getByLabelText('Storeys'), { target: { value: '2' } });
  fireEvent.change(screen.getByLabelText('Building footprint (%)'), { target: { value: '115' } });
  expect((screen.getByLabelText('Height (m)') as HTMLInputElement).value).toBe('9.29');
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
    floors: 2,
    floor_count: 2,
    height: 9.29,
    height_m: 9.29,
    building_footprint_scale: 1.15,
    building_footprint_program_id: 'house-flex-pilot-v001',
  }));
});

it.each([
  ['trial_postwar_bungalow', 1, 6.36],
  ['trial_edwardian_foursquare', 2, 10.81],
  ['validation_clapboard_north_end', 2, 10.48],
])('exposes the reviewed footprint band for %s and preserves the native height', (assetId, storeys, expectedHeight) => {
  const asset = placeAsset(assetId);
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={{ ...zone, properties: placementProperties(asset) }} disabled={false} onSave={onSave} />);
  const control = screen.getByLabelText('Building footprint (%)') as HTMLInputElement;
  expect(control).toMatchObject({ min: '85', max: '115', step: '5' });
  fireEvent.change(control, { target: { value: '85' } });
  expect((screen.getByLabelText('Storeys') as HTMLInputElement).value).toBe(String(storeys));
  expect(Number((screen.getByLabelText('Height (m)') as HTMLInputElement).value)).toBeCloseTo(expectedHeight, 2);
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
    floors: storeys,
    floor_count: storeys,
    height: expectedHeight,
    height_m: expectedHeight,
    building_footprint_scale: 0.85,
  }));
});

it('preserves an existing house scale while changing only its storeys', () => {
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
  expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
    floors: 2,
    building_footprint_scale: 1.15,
  }));
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
