import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { placeAsset, placementProperties } from '@/features/pickPlace/catalogue';
import { deriveItems } from './communityCompiler';

describe('house footprint compilation', () => {
  it('compiles the requested model scale inside the unchanged placement parcel', () => {
    const asset = placeAsset('trial_edwardian_foursquare');
    const coordinates = rectangleAt([-114.04677, 51.04542], asset.width, asset.depth, 22);
    const zone = {
      id: 'house', project_id: 'project', zone_type: 'building', coordinates,
      name: 'Flexible Foursquare', color: '#fff', sort_order: 0,
      created_at: 'now', updated_at: 'now',
      properties: { ...placementProperties(asset), building_footprint_scale: 0.85 },
    } as SiteZone;

    const item = deriveItems([zone])[0];
    expect(item.targets.width_m).toBeCloseTo(asset.footprintProgram!.nativeWidthM * 0.85, 6);
    expect(item.targets.depth_m).toBeCloseTo(asset.footprintProgram!.nativeDepthM * 0.85, 6);
    expect(zone.coordinates).toEqual(coordinates);
  });
});
