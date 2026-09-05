export interface AssetContext { projectId?: string; shareToken?: string }
interface Ticket { value: string; expiresAt: number }
interface TicketResponse { expires_in: number; asset_ticket?: string; file_ticket?: string }
interface Options {
  baseUrl: string;
  origin: () => string;
  /** Stable account identity, not the rotating access-token bytes. */
  session: () => string | null;
  projectTicket: (id: string) => Promise<TicketResponse>;
  fileTicket: (path: string) => Promise<TicketResponse>;
}

/** Cache identity only. The server still authenticates every ticket request and
 * protected download; decoding a JWT here does not establish authorization. */
export function assetAccountIdentity(accessToken: string | null): string | null {
  if (!accessToken) return null;
  try {
    const parts = accessToken.split('.');
    if (parts.length !== 3) return null;
    const encoded = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const bytes = Uint8Array.from(atob(encoded.padEnd(Math.ceil(encoded.length / 4) * 4, '=')), (value) => value.charCodeAt(0));
    const payload = JSON.parse(new TextDecoder().decode(bytes)) as { sub?: unknown; type?: unknown };
    return payload.type === 'access' && typeof payload.sub === 'string' && payload.sub.trim()
      ? payload.sub : null;
  } catch { return null; }
}

/** Short-lived, scoped download credentials for image and GLTF elements. */
export function createAssetAccess(options: Options) {
  let session: string | null = null;
  let generation = 0;
  const tickets = new Map<string, Ticket>();
  const pending = new Map<string, Promise<void>>();
  const objectProjects = new Map<string, string>();
  const targets = new Map<string, NonNullable<ReturnType<typeof scope>>>();
  const listeners = new Set<() => void>();
  let revision = 0;
  const changed = () => { revision += 1; listeners.forEach((listener) => listener()); };
  const discardSession = () => {
    generation += 1;
    tickets.clear(); pending.clear(); objectProjects.clear(); targets.clear();
  };
  const clear = () => { discardSession(); session = null; changed(); };
  const refreshSession = () => {
    const next = options.session();
    if (next === session) return false;
    discardSession(); session = next;
    return true;
  };
  const ownUrl = (value: string): URL | null => {
    try {
      const base = options.baseUrl || options.origin();
      const url = new URL(value, base);
      if (url.origin !== new URL(base).origin && url.origin !== options.origin()) return null;
      return /^\/api\/v1\/(files\/|buildings\/[^/]+\/model\/file$|documents\/[^/]+\/file$)/.test(url.pathname) ? url : null;
    } catch { return null; }
  };
  const scope = (url: URL, context?: AssetContext) => {
    const encodedFile = url.pathname.match(/^\/api\/v1\/files\/(.+)$/)?.[1];
    let file: string | undefined;
    try { file = encodedFile ? decodeURIComponent(encodedFile) : undefined; } catch { return null; }
    if (file?.startsWith('archetype-cache/')) return null;
    const project = file?.match(/^projects\/([^/]+)\//)?.[1]
      || objectProjects.get(url.pathname.match(/^\/api\/v1\/(?:buildings|documents)\/([^/]+)/)?.[1] || '')
      || context?.projectId;
    if (file && !file.startsWith('projects/')) return { key: `file:${file}`, file };
    return project ? { key: `project:${project}`, project } : null;
  };
  const ensure = async (target: NonNullable<ReturnType<typeof scope>>) => {
    targets.set(target.key, target);
    const cached = tickets.get(target.key);
    if (cached && cached.expiresAt > Date.now() + 60_000) return;
    const existing = pending.get(target.key);
    if (existing) return existing;
    const expectedGeneration = generation;
    const request = (async () => {
      try {
        const result = target.project ? await options.projectTicket(target.project) : await options.fileTicket(target.file!);
        refreshSession();
        const value = result.asset_ticket || result.file_ticket;
        if (value && generation === expectedGeneration && session) {
          tickets.set(target.key, { value, expiresAt: Date.now() + result.expires_in * 1000 });
          changed();
        }
      } finally {
        // An old account's completion must not release the next account's
        // pending request for the same resource key.
        if (generation === expectedGeneration) pending.delete(target.key);
      }
    })();
    pending.set(target.key, request);
    return request;
  };
  const resolve = (value: string, context?: AssetContext): string => {
    if (!value) return value;
    refreshSession();
    const url = ownUrl(value);
    if (!url) {
      return value.startsWith('/api/') && options.baseUrl ? `${options.baseUrl.replace(/\/$/, '')}${value}` : value;
    }
    // A decorated URL from old query data is not a credential source. Only
    // the current account's cache may attach private download tickets.
    url.searchParams.delete('asset_ticket'); url.searchParams.delete('file_ticket');
    if (context?.shareToken) {
      // Public viewers receive only the presentation's revocable share token.
      url.searchParams.set('share_token', context.shareToken);
    } else if (!url.searchParams.has('share_token')) {
      const target = scope(url, context);
      if (target && session) targets.set(target.key, target);
      const ticket = target && tickets.get(target.key);
      if (ticket && ticket.expiresAt > Date.now()) {
        url.searchParams.set(target.project ? 'asset_ticket' : 'file_ticket', ticket.value);
      }
    }
    return options.baseUrl || /^https?:\/\//.test(value) ? url.href : `${url.pathname}${url.search}${url.hash}`;
  };
  const prepare = async <T>(data: T, context?: AssetContext): Promise<T> => {
    refreshSession();
    const scopes = new Map<string, NonNullable<ReturnType<typeof scope>>>();
    const collect = (value: unknown, inherited = context) => {
      if (typeof value === 'string') {
        const url = ownUrl(value);
        const target = url && scope(url, inherited);
        if (target && !url.searchParams.has('share_token')) scopes.set(target.key, target);
        return;
      }
      if (!value || typeof value !== 'object') return;
      if (Array.isArray(value)) { value.forEach((item) => collect(item, inherited)); return; }
      const record = value as Record<string, unknown>;
      const projectId = typeof record.project_id === 'string' ? record.project_id : inherited?.projectId;
      const local = { ...inherited, projectId };
      if (typeof record.id === 'string' && projectId) objectProjects.set(record.id, projectId);
      for (const item of Object.values(record)) {
        if (typeof item === 'string') {
          const url = ownUrl(item);
          const target = url && scope(url, local);
          if (target && !url.searchParams.has('share_token')) scopes.set(target.key, target);
        } else collect(item, local);
      }
    };
    collect(data);
    const expectedGeneration = generation;
    if (session && !context?.shareToken) {
      // Ticket failures must not hide an otherwise readable project. The
      // protected download still enforces access and can be retried on refetch.
      const queue = [...scopes.values()];
      await Promise.all(Array.from({ length: Math.min(6, queue.length) }, async () => {
        while (queue.length && generation === expectedGeneration) { const target = queue.shift()!; try { await ensure(target); } catch { /* leave URL protected */ } }
      }));
    }
    const decorate = (value: unknown, inherited = context): unknown => {
      if (typeof value === 'string') return ownUrl(value) ? resolve(value, inherited) : value;
      if (Array.isArray(value)) return value.map((item) => decorate(item, inherited));
      if (!value || typeof value !== 'object') return value;
      const record = value as Record<string, unknown>;
      const local = { ...inherited, projectId: typeof record.project_id === 'string' ? record.project_id : inherited?.projectId };
      return Object.fromEntries(Object.entries(record).map(([key, item]) => [key, decorate(item, local)]));
    };
    return decorate(data) as T;
  };
  const refresh = async () => {
    if (refreshSession()) changed();
    if (!session) return;
    const expectedGeneration = generation;
    const queue = [...targets.values()];
    await Promise.all(Array.from({ length: Math.min(6, queue.length) }, async () => {
      while (queue.length && generation === expectedGeneration) {
        const target = queue.shift()!;
        try { await ensure(target); } catch {
          if (generation === expectedGeneration && tickets.delete(target.key)) changed();
        }
      }
    }));
  };
  return { resolve, prepare, refresh, clear, getRevision: () => revision,
    subscribe: (listener: () => void) => { listeners.add(listener); return () => { listeners.delete(listener); }; },
  };
}
