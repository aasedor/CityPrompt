import type { Object3D } from 'three';
import type { SiteZone } from '@/types';
import assets from './publicRealmTrialAssets.json';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';

// The coloured preview underlays are rebuilt on prepared terrain. Fine paving
// units and painted symbols remain in the native GLB above that owned ground.
export const TRIAL_GROUND_MATERIALS = new Set(['grass', 'paving', 'soil', 'cycle', 'asphalt']);
export type PublicRealmTrialAsset = typeof assets[number];
export function publicRealmTrialAsset(zone: SiteZone): PublicRealmTrialAsset | null {
  if (!import.meta.env.DEV) return null;
  return assets.find(asset => asset.id === zone.properties?.public_realm_trial_asset) ?? null;
}

/** A bounded local review contract, deliberately not a catalogue/compiler claim.
 * Native rectangle only. Shared prepared ground is mandatory; no slope fallback,
 * contain scaling, concave clipping, route bending, or hard-coded site elevation. */
export function publicRealmTrialPlacement(zone: SiteZone, zones: SiteZone[], fallback: number) {
  const asset = publicRealmTrialAsset(zone);
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
    if (state && state !== 'ready') throw new Error('The local public-realm model is not ready. Keep its full native rectangle inside a prepared site and wait for its 3D asset to load.');
  });
}
