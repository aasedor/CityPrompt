import { resolveApiFileUrl } from '@/services/api';
import type { MasterPlan2DReferenceMetadata, SiteZone } from '@/types';

type ZoneProperties = Record<string, unknown>;

type DomainConfig = {
  prefix: 'development' | 'road' | 'green_space' | 'plaza';
  inputKey: 'building' | 'streets_paths' | 'parks' | 'plazas';
  sourceLabel: string;
};

const DOMAIN_CONFIGS: DomainConfig[] = [
  { prefix: 'development', inputKey: 'building', sourceLabel: 'Building archetype' },
  { prefix: 'road', inputKey: 'streets_paths', sourceLabel: 'Street archetype' },
  { prefix: 'green_space', inputKey: 'parks', sourceLabel: 'Landscape archetype' },
  { prefix: 'plaza', inputKey: 'plazas', sourceLabel: 'Plaza archetype' },
];

const ZONE_DOMAIN_FALLBACK: Record<string, DomainConfig['prefix']> = {
  building: 'development',
  residential: 'development',
  development_area: 'development',
  road: 'road',
  green_space: 'green_space',
  parking: 'plaza',
  water: 'green_space',
};

export interface MasterPlan2DCollectedReference {
  id: string;
  url: string;
  label: string;
  zoneName: string;
  sourceLabel: string;
  metadata: MasterPlan2DReferenceMetadata;
}

type PromptLike = {
  positive?: string;
  negative?: string;
};

type ReferenceRecord = {
  id?: string;
  label?: string;
  description?: string;
  imageUrl?: string;
  imagePath?: string;
  url?: string;
  prompt?: PromptLike | Record<string, unknown>;
  generationTags?: string[];
  tags?: string[];
  category?: string;
  subcategory?: string;
  caption?: string;
};

const PLAN_VIEW_REPLACEMENTS: Array<[RegExp, string]> = [
  [/\bfront_day\b/gi, 'daytime plan reference'],
  [/\bfront_golden_hour\b/gi, 'golden-hour plan reference'],
  [/\bfront_overcast\b/gi, 'overcast plan reference'],
  [/\bfront_rain_reflection\b/gi, 'rain-washed plan reference'],
  [/\bfront\s+day\b/gi, 'daytime plan reference'],
  [/\bfront\s+golden\s+hour\b/gi, 'golden-hour plan reference'],
  [/\bfront\s+overcast\b/gi, 'overcast plan reference'],
  [/\bfront\s+rain\s+reflection\b/gi, 'rain-washed plan reference'],
  [/\bfront elevation\b/gi, 'roof plan character'],
  [/\bfront-facing\b/gi, 'plan-view'],
  [/\bstreet-level(?:\s+eye-height)?\s+camera\b/gi, '90-degree overhead orthographic view'],
  [/\beye-height\b/gi, 'overhead orthographic'],
  [/\brestrained perspective distortion\b/gi, 'orthographic clarity'],
  [/\bbalanced verticals\b/gi, 'clean linework'],
  [/\bperspective\b/gi, 'plan-view'],
  [/\bsection perspective\b/gi, 'plan-view massing relationship'],
  [/\bprofile view\b/gi, 'plan-view'],
  [/\bfacade\b/gi, 'architectural edge'],
  [/\bwindows?\b/gi, 'frontage rhythm'],
];

const PLAN_VIEW_DROP_PATTERNS: RegExp[] = [
  /\bcentered subject dominance\b\.?/gi,
  /\bsubject is centered and dominant in frame\b\.?/gi,
  /\bconsistent framing and crop\b\.?/gi,
  /\bcontrolled, low-clutter background\b\.?/gi,
  /\bgrounded cinematic atmosphere\b\.?/gi,
  /\bphotoreal architectural and urban design rendering\b\.?/gi,
  /\bno text overlays(?: inside image)?\b\.?/gi,
  /\bno collage layout\b\.?/gi,
  /\bno watermark or logo text\b\.?/gi,
  /\bno dominant crowds obscuring the subject\b\.?/gi,
  /\bno random unrelated backgrounds\b\.?/gi,
  /\bno fantasy impossible geometry\b\.?/gi,
  /\bno fantasy geometry\b\.?/gi,
  /\bno extreme fisheye perspective\b\.?/gi,
  /\btarget output \d+x\d+(?: \([^)]*\))?\b\.?/gi,
  /\bbenchmark visual direction:[^.]*\.?/gi,
];

