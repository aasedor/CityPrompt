import { beforeEach, describe, expect, it, vi } from 'vitest';
import { Group } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

function payload(document: object) {
  const json = new TextEncoder().encode(JSON.stringify(document));
  const bytes = new Uint8Array(20 + json.length);
  const view = new DataView(bytes.buffer);
  view.setUint32(0, 0x46546c67, true);
  view.setUint32(12, json.length, true);
  bytes.set(json, 20);
  return bytes.buffer;
}
const assetFor = async (bytes: ArrayBuffer) => ({ url: '/native-park-assets/test.glb', sha256: Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('') });
function suspension(read: () => unknown): Promise<unknown> {
  try { read(); } catch (value) { if (value instanceof Promise) return value; throw value; }
  throw new Error('Expected pending asset');
}

describe('verified park loading', () => {
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
    const { verifiedScene } = await import('./nativeParkAssets');
    const valid = await assetFor(bytes), corrupt = { ...valid, sha256: '0'.repeat(64) };
    await suspension(() => verifiedScene(corrupt));
    expect(() => verifiedScene(corrupt)).toThrow('saved revision');
    await suspension(() => verifiedScene(valid));
    expect(() => verifiedScene(valid)).toThrow('external assets');
    expect(parse).not.toHaveBeenCalled();
  });
  it('starts dependencies concurrently and permits explicit recovery after a failed load', async () => {
    const a = payload({ asset: { version: '2.0' } }), b = payload({ asset: { version: '2.0', generator: 'second' } });
    const first = await assetFor(a), second = { ...await assetFor(b), url: '/second.glb' };
    const fetch = vi.fn().mockResolvedValue({ ok: false });
    vi.stubGlobal('fetch', fetch);
    vi.spyOn(GLTFLoader.prototype, 'parseAsync').mockResolvedValue({ scene: new Group() } as never);
    const { verifyParkAssets, verifiedScene, clearFailedNativeParkLoads } = await import('./nativeParkAssets');
    const pending = suspension(() => verifyParkAssets([first, second]));
    expect(fetch).toHaveBeenCalledTimes(2);
    await pending;
    expect(() => verifyParkAssets([first, second])).toThrow('could not be loaded');
    fetch.mockImplementation(async (url: string) => ({ ok: true, arrayBuffer: async () => url === first.url ? a : b }));
    clearFailedNativeParkLoads();
    await suspension(() => verifyParkAssets([first, second]));
    expect(() => verifyParkAssets([first, second])).not.toThrow();
    expect(verifiedScene(first)).toBeInstanceOf(Group);
    expect(fetch).toHaveBeenCalledTimes(4);
  });
  it('explains an interrupted download and recovers on retry', async () => {
    const bytes = payload({ asset: { version: '2.0' } });
    const asset = await assetFor(bytes);
    const interrupted = Object.assign(new Error('The user aborted a request.'), { name: 'AbortError' });
    vi.stubGlobal('fetch', vi.fn().mockRejectedValueOnce(interrupted).mockResolvedValue({ ok: true, arrayBuffer: async () => bytes }));
    vi.spyOn(GLTFLoader.prototype, 'parseAsync').mockResolvedValue({ scene: new Group() } as never);
    const { verifiedScene, clearFailedNativeParkLoads } = await import('./nativeParkAssets');
    await suspension(() => verifiedScene(asset));
    expect(() => verifiedScene(asset)).toThrow('download was interrupted');
    clearFailedNativeParkLoads();
    await suspension(() => verifiedScene(asset));
    expect(verifiedScene(asset)).toBeInstanceOf(Group);
  });
});
