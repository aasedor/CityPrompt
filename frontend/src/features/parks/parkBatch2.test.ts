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
  { variant: 'student_community_ball_diamond_v1', size: [88, 88], probes: [
    [-14, -43.4, .01, 'entrance spur'], [-38, -30, .01, 'concrete apron by the bleachers'], [-20, -10, 0, 'infield grass'],
    [-15.087, -15.087, .15, "top of the pitcher's mound"], [10, 10, 0, 'outfield'], [60, 0, null, 'outside the park']] },
  { variant: 'student_community_track_field_v1', size: [200, 112], probes: [
    [0, -55.5, .01, 'entrance spur'], [0, -50.02, .01, 'walking loop'], [0, -39.5, .01, 'lane three of the home straight'],
    [0, 0, 0, 'soccer pitch'], [0, -45.6, -.02, 'long jump sand pit'], [0, 70, null, 'outside the park']] },
  { variant: 'student_village_green_cricket_v1', size: [120, 120], probes: [
    [16, -59.5, .01, 'entrance path'], [0, -45.8, .02, 'pavilion terrace'], [0, 0, .003, 'the pitch'], [30, 20, 0, 'outfield'],
    [0, 44.4, 0, 'boundary walk'], [0, -53, null, 'inside the closed pavilion'], [70, 0, null, 'outside the park']] },
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

describe.each(parks)('park batch 2: $variant', ({ variant, size, probes }) => {
  it('is registered at its native size as a prepared-level pilot', () => {
    const layout = nativeParkLayouts.find(p => p.variantId === variant)!;
    expect(layout).toBeDefined();
    expect([layout.widthM, layout.depthM]).toEqual(size);
    expect(layout.terrainPolicy).toBe('prepared_level');
    expect(layout.status).toBe('pilot');
    expect(layout.runtimeStatus).toBe('not_tested');
  });

  it('walks its paths, fields and surfaces but never into a building or off the site', async () => {
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
