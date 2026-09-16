import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { ParkComponentControls } from './ParkComponentControls';

const zone: SiteZone = { id: 'park', project_id: 'project', zone_type: 'green_space',
  coordinates: [[0, 0], [1, 0], [1, 1]], color: '#00aa00', sort_order: 0,
  created_at: '2026-09-16', updated_at: '2026-09-16' };

vi.mock('@/components/viewer/globe/parkGroundProfiles', () => ({
  resolveParkSpecialtyStructureKind: (zone: SiteZone) => zone.properties?.public_realm_fallback ? null : 'skate_park_v0_assembly',
}));
it('saves seating while retaining the park identity and ground datum', () => {
  const props = { green_space_archetype_id: 'skate_park', terrain_elevation_m: 1095 };
  const onSave = vi.fn(); render(<ParkComponentControls zone={{ ...zone, properties: props }} disabled={false} onSave={onSave} />);
  fireEvent.change(screen.getByLabelText('Spectator bench position'), { target: { value: 'south' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply seating' }));
  expect(onSave).toHaveBeenCalledWith({ ...props, skate_spectator_edge: 'south' });
});
it('does not promise assembly edits for a simplified fallback park', () => {
  render(<ParkComponentControls zone={{ ...zone, properties: { public_realm_fallback: {} } }} disabled={false} onSave={vi.fn()} />);
  expect(screen.queryByLabelText('Spectator bench position')).toBeNull();
});
