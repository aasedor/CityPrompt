/** Package the frontend's authored facts for backend-only installations. */
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { createServer } from 'vite';
import { resolve } from 'node:path';
const read = relative => JSON.parse(readFileSync(new URL(relative, import.meta.url), 'utf8'));
const revisions = read('../src/data/savedModelRevisions.json');
const root = fileURLToPath(new URL('..',import.meta.url));
const server = await createServer({root,configFile:resolve(root,'vite.config.ts'),logLevel:'silent',mode:'test',
  // Backend supports every authored selection, including opt-in trial cards.
  // This is a geometry contract, not frontend activation or publication approval.
  define:{'import.meta.env.DEV':'false','import.meta.env.PROD':'true','import.meta.env.VITE_CLAUDE_FIVE_TRIAL':JSON.stringify('true')},
  cacheDir:resolve(root,'../artifacts/model-contract-vite-cache'),server:{middlewareMode:true},
  appType:'custom',optimizeDeps:{noDiscovery:true,entries:[]}});
let records;
try {
  const { CATALOGUE_ASSETS } = await server.ssrLoadModule('/src/features/pickPlace/assetRegistry.ts');
  const { CATALOGUE_BUILDING_ASSETS } = await server.ssrLoadModule('/src/features/pickPlace/publishedBuildingAssets.ts');
  const { withBuildingOnlyFootprint } = await server.ssrLoadModule('/src/features/pickPlace/buildingOnlyFootprint.ts');
  const { validationNativeBuildingBinding } = await server.ssrLoadModule('/src/features/pickPlace/validationNativeBuildingBinding.ts');
  // Saved local trials need exact report facts without becoming production picker choices.
  // Prefer registered programmes for published assets; add only missing authored identities.
  const authored = CATALOGUE_BUILDING_ASSETS.filter(row => !CATALOGUE_ASSETS.some(asset => asset.id === row.id))
    .map(withBuildingOnlyFootprint);
  records = [...CATALOGUE_ASSETS, ...authored]
    .filter(row => row.zoneType === 'building' && row.reshapeMode === 'fixed_native')
    .map(row => {
      const binding = validationNativeBuildingBinding(row.id, row.model.revision);
      return {
        asset_id: row.id, variant_id: row.model.variantId, revision: row.model.revision,
        dimensions_m: row.nativeDimensions, storeys: row.properties.floor_count ?? row.properties.floors,
        fixed: (row.storeyProgram?.mode ?? 'fixed_authored_assembly') === 'fixed_authored_assembly', current: true,
        ...(binding?.model_revision && binding.standalone_native ? { static_model_sha256: binding.sha256 } : {}),
      };
    });
} finally {await server.close();}
records.push(...revisions.revisions.map(row => ({asset_id:row.assetId,variant_id:row.variantId,revision:row.revision,
  dimensions_m:row.nativeDimensions,storeys:row.storeys,fixed:true,current:false})));
const target = new URL('../../backend/app/data/native_model_contract.json', import.meta.url);
const content = JSON.stringify({schema:'cityprompt.native-model-contract@1',records},null,2)+'\n';
if(process.argv.includes('--write')) writeFileSync(target,content);
else if(readFileSync(target,'utf8').replace(/\r\n/g,'\n') !== content) throw new Error('Backend model contract is stale; run node scripts/check-model-contract.mjs --write');
console.log('Backend model contract matches authored catalogue: '+fileURLToPath(target));

const quantities = read('../src/data/catalogueBuildingQuantities.json');
const quantityIdentities = new Set();
const areaMethods = new Set(['storey_sections', 'typical_plate', 'source_programme']);
const authoredQuantities = [];
for (const { estimated_gross_floor_area_m2, estimated_dwellings_range, area_method, ...authored } of quantities.records) {
  const { variant_id, revision, gross_floor_area_m2, dwellings } = authored;
  const identity = `${variant_id}@${revision}`;
  if (quantityIdentities.has(identity) || !records.some(record => record.variant_id === variant_id && record.revision === revision)) {
    throw new Error(`Invalid or duplicate catalogue quantity identity: ${identity}`);
  }
  const hasAuthoredQuantity = gross_floor_area_m2 != null || dwellings != null;
  const hasEstimatedArea = estimated_gross_floor_area_m2 !== undefined;
  const hasEstimatedDwellings = estimated_dwellings_range !== undefined;
  const validDwellingRange = Array.isArray(estimated_dwellings_range) && estimated_dwellings_range.length === 2
    && estimated_dwellings_range.every(value => Number.isInteger(value) && value >= 0)
    && estimated_dwellings_range[0] <= estimated_dwellings_range[1];
  if ((!hasAuthoredQuantity && !hasEstimatedArea && !hasEstimatedDwellings)
    || (gross_floor_area_m2 != null && (!Number.isFinite(gross_floor_area_m2) || gross_floor_area_m2 <= 0))
    || (dwellings != null && (!Number.isInteger(dwellings) || dwellings < 0))
    || (hasEstimatedArea && (!Number.isFinite(estimated_gross_floor_area_m2) || estimated_gross_floor_area_m2 < 0))
    || (hasEstimatedDwellings && !validDwellingRange)
    || (area_method !== undefined && !areaMethods.has(area_method))) {
    throw new Error(`Invalid catalogue quantity: ${identity}`);
  }
  quantityIdentities.add(identity);
  // The backend reports use authored programmes. Planning estimates belong to the picker.
  if (hasAuthoredQuantity) authoredQuantities.push(authored);
}
const quantityTarget = new URL('../../backend/app/data/catalogue_dwelling_programmes.json', import.meta.url);
const quantityContent = JSON.stringify({ ...quantities, records: authoredQuantities }, null, 2) + '\n';
if (process.argv.includes('--write')) writeFileSync(quantityTarget, quantityContent);
else if (readFileSync(quantityTarget, 'utf8').replace(/\r\n/g, '\n') !== quantityContent) {
  throw new Error('Backend catalogue quantities are stale; run node scripts/check-model-contract.mjs --write');
}
