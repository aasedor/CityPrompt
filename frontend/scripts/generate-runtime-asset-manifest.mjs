import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { dirname, extname, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const frontendRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const repoRoot = resolve(frontendRoot, '..');
const publicRoot = resolve(process.env.CITYPROMPT_PUBLIC_DIR || resolve(frontendRoot, 'public'));
const sourceRoot = resolve(frontendRoot, 'src');
const outputPath = resolve(sourceRoot, 'data/runtimeAssetManifest.json');
const checkOnly = process.argv.includes('--check');
const requireHydrated = process.argv.includes('--require-hydrated');
const listRequiredLfsPaths = process.argv.includes('--list-required-lfs-paths');
// For sparse checkouts, inventory tracked metadata without downloading assets.
// --require-hydrated still fails on every absent file; this is never runtime proof.
const trackedMetadata = process.argv.includes('--tracked-metadata');

const runtimePrefixes = Object.freeze([
  '/archetypes/',
  '/assets/',
  '/entourage/',
  '/families/',
  '/images/',
  '/park-kits/',
  '/landscape-pilots/',
  '/park-skins/',
  '/street-kits/',
]);
const sourceExtensions = new Set(['.html', '.js', '.json', '.ts', '.tsx']);
// License text ships beside models; normalize it too for Windows/Linux parity.
const runtimeTextExtensions = new Set(['.js', '.json', '.svg', '.txt']);
const lfsPointerPattern = /^version https:\/\/git-lfs\.github\.com\/spec\/v1\noid sha256:([a-f0-9]{64})\nsize (\d+)\n?$/;
const catalogPaths = new Set([
  resolve(sourceRoot, 'data/buildingArchetypes.json'),
  resolve(sourceRoot, 'data/legoFamilySignatures.json'),
  resolve(sourceRoot, 'data/openSpaceArchetypes.json'),
  resolve(sourceRoot, 'data/streetPathArchetypes.json'),
]);

function compareText(left, right) {
  return left < right ? -1 : left > right ? 1 : 0;
}

function firstDifference(current, expected, path = '$') {
  if (Object.is(current, expected)) return null;
  if (typeof current !== typeof expected || current === null || expected === null) {
    return { path, current, expected };
  }
  if (Array.isArray(current) || Array.isArray(expected)) {
    if (!Array.isArray(current) || !Array.isArray(expected)) return { path, current, expected };
    if (current.length !== expected.length) {
      return { path: `${path}.length`, current: current.length, expected: expected.length };
    }
    for (let index = 0; index < current.length; index += 1) {
      const difference = firstDifference(current[index], expected[index], `${path}[${index}]`);
      if (difference) return difference;
    }
    return null;
  }
  if (typeof current === 'object') {
    const currentKeys = Object.keys(current);
    const expectedKeys = Object.keys(expected);
    const keyDifference = firstDifference(currentKeys, expectedKeys, `${path}.[keys]`);
    if (keyDifference) return keyDifference;
    for (const key of currentKeys) {
      const difference = firstDifference(current[key], expected[key], `${path}.${key}`);
      if (difference) return difference;
    }
    return null;
  }
  return { path, current, expected };
}

function loadLfsIndex() {
  try {
    const result = JSON.parse(execFileSync(
      'git',
      ['lfs', 'ls-files', '--json'],
      {
        cwd: repoRoot,
        encoding: 'utf8',
        maxBuffer: 64 * 1024 * 1024,
        stdio: ['ignore', 'pipe', 'ignore'],
      },
    ));
    return new Map((result.files ?? []).map((entry) => [
      entry.name.replace(/\\/g, '/'),
      { logicalBytes: Number(entry.size), lfsOid: entry.oid },
    ]));
  } catch {
    // Source archives and minimal developer environments may not provide
    // Git LFS. Pointer contents remain a valid fallback for unhydrated files.
    return new Map();
  }
}

const lfsIndex = loadLfsIndex();
const trackedFiles = new Map();
const trackedText = new Map();
if (trackedMetadata) {
  if (!lfsIndex.size) throw new Error('--tracked-metadata requires a usable Git LFS index.');
  const lines = execFileSync('git', ['ls-files', '--stage', '-z', 'frontend/public'], { cwd: repoRoot, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 }).split('\0').filter(Boolean);
  const records = lines.map(line => {
    const [header, path] = line.split('\t');
    return { oid: header.split(' ')[1], path, absolute: resolve(publicRoot, path.slice('frontend/public/'.length)) };
  });
  const sizes = execFileSync('git', ['cat-file', '--batch-check'], { cwd: repoRoot, encoding: 'utf8', input: records.map(row => row.oid).join('\n') + '\n', maxBuffer: 16 * 1024 * 1024 }).trim().split('\n');
  records.forEach((row, index) => trackedFiles.set(row.absolute, { ...row, bytes: Number(sizes[index].split(' ')[2]) }));
  const textRecords = records.filter(row => runtimeTextExtensions.has(extname(row.path)));
  const blobs = execFileSync('git', ['cat-file', '--batch'], { cwd: repoRoot, input: textRecords.map(row => row.oid).join('\n') + '\n', maxBuffer: 256 * 1024 * 1024 });
  let cursor = 0;
  for (const row of textRecords) {
    const end = blobs.indexOf(10, cursor);
    const size = Number(blobs.subarray(cursor, end).toString().split(' ')[2]);
    if (!Number.isFinite(size)) throw new Error(`Cannot read tracked text: ${row.path}`);
    trackedText.set(row.absolute, blobs.subarray(end + 1, end + 1 + size).toString('utf8'));
    cursor = end + 1 + size + 1;
  }
}

function assetExists(path) {
  return existsSync(path) || trackedFiles.has(path) || [...trackedFiles.keys()].some(file => file.startsWith(`${path}${sep}`));
}
function sourceText(path) {
  return existsSync(path) ? readFileSync(path, 'utf8') : trackedText.get(path);
}

function webPath(filePath) {
  return `/${relative(publicRoot, filePath).split(sep).join('/')}`;
}

function sourcePath(filePath) {
  const publicRelative = relative(publicRoot, filePath);
  if (!publicRelative.startsWith(`..${sep}`) && publicRelative !== '..' && !publicRelative.includes(':')) {
    return `public/${publicRelative.split(sep).join('/')}`;
  }
  return relative(frontendRoot, filePath).split(sep).join('/');
}

function walkFiles(root, filter = () => true, includeTracked = true) {
  if (trackedMetadata && includeTracked) {
    return [...new Set([...walkFiles(root, filter, false), ...[...trackedFiles.keys()].filter(path => path.startsWith(`${root}${sep}`) && filter(path))])].sort();
  }
  if (!existsSync(root)) return [];
  const files = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const path = resolve(root, entry.name);
    if (entry.isDirectory()) files.push(...walkFiles(path, filter, false));
    else if (entry.isFile() && filter(path)) files.push(path);
  }
  return files.sort();
}

