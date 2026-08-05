export type LandscapeTreeVariant =
  | 'honey_locust'
  | 'maple'
  | 'mature_oak'
  | 'ornamental_pear'
  | 'columnar_hornbeam'
  | 'pollarded_plane'
  | 'tropical_palm';

export type LandscapeTreeCanopyClass =
  | 'standard'
  | 'mature_deciduous'
  | 'columnar_deciduous'
  | 'pollarded_deciduous'
  | 'tropical_palm';

export interface LandscapeTreeProfile {
  textureUrl: string;
  crownGeometry: 'billboard_cluster' | 'radial_palm_fronds';
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
    crownGeometry: 'billboard_cluster',
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
    crownGeometry: 'billboard_cluster',
    trunkHeightM: 3.8,
    trunkRadiusM: 0.28,
    crownWidthM: 7.8,
    crownDepthM: 7.2,
    crownHeightM: 5.5,
    foliageTint: '#e3ead7',
    barkColor: '#5d5045',
  },
  mature_oak: {
    // Reuse the reviewed broadleaf crown map, but give the oak its own
    // metric trunk/crown assembly. This creates the spreading village-green
    // silhouette without adding a runtime image/model-generation dependency.
    textureUrl: '/assets/landscape/tree-crown-maple.png',
    crownGeometry: 'billboard_cluster',
    trunkHeightM: 4.2,
    trunkRadiusM: 0.38,
    crownWidthM: 10.2,
    crownDepthM: 9.4,
    crownHeightM: 5.4,
    foliageTint: '#d5e1c7',
    barkColor: '#51463a',
  },
  ornamental_pear: {
    textureUrl: '/assets/landscape/tree-crown-ornamental-pear.png',
    crownGeometry: 'billboard_cluster',
    trunkHeightM: 3.4,
    trunkRadiusM: 0.18,
    crownWidthM: 4.7,
    crownDepthM: 4.2,
    crownHeightM: 6.2,
    foliageTint: '#e5eddd',
    barkColor: '#62564b',
  },
  columnar_hornbeam: {
    textureUrl: '/assets/landscape/tree-crown-ornamental-pear.png',
    crownGeometry: 'billboard_cluster',
    trunkHeightM: 4.0,
    trunkRadiusM: 0.17,
    crownWidthM: 3.15,
    crownDepthM: 2.75,
    crownHeightM: 6.3,
    foliageTint: '#dfe9d4',
    barkColor: '#62584c',
  },
  pollarded_plane: {
    textureUrl: '/assets/landscape/tree-crown-maple.png',
    crownGeometry: 'billboard_cluster',
    trunkHeightM: 4.55,
    trunkRadiusM: 0.27,
    crownWidthM: 5.25,
    crownDepthM: 4.85,
    crownHeightM: 5.0,
    foliageTint: '#dfe6cf',
    barkColor: '#7a6a57',
  },
  tropical_palm: {
    textureUrl: '/assets/landscape/tree-crown-honey-locust.png',
    crownGeometry: 'radial_palm_fronds',
    trunkHeightM: 7.7,
    trunkRadiusM: 0.18,
    crownWidthM: 7,
    crownDepthM: 6.5,
    crownHeightM: 2.1,
    foliageTint: '#b8db8e',
    barkColor: '#9b7951',
  },
};

export const LANDSCAPE_TREE_VARIANTS = Object.freeze(
  Object.keys(LANDSCAPE_TREE_PROFILES) as LandscapeTreeVariant[],
);

export interface LandscapeTreeSeed {
  x: number;
  y: number;
  yawRad: number;
  canopyClass?: LandscapeTreeCanopyClass;
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
  const variants: readonly LandscapeTreeVariant[] = (() => {
    switch (tree.canopyClass) {
      case 'mature_deciduous': return ['honey_locust', 'maple', 'mature_oak'];
      case 'columnar_deciduous': return ['columnar_hornbeam'];
      case 'pollarded_deciduous': return ['pollarded_plane'];
      case 'tropical_palm': return ['tropical_palm'];
      default: return ['honey_locust', 'maple', 'ornamental_pear'];
    }
  })();
  return variants[(hash >>> 0) % variants.length];
}

export function resolveLandscapeTreeHeightM(
  variant: LandscapeTreeVariant,
  scale: number,
): number {
  const profile = LANDSCAPE_TREE_PROFILES[variant];
  return (profile.trunkHeightM + profile.crownHeightM * 0.88) * scale;
}
