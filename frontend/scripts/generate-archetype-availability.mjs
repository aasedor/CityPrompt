import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const frontendRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const publicRoot = resolve(frontendRoot, 'public');

const domains = Object.freeze({
  building: {
    catalog: 'buildingArchetypes.json',
    root: '/archetypes/buildings/',
    idsKey: 'buildingIds',
  },
  openSpace: {
    catalog: 'openSpaceArchetypes.json',
    root: '/archetypes/openspaces/',
    idsKey: 'openSpaceIds',
  },
  street: {
    catalog: 'streetPathArchetypes.json',
    root: '/archetypes/streets/',
    idsKey: 'streetIds',
  },
});

const transportStandardsText = readFileSync(resolve(frontendRoot, 'src/data/transportStandards.ts'), 'utf8');
const streetSectionById = new Map(
  [...transportStandardsText.matchAll(/"archetypeId":\s*"([^"]+)"[\s\S]*?"sectionSvgUrl":\s*"([^"]+)"/g)]
    .map((match) => [match[1], match[2]]),
);

function assetExists(url) {
  return existsSync(resolve(publicRoot, url.replace(/^\/+/, '')));
}

function classifyDomain(domain, { catalog: catalogName, root }) {
  const catalog = JSON.parse(readFileSync(resolve(frontendRoot, `src/data/${catalogName}`), 'utf8'));
  const availableIds = [];
  const completeIds = [];
  const incomplete = [];
  const entries = {};

  for (const archetype of catalog.archetypes ?? []) {
    const references = [
      archetype.thumbnailUrl,
      ...(archetype.variants ?? []).map((variant) => variant.thumbnailUrl),
    ].filter(Boolean);
    const nonAuthoritative = references.filter((url) => !url.startsWith(root));
    const missing = references.filter((url) => url.startsWith(root) && !assetExists(url));
    const candidateUrls = [...references];
    if (domain === 'street') {
      candidateUrls.push(...references.map((url) => url.replace(/\.[a-z0-9]+$/i, '.webp')));
      const sectionUrl = streetSectionById.get(archetype.id);
      if (sectionUrl) candidateUrls.push(sectionUrl);
    }
    const availableUrls = [...new Set(candidateUrls.filter((url) => (
      url.startsWith(root) && assetExists(url)
    )))].sort();
    const isAvailable = availableUrls.length > 0;
    const isComplete = references.length > 0 && nonAuthoritative.length === 0 && missing.length === 0;
    entries[archetype.id] = { availableUrls };
    if (isAvailable) availableIds.push(archetype.id);
    if (isComplete) completeIds.push(archetype.id);
    if (!isComplete) {
      incomplete.push({
        id: archetype.id,
        availability: isAvailable ? 'partial' : 'unavailable',
        status: references.length === 0
          ? 'no_reference_assets'
          : nonAuthoritative.length > 0
            ? 'non_authoritative_reference_root'
            : 'missing_reference_assets',
        referenceCount: references.length,
        missingCount: missing.length,
      });
    }
  }

  return {
    authoritativeRoot: root,
    availableIds: availableIds.sort(),
    completeIds: completeIds.sort(),
    incomplete: incomplete.sort((left, right) => left.id.localeCompare(right.id)),
    entries,
  };
}

const classifications = Object.fromEntries(
  Object.entries(domains).map(([domain, config]) => [domain, classifyDomain(domain, config)]),
);
const familySignatures = JSON.parse(readFileSync(
  resolve(frontendRoot, 'src/data/legoFamilySignatures.json'),
  'utf8',
));
const familySignatureIds = [];
const incompleteFamilySignatures = [];
for (const [id, signature] of Object.entries(familySignatures.families ?? {})) {
  const elevationUrl = signature.elevationUrl;
  if (
    typeof elevationUrl === 'string'
    && elevationUrl.startsWith('/families/')
    && existsSync(resolve(publicRoot, elevationUrl.replace(/^\/+/, '')))
  ) {
    familySignatureIds.push(id);
  } else {
    incompleteFamilySignatures.push({
      id,
      status: elevationUrl ? 'missing_reference_assets' : 'no_reference_assets',
    });
  }
}
familySignatureIds.sort();
incompleteFamilySignatures.sort((left, right) => left.id.localeCompare(right.id));

const output = {
  schema: 'cityprompt.archetype-reference-availability@2',
  domains: Object.fromEntries(Object.entries(classifications).map(([domain, classification]) => [domain, {
    authoritativeRoot: classification.authoritativeRoot,
    availableCount: classification.availableIds.length,
    completeCount: classification.completeIds.length,
    incompleteCount: classification.incomplete.length,
    incomplete: classification.incomplete,
    entries: classification.entries,
  }])),
  ...Object.fromEntries(Object.entries(domains).map(([domain, config]) => (
    [config.idsKey, classifications[domain].availableIds]
  ))),
  ...Object.fromEntries(Object.entries(domains).map(([domain, config]) => (
    [`complete${config.idsKey.charAt(0).toUpperCase()}${config.idsKey.slice(1)}`, classifications[domain].completeIds]
  ))),
  familySignatures: {
    availableCount: familySignatureIds.length,
    incompleteCount: incompleteFamilySignatures.length,
    incomplete: incompleteFamilySignatures,
  },
  familySignatureIds,
};
const outputPath = resolve(frontendRoot, 'src/data/archetypeReferenceAvailability.json');
writeFileSync(outputPath, `${JSON.stringify(output, null, 2)}\n`, 'utf8');

for (const [domain, classification] of Object.entries(classifications)) {
  console.log(`${domain}: ${classification.availableIds.length} usable, ${classification.completeIds.length} complete, ${classification.incomplete.length} incomplete.`);
}
console.log(`family signatures: ${familySignatureIds.length} complete, ${incompleteFamilySignatures.length} incomplete.`);
