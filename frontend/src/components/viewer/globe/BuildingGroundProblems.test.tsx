import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { BuildingGroundProblems } from './BuildingGroundProblems';

const zone: SiteZone = { id: 'plot', project_id: 'project', zone_type: 'building',
  name: 'Hill house', building_ids: ['model'], coordinates: [[-114, 51], [-113.9999, 51], [-114, 51.0001]],
  color: '#fff', sort_order: 1, created_at: 'before', updated_at: 'before' };

it('selects the exact saved plot for repair without changing its geometry', () => {
  const select = vi.fn(); const before = JSON.stringify(zone);
  render(<BuildingGroundProblems issues={[{ buildingId: 'model', reason: 'foundation_exceeds_3m' }]}
    zones={[zone]} onClose={vi.fn()} onSelect={select} />);
  expect(screen.getByText('Hill house')).toBeTruthy();
  expect(screen.getByText(/crosses a steep change/)).toBeTruthy();
  expect(screen.queryByText(/foundation_exceeds_3m/)).toBeNull();
  fireEvent.click(screen.getByRole('button', { name: 'Select and adjust' }));
  expect(select).toHaveBeenCalledWith(zone);
  expect(JSON.stringify(zone)).toBe(before);
});

it('handles missing owners and pending terrain without offering a wrong selection', () => {
  const close = vi.fn();
  render(<BuildingGroundProblems issues={[{ buildingId: 'deleted', reason: 'incomplete_footprint_ground' },
    { buildingId: 'model', reason: 'ground_not_ready' }]} zones={[zone]} onClose={close} onSelect={vi.fn()} />);
  expect(screen.queryByRole('button', { name: 'Select and adjust' })).toBeNull();
  expect(screen.queryByText('Hill house')).toBeNull();
  expect(screen.getByText(/could not be confirmed/)).toBeTruthy();
  fireEvent.keyDown(document, { key: 'Escape' });
  expect(close).toHaveBeenCalledOnce();
});

it('explains missing landing space and keeps the original plot available for repair', () => {
  const select=vi.fn();
  render(<BuildingGroundProblems issues={[{buildingId:'model',reason:'entrance_landing_run_too_short'}]}
    zones={[zone]} onClose={vi.fn()} onSelect={select}/>);
  expect(screen.getByText(/stairs and a level landing at the house/)).toBeTruthy();
  expect(screen.getByText(/Move the building farther from the street/)).toBeTruthy();
  fireEvent.click(screen.getByRole('button',{name:'Select and adjust'}));
  expect(select).toHaveBeenCalledWith(zone);
});
