/** Prepare local-only picker derivatives from the finite reviewed native-image batch.
 * Never generates, changes a GLB, replaces a source thumbnail or calls a provider.
 * --root contains receipts-v2/ (selected) and receipts/ (retained Maya/Clara).
 * --public is the existing local runtime public directory; --sharp names a
 * preinstalled sharp module, so this does not add an app dependency.
 */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const args=Object.fromEntries(process.argv.slice(2).reduce((rows,value,index,all)=>{
  if(value.startsWith('--'))rows.push([value.slice(2),all[index+1]]);return rows;
},[]));
for(const key of ['root','public','sharp'])if(!args[key])throw Error(`Missing --${key}`);
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const sharp=createRequire(import.meta.url)(args.sharp);
const json=async file=>JSON.parse(await readFile(file,'utf8'));
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
const actors=await json(path.join(repo,'frontend/src/features/people/peopleCatalogue.json'));
const styles=await json(path.join(repo,'tools/people_pilot/appearance_styles.json'));
if(actors.length!==23||styles.length!==23||new Set(styles.map(s=>s.id)).size!==23)throw Error('Expected exact 23-person batch');
const destination=path.join(args.public,'street-kits/people-appearance-v1');
const originals=path.join(args.root,'selected-originals');
await mkdir(destination,{recursive:true});await mkdir(originals,{recursive:true});
const previews=[],evidence=[];
for(const actor of actors){
  const style=styles.find(s=>s.id===actor.id);if(!style)throw Error(`Missing style ${actor.id}`);
  const current=path.join(args.root,'receipts-v2',actor.id+'.json');
  const receipt=await json(existsSync(current)?current:path.join(args.root,'receipts',actor.id+'.json'));
  if(receipt.id!==actor.id)throw Error(`Wrong receipt ${actor.id}`);
  const original=await readFile(receipt.path);
  const output=await sharp(original).resize({width:480,height:600,fit:'inside',withoutEnlargement:true}).webp({quality:84,effort:5}).toBuffer();
  const dimensions=await sharp(output).metadata();
  if(dimensions.width<400||dimensions.height<500||output.length>100000)throw Error(`Invalid/bloated portrait ${actor.id}`);
  const sourceThumbnail=await readFile(path.join(args.public,actor.thumbnailUrl));
  const model=await readFile(path.join(args.public,actor.url));
  if(digest(sourceThumbnail)!==actor.thumbnailSha256||digest(model)!==actor.sha256)throw Error(`Source mismatch ${actor.id}`);
  const outputPath=path.join(destination,actor.id+'.webp');
  if(existsSync(outputPath)&&digest(await readFile(outputPath))!==digest(output))throw Error(`Refusing conflicting preview ${actor.id}`);
  await writeFile(outputPath,output);
  await copyFile(receipt.path,path.join(originals,actor.id+'.png'));
  previews.push({id:actor.id,name:style.name,style:style.style,url:'/street-kits/people-appearance-v1/'+actor.id+'.webp',sha256:digest(output),bytes:output.length,width:dimensions.width,height:dimensions.height});
  evidence.push({...receipt,originalSha256:digest(original),sourceThumbnailSha256:digest(sourceThumbnail),unchangedModelSha256:digest(model),preview:previews.at(-1)});
}
await writeFile(path.join(repo,'frontend/src/features/people/peopleAppearancePreviews.json'),JSON.stringify(previews,null,2)+'\n');
await writeFile(path.join(args.root,'appearance-provenance.json'),JSON.stringify({localOnly:true,published:false,generator:'built-in image_gen',derivative:'sharp 480x600 inside, WebP quality 84, no crop',limitations:'Imagined appearances and varied clothing; not exact 3D captures or a guarantee of AI identity/wardrobe. No render prompt or character-reference wiring changed.',actors:evidence},null,2)+'\n');
console.log(JSON.stringify({count:previews.length,totalBytes:previews.reduce((sum,p)=>sum+p.bytes,0),maxBytes:Math.max(...previews.map(p=>p.bytes)),destination}));