function assetMetadata(filePath) {
  if (!existsSync(filePath) && trackedFiles.has(filePath)) {
    const tracked = trackedFiles.get(filePath);
    const lfs = lfsIndex.get(tracked.path);
    return lfs ? { ...lfs, hydrated: false } : {
      logicalBytes: trackedText.has(filePath) ? Buffer.byteLength(trackedText.get(filePath).replace(/\r\n?/g, '\n'), 'utf8') : tracked.bytes,
      lfsOid: null, hydrated: false,
    };
  }
  const stat = statSync(filePath);
  let pointer = null;
  if (stat.size <= 256) {
    pointer = lfsPointerPattern.exec(readFileSync(filePath, 'utf8'));
  }
  // Vite and this check may use the same external hydrated public directory.
  // Git identities remain repository-relative, independent of its disk location.
  const repoPath = `frontend/public/${relative(publicRoot, filePath).split(sep).join('/')}`;
  const trackedLfs = lfsIndex.get(repoPath);
  if (trackedLfs) {
    return { ...trackedLfs, hydrated: !pointer };
  }
  if (pointer) {
    return { logicalBytes: Number(pointer[2]), lfsOid: pointer[1], hydrated: false };
  }
  const logicalBytes = runtimeTextExtensions.has(extname(filePath).toLowerCase())
    ? Buffer.byteLength(readFileSync(filePath, 'utf8').replace(/\r\n?/g, '\n'), 'utf8')
    : stat.size;
  return { logicalBytes, lfsOid: null, hydrated: true };
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
].filter(assetExists);

