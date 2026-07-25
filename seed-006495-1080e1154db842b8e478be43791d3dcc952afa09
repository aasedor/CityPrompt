import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';

import {
  parkTerrainSampleOffset,
  selectBudgetedLiveParkZones,
  stableParkDetailHash,
} from './parkDetailLod';

function zone(id: string, core = false): SiteZone {
  return {
    id,
    project_id: 'project',
    zone_type: 'green_space',
    coordinates: [[0, 0], [1, 0], [1, 1]],
    color: '#00aa55',
    sort_order: 0,
    created_at: '2026-07-21T00:00:00Z',
    updated_at: '2026-07-21T00:00:00Z',
    properties: { core },
  } as SiteZone;
}

describe('park live-program LOD', () => {
  it('keeps independent deterministic budgets for core and decorative parks', () => {
    const zones = [
      ...Array.from({ length: 12 }, (_, index) => zone(`core-${index}`, true)),
      ...Array.from({ length: 12 }, (_, index) => zone(`decorative-${index}`)),
    ];
    const select = (input: SiteZone[]) => selectBudgetedLiveParkZones(
      input,
      (candidate) => candidate.properties?.core === true,
      8,
      5,
    );
    const first = select(zones);
    const reversed = select([...zones].reverse());
    expect(first.filter((candidate) => candidate.properties?.core === true)).toHaveLength(8);
    expect(first.filter((candidate) => candidate.properties?.core !== true)).toHaveLength(5);
    expect(new Set(first.map((candidate) => candidate.id)))
      .toEqual(new Set(reversed.map((candidate) => candidate.id)));
  });

  it('spreads terrain sampling deterministically across the frame interval', () => {
    const offsets = Array.from({ length: 24 }, (_, index) => (
      parkTerrainSampleOffset(`park-${index}`, 30)
    ));
    expect(offsets.every((offset) => offset >= 0 && offset < 30)).toBe(true);
    expect(new Set(offsets).size).toBeGreaterThan(8);
    expect(parkTerrainSampleOffset('park-a', 30)).toBe(parkTerrainSampleOffset('park-a', 30));
    expect(stableParkDetailHash('park-a')).not.toBe(stableParkDetailHash('park-b'));
  });
});
