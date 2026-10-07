/** Exercise the app's actual movement solver against one exported candidate. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const require=createRequire(path.join(repo,'frontend/package.json'));
const {build}=require('esbuild');
const candidate=path.resolve(process.argv[2]);
const solver=path.join(candidate,'evidence/app-walk-solver.mjs');
await build({entryPoints:[path.join(repo,'frontend/src/features/parks/parkWalking.ts')],bundle:true,format:'esm',platform:'node',outfile:solver});
const {advanceParkWalk,parkWalkHeight}=await import(pathToFileURL(solver).href);
const network=JSON.parse(fs.readFileSync(path.join(candidate,'evidence/walking-network.json')));
const results=[],samples=[];
for(const route of network.routes){
 let point=[...route.points[0]],error=0;
 const start=parkWalkHeight(network,...point);
 if(start===null){results.push({name:route.name,pass:false,reason:'start blocked'});continue;}
 point[2]=start;
 for(const target of route.points.slice(1)){
  for(let i=0;i<1500;i++){
   const distance=Math.hypot(target[0]-point[0],target[1]-point[1]);
   if(distance<.01)break;
   const step=Math.min(.06,distance);
   const next=advanceParkWalk(network,point,[point[0]+(target[0]-point[0])*step/distance,point[1]+(target[1]-point[1])*step/distance]);
   if(Math.hypot(next[0]-point[0],next[1]-point[1])<.0001)break;
   point=next;samples.push({route:route.name,point});
  }
  error=Math.max(error,Math.hypot(target[0]-point[0],target[1]-point[1],target[2]-point[2]));
 }
 results.push({name:route.name,pass:error<.10,maxErrorM:+error.toFixed(3),end:point});
}
const exclusions=network.obstacles.filter(o=>o[5]<1.5&&o[5]>.4).slice(-20).map(o=>{
 const z=parkWalkHeight(network,(o[0]+o[1])/2,(o[2]+o[3])/2,.14);
 return z===null||Math.abs(z-.14)>.18;
});
const report={candidate:path.basename(candidate),allPassed:results.every(r=>r.pass)&&exclusions.every(Boolean),
 furnitureExclusion:{checked:exclusions.length,allBlocked:exclusions.every(Boolean)},results,samples};
fs.writeFileSync(path.join(candidate,'evidence/walking-solver-review.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report,samples:samples.length},null,2));process.exitCode=report.allPassed?0:1;
