import type { SiteZoneProperties } from '@/types';

export function siteBoundaryOpacity(properties: SiteZoneProperties = {}): number {
  const value = properties.site_boundary_opacity;
  return typeof value === 'number' && Number.isFinite(value)
    ? Math.max(0, Math.min(1, value))
    : properties.community_3d_mask_existing_tiles === false ? 0 : 1;
}
