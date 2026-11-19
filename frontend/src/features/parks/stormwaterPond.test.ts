// Like sandyBeach.test.ts, this asset check runs in Vitest/Node;
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

describe('delivered stormwater pond walking surfaces', () => {
  it('walks the entrance, loop, meadow, bank and dock but never the water', async () => {
    const layout = nativeParkLayouts.find(p => p.variantId === 'student_stormwater_pond_v1')!;
    expect(layout).toBeDefined();
    expect([layout.widthM, layout.depthM]).toEqual([86, 68]);
    const assembly = layout.assets.assembly!;
    const gitDirectory = execFileSync('git', ['rev-parse', '--git-common-dir'], { encoding: 'utf8' }).trim();
    const paths = [resolve('public', assembly.url.slice(1)), resolve('..', assembly.archivePath),
      resolve(gitDirectory, 'lfs', 'objects', assembly.sha256.slice(0, 2), assembly.sha256.slice(2, 4), assembly.sha256)];
    const data = paths.filter(path => existsSync(path)).map(path => readFileSync(path))
      .find(bytes => createHash('sha256').update(bytes).digest('hex') === assembly.sha256);
    expect(data, `Hydrate the exact stormwater pond GLB ${assembly.sha256} with git lfs fetch`).toBeDefined();
    const buffer = new ArrayBuffer(data.byteLength);
    new Uint8Array(buffer).set(data);
    const gltf = await new GLTFLoader().parseAsync(buffer, '');
    const network = measuredParkWalking(layout, gltf.scene)!;
    expect(network).not.toBeNull();
    expect(parkWalkHeight(network, 0, -33.4)).toBeCloseTo(.015, 2);      // entrance spur
    expect(parkWalkHeight(network, -.56, -22.11)).toBeCloseTo(.02, 2);   // asphalt loop, south
    expect(parkWalkHeight(network, -.62, 26.86)).toBeCloseTo(.02, 2);    // asphalt loop, north
    expect(parkWalkHeight(network, 0, -8)).toBeCloseTo(.17, 2);          // timber dock over the water
    expect(parkWalkHeight(network, -1.03, 21.83)).toBeCloseTo(0, 2);     // meadow
    expect(parkWalkHeight(network, 0, 3)).toBeNull();                    // the middle of the pond
    expect(parkWalkHeight(network, 50, 0)).toBeNull();                   // outside the park
  });
});
