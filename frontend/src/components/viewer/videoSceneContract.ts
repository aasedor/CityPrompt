import type { SiteZone } from '@/types';

type UnknownRecord = Record<string, unknown>;

interface ContractEntry {
  line: string;
  identity: string;
}

/**
 * What the video model may do with City Prompt's captured clay massing.
 * `massing_fidelity` animates the approved pixels and nothing else;
 * `photoreal` materializes the study massing into built architecture while the
 * geometry, topology, and object-count locks stay exactly as strict.
 */
export type VideoFinishMode = 'massing_fidelity' | 'photoreal';

export interface VideoSceneContract {
  text: string;
  signature: string;
  summary: string;
  buildingCount: number;
  openSpaceCount: number;
  finishMode: VideoFinishMode;
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

function buildingContract(zone: SiteZone, index: number, finishMode: VideoFinishMode): ContractEntry {
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
  const facts = [
    floors ? `${floors} storeys` : undefined,
    height ? `${height} m authored height` : undefined,
  ].filter((item): item is string => Boolean(item));
  const measuredFacts = facts.length ? `: ${facts.join('; ')}` : '';
  return {
    line: finishMode === 'photoreal'
      ? `B${index + 1} — authored proposal building${measuredFacts}. It appears in the control input as untextured study massing. Preserve its exact on-screen footprint, orientation, silhouette, setbacks, storey count, and opening positions, then materialize its surfaces into photoreal, construction-plausible architecture consistent with the surrounding captured context. No place, city, historical style name, material prompt, or catalog image is supplied to the video model; do not invent a named architectural style. Count B${index + 1}'s visible courtyards, lightwells, roof voids, and wings in the first frame, then preserve that exact topology and every void's perimeter, aspect ratio, separation, and placement.`
      : `B${index + 1} — authored proposal building${measuredFacts}. Its complete appearance comes only from its exact pixels in Image1; no place, city, historical style name, material prompt, or catalog image is supplied to the video model. Preserve the exact on-screen footprint, orientation, silhouette, setbacks, openings, LEGO massing, materials, lighting, and level of detail without enhancement. Count B${index + 1}'s visible courtyards, lightwells, roof voids, and wings in the first frame, then preserve that exact topology and every void's perimeter, aspect ratio, separation, and placement.`,
    identity: `${zone.id}:${archetype}:${floors ?? ''}:${height ?? ''}:${massing ?? ''}:${roof ?? ''}:${materials.join(',')}`,
  };
}

function openSpaceContract(zone: SiteZone, index: number, finishMode: VideoFinishMode): ContractEntry {
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
  const paving = clipped(asString(style.pavingType), 180);
  const planting = clipped(asString(style.plantingType), 180);
  const seating = clipped(asString(style.seatingRealm), 180);
  const water = clipped(asString(style.waterFeatures), 140);
  return {
    line: finishMode === 'photoreal'
      ? `P${index + 1} — authored proposal open space. It appears in the control input as simplified study landscape. Preserve its exact on-screen boundary, path structure, planting positions, furniture placement, and internal program, then materialize its paving, planting, and furniture into photoreal detail consistent with the surrounding captured context. Archetype names, descriptive style words, and catalog images are intentionally withheld from the video model. Do not replace it with a generic lawn, formal garden, plaza, pool, or fountain, and do not add a fountain, monument, or centrepiece that is not already present.`
      : `P${index + 1} — authored proposal open space. Its complete appearance and program come only from its exact pixels in Image1; archetype names, descriptive style words, and catalog images are intentionally withheld from the video model. Preserve its exact on-screen boundary, layout, planting, furniture, materials, lighting, and internal program without enhancement. Do not replace it with a generic lawn, formal garden, plaza, pool, or fountain.`,
    identity: `${zone.id}:${archetype}:${paving ?? ''}:${planting ?? ''}:${seating ?? ''}:${water ?? ''}`,
  };
}

export function buildVideoSceneContract(
  siteZones: SiteZone[],
  finishMode: VideoFinishMode = 'massing_fidelity',
): VideoSceneContract {
  const photoreal = finishMode === 'photoreal';
  const buildings = siteZones.filter((zone) => zone.zone_type === 'building');
  const openSpaces = siteZones.filter((zone) => ['green_space', 'park', 'plaza'].includes(zone.zone_type));
  const buildingEntries = buildings.map((zone, index) => buildingContract(zone, index, finishMode));
  const openSpaceEntries = openSpaces.map((zone, index) => openSpaceContract(zone, index, finishMode));
  const entries = [...buildingEntries, ...openSpaceEntries];
  const fallback = photoreal
    ? 'Preserve the exact geometry of every authored zone as it appears in the control input, then materialize its untextured study surfaces into photoreal, construction-plausible architecture and landscape. Add no building, wing, storey, path, or landscape feature that is not already present.'
    : 'Preserve every authored zone exactly as it appears in Image1. Animate the existing captured pixels without adding materials, lighting, detail, or design interpretation.';
  const text = [
    photoreal
      ? `SCENE INVENTORY: exactly ${buildings.length} authored building zone(s) and ${openSpaces.length} authored open-space zone(s). The control input is the sole geometric source of truth; its surfaces are study massing awaiting materialization. Zone metadata identifies what must remain stable; it does not authorize redesign and never supplies a named style.`
      : `SCENE INVENTORY: exactly ${buildings.length} authored building zone(s) and ${openSpaces.length} authored open-space zone(s). Image1 is the sole geometric and visual source of truth. Zone metadata identifies what must remain stable; it does not authorize redesign or supply a new appearance.`,
    ...entries.map((entry) => entry.line),
    buildings.length > 1
      ? `BUILDING SEPARATION CHECKSUM: the ${buildings.length} authored building zones are exactly ${buildings.length} mutually disconnected solids. Preserve every open-air gap, alley, park edge, and setback between them from ground to sky. Never bridge, join, fuse, wrap, or extend one building toward another; never consolidate them into a perimeter block.`
      : undefined,
    'ARCHETYPE SCOPE LOCK: each archetype applies only to its explicitly authored zone and is never global art direction. All non-authored background buildings are immutable captured context, not additional archetype instances. Preserve their regional architecture exactly; never copy, repeat, or propagate an authored facade, roof, material, massing, or building type into the background.',
    'GLOBAL TOPOLOGY LOCK: building solids and their negative spaces are equally immutable. Never lengthen, widen, shrink, merge, split, fill, or invent any courtyard, lightwell, roof void, or gap between wings.',
    'GLOBAL FORBIDDEN CHANGES: no new wings, duplicate buildings, extra storeys, roof substitutions, moved entrances, changed facade bay spacing, genericized open space, fountains unless explicitly required, or objects borrowed from one archetype and applied to another.',
  ].filter(Boolean).join('\n');
  // The finish mode is part of the identity: switching it rewrites every zone
  // line, so a request prepared under the other mode must not be reused.
  const zoneSignature = entries.length
    ? entries.map((entry) => entry.identity).join('|')
    : `fallback:${siteZones.map((zone) => `${zone.id}:${zone.updated_at}`).join('|')}`;
  const finishLabel = photoreal ? 'photoreal finish' : 'source-fidelity animation';
  return {
    text: entries.length ? text : fallback,
    signature: `${finishMode}:${zoneSignature}`,
    summary: entries.length
      ? `${buildings.length} building archetype${buildings.length === 1 ? '' : 's'} · ${openSpaces.length} open-space archetype${openSpaces.length === 1 ? '' : 's'} · ${finishLabel}`
      : `Captured scene only · ${finishLabel}`,
    buildingCount: buildings.length,
    openSpaceCount: openSpaces.length,
    finishMode,
  };
}
