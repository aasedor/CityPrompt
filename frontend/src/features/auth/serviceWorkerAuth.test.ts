import { expect, it, vi } from 'vitest';

async function worker() {
  const { readFileSync } = await vi.importActual<{ readFileSync: (path: string, encoding: string) => string }>('node:fs');
  const vm = await vi.importActual<{ runInNewContext: (source: string, context: Record<string, unknown>) => void }>('node:vm');
  const listeners = new Map<string, (event: any) => void>();
  const cache = { put: vi.fn(), addAll: vi.fn() };
  const caches = { keys: vi.fn(async () => ['siteforge-v1']), delete: vi.fn(async () => true),
    match: vi.fn(async () => undefined), open: vi.fn(async () => cache) };
  const fetch = vi.fn(async () => ({ ok: true, clone: () => ({}) }));
  vm.runInNewContext(readFileSync('public/sw.js', 'utf8'), {
    URL, Promise, caches, fetch, self: { addEventListener: (name: string, callback: (event: any) => void) => listeners.set(name, callback), clients: { claim: vi.fn() }, skipWaiting: vi.fn() },
  });
  return { listeners, cache, caches, fetch };
}

it.each(['/oauth/callback?code=opaque', '/oauth/callback?access_token=legacy', '/reset-password?token=reset'])(
  'never stores sensitive navigation %s in the offline cache', async path => {
    const { listeners, cache, fetch } = await worker();
    let response: Promise<unknown> | undefined;
    listeners.get('fetch')!({ request: { method: 'GET', url: 'https://class.example' + path },
      respondWith: (value: Promise<unknown>) => { response = value; } });
    await response;
    expect(fetch).toHaveBeenCalled();
    expect(cache.put).not.toHaveBeenCalled();
  },
);

it('retires the old worker cache containing legacy callback request keys', async () => {
  const { listeners, caches } = await worker();
  let activation: Promise<unknown> | undefined;
  listeners.get('activate')!({ waitUntil: (value: Promise<unknown>) => { activation = value; } });
  await activation;
  expect(caches.delete).toHaveBeenCalledWith('siteforge-v1');
});

it('continues caching ordinary static assets', async () => {
  const { listeners, cache } = await worker();
  let response: Promise<unknown> | undefined;
  listeners.get('fetch')!({ request: { method: 'GET', url: 'https://class.example/assets/app.js' },
    respondWith: (value: Promise<unknown>) => { response = value; } });
  await response;
  expect(cache.put).toHaveBeenCalledOnce();
});
