/** Authored circulation exclusions against the bundled actual app solver. */
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const candidate=path.resolve(process.argv[2]);
const network=JSON.parse(fs.readFileSync(path.join(candidate,'evidence/walking-network.json')));
const {parkWalkHeight}=await import(pathToFileURL(path.join(candidate,'evidence/app-walk-solver.mjs')).href);
if(!network.circulationExclusionProbes?.length)throw new Error('No authored circulation exclusion probes');
const results=network.circulationExclusionProbes.map(p=>({name:p.name,point:p.point,blocked:parkWalkHeight(network,...p.point)===null}));
const report={scope:'Named circulation guard exclusions at their occupied floor height; sampled collision coverage',results,allPassed:results.every(r=>r.blocked)};
fs.writeFileSync(path.join(candidate,'evidence/circulation-collision-review.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));process.exitCode=report.allPassed?0:1;
