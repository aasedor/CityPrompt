import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import {
  SharedSiteGroundProvider,
  type SharedSiteGroundState,
} from './SharedSiteGroundProvider';
import { isNeighborhoodParkPilot } from './neighborhoodParkLayout';
import {
  measureParkTerrain,
  readParkTerrain,
  reuseMeasuredParkTerrain,
  parkFootprintKey,
  type ParkTerrainProfile,
} from './parkTerrain';

export interface ParkAlignment {
  pending: boolean;
  needsAttention: boolean;
  retry: () => void;
}
const Context = createContext<{ ids: ReadonlySet<string>; fallback: number }>({
  ids: new Set(),
  fallback: 0,
});
export const useAutomaticParkContext = () => useContext(Context);
export type SaveParkGround = (
  zone: SiteZone,
  profile: ParkTerrainProfile,
) => Promise<boolean>;

/** One bounded, debounced sampling job. Retired providers cannot finish it. */
function Sampler({
  zone,
  attempt,
  onResult,
  fallback,
}: {
  zone: SiteZone;
  attempt: number;
  onResult: (profile: ParkTerrainProfile | null) => void;
  fallback: number;
}) {
  const completed = useRef(false),
    latest = useRef(onResult);
  const mounted = useRef(true);
  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; };
  }, []);
  latest.current = onResult;
  const reused = useMemo(() => reuseMeasuredParkTerrain(zone), [zone]);
  useEffect(() => {
    if (!reused || completed.current) return;
    completed.current = true;
    latest.current(reused);
  }, [reused]);
  const boundary = useMemo(
    () => ({
      ...zone,
      zone_type: 'site_boundary' as const,
      is_active_boundary: true,
      properties: {
        community_3d_mask_existing_tiles: true,
        terrain_elevation_m:
          zone.properties?.terrain_elevation_m ??
          (zone.properties?.park_terrain as ParkTerrainProfile | undefined)
            ?.snapshot?.heights?.[0] ??
          fallback,
      },
    }),
    [zone, fallback],
  );
  const [started, setStarted] = useState(false);
  useEffect(() => {
    const timer = setTimeout(() => setStarted(true), attempt ? 5000 : 900);
    return () => clearTimeout(timer);
  }, [attempt]);
  useEffect(() => {
    if (!started) return;
    // Tile LOD changes can restart the provider's own timer. Bound the entire
    // attempt too, so a continuously refining scene never leaves a stuck job.
    const deadline = setTimeout(() => {
      if (!completed.current) {
        completed.current = true;
        latest.current(null);
      }
    }, 60000);
    return () => clearTimeout(deadline);
  }, [started]);
  const change = (state: SharedSiteGroundState) => {
    if (completed.current || !mounted.current) return;
    const profile = measureParkTerrain(zone, state.review);
    if (profile) {
      completed.current = true;
      latest.current(profile);
    } else if (state.inspectionStatus === 'unavailable') {
      completed.current = true;
      latest.current(null);
    }
  };
  return started && !reused ? (
    <SharedSiteGroundProvider
      zones={[boundary]}
      sampleSpacingM={1.25}
      inspectPrepared
      onChange={change}
    >
      {null}
    </SharedSiteGroundProvider>
  ) : null;
}

export function AutomaticParkGround({
  zones,
  paused,
  onSave,
  onChange,
  children,
  fallback,
}: {
  zones: SiteZone[];
  paused: boolean;
  onSave?: SaveParkGround;
  onChange: (state: ParkAlignment) => void;
  children: ReactNode;
  fallback: number;
}) {
  const boundary = getActiveSiteBoundary(zones);
  const landscape = boundary?.properties?.terrain_strategy === 'landscape';
  // A row or site revision can change grade without changing the park outline.
  // Restart conservatively; never re-label old samples with a newer revision.
  const jobKey = (zone: SiteZone) => JSON.stringify([
    parkFootprintKey(zone), zone.updated_at, boundary?.id, boundary?.updated_at, fallback,
  ]);
  const eligible = zones.filter(
    (z) =>
      isNeighborhoodParkPilot(z) &&
      !z.id.startsWith('temp-') &&
      (landscape || z.properties?.park_terrain),
  );
  const idKey = eligible.map((z) => z.id).join('|');
  const context = useMemo(
    () => ({ ids: new Set(idKey.split('|').filter(Boolean)), fallback }),
    [idKey, fallback],
  );
  const [attempts, setAttempts] = useState<Record<string, number>>({});
  const [saving, setSaving] = useState(false);
  const latest = useRef({ zones, paused, onSave });
  latest.current = { zones, paused, onSave };
  const pending = eligible.filter((z) => !readParkTerrain(z));
  const job = pending.find((z) => (attempts[jobKey(z)] ?? 0) < 3),
    key = job ? jobKey(job) : '';
  const active = useRef(key);
  active.current = key;
  const mounted = useRef(true);
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);
  const retry = useRef(() => setAttempts({}));
  useEffect(() => {
    const resume = () => retry.current();
    window.addEventListener('online', resume);
    return () => window.removeEventListener('online', resume);
  }, []);
  const callback = useRef(onChange);
  callback.current = onChange;
  const needsAttention = pending.some(
    (z) => (attempts[jobKey(z)] ?? 0) >= 3,
  );
  useEffect(() => {
    callback.current({
      pending: pending.length > 0,
      needsAttention,
      retry: retry.current,
    });
  }, [pending.length, needsAttention]);
  const finish = async (profile: ParkTerrainProfile | null) => {
    if (!mounted.current || !job || active.current !== key) return;
    const current = latest.current.zones.find((z) => z.id === job.id);
    if (!current || jobKey(current) !== key || latest.current.paused)
      return;
    setSaving(true);
    try {
      if (profile && (await latest.current.onSave?.(job, profile))) return;
    } catch {
      /* Bounded quiet retries; preserve the visible draft on failure. */
    } finally {
      if (mounted.current) {
        setSaving(false);
        setAttempts((a) => ({ ...a, [key]: (a[key] ?? 0) + 1 }));
      }
    }
  };
  return (
    <Context.Provider value={context}>
      {children}
      {onSave && job && !paused && !saving && (
        <Sampler
          key={`${key}:${attempts[key] ?? 0}`}
          zone={job}
          attempt={attempts[key] ?? 0}
          fallback={fallback}
          onResult={(p) => void finish(p)}
        />
      )}
    </Context.Provider>
  );
}
