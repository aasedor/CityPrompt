import { existsSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const frontendRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const repositoryRoot = resolve(frontendRoot, '..');
const publicRoot = resolve(frontendRoot, 'public');
const buildingCatalog = JSON.parse(readFileSync(
  resolve(frontendRoot, 'src/data/buildingArchetypes.json'),
  'utf8',
));
const openSpaceCatalog = JSON.parse(readFileSync(
  resolve(frontendRoot, 'src/data/openSpaceArchetypes.json'),
  'utf8',
));
const stickerBatch = JSON.parse(readFileSync(
  resolve(repositoryRoot, 'tools/archetype_compiler/sticker_method_batch_01.json'),
  'utf8',
));
const pilotManifest = JSON.parse(readFileSync(
  resolve(frontendRoot, 'src/data/stickerMethodPilots.json'),
  'utf8',
));
const referenceAvailability = JSON.parse(readFileSync(
  resolve(frontendRoot, 'src/data/archetypeReferenceAvailability.json'),
  'utf8',
));

const authoritativeRoots = Object.freeze({
  building: '/archetypes/buildings/',
  park: '/archetypes/openspaces/',
});
const missing = [];
const checked = new Set();

function buildingReferenceSetIsComplete(archetype) {
  const references = [
    archetype.thumbnailUrl,
    ...(archetype.variants ?? []).map((variant) => variant.thumbnailUrl),
  ].filter(Boolean);
  return references.length > 0 && references.every((url) => (
    url.startsWith(authoritativeRoots.building)
    && existsSync(resolve(publicRoot, url.replace(/^\/+/, '')))
  ));
}

function checkReference(archetypeId, kind, url) {
  if (!url) {
    missing.push(`${kind}:${archetypeId}: missing URL`);
    return;
  }
  if (!url.startsWith(authoritativeRoots[kind])) {
    missing.push(`${kind}:${archetypeId}: non-authoritative root ${url}`);
    return;
  }
  checked.add(url);
  const assetPath = resolve(publicRoot, url.replace(/^\/+/, ''));
  if (!existsSync(assetPath)) missing.push(`${kind}:${archetypeId}: ${url}`);
}

function checkArchetype(catalog, archetypeId, kind) {
  const archetype = (catalog.archetypes ?? []).find((entry) => entry.id === archetypeId);
  if (!archetype) {
    missing.push(`${kind}:${archetypeId}: missing catalogue entry`);
    return;
  }
  checkReference(archetypeId, kind, archetype.thumbnailUrl);
  for (const variant of archetype.variants ?? []) {
    checkReference(`${archetypeId}/${variant.id}`, kind, variant.thumbnailUrl);
  }
}

const approvedBuildings = stickerBatch.buildings ?? [];
const manifestBuildings = pilotManifest.buildings ?? [];
const expectedAvailableBuildingIds = (buildingCatalog.archetypes ?? [])
  .filter(buildingReferenceSetIsComplete)
  .map((archetype) => archetype.id)
  .sort();
if (JSON.stringify(referenceAvailability.completeBuildingIds) !== JSON.stringify(expectedAvailableBuildingIds)) {
  missing.push('reference availability manifest is stale or differs from the complete authored asset sets on disk');
}
if (JSON.stringify(manifestBuildings) !== JSON.stringify(approvedBuildings.map((building) => ({
  archetypeId: building.archetype_id,
  variantId: building.variant_id,
})))) {
  missing.push('pilot manifest building order/identity differs from the approved Sticker Method batch');
}

for (const building of approvedBuildings) {
  if (building.status !== 'approved_95_plus') {
    missing.push(`building:${building.archetype_id}: not approved_95_plus`);
    continue;
  }
  checkArchetype(buildingCatalog, building.archetype_id, 'building');
  if (!referenceAvailability.buildingIds?.includes(building.archetype_id)) {
    missing.push(`building:${building.archetype_id}: absent from reference availability manifest`);
  }
}
checkArchetype(openSpaceCatalog, 'neighborhood_park', 'park');
if (
  pilotManifest.parks?.length !== 1
  || pilotManifest.parks[0]?.archetypeId !== 'neighborhood_park'
  || pilotManifest.parks[0]?.variantId !== 'neighborhood_park_v0'
) {
  missing.push('pilot manifest must bind neighborhood_park/neighborhood_park_v0');
}

if (missing.length > 0) {
  console.error(`Sticker Method pilot asset gate failed with ${missing.length} issue(s):`);
  for (const entry of missing) console.error(`- ${entry}`);
  process.exitCode = 1;
} else {
  console.log(`Verified ${checked.size} Sticker Method pilot catalogue references (10 buildings + neighborhood park).`);
}
