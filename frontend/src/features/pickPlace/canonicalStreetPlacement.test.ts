import { expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { canonicalStreetAsset, streetDesignUpdate } from './canonicalStreetPlacement';
import { streetAssetForZone, streetCoordinateUpdate } from './streetPlacement';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';

it('uses the rendered section width for every current eligible street variant', () => {
  for (const choice of CANONICAL_CHOICES.filter(c => c.domain === 'street_pathway')) {
    for (const variant of choice.option.variants ?? [undefined]) {
      const asset = canonicalStreetAsset({ choice, variant });
      expect(asset.sectionWidth).toBeGreaterThan(0);
      expect(resolvePilotStreetSectionProfile({ properties: asset.properties })?.rowM).toBe(asset.sectionWidth);
      expect(streetAssetForZone({ zone_type: 'road', properties: asset.properties })?.sectionWidth).toBe(asset.sectionWidth);
    }
  }
});

it('changes width and identity atomically, retaining the exact authored route', () => {
  const line = [[-114, 51], [-113.998, 51]];
  const zone = { id: 'street', project_id: 'project', color: '#777', sort_order: 0, created_at: '', updated_at: '', zone_type: 'road', coordinates: bufferLineToPolygon(line, 16), properties: { plan_centerline: line, terrain_elevation_m: 1100, public_realm_lego: { stale: true } } } as SiteZone;
  const choice = CANONICAL_CHOICES.find(c => c.option.id === 'calgary_collector')!;
  const asset = canonicalStreetAsset({ choice, variant: choice.option.variants![0] });
  const update = streetDesignUpdate(zone, asset);
  expect(update.properties.plan_centerline).toEqual(line);
  expect(update.properties.terrain_elevation_m).toBe(1100);
  expect(update.properties.public_realm_lego).toBeUndefined();
  expect(update.properties.width).toBe(20);
  expect(update.coordinates).toEqual(bufferLineToPolygon(line, 20));
  const moved = streetCoordinateUpdate({ ...zone, ...update }, update.coordinates.map(([x, y]) => [x, y + .0001]));
  expect(moved.properties?.width).toBe(20);
  expect(streetAssetForZone({ ...zone, ...moved })?.sectionWidth).toBe(20);
});
