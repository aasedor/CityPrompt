#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '..');

const dataRoot = path.join(repoRoot, 'frontend', 'src', 'data');
const publicRoot = path.join(repoRoot, 'frontend', 'public', 'archetypes');

const visualSystemPath = path.join(dataRoot, 'archetypeVisualSystem.json');

const domainDefs = {
  buildings: {
    key: 'buildings',
    configPath: path.join(dataRoot, 'buildingArchetypes.json'),
    outputDir: path.join(publicRoot, 'buildings'),
    webPrefix: '/archetypes/buildings',
    promptTemplateKey: 'buildings',
    defaultSubjectHint: 'canonical architectural archetype card',
  },
  streets_pathways: {
    key: 'streets_pathways',
    configPath: path.join(dataRoot, 'streetPathArchetypes.json'),
    outputDir: path.join(publicRoot, 'streets'),
    webPrefix: '/archetypes/streets',
    promptTemplateKey: 'streets_pathways',
    defaultSubjectHint: 'canonical streets and pathways corridor archetype card',
  },
  parks_plazas: {
    key: 'parks_plazas',
    configPath: path.join(dataRoot, 'openSpaceArchetypes.json'),
    outputDir: path.join(publicRoot, 'openspaces'),
    webPrefix: '/archetypes/openspaces',
    promptTemplateKey: 'parks_plazas',
    defaultSubjectHint: 'canonical parks and plazas archetype card',
  },
};

const BENCHMARK_STYLE_RULES = [
  'Benchmark visual direction: premium photoreal architectural visualization cards',
  'Front-facing or strongly centered composition',
  'Subject is centered and dominant in frame',
  'Restrained perspective distortion and balanced verticals',
  'Consistent lighting mood and atmospheric realism',
  'Believable material richness and facade/landscape detail',
  'Minimal clutter and no unrelated distracting background elements',
  'No text, labels, logos, or watermarks in image',
  'No collage layout and no fantasy distortions',
];

const METADATA_SCHEMA_VERSION = 'archetype-image-v2';

function normalizeDomainForGeneration(domainKey) {
  if (domainKey === 'buildings') return 'building';
  if (domainKey === 'streets_pathways') return 'street_pathway';
  return 'park_plaza';
}

function inferAssetCategory(domainKey) {
  if (domainKey === 'buildings') return 'building';
  if (domainKey === 'streets_pathways') return 'streets_paths';
  return 'parks_plazas';
}

function normalizeSubtype(domainKey, archetype) {
  if (domainKey === 'buildings') {
    return typeof archetype?.buildingSubcategory === 'string' && archetype.buildingSubcategory.trim()
      ? archetype.buildingSubcategory.trim()
      : archetype?.id;
  }
  if (domainKey === 'streets_pathways') {
    return typeof archetype?.volume === 'string' && archetype.volume.trim()
      ? archetype.volume.trim()
      : archetype?.id;
  }
  if (typeof archetype?.spaceType === 'string' && archetype.spaceType.trim()) {
    return archetype.spaceType.trim();
  }
  return archetype?.id;
}

function safeObject(value) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return value;
  }
  return {};
}

function normalizeStringArray(value) {
  if (!Array.isArray(value)) return [];
  const seen = new Set();
  const normalized = [];
  for (const item of value) {
    if (typeof item !== 'string') continue;
    const trimmed = item.trim();
    if (!trimmed) continue;
    if (seen.has(trimmed)) continue;
    seen.add(trimmed);
    normalized.push(trimmed);
  }
  return normalized;
}

function inferMaterialDirection(styleProfile, generationTags) {
  const explicitMaterials = normalizeStringArray(styleProfile?.materials);
  if (explicitMaterials.length > 0) {
    return explicitMaterials;
  }

  const inferred = [];
  const candidateKeys = [
    'surfaceType',
    'pavingType',
    'corridorCharacter',
    'facadeRhythm',
    'roofForm',
    'windowStyle',
    'plantingType',
  ];

  for (const key of candidateKeys) {
    const value = styleProfile?.[key];
    if (typeof value === 'string' && value.trim()) {
      inferred.push(value.trim());
    }
  }

  if (inferred.length > 0) {
    return Array.from(new Set(inferred));
  }

  return generationTags.slice(0, 5);
}

