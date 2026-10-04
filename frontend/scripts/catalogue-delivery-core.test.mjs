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
