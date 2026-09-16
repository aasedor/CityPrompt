import { archetypeOwnedParkKitForSelection } from '@/components/viewer/globe/parkArchetypeOwnedKits';
import { CANONICAL_CHOICES, canonicalDrawing, type CanonicalSelection } from './canonicalCatalogue';
import type { PlaceAsset } from './assetRegistry';

const PREFIX = 'canonical-park:';
const cache = new Map<string, PlaceAsset>();

/** Catalogue identity selects the compiler; it never certifies a runtime kit. */
export function canonicalParkAsset(selection: CanonicalSelection): PlaceAsset {
  const { choice, variant } = selection;
  if (choice.domain !== 'park_plaza') throw new Error('Choose a park archetype.');
  const id = `${PREFIX}${choice.option.id}:${variant?.id ?? ''}`;
  const cached = cache.get(id);
  if (cached) return cached;
  const { option } = choice;
  const kit = archetypeOwnedParkKitForSelection(option.id, variant?.id ?? '');
  // Receive the complete metric programme plus its reviewed edge clearance.
  const width = kit ? kit.widthM + 2 * kit.clearanceM + 0.1 : variant?.suggestedWidth_m ?? option.suggestedWidth_m ?? 40;
  const depth = kit ? kit.depthM + 2 * kit.clearanceM + 0.1 : variant?.suggestedDepth_m ?? option.suggestedDepth_m ?? 35;
  const asset: PlaceAsset = {
    id, kind: 'object', definitionVersion: 1, readiness: 'candidate',
    label: option.label, description: variant?.description ?? option.description,
    thumbnail: variant?.thumbnailUrl ?? option.catalogCardImageUrl ?? option.photoUrl,
    calgaryGuide: option.calgaryGuide!, zoneType: 'green_space',
    model: { variantId: variant?.id ?? option.id, revision: null, method: 'canonical_design' },
    reshapeMode: 'authored_footprint', width, depth,
    minWidth: option.minWidth_m ?? 2, minDepth: option.minDepth_m ?? 2, maxSize: Math.max(1000, width, depth),
    reshapeDescription: 'The park keeps its selected type. Reviewed equipment keeps its real size; unsupported outlines use a simplified layout.',
    properties: canonicalDrawing(selection).properties,
  };
  cache.set(id, asset);
  return asset;
}

export function canonicalParkById(id: string): PlaceAsset | undefined {
  if (!id.startsWith(PREFIX)) return undefined;
  const [parent, variantId] = id.slice(PREFIX.length).split(':');
  const choice = CANONICAL_CHOICES.find(c => c.domain === 'park_plaza' && c.option.id === parent);
  if (!choice) return undefined;
  const variant = choice.option.variants?.find(v => v.id === variantId);
  if (variantId && !variant) return undefined;
  return canonicalParkAsset({ choice, variant });
}

export function canonicalParkForProperties(properties: Record<string, unknown>): PlaceAsset | undefined {
  const parent = properties.green_space_archetype_id ?? properties.green_space_subcategory;
  const variant = properties.green_space_selected_variant_id;
  return typeof parent === 'string' ? canonicalParkById(`${PREFIX}${parent}:${typeof variant === 'string' ? variant : ''}`) : undefined;
}