function parseOutputSize(sizeValue, fallbackOutput) {
  const fallbackWidth = Number(fallbackOutput?.width) || 1200;
  const fallbackHeight = Number(fallbackOutput?.height) || 900;
  const fallbackAspect = typeof fallbackOutput?.aspectRatio === 'string' ? fallbackOutput.aspectRatio : '4:3';

  const match = /^\s*(\d+)x(\d+)\s*$/i.exec(String(sizeValue || ''));
  if (!match) {
    return {
      width: fallbackWidth,
      height: fallbackHeight,
      aspectRatio: fallbackAspect,
    };
  }

  const width = Number(match[1]);
  const height = Number(match[2]);
  if (!Number.isFinite(width) || !Number.isFinite(height) || width <= 0 || height <= 0) {
    return {
      width: fallbackWidth,
      height: fallbackHeight,
      aspectRatio: fallbackAspect,
    };
  }

  return {
    width,
    height,
    aspectRatio: `${width}:${height}`,
  };
}

function inferModelConversionHints({ domainDef, archetype, variant, generationTags, styleProfile, imageRefs }) {
  const domain = normalizeDomainForGeneration(domainDef.key);
  const assetCategory = inferAssetCategory(domainDef.key);
  const subtype = normalizeSubtype(domainDef.key, archetype);

  let geometryStrategy = 'facade_extrusion_with_roof_profile';
  let parametricInputs = ['width_m', 'depth_m', 'height_m', 'floor_count', 'setback_front_m', 'setback_side_m'];
  let materialSlots = ['facade_primary', 'facade_secondary', 'trim', 'glazing', 'roof', 'ground'];
  let sceneElements = ['street_trees', 'lighting', 'street_furniture'];

  if (domainDef.key === 'streets_pathways') {
    geometryStrategy = 'corridor_ribbon_with_edge_system';
    parametricInputs = ['corridor_width_m', 'lane_count', 'mode_allocation', 'sidewalk_width_m', 'median_width_m'];
    materialSlots = ['carriageway', 'cycleway', 'sidewalk', 'curb', 'lane_markings', 'street_furniture'];
    sceneElements = ['trees', 'lighting', 'signage', 'crossings', 'seating'];
  } else if (domainDef.key === 'parks_plazas') {
    geometryStrategy = 'terrain_patch_with_surface_zones';
    parametricInputs = ['path_density', 'canopy_density', 'openness_ratio', 'water_feature_scale', 'seating_density'];
    materialSlots = ['paving_primary', 'paving_secondary', 'groundcover', 'canopy', 'water', 'site_furniture'];
    sceneElements = ['planting_layers', 'site_furniture', 'water_features', 'lighting'];
  }

  const reuseSignature = {
    domain,
    asset_category: assetCategory,
    archetype_id: archetype.id,
    archetype_label: archetype.title,
    aesthetic_category_id: archetype.aestheticCategory || null,
    aesthetic_category_label: null,
    building_subcategory: archetype.buildingSubcategory || null,
    subtype,
    generation_tags: generationTags,
    style_profile: styleProfile,
  };

  return {
    profileVersion: METADATA_SCHEMA_VERSION,
    profileId: `${domainDef.key}:${archetype.id}:${variant.id}`,
    targetDomain: domain,
    assetCategory,
    subtype,
    geometryStrategy,
    parametricInputs,
    materialSlots,
    sceneElements,
    qualityTarget: 'premium_photoreal',
    lodTargets: {
      lod0TriangleBudget: 180000,
      lod1TriangleBudget: 80000,
      lod2TriangleBudget: 30000,
    },
    imageReferences: imageRefs,
    reuseSignature,
  };
}