function asObject(value: unknown): Record<string, unknown> | undefined {
  return value && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : undefined;
}

function asString(value: unknown): string | undefined {
  if (typeof value !== 'string') return undefined;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value
    .map((entry) => asString(entry))
    .filter((entry): entry is string => Boolean(entry));
}

function sanitizePlanimetricText(value: unknown): string | undefined {
  const text = asString(value);
  if (!text) return undefined;
  let sanitized = text;
  for (const [pattern, replacement] of PLAN_VIEW_REPLACEMENTS) {
    sanitized = sanitized.replace(pattern, replacement);
  }
  for (const pattern of PLAN_VIEW_DROP_PATTERNS) {
    sanitized = sanitized.replace(pattern, ' ');
  }
  sanitized = sanitized.replace(/\s+/g, ' ').replace(/\s+([,.;:])/g, '$1').trim().replace(/^[-,.;:\s]+|[-,.;:\s]+$/g, '');
  return sanitized || undefined;
}

function sanitizeStringArray(value: unknown): string[] {
  return asStringArray(value)
    .map((entry) => sanitizePlanimetricText(entry))
    .filter((entry): entry is string => Boolean(entry));
}

function normalizeImageUrl(value: unknown): string | undefined {
  if (typeof value === 'string' && value.trim().length > 0) {
    return resolveApiFileUrl(value.trim());
  }
  const record = asObject(value);
  if (!record) return undefined;
  const direct = asString(record.imageUrl) || asString(record.url) || asString(record.image_path) || asString(record.imagePath);
  return direct ? resolveApiFileUrl(direct) : undefined;
}

function imageRecordFromUnknown(value: unknown): ReferenceRecord | undefined {
  if (typeof value === 'string') {
    const url = normalizeImageUrl(value);
    return url ? { imageUrl: url, url } : undefined;
  }
  const record = asObject(value);
  if (!record) return undefined;
  const imageUrl = normalizeImageUrl(record);
  return imageUrl
    ? {
        id: asString(record.id),
        label: sanitizePlanimetricText(record.label),
        description: sanitizePlanimetricText(record.description),
        imageUrl,
        imagePath: asString(record.imagePath) || asString(record.image_path),
        prompt: asObject(record.prompt),
        generationTags: sanitizeStringArray(record.generationTags),
        tags: sanitizeStringArray(record.tags),
        category: sanitizePlanimetricText(record.category),
        subcategory: sanitizePlanimetricText(record.subcategory),
        caption: sanitizePlanimetricText(record.caption),
      }
    : undefined;
}

function extractPromptText(record?: ReferenceRecord): string | undefined {
  if (!record) return undefined;
  return record.caption || record.description || record.label;
}

function collectTags(...values: unknown[]): string[] | undefined {
  const tags = new Set<string>();
  for (const value of values) {
    for (const tag of sanitizeStringArray(value)) {
      tags.add(tag);
    }
  }
  return tags.size > 0 ? Array.from(tags) : undefined;
}

function resolveGenerationStyle(props: ZoneProperties, domain: DomainConfig): Record<string, unknown> | undefined {
  if (domain.prefix === 'development') {
    return asObject(props['generation_style_input']);
  }
  const map = asObject(props['generation_style_inputs']);
  return map ? asObject(map[domain.inputKey]) : undefined;
}

function resolveDomainContext(zone: SiteZone, props: ZoneProperties, prefix?: DomainConfig['prefix']) {
  const domainPrefix = prefix || ZONE_DOMAIN_FALLBACK[zone.zone_type] || 'development';
  const generationStyle = resolveGenerationStyle(props, DOMAIN_CONFIGS.find((item) => item.prefix === domainPrefix) || DOMAIN_CONFIGS[0]);
  return {
    prefix: domainPrefix,
    domain: domainPrefix === 'road' ? 'streets_paths' : domainPrefix === 'green_space' ? 'parks' : domainPrefix === 'plaza' ? 'plazas' : 'building',
    category: sanitizePlanimetricText(props[`${domainPrefix}_aesthetic_category`]) || sanitizePlanimetricText(generationStyle?.aestheticCategoryLabel),
    subcategory:
      sanitizePlanimetricText(props[`${domainPrefix}_subcategory`])
      || sanitizePlanimetricText(generationStyle?.['buildingSubcategory'])
      || sanitizePlanimetricText(generationStyle?.['subtype']),
    archetypeName: sanitizePlanimetricText(props[`${domainPrefix}_archetype_label`]),
    generationStyle,
    styleProfile: asObject(props[`${domainPrefix}_style_profile`]) || asObject(generationStyle?.styleProfile),
    tags: collectTags(props[`${domainPrefix}_generation_tags`], generationStyle?.generationTags),
  };
}

