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
        preferences[map.id].enabled &&
        preferences[map.id].opacity > 0,
      ),
      staleTime: Infinity,
      gcTime: 30 * 60_000,
      retry: false,
    })),
  });
  const [imageErrors, setImageErrors] = useState<Record<string, boolean>>({});
  const [retryVersion, setRetryVersion] = useState<Record<string, number>>({});
  const layers = CITY_PLAN_MAPS.map((map, i) => ({
    map,
    ...preferences[map.id],
    data: queries[i].data,
    loading: queries[i].isFetching,
    error: Boolean(queries[i].error || imageErrors[map.id]),
  }));
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
    selected:
      selection?.key === key
        ? (CITY_PLAN_MAPS.find((map) => map.id === selection.id) ?? null)
        : null,
    setEnabled: (id: string, enabled: boolean) => update(id, { enabled }),
    setOpacity: (id: string, opacity: number) => {
      if (Number.isFinite(opacity))
        update(id, { opacity: Math.max(0, Math.min(1, opacity)) });
    },
    inspect: (id: string) => {
      if (CITY_PLAN_MAPS.some((map) => map.id === id))
        setSelection({ key, id });
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
      void queries[CITY_PLAN_MAPS.findIndex((map) => map.id === id)]?.refetch();
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
