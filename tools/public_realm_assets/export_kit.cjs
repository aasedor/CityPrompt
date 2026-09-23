// Export the actual runtime kit, preserving metric Z-up vertices and linear colours.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const esbuild = require(path.join(root, 'frontend/node_modules/esbuild'));
const out = path.resolve(process.argv[2]);
fs.mkdirSync(out, { recursive: true });
const geometryFile = path.join(out, 'kit.json');
if (fs.existsSync(geometryFile)) throw new Error('Refusing to overwrite kit.json');
const source = `
import { createMeadowFurniture } from './frontend/src/components/viewer/globe/meadowFurnitureGeometry';
import { createMeadowVegetation } from './frontend/src/components/viewer/globe/meadowVegetationGeometry';
import fs from 'node:fs';
const pack = g => ({position:Array.from(g.attributes.position.array),color:Array.from(g.attributes.color.array),index:g.index ? Array.from(g.index.array):null});
const result = {};
for (const k of ['bench','picnic_table','backless_bench','bike_rack','bin','light','planter']) result[k]={body:pack(createMeadowFurniture(k))};
for (const k of ['shade_tree','grove_tree','ornamental_tree','silver_shrub','meadow_grass','flowering_perennial']) result[k]=Object.fromEntries(Object.entries(createMeadowVegetation(k,17)).map(([n,g])=>[n,pack(g)]));
fs.writeFileSync(process.argv[2],JSON.stringify(result),{flag:'wx'});
`;
esbuild.buildSync({stdin:{contents:source,resolveDir:root,loader:'ts'},bundle:true,platform:'node',outfile:path.join(out,'export-kit.cjs')});
require('node:child_process').execFileSync(process.execPath,[path.join(out,'export-kit.cjs'),geometryFile],{stdio:'inherit'});
console.log('Exported 13 runtime kit prototypes to '+geometryFile);
