/** Isolated batch inspector, reusing the reviewed exact-GLB/walking UI. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const here=path.dirname(fileURLToPath(import.meta.url));
const repo=path.resolve(here,'../..');
if(!process.argv[2])throw new Error('Usage: node preview.mjs <batch-root> [port]');
const root=path.resolve(process.argv[2]);
const candidates=fs.readdirSync(root,{withFileTypes:true})
 .filter(d=>d.isDirectory()&&fs.existsSync(path.join(root,d.name,'build-report.json')))
 .map(d=>d.name).sort();
if(!candidates.length)throw new Error('No complete exports available yet');
const ui=path.join(here,'../neighborhood_refinement/preview');
let html=fs.readFileSync(path.join(ui,'index.html'),'utf8');
html=html.replace('<option>school-v006</option><option>fourplex-v005</option>',candidates.map(n=>`<option>${n}</option>`).join(''));
html=html.replaceAll('Neighbourhood building trial','Neighbourhood expansion');
fs.writeFileSync(path.join(root,'index.html'),html);
let js=fs.readFileSync(path.join(ui,'review.js'),'utf8');
js=js.replaceAll('neighborhood-review-model','neighborhood-expansion-model');
const start=js.indexOf('const chosen=new URLSearchParams');
if(start<0)throw new Error('Inspector initialization changed; review adaptation');
js=js.slice(0,start)+`const candidates=${JSON.stringify(candidates)};
const requested=new URLSearchParams(location.search).get('model')||localStorage.getItem('neighborhood-expansion-model');
const chosen=candidates.includes(requested)?requested:candidates[0];
document.querySelector('#model').value=chosen;load(chosen).catch(e=>status.textContent=e.message);\n`;
fs.writeFileSync(path.join(root,'review.js'),js);
if(process.argv.includes('--refresh'))process.exit(0);
const require=createRequire(path.join(repo,'frontend/package.json'));
const {createServer}=await import(pathToFileURL(require.resolve('vite')).href);
const server=await createServer({configFile:false,root,
 resolve:{alias:{three:path.resolve(path.dirname(require.resolve('three')),'..'),'@walk-solver':path.join(repo,'frontend/src/features/parks/parkWalking.ts')}},
 server:{host:'127.0.0.1',port:Number(process.argv[3]||5203),strictPort:true,
 fs:{allow:[root,repo,fs.realpathSync(path.join(repo,'frontend/node_modules'))]}}});
await server.listen();server.printUrls();
