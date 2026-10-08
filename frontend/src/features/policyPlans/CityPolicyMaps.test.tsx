import "@testing-library/jest-dom/vitest";
import {
  act,
  fireEvent,
  render,
  renderHook,
  screen,
  waitFor,
} from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useState } from "react";
import { useCityPolicyMaps } from "./useCityPolicyMaps";
import { CityPolicyMapsPanel } from "./CityPolicyMapsPanel";
import { CityPolicyDetailsCard } from "./CityPolicyDetailsCard";
import { CITY_PLAN_MAPS, readCityPlanPreferences } from "./citywidePlans";
import { TRANSPORT_ASSETS } from './transportVectors';

const transitSnapshot = { type: 'FeatureCollection', network: 'transit', retrieved: '2026-10-07',
  sources: { city: { url: 'https://data.calgary.ca/resource/qseb-xcrr.geojson', featureCount: 1 } }, featureCount: 1,
  features: [{ type: 'Feature', id: 'test-hub', properties: { category: 'hub', source: 'city' },
    geometry: { type: 'Point', coordinates: [-114.1, 51.05] } }] };

const fetchMap = vi.fn(async (url: string) => ({
  ok: true,
  json: async () => url.endsWith('/transit.geojson') ? transitSnapshot : ({ id: url.split("/").slice(-2)[0], tiles: [], gridSize: 4 }),
}));
beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
  vi.stubGlobal("fetch", fetchMap);
});
function wrapper({ children }: { children: React.ReactNode }) {
  const [client] = useState(
    () => new QueryClient({ defaultOptions: { queries: { retry: false } } }),
  );
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
function App() {
  const state = useCityPolicyMaps("pilot");
  return (
    <>
      <CityPolicyMapsPanel state={state} />
      <CityPolicyDetailsCard
        map={state.selected}
        feature={state.selectedFeature}
        snapshot={state.selectedSnapshot}
        onClose={state.clearSelection}
      />
    </>
  );
}

describe("City-wide plan maps", () => {
  it('defaults to vectors, shares the transit download, and restores PDF comparison per project', async () => {
    const { result, rerender } = renderHook(({ project }) => useCityPolicyMaps(project), {
      initialProps: { project: 'vector-pilot' }, wrapper,
    });
    act(() => result.current.setEnabled('ctp-2', true));
    await waitFor(() => expect(result.current.layers.find(l => l.map.id === 'ctp-2')?.vectorData).toEqual(transitSnapshot));
    expect(fetchMap).toHaveBeenCalledWith(`${TRANSPORT_ASSETS}/transit.geojson`, expect.anything());
    act(() => result.current.setEnabled('mdp-2', true));
    expect(fetchMap).toHaveBeenCalledTimes(1);
    act(() => result.current.inspect('ctp-2::test-hub'));
    expect(result.current.selectedFeature?.properties.category).toBe('hub');
    expect(result.current.selectedSnapshot?.sources.city.url).toContain('calgary.ca');
    act(() => result.current.setFormat('ctp-2', 'pdf'));
    await waitFor(() => expect(result.current.layers.find(l => l.map.id === 'ctp-2')?.data?.id).toBe('ctp-2'));
    expect(result.current.selectedFeature).toBeUndefined();
    expect(result.current.layers.find(l => l.map.id === 'ctp-2')?.vectorData).toBeUndefined();
    rerender({ project: 'another' });
    expect(result.current.layers.find(l => l.map.id === 'ctp-2')?.format).toBe('vector');
    rerender({ project: 'vector-pilot' });
    expect(result.current.layers.find(l => l.map.id === 'ctp-2')?.format).toBe('pdf');
    act(() => result.current.setFormat('ctp-2', 'vector'));
    expect(fetchMap).toHaveBeenCalledTimes(2);
    act(() => result.current.inspect('ctp-2::test-hub'));
    act(() => result.current.setOpacity('ctp-2', 0));
    expect(result.current.selectedFeature).toBeUndefined();
  });

  it('retries a failed vector snapshot without switching to the PDF', async () => {
    fetchMap.mockRejectedValueOnce(new Error('Offline'));
    const { result } = renderHook(() => useCityPolicyMaps('retry-vector'), { wrapper });
    act(() => result.current.setEnabled('mdp-2', true));
    await waitFor(() => expect(result.current.layers[1].error).toBe(true));
    act(() => result.current.retry('mdp-2'));
    await waitFor(() => expect(result.current.layers[1].vectorData?.features).toHaveLength(1));
    expect(result.current.layers[1].format).toBe('vector');
    expect(fetchMap.mock.calls.every(([url]) => url.endsWith('/transit.geojson'))).toBe(true);
  });

  it('explains the selected feature with its City source and keeps PDF legends labelled as reference', () => {
    render(<CityPolicyDetailsCard map={CITY_PLAN_MAPS.find(m => m.id === 'ctp-2')!}
      feature={{ type: 'Feature', id: 'hub', properties: { category: 'hub', source: 'city' }, geometry: { type: 'Point', coordinates: [-114.1, 51.05] } }}
      snapshot={{ ...transitSnapshot, type: 'FeatureCollection', network: 'transit', features: [] }} onClose={() => {}} />);
    expect(screen.getByText('Primary Transit Hub')).toBeInTheDocument();
    expect(screen.getByText(/safe walking access/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'View official City feature service' })).toHaveAttribute('href', transitSnapshot.sources.city.url);
    expect(screen.getByText('Published PDF reference legend')).toBeInTheDocument();
  });
  it("offers all 12 maps, excludes removed CTP 4, and explains each with its exact source page before loading artwork", () => {
    render(<App />, { wrapper });
    expect(screen.getAllByRole("switch", { hidden: true })).toHaveLength(12);
    expect(CITY_PLAN_MAPS.some((map) => map.id === "ctp-4")).toBe(false);
    for (const map of CITY_PLAN_MAPS) {
      fireEvent.click(
        screen.getByLabelText(
          `Legend and meaning for ${map.group} Map ${map.number}`,
        ),
      );
      const region = screen.getByRole("region", { name: map.title });
      expect(region).toHaveFocus();
      expect(screen.getByRole("img")).toHaveAttribute("alt", map.legendText);
      expect(
        screen.getByRole("link", { name: /^Read the plan/ }),
      ).toHaveAttribute("href", map.source);
      expect(map.source).toContain(`#page=${map.page}`);
      fireEvent.keyDown(region, { key: "Escape" });
      expect(
        screen.queryByRole("region", { name: map.title }),
      ).not.toBeInTheDocument();
    }
    expect(fetchMap).not.toHaveBeenCalled();
  });

  it("fetches only enabled maps and preserves independent opacity, project preferences and hide-all", async () => {
    const { result, rerender } = renderHook(
      ({ project }) => useCityPolicyMaps(project),
      { initialProps: { project: "one" }, wrapper },
    );
    expect(fetchMap).not.toHaveBeenCalled();
    act(() => result.current.setEnabled("mdp-1", true));
    await waitFor(() =>
      expect(result.current.layers[0].data?.id).toBe("mdp-1"),
    );
    act(() => result.current.setEnabled("ctp-3", true));
    await waitFor(() => expect(fetchMap).toHaveBeenCalledTimes(2));
    act(() => result.current.setOpacity("mdp-1", 0.35));
    expect(
      result.current.layers.find((layer) => layer.map.id === "ctp-3")?.opacity,
    ).toBe(0.7);
    act(() => result.current.inspect("mdp-1"));
    act(() => result.current.setOpacity("mdp-1", 0));
    expect(result.current.selected).toBeNull();
    act(() => result.current.setOpacity("mdp-1", 1));
    act(() => result.current.inspect("mdp-1"));
    rerender({ project: "two" });
    expect(result.current.layers.every((layer) => !layer.enabled)).toBe(true);
    expect(result.current.selected).toBeNull();
    rerender({ project: "one" });
    expect(result.current.layers[0]).toMatchObject({
      enabled: true,
      opacity: 1,
    });
    act(() => result.current.hideAll());
    expect(result.current.layers.every((layer) => !layer.enabled)).toBe(true);
    expect(result.current.selected).toBeNull();
    expect(
      JSON.parse(localStorage.getItem("cityprompt:city-policy:v1:one")!)[
        "mdp-1"
      ],
    ).toEqual({ enabled: false, opacity: 1 });
  });

  it("can recover a missing map and failed tile without changing other map choices", async () => {
    fetchMap.mockRejectedValueOnce(new Error("Offline"));
    const { result } = renderHook(() => useCityPolicyMaps("pilot"), {
      wrapper,
    });
    act(() => result.current.setFormat('mdp-2', 'pdf'));
    act(() => result.current.setEnabled("mdp-2", true));
    await waitFor(() => expect(result.current.layers[1].error).toBe(true));
    act(() => result.current.retry("mdp-2"));
    await waitFor(() =>
      expect(result.current.layers[1].data?.id).toBe("mdp-2"),
    );
    act(() => result.current.imageFailed("mdp-2"));
    expect(result.current.layers[1].error).toBe(true);
    act(() => result.current.retry("mdp-2"));
    await waitFor(() => expect(result.current.layers[1].error).toBe(false));
    expect(result.current.layers[0].enabled).toBe(false);
  });

  it("tolerates corrupt or unavailable saved preferences and clamps opacity", () => {
    for (const bad of ["{", "null", "[]", '"text"'])
      expect(
        Object.values(readCityPlanPreferences(bad)).every(
          (value) => !value.enabled && value.opacity === 0.7,
        ),
      ).toBe(true);
    const preferences = readCityPlanPreferences(
      JSON.stringify({
        "mdp-1": { enabled: "yes", opacity: -3 },
        "ctp-3": { enabled: true, opacity: 9 },
        unknown: { enabled: true },
      }),
    );
    expect(preferences["mdp-1"]).toEqual({ enabled: false, opacity: 0 });
    expect(preferences["ctp-3"]).toEqual({ enabled: true, opacity: 1 });
    expect(preferences.unknown).toBeUndefined();
  });
});
