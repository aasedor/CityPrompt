// @ts-expect-error -- available in Vitest without browser-project @types/node.
import { existsSync, readFileSync } from 'node:fs';
// @ts-expect-error -- available in Vitest without browser-project @types/node.
import { resolve } from 'node:path';
// @ts-expect-error -- available in Vitest without browser-project @types/node.
import { createHash } from 'node:crypto';
// @ts-expect-error -- available in Vitest without browser-project @types/node.
import process from 'node:process';
import { it, expect } from 'vitest';
import { GLTFLoader } from 'three-stdlib';
import * as THREE from 'three';
import { prepareBuildingOnlyScene } from './buildingOnlyScene';
import contractData from './buildingOnlyContracts.json';

const revision='clay-calgary-cbe-brutalist-hq-clay-v004';
const bytes=readFileSync(resolve(process.env.CITYPROMPT_BUILDING_ONLY_MODEL_DIR
  ?? '../seed/model-library/rlasm-architectural-clay/models',revision+'.glb'));
const pointer=bytes.subarray(0,64).toString().startsWith('version https://git-lfs.github.com/spec/v1');
const triangleCount=(scene:THREE.Object3D)=>{
  let count=0; scene.traverse(object=>{
    const mesh=object as THREE.Mesh;
    if(mesh.isMesh) count+=(mesh.geometry.getIndex()?.count ?? mesh.geometry.getAttribute('position').count)/3;
  }); return count;
};

it.skipIf(pointer)('retains every source-measured CBE architectural component while removing roads, plaza and neighbours',async()=>{
  expect(createHash('sha256').update(bytes).digest('hex')).toBe('a0836dc6e11577f734452f01e087fe1ee3c08c57ccfe63addd95f0428eb91433');
  const buffer=new ArrayBuffer(bytes.byteLength); new Uint8Array(buffer).set(bytes);
  const gltf=await new GLTFLoader().parseAsync(buffer,'');
  expect(triangleCount(gltf.scene)).toBe(35078);
  const before=new THREE.Box3().setFromObject(gltf.scene,true);
  const result=prepareBuildingOnlyScene(gltf.scene,revision);
  expect(triangleCount(result.clone)).toBe(28938);
  expect(result.clone.getObjectByName('CLAY_ASPHALT')).toBeUndefined();
  expect(result.clone.getObjectByName('CLAY_NEIGHBOUR')).toBeUndefined();
  expect(result.clone.getObjectByName('CLAY_PLANTING')).toBeUndefined();
  expect(triangleCount(result.clone.getObjectByName('CLAY_GLASS')!)).toBe(2244);
  expect(triangleCount(result.clone.getObjectByName('CLAY_CONCRETE')!)).toBe(60);
  const bounds=new THREE.Box3().setFromObject(result.clone,true);
  expect(bounds.min.x).toBeCloseTo(-20.1,3);
  expect(bounds.max.x).toBeCloseTo(23.2,3);
  expect(bounds.min.z).toBeCloseTo(-18.75,3);
  expect(bounds.max.z).toBeCloseTo(21.85,3);
  expect(bounds.min.y).toBeCloseTo(0,4);
  expect(bounds.max.y).toBeCloseTo(before.max.y,4);
  expect(triangleCount(gltf.scene)).toBe(35078);
  expect(new THREE.Box3().setFromObject(gltf.scene,true)).toEqual(before);
  expect(createHash('sha256').update(bytes).digest('hex')).toBe('a0836dc6e11577f734452f01e087fe1ee3c08c57ccfe63addd95f0428eb91433');
  result.ownedGeometries.forEach(geometry=>geometry.dispose());
});

for(const [candidate,contract] of Object.entries(contractData)) {
  const modelDir=process.env.CITYPROMPT_BUILDING_ONLY_MODEL_DIR ?? '../seed/model-library/rlasm-architectural-clay/models';
  const primary=resolve(modelDir,candidate+'.glb');
  const path=existsSync(primary) ? primary : resolve(modelDir,'../../objects/claude-five/models',candidate+'.glb');
  const source=readFileSync(path);
  const isPointer=source.subarray(0,64).toString().startsWith('version https://git-lfs.github.com/spec/v1');
  it.skipIf(isPointer)(candidate+' preserves its complete measured architecture and original bytes',async()=>{
    const hash=()=>createHash('sha256').update(source).digest('hex');
    expect(hash()).toBe(contract.sourceSha256);
    const buffer=new ArrayBuffer(source.byteLength); new Uint8Array(buffer).set(source);
    const gltf=await new GLTFLoader().parseAsync(buffer,'');
    const before=new THREE.Box3().setFromObject(gltf.scene,true);
    expect(triangleCount(gltf.scene)).toBe(contract.sourceTriangles);
    const result=prepareBuildingOnlyScene(gltf.scene,candidate);
    expect(result.applied).toBe(true);
    expect(triangleCount(result.clone)).toBe(contract.retainedTriangles);
    for(const [name,count] of Object.entries(contract.meshTriangles)) {
      const mesh=result.clone.getObjectByName(name);
      expect(mesh ? triangleCount(mesh) : 0,name).toBe(count);
    }
    const bounds=new THREE.Box3().setFromObject(result.clone,true);
    bounds.min.toArray().forEach((value,i)=>expect(value).toBeCloseTo(contract.bounds.min[i],4));
    bounds.max.toArray().forEach((value,i)=>expect(value).toBeCloseTo(contract.bounds.max[i],4));
    expect(triangleCount(gltf.scene)).toBe(contract.sourceTriangles);
    expect(new THREE.Box3().setFromObject(gltf.scene,true)).toEqual(before);
    expect(hash()).toBe(contract.sourceSha256);
    result.ownedGeometries.forEach(geometry=>geometry.dispose());
  });
}
