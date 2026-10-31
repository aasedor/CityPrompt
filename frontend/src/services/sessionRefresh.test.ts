import { expect, it, vi } from 'vitest';
import { createSessionRefreshCoordinator, type SessionTokens } from './sessionRefresh';

function refreshToken(subject: string, session: string, nonce: string, version = 0) {
  return `header.${btoa(JSON.stringify({ type: 'refresh', sub: subject, sid: session, ver: version, jti: nonce }))}.signature`;
}

function sharedStorage(refresh: string) {
  const values = new Map([['access_token', 'expired-access'], ['refresh_token', refresh]]);
  return {
    getItem: (key: string) => values.get(key) ?? null,
    setItem: (key: string, value: string) => { values.set(key, value); },
  };
}

function exclusiveLock() {
  let tail = Promise.resolve();
  return (work: () => Promise<SessionTokens>) => {
    const previous = tail;
    let release!: () => void;
    tail = new Promise<void>(resolve => { release = resolve; });
    return previous.then(work).finally(() => { release(); });
  };
}

it('lets two tabs share one rotation by rereading shared credentials inside their lock', async () => {
  const old = refreshToken('student', 'browser-session', 'old');
  const fresh = { access_token: 'fresh-access', refresh_token: refreshToken('student', 'browser-session', 'new') };
  const storage = sharedStorage(old);
  const withLock = exclusiveLock();
  let consumed = false;
  const exchange = vi.fn(async (_token: string) => {
    await Promise.resolve();
    if (consumed) throw new Error('Refresh token replay');
    consumed = true;
    return fresh;
  });
  const firstTab = createSessionRefreshCoordinator({ storage: () => storage, exchange, withLock });
  const secondTab = createSessionRefreshCoordinator({ storage: () => storage, exchange, withLock });
  const outcomes = await Promise.allSettled([firstTab(old), secondTab(old)]);
  expect(outcomes).toEqual([
    { status: 'fulfilled', value: fresh },
    { status: 'fulfilled', value: fresh },
  ]);
  expect(exchange).toHaveBeenCalledExactlyOnceWith(old);
  expect(storage.getItem('refresh_token')).toBe(fresh.refresh_token);
});

it.each([
  ['other-account', 'browser-session', 0],
  ['student', 'different-sign-in', 0],
  ['student', 'browser-session', 1],
] as const)('does not adopt an unrelated session while waiting for the lock (%s/%s/%s)', async (subject, session, version) => {
  const old = refreshToken('student', 'browser-session', 'old');
  const storage = sharedStorage(old);
  let release!: () => void;
  const wait = new Promise<void>(resolve => { release = resolve; });
  const withLock = (work: () => Promise<SessionTokens>) => wait.then(work);
  const exchange = vi.fn(async () => ({ access_token: 'wrong-access', refresh_token: 'wrong-refresh' }));
  const refresh = createSessionRefreshCoordinator({ storage: () => storage, exchange, withLock });
  const pending = refresh(old);
  const replacement = refreshToken(subject, session, 'replacement', version);
  storage.setItem('refresh_token', replacement);
  storage.setItem('access_token', 'replacement-access');
  release();
  await expect(pending).rejects.toThrow('session changed');
  expect(exchange).not.toHaveBeenCalled();
  expect(storage.getItem('access_token')).toBe('replacement-access');
  expect(storage.getItem('refresh_token')).toBe(replacement);
});

it('retains same-tab coalescing without Web Locks support', async () => {
  const old = refreshToken('student', 'session', 'old');
  const storage = sharedStorage(old);
  const next = { access_token: 'fresh-access', refresh_token: refreshToken('student', 'session', 'next') };
  const exchange = vi.fn(async () => next);
  const refresh = createSessionRefreshCoordinator({ storage: () => storage, exchange });
  expect(await Promise.all([refresh(old), refresh(old), refresh(old)])).toEqual([next, next, next]);
  expect(exchange).toHaveBeenCalledOnce();
});
