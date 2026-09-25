import {
  BUILDING_AESTHETIC_OPTIONS_V2, OPENSPACE_AESTHETIC_OPTIONS_V2, ROADWAY_AESTHETIC_OPTIONS_V2,
  type AestheticOption, type ArchetypeVariant,
} from '@/components/viewer/aestheticCatalog';
import { buildAestheticSelectionProps } from '@/components/viewer/aestheticSelection';
import { calgaryGroup, classifyCalgaryVariant, type CatalogueDomain } from '@/features/calgaryCatalogue/guide';
import type { SiteZoneProperties, SiteZoneType } from '@/types';
import { CATALOGUE_ASSETS, isPlaceable, type CatalogueAsset } from './assetRegistry';
import starter from '@/data/classroomStarter.json';
import validation from '@/data/validationCatalogue.json';

export interface CanonicalChoice {
  id: string; domain: CatalogueDomain; option: AestheticOption;
  placements: CatalogueAsset[];
}
export const CANONICAL_DOMAINS = {
  building: BUILDING_AESTHETIC_OPTIONS_V2,
  park_plaza: OPENSPACE_AESTHETIC_OPTIONS_V2,
  street_pathway: ROADWAY_AESTHETIC_OPTIONS_V2,
};

/** References own discovery; the runtime registry alone owns detailed placement readiness. */
export function catalogueChoices(domains = CANONICAL_DOMAINS, assets = CATALOGUE_ASSETS): CanonicalChoice[] {
  const choices: CanonicalChoice[] = [];
  const ids = new Set<string>();
  for (const [domain, options] of Object.entries(domains) as [CatalogueDomain, AestheticOption[]][]) {
    for (const option of options) {
      const id = `${domain}:${option.id}`;
      if (!option.id || ids.has(id)) throw new Error(`Duplicate or empty canonical catalogue ID: ${id}`);
      if (!option.label || !option.photoUrl || calgaryGroup(option.calgaryGuide)?.domain !== domain) {
        throw new Error(`Incomplete canonical catalogue entry: ${id}`);
      }
      const variants = option.variants ?? [];
      if (variants.some(v => !v.id || !v.label) || new Set(variants.map(v => v.id)).size !== variants.length) {
        throw new Error(`Invalid canonical variants: ${id}`);
      }
      ids.add(id);
      const parentKey = domain === 'building' ? 'development_archetype_id' : domain === 'park_plaza' ? 'green_space_archetype_id' : 'road_archetype_id';
      choices.push({ id, domain, option, placements: assets.filter(asset => isPlaceable(asset) && asset.properties[parentKey] === option.id) });
    }
  }
  return choices.sort((a, b) => Number(b.placements.length > 0) - Number(a.placements.length > 0));
}
// Local validation roster: no legacy variants or generic massing fallbacks in discovery.
export const CANONICAL_CHOICES: CanonicalChoice[] = validation.entries.map(entry => {
  const domain = entry.domain === 'building' ? 'building' : entry.domain === 'park' ? 'park_plaza' : 'street_pathway';
  const asset = CATALOGUE_ASSETS.find(a => a.id === entry.placement_id)!;
  const source = CANONICAL_DOMAINS[domain].find(o => o.id === entry.archetype_id);
  return { id: `${domain}:${entry.archetype_id}`, domain, placements: [asset], option: {
    ...source, id: entry.archetype_id, label: asset.label, description: asset.description,
    photoUrl: asset.thumbnail, calgaryGuide: asset.calgaryGuide, propertyPresets: asset.properties,
    variants: [{ id: entry.variant_id, label: asset.label, thumbnailUrl: asset.thumbnail }],
  } };
});
/** Exact starter variants only. Parent cards must not quietly expose their other
 * variants under the classroom promise. The full catalogue remains separate. */
