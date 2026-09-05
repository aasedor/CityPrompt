/**
 * Authored archetype artwork for Direct 3D renders.
 *
 * Buildings are bound to their exact selected variant and authored facade
 * source whenever one exists. Parks and streets carry the selected catalogue
 * appearance too, but only for material finish. Their capacity and facility
 * layout have already been resolved in the captured 3D scene.
 */
import type { SiteZone } from '@/types';
import archetypeReferenceAvailability from '@/data/archetypeReferenceAvailability.json';
import buildingCatalog from '@/data/buildingArchetypes.json';
import legoFamilySignatures from '@/data/legoFamilySignatures.json';
import openSpaceCatalog from '@/data/openSpaceArchetypes.json';
import streetCatalog from '@/data/streetPathArchetypes.json';

export interface Direct3DArchetypeReference {
  image_base64: string;
  label: string;
}

interface FamilySignature {
  archetypeId?: string;
  identity?: string;
  materialZones?: string;
  elevationUrl?: string;
}

interface CatalogVariant {
  id?: string;
  label?: string;
  description?: string;
  thumbnailUrl?: string;
}

interface CatalogEntry {
  id?: string;
  title?: string;
  thumbnailUrl?: string;
  variants?: CatalogVariant[];
}

interface ReferenceCandidate {
  key: string;
  kind: 'building' | 'park' | 'street';
  title: string;
  selectedId: string;
  imageUrl?: string;
  signature?: FamilySignature;
  variant?: CatalogVariant;
  zoneNames: string[];
  targetDescription?: string;
}

const AVAILABLE_FAMILY_SIGNATURES = new Set(archetypeReferenceAvailability.familySignatureIds);
const FAMILIES: Record<string, FamilySignature> = Object.fromEntries(
  Object.entries((legoFamilySignatures as { families?: Record<string, FamilySignature> }).families ?? {})
    .filter(([id]) => AVAILABLE_FAMILY_SIGNATURES.has(id)),
);

const BUILDINGS: CatalogEntry[] =
  (buildingCatalog as { archetypes?: CatalogEntry[] }).archetypes ?? [];

const PARKS: CatalogEntry[] =
  (openSpaceCatalog as { archetypes?: CatalogEntry[] }).archetypes ?? [];

const STREETS: CatalogEntry[] =
  (streetCatalog as { archetypes?: CatalogEntry[] }).archetypes ?? [];

/** The server schema accepts at most eight reference images. */
const MAX_REFERENCES = 8;
const MAX_LABEL_LENGTH = 600;

/** Planner cards may store numbered view variants on the parent identity. */
function stripCardVariantSuffix(id: string): string {
  return id.replace(/_(?:variant_|v)\d+$/, '');
}

function normalizeId(value: unknown): string {
  return typeof value === 'string' ? value.trim().toLowerCase().replace(/-/g, '_') : '';
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? value as Record<string, unknown>
    : null;
}

function findEntry(catalog: CatalogEntry[], id: string): CatalogEntry | undefined {
  const normalized = normalizeId(id);
  return catalog.find((entry) => normalizeId(entry.id) === normalized)
    ?? catalog.find((entry) => normalizeId(entry.id) === stripCardVariantSuffix(normalized));
}

function findVariant(entry: CatalogEntry | undefined, id: string): CatalogVariant | undefined {
  const normalized = normalizeId(id);
  return entry?.variants?.find((variant) => normalizeId(variant.id) === normalized);
}

function targetDescription(
  properties: Record<string, unknown>,
  kind: 'park' | 'street',
): string | undefined {
  const recipe = asRecord(properties.public_realm_lego);
  const target = asRecord(recipe?.target);
  if (!target) return undefined;
  const number = (key: string) => {
    const value = Number(target[key]);
    return Number.isFinite(value) && value > 0 ? value : undefined;
  };
  if (kind === 'park') {
    const width = number('width_m');
    const depth = number('depth_m');
    const area = number('area_m2');
    return width && depth
      ? `${width.toFixed(1)} by ${depth.toFixed(1)} metre polygon${area ? ` (${Math.round(area)} square metres)` : ''}`
      : undefined;
  }
  const row = number('row_width_m');
  const length = number('length_m');
  return row && length ? `${row.toFixed(1)} metre width over ${Math.round(length)} metres` : undefined;
}

