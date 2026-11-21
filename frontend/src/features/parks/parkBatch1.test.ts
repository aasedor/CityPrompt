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
  { variant: 'student_prairie_bowl_skate_park_v1', size: [64, 52], probes: [
    [0, -25.4, 0, 'entrance spur'], [18, 0, 0, 'street plaza'], [-12, -3, null, 'kidney bowl floor, 2.4 m down'],
    [5, 2.5, null, 'clover bowl floor'], [40, 0, null, 'outside the park']] },
  { variant: 'student_parkour_calisthenics_yard_v1', size: [44, 36], probes: [
    [6, -17.5, .01, 'entrance spur'], [-1, 1, .02, 'rubber movement floor'], [30, 0, null, 'outside the park']] },
  { variant: 'student_walled_memorial_garden_v1', size: [36, 50], probes: [
    [0, -24.5, .01, 'entrance path'], [0, -19, .01, 'gate threshold'], [0, -6.9, .01, 'pool terrace'],
    [-9.625, 0, .005, 'perimeter walk'], [0, 3, null, 'reflecting pool'], [30, 0, null, 'outside the park']] },
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

describe.each(parks)('park batch 1: $variant', ({ variant, size, probes }) => {
  it('is registered at its native size as a prepared-level pilot', () => {
    const layout = nativeParkLayouts.find(p => p.variantId === variant)!;
    expect(layout).toBeDefined();
    expect([layout.widthM, layout.depthM]).toEqual(size);
    expect(layout.terrainPolicy).toBe('prepared_level');
    expect(layout.status).toBe('pilot');
    expect(layout.runtimeStatus).toBe('not_tested');
  });

  it('walks its paths and floors but never into a bowl, a pool or off the site', async () => {
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
