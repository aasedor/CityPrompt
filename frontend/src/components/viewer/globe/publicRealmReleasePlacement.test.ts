import { describe, expect, it, vi } from 'vitest';
import { Group } from 'three';
import type { SiteZone } from '@/types';
import manifest from '@/data/publicRealmRelease20261023.json';
import { rectangleAt, resizeRectangleCorner } from '@/features/pickPlace/geometry';
import { publicRealmTrialAsset, publicRealmTrialPlacement, publicRealmTrialGroundCells, assertPublicRealmTrialsReady } from './publicRealmTrial';

vi.mock('@/features/pickPlace/publicRealmRelease', async () => {
  const actual = await vi.importActual<typeof import('@/features/pickPlace/publicRealmRelease')>('@/features/pickPlace/publicRealmRelease');
  return { ...actual, publicRealmReleaseAllowed: (row: Parameters<typeof actual.publicRealmReleaseAllowed>[0]) => actual.publicRealmReleaseRows(true, [row], true).length === 1 };
});
const row = manifest.models.find(row => row.candidate === 'clay-ice-rink-market-square-clay-v007-park-only-r001')!;
const origin = [-114.04, 51.04];
const common = { project_id: 'test', color: '#668545', sort_order: 0, created_at: '2026-10-23', updated_at: '2026-10-23' };
const boundary = { ...common, id: 'site', zone_type: 'site_boundary', is_active_boundary: true,
  coordinates: rectangleAt(origin, 1000, 1000), properties: { community_3d_mask_existing_tiles: true, terrain_elevation_m: 1042 } } as SiteZone;
const zone = { ...common, id: 'rink', zone_type: row.asset.zoneType, coordinates: rectangleAt(origin, row.asset.width, row.asset.depth, 23),
  properties: { ...row.asset.properties, pick_place_asset: row.asset.id, pick_place_model_revision: row.runtime_sha256,
    pick_place_definition_version: row.asset.definitionVersion } } as SiteZone;

describe('fixed public-realm release native placement', () => {
  it('accepts the actual saved 15-degree rink at the prepared boundary datum despite its stale server fallback marker', () => {
    const saved = { ...zone, coordinates: [
      [-114.0439076433427, 51.04271084344462], [-114.04312100071138, 51.04284336846771],
      [-114.04340573895438, 51.04351149897996], [-114.0441923815857, 51.04337897395687],
    ], properties: { ...zone.properties, terrain_elevation_m: 1023.0044807038905,
      public_realm_fallback: { schema_version: 1, state: 'family_pending', kind: 'park', generator: 'park_kit',
        archetype_id: 'outdoor_ice_rink', variant_id: 'outdoor_ice_rink_v0', target_source: 'zone_geometry' },
    } } as SiteZone;
    const site = { ...boundary, coordinates: [
      [-114.0487507271552, 51.04153422206252], [-114.03874927284481, 51.04153422206252],
      [-114.03874927284481, 51.04602577793747], [-114.0487507271552, 51.04602577793747],
    ], properties: { community_3d_mask_existing_tiles: true, terrain_strategy: 'flatten', terrain_elevation_m: 1025.6715063261545 } } as SiteZone;
    const placement = publicRealmTrialPlacement(saved, [site, saved], 0);
    expect(placement?.asset.url).toBe(row.fixture.url);
    expect(placement?.asset.sha256).toBe(row.runtime_sha256);
    expect(placement?.height).toBe(1025.6715063261545);
    expect(placement?.yaw).toBeCloseTo(15*Math.PI/180, 6);
  });
  it.each([
    ['clay-halifax-public-gardens-clay-v005-park-only-r001', '9282a9ffd6a31997407cff90ebaea2c95e7ece983746d33e42f1c6e9ae154b79'],
    ['clay-princes-island-park-clay-v005', '498a973435fc8bc077084d3ee630babc55574a7365fdbd978a1cea742525a0ec'],
  ])('retains exact raw marker %s rather than substituting its optimized replacement', (candidate, digest) => {
    const raw = manifest.models.find(row => row.candidate === candidate)!;
    const optimized = manifest.models.find(row => row.candidate === candidate+'-gpu-r001')!;
    const rawZone = { ...zone, coordinates: rectangleAt(origin, raw.asset.width, raw.asset.depth), properties: {
      ...raw.asset.properties, pick_place_asset: raw.asset.id, pick_place_model_revision: raw.runtime_sha256,
      pick_place_definition_version: raw.asset.definitionVersion,
    } } as SiteZone;
    expect(publicRealmTrialAsset(rawZone)?.sha256).toBe(raw.runtime_sha256);
    expect(publicRealmTrialAsset(rawZone)?.url).toBe(raw.fixture.url);
    expect(publicRealmTrialPlacement(rawZone, [boundary], 0)).toBeNull();
    const optimizedZone = { ...rawZone, properties: {
      ...optimized.asset.properties, pick_place_asset: optimized.asset.id, pick_place_model_revision: optimized.runtime_sha256,
      pick_place_definition_version: optimized.asset.definitionVersion,
    } } as SiteZone;
    expect(publicRealmTrialAsset(optimizedZone)?.sha256).toBe(digest);
    expect(publicRealmTrialPlacement(optimizedZone, [boundary], 0)?.asset.sha256).toBe(digest);
  });
  it('uses the exact bytes, authored ground, fixed dimensions and shared site datum', () => {
    expect(publicRealmTrialAsset(zone)?.sha256).toBe(row.runtime_sha256);
    expect(publicRealmTrialGroundCells(publicRealmTrialAsset(zone)!)).toEqual([]);
    const placement = publicRealmTrialPlacement(zone, [boundary, zone], 0)!;
    expect(placement.height).toBe(1042);
    expect(placement.yaw).toBeCloseTo(23 * Math.PI / 180);
    expect(publicRealmTrialPlacement(zone, [], 0)).toBeNull();
    expect(publicRealmTrialPlacement({ ...zone, coordinates: rectangleAt(origin, row.asset.width + 1, row.asset.depth) }, [boundary], 0)).toBeNull();
    expect(resizeRectangleCorner(zone.coordinates, 0, origin, row.asset as never)).toEqual(zone.coordinates);
  });

  it('retains unsupported markers for unknown, stale, pending or redirected saved claims', () => {
    for (const mutation of [
      { pick_place_model_revision: '0'.repeat(64) }, { native_public_realm_url: '/other.glb' },
      { public_realm_release_asset: 'claude_public_realm:unknown:123' },
      { public_realm_release_asset: '' }, { public_realm_release_asset: null },
      { pick_place_definition_version: 99 }, { green_space_selected_variant_id: 'other' },
      { validation_fixed_fixture: true }, { _plan_scenario: 'ai-route' },
    ]) {
      const stale = { ...zone, properties: { ...zone.properties, ...mutation } };
      expect(publicRealmTrialAsset(stale)).not.toBeNull();
      expect(publicRealmTrialPlacement(stale, [boundary], 0)).toBeNull();
    }
    const pending = manifest.models.find(row => row.candidate !== 'clay-ice-rink-market-square-clay-v007-park-only-r001')!;
    const saved = { ...zone, properties: { public_realm_release_asset: pending.asset.id } };
    expect(publicRealmTrialAsset(saved)).not.toBeNull();
    expect(publicRealmTrialPlacement(saved, [boundary], 0)).toBeNull();
    const scene = new Group(); scene.userData.publicRealmTrialStatus = 'unsupported';
    expect(() => assertPublicRealmTrialsReady(scene)).toThrow('not ready');
  });
});
