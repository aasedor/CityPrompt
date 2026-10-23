/** Finite ten-portrait local update. No generation/provider calls and no model edits.
 * --root: reviewed receipts/*.json; --public: current runtime public folder;
 * --sharp: preinstalled sharp module. Preserve original previews and raw receipts.
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
const sharp=createRequire(import.meta.url)(args.sharp),json=async file=>JSON.parse(await readFile(file,'utf8'));
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
const registry=path.join(repo,'frontend/src/features/people/peopleAppearancePreviews.json');
const stylesFile=path.join(repo,'tools/people_pilot/appearance_styles.json');
const baseline=path.join(args.root,'appearance-baseline.json'),styleBaseline=path.join(args.root,'styles-baseline.json');
if(!existsSync(baseline))await copyFile(registry,baseline);
if(!existsSync(styleBaseline))await copyFile(stylesFile,styleBaseline);
const previews=await json(baseline),styles=await json(styleBaseline);
const actors=await json(path.join(repo,'frontend/src/features/people/peopleCatalogue.json'));
const names=['noah','leo','ava','nina','jules','rhea','sana','kai','amara','felix'];
const ids=names.map(name=>'people-community-'+name);
if(actors.length!==23||previews.length!==23||styles.length!==23)throw Error('Expected complete 23-person catalogue');
const destination=path.join(args.public,'street-kits/people-appearance-v2');
await mkdir(destination,{recursive:true});await mkdir(path.join(args.root,'selected-originals'),{recursive:true});
const evidence=[];
for(const id of ids){
  const actor=actors.find(a=>a.id===id),previous=previews.find(a=>a.id===id),style=styles.find(a=>a.id===id);
  if(!actor||!previous||!style)throw Error('Missing existing actor '+id);
  const receipt=await json(path.join(args.root,'receipts',id+'.json'));
  if(receipt.id!==id||!receipt.prompt||!receipt.wardrobe||!receipt.path)throw Error('Incomplete receipt '+id);
  const original=await readFile(receipt.path),reference=await readFile(receipt.reference);
  if(digest(reference)!==previous.sha256)throw Error('Reference differs from approved previous preview '+id);
  const glb=await readFile(path.join(args.public,actor.url)),thumbnail=await readFile(path.join(args.public,actor.thumbnailUrl));
  if(digest(glb)!==actor.sha256||digest(thumbnail)!==actor.thumbnailSha256)throw Error('Source model/thumbnail changed '+id);
  const output=await sharp(original).resize({width:480,height:600,fit:'inside',withoutEnlargement:true}).webp({quality:84,effort:5}).toBuffer();
  const dimensions=await sharp(output).metadata();
  if(dimensions.width<400||dimensions.height<500||output.length>100000)throw Error('Invalid preview '+id);
  const target=path.join(destination,id+'.webp'),sha256=digest(output);
  if(existsSync(target)&&digest(await readFile(target))!==sha256)throw Error('Refusing conflicting v2 preview '+id);
  await writeFile(target,output);await copyFile(receipt.path,path.join(args.root,'selected-originals',id+'.png'));
  const preview={id,name:receipt.name,style:receipt.style,url:'/street-kits/people-appearance-v2/'+id+'.webp',sha256,bytes:output.length,width:dimensions.width,height:dimensions.height};
  previews[previews.indexOf(previous)]=preview;
  styles[styles.indexOf(style)]={id,name:receipt.name,style:receipt.style,wardrobe:receipt.wardrobe};
  evidence.push({...receipt,originalSha256:digest(original),referenceSha256:digest(reference),unchangedModelSha256:digest(glb),unchangedThumbnailSha256:digest(thumbnail),previous,preview});
}
if(new Set(previews.map(p=>p.id)).size!==23||new Set(previews.map(p=>p.url)).size!==23)throw Error('Duplicate catalogue identity');
const retained=(await json(baseline)).filter(p=>!ids.includes(p.id));
if(retained.length!==13||retained.some(p=>JSON.stringify(p)!==JSON.stringify(previews.find(q=>q.id===p.id))))throw Error('Unrelated portrait changed');
await writeFile(registry,JSON.stringify(previews,null,2)+'\n');
await writeFile(stylesFile,JSON.stringify(styles,null,2)+'\n');
await writeFile(path.join(args.root,'appearance-provenance.json'),JSON.stringify({localOnly:true,published:false,generator:'built-in image_gen',derivative:'sharp 480x600 inside, WebP q84, no crop',updated:10,retained:13,limitations:'Picker-only imagined wardrobe and expression. GLBs and render reference wiring unchanged; AI identity/outfit is not guaranteed.',actors:evidence},null,2)+'\n');
console.log(JSON.stringify({updated:10,retained:13,totalBytes:previews.reduce((sum,p)=>sum+p.bytes,0),newBytes:evidence.reduce((sum,p)=>sum+p.preview.bytes,0),destination}));
