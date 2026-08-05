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
  /** Keep a metric program anchor such as the base of a basketball post. */
  preserveHorizontalOrigin?: boolean;
  footprint_m?: { width: number; depth: number };
  clearance_m?: number;
  /** ~triangle budget the asset was generated with (trees are instanced
   *  hundreds of times — keep them low-poly). */
  maxTriangles?: number;
}

const GENERATED_PARK_KITS_READY = import.meta.env.VITE_PARK_KIT_ASSETS_READY === 'true';

// Do not issue guaranteed 404s for stable URLs until the one-time kit
// generation job has actually populated them. GlobeParkKitLayer supplies a
// detailed procedural kit in the meantime, so parks remain visually complete
// without noisy failed requests on every load.
export const PARK_KIT_MANIFEST: Partial<Record<ParkPropId, ParkKitAsset>> = {
  ...(GENERATED_PARK_KITS_READY
    ? {
      tree: { url: '/api/v1/files/kits/park-tree.glb', targetHeight_m: 9, maxTriangles: 5000 },
      bench: { url: '/api/v1/files/kits/park-bench.glb', targetHeight_m: 0.9 },
      playground: { url: '/api/v1/files/kits/park-playground.glb', targetHeight_m: 2.8 },
      pavilion: { url: '/api/v1/files/kits/park-pavilion.glb', targetHeight_m: 3.8 },
    }
    : {}),
  basketball_hoop: {
    url: '/park-kits/basketball-hoop.glb',
    targetHeight_m: 3.95,
    preserveHorizontalOrigin: true,
    footprint_m: { width: 1.85, depth: 1.8 },
    clearance_m: 2,
    maxTriangles: 5000,
  },
  chainlink_fence_4m: {
    url: '/park-kits/chainlink-fence-4m.glb',
    targetHeight_m: 3.05,
    preserveHorizontalOrigin: true,
    footprint_m: { width: 4, depth: 0.12 },
    clearance_m: 0.25,
    maxTriangles: 6000,
  },
  chainlink_gate_3m: {
    url: '/park-kits/chainlink-gate-3m.glb',
    targetHeight_m: 3.05,
    preserveHorizontalOrigin: true,
    footprint_m: { width: 3, depth: 0.2 },
    clearance_m: 1.5,
    maxTriangles: 6000,
  },
  basketball_floodlight: {
    url: '/park-kits/basketball-floodlight.glb',
    targetHeight_m: 12.35,
    preserveHorizontalOrigin: true,
    footprint_m: { width: 0.3, depth: 0.3 },
    clearance_m: 1,
    maxTriangles: 2000,
  },
};
