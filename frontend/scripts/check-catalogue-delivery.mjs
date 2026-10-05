/** Read-only whole-catalogue audit. No generation, catalogue activation or project writes. */
import { createServer } from 'vite';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { catalogueRequirements, containedPath, inspectAsset } from './catalogue-delivery-core.mjs';
import { gitLfsObjectRoot, parseLfsPointer, readVerifiedLfsObject } from './lfs-runtime-assets.mjs';

const frontend = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const repo = resolve(frontend, '..');
const args = process.argv.slice(2);
const option = name => args.find(arg => arg.startsWith(name+'='))?.slice(name.length+1);
const base = option('--base-url');
const output = option('--report');
const fixtures = option('--fixtures');
const libraryReport = option('--model-library-report');
const packetDirectory = option('--packet-dir');
const packet = process.env.CITYPROMPT_CATALOGUE_PACKET ? readPacket(process.env.CITYPROMPT_CATALOGUE_PACKET) : null;
const metadataOnly = args.includes('--metadata-only');
const publicRoot = resolve(process.env.CITYPROMPT_PUBLIC_DIR || resolve(frontend,'public'));
const read = file => JSON.parse(readFileSync(file,'utf8').replace(/^\uFEFF/,''));
function readPacket(directory) {
  const receipt = JSON.parse(readFileSync(resolve(directory,'delivery-manifest.json'),'utf8'));
  if (receipt.schema !== 'cityprompt.catalogue-packet@1') throw new Error('Invalid catalogue packet');
  return {directory,receipt};
}
const source = name => read(resolve(frontend,'src/data',name));
const server = await createServer({root:frontend,configFile:resolve(frontend,'vite.config.ts'),logLevel:'silent',
  // This SSR-only audit must never re-optimize the scripts of a live preview.
  // node_modules can be shared between worktrees, so put its cache in the
  // checkout's ignored artifact directory rather than that shared dependency tree.
  cacheDir:resolve(repo,'artifacts/catalogue-audit-vite-cache'),
  server:{middlewareMode:true},appType:'custom', optimizeDeps:{noDiscovery:true,entries:[]}});
let choices, heroImage, sharedEquipment;
try {
  choices = (await server.ssrLoadModule('/src/features/pickPlace/canonicalCatalogue.ts')).CLASSROOM_CHOICES;
  heroImage = (await server.ssrLoadModule('/src/features/pickPlace/pickerHeroImages.ts')).pickerHeroImage;
  sharedEquipment = Object.values((await server.ssrLoadModule('/src/data/sharedParkEquipment.ts')).SHARED_PARK_EQUIPMENT);
} finally { await server.close(); }
const entries = [...source('validationCatalogue.json').entries,...source('classroomExpansion.json').entries];
if (fixtures) {
  const sealed = read(fixtures);
  if (!sealed.local_trial_only || sealed.models.length !== 10) throw new Error('Expected sealed ten-model local fixture receipt');
  for (const model of sealed.models) {
    choices.push({id:model.asset.id,domain:'building',option:{id:model.archetype_id},placements:[model.asset]});
    entries.push(model.entry);
  }
}
const starter = source('classroomStarter.json');
const equipmentManifest = read(resolve(frontend,'public/park-kits/shared-park-equipment-v1/kit_manifest.json'));
const sharedKits = sharedEquipment.map(asset => {
  const lock = equipmentManifest.assets.find(row => row.id === asset.id && asset.url.endsWith('/'+row.file));
  if (!lock?.sha256) throw new Error('Shared park equipment lacks an exact delivery lock: '+asset.id);
  return {url:asset.url,kind:'glb',sha256:lock.sha256};
});
const data = {entries,parks:source('nativeParks.json').layouts,streets:source('nativeStreetPilots.json'),
  library:read(resolve(repo,'seed/model-library/rlasm-architectural-clay/library.json')).entries,
  kits:[...sharedKits,...starter.dependencies.filter(row=>row.location==='public'&&row.path.endsWith('.glb')&&/park-kits|landscape-pilots/.test(row.path)).map(row=>({url:'/'+row.path,kind:'glb',sha256:row.sha256}))]};
