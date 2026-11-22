// Like stormwaterPond.test.ts, this asset check runs in Vitest/Node;
// the browser-only production tsconfig intentionally omits @types/node.
// @ts-expect-error -- available in the Vitest runtime without @types/node.
import { existsSync, readFileSync } from 'node:fs';
// @ts-expect-error -- available in the Vitest runtime without @types/node.
import { execFileSync } from 'node:child_process';
// @ts-expect-error -- available in the Vitest runtime without @types/node.
import { createHash } from 'node:crypto';
// @ts-expect-error -- available in the Vitest runtime without @types/node.
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { nativeParkLayouts } from './nativeParkRegistry';
import { measuredParkWalking } from './measuredParkWalking';
import { parkWalkHeight } from './parkWalking';

type Probe = [x: number, y: number, height: number | null, what: string];
const parks: Array<{ variant: string; size: [number, number]; probes: Probe[] }> = [
  { variant: 'student_calgary_prairie_plaza_v1', size: [64, 52], probes: [
    [0, -25.5, 0, 'entrance'], [2, -1, 0, 'sandstone circle'], [0, 8.8, 0, 'ring walk'], [0, 11.2, .04, 'pool coping'],
    [0, 14, null, 'reflecting pool'], [24, 0, 0, 'market strip'], [40, 0, null, 'outside the park']] },
  { variant: 'student_clover_neighbourhood_park_v1', size: [84, 68], probes: [
    [4, -33.5, .01, 'entrance path'], [0, -12.4, .01, 'ring walk'], [0, 3, 0, 'open lawn'], [29.5, -8, .03, 'playground surfacing'],
    [-19, 11, .01, 'picnic pad'], [50, 0, null, 'outside the park']] },
  { variant: 'student_prairie_sports_complex_v1', size: [216, 168], probes: [
    [0, -83.5, .01, 'entrance spine'], [-60, -7, .01, 'promenade'], [55, -46, 0, 'soccer pitch'], [23, 19, 0, 'infield grass'],
    [27.913, 19.913, .15, "north-east pitcher's mound"], [-27.913, 19.913, .15, "north-west pitcher's mound"],
    [0, 49, null, 'inside the fieldhouse'], [130, 0, null, 'outside the park']] },
];

async function scene(variant: string) {
  const layout = nativeParkLayouts.find(p => p.variantId === variant)!;
  const assembly = layout.assets.assembly!;
  const gitDirectory = execFileSync('git', ['rev-parse', '--git-common-dir'], { encoding: 'utf8' }).trim();
  const paths = [resolve('public', assembly.url.slice(1)), resolve('..', assembly.archivePath),
    resolve(gitDirectory, 'lfs', 'objects', assembly.sha256.slice(0, 2), assembly.sha256.slice(2, 4), assembly.sha256)];
  const data = paths.filter(path => existsSync(path)).map(path => readFileSync(path))
    .find(bytes => createHash('sha256').update(bytes).digest('hex') === assembly.sha256);
  expect(data, `Hydrate the exact ${variant} GLB ${assembly.sha256} with git lfs fetch`).toBeDefined();
  const buffer = new ArrayBuffer(data.byteLength);
  new Uint8Array(buffer).set(data);
  return { layout, gltf: await new GLTFLoader().parseAsync(buffer, '') };
}

describe.each(parks)('park batch 3: $variant', ({ variant, size, probes }) => {
  it('is registered at its native size as a prepared-level pilot', () => {
    const layout = nativeParkLayouts.find(p => p.variantId === variant)!;
    expect(layout).toBeDefined();
    expect([layout.widthM, layout.depthM]).toEqual(size);
    expect(layout.terrainPolicy).toBe('prepared_level');
    expect(layout.status).toBe('pilot');
    expect(layout.runtimeStatus).toBe('not_tested');
  });

  it('walks its paths, fields and surfaces but never into a pool, a building or off the site', async () => {
    const { layout, gltf } = await scene(variant);
    const network = measuredParkWalking(layout, gltf.scene)!;
    expect(network).not.toBeNull();
    for (const [x, y, height, what] of probes) {
      const z = parkWalkHeight(network, x, y);
      if (height === null) expect(z, what).toBeNull();
      else expect(z, what).toBeCloseTo(height, 1);
    }
  });
});
