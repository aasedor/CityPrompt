import manifest from '@/data/publicRealmRelease20261023.json';
import type { PlaceAsset } from './assetRegistry';

export interface PublicRealmReleaseFixture {
  id: string; title: string; kind: string; dimensions: number[]; sha256: string; url: string;
  surfaceRegions: { x: number; y: number; width: number; depth: number; material: string | null }[];
  preserveNativeGround: boolean; centerNativeClay: boolean;
}
export interface PublicRealmReleaseRow {
  candidate: string; category: string; source_sha256: string; review_sha256: string;
  runtime_sha256: string; thumbnail_sha256: string; status: string;
  visual_review: { status: string; scope: string; runtime_sha256: string; evidence_sha256: string | null;
    unresolved_p0: number | null; unresolved_p1: number | null };
  runtime_review: { status: string; runtime_sha256: string; evidence_sha256: string | null };
  asset: PlaceAsset; fixture: PublicRealmReleaseFixture;
}
const rows = manifest.models as unknown as PublicRealmReleaseRow[];
const sha = (value: unknown): value is string => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);

/** The local correction review closes context removal only. Production also
 * needs a complete review of these exact runtime bytes and ordinary UI proof. */
export function releaseGateErrors(row: PublicRealmReleaseRow): string[] {
  const errors: string[] = [];
  const { asset, fixture } = row;
  const prefix = row.category === 'park' ? '/park-kits/claude-20261023/' : '/street-kits/claude-20261023/';
  const variant = asset.zoneType === 'green_space' ? asset.properties.green_space_selected_variant_id : asset.properties.road_selected_variant_id;
  if (!sha(row.source_sha256) || !sha(row.review_sha256) || !sha(row.runtime_sha256) || !sha(row.thumbnail_sha256)
    || !asset.id.startsWith('claude_public_realm:') || !asset.id.endsWith(`:${row.runtime_sha256.slice(0, 12)}`)
    || asset.kind !== 'object' || asset.reshapeMode !== 'fixed_native' || asset.model.method !== 'fixed_public_realm_v1'
    || !['park', 'street'].includes(row.category) || asset.zoneType !== (row.category === 'park' ? 'green_space' : 'road')
    || asset.model.revision !== row.runtime_sha256 || variant !== asset.model.variantId
    || asset.properties.public_realm_release_asset !== asset.id || asset.properties.native_public_realm_url !== fixture.url
    || asset.properties.validation_fixed_fixture != null || asset.properties.validation_native_url != null || asset.properties.public_realm_trial_asset != null
    || fixture.id !== asset.id || fixture.sha256 !== row.runtime_sha256 || fixture.kind !== row.category
    || fixture.url !== `${prefix}${row.runtime_sha256}.glb`
    || ![`${prefix}${row.thumbnail_sha256}.jpg`, `${prefix}${row.thumbnail_sha256}.png`].includes(asset.thumbnail)
    || fixture.dimensions.length !== 2 || fixture.dimensions[0] !== asset.width || fixture.dimensions[1] !== asset.depth
    || asset.minWidth !== asset.width || asset.minDepth !== asset.depth || asset.maxWidth !== asset.width || asset.maxDepth !== asset.depth
    || ![asset.width, asset.depth, ...(asset.nativeDimensions ?? [])].every(value => Number.isFinite(value) && value > 0)
    || asset.nativeDimensions?.length !== 3 || asset.nativeDimensions[0] > asset.width || asset.nativeDimensions[1] > asset.depth
    || !fixture.preserveNativeGround || !fixture.centerNativeClay) errors.push('identity_mismatch');
  const visual = row.visual_review;
  if (visual.status !== 'passed' || visual.scope !== 'complete_runtime_derivative'
    || visual.runtime_sha256 !== row.runtime_sha256 || !sha(visual.evidence_sha256)
    || visual.unresolved_p0 !== 0 || visual.unresolved_p1 !== 0) errors.push('visual_review_pending');
  const runtime = row.runtime_review;
  if (runtime.status !== 'passed' || runtime.runtime_sha256 !== row.runtime_sha256 || !sha(runtime.evidence_sha256)) errors.push('runtime_review_pending');
  return errors;
}

export function publicRealmReleaseRows(localRehearsal: boolean, candidates = rows, includeRetired = false): PublicRealmReleaseRow[] {
  if (manifest.schema !== 'cityprompt.fixed-public-realm-release@1') return [];
  return candidates.filter(row => {
    const errors = releaseGateErrors(row);
    if (errors.includes('identity_mismatch')) return false;
    if (localRehearsal && row.status === 'runtime_trial') return true;
    return (row.status === 'ready' || (includeRetired && row.status === 'retired')) && errors.length === 0;
  });
}
const localRehearsal = import.meta.env.DEV && import.meta.env.MODE === 'development';
export const PUBLIC_REALM_RELEASE_ASSETS = publicRealmReleaseRows(localRehearsal).map(row => ({ ...row.asset,
  readiness: row.status === 'ready' ? 'ready' as const : 'pilot' as const }));
export const PUBLIC_REALM_RELEASE_SAVED_ASSETS = publicRealmReleaseRows(localRehearsal, rows, true).map(row => ({ ...row.asset,
  readiness: row.status === 'retired' ? 'retired' as const : row.status === 'ready' ? 'ready' as const : 'pilot' as const }));
/** Unlike discovery, known claims retain an error marker when disabled/stale.
 * Placement below decides whether their exact runtime bytes may be mounted. */
export function publicRealmReleaseRow(id: unknown): PublicRealmReleaseRow | undefined {
  return rows.find(row => row.asset.id === id);
}
export function publicRealmReleaseAllowed(row: PublicRealmReleaseRow): boolean {
  return publicRealmReleaseRows(localRehearsal, [row], true).length === 1;
}
