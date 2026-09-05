import type { SiteZone } from '@/types';

interface GlobeTileMaskLayerProps {
  zones: SiteZone[];
  terrainHeight: number;
}

/** Compatibility mount point. TileStencilPatcher now owns world-space cuts.
 * Never substitute projected stencil prisms when an exact mask is invalid or
 * exceeds capacity: their side walls erase unrelated buildings behind the site
 * in oblique views and also contaminate clean captures. Keep context intact. */
export function GlobeTileMaskLayer(_props: GlobeTileMaskLayerProps) {
  return null;
}
