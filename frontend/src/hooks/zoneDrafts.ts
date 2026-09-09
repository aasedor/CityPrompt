import { useCallback, useMemo, useSyncExternalStore } from 'react';
import { ZONE_TYPE_CONFIG, type SiteZone, type SiteZoneProperties, type SiteZoneType } from '@/types';

export interface ZoneDraft {
  requestId: string;
  coordinates: number[][];
  zoneType: SiteZoneType;
  properties?: SiteZoneProperties;
  createdAt: string;
  error?: string;
  /** Only identified create rejections prove that this attempt did not save. */
  rejectionStatus?: 400 | 409 | 422;
  rejectionReason?: 'outside_site_boundary' | 'boundary_excludes_zones';
}

export function isDiscardableDraft(draft: ZoneDraft): boolean {
  return draft.rejectionStatus === 400 || draft.rejectionStatus === 422
    || (draft.rejectionStatus === 409 && (draft.rejectionReason === 'outside_site_boundary' || draft.rejectionReason === 'boundary_excludes_zones'));
}

const CHANGE_EVENT = 'cityprompt:zone-drafts-changed';
const EMPTY = '[]';

export function parseZoneDrafts(raw: string): ZoneDraft[] {
  try {
    const value: unknown = JSON.parse(raw);
    if (!Array.isArray(value)) return [];
    return value.filter((item): item is ZoneDraft => Boolean(
      item && typeof item.requestId === 'string' && typeof item.createdAt === 'string'
      && Object.prototype.hasOwnProperty.call(ZONE_TYPE_CONFIG, item.zoneType)
      && Array.isArray(item.coordinates) && item.coordinates.length >= 3
      && item.coordinates.every((p: unknown) => Array.isArray(p) && p.length >= 2
        && Number.isFinite(p[0]) && Number.isFinite(p[1])),
    ));
  } catch { return []; }
}

// Memory also keeps the current session usable if browser storage is unavailable.
const memory = new Map<string, string>();
const unavailableKeys = new Set<string>();
function snapshot(key: string): string {
  if (unavailableKeys.has(key)) return memory.get(key) ?? EMPTY;
  try { return localStorage.getItem(key) ?? EMPTY; }
  catch { return memory.get(key) ?? EMPTY; }
}

function write(key: string, drafts: ZoneDraft[]): boolean {
  const raw = JSON.stringify(drafts);
  memory.set(key, raw);
  try { localStorage.setItem(key, raw); unavailableKeys.delete(key); }
  catch { unavailableKeys.add(key); }
  window.dispatchEvent(new CustomEvent(CHANGE_EVENT, { detail: key }));
  return !unavailableKeys.has(key);
}

export function useZoneDrafts(projectId: string | undefined, userId: string | undefined) {
  const key = `cityprompt:zone-drafts:v1:${userId ?? 'local'}:${projectId ?? 'none'}`;
  const subscribe = useCallback((notify: () => void) => {
    const listener = (event: Event) => {
      if (event instanceof StorageEvent ? event.key === key : (event as CustomEvent).detail === key) notify();
    };
    window.addEventListener(CHANGE_EVENT, listener);
    window.addEventListener('storage', listener);
    return () => {
      window.removeEventListener(CHANGE_EVENT, listener);
      window.removeEventListener('storage', listener);
    };
  }, [key]);
  const getSnapshot = useCallback(() => snapshot(key), [key]);
  const raw = useSyncExternalStore(subscribe, getSnapshot, () => EMPTY);
  const drafts = useMemo(() => parseZoneDrafts(raw), [raw]);
  const upsertDraft = useCallback((draft: ZoneDraft) => {
    const previous = parseZoneDrafts(snapshot(key));
    return write(key, [...previous.filter((item) => item.requestId !== draft.requestId), draft]);
  }, [key]);
  const removeDraft = useCallback((requestId: string) => {
    write(key, parseZoneDrafts(snapshot(key)).filter((item) => item.requestId !== requestId));
  }, [key]);
  const discardRejectedDraft = useCallback((requestId: string): boolean => {
    // Read the current record, not a rendered snapshot: retrying removes its
    // rejection status before the request starts, making stale controls safe.
    const current = parseZoneDrafts(snapshot(key));
    const target = current.find((draft) => draft.requestId === requestId);
    if (!target || !isDiscardableDraft(target)) return false;
    write(key, current.filter((draft) => draft.requestId !== requestId));
    return true;
  }, [key]);
  return { drafts, upsertDraft, removeDraft, discardRejectedDraft, draftsPersistOnDevice: !unavailableKeys.has(key) };
}

export function draftToZone(draft: ZoneDraft, projectId: string): SiteZone {
  return {
    id: `temp-${draft.requestId}`, project_id: projectId, zone_type: draft.zoneType,
    coordinates: draft.coordinates, color: ZONE_TYPE_CONFIG[draft.zoneType].color,
    properties: draft.properties ?? ZONE_TYPE_CONFIG[draft.zoneType].defaultProperties,
    sort_order: 0, created_at: draft.createdAt, updated_at: draft.createdAt,
  };
}
