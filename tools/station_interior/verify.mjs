// Verify both directions on actual authored routes and reimported GLB surfaces.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { advanceParkWalk, parkWalkHeight } from '../../frontend/src/features/parks/parkWalking.ts';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const require = createRequire(path.join(root, 'frontend/package.json'));
const THREE = await import(pathToFileURL(require.resolve('three')).href);
const { MeshBVH, acceleratedRaycast } = require('three-mesh-bvh');
const { GLTFLoader } = await import(pathToFileURL(require.resolve('three/examples/jsm/loaders/GLTFLoader.js')).href);
const folder = path.resolve(process.argv[2]);
const reportPath = path.join(folder, 'walking-verification-v1.json');
if (fs.existsSync(reportPath)) throw new Error('Preserve the existing verification record; use a new candidate for changes.');
const pre = JSON.parse(fs.readFileSync(path.join(folder, 'prework-manifest.json')));
const networkBytes = fs.readFileSync(path.join(folder, 'walking-network.json'));
const network = JSON.parse(networkBytes);
const bytes = fs.readFileSync(path.join(folder, pre.candidate + '.glb'));
const hash = createHash('sha256').update(bytes).digest('hex');
const lock=JSON.parse(fs.readFileSync(path.join(folder,'walking-model-lock.json')));
if(hash!==lock.model_sha256)throw new Error('Model hash mismatch');
if(createHash('sha256').update(networkBytes).digest('hex')!==lock.network_sha256)throw new Error('Network hash mismatch');
const { scene } = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
let embedded = null;
scene.traverse(o => { if (o.userData.cityprompt_walking_json) embedded = JSON.parse(o.userData.cityprompt_walking_json); });
if(JSON.stringify(embedded)!==JSON.stringify(network))throw new Error('Runtime GLB must contain the exact verified network');
scene.updateMatrixWorld(true);
const surfaces = [], solids = [];
scene.traverse(o => {
  if (!o.isMesh) return;
  const materials = Array.isArray(o.material) ? o.material : [o.material];
  o.geometry.boundsTree = new MeshBVH(o.geometry);
  o.raycast = acceleratedRaycast;
  for (const material of materials) material.side = THREE.DoubleSide;
  if (materials.some(m => m.name === 'CLAY_WALK_FLOOR')) surfaces.push(o);
  if (!materials.some(m => m.name === 'CLAY_GLASS')) solids.push(o);
});
const ray = new THREE.Raycaster(), bodyRay = new THREE.Raycaster(), results = [], failures = [];
let samples = 0, maxSurfaceError = 0, maxStep = 0;

for (const route of network.routes) for (const reversed of [false, true]) {
  const previousFailures = failures.length;
  const points = reversed ? [...route.points].reverse() : route.points;
  let current = [...points[0]];
  const z = parkWalkHeight(network, current[0], current[1], current[2]);
  if (z === null) { failures.push(`${route.name}: missing start`); continue; }
  current[2] = z;
  for (let i = 1; i < points.length; i++) {
    const target = points[i];
    let count = 0;
    while (Math.hypot(current[0] - target[0], current[1] - target[1]) > .04 && count++ < 5000) {
      const dx = target[0] - current[0], dy = target[1] - current[1], length = Math.hypot(dx, dy);
      const step = Math.min(.09, length);
      const next = advanceParkWalk(network, current, [current[0] + dx / length * step, current[1] + dy / length * step]);
      if (Math.hypot(next[0] - current[0], next[1] - current[1]) < .0001) {
        failures.push(`${route.name} ${reversed ? 'reverse' : 'forward'}: stopped at ${current.map(x => x.toFixed(3))}, aiming at ${target}`); break;
      }
      maxStep = Math.max(maxStep, Math.abs(next[2] - current[2]));
      // Sweep a 44 cm wide torso through real rails, stone and furniture.
      // Test above the risers, including the height of both guard rails.
      const move = new THREE.Vector3(next[0]-current[0],next[2]-current[2],current[1]-next[1]);
      bodyRay.far = move.length() + .001;
      for (const height of [.45,.8,1.05,1.7]) for (const side of [-.22,0,.22]) {
        bodyRay.set(new THREE.Vector3(current[0]-dy/length*side,current[2]+height,-current[1]-dx/length*side),move.clone().normalize());
        const obstruction = bodyRay.intersectObjects(solids,false)[0];
        if (obstruction) { failures.push(`Body clearance: ${route.name} at ${current} (${obstruction.object.name})`); break; }
      }
      if (failures.length > previousFailures) break;
      current = next;samples++;
      // Float32 GLB vertices can put a shared tread boundary micrometres on
      // either side. Check the same point within a 0.02 mm positional tolerance.
      let error=Infinity;
      for(const [dx,dy] of [[0,0],[.00002,0],[-.00002,0],[0,.00002],[0,-.00002]]){
        ray.set(new THREE.Vector3(current[0]+dx,30,-current[1]-dy),new THREE.Vector3(0,-1,0));
        const hits=ray.intersectObjects(surfaces,false);
        for(const hit of hits)error=Math.min(error,Math.abs(hit.point.y-current[2]));
        if(error<.0001)break;
      }
      maxSurfaceError = Math.max(maxSurfaceError, error);
      if (error > .012) { failures.push(`GLB surface mismatch at ${current}: ${error}`); break; }
    }
    if (count >= 5000) failures.push(`${route.name}: movement did not converge`);
    if (failures.length > previousFailures) break;
  }
  results.push({ route: route.name, direction: reversed ? 'reverse' : 'forward', end: current });
}
const result = { status: failures.length ? 'FAIL' : 'PASS', model_sha256: hash, samples, max_step_m: maxStep,
  max_surface_error_m: maxSurfaceError, body_clearance_width_m: .44, results, failures, scope: 'Deterministic movement and torso clearance on exported route geometry; browser and visual review are separate.' };
fs.writeFileSync(reportPath, JSON.stringify(result, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify(result, null, 2));
if (failures.length) process.exitCode = 1;
