import { CANONICAL_CHOICES, canonicalDrawing, type CanonicalSelection } from './canonicalCatalogue';
import type { PlaceAsset } from './assetRegistry';

const PREFIX = 'canonical-building:';
const cache = new Map<string, PlaceAsset>();

/** A placement descriptor, not a published detailed representation. The compiler
 * remains responsible for reviewed geometry or explicit planned massing. */
export function canonicalBuildingAsset(selection: CanonicalSelection): PlaceAsset {
  const { choice, variant } = selection;
  if (choice.domain !== 'building') throw new Error('Building placement requires a building archetype.');
  const id = `${PREFIX}${choice.option.id}:${variant?.id ?? ''}`;
  const cached = cache.get(id);
  if (cached) return cached;
  const { option } = choice;
  const width = variant?.suggestedWidth_m ?? option.suggestedWidth_m ?? option.footprintCompatibility?.recommendedWidth_m[0] ?? 12;
  const depth = variant?.suggestedDepth_m ?? option.suggestedDepth_m ?? option.footprintCompatibility?.recommendedDepth_m[0] ?? 18;
  const asset: PlaceAsset = {
    id, kind: 'object', definitionVersion: 1, readiness: 'candidate',
    label: option.label, description: variant?.description ?? option.description,
    thumbnail: variant?.thumbnailUrl ?? option.catalogCardImageUrl ?? option.photoUrl,
    calgaryGuide: option.calgaryGuide!, zoneType: 'building',
    model: { variantId: variant?.id ?? option.id, revision: null, method: 'canonical_design' },
    reshapeMode: 'authored_footprint', width, depth, minWidth: 2, minDepth: 2,
    maxSize: Math.max(500, width, depth),
    reshapeDescription: 'Stretch changes the design footprint. If a detailed model cannot fit, the building is shown as design massing with its selected type retained.',
    properties: { ...canonicalDrawing(selection).properties, native_plot_axes: true },
  };
  cache.set(id, asset);
  return asset;
}

export function canonicalBuildingById(id: string): PlaceAsset | undefined {
  if (!id.startsWith(PREFIX)) return undefined;
  const [parent, variantId] = id.slice(PREFIX.length).split(':');
  const choice = CANONICAL_CHOICES.find(c => c.domain === 'building' && c.option.id === parent);
  if (!choice) return undefined;
  const variant = choice.option.variants?.find(v => v.id === variantId);
  if (variantId && !variant) return undefined;
  return canonicalBuildingAsset({ choice, variant });
}

export function canonicalBuildingForProperties(properties: Record<string, unknown>): PlaceAsset | undefined {
  const parent = properties.development_subcategory ?? properties.development_archetype_id;
  const variant = properties.development_selected_variant_id;
  return typeof parent === 'string' ? canonicalBuildingById(`${PREFIX}${parent}:${typeof variant === 'string' ? variant : ''}`) : undefined;
}