function buildMetadata(
  zone: SiteZone,
  props: ZoneProperties,
  source: 'zone_prompt' | 'archetype' | 'reference_image',
  sourceLabel: string,
  url: string,
  order: number,
  domainPrefix?: DomainConfig['prefix'],
  record?: ReferenceRecord,
): MasterPlan2DReferenceMetadata {
  const context = resolveDomainContext(zone, props, domainPrefix);
  return {
    reference_id: record?.id || `${zone.id}:${source}:${order}`,
    zone_id: zone.id,
    zone_name: zone.name,
    zone_type: zone.zone_type,
    domain: context.domain,
    category: record?.category || context.category,
    subcategory: record?.subcategory || context.subcategory,
    archetype_name: record?.label || context.archetypeName,
    asset_id: record?.id,
    image_url: url,
    image_path: record?.imagePath,
    source,
    source_label: sourceLabel,
    prompt_text: extractPromptText(record),
    caption: record?.caption || record?.label || record?.description || zone.name,
    tags: collectTags(record?.generationTags, record?.tags, context.tags),
    selection_order: order,
    style_profile: context.styleProfile,
    generation_style: context.generationStyle,
  };
}

function pushReference(
  list: MasterPlan2DCollectedReference[],
  seen: Set<string>,
  zone: SiteZone,
  source: 'zone_prompt' | 'archetype' | 'reference_image',
  sourceLabel: string,
  order: number,
  domainPrefix?: DomainConfig['prefix'],
  value?: unknown,
) {
  const record = imageRecordFromUnknown(value);
  const url = record?.imageUrl || normalizeImageUrl(value);
  if (!url) return;
  const dedupeKey = `${record?.id || ''}::${url}`;
  if (seen.has(dedupeKey)) return;
  seen.add(dedupeKey);
  const metadata = buildMetadata(zone, (zone.properties || {}) as ZoneProperties, source, sourceLabel, url, order, domainPrefix, record);
  list.push({
    id: metadata.reference_id || dedupeKey,
    url,
    label: metadata.archetype_name || metadata.caption || zone.name || 'Reference image',
    zoneName: zone.name || zone.zone_type.replace(/_/g, ' '),
    sourceLabel,
    metadata,
  });
}

export function collectMasterPlan2DReferences(siteZones: SiteZone[]): MasterPlan2DCollectedReference[] {
  const seen = new Set<string>();
  const references: MasterPlan2DCollectedReference[] = [];
  const orderedZones = [...siteZones].sort((a, b) => a.sort_order - b.sort_order || a.created_at.localeCompare(b.created_at));

  for (const zone of orderedZones) {
    const props = (zone.properties || {}) as ZoneProperties;
    let order = 0;

    for (const domain of DOMAIN_CONFIGS) {
      const selectedReference = props[`${domain.prefix}_selected_reference`];
      if (selectedReference) {
        pushReference(references, seen, zone, 'zone_prompt', 'Zone prompt', order++, domain.prefix, selectedReference);
      }

      const selectedId = asString(props[`${domain.prefix}_archetype_id`]);
      const archetypeImages = Array.isArray(props[`${domain.prefix}_archetype_images`]) ? (props[`${domain.prefix}_archetype_images`] as unknown[]) : [];
      const matchingArchetype = archetypeImages
        .map((entry) => imageRecordFromUnknown(entry))
        .find((entry) => entry && (entry.id === selectedId || entry.imageUrl === normalizeImageUrl(props[`${domain.prefix}_archetype_image`])));
      const archetypeValue = matchingArchetype || props[`${domain.prefix}_archetype_image`];
      if (archetypeValue) {
        pushReference(references, seen, zone, 'archetype', domain.sourceLabel, order++, domain.prefix, archetypeValue);
      }
    }

    const referenceImages = Array.isArray(props['reference_images']) ? props['reference_images'] : [];
    for (const [index, value] of referenceImages.entries()) {
      pushReference(references, seen, zone, 'reference_image', 'Reference image', order + index, undefined, value);
    }
  }

  return references;
}

