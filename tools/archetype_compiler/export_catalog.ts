/**
 * Export building archetypes from the REAL aesthetic catalogue to machine-readable JSON.
 *
 * This deliberately imports the same module the app uses (aestheticCatalog.ts), so the
 * derived Urban Intelligence payload (generationStyleInput, downstreamHints.reuseKeys,
 * aestheticCategoryId/Label, ...) is produced by the production code path — the catalogue
 * is never duplicated or re-derived here.
 *
 * Run from the frontend directory so Vite aliases / import.meta.env resolve:
 *
 *   cd frontend
 *   npx vite-node ../tools/archetype_compiler/export_catalog.ts -- --list
 *   npx vite-node ../tools/archetype_compiler/export_catalog.ts -- \
 *     --archetype-id nordic_timber_midrise --output ../build/archetype-source.json
 *   npx vite-node ../tools/archetype_compiler/export_catalog.ts -- --all --output ../build/archetype-catalog.json
 */
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, extname, posix, resolve } from 'node:path';
import {
  BUILDING_AESTHETIC_CATEGORIES_V2,
  BUILDING_AESTHETIC_OPTIONS_V2,
  type AestheticOption,
  type ArchetypeVariant,
} from '../../frontend/src/components/viewer/aestheticCatalog';
import buildingArchetypeLibrary from '../../frontend/src/data/buildingArchetypes.json';

const EXPORT_SCHEMA = 'archetype-source@1';

type RawSeed = Record<string, unknown> & {
  id: string;
  title?: string;
  facadeDetail?: Record<string, string>;
  roofDetail?: Record<string, string>;
  palette?: Record<string, string>;
  prompt?: unknown;
  renderPrompt?: unknown;
  shadeId?: string | null;
  thumbnailUrl?: string;
  districtKit?: string;
  footprintCompatibility?: AestheticOption['footprintCompatibility'];
  description?: string;
  suggestedFloorHeight?: number;
};

const RAW_SEEDS: RawSeed[] = ((buildingArchetypeLibrary as { archetypes?: RawSeed[] }).archetypes ?? []);
const SEED_BY_ID = new Map(RAW_SEEDS.map((seed) => [seed.id, seed]));

interface ExportedArchetype {
  exportSchema: typeof EXPORT_SCHEMA;
  exportedAt: string;
  source: {
    catalog: 'frontend/src/data/buildingArchetypes.json';
    derivation: 'frontend/src/components/viewer/aestheticCatalog.ts#toAestheticOption';
  };
  archetypeId: string;
  archetypeLabel: string;
  domain: 'building';
  developmentType?: string;
  buildingSubcategory?: string;
  aestheticCategoryId?: string;
  aestheticCategoryLabel?: string;
  description?: string;
  generationTags?: string[];
  styleProfile?: AestheticOption['styleProfile'];
  generationStyleInput?: AestheticOption['generationStyleInput'];
  facadeDetail?: Record<string, string>;
  roofDetail?: Record<string, string>;
  palette?: Record<string, string>;
  shadeId?: string | null;
  prompt?: unknown;
  renderPrompt?: unknown;
  thumbnailUrl?: string;
  districtKit?: string;
  footprintCompatibility?: AestheticOption['footprintCompatibility'];
  dimensions: {
    suggestedWidth_m?: number;
    suggestedDepth_m?: number;
    minWidth_m?: number;
    maxWidth_m?: number;
    minDepth_m?: number;
    maxDepth_m?: number;
    suggestedAreaSqm?: number;
    minAreaSqm?: number;
    maxAreaSqm?: number;
    minFloors?: number;
    maxFloors?: number;
    suggestedFloorHeight?: number;
    aspectRatio?: string;
  };
  archetypeImages?: AestheticOption['archetypeImages'];
  referenceViews: Array<{
    role: 'street_identity' | 'oblique_massing' | 'roof_or_aerial';
    path: string;
  }>;
  variants?: ArchetypeVariant[];
  selectedVariant?: ArchetypeVariant | null;
}

