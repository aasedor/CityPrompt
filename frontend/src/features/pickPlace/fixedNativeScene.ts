import type { SiteZoneProperties } from '@/types';

/** Fixed authored scenes cannot inherit procedural route or reshape controls.
 * Treat even an unavailable saved release claim as fixed until it is repaired. */
export function isFixedNativeScene(properties?: SiteZoneProperties | null): boolean {
  return properties?.validation_fixed_fixture === true
    || [properties?.public_realm_release_asset, properties?.pick_place_asset].some(value =>
      typeof value === 'string' && value.startsWith('claude_public_realm:'));
}
