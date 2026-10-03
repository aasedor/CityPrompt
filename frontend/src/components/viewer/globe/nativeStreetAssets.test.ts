import { beforeEach, describe, expect, it, vi } from 'vitest';
import { Group } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

function payload(document: object) {
  const json = new TextEncoder().encode(JSON.stringify(document));
  const bytes = new Uint8Array(20 + json.length);
  const view = new DataView(bytes.buffer);
  view.setUint32(0, 0x46546c67, true);
  view.setUint32(4, 2, true);
  view.setUint32(8, bytes.length, true);
  view.setUint32(16, 0x4e4f534a, true);
  view.setUint32(12, json.length, true);
  bytes.set(json, 20);
  return bytes.buffer;
}
const assetFor = async (bytes: ArrayBuffer) => ({ url: '/native-park-assets/test.glb', sha256: Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('') });
function suspension(read: () => unknown): Promise<unknown> {
  try { read(); } catch (value) { if (value instanceof Promise) return value; throw value; }
  throw new Error('Expected pending asset');
}

describe('verified street loading', () => {
  beforeEach(async () => {
    vi.resetModules();
    vi.restoreAllMocks();
    const { webcrypto }=await vi.importActual<{webcrypto:Crypto}>('node:crypto');
    vi.stubGlobal('crypto', webcrypto);
  });
  it('rejects corrupt bytes and unverified external dependencies before parsing', async () => {
    const parse = vi.spyOn(GLTFLoader.prototype, 'parseAsync');
    const bytes = payload({ buffers: [{ uri: 'untrusted.bin' }] });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, arrayBuffer: async () => bytes }));
    const { verifiedStreetScene } = await import('./nativeStreetAssets');
    const valid = await assetFor(bytes), corrupt = { ...valid, sha256: '0'.repeat(64) };
    await suspension(() => verifiedStreetScene(corrupt));
    expect(() => verifiedStreetScene(corrupt)).toThrow('saved revision');
    await suspension(() => verifiedStreetScene(valid));
    expect(() => verifiedStreetScene(valid)).toThrow('external assets');
    expect(parse).not.toHaveBeenCalled();
  });
  it('starts dependencies concurrently and permits explicit recovery after a failed load', async () => {
    const a = payload({ asset: { version: '2.0' } }), b = payload({ asset: { version: '2.0', generator: 'second' } });
    const first = await assetFor(a), second = { ...await assetFor(b), url: '/second.glb' };
    const fetch = vi.fn().mockResolvedValue({ ok: false });
    vi.stubGlobal('fetch', fetch);
    vi.spyOn(GLTFLoader.prototype, 'parseAsync').mockResolvedValue({ scene: new Group() } as never);
    const { verifyStreetAssets, verifiedStreetScene, clearFailedNativeStreetLoads } = await import('./nativeStreetAssets');
    const pending = suspension(() => verifyStreetAssets([first, second]));
    expect(fetch).toHaveBeenCalledTimes(2);
    await pending;
    expect(() => verifyStreetAssets([first, second])).toThrow('could not be loaded');
    fetch.mockImplementation(async (url: string) => ({ ok: true, arrayBuffer: async () => url === first.url ? a : b }));
    clearFailedNativeStreetLoads();
    await suspension(() => verifyStreetAssets([first, second]));
    expect(() => verifyStreetAssets([first, second])).not.toThrow();
    expect(verifiedStreetScene(first)).toBeInstanceOf(Group);
    expect(fetch).toHaveBeenCalledTimes(4);
  });
});
