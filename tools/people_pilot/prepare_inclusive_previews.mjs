/** Eight explicit built-in-image receipts -> small local picker derivatives. No API calls. */

import {createRequire} from 'node:module';

import {readFile,writeFile,mkdir} from 'node:fs/promises';

import {createHash} from 'node:crypto';

const [root,sharpPath]=process.argv.slice(2);

if(!sharpPath)throw Error('Usage: artifact-root installed-sharp-path');

const sharp=createRequire(import.meta.url)(sharpPath),sha=data=>createHash('sha256').update(data).digest('hex');

const roles=[['white-cane','Ava','White cane · teal jacket'],['guide-dog','Mateo','Guide dog · camel hoodie'],['manual-wheelchair','Maya','Manual wheelchair · coral knit'],['power-wheelchair','Andre','Powered wheelchair · plum polo'],['older-woman','Clara','Older adult · sage coat'],['older-man-rollator','Eli','Rollator · blue jacket'],['family-parent-child','Imani & child','Parent and child'],['family-stroller','Noah & baby','Parent - striped T-shirt & stroller']];

await mkdir(root+'/picker',{recursive:true});const previews=[];

for(const [role,name,style] of roles){

 const id='people-inclusive-'+role,receipt=JSON.parse(await readFile(`${root}/receipts/${id}.json`,'utf8'));

 const original=await readFile(receipt.path);

 if(sha(original)!==receipt.rawSha256)throw Error('Original image changed '+id);

 const bytes=await sharp(original).resize({width:480,height:600,fit:'inside',withoutEnlargement:true}).webp({quality:84,effort:5}).toBuffer();

 const {width,height}=await sharp(bytes).metadata();

 if(width!==480||height!==600||bytes.length>100000)throw Error('Unexpected picker dimensions '+id);

 await writeFile(`${root}/picker/${id}.webp`,bytes);

 previews.push({id,name,style,url:`/street-kits/people-appearance-v3/${id}.webp`,sha256:sha(bytes),bytes:bytes.length,width,height});

}

await writeFile(root+'/picker/previews.json',JSON.stringify(previews,null,2)+'\n');

console.log(JSON.stringify({previews:previews.length,bytes:previews.reduce((n,r)=>n+r.bytes,0),output:root+'/picker',published:false}));
