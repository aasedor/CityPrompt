/** Prominent-prop probes against the actual app solver bundled by check-walking. */
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const candidate=path.resolve(process.argv[2]);
const network=JSON.parse(fs.readFileSync(path.join(candidate,'evidence/walking-network.json')));
const {parkWalkHeight}=await import(pathToFileURL(path.join(candidate,'evidence/app-walk-solver.mjs')).href);
if(!network.gardenExclusionProbes?.length)throw new Error('No authored garden probes');
const results=network.gardenExclusionProbes.map(p=>({name:p.name,point:p.point,blocked:parkWalkHeight(network,...p.point)===null}));
const report={scope:'Prominent garden props; sampled collision coverage, not exhaustive collision certification',results,allPassed:results.every(r=>r.blocked)};
fs.writeFileSync(path.join(candidate,'evidence/garden-collision-review.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));process.exitCode=report.allPassed?0:1;
