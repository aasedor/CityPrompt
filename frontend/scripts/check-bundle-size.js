#!/usr/bin/env node
/**
 * Performance budget checker for CI/CD pipelines.
 *
 * Regression budgets measured from the 2026-08 clean-release build:
 * - Initial app shell: < 600 KiB
 * - Total JS bundle: < 8.25 MiB
 * - Largest individual chunk: < 3.5 MiB
 * - Total CSS: < 175 KiB
 *
 * Route checks also keep 3D, Mapbox, and catalogue code out of the app shell,
 * and keep Mapbox out of the default 3D project route.
 *
 * Run after `npm run build`:
 *   node scripts/check-bundle-size.js
 */

import { readFileSync, readdirSync, statSync } from 'fs';
import { join, extname } from 'path';

const DIST_DIR = join(process.cwd(), 'dist', 'assets');
const MANIFEST_PATH = join(process.cwd(), 'dist', '.vite', 'manifest.json');

const BUDGETS = {
  initialJs: 600 * 1024,
  totalJs: 8.25 * 1024 * 1024,
  maxChunkJs: 3.5 * 1024 * 1024,
  totalCss: 175 * 1024,
};

function getFiles(dir) {
  try {
    return readdirSync(dir).map((f) => ({
      name: f,
      path: join(dir, f),
      size: statSync(join(dir, f)).size,
      ext: extname(f),
    }));
  } catch {
    console.error(`Build directory not found: ${dir}`);
    console.error('Run "npm run build" first.');
    process.exit(1);
  }
}

const files = getFiles(DIST_DIR);
const jsFiles = files.filter((f) => f.ext === '.js');
const cssFiles = files.filter((f) => f.ext === '.css');
const fileSizeByOutput = new Map(files.map((file) => [`assets/${file.name}`, file.size]));

let manifest;
try {
  manifest = JSON.parse(readFileSync(MANIFEST_PATH, 'utf8'));
} catch {
  console.error(`Build manifest not found: ${MANIFEST_PATH}`);
  console.error('Run "npm run build" first.');
  process.exit(1);
}

function collectStaticOutputs(entryKey) {
  const outputs = new Set();
  const visited = new Set();
  const visit = (key) => {
    if (!key || visited.has(key)) return;
    visited.add(key);
    const entry = manifest[key];
    if (!entry) return;
    if (entry.file?.endsWith('.js')) outputs.add(entry.file);
    for (const dependency of entry.imports ?? []) visit(dependency);
  };
  visit(entryKey);
  return outputs;
}

const initialOutputs = collectStaticOutputs('index.html');
const initialJs = [...initialOutputs].reduce((sum, output) => sum + (fileSizeByOutput.get(output) ?? 0), 0);
const projectEntryKey = Object.keys(manifest).find((key) => (
  key.endsWith('/ProjectViewPage.tsx') || manifest[key]?.name === 'ProjectViewPage'
));
const projectOutputs = collectStaticOutputs(projectEntryKey);
const forbiddenShellChunks = [...initialOutputs].filter((output) => /\/(?:three|react-three|mapbox|aestheticCatalog)-/.test(output));
const projectMapboxChunks = [...projectOutputs].filter((output) => /\/mapbox-/.test(output));

const totalJs = jsFiles.reduce((sum, f) => sum + f.size, 0);
const totalCss = cssFiles.reduce((sum, f) => sum + f.size, 0);
const largestChunk = jsFiles.reduce((max, f) => (f.size > max.size ? f : max), { size: 0, name: '' });

const fmt = (bytes) => `${(bytes / 1024).toFixed(1)}KB`;

console.log('\n📦 Bundle Size Report');
console.log('─'.repeat(50));
console.log(`Initial JS:     ${fmt(initialJs)} / ${fmt(BUDGETS.initialJs)}`);
console.log(`Total JS:       ${fmt(totalJs)} / ${fmt(BUDGETS.totalJs)}`);
console.log(`Largest chunk:  ${fmt(largestChunk.size)} (${largestChunk.name}) / ${fmt(BUDGETS.maxChunkJs)}`);
console.log(`Total CSS:      ${fmt(totalCss)} / ${fmt(BUDGETS.totalCss)}`);
console.log('─'.repeat(50));

jsFiles
  .sort((a, b) => b.size - a.size)
  .slice(0, 5)
  .forEach((f) => console.log(`  ${f.name}: ${fmt(f.size)}`));

let failed = false;
if (initialJs > BUDGETS.initialJs) {
  console.error(`\n❌ OVER BUDGET: Initial JS ${fmt(initialJs)} exceeds ${fmt(BUDGETS.initialJs)}`);
  failed = true;
}
if (forbiddenShellChunks.length > 0) {
  console.error(`\n❌ ROUTE BLOAT: App shell eagerly imports ${forbiddenShellChunks.join(', ')}`);
  failed = true;
}
if (!projectEntryKey) {
  console.error('\n❌ ROUTE BLOAT: ProjectViewPage is missing from the build manifest');
  failed = true;
} else if (projectMapboxChunks.length > 0) {
  console.error(`\n❌ ROUTE BLOAT: Default project route eagerly imports ${projectMapboxChunks.join(', ')}`);
  failed = true;
}
if (totalJs > BUDGETS.totalJs) {
  console.error(`\n❌ OVER BUDGET: Total JS ${fmt(totalJs)} exceeds ${fmt(BUDGETS.totalJs)}`);
  failed = true;
}
if (largestChunk.size > BUDGETS.maxChunkJs) {
  console.error(`\n❌ OVER BUDGET: Chunk ${largestChunk.name} (${fmt(largestChunk.size)}) exceeds ${fmt(BUDGETS.maxChunkJs)}`);
  failed = true;
}
if (totalCss > BUDGETS.totalCss) {
  console.error(`\n❌ OVER BUDGET: Total CSS ${fmt(totalCss)} exceeds ${fmt(BUDGETS.totalCss)}`);
  failed = true;
}

if (failed) {
  process.exit(1);
} else {
  console.log('\n✅ All performance budgets met!');
}
