import { afterEach, expect, it, vi } from 'vitest';
import { readFixedSplat } from './fixedSplatAsset';
afterEach(() => vi.unstubAllGlobals());
it('rejects error responses and wrong lengths before decoding an archive', async () => {
  for (const response of [new Response('missing', { status: 404 }), new Response('wrong', { headers: { 'content-length': '5' } })]) {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response));
    await expect(readFixedSplat(new AbortController().signal)).rejects.toThrow('Unexpected');
  }
});
it('rejects truncated content even when its declared length matches', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(new Uint8Array(32), { headers: { 'content-length': '27830709' } })));
  await expect(readFixedSplat(new AbortController().signal)).rejects.toThrow('Incomplete');
});