function discoverReferenceViews(thumbnailUrl?: string): ExportedArchetype['referenceViews'] {
  if (!thumbnailUrl?.startsWith('/archetypes/')) return [];

  const normalized = thumbnailUrl.replace(/\\/g, '/');
  const publicPath = resolve(process.cwd(), 'public', normalized.slice(1));
  if (!existsSync(publicPath)) return [];

  const extension = extname(normalized);
  const stem = normalized.slice(0, -extension.length);
  const candidates: ExportedArchetype['referenceViews'] = [
    { role: 'street_identity', path: normalized },
    { role: 'oblique_massing', path: `${stem}_angle_60.jpg` },
    { role: 'roof_or_aerial', path: `${stem}_angle_90.jpg` },
  ];

  return candidates.filter((candidate) => {
    const candidatePath = resolve(process.cwd(), 'public', candidate.path.slice(1));
    return existsSync(candidatePath);
  }).map((candidate) => ({ ...candidate, path: posix.normalize(candidate.path) }));
}

function buildPayload(option: AestheticOption, variantId?: string): ExportedArchetype {
  const seed = SEED_BY_ID.get(option.id);
  let selectedVariant: ArchetypeVariant | null = null;
  let selectedVariantIndex = -1;
  if (variantId) {
    selectedVariantIndex = (option.variants ?? []).findIndex((variant) => variant.id === variantId);
    selectedVariant = selectedVariantIndex >= 0 ? option.variants?.[selectedVariantIndex] ?? null : null;
    if (!selectedVariant) {
      const available = (option.variants ?? []).map((variant) => variant.id).join(', ') || '(none)';
      throw new Error(`Variant '${variantId}' not found on archetype '${option.id}'. Available variants: ${available}`);
    }
  }
  const generationStyleInput = selectedVariant && option.generationStyleInput
    ? {
        ...option.generationStyleInput,
        archetypeId: `${option.id}_variant_${selectedVariantIndex}`,
        archetypeLabel: selectedVariant.label,
        archetypeImageUrl: selectedVariant.thumbnailUrl,
        archetypeImagePath: selectedVariant.thumbnailUrl,
      }
    : option.generationStyleInput;
  const thumbnailUrl = selectedVariant?.thumbnailUrl ?? seed?.thumbnailUrl;

  return {
    exportSchema: EXPORT_SCHEMA,
    exportedAt: new Date().toISOString(),
    source: {
      catalog: 'frontend/src/data/buildingArchetypes.json',
      derivation: 'frontend/src/components/viewer/aestheticCatalog.ts#toAestheticOption',
    },
    archetypeId: option.id,
    archetypeLabel: option.label,
    domain: 'building',
    developmentType: option.developmentType,
    buildingSubcategory: option.buildingSubcategory,
    aestheticCategoryId: option.categoryId,
    aestheticCategoryLabel: BUILDING_AESTHETIC_CATEGORIES_V2.find((category) => category.id === option.categoryId)?.label,
    description: selectedVariant?.description ?? option.description,
    generationTags: option.generationTags,
    styleProfile: option.styleProfile,
    generationStyleInput,
    facadeDetail: selectedVariant?.facadeDetail ?? seed?.facadeDetail,
    roofDetail: selectedVariant?.roofDetail ?? seed?.roofDetail,
    palette: selectedVariant?.palette ?? seed?.palette,
    shadeId: selectedVariant?.shadeId ?? seed?.shadeId,
    prompt: seed?.prompt,
    renderPrompt: selectedVariant?.renderPrompt ?? seed?.renderPrompt,
    thumbnailUrl,
    districtKit: seed?.districtKit,
    footprintCompatibility: option.footprintCompatibility,
    dimensions: {
      suggestedWidth_m: selectedVariant?.suggestedWidth_m ?? option.suggestedWidth_m,
      suggestedDepth_m: selectedVariant?.suggestedDepth_m ?? option.suggestedDepth_m,
      minWidth_m: option.minWidth_m,
      maxWidth_m: option.maxWidth_m,
      minDepth_m: option.minDepth_m,
      maxDepth_m: option.maxDepth_m,
      suggestedAreaSqm: selectedVariant?.suggestedAreaSqm ?? option.suggestedAreaSqm,
      minAreaSqm: selectedVariant?.minAreaSqm ?? option.minAreaSqm,
      maxAreaSqm: selectedVariant?.maxAreaSqm ?? option.maxAreaSqm,
      minFloors: selectedVariant?.minFloors ?? option.minFloors,
      maxFloors: selectedVariant?.maxFloors ?? option.maxFloors,
      suggestedFloorHeight: selectedVariant?.suggestedFloorHeight ?? option.suggestedFloorHeight ?? seed?.suggestedFloorHeight,
      aspectRatio: selectedVariant?.aspectRatio ?? option.aspectRatio,
    },
    archetypeImages: option.archetypeImages,
    referenceViews: discoverReferenceViews(thumbnailUrl),
    variants: option.variants,
    selectedVariant,
  };
}