function buildGenerationStyleInput({
  domainDef,
  archetype,
  variant,
  bundle,
  categoryLabel,
  generationTags,
  styleProfile,
  imageRefs,
}) {
  const domain = normalizeDomainForGeneration(domainDef.key);
  const subtype = normalizeSubtype(domainDef.key, archetype);
  const archetypeImageId = `${archetype.id}_${variant.id}`;
  const materialDirection = inferMaterialDirection(styleProfile, generationTags);

  return {
    schemaVersion: METADATA_SCHEMA_VERSION,
    source: 'archetype_image_library',
    domain,
    developmentType: Array.isArray(archetype?.developmentTypes) ? archetype.developmentTypes[0] : undefined,
    buildingSubcategory: archetype?.buildingSubcategory,
    subtype,
    aestheticCategoryId: archetype?.aestheticCategory,
    aestheticCategoryLabel: categoryLabel,
    archetypeId: archetype?.id,
    archetypeLabel: archetype?.title,
    archetypeImageId,
    archetypeImageVariantId: variant?.id,
    archetypeImageVariantLabel: bundle?.variantTitle,
    archetypeImageUrl: imageRefs?.svg,
    archetypeImagePath: imageRefs?.png,
    generationTags,
    imagePrompt: {
      positive: bundle?.positive,
      negative: bundle?.negative,
      compositionRules: [],
      renderingRules: [],
      output: bundle?.output,
    },
    styleProfile,
    downstreamHints: {
      sceneDressing: generationTags,
      materialDirection,
      reuseKeys: [
        domainDef.key,
        archetype?.aestheticCategory,
        archetype?.id,
        variant?.id,
        subtype,
      ].filter(Boolean),
    },
  };
}

