/**
 * Park kit asset manifest — maps prop ids to cached GLB urls served through
 * the /api/v1/files proxy (MinIO). Assets are generated ONCE via the
 * archetype-cache pre-warm pipeline (Meshy text mode, e.g. "a park bench,
 * single object, low poly") and uploaded under the stable kits/ namespace.
 *
 * targetHeight_m drives normalization: each GLB is uniformly scaled so its
 * height matches the real-world dimension (from PARK_FURNITURE /
 * PLAYGROUND_EQUIPMENT in archetypeMetadataSchema), base at origin.
 *
 * A missing/unreachable GLB is fine — GlobeParkKitLayer falls back to the
 * procedural placeholder for that prop.
 */

import type { ParkPropId } from '../components/viewer/globe/parkScatter';

export interface ParkKitAsset {
  url: string;
  targetHeight_m: number;
  /** ~triangle budget the asset was generated with (trees are instanced
   *  hundreds of times — keep them low-poly). */
  maxTriangles?: number;
}

export const PARK_KIT_MANIFEST: Partial<Record<ParkPropId, ParkKitAsset>> = {
  tree: { url: '/api/v1/files/kits/park-tree.glb', targetHeight_m: 9, maxTriangles: 5000 },
  bench: { url: '/api/v1/files/kits/park-bench.glb', targetHeight_m: 0.9 },
  playground: { url: '/api/v1/files/kits/park-playground.glb', targetHeight_m: 2.8 },
  pavilion: { url: '/api/v1/files/kits/park-pavilion.glb', targetHeight_m: 3.8 },
};
