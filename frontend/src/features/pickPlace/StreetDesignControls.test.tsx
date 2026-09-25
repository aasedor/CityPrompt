import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { StreetDesignControls } from './StreetDesignControls';
import { STREET_ASSETS } from './assetRegistry';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { bufferLineToPolygon } from '@/utils/roadGeometry';

it('lets a student choose a supported width and see the resulting type before saving', () => {
  const line = [[-114, 51], [-113.998, 51]];
  const initial = STREET_ASSETS.find(a => a.model.variantId === 'student_main_street_v1')!;
  const target = STREET_ASSETS.find(a => a.model.variantId === 'student_market_street_v1')!;
  const zone = { id: 'street', project_id: 'project', color: '#777', sort_order: 0, created_at: '', updated_at: '', zone_type: 'road', coordinates: bufferLineToPolygon(line, initial.sectionWidth), properties: { ...initial.properties, plan_centerline: line } } as SiteZone;
  const save = vi.fn(); render(<StreetDesignControls zone={zone} disabled={false} onSave={save} />);
  // Import and render the actual mixed roster: fixed fixtures must not crash route controls.
  expect(CANONICAL_CHOICES.filter(c => c.domain === 'street_pathway')).toHaveLength(7);
  const types = screen.getByLabelText('Street type') as HTMLSelectElement;
  expect(Array.from(types.options, option => option.value).sort()).toEqual(
    STREET_ASSETS.map(a => String(a.properties.road_archetype_id)).sort());
  fireEvent.change(screen.getByLabelText('Street width'), { target: { value: String(target.sectionWidth) } });
  expect(types.value).toBe(target.properties.road_archetype_id);
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