async function fetchImageBase64(url: string): Promise<string | null> {
  try {
    const response = await fetch(url);
    if (!response.ok) return null;
    const blob = await response.blob();
    // Dev servers answer missing files with 200 + an HTML fallback page;
    // forwarding those bytes as an image poisons the provider request.
    if (!blob.type.startsWith('image/')) {
      console.warn(`[Direct3D refs] Skipping non-image response (${blob.type || 'unknown'}):`, url);
      return null;
    }
    const bytes = new Uint8Array(await blob.arrayBuffer());
    const isPng = bytes.length >= 8
      && bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47
      && bytes[4] === 0x0d && bytes[5] === 0x0a && bytes[6] === 0x1a && bytes[7] === 0x0a;
    const isJpeg = bytes.length >= 3
      && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff;
    const isWebp = bytes.length >= 12
      && String.fromCharCode(...bytes.slice(0, 4)) === 'RIFF'
      && String.fromCharCode(...bytes.slice(8, 12)) === 'WEBP';
    // Static servers infer Content-Type from the .png/.jpg suffix. A Git LFS
    // pointer or other text payload therefore arrives as image/* even though
    // the provider cannot decode it. Prove the file signature before billing.
    if (!isPng && !isJpeg && !isWebp) {
      console.warn('[Direct3D refs] Skipping invalid image payload:', url);
      return null;
    }
    return await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        resolve(dataUrl.includes(',') ? dataUrl.split(',')[1] : null);
      };
      reader.onerror = () => resolve(null);
      reader.readAsDataURL(new Blob([bytes], { type: blob.type }));
    });
  } catch (err) {
    console.warn('[Direct3D refs] Failed to fetch reference image:', url, err);
    return null;
  }
}

function clampLabel(label: string): string {
  return label.length <= MAX_LABEL_LENGTH ? label : `${label.slice(0, MAX_LABEL_LENGTH - 1)}…`;
}

function namedZones(candidate: ReferenceCandidate): string {
  return candidate.zoneNames.length
    ? ` for ${candidate.kind === 'building' ? 'building(s)' : 'zone(s)'} ${candidate.zoneNames.map((name) => `"${name}"`).join(', ')}`
    : '';
}

function candidateLabel(candidate: ReferenceCandidate, facadeSource: boolean): string {
  const selected = candidate.variant?.label || candidate.selectedId.replace(/_/g, ' ');
  const heading = candidate.kind === 'building'
    ? `${facadeSource ? 'FACADE SOURCE' : 'BUILDING FIDELITY REFERENCE'} — ${candidate.title} — ${selected}`
    : candidate.kind === 'park'
      ? `PARK APPEARANCE REFERENCE — ${candidate.title} — ${selected}`
      : `STREET APPEARANCE REFERENCE — ${candidate.title} — ${selected}`;
  const binding = candidate.kind === 'building'
    ? 'BINDING BUILDING IDENTITY: reproduce this selected variant\'s architectural language, material hierarchy, facade rhythm, openings, roof character and detailing. It overrides generic material examples; never substitute an unrelated architectural style.'
    : candidate.kind === 'park'
      ? `APPEARANCE ONLY: use this variant's planting, surface and furniture materials within the ${candidate.targetDescription ?? 'compiled park'}. The captured 3D scene has already resolved capacity. Keep every path, pavilion, play feature and tree in its captured position; do not copy the reference layout, add facilities or swap their positions.`
      : `APPEARANCE ONLY: use this variant's surface and furnishing materials on the ${candidate.targetDescription ?? 'compiled street'}. Keep the compiled cross-section exact, including the captured count and positions of trees and furnishings. Do not add roads, crossings or connections from this reference.`;
  const identity = candidate.signature?.identity
    ? ` AUTHORED IDENTITY: ${candidate.signature.identity}${candidate.signature.materialZones ? ` Materials: ${candidate.signature.materialZones}.` : ''}`
    : candidate.variant?.description ? ` SELECTED VARIANT: ${candidate.variant.description}` : '';
  return clampLabel(`${heading}${namedZones(candidate)}. ${binding}${identity}`);
}

function addCandidate(
  candidates: Map<string, ReferenceCandidate>,
  candidate: ReferenceCandidate,
  zoneName: string | undefined,
): void {
  const existing = candidates.get(candidate.key);
  if (!existing) {
    if (zoneName) candidate.zoneNames.push(zoneName);
    candidates.set(candidate.key, candidate);
    return;
  }
  if (zoneName && existing.zoneNames.length < 3 && !existing.zoneNames.includes(zoneName)) {
    existing.zoneNames.push(zoneName);
  }
}

