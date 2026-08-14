import {
  legoAssemblyApi,
  type Community3DCompileResponse,
} from './legoAssemblyApi';

type CommunityCompileItems = Parameters<typeof legoAssemblyApi.compileCommunity>[0];

interface ProjectCompileInFlight {
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
const projectCompiles = new Map<string, Map<string, ProjectCompileInFlight>>();
const projectCompileTails = new Map<string, Promise<void>>();
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
      ? { state: 'omitted' }
      : {
          state: 'provided',
          value: Array.from(new Set(scopeZoneIds)).sort((left, right) => left.localeCompare(right)),
        },
    scope_boundary_id: scopeBoundaryId === undefined
      ? { state: 'omitted' }
      : { state: 'provided', value: scopeBoundaryId },
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
  const inFlight = projectCompiles.get(projectId) ?? new Map<string, ProjectCompileInFlight>();
  const duplicate = inFlight.get(fingerprint);
  if (duplicate) return duplicate.promise;

  const previousTail = projectCompileTails.get(projectId);

  const execute = () => {
    // Different requests for one project must run in submission order. Keep
    // every fingerprint in the in-flight registry while they wait so an A/B/A
    // burst joins the first A instead of losing it behind B and posting a
    // guaranteed-stale third transaction.
    return withProjectBrowserLock(projectId, async () => {
      const recent = readRecentCompile(projectId);
      if (recent?.requestFingerprint === fingerprint) return recent.response;

      const response = scopeBoundaryId !== undefined
        ? await legoAssemblyApi.compileCommunity(items, scopeZoneIds, scopeBoundaryId)
        : scopeZoneIds !== undefined
          ? await legoAssemblyApi.compileCommunity(items, scopeZoneIds)
          : await legoAssemblyApi.compileCommunity(items);
      writeRecentCompile(projectId, {
        requestFingerprint: fingerprint,
        completedAt: Date.now(),
        response,
      });
      return response;
    });
  };
  const promise = previousTail ? previousTail.then(execute) : execute();

  const entry = { promise };
  inFlight.set(fingerprint, entry);
  projectCompiles.set(projectId, inFlight);
  const settledTail = promise.then(
    () => undefined,
    () => undefined,
  );
  projectCompileTails.set(projectId, settledTail);
  void promise.then(
    () => {
      const current = projectCompiles.get(projectId);
      if (current?.get(fingerprint) === entry) current.delete(fingerprint);
      if (current?.size === 0) projectCompiles.delete(projectId);
      if (projectCompileTails.get(projectId) === settledTail) projectCompileTails.delete(projectId);
    },
    () => {
      const current = projectCompiles.get(projectId);
      if (current?.get(fingerprint) === entry) current.delete(fingerprint);
      if (current?.size === 0) projectCompiles.delete(projectId);
      if (projectCompileTails.get(projectId) === settledTail) projectCompileTails.delete(projectId);
    },
  );
  return promise;
}

export function resetProjectCommunityCompileCoordinatorForTests(): void {
  projectCompiles.clear();
  projectCompileTails.clear();
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
