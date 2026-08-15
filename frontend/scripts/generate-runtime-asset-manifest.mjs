import { createHash } from 'node:crypto';
import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { dirname, extname, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const frontendRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const publicRoot = resolve(frontendRoot, 'public');
const sourceRoot = resolve(frontendRoot, 'src');
const outputPath = resolve(sourceRoot, 'data/runtimeAssetManifest.json');
const checkOnly = process.argv.includes('--check');
const requireHydrated = process.argv.includes('--require-hydrated');

const runtimePrefixes = Object.freeze([
  '/archetypes/',
  '/assets/',
  '/entourage/',
  '/families/',
  '/images/',
  '/park-kits/',
  '/park-skins/',
]);
const sourceExtensions = new Set(['.html', '.js', '.json', '.ts', '.tsx']);
const lfsPointerPattern = /^version https:\/\/git-lfs\.github\.com\/spec\/v1\noid sha256:([a-f0-9]{64})\nsize (\d+)\n?$/;
const catalogPaths = new Set([
  resolve(sourceRoot, 'data/buildingArchetypes.json'),
  resolve(sourceRoot, 'data/legoFamilySignatures.json'),
  resolve(sourceRoot, 'data/openSpaceArchetypes.json'),
  resolve(sourceRoot, 'data/streetPathArchetypes.json'),
]);

function webPath(filePath) {
  return `/${relative(publicRoot, filePath).split(sep).join('/')}`;
}

function sourcePath(filePath) {
  return relative(frontendRoot, filePath).split(sep).join('/');
}

function walkFiles(root, filter = () => true) {
  if (!existsSync(root)) return [];
  const files = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const path = resolve(root, entry.name);
    if (entry.isDirectory()) files.push(...walkFiles(path, filter));
    else if (entry.isFile() && filter(path)) files.push(path);
  }
  return files.sort();
}

function assetMetadata(filePath) {
  const stat = statSync(filePath);
  if (stat.size <= 256) {
    const pointer = lfsPointerPattern.exec(readFileSync(filePath, 'utf8'));
    if (pointer) {
      return { logicalBytes: Number(pointer[2]), lfsOid: pointer[1], hydrated: false };
    }
  }
  return { logicalBytes: stat.size, lfsOid: null, hydrated: true };
}

function digestRows(rows) {
  const hash = createHash('sha256');
  for (const row of rows) hash.update(`${row.path}\0${row.logicalBytes}\0${row.lfsOid ?? ''}\n`);
  return hash.digest('hex');
}

function resolveSourceImport(specifier, importerPath) {
  if (!specifier.startsWith('.') && !specifier.startsWith('@/')) return null;
  const base = specifier.startsWith('@/')
    ? resolve(sourceRoot, specifier.slice(2))
    : resolve(dirname(importerPath), specifier);
  const candidates = [
    base,
    ...['.ts', '.tsx', '.js', '.json'].map((extension) => `${base}${extension}`),
    ...['.ts', '.tsx', '.js', '.json'].map((extension) => resolve(base, `index${extension}`)),
  ];
  return candidates.find((candidate) => (
    existsSync(candidate) && statSync(candidate).isFile() && candidate !== outputPath
  )) ?? null;
}

