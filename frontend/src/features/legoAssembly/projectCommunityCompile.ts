import {
  legoAssemblyApi,
  type Community3DCompileResponse,
} from './legoAssemblyApi';

type CommunityCompileItems = Parameters<typeof legoAssemblyApi.compileCommunity>[0];

interface ProjectCompileInFlight {
  requestFingerprint: string;
  promise: Promise<Community3DCompileResponse>;
}

interface RecentProjectCompile {
  requestFingerprint: string;
  completedAt: number;
  response: Community3DCompileResponse;
}

interface BrowserLockManager {
  request<T>(name: string, callback: () => Promise<T>): Promise<T>;
}

const RECENT_SUCCESS_TTL_MS = 60_000;
const STORAGE_KEY_PREFIX = 'siteforge:community-3d-compile:v1:';
const projectCompiles = new Map<string, ProjectCompileInFlight>();
const touchedStorageKeys = new Set<string>();

function canonicalizeJson(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonicalizeJson);
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .filter(([, nested]) => nested !== undefined)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, nested]) => [key, canonicalizeJson(nested)]),
    );
  }
  return value;
}

function requestFingerprint(
  items: CommunityCompileItems,
  scopeZoneIds?: string[],
  scopeBoundaryId?: string,
): string {
  const canonicalItems = items
    .map((item) => canonicalizeJson(item))
    .sort((left, right) => (
      JSON.stringify(left).localeCompare(JSON.stringify(right))
    ));
  return JSON.stringify({
    items: canonicalItems,
    scope_zone_ids: scopeZoneIds === undefined
      ? null
      : Array.from(new Set(scopeZoneIds)).sort((left, right) => left.localeCompare(right)),
    scope_boundary_id: scopeBoundaryId ?? null,
  });
}

function storageKey(projectId: string): string {
  const key = `${STORAGE_KEY_PREFIX}${encodeURIComponent(projectId)}`;
  touchedStorageKeys.add(key);
  return key;
}

function readRecentCompile(projectId: string): RecentProjectCompile | null {
  if (typeof window === 'undefined') return null;
  const key = storageKey(projectId);
  try {
    const value = window.localStorage.getItem(key);
    if (!value) return null;
    const parsed = JSON.parse(value) as Partial<RecentProjectCompile>;
    if (
      typeof parsed.requestFingerprint !== 'string'
      || typeof parsed.completedAt !== 'number'
      || parsed.response?.status !== 'compiled'
    ) {
      window.localStorage.removeItem(key);
      return null;
    }
    if (Date.now() - parsed.completedAt > RECENT_SUCCESS_TTL_MS) {
      window.localStorage.removeItem(key);
      return null;
    }
    return parsed as RecentProjectCompile;
  } catch {
    return null;
  }
}

function writeRecentCompile(
  projectId: string,
  recent: RecentProjectCompile,
): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(storageKey(projectId), JSON.stringify(recent));
  } catch {
    // Coordination still works within this tab when storage is unavailable.
  }
}

function browserLockManager(): BrowserLockManager | undefined {
  if (typeof navigator === 'undefined') return undefined;
  return (navigator as Navigator & { locks?: BrowserLockManager }).locks;
}

async function withProjectBrowserLock<T>(
  projectId: string,
  callback: () => Promise<T>,
): Promise<T> {
  const locks = browserLockManager();
  if (!locks) return callback();
  return locks.request(`siteforge:community-3d:${projectId}`, callback);
}

/**
 * Serialize Community 3D writes for one project and make repeated submissions
 * from another mounted panel or browser tab idempotent. The source revisions
 * are the backend's optimistic-concurrency identity: once one request commits,
 * an identical snapshot must reuse that success instead of POSTing stale
 * revisions and surfacing a misleading 409. Request identity includes the
 * recipes and exact visible/boundary scope because those fields change the
 * persisted 3D result even when the source zone revisions are unchanged.
 *
 * A real rebuild remains available after project queries refetch because the
 * server advances each zone's `updated_at`, producing a new fingerprint.
 */
export function compileProjectCommunity3D(
  projectId: string,
  items: CommunityCompileItems,
  scopeZoneIds?: string[],
  scopeBoundaryId?: string,
): Promise<Community3DCompileResponse> {
  const fingerprint = requestFingerprint(items, scopeZoneIds, scopeBoundaryId);
  const active = projectCompiles.get(projectId);
  if (active?.requestFingerprint === fingerprint) return active.promise;

  const promise = (async () => {
    if (active) {
      try {
        await active.promise;
      } catch {
        // A failed transaction saved nothing, so the queued request may retry.
      }
    }

    return withProjectBrowserLock(projectId, async () => {
      const recent = readRecentCompile(projectId);
      if (recent?.requestFingerprint === fingerprint) return recent.response;

      const response = scopeBoundaryId
        ? await legoAssemblyApi.compileCommunity(items, scopeZoneIds, scopeBoundaryId)
        : scopeZoneIds
          ? await legoAssemblyApi.compileCommunity(items, scopeZoneIds)
          : await legoAssemblyApi.compileCommunity(items);
      writeRecentCompile(projectId, {
        requestFingerprint: fingerprint,
        completedAt: Date.now(),
        response,
      });
      return response;
    });
  })();

  const entry = { requestFingerprint: fingerprint, promise };
  projectCompiles.set(projectId, entry);
  void promise.then(
    () => {
      if (projectCompiles.get(projectId) === entry) projectCompiles.delete(projectId);
    },
    () => {
      if (projectCompiles.get(projectId) === entry) projectCompiles.delete(projectId);
    },
  );
  return promise;
}

export function resetProjectCommunityCompileCoordinatorForTests(): void {
  projectCompiles.clear();
  if (typeof window !== 'undefined') {
    for (const key of touchedStorageKeys) {
      try {
        window.localStorage.removeItem(key);
      } catch {
        // Ignore storage restrictions in tests, matching runtime fallback.
      }
    }
  }
  touchedStorageKeys.clear();
}
