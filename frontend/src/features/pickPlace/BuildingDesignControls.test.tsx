import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { BuildingDesignControls } from './BuildingDesignControls';
import { placementProperties, placeAsset } from './catalogue';

const zone = { id: 'home', zone_type: 'building', coordinates: [[0, 0], [1, 0], [1, 1], [0, 1]],
  properties: placementProperties(placeAsset('infill_home')) } as SiteZone;

it('saves an explicit height contract and synchronizes both floor fields', () => {
  const onSave = vi.fn(); render(<BuildingDesignControls zone={zone} disabled={false} onSave={onSave} />);
  fireEvent.change(screen.getByLabelText('Storeys'), { target: { value: '4' } });
  fireEvent.change(screen.getByLabelText('Height (m)'), { target: { value: '14' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ floors: 4, floor_count: 4, height: 14, height_m: 14,
    floor_height: 3.5, development_height_override_m: 14 }));
});

it('changes exact catalogue identity while retaining independent object data', () => {
  const onSave = vi.fn(); render(<BuildingDesignControls zone={{ ...zone, properties: { ...zone.properties, terrain_elevation_m: 1100 } }} disabled={false} onSave={onSave} />);
  fireEvent.change(screen.getByLabelText('Building type'), { target: { value: 'brownstone_rowhouse_frontage' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
  expect(onSave.mock.calls[0][0]).toMatchObject({ development_subcategory: 'brownstone_rowhouse_frontage', development_selected_variant_id: 'brownstone_rowhouse_red_sandstone', terrain_elevation_m: 1100 });
  expect(onSave.mock.calls[0][0].native_home_plot).toBeUndefined();
  expect(onSave.mock.calls[0][0].pick_place_asset).toMatch(/^canonical-building:/);
});