function reachableSourceFiles(entryPath) {
  const visited = new Set();
  const pending = [entryPath];
  while (pending.length > 0) {
    const filePath = pending.pop();
    if (!filePath || visited.has(filePath)) continue;
    visited.add(filePath);
    if (!sourceExtensions.has(extname(filePath)) || extname(filePath) === '.json') continue;
    const text = readFileSync(filePath, 'utf8');
    const specifiers = [
      ...text.matchAll(/\bfrom\s+['"]([^'"]+)['"]/g),
      ...text.matchAll(/\bimport\s*(?:\(\s*)?['"]([^'"]+)['"]/g),
    ].map((match) => match[1]);
    for (const specifier of specifiers) {
      const dependency = resolveSourceImport(specifier, filePath);
      if (dependency && !visited.has(dependency)) pending.push(dependency);
    }
  }
  return [...visited].sort();
}

const sourceFiles = [
  ...reachableSourceFiles(resolve(sourceRoot, 'main.tsx')),
  resolve(frontendRoot, 'index.html'),
  resolve(publicRoot, 'manifest.json'),
  resolve(publicRoot, 'sw.js'),
].filter(existsSync);

const references = new Map();
const urlPattern = /\/(?:archetypes|assets|entourage|families|images|park-kits|park-skins)\/[^\s"'`<>)\]}]+/g;
for (const filePath of sourceFiles) {
  if (catalogPaths.has(filePath)) continue;
  const text = readFileSync(filePath, 'utf8');
  for (const rawMatch of text.matchAll(urlPattern)) {
    if (rawMatch.index > 0 && text[rawMatch.index - 1] === '@') continue;
    const url = rawMatch[0].replace(/[.,;:]+$/, '').split(/[?#]/, 1)[0];
    if (url.includes('${')) continue;
    const sources = references.get(url) ?? new Set();
    sources.add(sourcePath(filePath));
    references.set(url, sources);
  }
}

const availability = JSON.parse(readFileSync(resolve(sourceRoot, 'data/archetypeReferenceAvailability.json'), 'utf8'));
const catalogDomains = [
  ['buildingArchetypes.json', 'buildingIds', 'building'],
  ['openSpaceArchetypes.json', 'openSpaceIds', 'openSpace'],
  ['streetPathArchetypes.json', 'streetIds', 'street'],
];
for (const [catalogName, idsKey, domain] of catalogDomains) {
  const catalogPath = resolve(sourceRoot, `data/${catalogName}`);
  const catalog = JSON.parse(readFileSync(catalogPath, 'utf8'));
  const availableIds = new Set(availability[idsKey] ?? []);
  for (const archetype of catalog.archetypes ?? []) {
    if (!availableIds.has(archetype.id)) continue;
    const availableUrls = availability.domains?.[domain]?.entries?.[archetype.id]?.availableUrls ?? [];
    for (const url of availableUrls) {
      const sources = references.get(url) ?? new Set();
      sources.add(sourcePath(catalogPath));
      references.set(url, sources);
    }
  }
}
const familySignaturesPath = resolve(sourceRoot, 'data/legoFamilySignatures.json');
const familySignatures = JSON.parse(readFileSync(familySignaturesPath, 'utf8'));
const availableFamilySignatureIds = new Set(availability.familySignatureIds ?? []);
for (const [id, signature] of Object.entries(familySignatures.families ?? {})) {
  if (!availableFamilySignatureIds.has(id) || !signature.elevationUrl) continue;
  const sources = references.get(signature.elevationUrl) ?? new Set();
  sources.add(sourcePath(familySignaturesPath));
  references.set(signature.elevationUrl, sources);
}

const missingReferences = [];
const directoryReferences = [];
const explicitReferences = [];
const claimedPaths = new Set();
let unhydratedRequiredCount = 0;

for (const [url, sources] of [...references].sort(([left], [right]) => left.localeCompare(right))) {
  const filePath = resolve(publicRoot, url.replace(/^\/+/, ''));
  if (!existsSync(filePath)) {
    missingReferences.push({ url, sources: [...sources].sort() });
    continue;
  }
  if (statSync(filePath).isDirectory()) {
    directoryReferences.push({ url, sources: [...sources].sort() });
    continue;
  }
  const metadata = assetMetadata(filePath);
  if (!metadata.hydrated) unhydratedRequiredCount += 1;
  claimedPaths.add(url);
  explicitReferences.push({
    url,
    sources: [...sources].sort(),
    logicalBytes: metadata.logicalBytes,
    ...(metadata.lfsOid ? { lfsOid: metadata.lfsOid } : {}),
  });
}

const activeFamilySlugs = [...new Set(Object.entries(familySignatures.families ?? {})
  .filter(([id]) => availableFamilySignatureIds.has(id))
  .map(([, entry]) => entry)
  .map((entry) => entry.elevationUrl?.match(/^\/families\/([^/]+)\//)?.[1])
  .filter(Boolean))].sort();

function summarizeCollection(name, roots, reason, include = () => true) {
  const rows = [];
  for (const root of roots) {
    const diskRoot = resolve(publicRoot, root.replace(/^\/+/, ''));
    for (const filePath of walkFiles(diskRoot).filter((path) => include(path, root))) {
      const metadata = assetMetadata(filePath);
      if (!metadata.hydrated) unhydratedRequiredCount += 1;
      const path = webPath(filePath);
      claimedPaths.add(path);
      rows.push({ path, logicalBytes: metadata.logicalBytes, lfsOid: metadata.lfsOid });
    }
  }
  rows.sort((left, right) => left.path.localeCompare(right.path));
  return {
    name,
    roots,
    reason,
    fileCount: rows.length,
    logicalBytes: rows.reduce((sum, row) => sum + row.logicalBytes, 0),
    pathDigest: digestRows(rows),
  };
}

const collections = [
  summarizeCollection(
    'lego-building-families',
    activeFamilySlugs.map((slug) => `/families/${slug}/`),
    'Selected by legoFamilySignatures.json; deployable manifests and GLB model parts are assembled by family and role at runtime.',
    (path, root) => {
      const filename = path.slice(resolve(publicRoot, root.replace(/^\/+/, '')).length + 1);
      return !filename.includes(sep)
        && (filename === 'elevation.jpg' || filename.endsWith('_manifest.json') || filename.endsWith('.glb'));
    },
  ),
  summarizeCollection(
    'public-realm-kits',
    ['/park-kits/'],
    'Kit filenames are selected from typed park recipes and composed into URLs at runtime.',
  ),
  summarizeCollection(
    'public-realm-skins',
    ['/park-skins/'],
    'Park skin roles and adaptive sizes are composed into URLs at runtime.',
  ),
];

const allRuntimeFiles = runtimePrefixes.flatMap((prefix) => (
  walkFiles(resolve(publicRoot, prefix.replace(/^\/+|\/+$/g, '')))
)).map(webPath).sort();
const unclassifiedPaths = allRuntimeFiles.filter((path) => !claimedPaths.has(path));
const allFamilyDirectories = readdirSync(resolve(publicRoot, 'families'), { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();

const manifest = {
  schema: 'cityprompt.runtime-assets@1',
  generatedBy: 'frontend/scripts/generate-runtime-asset-manifest.mjs',
  sourceInputs: sourceFiles.map(sourcePath).sort(),
  coverage: {
    explicitReferenceCount: explicitReferences.length,
    dynamicCollectionCount: collections.length,
    requiredFileCount: claimedPaths.size,
    requiredLogicalBytes: explicitReferences.reduce((sum, entry) => sum + entry.logicalBytes, 0)
      + collections.reduce((sum, entry) => sum + entry.logicalBytes, 0),
    missingReferenceCount: missingReferences.length,
  },
  explicitReferences,
  directoryReferences,
  dynamicCollections: collections,
  cleanupCandidates: {
    unclassifiedRuntimeFileCount: unclassifiedPaths.length,
    unclassifiedRuntimePathDigest: createHash('sha256').update(unclassifiedPaths.join('\n')).digest('hex'),
    unclassifiedRuntimePathSample: unclassifiedPaths.slice(0, 100),
    familyDirectoriesAbsentFromRuntimeSignatures: allFamilyDirectories
      .filter((slug) => !activeFamilySlugs.includes(slug)),
  },
};
const serialized = `${JSON.stringify(manifest, null, 2)}\n`;

if (missingReferences.length > 0) {
  console.error(`Runtime asset manifest found ${missingReferences.length} missing direct reference(s).`);
  for (const missing of missingReferences.slice(0, 25)) console.error(`- ${missing.url}`);
  process.exitCode = 1;
} else if (requireHydrated && unhydratedRequiredCount > 0) {
  console.error(`Runtime assets are not hydrated: ${unhydratedRequiredCount} required Git LFS pointer file(s) remain.`);
  process.exitCode = 1;
} else if (checkOnly) {
  if (!existsSync(outputPath) || readFileSync(outputPath, 'utf8') !== serialized) {
    console.error('Runtime asset manifest is stale. Run npm run generate:runtime-assets.');
    process.exitCode = 1;
  } else {
    console.log(`Verified ${claimedPaths.size} required runtime files; manifest is current.`);
  }
} else {
  writeFileSync(outputPath, serialized, 'utf8');
  console.log(`Recorded ${claimedPaths.size} required runtime files and ${unclassifiedPaths.length} cleanup candidates.`);
  if (unhydratedRequiredCount > 0) {
    console.warn(`${unhydratedRequiredCount} required files are Git LFS pointers in this checkout; run git lfs pull before release verification.`);
  }
}
