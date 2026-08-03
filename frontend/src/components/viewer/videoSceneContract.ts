import type { SiteZone } from '@/types';
import buildingCatalog from '@/data/buildingArchetypes.json';
import openSpaceCatalog from '@/data/openSpaceArchetypes.json';

type UnknownRecord = Record<string, unknown>;

interface CatalogEntry {
  id?: string;
  thumbnailUrl?: string;
  videoReferenceUrl?: string;
  variants?: Array<{ thumbnailUrl?: string; videoReferenceUrl?: string }>;
}

interface ContractEntry {
  label: string;
  line: string;
  referenceUrl?: string;
  identity: string;
}

const BUILDING_CATALOG = ((buildingCatalog as { archetypes?: CatalogEntry[] }).archetypes ?? []);
const OPEN_SPACE_CATALOG = ((openSpaceCatalog as { archetypes?: CatalogEntry[] }).archetypes ?? []);

export interface VideoSceneContract {
  text: string;
  signature: string;
  summary: string;
  buildingCount: number;
  openSpaceCount: number;
  referenceImageUrls: string[];
  referenceRoleLabels: string[];
}

function asObject(value: unknown): UnknownRecord | undefined {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? value as UnknownRecord
    : undefined;
}

function asString(value: unknown): string | undefined {
  if (typeof value !== 'string') return undefined;
  const trimmed = value.trim();
  return trimmed || undefined;
}

function asNumber(value: unknown): number | undefined {
  const number = typeof value === 'number' ? value : Number(value);
  return Number.isFinite(number) ? number : undefined;
}

function asStringList(value: unknown): string[] {
  return Array.isArray(value) ? value.map(asString).filter((item): item is string => Boolean(item)) : [];
}

function firstString(properties: UnknownRecord, keys: string[]): string | undefined {
  for (const key of keys) {
    const value = asString(properties[key]);
    if (value) return value;
  }
  return undefined;
}

function clipped(value: string | undefined, maxLength = 420): string | undefined {
  if (!value) return undefined;
  return value.length <= maxLength ? value : `${value.slice(0, maxLength - 1).trim()}…`;
}

function catalogReference(rawId: string, fallback: string | undefined, catalog: CatalogEntry[]): string | undefined {
  const match = rawId.match(/_(?:variant_|v)(\d+)$/);
  const baseId = match ? rawId.slice(0, match.index) : rawId;
  const variantIndex = match ? Number(match[1]) : 0;
  const entry = catalog.find((candidate) => candidate.id === baseId) ?? catalog.find((candidate) => candidate.id === rawId);
  return entry?.variants?.[variantIndex]?.videoReferenceUrl
    ?? entry?.videoReferenceUrl
    ?? entry?.variants?.[variantIndex]?.thumbnailUrl
    ?? entry?.thumbnailUrl
    ?? fallback;
}

function buildingContract(zone: SiteZone, index: number): ContractEntry {
  const properties = (zone.properties ?? {}) as UnknownRecord;
  const style = asObject(properties.development_style_profile)
    ?? asObject(asObject(properties.generation_style_input)?.styleProfile)
    ?? {};
  const archetype = firstString(properties, ['development_archetype_id', 'development_aesthetic']) ?? 'authored building';
  const floors = asNumber(properties.floors);
  const height = asNumber(properties.height);
  const massing = clipped(asString(style.massing), 180);
  const roof = clipped(asString(style.roofForm), 160);
  const materials = asStringList(style.materials).slice(0, 5);
  const description = clipped(asString(properties.description_text), 300);
  const facts = [
    floors ? `${floors} storeys` : undefined,
    height ? `${height} m authored height` : undefined,
    massing,
    roof,
    materials.length ? `materials: ${materials.join(', ')}` : undefined,
    description,
  ].filter((item): item is string => Boolean(item));
  return {
    label: `B${index + 1}`,
    line: `B${index + 1} — ${archetype}: ${facts.join('; ')}. Preserve the exact on-screen footprint, orientation, silhouette, setbacks, openings, and LEGO massing; improve finish only. Count B${index + 1}'s visible courtyards, lightwells, roof voids, and wings in the first frame, then preserve that exact topology and every void's perimeter, aspect ratio, separation, and placement.`,
    referenceUrl: catalogReference(archetype, firstString(properties, [
      'development_archetype_image',
      'development_archetype_image_url',
    ]), BUILDING_CATALOG),
    identity: `${zone.id}:${archetype}:${floors ?? ''}:${height ?? ''}:${massing ?? ''}:${roof ?? ''}:${materials.join(',')}`,
  };
}

