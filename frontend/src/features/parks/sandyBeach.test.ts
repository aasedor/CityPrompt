// Like streetVisualContracts.test.ts, this asset check runs in Vitest/Node;
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
import registry from '@/data/nativeParks.json';
import { nativeParkLayouts } from './nativeParkRegistry';
import { measuredParkWalking } from './measuredParkWalking';
import { parkWalkHeight } from './parkWalking';

describe('delivered sandy beach walking surfaces', () => {
  it.each([nativeParkLayouts.find(p => p.variantId === 'student_sandy_beach_v1')!, ...registry.archivedLayouts])('supports dry entry and sand for saved revision $contentRevision', async (layout) => {
    const assembly = layout.assets.assembly!;
    const gitDirectory = execFileSync('git', ['rev-parse', '--git-common-dir'], { encoding: 'utf8' }).trim();
    // Archived revisions can share a source path with the current version.
    // Resolve exact bytes from the packaged asset or Git LFS cache, never a sibling revision.
    const paths = [resolve('public', assembly.url.slice(1)), resolve('..', assembly.archivePath),
      resolve(gitDirectory, 'lfs', 'objects', assembly.sha256.slice(0, 2), assembly.sha256.slice(2, 4), assembly.sha256)];
    const data = paths.filter(path => existsSync(path)).map(path => readFileSync(path))
      .find(bytes => createHash('sha256').update(bytes).digest('hex') === assembly.sha256);
    expect(data, `Hydrate the exact sandy beach GLB ${assembly.sha256} with git lfs fetch`).toBeDefined();
    const buffer = new ArrayBuffer(data.byteLength);
    new Uint8Array(buffer).set(data);
    const gltf = await new GLTFLoader().parseAsync(buffer, '');
    const network = measuredParkWalking(layout, gltf.scene)!;
    expect(network).not.toBeNull();
    expect(parkWalkHeight(network, 0, -23.4)).toBeCloseTo(.012, 2);
    expect(parkWalkHeight(network, -7, -9)).toBeCloseTo(.012, 2);
    expect(parkWalkHeight(network, 0, -7)).not.toBeNull();
    expect(parkWalkHeight(network, 0, 10)).toBeNull();
    expect(parkWalkHeight(network, 14, 10)).toBeNull();
    expect(parkWalkHeight(network, 24, 0)).toBeNull();
  });
});
