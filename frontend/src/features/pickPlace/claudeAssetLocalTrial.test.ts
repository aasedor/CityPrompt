import { describe, expect, it, vi } from 'vitest';
import { Box3, BoxGeometry, Group, Mesh, MeshStandardMaterial, Vector3 } from 'three';
import { localClaudeAssets, LOCAL_CLAUDE_ASSETS } from './claudeAssetLocalTrial';
import { CATALOGUE_ASSETS, validateRegistry } from './assetRegistry';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { assetForZone, placementProperties } from './catalogue';
import { rectangleAt, resizeRectangleCorner } from './geometry';
import { publicRealmTrialAsset, publicRealmTrialPlacement } from '@/components/viewer/globe/publicRealmTrial';
import { trimNativeStreetModel } from '@/components/viewer/globe/nativeStreetModelTrim';
import type { SiteZone } from '@/types';
import trial from '@/data/claudeAssetLocalTrial.json';

// Exercise the development-only roster explicitly. Ordinary release tests
// must continue to cover the published catalogue rather than this local pilot.
vi.mock('./claudeAssetLocalTrial', async () => {
  const actual = await vi.importActual<typeof import('./claudeAssetLocalTrial')>('./claudeAssetLocalTrial');
  return { ...actual, LOCAL_CLAUDE_ASSETS: actual.localClaudeAssets(true),
    LOCAL_CLAUDE_SAVED_ASSETS: actual.localClaudeAssets(true, true) };
});

const origin = [-114.04677, 51.04542];
const boundary = { id: 'trial-site', zone_type: 'site_boundary', is_active_boundary: true,
  project_id: 'local-trial', color: '#668545', sort_order: 0,
  created_at: '2026-10-22', updated_at: '2026-10-22',
  coordinates: rectangleAt(origin, 1000, 1000), properties: {
    community_3d_mask_existing_tiles: true, terrain_elevation_m: 1042,
  } } as SiteZone;

describe('bounded Claude local model trial', () => {
  it('cannot expose local review assets through production discovery', () => {
    expect(localClaudeAssets(false)).toEqual([]);
    expect(localClaudeAssets(true).length).toBeGreaterThanOrEqual(3);
    expect(localClaudeAssets(true).every(a => a.readiness === 'pilot')).toBe(true);
  });

  it('registers one building, park and fixed street pilot without replacing any existing ID', () => {
    for (const suffix of ['cmu_dock_warehouse', 'ice_rink_market_square_park_only', 'inglewood_main_street']) {
      expect(LOCAL_CLAUDE_ASSETS.some(a => a.id === `claude_trial_${suffix}`)).toBe(true);
    }
    expect(validateRegistry(CATALOGUE_ASSETS)).toEqual([]);
    for (const asset of LOCAL_CLAUDE_ASSETS) {
      expect(CATALOGUE_ASSETS.filter(a => a.id === asset.id)).toHaveLength(1);
      expect(CANONICAL_CHOICES.filter(c => c.placements.some(a => a.id === asset.id))).toHaveLength(1);
      expect(asset.reshapeMode).toBe('fixed_native');
      expect(asset.properties.validation_fixed_fixture).toBe(true);
      expect(asset.width).toBeGreaterThanOrEqual(asset.nativeDimensions![0] + 3);
      expect(asset.depth).toBeGreaterThanOrEqual(asset.nativeDimensions![1] + 3);
    }
  });

  it('retires the context-heavy rink from discovery without losing its saved exact version', () => {
    expect(LOCAL_CLAUDE_ASSETS.some(a => a.id === 'claude_trial_ice_rink_market_square')).toBe(false);
    const old = trial.models.find(row => row.asset.id === 'claude_trial_ice_rink_market_square')!;
    const saved = { properties: placementProperties(old.asset as unknown as typeof LOCAL_CLAUDE_ASSETS[number]) };
    expect(assetForZone(saved)?.id).toBe(old.asset.id);
    expect(publicRealmTrialAsset(saved as SiteZone)?.sha256).toBe(old.source_sha256);
  });

  it('preserves exact saved model revisions and rejects stretching', () => {
    for (const asset of LOCAL_CLAUDE_ASSETS) {
      const coordinates = rectangleAt(origin, asset.width, asset.depth, 37);
      const saved = JSON.parse(JSON.stringify({ coordinates, properties: placementProperties(asset, 1042, coordinates) }));
      expect(assetForZone(saved)?.id).toBe(asset.id);
      expect(saved.properties.pick_place_model_revision).toBe(asset.model.revision);
      expect(resizeRectangleCorner(coordinates, 0, origin, asset)).toEqual(coordinates);
    }
  });

  it('requires prepared level ground for the complete fixed public-realm scene', () => {
    for (const asset of LOCAL_CLAUDE_ASSETS.filter(a => a.zoneType !== 'building')) {
      const zone = { id: asset.id, zone_type: asset.zoneType,
        coordinates: rectangleAt(origin, asset.width, asset.depth, 23),
        properties: placementProperties(asset) } as SiteZone;
      const fixture = publicRealmTrialAsset(zone)!;
      expect(fixture.sha256).toMatch(/^[a-f0-9]{64}$/);
      expect(fixture.preserveNativeGround).toBe(true);
      const placement = publicRealmTrialPlacement(zone, [boundary, zone], 0)!;
      expect(placement.height).toBe(1042);
      expect(placement.yaw).toBeCloseTo(23 * Math.PI / 180);
      expect(publicRealmTrialPlacement(zone, [], 0)).toBeNull();
      expect(publicRealmTrialPlacement({ ...zone, coordinates: rectangleAt(origin, asset.width + 1, asset.depth) }, [boundary], 0)).toBeNull();
      for (const mismatch of [{ pick_place_model_revision: 'unknown-old-version' }, { validation_native_url: '/wrong.glb' }]) {
        const stale = { ...zone, properties: { ...zone.properties, ...mismatch } };
        expect(publicRealmTrialAsset(stale)).not.toBeNull(); // Keep the error marker, never a generic fallback.
        expect(publicRealmTrialPlacement(stale, [boundary, stale], 0)).toBeNull();
      }
    }
  });

  it('centres asymmetric native public-realm clones without changing shared source geometry', () => {
    const scene = new Group();
    const mesh = new Mesh(new BoxGeometry(10, 4, 20), new MeshStandardMaterial());
    mesh.position.set(17, 5, -13); scene.add(mesh);
    scene.updateMatrixWorld(true);
    const original = new Box3().setFromObject(scene);
    const asset = LOCAL_CLAUDE_ASSETS.find(a => a.zoneType === 'road')!;
    const zone = { properties: placementProperties(asset) } as SiteZone;
    const fixture = publicRealmTrialAsset(zone)!;
    const result = trimNativeStreetModel(scene, { asset: fixture, lng: 0, lat: 0, yaw: 0, height: 0 }, []);
    const bounds = new Box3().setFromObject(result.clone);
    expect(bounds.getSize(new Vector3()).toArray()).toEqual([10, 4, 20]);
    expect(bounds.min.y).toBe(0);
    expect(bounds.getCenter(new Vector3()).x).toBe(0);
    expect(bounds.getCenter(new Vector3()).z).toBe(0);
    expect(new Box3().setFromObject(scene)).toEqual(original);
    expect(mesh.position.toArray()).toEqual([17, 5, -13]);
  });
});
