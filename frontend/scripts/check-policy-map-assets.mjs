import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const publicRoot = process.env.CITYPROMPT_PUBLIC_DIR || fileURLToPath(new URL('../public/', import.meta.url));
const root = path.join(publicRoot, 'policy-maps/citywide-2026-v1');
const ids = ['mdp-1', 'mdp-2', 'mdp-3', 'mdp-4', 'mdp-5', 'mdp-6', 'ctp-1', 'ctp-2', 'ctp-3', 'ctp-5', 'ctp-6', 'ctp-7'];
let assets = 0, bytes = 0;
for (const id of ids) {
  const directory = path.join(root, id);
  const map = JSON.parse(readFileSync(path.join(directory, 'map.json'), 'utf8'));
  if (map.id !== id || map.gridSize !== 4 || !map.tiles.length) throw Error(`Invalid policy map: ${id}`);
  for (const tile of map.tiles) {
    if (!/^r[0-7]-c[0-7]$/.test(tile.id) || tile.grid.length !== 25 || tile.grid.some(point => point.length !== 2 || point.some(value => !Number.isFinite(value)))) throw Error(`Invalid geographic tile: ${id}/${tile.id}`);
  }
  for (const file of ['overview.webp', 'legend.webp', ...map.tiles.map(tile => `${tile.id}.webp`)]) {
    const data = readFileSync(path.join(directory, file));
    if (data.toString('ascii', 0, 4) !== 'RIFF' || data.toString('ascii', 8, 12) !== 'WEBP') throw Error(`Policy map image unavailable: ${id}/${file}. Run git lfs pull before building.`);
    assets++; bytes += data.length;
  }
}
console.log(`Policy maps: ${ids.length} maps, ${assets} hydrated images, ${(bytes / 1048576).toFixed(1)} MiB on disk; loaded on demand.`);
