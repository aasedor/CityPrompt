import { createHash } from 'node:crypto';
import { resolve, relative, isAbsolute } from 'node:path';

export function containedPath(root, url) {
  if (!url.startsWith('/') || url.includes('\\')) throw new Error('Asset URL must be an absolute web path');
  const file = resolve(root, '.' + decodeURIComponent(url));
  const rel = relative(root, file);
  if (rel.startsWith('..') || isAbsolute(rel)) throw new Error('Asset URL escapes its public root');
  return file;
}

/** HTTP 200 and a filename extension do not establish usable asset bytes. */
export function inspectAsset(bytes, kind, expectedSha) {
  if (bytes.subarray(0, 128).toString().startsWith('version https://git-lfs.github.com/spec/v1')) throw new Error('Git LFS pointer; hydrate the exact asset');
  if (/^\s*(?:<!doctype html|<html)/i.test(bytes.subarray(0, 256).toString())) throw new Error('HTML application fallback returned instead of an asset');
  const sha256 = createHash('sha256').update(bytes).digest('hex');
  if (expectedSha && sha256 !== expectedSha) throw new Error('Exact asset SHA-256 differs');
  if (kind === 'glb') {
    if (bytes.length < 20 || bytes.toString('ascii', 0, 4) !== 'glTF' || bytes.readUInt32LE(4) !== 2 || bytes.readUInt32LE(8) !== bytes.length || bytes.readUInt32LE(16) !== 0x4e4f534a) throw new Error('Invalid or truncated GLB');
    const length = bytes.readUInt32LE(12);
    if (20 + length > bytes.length) throw new Error('Truncated GLB JSON chunk');
    const model = JSON.parse(bytes.subarray(20, 20 + length).toString());
    if (!model.meshes?.some(mesh => mesh.primitives?.length) || !model.scenes?.some(scene => scene.nodes?.length)) throw new Error('GLB has no renderable model');
    if ((model.buffers ?? []).some(buffer => buffer.uri) || (model.images ?? []).some(image => image.uri && !image.uri.startsWith('data:'))) throw new Error('GLB has unbound external buffers or images');
    return { sha256, bytes: bytes.length, meshes: model.meshes.length };
  }
  const png = bytes.subarray(0, 8).equals(Buffer.from([137,80,78,71,13,10,26,10]));
  const jpeg = bytes.length > 3 && bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255;
  const webp = bytes.toString('ascii',0,4) === 'RIFF' && bytes.toString('ascii',8,12) === 'WEBP';
  const svg = /^\s*(?:<\?xml[^>]*>\s*)?<svg\b/i.test(bytes.subarray(0,512).toString());
  if (!png && !jpeg && !webp && !svg) throw new Error('Invalid image bytes');
  if (png) {
    if (bytes.length < 33 || bytes.toString('ascii',12,16)!=='IHDR' || bytes.readUInt32BE(8)!==13 || !bytes.readUInt32BE(16) || !bytes.readUInt32BE(20)) throw new Error('Invalid PNG dimensions');
    let cursor=8, imageData=false, ended=false;
    while(cursor+12<=bytes.length) {
      const size=bytes.readUInt32BE(cursor), type=bytes.toString('ascii',cursor+4,cursor+8);
      if(cursor+12+size>bytes.length) throw new Error('Truncated PNG chunk');
      if(type==='IDAT'&&size>0)imageData=true;
      cursor+=size+12;
      if(type==='IEND') {ended=size===0;break;}
    }
    if(!imageData||!ended) throw new Error('Incomplete PNG image');
  }
  if(jpeg && bytes.indexOf(Buffer.from([255,217]),2)<0) throw new Error('Incomplete JPEG image');
  if(webp && (bytes.length<12||bytes.readUInt32LE(4)+8!==bytes.length)) throw new Error('Truncated WebP image');
  return { sha256, bytes: bytes.length };
}

export function catalogueRequirements(choices, heroImage, data) {
  const requirements = [];
  for (const choice of choices) {
    const asset = choice.placements[0];
    if (!asset) throw new Error('Unbound catalogue choice: ' + choice.id);
    const entry = data.entries.find(row => row.variant_id === asset.model.variantId && row.archetype_id === choice.option.id);
    const checks = [{ url: heroImage(asset.id, asset.thumbnail), kind: 'image' }];
    // Saved capture/reference paths retain their original technical image even
    // where discovery deliberately uses a source hero override.
    if(asset.thumbnail!==checks[0].url) checks.push({url:asset.thumbnail,kind:'image',sha256:asset.thumbnail.match(/\/([a-f0-9]{64})\.png$/)?.[1]});
    let representation = '';
    const park = data.parks.find(row => row.id === asset.properties.green_space_native_layout_id);
    const street = data.streets.find(row => row.id === asset.model.variantId);
    const library = data.library.find(row => row.variant_id === asset.model.variantId && row.model.sha256 === (entry?.sha256 || asset.model.revision));
    if (park) {
      representation = 'native_park';
      checks.push(...Object.values(park.assets).map(row => ({url:row.url,kind:'glb',sha256:row.sha256})));
    } else if (street) {
      representation = 'native_street';
      checks.push(...Object.values(street.modules).map(row => ({url:row.url,kind:'glb',sha256:row.sha256})));
    } else if (asset.model.method === 'manual_metric_section_v1') {
      representation = 'procedural_metric_street';
      if (!(asset.sectionWidth > 0) || !asset.model.revision) throw new Error('Unbound metric street: ' + choice.id);
    } else if (asset.model.method === 'public_realm_park_kit') {
      representation = 'procedural_park_kit';
      checks.push(...data.kits);
    } else if (library) {
      representation = 'model_library';
      checks.push({kind:'glb',sha256:library.model.sha256,sourcePath:'seed/model-library/rlasm-architectural-clay/'+library.model.path,variantId:library.variant_id});
    } else if (asset.properties.validation_native_url || entry?.local_url) {
      representation = 'exact_fixture';
      checks.push({url:asset.properties.validation_native_url || entry.local_url,kind:'glb',sha256:entry?.sha256 || asset.model.revision});
    } else throw new Error('No executable representation: ' + choice.id);
    requirements.push({id:asset.id,label:asset.label,domain:choice.domain,variantId:asset.model.variantId,representation,checks});
  }
  return requirements;
}
