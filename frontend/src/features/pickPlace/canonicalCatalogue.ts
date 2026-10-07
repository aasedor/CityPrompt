import {
  BUILDING_AESTHETIC_OPTIONS_V2, OPENSPACE_AESTHETIC_OPTIONS_V2, ROADWAY_AESTHETIC_OPTIONS_V2, SAVED_BUILDING_AESTHETIC_OPTIONS, SAVED_OPENSPACE_AESTHETIC_OPTIONS, SAVED_ROADWAY_AESTHETIC_OPTIONS,
  type AestheticOption, type ArchetypeVariant,
} from '@/components/viewer/aestheticCatalog';
import { buildAestheticSelectionProps } from '@/components/viewer/aestheticSelection';
import { calgaryGroup, classifyCalgaryVariant, type CatalogueDomain } from '@/features/calgaryCatalogue/guide';
import type { SiteZoneProperties, SiteZoneType } from '@/types';
import { CATALOGUE_ASSETS, FLEXIBLE_PARK_ASSETS, MANUAL_STREET_ASSETS, OCTOBER_BUILDING_ASSETS, COMMUNITY_BUILDING_ASSETS, isPlaceable, type CatalogueAsset } from './assetRegistry';
import starter from '@/data/classroomStarter.json';
import validation from '@/data/validationCatalogue.json';
import expansion from '@/data/classroomExpansion.json';
import { catalogueStyleIds, catalogueStyleLabel } from './catalogueFacets';

export interface CanonicalChoice {
  id: string; domain: CatalogueDomain; option: AestheticOption;
  placements: CatalogueAsset[];
}
export const CANONICAL_DOMAINS = {
  building: BUILDING_AESTHETIC_OPTIONS_V2,
  park_plaza: OPENSPACE_AESTHETIC_OPTIONS_V2,
  street_pathway: ROADWAY_AESTHETIC_OPTIONS_V2,
};

/** Reference photography is presentation metadata; it cannot change which
 * exact model, dimensions, or revision is placed. Preserve the full reference
 * lookup before the inspector's validation-only variant filtering. */
const REFERENCE_DOMAINS = {
  building: SAVED_BUILDING_AESTHETIC_OPTIONS,
  park_plaza: SAVED_OPENSPACE_AESTHETIC_OPTIONS,
  street_pathway: SAVED_ROADWAY_AESTHETIC_OPTIONS,
};
function referenceImage(domain: CatalogueDomain, archetypeId: string, variantId: string, fallback: string) {
  const source = REFERENCE_DOMAINS[domain].find(option => option.id === archetypeId);
  return source?.variants?.find(variant => variant.id === variantId)?.thumbnailUrl
    || source?.catalogCardImageUrl || source?.photoUrl || fallback;
}

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
interface CatalogueRosterEntry {
  domain: string; archetype_id: string; variant_id: string; placement_id: string;
}

/** A missing registration must not prevent the other designs from loading.
 * Native upgrades may rename placement IDs, but must retain the exact design. */