const references = new Map();
// The classroom roster also contains dynamically addressed modules. Keep its
// explicit dependency closure even if a renderer no longer spells out a URL.
const starterPath = resolve(sourceRoot, 'data/classroomStarter.json');
const starter = JSON.parse(readFileSync(starterPath, 'utf8'));
for (const dependency of starter.dependencies) {
  if (dependency.location === 'public') references.set(`/${dependency.path}`, new Set([sourcePath(starterPath)]));
}
const urlPattern = /\/(?:archetypes|assets|entourage|families|images|park-kits|park-skins|landscape-pilots|street-kits)\/[^\s"'`<>)\]}]+/g;
for (const filePath of sourceFiles) {
  if (catalogPaths.has(filePath)) continue;
  const text = sourceText(filePath);
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

for (const [url, sources] of [...references].sort(([left], [right]) => compareText(left, right))) {
  const filePath = resolve(publicRoot, url.replace(/^\/+/, ''));
  if (!assetExists(filePath)) {
    missingReferences.push({ url, sources: [...sources].sort() });
    continue;
  }
  if (existsSync(filePath) ? statSync(filePath).isDirectory() : !trackedFiles.has(filePath)) {
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
  rows.sort((left, right) => compareText(left.path, right.path));
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
  summarizeCollection(
    'neighbourhood-park-pilot',
    ['/landscape-pilots/neighborhood-rustic-v5/'],
    'Reviewed park components selected by the adaptive neighbourhood park renderer.',
  ),
  summarizeCollection(
    'park-trio',
    ['/landscape-pilots/park-trio-v3/'],
    'Published cinema, teaching garden and concert lawn modules selected by the adaptive park renderer.',
    (path) => path.endsWith('.glb'),
  ),
  summarizeCollection(
    'native-street-modules',
    ['/street-kits/pilots/'],
    'Versioned native street modules and locked references; module URLs are resolved from the delivery manifest.',
  ),
  summarizeCollection(
    'sports-park-modules',
    ['/landscape-pilots/sports-parks-v1/'],
    'Sports equipment including the classroom basketball court is selected dynamically by park programme.',
    (path) => path.endsWith('.glb'),
  ),
];

const allRuntimeFiles = runtimePrefixes.flatMap((prefix) => (
  walkFiles(resolve(publicRoot, prefix.replace(/^\/+|\/+$/g, '')))
)).map(webPath).sort();
const unclassifiedPaths = allRuntimeFiles.filter((path) => !claimedPaths.has(path));
const allFamilyDirectories = [...new Set(walkFiles(resolve(publicRoot, 'families'))
  .map(path => relative(resolve(publicRoot, 'families'), path).split(sep)[0]))].sort();

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
} else if (listRequiredLfsPaths) {
  for (const path of [...claimedPaths].sort()) {
    const filePath = resolve(publicRoot, path.replace(/^\/+/, ''));
    if (assetMetadata(filePath).lfsOid) {
      console.log(`frontend/public/${relative(publicRoot, filePath).split(sep).join('/')}`);
    }
  }
} else if (requireHydrated && unhydratedRequiredCount > 0) {
  console.error(`Runtime assets are not hydrated: ${unhydratedRequiredCount} required file(s) are missing or remain Git LFS pointers.`);
  process.exitCode = 1;
} else if (checkOnly) {
  const currentManifest = existsSync(outputPath)
    ? readFileSync(outputPath, 'utf8').replace(/\r\n?/g, '\n')
    : null;
  if (currentManifest !== serialized) {
    console.error('Runtime asset manifest is stale. Run npm run generate:runtime-assets.');
    if (currentManifest) {
      try {
        const difference = firstDifference(JSON.parse(currentManifest), manifest);
        if (difference) {
          console.error(`First difference: ${difference.path}`);
          console.error(`- recorded: ${JSON.stringify(difference.current)}`);
          console.error(`- generated: ${JSON.stringify(difference.expected)}`);
        }
      } catch {
        console.error('The recorded runtime asset manifest is not valid JSON.');
      }
    }
    process.exitCode = 1;
  } else {
    console.log(`Verified ${claimedPaths.size} required runtime file records; manifest is current.${trackedMetadata ? ' Tracked metadata only; run --require-hydrated on the release package.' : ''}`);
  }
} else {
  writeFileSync(outputPath, serialized, 'utf8');
  console.log(`Recorded ${claimedPaths.size} required runtime files and ${unclassifiedPaths.length} cleanup candidates.`);
  if (unhydratedRequiredCount > 0) {
    console.warn(`${unhydratedRequiredCount} required files are missing or Git LFS pointers in this checkout; hydrate the release package before release verification.`);
  }
}
