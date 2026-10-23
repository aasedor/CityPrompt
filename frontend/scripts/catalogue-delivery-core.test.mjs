import { test } from 'node:test';
import assert from 'node:assert/strict';
import { inspectAsset, containedPath, catalogueRequirements } from './catalogue-delivery-core.mjs';

test('rejects successful HTML responses and Git LFS pointers',()=>{
  assert.throws(()=>inspectAsset(Buffer.from('<!DOCTYPE html><html>app</html>'),'image'),/HTML/);
  assert.throws(()=>inspectAsset(Buffer.from('version https://git-lfs.github.com/spec/v1\noid sha256:abc'),'glb'),/pointer/);
});
test('rejects truncated image payloads even when their signatures remain intact',()=>{
  const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=','base64');
  inspectAsset(png,'image');
  assert.throws(()=>inspectAsset(png.subarray(0,-12),'image'),/Incomplete PNG/);
  assert.throws(()=>inspectAsset(Buffer.from([255,216,255,1]),'image'),/Incomplete JPEG/);
  const webp=Buffer.alloc(12);webp.write('RIFF');webp.writeUInt32LE(100,4);webp.write('WEBP',8);
  assert.throws(()=>inspectAsset(webp,'image'),/Truncated WebP/);
});
test('rejects corrupt, empty and incomplete models',()=>{
  const body=Buffer.from(JSON.stringify({meshes:[],scenes:[]}));
  const glb=Buffer.alloc(20+body.length);glb.write('glTF');glb.writeUInt32LE(2,4);glb.writeUInt32LE(glb.length,8);glb.writeUInt32LE(body.length,12);glb.writeUInt32LE(0x4e4f534a,16);body.copy(glb,20);
  assert.throws(()=>inspectAsset(glb,'glb'),/renderable/);
  assert.throws(()=>inspectAsset(glb.subarray(0,-1),'glb'),/truncated/);
  assert.throws(()=>inspectAsset(glb,'glb','a'.repeat(64)),/SHA/);
});
test('rejects path escape and catalogue entries without executable geometry',()=>{
  assert.throws(()=>containedPath('/public','/../secret.glb'),/escapes/);
  assert.throws(()=>catalogueRequirements([{id:'missing',option:{id:'missing'},placements:[{id:'missing',thumbnail:'/hero.png',model:{variantId:'missing'},properties:{}}]}],()=>'/hero.png',{entries:[],parks:[],streets:[],library:[]}),/No executable/);
});

test('resolves promoted candidate revisions without accepting another variant or stale hash',()=>{
  const hash='a'.repeat(64);
  const choice={id:'office',domain:'building',option:{id:'office'},placements:[{
    id:'office',label:'Office',thumbnail:'/office.png',model:{variantId:'brick-office',revision:'office-v005'},properties:{},
  }]};
  const row={archetype_id:'office',variant_id:'brick-office',candidate:'office-v005',model:{path:'models/office.glb',sha256:hash}};
  const data={entries:[],parks:[],streets:[],library:[row]};
  const result=catalogueRequirements([choice],()=>'/office.png',data);
  assert.equal(result[0].representation,'model_library');
  assert.equal(result[0].checks[1].sha256,hash);
  for(const changed of [{archetype_id:'other'},{variant_id:'other'},{candidate:'office-v004'}]) {
    assert.throws(()=>catalogueRequirements([choice],()=>'/office.png',{...data,library:[{...row,...changed}]}),/No executable/);
  }
  assert.throws(()=>catalogueRequirements([choice],()=>'/office.png',{...data,entries:[{archetype_id:'office',variant_id:'brick-office',sha256:'b'.repeat(64)}]}),/No executable/);
});

test('checks the displayed reference image as well as the runtime conditioning image',()=>{
  const asset={id:'office',label:'Office',thumbnail:'/conditioning.png',model:{variantId:'brick-office',revision:'office-v005'},properties:{}};
  const choice={id:'office',domain:'building',option:{id:'office',photoUrl:'/shown-reference.png'},placements:[asset]};
  const data={entries:[],parks:[],streets:[],library:[{archetype_id:'office',variant_id:'brick-office',candidate:'office-v005',model:{path:'models/office.glb',sha256:'a'.repeat(64)}}]};
  const images=catalogueRequirements([choice],(_id,fallback)=>fallback,data)[0].checks.filter(c=>c.kind==='image').map(c=>c.url);
  assert.deepEqual(images,['/shown-reference.png','/conditioning.png']);
});


test('separate trial manifest retains exact repository model path and publication gate',()=>{
 const choice={id:'trial',domain:'building',option:{id:'hotel'},placements:[{id:'trial',label:'Hotel',thumbnail:'/hotel.png',model:{variantId:'hotel-v',revision:'hotel-v006'},properties:{}}]};
 const row={archetype_id:'hotel',variant_id:'hotel-v',candidate:'hotel-v006',local_trial_only:true,sourcePath:'seed/model-library/objects/claude-five/models/hotel.glb',model:{path:'../model-library/objects/claude-five/models/hotel.glb',sha256:'a'.repeat(64)}};
 const result=catalogueRequirements([choice],()=>'/hotel.png',{entries:[],parks:[],streets:[],library:[row]})[0];
 assert.equal(result.checks[1].sourcePath,row.sourcePath);
 assert.equal(result.local_trial_only,true);
});


test('fixed public realm delivery requires its exact release fixture before other representations', async()=>{
 const {readFileSync}=await import('node:fs');
 const manifest=JSON.parse(readFileSync(new URL('../src/data/publicRealmRelease20261023.json',import.meta.url)));
 for (const row of manifest.models) {
  const choice={id:row.asset.id,domain:row.category,option:{id:'test'},placements:[structuredClone(row.asset)]};
  const data={entries:[{archetype_id:'test',variant_id:row.asset.model.variantId,local_url:'/wrong.glb',sha256:'b'.repeat(64)}],parks:[],streets:[{id:row.asset.model.variantId,modules:{wrong:{url:'/wrong.glb',sha256:'b'.repeat(64)}}}],library:[],fixedPublicRealm:manifest.models};
  const result=catalogueRequirements([choice],(_id,fallback)=>fallback,data)[0];
  assert.equal(result.representation,'fixed_public_realm');
  assert.deepEqual(result.checks.filter(c=>c.kind==='glb'),[{url:row.fixture.url,kind:'glb',sha256:row.runtime_sha256}]);
  assert.equal(result.local_trial_only,row.status !== 'ready');
  for (const mutate of [a=>a.model.revision='b'.repeat(64),a=>a.properties.native_public_realm_url='/wrong.glb',a=>a.model.variantId='other',a=>a.width+=1]) {
   const invalid=structuredClone(choice); mutate(invalid.placements[0]);
   assert.throws(()=>catalogueRequirements([invalid],(_id,fallback)=>fallback,data),/fixed public.realm/i);
  }
  assert.throws(()=>catalogueRequirements([choice],(_id,fallback)=>fallback,{...data,fixedPublicRealm:[]}),/fixed public.realm/i);
 }
});
