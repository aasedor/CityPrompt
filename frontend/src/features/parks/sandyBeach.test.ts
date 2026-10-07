// Like streetVisualContracts.test.ts, this asset check runs in Vitest/Node;
// the browser-only production tsconfig intentionally omits @types/node.
// @ts-expect-error -- available in the Vitest runtime without @types/node.
import { readFileSync } from 'node:fs';
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
    const data = readFileSync(resolve('..', layout.assets.assembly!.archivePath));
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
