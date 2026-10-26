import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { NativeBuildingRecoveryNotice } from './NativeBuildingRecoveryNotice';
import type { SiteZone } from '@/types';

afterEach(cleanup);
it('shows the required saved model and recovery without changing the preserved plot', () => {
  const zone = {id:'saved-plot',project_id:'project',color:'#fff',sort_order:0,created_at:'before',updated_at:'before',zone_type:'building',properties:{
    development_archetype_label:'Prairie School house',pick_place_model_revision:'prairie-unavailable-v001',
  },coordinates:[[-114,51],[-113.999,51],[-113.999,51.001]]} as SiteZone;
  const before = JSON.stringify(zone); const select = vi.fn();
  render(<NativeBuildingRecoveryNotice zones={[zone]} onSelect={select}/>);
  expect(screen.getByRole('alert').textContent).toContain('Saved building model unavailable');
  expect(screen.getByText('Prairie School house')).toBeTruthy();
  expect(screen.getByText(/prairie-unavailable-v001/)).toBeTruthy();
  expect(screen.getByText(/Restore the matching local model, or choose a replacement in Buildings/)).toBeTruthy();
  fireEvent.click(screen.getByRole('button',{name:'Select saved plot'}));
  expect(select).toHaveBeenCalledWith(zone);
  expect(JSON.stringify(zone)).toBe(before);
});

it('stays absent from healthy scenes', () => {
  render(<NativeBuildingRecoveryNotice zones={[]} onSelect={vi.fn()}/>);
  expect(screen.queryByRole('alert')).toBeNull();
});
