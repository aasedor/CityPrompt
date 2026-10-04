/** Serve the local candidate inspector; never writes to the runtime catalogue. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const here=path.dirname(fileURLToPath(import.meta.url));
const repo=path.resolve(here,'../..');
if (!process.argv[2]) throw new Error('Usage: node preview.mjs <artifact-root> [port]');
const root=path.resolve(process.argv[2]);
if (!fs.statSync(root).isDirectory()) throw new Error('Artifact root must exist');
const require=createRequire(path.join(repo,'frontend/package.json'));
const {createServer}=await import(pathToFileURL(require.resolve('vite')).href);
for(const name of ['index.html','review.js']) fs.copyFileSync(path.join(here,'preview',name),path.join(root,name));
const server=await createServer({configFile:false,root,
 resolve:{alias:{three:path.resolve(path.dirname(require.resolve('three')),'..'),'@walk-solver':path.join(repo,'frontend/src/features/parks/parkWalking.ts'),'@review-glass':path.join(repo,'frontend/src/components/viewer/globe/reviewBuildingGlass.ts')}},
 server:{host:'127.0.0.1',port:Number(process.argv[3]||5201),strictPort:true,fs:{allow:[root,repo,fs.realpathSync(path.join(repo,'frontend/node_modules'))]}}});
await server.listen();server.printUrls();