function parseArgs(argv: string[]) {
  const args = argv.filter((token) => token !== '--');
  const flags: Record<string, string | boolean> = {};
  for (let i = 0; i < args.length; i += 1) {
    const token = args[i];
    if (!token.startsWith('--')) continue;
    const key = token.slice(2);
    const next = args[i + 1];
    if (next !== undefined && !next.startsWith('--')) {
      flags[key] = next;
      i += 1;
    } else {
      flags[key] = true;
    }
  }
  return flags;
}

function writeJson(path: string, value: unknown) {
  const absolute = resolve(process.cwd(), path);
  mkdirSync(dirname(absolute), { recursive: true });
  writeFileSync(absolute, JSON.stringify(value, null, 2), 'utf-8');
  return absolute;
}

function main() {
  const flags = parseArgs(process.argv.slice(2));

  if (flags.list) {
    const rows = BUILDING_AESTHETIC_OPTIONS_V2.map((option) => ({
      id: option.id,
      label: option.label,
      developmentType: option.developmentType ?? '',
      aestheticCategory: option.categoryId ?? '',
      floors: `${option.minFloors ?? '?'}-${option.maxFloors ?? '?'}`,
      footprint: `${option.suggestedWidth_m ?? '?'}x${option.suggestedDepth_m ?? '?'}m`,
      variants: (option.variants ?? []).map((variant) => variant.id).join(','),
    }));
    console.log(JSON.stringify(rows, null, 2));
    console.error(`\n${rows.length} building archetypes available.`);
    return;
  }

  if (flags.all) {
    const output = typeof flags.output === 'string' ? flags.output : 'build/archetype-catalog.json';
    const payloads = BUILDING_AESTHETIC_OPTIONS_V2.map((option) => buildPayload(option));
    const absolute = writeJson(output, payloads);
    console.error(`Exported ${payloads.length} archetypes -> ${absolute}`);
    console.log(absolute);
    return;
  }

  const archetypeId = typeof flags['archetype-id'] === 'string' ? (flags['archetype-id'] as string) : undefined;
  if (!archetypeId) {
    console.error('Usage: vite-node export_catalog.ts -- (--list | --all | --archetype-id <id> [--variant-id <id>]) [--output <path>]');
    process.exitCode = 2;
    return;
  }

  const option = BUILDING_AESTHETIC_OPTIONS_V2.find((candidate) => candidate.id === archetypeId);
  if (!option) {
    const near = BUILDING_AESTHETIC_OPTIONS_V2
      .filter((candidate) => candidate.id.includes(archetypeId.slice(0, Math.max(4, archetypeId.length / 2))))
      .map((candidate) => candidate.id)
      .slice(0, 8);
    console.error(`Archetype '${archetypeId}' not found in the building catalogue (223 entries).`);
    if (near.length) console.error(`Did you mean: ${near.join(', ')}`);
    console.error('Run with --list to see every id.');
    process.exitCode = 2;
    return;
  }

  const variantId = typeof flags['variant-id'] === 'string' ? (flags['variant-id'] as string) : undefined;
  const payload = buildPayload(option, variantId);
  const output = typeof flags.output === 'string' ? (flags.output as string) : 'build/archetype-source.json';
  const absolute = writeJson(output, payload);
  console.error(`Exported '${archetypeId}'${variantId ? ` (variant ${variantId})` : ''} -> ${absolute}`);
  console.log(absolute);
}

main();
