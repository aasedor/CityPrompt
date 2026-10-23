import type { Object3D } from 'three';
import type { SiteZone } from '@/types';
import assets from './publicRealmTrialAssets.json';
import claudeTrial from '@/data/claudeAssetLocalTrial.json';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import { publicRealmReleaseRow, publicRealmReleaseAllowed, type PublicRealmReleaseFixture } from '@/features/pickPlace/publicRealmRelease';

// The coloured preview underlays are rebuilt on prepared terrain. Fine paving
// units and painted symbols remain in the native GLB above that owned ground.
export const TRIAL_GROUND_MATERIALS = new Set(['grass', 'paving', 'soil', 'cycle', 'asphalt']);
export type PublicRealmTrialAsset = typeof assets[number] | NonNullable<typeof claudeTrial.models[number]['fixture']> | PublicRealmReleaseFixture;
const localClaudeFixtures = import.meta.env.DEV
  ? claudeTrial.models.flatMap(row => row.fixture ? [row.fixture] : []) : [];
export function publicRealmTrialAsset(zone: SiteZone): PublicRealmTrialAsset | null {
  const savedRelease = String(zone.properties?.pick_place_asset).startsWith('claude_public_realm:');
  const claim = zone.properties?.public_realm_release_asset ?? (savedRelease ? zone.properties?.pick_place_asset : undefined);
  if (zone.properties?.public_realm_release_asset !== undefined || savedRelease) return publicRealmReleaseRow(claim)?.fixture ?? {
    id: String(claim), title: 'Unavailable fixed public-realm model', kind: zone.zone_type === 'road' ? 'street' : 'park',
    dimensions: [0, 0], sha256: '', url: '', surfaceRegions: [], preserveNativeGround: true, centerNativeClay: true,
  };
  if (!import.meta.env.DEV) return null;
  return [...assets, ...localClaudeFixtures].find(asset => asset.id === zone.properties?.public_realm_trial_asset) ?? null;
}

/** A bounded local review contract, deliberately not a catalogue/compiler claim.
 * Native rectangle only. Shared prepared ground is mandatory; no slope fallback,
 * contain scaling, concave clipping, route bending, or hard-coded site elevation. */
export function publicRealmTrialPlacement(zone: SiteZone, zones: SiteZone[], fallback: number) {
  const asset = publicRealmTrialAsset(zone);
  if (asset && (zone.properties?.public_realm_release_asset !== undefined || asset.id.startsWith('claude_public_realm:'))) {
    const row = publicRealmReleaseRow(asset.id);
    const properties = zone.properties ?? {};
    if (!row || !publicRealmReleaseAllowed(row) || zone.zone_type !== row.asset.zoneType
      || properties.pick_place_asset !== asset.id || properties.public_realm_release_asset !== asset.id
      || properties.pick_place_model_revision !== asset.sha256 || properties.native_public_realm_url !== asset.url
      || properties.pick_place_definition_version !== row.asset.definitionVersion
      || Object.entries(row.asset.properties).some(([key, value]) => properties[key] !== value)
      || properties.validation_fixed_fixture != null || properties.validation_native_url != null || properties.public_realm_trial_asset != null
      || properties._plan_scenario) return null;
  }
  // Identify invalid local fixtures above so they retain their readiness/error
  // marker; never display current bytes for a different saved revision.
  if (asset?.id.startsWith('claude_trial_') && (
    zone.properties?.pick_place_model_revision !== asset.sha256
    || zone.properties?.validation_native_url !== asset.url
    || zone.properties?.pick_place_asset !== asset.id
  )) return null;
  const boundary = getActiveSiteBoundary(zones);
  if (!asset || !boundary || boundary.properties?.community_3d_mask_existing_tiles !== true
    || boundary.properties?.terrain_strategy === 'landscape') return null;
  const ring = zone.coordinates.slice();
  if (ring.length === 5 && ring[0].every((v, i) => v === ring[4][i])) ring.pop();
  if (ring.length !== 4 || ring.some(p => p.length < 2 || !p.every(Number.isFinite))) return null;
  const lng = ring.reduce((n, p) => n + p[0], 0) / 4;
  const lat = ring.reduce((n, p) => n + p[1], 0) / 4;
  const east = metersPerDegLon(lat);
  const points = ring.map(p => [(p[0] - lng) * east, (p[1] - lat) * METERS_PER_DEG_LAT]);
  const yaw = Math.atan2(points[1][1] - points[0][1], points[1][0] - points[0][0]);
  const [w, d] = asset.dimensions;
  const corners = [[-w / 2, -d / 2], [w / 2, -d / 2], [w / 2, d / 2], [-w / 2, d / 2]];
  if (points.some((p, i) => Math.hypot(
    p[0] - (corners[i][0] * Math.cos(yaw) - corners[i][1] * Math.sin(yaw)),
    p[1] - (corners[i][0] * Math.sin(yaw) + corners[i][1] * Math.cos(yaw)),
  ) > 0.04)) return null;
  const height = resolvePreparedSiteTerrainForZone(zone, zones, fallback);
  return height === null || !Number.isFinite(height) ? null : { asset, lng, lat, yaw, height };
}

/** Same last-region-wins ownership as the reviewed authoring recipe. */
export function publicRealmTrialGroundCells(asset: PublicRealmTrialAsset) {
  if ('preserveNativeGround' in asset && asset.preserveNativeGround) return [];
  const [w, d] = asset.dimensions;
  const xs = [...new Set([-w / 2, w / 2, ...asset.surfaceRegions.flatMap(r => [r.x - r.width / 2, r.x + r.width / 2])])].sort((a, b) => a - b);
  const ys = [...new Set([-d / 2, d / 2, ...asset.surfaceRegions.flatMap(r => [r.y - r.depth / 2, r.y + r.depth / 2])])].sort((a, b) => a - b);
  const cells: { x: number; y: number; width: number; depth: number; material: string }[] = [];
  for (let i = 0; i < xs.length - 1; i++) for (let j = 0; j < ys.length - 1; j++) {
    const x = (xs[i] + xs[i + 1]) / 2, y = (ys[j] + ys[j + 1]) / 2;
    let material: string | null = 'grass';
    for (const r of asset.surfaceRegions) if (Math.abs(x - r.x) < r.width / 2 && Math.abs(y - r.y) < r.depth / 2) material = r.material;
    if (material) cells.push({ x, y, width: xs[i + 1] - xs[i], depth: ys[j + 1] - ys[j], material });
  }
  return cells;
}

export function assertPublicRealmTrialsReady(scene: Object3D | null) {
  scene?.traverse(object => {
    const state = object.userData.publicRealmTrialStatus;
    if (state && state !== 'ready') throw new Error('The fixed public-realm model is not ready. Keep its full native rectangle inside a prepared site and wait for its 3D asset to load.');
  });
}