function collectCandidates(zones: SiteZone[]): ReferenceCandidate[] {
  const candidates = new Map<string, ReferenceCandidate>();
  for (const zone of zones) {
    const props = asRecord(zone.properties) ?? {};
    if (zone.zone_type === 'building') {
      const rawBaseId = normalizeId(props.development_archetype_id ?? props.archetype_id);
      if (!rawBaseId) continue;
      const baseId = stripCardVariantSuffix(rawBaseId);
      const requestedVariantId = normalizeId(
        props.development_selected_variant_id
        ?? asRecord(props.generation_style_input)?.archetypeId
        ?? baseId,
      );
      const entry = findEntry(BUILDINGS, baseId) ?? findEntry(BUILDINGS, requestedVariantId);
      const variant = findVariant(entry, requestedVariantId);
      // Visual-system view ids such as `<parent>_variant_0` are camera cards,
      // not design variants. Collapse them to the parent so repeated buildings
      // share one reference; only a catalogue design variant remains exact.
      const selectedId = variant ? requestedVariantId : baseId;
      const exactSignature = FAMILIES[selectedId];
      const parentSignature = FAMILIES[baseId] ?? FAMILIES[stripCardVariantSuffix(baseId)];
      const signature = exactSignature ?? parentSignature;
      // Exact variant artwork wins unless an exact compiler signature proves
      // the elevation belongs to this selected variant.
      const imageUrl = exactSignature?.elevationUrl
        ?? variant?.thumbnailUrl
        ?? parentSignature?.elevationUrl
        ?? entry?.thumbnailUrl;
      addCandidate(candidates, {
        key: `building:${selectedId}`,
        kind: 'building',
        title: entry?.title || baseId.replace(/_/g, ' '),
        selectedId,
        imageUrl,
        signature,
        variant,
        zoneNames: [],
      }, zone.name);
      continue;
    }

    const parkId = normalizeId(props.green_space_archetype_id ?? props.plaza_archetype_id);
    if (parkId) {
      const selectedId = normalizeId(
        props.green_space_selected_variant_id
        ?? props.plaza_selected_variant_id
        ?? parkId,
      );
      const entry = findEntry(PARKS, parkId);
      const variant = findVariant(entry, selectedId);
      addCandidate(candidates, {
        key: `park:${selectedId}`,
        kind: 'park',
        title: entry?.title || parkId.replace(/_/g, ' '),
        selectedId,
        imageUrl: variant?.thumbnailUrl ?? entry?.thumbnailUrl,
        variant,
        zoneNames: [],
        targetDescription: targetDescription(props, 'park'),
      }, zone.name);
      continue;
    }

    const streetId = normalizeId(props.road_archetype_id);
    if (!streetId) continue;
    const selectedId = normalizeId(props.road_selected_variant_id ?? streetId);
    const entry = findEntry(STREETS, streetId);
    const variant = findVariant(entry, selectedId);
    addCandidate(candidates, {
      key: `street:${selectedId}`,
      kind: 'street',
      title: entry?.title || streetId.replace(/_/g, ' '),
      selectedId,
      imageUrl: variant?.thumbnailUrl ?? entry?.thumbnailUrl,
      variant,
      zoneNames: [],
      targetDescription: targetDescription(props, 'street'),
    }, zone.name);
  }
  // Buildings remain strict and receive reference capacity first. Public realm
  // follows in stable semantic order and is intentionally size-aware.
  return [...candidates.values()].sort((left, right) => (
    ['building', 'park', 'street'].indexOf(left.kind) - ['building', 'park', 'street'].indexOf(right.kind)
    || left.key.localeCompare(right.key)
  ));
}

/** Collect exact selected-variant artwork for the compiled proposal. */
export async function collectDirect3DArchetypeReferences(
  zones: SiteZone[],
  limit: number = MAX_REFERENCES,
): Promise<Direct3DArchetypeReference[]> {
  const references: Direct3DArchetypeReference[] = [];
  for (const candidate of collectCandidates(zones)) {
    if (references.length >= limit) break;
    if (!candidate.imageUrl) continue;
    const image = await fetchImageBase64(candidate.imageUrl);
    if (!image) continue;
    references.push({
      image_base64: image,
      label: candidateLabel(
        candidate,
        candidate.kind === 'building' && candidate.imageUrl === candidate.signature?.elevationUrl,
      ),
    });
  }
  return references;
}