const rows = catalogueRequirements(choices,heroImage,data);
const savedLayoutChecks = Object.values(Object.fromEntries(data.parks.flatMap(park=>Object.values(park.assets).map(asset=>[asset.url,{url:asset.url,kind:'glb',sha256:asset.sha256}]))));
const rusticKitChecks=Object.values(source('neighborhoodParkV0StickerKit.json').assets).map(asset=>({url:asset.url,kind:'glb',sha256:asset.sha256}));
const savedRevisionChecks=source('savedModelRevisions.json').revisions.map(row=>({url:row.url,kind:'glb',sha256:row.revision}));
const receipt = libraryReport ? read(libraryReport) : null;
if(base && (!receipt?.checked_utc || Date.now()-Date.parse(receipt.checked_utc)>10*60*1000)) throw new Error('A fresh Model Library storage receipt is required (within ten minutes)');
const results = new Map();
const payloads = new Map();
for (const row of [...rows,{checks:[...savedLayoutChecks,...rusticKitChecks,...savedRevisionChecks]}]) for (const check of row.checks) {
  const key = check.url || check.sourcePath;
  if (results.has(key)) continue;
  try {
    if (check.sourcePath && base) {
      const stored = receipt?.catalogue?.find(item=>item.variant_id===check.variantId&&item.sha256===check.sha256&&item.status==='verified');
      if (!stored) throw new Error('Live Model Library readback is required; source bytes alone do not prove storage');
      results.set(key,{status:'PASS',...stored}); continue;
    }
    if (metadataOnly) {
      if (check.kind==='glb'&& !/^[a-f0-9]{64}$/.test(check.sha256??'')) throw new Error('Missing exact model hash');
      if (!check.url && !existsSync(resolve(repo,check.sourcePath))) throw new Error('Missing seed model binding');
      if (check.url) containedPath(publicRoot,check.url);
      results.set(key,{status:'METADATA_ONLY'}); continue;
    }
    let bytes;
    if (base && check.url) {
      const response = await fetch(new URL(check.url,base),{signal:AbortSignal.timeout(30000)});
      if (!response.ok) throw new Error('HTTP '+response.status);
      bytes = Buffer.from(await response.arrayBuffer());
    } else {
      const bound=packet?.receipt.assets.find(row=>row.url===check.url);
      const file=check.sourcePath?resolve(repo,check.sourcePath):containedPath(bound?packet.directory:publicRoot,check.url);
      bytes=existsSync(file)?readFileSync(file):check.url?.startsWith('/model-revisions/')
        ? readVerifiedLfsObject(gitLfsObjectRoot(repo),check.sha256) : readFileSync(file);
      const pointer=parseLfsPointer(bytes);
      if(pointer)bytes=readVerifiedLfsObject(gitLfsObjectRoot(repo),pointer.sha256,pointer.size);
      if(bound) inspectAsset(bytes,check.kind,bound.sha256);
    }
    results.set(key,{status:'PASS',...inspectAsset(bytes,check.kind,check.sha256)});
    if(packetDirectory && check.url) payloads.set(check.url,bytes);
  } catch(error) { results.set(key,{status:'FAIL',error:error.message}); }
}
const report = {schema:'cityprompt.catalogue-delivery-audit@1',checked_utc:new Date().toISOString(),scope:base||publicRoot,
  metadata_only:metadataOnly,choice_count:rows.length,distinct_assets:results.size,
  failures:[...results].filter(([,v])=>v.status==='FAIL').map(([asset,result])=>({asset,...result})),
  saved_layout_dependencies:savedLayoutChecks.map(check=>({...check,...results.get(check.url)})),
  saved_model_revisions:savedRevisionChecks.map(check=>({...check,...results.get(check.url)})),
  rustic_park_dependencies:rusticKitChecks.map(check=>({...check,...results.get(check.url)})),
  choices:rows.map(row=>({...row,status:row.checks.every(check=>results.get(check.url||check.sourcePath).status!=='FAIL')?(metadataOnly?'METADATA_ONLY':'PASS'):'FAIL',checks:row.checks.map(check=>({...check,...results.get(check.url||check.sourcePath)}))}))};
if (output) writeFileSync(output,JSON.stringify(report,null,2)+'\n');
if (packetDirectory && report.failures.length===0 && !metadataOnly) {
  const directory=resolve(packetDirectory);
  if(directory.startsWith(repo)) throw new Error('Keep generated packets outside the source tree');
  const sources=['src/data/validationCatalogue.json','src/data/classroomExpansion.json','src/data/nativeParks.json','src/data/nativeStreetPilots.json','src/data/streetManual.json','src/data/flexibleParks.json','src/data/sharedParkEquipment.ts','src/data/neighborhoodParkV0StickerKit.json','src/data/savedModelRevisions.json','public/park-kits/shared-park-equipment-v1/kit_manifest.json','src/features/pickPlace/pickerHeroImages.ts','src/features/pickPlace/assetRegistry.ts','src/features/pickPlace/canonicalCatalogue.ts','src/features/pickPlace/catalogueClassification.ts'];
  const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
  const normalize=file=>readFileSync(file,'utf8').replace(/\r\n?/g,'\n');
  const receipt={schema:'cityprompt.catalogue-packet@1',catalogue_activation:false,sourceInputs:sources.map(file=>({path:file,sha256:hash(normalize(resolve(frontend,file)))})),
    assets:[...payloads].map(([url,bytes])=>({url,sha256:hash(bytes),bytes:bytes.length}))};
  for(const [url,bytes] of payloads) {
    const file=containedPath(directory,url);
    if(existsSync(file)&&hash(readFileSync(file))!==hash(bytes)) throw new Error('Existing packet asset differs: '+url);
  }
  if(existsSync(resolve(directory,'delivery-manifest.json'))&&JSON.stringify(read(resolve(directory,'delivery-manifest.json')))!==JSON.stringify(receipt)) throw new Error('Existing packet receipt differs; select a new packet directory');
  for(const [url,bytes] of payloads) {const file=containedPath(directory,url);mkdirSync(dirname(file),{recursive:true});if(!existsSync(file))writeFileSync(file,bytes);}
  writeFileSync(resolve(directory,'delivery-manifest.json'),JSON.stringify(receipt,null,2)+'\n');
  console.log('Prepared exact local catalogue packet: '+directory);
}
console.log(`${report.choice_count} catalogue choices; ${report.distinct_assets} distinct image/model dependencies; ${report.failures.length} failures${metadataOnly?' (metadata only; no runtime proof)':''}.`);
for (const failure of report.failures.slice(0,15)) console.error(`${failure.asset}: ${failure.error}`);
if (report.failures.length) process.exitCode=1;
