import type { SiteZone, SiteZoneProperties } from '@/types';

/** Site settings are a form draft, but landscape writes and compilation save
 * independently. Saving other settings must retain their latest saved state. */
export function mergeSavedSiteLandscape(draft: SiteZoneProperties, saved: SiteZoneProperties): SiteZoneProperties {
  return {...draft,
    community_3d_landscape: saved.community_3d_landscape,
    community_3d_landscape_mode: saved.community_3d_landscape_mode,
    community_3d_automatic_trees: saved.community_3d_automatic_trees,
  };
}

/** New sites opt out. Retain existing automatic landscapes until explicitly
 * switched off; separately applied landscape presets own their own planting. */
export function automaticSiteTreesEnabled(zone: SiteZone | null | undefined): boolean {
  const properties = zone?.properties;
  if (!properties || properties.community_3d_landscape_mode === 'generated') return false;
  if (typeof properties.community_3d_automatic_trees === 'boolean') return properties.community_3d_automatic_trees;
  return properties.community_3d_landscape_mode !== 'placed_objects_only'
    && Boolean(properties.community_3d_landscape);
}
