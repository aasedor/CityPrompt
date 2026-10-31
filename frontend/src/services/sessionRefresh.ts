export interface SessionTokens {
  access_token: string;
  refresh_token: string;
}

interface RefreshOptions {
  storage: () => Pick<Storage, 'getItem' | 'setItem'>;
  exchange: (refreshToken: string) => Promise<SessionTokens>;
  withLock?: (work: () => Promise<SessionTokens>) => Promise<SessionTokens>;
}

/** A busy/frozen tab must not force another tab to discard valid credentials. */
export class RefreshLockTimeoutError extends Error {}

function refreshIdentity(token: string): string | null {
  try {
    const encoded = token.split('.')[1]?.replace(/-/g, '+').replace(/_/g, '/');
    if (!encoded || token.length > 16384) return null;
    const payload = JSON.parse(atob(encoded.padEnd(Math.ceil(encoded.length / 4) * 4, '='))) as {
      sub?: unknown; sid?: unknown; ver?: unknown; type?: unknown;
    };
    if (payload.type !== 'refresh' || typeof payload.sub !== 'string' || !payload.sub
        || typeof payload.sid !== 'string' || !payload.sid
        || typeof payload.ver !== 'number' || !Number.isInteger(payload.ver)) return null;
    // Correlation only: protected API requests still validate their signatures.
    return JSON.stringify([payload.sub, payload.sid, payload.ver]);
  } catch {
    return null;
  }
}

/** Coalesce one tab's requests and serialize rotations across supporting tabs. */
export function createSessionRefreshCoordinator(options: RefreshOptions) {
  const pendingRequests = new Map<string, Promise<SessionTokens>>();
  return (refreshToken: string): Promise<SessionTokens> => {
    let pending = pendingRequests.get(refreshToken);
    if (!pending) {
      const rotate = async () => {
        const storage = options.storage();
        const currentRefresh = storage.getItem('refresh_token');
        if (currentRefresh !== refreshToken) {
          const identity = refreshIdentity(refreshToken);
          const access = storage.getItem('access_token');
          // The preceding tab may have already rotated this exact browser
          // session. Reuse its current access token instead of replaying ours.
          if (currentRefresh && access && identity && refreshIdentity(currentRefresh) === identity) {
            return { access_token: access, refresh_token: currentRefresh };
          }
          throw new Error('The sign-in session changed while refreshing.');
        }
        const data = await options.exchange(refreshToken);
        if (storage.getItem('refresh_token') !== refreshToken) {
          throw new Error('The sign-in session changed while refreshing.');
        }
        storage.setItem('access_token', data.access_token);
        storage.setItem('refresh_token', data.refresh_token);
        return data;
      };
      pending = (options.withLock ? options.withLock(rotate) : rotate())
        .finally(() => { pendingRequests.delete(refreshToken); });
      pendingRequests.set(refreshToken, pending);
    }
    return pending;
  };
}