function openSpaceContract(zone: SiteZone, index: number): ContractEntry {
  const properties = (zone.properties ?? {}) as UnknownRecord;
  const generated = asObject(properties.generation_style_input)
    ?? asObject(asObject(properties.generation_style_inputs)?.plazas)
    ?? asObject(asObject(properties.generation_style_inputs)?.green_spaces);
  const style = asObject(properties.plaza_style_profile)
    ?? asObject(properties.green_space_style_profile)
    ?? asObject(generated?.styleProfile)
    ?? {};
  const archetype = firstString(properties, [
    'plaza_archetype_id',
    'green_space_archetype_id',
    'plaza_aesthetic',
    'green_space_aesthetic',
  ]) ?? 'authored open space';
  const description = clipped(asString(properties.description_text), 420);
  const paving = clipped(asString(style.pavingType), 180);
  const planting = clipped(asString(style.plantingType), 180);
  const seating = clipped(asString(style.seatingRealm), 180);
  const water = clipped(asString(style.waterFeatures), 140);
  const facts = [paving, planting, seating, water ? `water features: ${water}` : undefined, description]
    .filter((item): item is string => Boolean(item));
  return {
    label: `P${index + 1}`,
    line: `P${index + 1} — ${archetype}: ${facts.join('; ')}. Preserve its exact on-screen boundary and internal program. Do not replace it with a generic lawn, formal garden, plaza, pool, or fountain.`,
    referenceUrl: catalogReference(archetype, firstString(properties, [
      'plaza_archetype_image',
      'green_space_archetype_image',
      'plaza_archetype_image_url',
      'green_space_archetype_image_url',
    ]), OPEN_SPACE_CATALOG),
    identity: `${zone.id}:${archetype}:${paving ?? ''}:${planting ?? ''}:${seating ?? ''}:${water ?? ''}`,
  };
}

export function buildVideoSceneContract(siteZones: SiteZone[]): VideoSceneContract {
  const buildings = siteZones.filter((zone) => zone.zone_type === 'building');
  const openSpaces = siteZones.filter((zone) => ['green_space', 'park', 'plaza'].includes(zone.zone_type));
  const buildingEntries = buildings.map(buildingContract);
  const openSpaceEntries = openSpaces.map(openSpaceContract);
  const entries = [...buildingEntries, ...openSpaceEntries];
  const referenceLabels = new Map<string, string[]>();
  entries.forEach((entry) => {
    if (!entry.referenceUrl) return;
    referenceLabels.set(entry.referenceUrl, [...(referenceLabels.get(entry.referenceUrl) ?? []), entry.label]);
  });
  const referenceImageUrls = [...referenceLabels.keys()].slice(0, 6);
  const referenceRoleLabels = referenceImageUrls.map((url) => referenceLabels.get(url)?.join(' and ') ?? 'authored zone');
  const fallback = 'Preserve every authored zone exactly as it appears in the supplied first frame; add materials and lighting only.';
  const text = [
    `ARCHETYPE CONTRACT: exactly ${buildings.length} authored building zone(s) and ${openSpaces.length} authored open-space zone(s). The first frame is the geometric source of truth; archetype records and reference images define appearance, never replacement massing.`,
    ...entries.map((entry) => entry.line),
    'GLOBAL TOPOLOGY LOCK: building solids and their negative spaces are equally immutable. Never lengthen, widen, shrink, merge, split, fill, or invent any courtyard, lightwell, roof void, or gap between wings.',
    'GLOBAL FORBIDDEN CHANGES: no new wings, duplicate buildings, extra storeys, roof substitutions, moved entrances, changed facade bay spacing, genericized open space, fountains unless explicitly required, or objects borrowed from one archetype and applied to another.',
  ].filter(Boolean).join('\n');
  const signature = entries.length
    ? entries.map((entry) => entry.identity).join('|')
    : `fallback:${siteZones.map((zone) => `${zone.id}:${zone.updated_at}`).join('|')}`;
  return {
    text: entries.length ? text : fallback,
    signature,
    summary: entries.length
      ? `${buildings.length} building archetype${buildings.length === 1 ? '' : 's'} · ${openSpaces.length} open-space archetype${openSpaces.length === 1 ? '' : 's'} · geometry-first video`
      : 'Captured geometry only · no archetype metadata found',
    buildingCount: buildings.length,
    openSpaceCount: openSpaces.length,
    referenceImageUrls,
    referenceRoleLabels,
  };
}
