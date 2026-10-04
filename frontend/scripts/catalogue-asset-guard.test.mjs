import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync,writeFileSync,rmSync,mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createServer } from 'vite';
import { catalogueAssetGuard } from './catalogue-asset-guard.mjs';
import { createHash } from 'node:crypto';

test('missing and unhydrated assets cannot return the HTTP-200 application page',async()=>{
  const root=mkdtempSync(join(tmpdir(),'cityprompt-asset-guard-'));
  writeFileSync(join(root,'index.html'),'<!doctype html><html>application</html>');
  mkdirSync(join(root,'public/archetypes'),{recursive:true});
  writeFileSync(join(root,'public/archetypes/pointer.png'),'version https://git-lfs.github.com/spec/v1\n');
  const server=await createServer({configFile:false,root,plugins:[catalogueAssetGuard()],logLevel:'silent',server:{host:'127.0.0.1',port:0},optimizeDeps:{noDiscovery:true,entries:[]}});
  try {
    await server.listen();
    const address=server.httpServer.address();
    const base='http://127.0.0.1:'+address.port;
    const missing=await fetch(base+'/validation-assets/missing.glb');
    assert.equal(missing.status,404);assert.match(await missing.text(),/Catalogue asset missing/);
    const pointer=await fetch(base+'/archetypes/pointer.png');
    assert.equal(pointer.status,503);assert.match(await pointer.text(),/Git LFS hydration/);
    // A recovered asset appears after Vite has cached its initial inventory.
    const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=','base64');
    writeFileSync(join(root,'public/archetypes/recovered.png'),png);
    const recovered=await fetch(base+'/archetypes/recovered.png');
    assert.equal(recovered.status,200);assert.match(recovered.headers.get('content-type'),/image\/png/);
    assert.deepEqual(Buffer.from(await recovered.arrayBuffer()),png);
  } finally {await server.close();rmSync(root,{recursive:true,force:true});}
});

test('a packet with changed bytes or stale catalogue inputs refuses startup',async()=>{
  const root=mkdtempSync(join(tmpdir(),'cityprompt-stale-packet-'));
  const packet=join(root,'packet');mkdirSync(packet);mkdirSync(join(packet,'archetypes'));
  writeFileSync(join(root,'catalogue.json'),'current catalogue');
  writeFileSync(join(packet,'archetypes/hero.png'),'corrupt bytes');
  const manifest={schema:'cityprompt.catalogue-packet@1',catalogue_activation:false,sourceInputs:[{path:'catalogue.json',sha256:'a'.repeat(64)}],assets:[]};
  const prior=process.env.CITYPROMPT_CATALOGUE_PACKET;
  process.env.CITYPROMPT_CATALOGUE_PACKET=packet;
  try {
    writeFileSync(join(packet,'delivery-manifest.json'),JSON.stringify(manifest));
    await assert.rejects(createServer({configFile:false,root,plugins:[catalogueAssetGuard()],logLevel:'silent',optimizeDeps:{noDiscovery:true,entries:[]}}),/stale/);
    manifest.sourceInputs[0].sha256=createHash('sha256').update('current catalogue').digest('hex');
    manifest.assets.push({url:'/archetypes/hero.png',sha256:'b'.repeat(64),bytes:13});
    writeFileSync(join(packet,'delivery-manifest.json'),JSON.stringify(manifest));
    await assert.rejects(createServer({configFile:false,root,plugins:[catalogueAssetGuard()],logLevel:'silent',optimizeDeps:{noDiscovery:true,entries:[]}}),/SHA-256 differs/);
  } finally {
    if(prior===undefined)delete process.env.CITYPROMPT_CATALOGUE_PACKET;else process.env.CITYPROMPT_CATALOGUE_PACKET=prior;
    rmSync(root,{recursive:true,force:true});
  }
});
