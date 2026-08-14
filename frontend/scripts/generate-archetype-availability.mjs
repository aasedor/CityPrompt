import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const frontendRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const publicRoot = resolve(frontendRoot, 'public');
const catalog = JSON.parse(readFileSync(
  resolve(frontendRoot, 'src/data/buildingArchetypes.json'),
  'utf8',
));

const buildingIds = (catalog.archetypes ?? [])
  .filter((archetype) => {
    const references = [
      archetype.thumbnailUrl,
      ...(archetype.variants ?? []).map((variant) => variant.thumbnailUrl),
    ].filter(Boolean);
    return references.length > 0 && references.every((url) => (
      url.startsWith('/archetypes/buildings/')
      && existsSync(resolve(publicRoot, url.replace(/^\/+/, '')))
    ));
  })
  .map((archetype) => archetype.id)
  .sort();

const output = {
  schema: 'cityprompt.archetype-reference-availability@1',
  authoritativeRoot: '/archetypes/buildings/',
  buildingIds,
};
const outputPath = resolve(frontendRoot, 'src/data/archetypeReferenceAvailability.json');
writeFileSync(outputPath, `${JSON.stringify(output, null, 2)}\n`, 'utf8');
console.log(`Recorded ${buildingIds.length} building archetypes with complete authored reference sets.`);