function escapeXml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function parseArgs(argv) {
  const args = {
    domains: ['buildings', 'streets_pathways', 'parks_plazas'],
    dryRun: false,
    overwrite: false,
    limit: undefined,
    model: process.env.ARCHETYPE_IMAGE_MODEL || 'gpt-image-1',
    quality: process.env.ARCHETYPE_IMAGE_QUALITY || 'high',
    size: process.env.ARCHETYPE_IMAGE_SIZE || '1536x1024',
    delayMs: Number(process.env.ARCHETYPE_IMAGE_DELAY_MS || 900),
    onlyArchetype: process.env.ARCHETYPE_ONLY || undefined,
    variantIds: String(process.env.ARCHETYPE_VARIANTS || '')
      .split(',')
      .map((part) => part.trim())
      .filter(Boolean),
  };

  for (const raw of argv) {
    const arg = String(raw || '');
    if (arg === '--dry-run') {
      args.dryRun = true;
      continue;
    }
    if (arg === '--overwrite') {
      args.overwrite = true;
      continue;
    }
    if (arg.startsWith('--domains=')) {
      args.domains = arg
        .slice('--domains='.length)
        .split(',')
        .map((part) => part.trim())
        .filter(Boolean);
      continue;
    }
    if (arg.startsWith('--limit=')) {
      const parsed = Number(arg.slice('--limit='.length));
      if (Number.isFinite(parsed) && parsed > 0) {
        args.limit = Math.floor(parsed);
      }
      continue;
    }
    if (arg.startsWith('--model=')) {
      const value = arg.slice('--model='.length).trim();
      if (value) args.model = value;
      continue;
    }
    if (arg.startsWith('--quality=')) {
      const value = arg.slice('--quality='.length).trim();
      if (value) args.quality = value;
      continue;
    }
    if (arg.startsWith('--size=')) {
      const value = arg.slice('--size='.length).trim();
      if (value) args.size = value;
      continue;
    }
    if (arg.startsWith('--delay-ms=')) {
      const parsed = Number(arg.slice('--delay-ms='.length));
      if (Number.isFinite(parsed) && parsed >= 0) {
        args.delayMs = parsed;
      }
      continue;
    }
    if (arg.startsWith('--archetype=')) {
      const value = arg.slice('--archetype='.length).trim();
      if (value) args.onlyArchetype = value;
      continue;
    }
    if (arg.startsWith('--variants=')) {
      args.variantIds = arg
        .slice('--variants='.length)
        .split(',')
        .map((part) => part.trim())
        .filter(Boolean);
      continue;
    }
  }

  return args;
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function readJson(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Missing JSON file: ${filePath}`);
  }
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, payload) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function joinPromptParts(parts) {
  return parts
    .filter((part) => typeof part === 'string' && part.trim().length > 0)
    .map((part) => part.trim())
    .join('. ');
}

function toSentence(value) {
  if (typeof value !== 'string') return '';
  const trimmed = value.trim();
  if (!trimmed) return '';
  return trimmed;
}

function stringifyStyleProfile(styleProfile) {
  if (!styleProfile || typeof styleProfile !== 'object' || Array.isArray(styleProfile)) return [];
  const lines = [];
  for (const [key, value] of Object.entries(styleProfile)) {
    if (typeof value === 'string' && value.trim()) {
      lines.push(`${key}: ${value.trim()}`);
      continue;
    }
    if (Array.isArray(value)) {
      const items = value.filter((item) => typeof item === 'string' && item.trim()).map((item) => item.trim());
      if (items.length > 0) {
        lines.push(`${key}: ${items.join(', ')}`);
      }
    }
  }
  return lines;
}

function buildPromptBundle({ visualSystem, domainTemplate, archetype, variant, domainDef }) {
  const output = visualSystem?.output || { width: 1200, height: 900, aspectRatio: '4:3' };
  const variantTitle = toSentence(variant?.title) || variant.id;
  const variantLighting = toSentence(variant?.lighting) || 'neutral daylight';

  const subject = toSentence(archetype?.prompt?.subject)
    || (typeof domainTemplate?.subjectTemplate === 'string'
      ? domainTemplate.subjectTemplate.replace('{{title}}', archetype.title)
      : `${archetype.title} ${domainDef.defaultSubjectHint}`);

  const details = [
    ...(Array.isArray(archetype?.prompt?.details) ? archetype.prompt.details : []),
    ...(Array.isArray(domainTemplate?.details) ? domainTemplate.details : []),
    ...(Array.isArray(visualSystem?.sharedCompositionRules) ? visualSystem.sharedCompositionRules : []),
    ...(Array.isArray(visualSystem?.sharedRenderingRules) ? visualSystem.sharedRenderingRules : []),
    ...BENCHMARK_STYLE_RULES,
    `${variantTitle} using ${variantLighting}`,
    `Target output ${output.width}x${output.height} (${output.aspectRatio})`,
  ];

  const styleProfileLines = stringifyStyleProfile(archetype?.styleProfile);
  if (styleProfileLines.length > 0) {
    details.push('Style profile guidance:');
    details.push(...styleProfileLines);
  }

  const negatives = [
    ...(Array.isArray(archetype?.prompt?.negative) ? archetype.prompt.negative : []),
    ...(Array.isArray(visualSystem?.sharedNegativeGuidance) ? visualSystem.sharedNegativeGuidance : []),
  ];

  const positive = joinPromptParts([subject, ...details]);
  const negative = joinPromptParts(negatives);

  const finalPrompt = [
    'Create exactly one high-fidelity image for a public-facing urban planning archetype selector.',
    positive,
    negative ? `Negative guidance: ${negative}.` : '',
  ].filter(Boolean).join(' ');

  return {
    prompt: finalPrompt,
    positive,
    negative,
    output,
    variantTitle,
    variantLighting,
  };
}

async function fetchImageFromOpenAI({ apiKey, model, quality, size, prompt }) {
  const payload = {
    model,
    prompt,
    size,
    quality,
  };

  const response = await fetch('https://api.openai.com/v1/images/generations', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`OpenAI image generation failed (${response.status}): ${text}`);
  }

  const json = await response.json();
  const first = Array.isArray(json?.data) ? json.data[0] : undefined;
  if (!first) {
    throw new Error('OpenAI response missing image payload');
  }

  if (typeof first.b64_json === 'string' && first.b64_json.length > 0) {
    return Buffer.from(first.b64_json, 'base64');
  }

  if (typeof first.url === 'string' && first.url.length > 0) {
    const remote = await fetch(first.url);
    if (!remote.ok) {
      throw new Error(`Failed to download generated image URL (${remote.status})`);
    }
    const arrayBuffer = await remote.arrayBuffer();
    return Buffer.from(arrayBuffer);
  }

  throw new Error('OpenAI response missing b64_json/url image data');
}

function buildSvgWrapper({ width, height, pngFilename, alt, metadata }) {
  const metadataNode = metadata
    ? `\n  <metadata id="archetype-card-metadata" data-format="json">${escapeXml(JSON.stringify(metadata))}</metadata>`
    : '';

  return `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="${alt}">${metadataNode}\n  <image href="./${pngFilename}" x="0" y="0" width="${width}" height="${height}" preserveAspectRatio="xMidYMid slice" />\n</svg>\n`;
}

function domainSummaryInit() {
  return {
    domains: 0,
    archetypes: 0,
    variants: 0,
    generated: 0,
    skipped: 0,
    failures: 0,
  };
}

async function processDomain({ domainDef, visualSystem, args, apiKey, summary }) {
  const config = readJson(domainDef.configPath);
  const allVariants = Array.isArray(visualSystem?.cardVariants) ? visualSystem.cardVariants : [];
  const requestedVariantIds = Array.isArray(args.variantIds)
    ? args.variantIds.filter((id) => typeof id === 'string' && id.trim().length > 0)
    : [];
  const variants = requestedVariantIds.length > 0
    ? allVariants.filter((variant) => requestedVariantIds.includes(variant.id))
    : allVariants;

  if (requestedVariantIds.length > 0 && variants.length === 0) {
    throw new Error(
      `No matching variants for domain '${domainDef.key}'. Requested: ${requestedVariantIds.join(', ')}. Available: ${allVariants.map((variant) => variant.id).join(', ')}`,
    );
  }

  const missingVariantIds = requestedVariantIds.filter((id) => !allVariants.some((variant) => variant.id === id));
  if (missingVariantIds.length > 0) {
    console.warn(
      `[render-community-archetype-images-openai] ${domainDef.key}: ignoring unknown variants: ${missingVariantIds.join(', ')}`,
    );
  }

  const archetypes = Array.isArray(config?.archetypes) ? config.archetypes : [];
  const domainTemplate = visualSystem?.domainPromptTemplates?.[domainDef.promptTemplateKey];

  const fallbackOutput = visualSystem?.output || { width: 1200, height: 900, aspectRatio: '4:3' };
  const categories = Array.isArray(config?.categories) ? config.categories : [];
  const categoryLabelLookup = new Map(
    categories
      .filter((item) => item && typeof item === 'object')
      .map((item) => [item.id, item.label]),
  );
  const requestedOutput = parseOutputSize(args.size, fallbackOutput);

  ensureDir(domainDef.outputDir);
  ensureDir(path.join(domainDef.outputDir, 'prompts'));
  ensureDir(path.join(domainDef.outputDir, 'metadata'));

  const domainManifest = {
    schemaVersion: METADATA_SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    domain: domainDef.key,
    provider: args.dryRun ? 'dry-run' : 'openai',
    model: args.model,
    quality: args.quality,
    size: args.size,
    requestedOutput,
    output: fallbackOutput,
    categories,
    archetypes: [],
  };

  summary.domains += 1;

  let processed = 0;
  for (const archetype of archetypes) {
    if (args.onlyArchetype && archetype.id !== args.onlyArchetype) continue;
    if (typeof args.limit === 'number' && processed >= args.limit) break;
    processed += 1;
    summary.archetypes += 1;

    const archetypeDir = path.join(domainDef.outputDir, archetype.id);
    const promptDir = path.join(domainDef.outputDir, 'prompts', archetype.id);
    const metadataDir = path.join(domainDef.outputDir, 'metadata', archetype.id);
    ensureDir(archetypeDir);
    ensureDir(promptDir);
    ensureDir(metadataDir);

    const imageEntries = [];

    for (const variant of variants) {
      summary.variants += 1;

      const bundle = buildPromptBundle({
        visualSystem,
        domainTemplate,
        archetype,
        variant,
        domainDef,
      });

      const pngFilename = `${variant.id}.png`;
      const svgFilename = `${variant.id}.svg`;
      const pngPath = path.join(archetypeDir, pngFilename);
      const svgPath = path.join(archetypeDir, svgFilename);
      const promptPath = path.join(promptDir, `${variant.id}.json`);
      const metadataPath = path.join(metadataDir, `${variant.id}.json`);

      const pngWebPath = `${domainDef.webPrefix}/${archetype.id}/${pngFilename}`;
      const svgWebPath = `${domainDef.webPrefix}/${archetype.id}/${svgFilename}`;
      const promptWebPath = `${domainDef.webPrefix}/prompts/${archetype.id}/${variant.id}.json`;
      const metadataWebPath = `${domainDef.webPrefix}/metadata/${archetype.id}/${variant.id}.json`;

      const generationTags = normalizeStringArray(archetype.generationTags);
      const styleProfile = safeObject(archetype.styleProfile);
      const categoryLabel = categoryLabelLookup.get(archetype.aestheticCategory);

      const imageRefs = {
        svg: svgWebPath,
        png: pngWebPath,
        prompt: promptWebPath,
        metadata: metadataWebPath,
      };

      const generationStyleInput = buildGenerationStyleInput({
        domainDef,
        archetype,
        variant,
        bundle,
        categoryLabel,
        generationTags,
        styleProfile,
        imageRefs,
      });

      const modelConversionHints = inferModelConversionHints({
        domainDef,
        archetype,
        variant,
        generationTags,
        styleProfile,
        imageRefs,
      });

      modelConversionHints.reuseSignature.aesthetic_category_label = categoryLabel || null;

      const promptPayload = {
        schemaVersion: METADATA_SCHEMA_VERSION,
        generatedAt: new Date().toISOString(),
        domain: domainDef.key,
        assetCategory: inferAssetCategory(domainDef.key),
        archetypeId: archetype.id,
        archetypeTitle: archetype.title,
        variantId: variant.id,
        variantTitle: bundle.variantTitle,
        variantLighting: bundle.variantLighting,
        prompt: bundle.prompt,
        positive: bundle.positive,
        negative: bundle.negative,
        output: requestedOutput,
        styleProfile,
        generationTags,
        generationStyleInput,
        modelConversionHints,
        imageRefs,
      };
      writeJson(promptPath, promptPayload);

      writeJson(metadataPath, {
        schemaVersion: METADATA_SCHEMA_VERSION,
        generatedAt: new Date().toISOString(),
        domain: domainDef.key,
        archetype: {
          id: archetype.id,
          title: archetype.title,
          aestheticCategoryId: archetype.aestheticCategory,
          aestheticCategoryLabel: categoryLabel,
          buildingSubcategory: archetype.buildingSubcategory,
          spaceType: archetype.spaceType,
          transportModes: archetype.transportModes,
          volume: archetype.volume,
        },
        variant: {
          id: variant.id,
          title: bundle.variantTitle,
          lighting: bundle.variantLighting,
        },
        output: requestedOutput,
        imageRefs,
        generationTags,
        styleProfile,
        generationStyleInput,
        modelConversionHints,
      });

      let status = 'dry_run';
      let failure = null;

      if (!args.dryRun) {
        if (!apiKey) {
          throw new Error('OPENAI_API_KEY is required unless --dry-run is used');
        }

        const exists = fs.existsSync(pngPath);
        if (exists && !args.overwrite) {
          summary.skipped += 1;
          status = 'skipped_existing';
        } else {
          let imageBuffer = null;
          let attempt = 0;
          const maxAttempts = 3;
          while (attempt < maxAttempts && !imageBuffer) {
            attempt += 1;
            try {
              imageBuffer = await fetchImageFromOpenAI({
                apiKey,
                model: args.model,
                quality: args.quality,
                size: args.size,
                prompt: bundle.prompt,
              });
            } catch (err) {
              if (attempt >= maxAttempts) {
                throw err;
              }
              await sleep(1000 * attempt);
            }
          }

          if (imageBuffer) {
            fs.writeFileSync(pngPath, imageBuffer);
            const svgWrapper = buildSvgWrapper({
              width: Number(requestedOutput.width) || 1200,
              height: Number(requestedOutput.height) || 900,
              pngFilename,
              alt: `${archetype.title} ${bundle.variantTitle}`,
              metadata: {
                schemaVersion: METADATA_SCHEMA_VERSION,
                domain: domainDef.key,
                archetypeId: archetype.id,
                variantId: variant.id,
                promptPath: promptWebPath,
                metadataPath: metadataWebPath,
                generationStyleInput: {
                  domain: generationStyleInput.domain,
                  archetypeId: generationStyleInput.archetypeId,
                  archetypeImageId: generationStyleInput.archetypeImageId,
                  aestheticCategoryId: generationStyleInput.aestheticCategoryId,
                  subtype: generationStyleInput.subtype,
                  generationTags: generationStyleInput.generationTags,
                },
                reuseSignature: modelConversionHints.reuseSignature,
              },
            });
            fs.writeFileSync(svgPath, svgWrapper, 'utf8');
            summary.generated += 1;
            status = 'generated';
            if (args.delayMs > 0) {
              await sleep(args.delayMs);
            }
          }
        }
      }

      imageEntries.push({
        id: `${archetype.id}_${variant.id}`,
        title: bundle.variantTitle,
        lighting: bundle.variantLighting,
        imagePath: svgWebPath,
        rasterPath: pngWebPath,
        promptPath: promptWebPath,
        metadataPath: metadataWebPath,
        generationStyleInput: {
          domain: generationStyleInput.domain,
          archetypeId: generationStyleInput.archetypeId,
          archetypeImageId: generationStyleInput.archetypeImageId,
          aestheticCategoryId: generationStyleInput.aestheticCategoryId,
          subtype: generationStyleInput.subtype,
          generationTags: generationStyleInput.generationTags,
        },
        modelConversionProfile: modelConversionHints.profileId,
        status,
        error: failure,
      });
    }

    domainManifest.archetypes.push({
      id: archetype.id,
      title: archetype.title,
      aestheticCategory: archetype.aestheticCategory,
      aestheticCategoryLabel: categoryLabelLookup.get(archetype.aestheticCategory),
      description: archetype.description,
      buildingSubcategory: archetype.buildingSubcategory,
      spaceType: archetype.spaceType,
      transportModes: archetype.transportModes,
      volume: archetype.volume,
      generationTags: normalizeStringArray(archetype.generationTags),
      styleProfile: safeObject(archetype.styleProfile),
      conversionSubtype: normalizeSubtype(domainDef.key, archetype),
      images: imageEntries,
    });
  }

  writeJson(path.join(domainDef.outputDir, 'manifest.json'), domainManifest);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const visualSystem = readJson(visualSystemPath);
  const apiKey = process.env.OPENAI_API_KEY;

  if (!args.dryRun && !apiKey) {
    console.error('[render-community-archetype-images-openai] Missing OPENAI_API_KEY. Use --dry-run to only emit prompt manifests.');
    process.exit(1);
  }

  const requestedDomains = args.domains.map((domain) => domain.trim()).filter(Boolean);
  const selected = requestedDomains.map((domain) => {
    const def = domainDefs[domain];
    if (!def) {
      throw new Error(`Unknown domain '${domain}'. Expected one of: ${Object.keys(domainDefs).join(', ')}`);
    }
    return def;
  });

  const summary = domainSummaryInit();

  for (const domainDef of selected) {
    try {
      await processDomain({ domainDef, visualSystem, args, apiKey, summary });
      console.log(`[render-community-archetype-images-openai] processed ${domainDef.key}`);
    } catch (err) {
      summary.failures += 1;
      console.error(`[render-community-archetype-images-openai] failed ${domainDef.key}:`, err instanceof Error ? err.message : err);
      if (!args.dryRun) {
        throw err;
      }
    }
  }

  console.log(
    `[render-community-archetype-images-openai] domains=${summary.domains} archetypes=${summary.archetypes} variants=${summary.variants} generated=${summary.generated} skipped=${summary.skipped} failures=${summary.failures}`,
  );
}

main().catch((err) => {
  console.error('[render-community-archetype-images-openai] fatal:', err instanceof Error ? err.message : err);
  process.exit(1);
});
