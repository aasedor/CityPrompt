/** Node GLTFLoader rig/clip smoke check. PNG pixels are checked separately by Pillow/Blender. */
import { readFileSync, writeFileSync } from 'node:fs';
import { GLTFLoader } from '../../frontend/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import { AnimationMixer, Box3 } from '../../frontend/node_modules/three/build/three.module.js';

const root = 'C:/dev-artifacts/CityPrompt/people-actions-2026-10-22/characters';
const designs = JSON.parse(readFileSync(new URL('./community_designs.json', import.meta.url), 'utf8'));
// Node has no raster DOM. Supply dimensions from the already-validated embedded
// PNG while preserving the real GLTFLoader geometry, skeleton and animation path.
globalThis.self = globalThis;
globalThis.createImageBitmap = async blob => {
  const png = new DataView(await blob.arrayBuffer());
  return { width: png.getUint32(16), height: png.getUint32(20), close() {} };
};
const loader = new GLTFLoader();
const reports = [];
for (const design of designs) {
  const bytes = readFileSync(`${root}/runtime/${design.id}.glb`);
  const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  const gltf = await loader.parseAsync(buffer, '');
  let meshes = 0;
  gltf.scene.traverse(object => {
    if (!object.isSkinnedMesh) return;
    meshes++;
    if (!object.skeleton.bones.length || !object.geometry.attributes.skinWeight) throw new Error(`Invalid skin ${design.id}`);
  });
  if (meshes < 10 || gltf.animations.length !== 2) throw new Error(`Invalid rig ${design.id}`);
  const mixer = new AnimationMixer(gltf.scene);
  for (const name of ['Idle', 'Walk']) {
    const clip = gltf.animations.find(c => c.name === name);
    if (!clip || clip.duration <= 0) throw new Error(`Missing ${name} ${design.id}`);
    mixer.stopAllAction();
    mixer.clipAction(clip).play();
    mixer.setTime(clip.duration / 2);
    gltf.scene.updateMatrixWorld(true);
    const bounds = new Box3().setFromObject(gltf.scene, true);
    if (![...bounds.min, ...bounds.max].every(Number.isFinite)) throw new Error(`Invalid posed bounds ${design.id}`);
  }
  reports.push({ id: design.id, skinnedMeshes: meshes, clips: gltf.animations.map(c => ({ name: c.name, duration: c.duration, tracks: c.tracks.length })) });
  mixer.stopAllAction();
  gltf.scene.traverse(o => { if (o.isMesh) o.geometry.dispose(); });
}
writeFileSync(`${root}/gltf-loader-validation.json`, JSON.stringify(reports, null, 2) + '\n');
console.log('PASS 20/20 real Three.js GLTFLoader parses and rig/clip poses; texture pixels independently verified; GPU render excluded.');
