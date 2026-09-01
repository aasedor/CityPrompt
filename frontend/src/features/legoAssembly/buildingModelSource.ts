import type { Building } from '@/types';
import type {
  LegoAssemblyInstance,
  LegoAssemblyRecipe,
} from './legoAssemblyApi';

type BuildingModelRecord = Pick<Building, 'lod_urls' | 'model_url' | 'specifications'>;

export type BuildingModelSource =
  | {
      kind: 'lego_assembly';
      recipe: LegoAssemblyRecipe;
      presentation: 'architectural_clay' | 'assembly';
      variantKey: string | null;
      downloadUrl: string | null;
    }
  | {
      kind: 'legacy_model';
      modelUrl: string;
      presentation: 'model';
      variantKey: null;
      downloadUrl: string;
    };

function isFiniteTriple(value: unknown): value is [number, number, number] {
  return Array.isArray(value)
    && value.length === 3
    && value.every((number) => Number.isFinite(number));
}

function isValidInstance(value: unknown): value is LegoAssemblyInstance {
  if (!value || typeof value !== 'object') return false;
  const instance = value as Partial<LegoAssemblyInstance>;
  return (
    typeof instance.model_url === 'string'
    && instance.model_url.trim().length > 0
    && isFiniteTriple(instance.position)
    && isFiniteTriple(instance.scale)
    && (instance.rotation_degrees === undefined || Number.isFinite(instance.rotation_degrees))
  );
}

/**
 * Parse the persisted v1 assembly independently of any geospatial placement.
 * A standalone model viewer can display a valid assembly without a footprint;
 * the globe adds its stricter footprint requirement at the placement boundary.
 */
export function extractLegoAssemblyRecipe(
  building: Pick<Building, 'specifications'>,
): LegoAssemblyRecipe | null {
  const raw = building.specifications?.legoAssembly;
  if (!raw || typeof raw !== 'object') return null;

  const recipe = raw as Partial<LegoAssemblyRecipe> & { schemaVersion?: number };
  const version = recipe.schema_version ?? recipe.schemaVersion;
  if (version !== 1) return null;
  if (!Array.isArray(recipe.instances) || recipe.instances.length === 0) return null;
  if (!recipe.instances.every(isValidInstance)) return null;

  const target = recipe.target;
  if (!target || !(Number(target.width_m) > 0) || !(Number(target.depth_m) > 0)) return null;
  return recipe as LegoAssemblyRecipe;
}

export function isArchitecturalClayRecipe(recipe: LegoAssemblyRecipe): boolean {
  const identity = [
    recipe.module_family,
    recipe.archetype_id,
    ...recipe.instances.flatMap((instance) => [
      instance.family,
      instance.asset_name,
      instance.variant_key,
    ]),
  ]
    .filter((value): value is string => typeof value === 'string')
    .join(' ')
    .toLowerCase();
  return /semantic[-_\s]?clay|architectural[-_\s]?clay/.test(identity);
}

function singleAssemblyDownloadUrl(recipe: LegoAssemblyRecipe): string | null {
  const urls = new Set(recipe.instances.map((instance) => instance.model_url.trim()));
  return urls.size === 1 ? [...urls][0] ?? null : null;
}

/**
 * Resolve the visible authored representation. A saved LEGO assembly owns the
 * building before a historical monolithic model URL; that same precedence is
 * used by the globe and must also hold in standalone viewers.
 */
export function resolveBuildingModelSource(
  building: BuildingModelRecord,
): BuildingModelSource | null {
  const recipe = extractLegoAssemblyRecipe(building);
  if (recipe) {
    return {
      kind: 'lego_assembly',
      recipe,
      presentation: isArchitecturalClayRecipe(recipe) ? 'architectural_clay' : 'assembly',
      variantKey: recipe.fit?.selected_variant_key
        ?? recipe.instances.find((instance) => instance.variant_key)?.variant_key
        ?? null,
      downloadUrl: singleAssemblyDownloadUrl(recipe),
    };
  }

  const modelUrl = building.lod_urls?.['0']
    ?? building.model_url
    ?? Object.values(building.lod_urls ?? {}).find((url) => Boolean(url));
  if (typeof modelUrl !== 'string' || !modelUrl.trim()) return null;
  return {
    kind: 'legacy_model',
    modelUrl: modelUrl.trim(),
    presentation: 'model',
    variantKey: null,
    downloadUrl: modelUrl.trim(),
  };
}
