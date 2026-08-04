import type { LandscapeTreeVariant } from './landscapeKitProfiles';
import type { ParkLegoMaterialPattern } from './parkLegoFamilies';

export type PublicRealmBenchStyle =
  | 'timber_slat'
  | 'heritage_cast_iron'
  | 'minimal_slab'
  | 'backless_timber';

/** Repetition is intentional weighting. The catalog stays small and explicit
 * while a family can strongly prefer one silhouette without cloning geometry
 * or calling an image/model service at runtime. */
const PARK_TREE_POOLS = {
  rustic_gravel: ['honey_locust', 'honey_locust', 'maple', 'ornamental_pear'],
  modern_turf: ['columnar_hornbeam', 'columnar_hornbeam', 'ornamental_pear'],
  native_meadow: ['honey_locust', 'honey_locust', 'maple'],
  urban_pavers: ['ornamental_pear', 'columnar_hornbeam', 'columnar_hornbeam'],
  english_pastoral: ['maple', 'maple', 'honey_locust', 'ornamental_pear'],
  modern_minimal: ['columnar_hornbeam', 'columnar_hornbeam', 'ornamental_pear'],
  mediterranean_xeriscape: ['ornamental_pear', 'ornamental_pear', 'honey_locust'],
  tropical_lush: ['tropical_palm', 'tropical_palm', 'ornamental_pear'],
} as const satisfies Readonly<Record<ParkLegoMaterialPattern, readonly LandscapeTreeVariant[]>>;

const PARK_BENCH_STYLES: Readonly<Record<ParkLegoMaterialPattern, PublicRealmBenchStyle>> = Object.freeze({
  rustic_gravel: 'timber_slat',
  modern_turf: 'minimal_slab',
  native_meadow: 'backless_timber',
  urban_pavers: 'heritage_cast_iron',
  english_pastoral: 'heritage_cast_iron',
  modern_minimal: 'minimal_slab',
  mediterranean_xeriscape: 'minimal_slab',
  tropical_lush: 'backless_timber',
});

function stableIndex(seed: string, length: number): number {
  let hash = 2166136261;
  for (let index = 0; index < seed.length; index += 1) {
    hash ^= seed.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return length > 0 ? (hash >>> 0) % length : 0;
}

export function resolveParkTreeVariant(
  materialPattern: ParkLegoMaterialPattern,
  seed: string,
): LandscapeTreeVariant {
  const pool = PARK_TREE_POOLS[materialPattern];
  return pool[stableIndex(seed, pool.length)];
}

export function resolveParkBenchStyle(
  materialPattern: ParkLegoMaterialPattern,
): PublicRealmBenchStyle {
  return PARK_BENCH_STYLES[materialPattern];
}
