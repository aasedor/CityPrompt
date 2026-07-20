export type LandscapeTreeVariant = 'honey_locust' | 'maple' | 'ornamental_pear';

export interface LandscapeTreeProfile {
  textureUrl: string;
  trunkHeightM: number;
  trunkRadiusM: number;
  crownWidthM: number;
  crownDepthM: number;
  crownHeightM: number;
  foliageTint: string;
  barkColor: string;
}

/** Metric, reusable vegetation family for the interactive Google Tiles scene.
 * The images supply leaf-scale appearance while these dimensions remain the
 * authoritative model contract. */
export const LANDSCAPE_TREE_PROFILES: Record<LandscapeTreeVariant, LandscapeTreeProfile> = {
  honey_locust: {
    textureUrl: '/assets/landscape/tree-crown-honey-locust.png',
    trunkHeightM: 4.2,
    trunkRadiusM: 0.22,
    crownWidthM: 7.4,
    crownDepthM: 6.5,
    crownHeightM: 5.6,
    foliageTint: '#f2f5dc',
    barkColor: '#685746',
  },
  maple: {
    textureUrl: '/assets/landscape/tree-crown-maple.png',
    trunkHeightM: 3.8,
    trunkRadiusM: 0.28,
    crownWidthM: 7.8,
    crownDepthM: 7.2,
    crownHeightM: 5.5,
    foliageTint: '#e3ead7',
    barkColor: '#5d5045',
  },
  ornamental_pear: {
    textureUrl: '/assets/landscape/tree-crown-ornamental-pear.png',
    trunkHeightM: 3.4,
    trunkRadiusM: 0.18,
    crownWidthM: 4.7,
    crownDepthM: 4.2,
    crownHeightM: 6.2,
    foliageTint: '#e5eddd',
    barkColor: '#62564b',
  },
};

export const LANDSCAPE_TREE_VARIANTS = Object.freeze(
  Object.keys(LANDSCAPE_TREE_PROFILES) as LandscapeTreeVariant[],
);

export interface LandscapeTreeSeed {
  x: number;
  y: number;
  yawRad: number;
}

/** Stable selection keeps species consistent across reloads and camera LOD. */
export function selectLandscapeTreeVariant(
  tree: LandscapeTreeSeed,
  index: number,
): LandscapeTreeVariant {
  const key = `${Math.round(tree.x * 10)}:${Math.round(tree.y * 10)}:${Math.round(tree.yawRad * 100)}:${index}`;
  let hash = 2166136261;
  for (let charIndex = 0; charIndex < key.length; charIndex += 1) {
    hash ^= key.charCodeAt(charIndex);
    hash = Math.imul(hash, 16777619);
  }
  return LANDSCAPE_TREE_VARIANTS[(hash >>> 0) % LANDSCAPE_TREE_VARIANTS.length];
}

export function resolveLandscapeTreeHeightM(
  variant: LandscapeTreeVariant,
  scale: number,
): number {
  const profile = LANDSCAPE_TREE_PROFILES[variant];
  return (profile.trunkHeightM + profile.crownHeightM * 0.88) * scale;
}
