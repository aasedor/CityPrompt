import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { containedPath, inspectAsset } from './catalogue-delivery-core.mjs';

/** Missing binary assets must never fall through to Vite's HTTP-200 app page. */
export function catalogueAssetGuard() {
  let bindings=new Map();
  const respond = (res, url, bytes) => {
    const extension=path.extname(url).toLowerCase();
    res.setHeader('Content-Type',extension==='.glb'?'model/gltf-binary':extension==='.jpg'||extension==='.jpeg'?'image/jpeg':extension==='.svg'?'image/svg+xml':'image/'+extension.slice(1));
    res.setHeader('Cache-Control','no-cache');
    res.end(bytes);
  };
  const validate = config => {
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
      if (!/^\/(?:archetypes|validation-assets|native-park-assets|street-kits|park-kits|landscape-pilots)\/.+\.(?:glb|png|jpe?g|webp|svg)$/i.test(url)) { next(); return; }
      const bound=bindings.get(url);
      if(bound) {
        try {
          const bytes=fs.readFileSync(bound.file);
          inspectAsset(bytes,url.endsWith('.glb')?'glb':'image',bound.sha256);
          res.setHeader('X-CityPrompt-Exact-SHA256',bound.sha256);respond(res,url,bytes);return;
        } catch {res.statusCode=503;res.end('Catalogue packet changed: '+url);return;}
      }
      let file;
      try { file=containedPath(server.config.publicDir,url); }
      catch { res.statusCode=404;res.end('Asset path unavailable');return; }
      if (!fs.existsSync(file)) { res.statusCode=404; res.setHeader('Content-Type','text/plain'); res.end('Catalogue asset missing: '+url); return; }
      if (fs.statSync(file).size < 300 && fs.readFileSync(file,'utf8').startsWith('version https://git-lfs.github.com/spec/v1')) {
        res.statusCode=503; res.setHeader('Content-Type','text/plain'); res.end('Catalogue asset needs Git LFS hydration: '+url); return;
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
  return {name:'catalogue-asset-delivery-guard',configResolved:validate,configureServer:install,configurePreviewServer:install};
}
