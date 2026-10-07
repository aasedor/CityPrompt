/** Package the frontend's authored facts for backend-only installations. */
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { createServer } from 'vite';
import { resolve } from 'node:path';
const read = relative => JSON.parse(readFileSync(new URL(relative, import.meta.url), 'utf8'));
const revisions = read('../src/data/savedModelRevisions.json');
const root = fileURLToPath(new URL('..',import.meta.url));
const server = await createServer({root,configFile:resolve(root,'vite.config.ts'),logLevel:'silent',mode:'test',
  cacheDir:resolve(root,'../artifacts/model-contract-vite-cache'),server:{middlewareMode:true},
  appType:'custom',optimizeDeps:{noDiscovery:true,entries:[]}});
let rows;
try {
  const { CATALOGUE_ASSETS } = await server.ssrLoadModule('/src/features/pickPlace/assetRegistry.ts');
  rows = CATALOGUE_ASSETS.filter(row => row.zoneType === 'building' && row.reshapeMode === 'fixed_native');
} finally {await server.close();}
const records = rows.map(row => ({asset_id:row.id,variant_id:row.model.variantId,revision:row.model.revision,
  dimensions_m:row.nativeDimensions,storeys:row.properties.floor_count ?? row.properties.floors,
  fixed:(row.storeyProgram?.mode ?? 'fixed_authored_assembly') === 'fixed_authored_assembly',current:true}));
records.push(...revisions.revisions.map(row => ({asset_id:row.assetId,variant_id:row.variantId,revision:row.revision,
  dimensions_m:row.nativeDimensions,storeys:row.storeys,fixed:true,current:false})));
const target = new URL('../../backend/app/data/native_model_contract.json', import.meta.url);
const content = JSON.stringify({schema:'cityprompt.native-model-contract@1',records},null,2)+'\n';
if(process.argv.includes('--write')) writeFileSync(target,content);
else if(readFileSync(target,'utf8').replace(/\r\n/g,'\n') !== content) throw new Error('Backend model contract is stale; run node scripts/check-model-contract.mjs --write');
console.log('Backend model contract matches authored catalogue: '+fileURLToPath(target));
