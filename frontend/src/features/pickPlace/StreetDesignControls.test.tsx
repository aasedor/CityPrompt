import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { StreetDesignControls } from './StreetDesignControls';
import { STREET_ASSETS, ALL_MANUAL_STREET_ASSETS } from './assetRegistry';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { bufferLineToPolygon } from '@/utils/roadGeometry';

it('lets a student choose a supported width and see the resulting type before saving', () => {
  const line = [[-114, 51], [-113.998, 51]];
  const initial = STREET_ASSETS.find(a => a.model.variantId === 'student_main_street_v1')!;
  const target = STREET_ASSETS.find(a => a.model.variantId === 'student_market_street_v1')!;
  const zone = { id: 'street', project_id: 'project', color: '#777', sort_order: 0, created_at: '', updated_at: '', zone_type: 'road', coordinates: bufferLineToPolygon(line, initial.sectionWidth), properties: { ...initial.properties, plan_centerline: line } } as SiteZone;
  const save = vi.fn(); render(<StreetDesignControls zone={zone} disabled={false} onSave={save} />);
  // Import and render the actual mixed roster: fixed fixtures must not crash route controls.
  expect(CANONICAL_CHOICES.filter(c => c.domain === 'street_pathway')).toHaveLength(STREET_ASSETS.length);
  const types = screen.getByLabelText('Street type') as HTMLSelectElement;
  expect(Array.from(types.options, option => option.value).sort()).toEqual(
    CANONICAL_CHOICES.filter(c => c.domain === 'street_pathway').map(c => c.id).sort());
  fireEvent.change(screen.getByLabelText('Street width'), { target: { value: String(target.sectionWidth) } });
  const selected = CANONICAL_CHOICES.find(choice => choice.id === types.value)!.placements[0];
  if (selected.kind !== 'street') throw new Error('Expected a street selection');
  expect(selected.sectionWidth).toBe(target.sectionWidth);
  // Several faithful designs can share a width. Selecting the specific type
  // still chooses Market without changing the authored centreline.
  const targetChoice = CANONICAL_CHOICES.find(c => c.option.id === target.properties.road_archetype_id
    && c.placements.some(a => a.model.variantId === target.model.variantId))!;
  fireEvent.change(types, { target: { value: targetChoice.id } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply street' }));
  expect(save.mock.calls[0][0].properties).toMatchObject({ road_archetype_id: target.properties.road_archetype_id,
    road_selected_variant_id: target.model.variantId, width: target.sectionWidth, plan_centerline: line });
});

it.each(['student_main_street_v1', 'student_market_street_v1'])('retains %s and its exact width when the student applies unchanged settings', variantId => {
  const asset = STREET_ASSETS.find(a => a.model.variantId === variantId)!;
  const line = [[-114, 51], [-113.998, 51]];
  const zone = { id: 'native', project_id: 'project', color: '#777', sort_order: 0, created_at: '', updated_at: '', zone_type: 'road', coordinates: bufferLineToPolygon(line, asset.sectionWidth),
    properties: { ...asset.properties, plan_centerline: line } } as SiteZone;
  const save = vi.fn(); render(<StreetDesignControls zone={zone} disabled={false} onSave={save} />);
  expect((screen.getByLabelText('Street variant') as HTMLSelectElement).value).toBe(variantId);
  expect((screen.getByLabelText('Street width') as HTMLSelectElement).value).toBe(String(asset.sectionWidth));
  fireEvent.click(screen.getByRole('button', {name: 'Apply street'}));
  expect(save.mock.calls[0][0].properties).toMatchObject({road_selected_variant_id: variantId, width:asset.sectionWidth, plan_centerline:line});
});

it.each(['standalone_narrow_sidewalk_v1', 'standalone_neighbourhood_sidewalk_v1', 'standalone_urban_sidewalk_v1'])('shows the exact %s type instead of borrowing a sibling with the same parent', variantId => {
  const asset = STREET_ASSETS.find(a => a.model.variantId === variantId)!;
  const line = [[-114, 51], [-113.998, 51]];
  const zone = { id: 'sidewalk', project_id: 'project', color: '#777', sort_order: 0, created_at: '', updated_at: '', zone_type: 'road', coordinates: bufferLineToPolygon(line, asset.sectionWidth),
    properties: { ...asset.properties, plan_centerline: line } } as SiteZone;
  const save = vi.fn(); render(<StreetDesignControls zone={zone} disabled={false} onSave={save} />);
  const types = screen.getByLabelText('Street type') as HTMLSelectElement;
  expect(types.selectedOptions[0].textContent).toBe(asset.label);
  const variants = screen.getByLabelText('Street variant') as HTMLSelectElement;
  expect(Array.from(variants.options, option => option.value)).toEqual([variantId]);
  fireEvent.click(screen.getByRole('button', { name: 'Apply street' }));
  expect(save.mock.calls[0][0].properties).toMatchObject({ road_archetype_id: asset.properties.road_archetype_id,
    road_selected_variant_id: variantId, width: asset.sectionWidth, plan_centerline: line });
});

it('keeps a saved superseded collector intact until the student explicitly selects its replacement', () => {
  const old = ALL_MANUAL_STREET_ASSETS.find(a => a.model.variantId === 'calgary_collector_manual_v1')!;
  const line = [[-114,51],[-113.998,51]];
  const zone = {id:'old',project_id:'pilot',color:'#777777',sort_order:0,created_at:'',updated_at:'',
    zone_type:'road',coordinates:bufferLineToPolygon(line,20),properties:{...old.properties,plan_centerline:line}} as SiteZone;
  const save = vi.fn();
  render(<StreetDesignControls zone={zone} disabled={false} onSave={save} />);
  expect((screen.getByLabelText('Street variant') as HTMLSelectElement).value).toBe(old.model.variantId);
  fireEvent.click(screen.getByRole('button',{name:'Apply street'}));
  expect(save.mock.calls[0][0].properties).toMatchObject({road_selected_variant_id:old.model.variantId,width:20});
  fireEvent.change(screen.getByLabelText('Street variant'), {target:{value:'calgary_collector_draft3_v1'}});
  expect(save).toHaveBeenCalledTimes(1);
  fireEvent.click(screen.getByRole('button',{name:'Apply street'}));
  expect(save.mock.calls[1][0].properties).toMatchObject({road_selected_variant_id:'calgary_collector_draft3_v1',width:23,plan_centerline:line});
});
