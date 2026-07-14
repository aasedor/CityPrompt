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
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
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
  variants?: ArchetypeVariant[];
  selectedVariant?: ArchetypeVariant | null;
}

function buildPayload(option: AestheticOption, variantId?: string): ExportedArchetype {
  const seed = SEED_BY_ID.get(option.id);
  let selectedVariant: ArchetypeVariant | null = null;
  if (variantId) {
    selectedVariant = (option.variants ?? []).find((variant) => variant.id === variantId) ?? null;
    if (!selectedVariant) {
      const available = (option.variants ?? []).map((variant) => variant.id).join(', ') || '(none)';
      throw new Error(`Variant '${variantId}' not found on archetype '${option.id}'. Available variants: ${available}`);
    }
  }

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
    description: option.description,
    generationTags: option.generationTags,
    styleProfile: option.styleProfile,
    generationStyleInput: option.generationStyleInput,
    facadeDetail: seed?.facadeDetail,
    roofDetail: seed?.roofDetail,
    palette: seed?.palette,
    shadeId: seed?.shadeId,
    prompt: seed?.prompt,
    renderPrompt: seed?.renderPrompt,
    thumbnailUrl: seed?.thumbnailUrl,
    districtKit: seed?.districtKit,
    dimensions: {
      suggestedWidth_m: option.suggestedWidth_m,
      suggestedDepth_m: option.suggestedDepth_m,
      minWidth_m: option.minWidth_m,
      maxWidth_m: option.maxWidth_m,
      minDepth_m: option.minDepth_m,
      maxDepth_m: option.maxDepth_m,
      suggestedAreaSqm: option.suggestedAreaSqm,
      minAreaSqm: option.minAreaSqm,
      maxAreaSqm: option.maxAreaSqm,
      minFloors: option.minFloors,
      maxFloors: option.maxFloors,
      suggestedFloorHeight: option.suggestedFloorHeight ?? seed?.suggestedFloorHeight,
      aspectRatio: option.aspectRatio,
    },
    archetypeImages: option.archetypeImages,
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
