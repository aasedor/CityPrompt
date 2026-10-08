// Export the current app's small landscape geometry, without inventing replacement meshes.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
if (!process.argv[2]) throw new Error('Provide a fresh external output directory');
const out = path.resolve(process.argv[2]);
fs.mkdirSync(out, { recursive: true });
const target = path.join(out, 'kit.json');
if (fs.existsSync(target)) throw new Error('Use a fresh output directory');
const esbuild = require(path.join(root, 'frontend/node_modules/esbuild'));
const source = `
import { createMeadowFurniture } from './frontend/src/components/viewer/globe/meadowFurnitureGeometry';
import { createTreeWellGeometry } from './frontend/src/components/viewer/globe/treeWellGeometry';
import { createPublicRealmPlant } from './frontend/src/components/viewer/globe/publicRealmPlantGeometry';
import { createMeadowPatch } from './frontend/src/components/viewer/globe/parkPlantingGeometry';
import fs from 'node:fs';
const pack = g => ({body:{position:Array.from(g.attributes.position.array),color:Array.from(g.attributes.color.array),index:g.index ? Array.from(g.index.array):null}});
const data = {};
for (const k of ['backless_bench','picnic_table']) data[k] = pack(createMeadowFurniture(k));
for (const k of ['planted','guarded']) data['tree_well_'+k] = pack(createTreeWellGeometry(k));
for (const k of ['shrub','grass','perennial']) data['compact_'+k] = pack(createPublicRealmPlant(k));
data.meadow_patch = pack(createMeadowPatch());
fs.writeFileSync(process.argv[2],JSON.stringify(data),{flag:'wx'});
`;
const bundle = path.join(out, 'export.cjs');
esbuild.buildSync({stdin:{contents:source,resolveDir:root,loader:'ts'},bundle:true,platform:'node',outfile:bundle});
require('node:child_process').execFileSync(process.execPath,[bundle,target],{stdio:'inherit'});
