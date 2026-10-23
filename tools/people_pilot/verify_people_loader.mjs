/** Actual Three GLTFLoader validation; GPU/image pixels verified in the browser. */
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {GLTFLoader} from '../../frontend/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {AnimationMixer,Box3} from '../../frontend/node_modules/three/build/three.module.js';
const [catalogue,publicRoot,output]=process.argv.slice(2);
if(!output)throw Error('Usage: catalogue.json public-root report.json');
globalThis.self=globalThis;
globalThis.createImageBitmap=async blob=>{const data=new DataView(await blob.arrayBuffer());return {width:data.getUint32(16),height:data.getUint32(20),close(){}};};
const loader=new GLTFLoader(),reports=[];
for(const row of JSON.parse(readFileSync(catalogue,'utf8'))){
  const bytes=readFileSync(publicRoot+row.url);
  const hash=createHash('sha256').update(bytes).digest('hex');
  if(hash!==row.sha256)throw Error('Hash conflict '+row.id);
  const gltf=await loader.parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
  const geometries=new Set(),materials=new Set(),textures=new Set();let triangles=0,meshes=0,skins=0;
  gltf.scene.traverse(o=>{
    if(!o.isMesh)return;meshes++;if(o.isSkinnedMesh)skins++;
    geometries.add(o.geometry);triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;
    const position=o.geometry.attributes.position;
    for(const a of Object.values(o.geometry.attributes))for(const value of a.array)if(!Number.isFinite(value))throw Error('Nonfinite geometry '+row.id);
    if(o.geometry.index)for(const index of o.geometry.index.array)if(index>=position.count)throw Error('Index out of bounds '+row.id);
    for(const mat of Array.isArray(o.material)?o.material:[o.material]){materials.add(mat);for(const value of Object.values(mat))if(value?.isTexture)textures.add(value);}
  });
  const poses=[];
  if(row.people){
    if(!skins||gltf.animations.length!==2)throw Error('Rig contract '+row.id);
    const mixer=new AnimationMixer(gltf.scene);
    for(const name of ['Idle','Walk']){
      const clip=gltf.animations.find(a=>a.name===name);if(!clip||clip.duration<=0)throw Error('Missing clip '+row.id);
      for(const fraction of [0,.25,.5,.75,1]){mixer.stopAllAction();mixer.clipAction(clip).play();mixer.setTime(clip.duration*fraction);gltf.scene.updateMatrixWorld(true);const box=new Box3().setFromObject(gltf.scene,true);if(![...box.min,...box.max].every(Number.isFinite))throw Error('Invalid pose '+row.id);poses.push({clip:name,fraction,min:[...box.min],max:[...box.max]});}
    }
    mixer.stopAllAction();
  }else if(skins||gltf.animations.length)throw Error('Static pose unexpectedly rigged '+row.id);
  gltf.scene.updateMatrixWorld(true);const box=new Box3().setFromObject(gltf.scene,true),dim=box.max.clone().sub(box.min);
  const geometryBytes=[...geometries].reduce((n,g)=>n+Object.values(g.attributes).reduce((m,a)=>m+a.array.byteLength,0)+(g.index?.array.byteLength??0),0);
  const textureRGBA8Bytes=[...textures].reduce((n,t)=>n+t.image.width*t.image.height*4,0);
  reports.push({id:row.id,sha256:hash,bytes:bytes.length,meshes,skins,triangles,materials:materials.size,textures:textures.size,geometryBytes,textureRGBA8Bytes,textureRGBA8WithMipmapsEstimate:Math.ceil(textureRGBA8Bytes*4/3),bounds:{min:[...box.min],max:[...box.max]},dimensionsWidthDepthHeight:[dim.x,dim.z,dim.y],poses});
  geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());textures.forEach(t=>t.dispose());
}
writeFileSync(output,JSON.stringify({note:'CPU loader/geometry validation. Browser GPU, texture pixels and frame time are separate checks.',models:reports},null,2)+'\n');
console.log(`PASS ${reports.length} exact GLBs loaded, finite geometry/index ranges, rig/static contracts and sampled poses.`);
