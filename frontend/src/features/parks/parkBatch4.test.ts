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
  { variant: 'student_creekside_mini_golf_v1', size: [48, 40], probes: [
    [0, -19.5, .01, 'entrance path'], [0, -11.5, .01, 'south path'], [-19.2, 14.5, .02, 'first green'],
    [-12, 3.05, .245, 'footbridge deck'], [0, 2.6, null, 'creek'], [30, 0, null, 'outside the park']] },
  { variant: 'student_boulder_block_park_v1', size: [40, 32], probes: [
    [0, -15.5, 0, 'entrance paving'], [4.2, -5.6, .04, 'rubber fall zone'], [-15, 0, 0, 'paving beside the blocks'],
    [30, 0, null, 'outside the park']] },
  { variant: 'student_prairie_pollinator_meadow_v1', size: [48, 36], probes: [
    [0, -17.5, .01, 'entrance walk'], [0, 11.5, .01, 'gathering circle'], [17, -.5, .005, 'mown loop'], [10, -10, 0, 'meadow bed'],
    [30, 0, null, 'outside the park']] },
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

describe.each(parks)('park batch 4: $variant', ({ variant, size, probes }) => {
  it('is registered at its native size as a prepared-level pilot', () => {
    const layout = nativeParkLayouts.find(p => p.variantId === variant)!;
    expect(layout).toBeDefined();
    expect([layout.widthM, layout.depthM]).toEqual(size);
    expect(layout.terrainPolicy).toBe('prepared_level');
    expect(layout.status).toBe('pilot');
    expect(layout.runtimeStatus).toBe('not_tested');
  });

  it('walks its paths, greens and surfaces but never into the creek or off the site', async () => {
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
