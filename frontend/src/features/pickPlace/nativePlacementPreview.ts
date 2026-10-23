import type { PlaceAsset } from './assetRegistry';
import { publicRealmReleaseRow, publicRealmReleaseAllowed, releaseGateErrors } from './publicRealmRelease';

/** Bind the cursor preview to the same exact fixed scene as saved placement. */
export function nativePlacementPreviewUrl(asset: PlaceAsset | null): string | null {
  if (!asset) return null;
  if (asset.model.method === 'fixed_public_realm_v1' || asset.id.startsWith('claude_public_realm:')) {
    const row = publicRealmReleaseRow(asset.id);
    return row && publicRealmReleaseAllowed(row)
      && !releaseGateErrors({ ...row, asset }).includes('identity_mismatch') ? row.fixture.url : null;
  }
  return typeof asset.properties.validation_native_url === 'string' ? asset.properties.validation_native_url : null;
}
