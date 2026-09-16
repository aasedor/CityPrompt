import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { StreetDesignControls } from './StreetDesignControls';
import { LOCAL_STREET_ASSET } from './assetRegistry';
import { bufferLineToPolygon } from '@/utils/roadGeometry';

it('lets a student choose a supported width and see the resulting type before saving', () => {
  const line = [[-114, 51], [-113.998, 51]];
  const zone = { id: 'street', project_id: 'project', color: '#777', sort_order: 0, created_at: '', updated_at: '', zone_type: 'road', coordinates: bufferLineToPolygon(line, 16), properties: { ...LOCAL_STREET_ASSET.properties, plan_centerline: line } } as SiteZone;
  const save = vi.fn(); render(<StreetDesignControls zone={zone} disabled={false} onSave={save} />);
  fireEvent.change(screen.getByLabelText('Street width'), { target: { value: '20' } });
  expect((screen.getByLabelText('Street type') as HTMLSelectElement).value).toBe('calgary_collector');
  fireEvent.click(screen.getByRole('button', { name: 'Apply street' }));
  expect(save.mock.calls[0][0].properties).toMatchObject({ road_archetype_id: 'calgary_collector', width: 20, plan_centerline: line });
});
