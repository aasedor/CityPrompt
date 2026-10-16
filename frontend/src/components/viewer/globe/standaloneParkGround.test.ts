import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';

const park = (id: string, height: unknown, extra = {}) => ({ id, zone_type: 'green_space',
  project_id: 'qa', color: '#66874f', sort_order: 0, created_at: '', updated_at: '',
  coordinates: [[1, 1], [3, 1], [3, 3], [1, 3]],
  properties: { green_space_native_layout: { layout_id: 'native' }, terrain_elevation_m: height, ...extra },
}) as unknown as SiteZone;

describe('independent prepared park footprints', () => {
  it('keeps multiple standalone parks on their individual saved datums after reload', () => {
    const parks = JSON.parse(JSON.stringify([park('one', 1031.2), park('two', 1044.5)])) as SiteZone[];
    expect(parks.map(p => resolvePreparedSiteTerrainForZone(p, parks, 999))).toEqual([1031.2, 1044.5]);
  });
  it.each([undefined, null, true, '1044', NaN, Infinity])('never invents standalone ground from %s', height => {
    const p = park('park', height);
    expect(resolvePreparedSiteTerrainForZone(p, [p], 999)).toBeNull();
  });
  it.each([{ community_3d_mask_existing_tiles: false }, { terrain_strategy: 'landscape' }, { park_terrain: {} }])('preserves explicit ground restrictions %s', props => {
    const p = park('park', 1044, props);
    expect(resolvePreparedSiteTerrainForZone(p, [p], 999)).toBeNull();
  });
  it('uses the prepared boundary when present and never bypasses its extent or retained terrain', () => {
    const p = park('park', 1044);
    const boundary = { ...p, id: 'site', zone_type: 'site_boundary', is_active_boundary: true,
      coordinates: [[0, 0], [4, 0], [4, 4], [0, 4]],
      properties: { terrain_elevation_m: 1030, community_3d_mask_existing_tiles: true } } as SiteZone;
    expect(resolvePreparedSiteTerrainForZone(p, [boundary, p], 999)).toBe(1030);
    expect(resolvePreparedSiteTerrainForZone(p, [{ ...boundary, coordinates: [[5, 5], [6, 5], [6, 6]] }, p], 999)).toBeNull();
    expect(resolvePreparedSiteTerrainForZone(p, [{ ...boundary, properties: { community_3d_mask_existing_tiles: false } }, p], 999)).toBeNull();
  });
  it('does not change buildings or ordinary terrain-following parks', () => {
    for (const p of [ { ...park('building', 1044), zone_type: 'building' } as SiteZone,
      { ...park('plain', 1044), properties: { terrain_elevation_m: 1044 } } ])
      expect(resolvePreparedSiteTerrainForZone(p, [p], 999)).toBeNull();
  });
});