export function classroomChoices(choices = CANONICAL_CHOICES): CanonicalChoice[] {
  return starter.entries.flatMap(entry => {
    const domain = entry.domain === 'street' ? 'street_pathway' : entry.domain === 'park' ? 'park_plaza' : 'building';
    const choice = choices.find(item => item.domain === domain && item.option.id === entry.archetypeId);
    const placement = choice?.placements.find(asset => asset.id === entry.placementId && asset.model.variantId === entry.variantId);
    if (!choice || !placement) return [];
    const variant = choice.option.variants?.find(item => item.id === entry.variantId)
      ?? { id: entry.variantId, label: placement.label, thumbnailUrl: placement.thumbnail };
    return [{ ...choice, placements: [placement], option: { ...choice.option, variants: [variant] } }];
  });
}
export const CLASSROOM_CHOICES = CANONICAL_CHOICES;
const normalizeSearch = (v: string) => v.toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, ' ');
export function choiceMatchesGroup(choice: CanonicalChoice, groupId: string) {
  return !groupId || choice.option.calgaryGuide?.groupId === groupId
    || choice.option.variants?.some(variant => classifyCalgaryVariant(choice.option.id, variant.id)?.groupId === groupId)
    || choice.placements.some(asset => asset.calgaryGuide.groupId === groupId);
}
/** Open a matching detailed variant when a parent spans several housing types. */
export function preferredCatalogueVariant(choice: CanonicalChoice, query = '', groupId = '') {
  const terms = normalizeSearch(query).trim().split(/\s+/).filter(Boolean);
  const placements = choice.placements.filter(asset => !groupId || asset.calgaryGuide.groupId === groupId);
  const variants = choice.option.variants?.filter(variant => !groupId || classifyCalgaryVariant(choice.option.id, variant.id)?.groupId === groupId) ?? [];
  const matching = placements.find(asset => terms.every(term => normalizeSearch(`${asset.label} ${asset.model.variantId}`).includes(term)));
  const variant = variants.find(item => terms.length && terms.every(term => normalizeSearch(`${item.label} ${item.id} ${item.description ?? ''}`).includes(term)));
  return matching?.model.variantId || (groupId && placements[0]?.model.variantId) || variant?.id || (groupId && variants[0]?.id)
    || placements[0]?.model.variantId || choice.placements[0]?.model.variantId || choice.option.variants?.[0]?.id || '';
}
export function filterCanonicalChoices(domain: CatalogueDomain, query = '', groupId = '', choices = CANONICAL_CHOICES) {
  const normalize = normalizeSearch;
  const terms = normalize(query).trim().split(/\s+/).filter(Boolean);
  return choices.filter(choice => {
    if (choice.domain !== domain || !choiceMatchesGroup(choice, groupId)) return false;
    const group = calgaryGroup(choice.option.calgaryGuide);
    const haystack = normalize([choice.option.id, choice.option.label, choice.option.description, choice.option.categoryId,
      group?.label, ...(group?.districts ?? []), ...(choice.option.generationTags ?? []),
      ...(choice.option.variants ?? []).map(v => v.label), ...choice.placements.map(a => a.label)].join(' '));
    return terms.every(term => haystack.includes(term));
  });
}

export interface CanonicalSelection { choice: CanonicalChoice; variant?: ArchetypeVariant }
export function canonicalDrawing({ choice, variant }: CanonicalSelection): { type: SiteZoneType; properties: SiteZoneProperties } {
  if (variant && !choice.option.variants?.some(v => v.id === variant.id)) throw new Error('The selected variant does not belong to this archetype.');
  const key = choice.domain === 'building' ? 'development_aesthetic' : choice.domain === 'street_pathway' ? 'road_aesthetic' : 'green_space_aesthetic';
  const base: SiteZoneProperties = { ...choice.option.propertyPresets, pick_place_automatic_3d: true };
  if (choice.domain === 'building') {
    const floors = variant?.minFloors ?? choice.option.minFloors ?? 2;
    const floorHeight = variant?.suggestedFloorHeight ?? choice.option.suggestedFloorHeight ?? 3;
    Object.assign(base, { development_type: choice.option.developmentType, floors, floor_count: floors,
      floor_height: floorHeight, height: floors * floorHeight });
  }
  return {
    type: choice.domain === 'building' ? 'building' : choice.domain === 'street_pathway' ? 'road' : 'green_space',
    properties: buildAestheticSelectionProps(base, key, choice.option.id, [choice.option], undefined,
      choice.option.archetypeImages?.find(image => image.imageUrl === variant?.thumbnailUrl)?.id, variant?.id),
  };
}
