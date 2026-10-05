import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

/** JSON.parse accepts last-wins duplicates. Reject them before that information is lost. */
export function duplicateJsonKeys(text) {
  JSON.parse(text);
  const stack=[], duplicates=[];
  const tokens=/"(?:\\[\s\S]|[^"\\])*"|[{}\[\]:,]|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|true|false|null/g;
  for(const token of text.matchAll(tokens)) {
    const value=token[0];
    if(value==='{')stack.push(new Set());
    else if(value==='[')stack.push(null);
    else if(value==='}'||value===']')stack.pop();
    else if(value.startsWith('"') && /^\s*:/.test(text.slice(token.index+value.length))) {
      const key=JSON.parse(value), keys=stack.at(-1);
      if(keys?.has(key))duplicates.push({key,line:text.slice(0,token.index).split('\n').length});
      keys?.add(key);
    }
  }
  return duplicates;
}

export function checkCatalogueJson(directory) {
  return fs.readdirSync(directory).filter(file=>file.endsWith('.json')).flatMap(file=>
    duplicateJsonKeys(fs.readFileSync(path.join(directory,file),'utf8')).map(row=>({file,...row})));
}
if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const duplicates=checkCatalogueJson(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../src/data'));
  if(duplicates.length) {console.error(JSON.stringify(duplicates,null,2));process.exitCode=1;}
  else console.log('Catalogue JSON: no duplicate keys');
}
