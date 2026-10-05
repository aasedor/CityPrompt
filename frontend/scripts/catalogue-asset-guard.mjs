import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { containedPath, inspectAsset } from './catalogue-delivery-core.mjs';
import { gitLfsObjectRoot, parseLfsPointer, readVerifiedLfsObject } from './lfs-runtime-assets.mjs';

/** Missing binary assets must never fall through to Vite's HTTP-200 app page. */
export function catalogueAssetGuard() {
  let bindings=new Map();
  let objectRoot=null;
  let savedRevisions=new Map();
  let resolvedConfig;
  const respond = (res, url, bytes) => {
    const extension=path.extname(url).toLowerCase();
    res.setHeader('Content-Type',extension==='.glb'?'model/gltf-binary':extension==='.jpg'||extension==='.jpeg'?'image/jpeg':extension==='.svg'?'image/svg+xml':'image/'+extension.slice(1));
    res.setHeader('Cache-Control','no-cache');
    res.end(bytes);
  };
  const validate = config => {
    resolvedConfig=config;
    objectRoot=gitLfsObjectRoot(path.resolve(config.root,'..'));
    savedRevisions=new Map();
    const revisionsFile=path.join(config.root,'src/data/savedModelRevisions.json');
    if(fs.existsSync(revisionsFile)) for(const row of JSON.parse(fs.readFileSync(revisionsFile,'utf8')).revisions) {
      if(row.url!==`/model-revisions/${row.revision}.glb`||!/^[a-f0-9]{64}$/.test(row.revision)) throw new Error('Invalid saved model revision URL');
      savedRevisions.set(row.url,row.revision);
    }
    const directory=process.env.CITYPROMPT_CATALOGUE_PACKET;
    bindings=new Map();
    if(directory) {
      const receipt=JSON.parse(fs.readFileSync(path.join(directory,'delivery-manifest.json'),'utf8'));
      if(receipt.schema!=='cityprompt.catalogue-packet@1'||receipt.catalogue_activation!==false) throw new Error('Invalid local catalogue packet');
      for(const input of receipt.sourceInputs) {
        const text=fs.readFileSync(containedPath(config.root,'/'+input.path),'utf8').replace(/\r\n?/g,'\n');
        if(createHash('sha256').update(text).digest('hex')!==input.sha256) throw new Error('Catalogue packet is stale for '+input.path);
      }
      for(const asset of receipt.assets) {
        const file=containedPath(directory,asset.url);
        const checked=inspectAsset(fs.readFileSync(file),asset.url.endsWith('.glb')?'glb':'image',asset.sha256);
        if(checked.bytes!==asset.bytes||bindings.has(asset.url)) throw new Error('Catalogue packet binding differs: '+asset.url);
        bindings.set(asset.url,{...asset,file});
      }
    }
  };
  const install = server => {
    server.middlewares.use((req,res,next) => {
      const url = new URL(req.url ?? '/', 'http://localhost').pathname;
      if (!/^\/(?:archetypes|validation-assets|model-revisions|native-park-assets|street-kits|park-kits|landscape-pilots)\/.+\.(?:glb|png|jpe?g|webp|svg)$/i.test(url)) { next(); return; }
      const bound=bindings.get(url);
      if(bound) {
        try {
          const bytes=fs.readFileSync(bound.file);
          inspectAsset(bytes,url.endsWith('.glb')?'glb':'image',bound.sha256);
          res.setHeader('X-CityPrompt-Exact-SHA256',bound.sha256);respond(res,url,bytes);return;
        } catch {res.statusCode=503;res.end('Catalogue packet changed: '+url);return;}
      }
      const revision=savedRevisions.get(url);
      if(revision) {
        try {
          const bytes=readVerifiedLfsObject(objectRoot,revision);
          inspectAsset(bytes,'glb',revision);
          res.setHeader('X-CityPrompt-Exact-SHA256',revision);respond(res,url,bytes);return;
        } catch {res.statusCode=503;res.end('Saved model revision is unavailable: '+revision);return;}
      }
      let file;
      try { file=containedPath(server.config.publicDir,url); }
      catch { res.statusCode=404;res.end('Asset path unavailable');return; }
      if (!fs.existsSync(file)) { res.statusCode=404; res.setHeader('Content-Type','text/plain'); res.end('Catalogue asset missing: '+url); return; }
      if (fs.statSync(file).size < 300 && fs.readFileSync(file,'utf8').startsWith('version https://git-lfs.github.com/spec/v1')) {
        try {
          const pointer=parseLfsPointer(fs.readFileSync(file));
          if(!pointer)throw new Error('Invalid pointer');
          const bytes=readVerifiedLfsObject(objectRoot,pointer.sha256,pointer.size);
          inspectAsset(bytes,url.endsWith('.glb')?'glb':'image',pointer.sha256);
          res.setHeader('X-CityPrompt-Exact-SHA256',pointer.sha256);respond(res,url,bytes);return;
        } catch {res.statusCode=503; res.setHeader('Content-Type','text/plain'); res.end('Catalogue asset needs Git LFS hydration: '+url); return;}
      }
      // Public asset watching is disabled for this large catalogue. Serve
      // actual disk bytes so a restored file is available without restarting
      // Vite or relying on its startup public-file inventory.
      try {
        const bytes=fs.readFileSync(file);
        inspectAsset(bytes,url.endsWith('.glb')?'glb':'image');
        respond(res,url,bytes);
      } catch {res.statusCode=503;res.end('Catalogue asset is invalid: '+url);}
    });
  };
  return {name:'catalogue-asset-delivery-guard',configResolved:validate,configureServer:install,configurePreviewServer:install,
    writeBundle() {
      // A verified packet makes production output independent of the developer's
      // LFS cache or artifact paths. Never copy generated bytes into source.
      const output=path.resolve(resolvedConfig.root,resolvedConfig.build.outDir);
      if(output===resolvedConfig.root || ['src','public','scripts'].some(directory => {
        const source=path.resolve(resolvedConfig.root,directory);
        return output===source || output.startsWith(source+path.sep);
      })) throw new Error('Catalogue output must be outside source directories');
      for(const [url,binding] of bindings) {
        const bytes=fs.readFileSync(binding.file);
        inspectAsset(bytes,url.endsWith('.glb')?'glb':'image',binding.sha256);
        const target=containedPath(output,url);
        fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,bytes);
      }
    }};
}