export function resolveCatalogueRoster(entries: CatalogueRosterEntry[], assets = CATALOGUE_ASSETS) {
  const choices: CanonicalChoice[] = [];
  const unavailable: CatalogueRosterEntry[] = [];
  for (const entry of entries) {
    const domain = entry.domain === 'building' ? 'building' : entry.domain === 'park' ? 'park_plaza'
      : entry.domain === 'street' ? 'street_pathway' : undefined;
    if (!domain) { unavailable.push(entry); continue; }
    const parentKey = domain === 'building' ? 'development_archetype_id'
      : domain === 'park_plaza' ? 'green_space_archetype_id' : 'road_archetype_id';
    const zoneType = domain === 'building' ? 'building' : domain === 'park_plaza' ? 'green_space' : 'road';
    const matches = assets.filter(asset => isPlaceable(asset)
      && (asset.kind === 'street' ? zoneType === 'road' : asset.zoneType === zoneType)
      && asset.properties[parentKey] === entry.archetype_id && asset.model.variantId === entry.variant_id);
    const asset = matches.find(candidate => candidate.id === entry.placement_id) ?? matches[0];
    if (!asset) { unavailable.push(entry); continue; }
    const source = CANONICAL_DOMAINS[domain].find(option => option.id === entry.archetype_id);
    // Expansion variants already have exact runtime registrations, but their
    // parent can be absent from the validation-only inspector catalogue.
    // Restore browsing tags alone: never revive the parent's other variants,
    // presets, floor counts, references, or runtime eligibility.
    const styleSource = source ?? (domain === 'building' ? SAVED_BUILDING_AESTHETIC_OPTIONS.find(option => option.id === entry.archetype_id) : undefined);
    choices.push({ id: `${domain}:${entry.archetype_id}:${entry.variant_id}`, domain, placements: [asset], option: {
      ...source, categoryId: styleSource?.categoryId, generationTags: styleSource?.generationTags,
      id: entry.archetype_id, label: asset.label, description: asset.description,
      photoUrl: referenceImage(domain, entry.archetype_id, entry.variant_id, asset.thumbnail), calgaryGuide: asset.calgaryGuide, propertyPresets: asset.properties,
      variants: [{ id: entry.variant_id, label: asset.label, thumbnailUrl: referenceImage(domain, entry.archetype_id, entry.variant_id, asset.thumbnail) }],
    } });
  }
  return { choices, unavailable };
}

// Local validation roster: no legacy variants or generic massing fallbacks in discovery.
const resolvedRoster = resolveCatalogueRoster([...validation.entries, ...expansion.entries,
  ...[...OCTOBER_BUILDING_ASSETS, ...COMMUNITY_BUILDING_ASSETS].map(asset => ({ domain: 'building',
    archetype_id: String(asset.properties.development_archetype_id),
    variant_id: asset.model.variantId, placement_id: asset.id }))]);
/** Supplemental choices must share the reviewed registry's exact identity and
 * browsing classification, just like the resolved validation roster. */
function registeredSupplement(asset: CatalogueAsset): CatalogueAsset {
  const registered = CATALOGUE_ASSETS.find(candidate => candidate.id === asset.id
    && candidate.model.variantId === asset.model.variantId && isPlaceable(candidate));
  if (!registered) throw new Error(`Missing supplemental catalogue registration: ${asset.id}`);
  return registered;
}
export const CANONICAL_CHOICES: CanonicalChoice[] = [
  ...resolvedRoster.choices,
  ...FLEXIBLE_PARK_ASSETS.map(registeredSupplement).map(asset => {
    const source = CANONICAL_DOMAINS.park_plaza.find(option => option.id === asset.properties.green_space_archetype_id);
    if (!source) throw new Error(`Missing park reference for ${asset.id}`);
    return { id: `park_plaza:${source.id}:flexible:${asset.id}`, domain: 'park_plaza' as const, placements: [asset], option: {
      ...source, label: asset.label, description: asset.description, photoUrl: referenceImage('park_plaza', source.id, asset.model.variantId, asset.thumbnail),
      calgaryGuide: asset.calgaryGuide, propertyPresets: asset.properties,
      variants: [{ id: asset.model.variantId, label: asset.label, thumbnailUrl: asset.thumbnail }],
    } };
  }),
];
export const UNAVAILABLE_CATALOGUE_ENTRIES = resolvedRoster.unavailable;
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
CANONICAL_CHOICES.push(...MANUAL_STREET_ASSETS.map(registeredSupplement).map(asset => ({
  id: `street_pathway:${asset.properties.road_archetype_id}:${asset.model.variantId}`,
  domain: 'street_pathway' as const, placements: [asset], option: {
    ...CANONICAL_DOMAINS.street_pathway.find(o => o.id === asset.properties.road_archetype_id),
    id: String(asset.properties.road_archetype_id), label: asset.label, description: asset.description,
    photoUrl: referenceImage('street_pathway', String(asset.properties.road_archetype_id), asset.model.variantId, asset.thumbnail), calgaryGuide: asset.calgaryGuide, propertyPresets: asset.properties,
    variants: [{ id: asset.model.variantId, label: 'Street Manual | metric 3D', thumbnailUrl: asset.thumbnail }],
  },
})));
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
      ...catalogueStyleIds(choice).map(id => catalogueStyleLabel(id)),
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
