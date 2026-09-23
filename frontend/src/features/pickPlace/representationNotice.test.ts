import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { representationNotice } from './representationNotice';
import { PARK_TRIO_ASSETS } from './parkTrioAssets';

describe('saved representation notice', () => {
  it('explains both fallback kinds from a reloaded snapshot without a running job', () => {
    const base = { project_id: 'project', coordinates: [[0, 0], [0, 1], [1, 1]], color: '#ccc', sort_order: 0, created_at: '', updated_at: '' };
    const zones: SiteZone[] = [{ ...base, id: 'building', zone_type: 'building', properties: { community_3d: {
      schema_version: 1, state: 'compiled', kind: 'building', generator: 'planned_massing', compiled_at: '2026-09-16',
    } } }, { ...base, id: 'park', zone_type: 'green_space', properties: { public_realm_fallback: { state: 'family_pending' } } }];
    const message = representationNotice(JSON.parse(JSON.stringify(zones)));
    expect(message).toContain('1 building is shown as design massing');
    expect(message).toContain('1 park or street has a simplified layout');
  });
  it('does not imply a fallback for ordinary uncompiled or detailed zones', () => {
    expect(representationNotice([{ properties: {} }] as SiteZone[])).toBe('');
  });
  it('distinguishes an exact adaptive garden from an unsupported sibling after reload', () => {
    const garden = PARK_TRIO_ASSETS.find(asset => asset.id === 'park_trio_garden')!;
    const saved = JSON.parse(JSON.stringify({ zone_type: 'green_space', properties: {
      ...garden.properties, public_realm_fallback: { state: 'family_pending' },
    } })) as SiteZone;
    expect(representationNotice([saved])).toBe('1 park uses an adaptive 3D layout; available features depend on its outline.');
    const sibling = { ...saved, properties: { ...saved.properties, green_space_selected_variant_id: 'other' } };
    expect(representationNotice([sibling])).toContain('1 park or street has a simplified layout');
    expect(representationNotice([saved, sibling])).toContain('1 park or street has a simplified layout');
  });
});
