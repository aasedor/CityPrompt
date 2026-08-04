import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from './siteBoundary';

function boundary(id: string, active?: boolean): SiteZone {
  return {
    id,
    project_id: 'project-1',
    zone_type: 'site_boundary',
    coordinates: [[0, 0], [2, 0], [2, 2]],
    color: '#f59e0b',
    properties: {},
    ...(active === undefined ? {} : { is_active_boundary: active }),
    sort_order: 0,
    created_at: '2026-08-03T00:00:00Z',
    updated_at: '2026-08-03T00:00:00Z',
  };
}

describe('getActiveSiteBoundary', () => {
  it('chooses the explicit active boundary over preserved inactive duplicates', () => {
    expect(getActiveSiteBoundary([boundary('old', false), boundary('active', true)])?.id)
      .toBe('active');
  });

  it('does not reactivate an explicitly inactive legacy boundary', () => {
    expect(getActiveSiteBoundary([boundary('old', false)])).toBeNull();
  });

  it('supports pre-migration zone fixtures without an active flag', () => {
    expect(getActiveSiteBoundary([boundary('legacy')])?.id).toBe('legacy');
  });
});
