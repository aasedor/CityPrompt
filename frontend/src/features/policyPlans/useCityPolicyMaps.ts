import { useCallback, useMemo, useState } from "react";
import { useQueries } from "@tanstack/react-query";
import {
  readBrowserPreference,
  writeBrowserPreference,
} from "@/utils/browserPreferences";
import {
  CITY_PLAN_ASSETS,
  CITY_PLAN_MAPS,
  readCityPlanPreferences,
  type MapPreference,
  type PlanRaster,
} from "./citywidePlans";
import { TRANSPORT_ASSETS, parseTransportSnapshot, transportNetworkForMap } from './transportVectors';

export function useCityPolicyMaps(projectId: string | undefined) {
  const key = `cityprompt:city-policy:v1:${projectId}`;
  const saved = useMemo(
    () => readCityPlanPreferences(readBrowserPreference(key)),
    [key],
  );
  const [choices, setChoices] = useState<
    Record<string, Record<string, MapPreference>>
  >({});
  const [selection, setSelection] = useState<{
    key: string;
    id: string;
    featureId?: string;
  } | null>(null);
  const preferences = choices[key] ?? saved;
  const queries = useQueries({
    queries: CITY_PLAN_MAPS.map((map) => ({
      queryKey: ["city-policy-2026-v1", map.id],
      queryFn: async ({ signal }: { signal: AbortSignal }) => {
        const response = await fetch(`${CITY_PLAN_ASSETS}/${map.id}/map.json`, {
          signal,
        });
        if (!response.ok) throw new Error("Map unavailable");
        const data = (await response.json()) as PlanRaster;
        if (
          data.id !== map.id ||
          !Array.isArray(data.tiles) ||
          data.gridSize !== 4
        )
          throw new Error("Invalid map");
        return data;
      },
      enabled: Boolean(
        projectId &&
        (!transportNetworkForMap(map.id) || preferences[map.id].format === 'pdf') &&
        preferences[map.id].enabled &&
        preferences[map.id].opacity > 0,
      ),
      staleTime: Infinity,
      gcTime: 30 * 60_000,
      retry: false,
    })),
  });
  const networks = ['transit', '5a'] as const;
  const vectorQueries = useQueries({ queries: networks.map(network => ({
    queryKey: ['transport-vectors-v1', network],
    queryFn: async ({ signal }: { signal: AbortSignal }) => {
      const response = await fetch(`${TRANSPORT_ASSETS}/${network}.geojson`, { signal });
      if (!response.ok) throw new Error('Transport map unavailable');
      return parseTransportSnapshot(await response.json(), network);
    },
    enabled: Boolean(projectId && CITY_PLAN_MAPS.some(map => transportNetworkForMap(map.id) === network
      && preferences[map.id].enabled && preferences[map.id].opacity > 0 && preferences[map.id].format !== 'pdf')),
    staleTime: Infinity, gcTime: 30 * 60_000, retry: false,
  })) });
  const [imageErrors, setImageErrors] = useState<Record<string, boolean>>({});
  const [retryVersion, setRetryVersion] = useState<Record<string, number>>({});
  const layers = CITY_PLAN_MAPS.map((map, i) => {
    const network = transportNetworkForMap(map.id);
    const vector = network && preferences[map.id].format !== 'pdf';
    const query = network ? vectorQueries[networks.indexOf(network)] : undefined;
    return ({
    map,
    ...preferences[map.id],
    format: vector ? 'vector' as const : 'pdf' as const,
    data: vector ? undefined : queries[i].data,
    vectorData: vector ? query?.data : undefined,
    loading: vector ? Boolean(query?.isFetching) : queries[i].isFetching,
    error: vector ? Boolean(query?.error) : Boolean(queries[i].error || imageErrors[map.id]),
  }); });
  const update = (id: string, patch: Partial<MapPreference>) => {
    if (!preferences[id]) return;
    const next = { ...preferences, [id]: { ...preferences[id], ...patch } };
    writeBrowserPreference(key, JSON.stringify(next));
    setChoices((current) => ({ ...current, [key]: next }));
    if (patch.enabled === false || patch.opacity === 0)
      setSelection((current) => (current?.id === id ? null : current));
  };
  return {
    layers,
    retryVersion,
    selectedFeature: selection?.key === key && selection.featureId
      ? layers.find(layer => layer.map.id === selection.id)?.vectorData?.features.find(f => f.id === selection.featureId) : undefined,
    selectedSnapshot: selection?.key === key ? layers.find(layer => layer.map.id === selection.id)?.vectorData : undefined,
    selected:
      selection?.key === key
        ? (CITY_PLAN_MAPS.find((map) => map.id === selection.id) ?? null)
        : null,
    setEnabled: (id: string, enabled: boolean) => update(id, { enabled }),
    setFormat: (id: string, format: 'vector' | 'pdf') => { update(id, { format }); setSelection(null); },
    setOpacity: (id: string, opacity: number) => {
      if (Number.isFinite(opacity))
        update(id, { opacity: Math.max(0, Math.min(1, opacity)) });
    },
    inspect: (token: string) => {
      const [id, featureId] = token.split('::');
      if (CITY_PLAN_MAPS.some((map) => map.id === id))
        setSelection({ key, id, featureId });
    },
    clearSelection: useCallback(() => setSelection(null), []),
    imageFailed: useCallback(
      (id: string) =>
        setImageErrors((current) =>
          current[id] ? current : { ...current, [id]: true },
        ),
      [],
    ),
    retry: (id: string) => {
      setImageErrors((current) => ({ ...current, [id]: false }));
      setRetryVersion((current) => ({
        ...current,
        [id]: (current[id] ?? 0) + 1,
      }));
      const network = transportNetworkForMap(id);
      if (network && preferences[id].format !== 'pdf') void vectorQueries[networks.indexOf(network)].refetch();
      else void queries[CITY_PLAN_MAPS.findIndex((map) => map.id === id)]?.refetch();
    },
    hideAll: () => {
      const next = Object.fromEntries(
        Object.entries(preferences).map(([id, preference]) => [
          id,
          { ...preference, enabled: false },
        ]),
      );
      writeBrowserPreference(key, JSON.stringify(next));
      setChoices((current) => ({ ...current, [key]: next }));
      setSelection(null);
    },
  };
}
export type CityPolicyMapsState = ReturnType<typeof useCityPolicyMaps>;
