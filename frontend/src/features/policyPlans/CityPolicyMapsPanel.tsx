import type { CityPolicyMapsState } from "./useCityPolicyMaps";
import { CITY_PLAN_EDITION } from "./citywidePlans";

export function CityPolicyMapsPanel({ state }: { state: CityPolicyMapsState }) {
  const count = state.layers.filter((layer) => layer.enabled).length;
  return (
    <section
      aria-label="City-wide policy maps"
      className="max-w-sm space-y-3 rounded-2xl border border-[#151515]/20 bg-[#fffdf6]/95 p-3 text-[#151515] shadow-lg"
    >
      <header>
        <h3 className="text-sm font-bold">City-wide policy maps</h3>
        <p className="mt-1 text-xs text-[#5c554d]">
          Compare the plans behind your site.
        </p>
      </header>
      <p className="text-[10px] text-[#5c554d]">{CITY_PLAN_EDITION}</p>
      {(["MDP", "CTP"] as const).map((group) => (
        <details
          key={group}
          open={group === "MDP"}
          className="rounded-xl border border-[#151515]/15 bg-white/80"
        >
          <summary className="cursor-pointer px-3 py-3 text-xs font-semibold">
            {group === "MDP"
              ? "Municipal Development Plan"
              : "Calgary Transportation Plan"}
          </summary>
          <ul className="divide-y divide-[#151515]/10 border-t border-[#151515]/10">
            {state.layers
              .filter((layer) => layer.map.group === group)
              .map((layer) => (
                <li key={layer.map.id} className="p-2">
                  <label className="flex min-h-11 cursor-pointer items-center gap-2 text-xs font-semibold">
                    <input
                      type="checkbox"
                      role="switch"
                      aria-label={`Show ${group} Map ${layer.map.number}: ${layer.map.title}`}
                      checked={layer.enabled}
                      onChange={(event) =>
                        state.setEnabled(layer.map.id, event.target.checked)
                      }
                      className="h-4 w-4 shrink-0 accent-[#37594b]"
                    />
                    <span>
                      <span className="mr-1 text-[#5c554d]">
                        {layer.map.number}.
                      </span>
                      {layer.map.title}
                    </span>
                  </label>
                  <button
                    type="button"
                    onClick={() => state.inspect(layer.map.id)}
                    aria-label={`Legend and meaning for ${group} Map ${layer.map.number}`}
                    className="min-h-11 px-1 text-[11px] font-semibold text-[#37594b] underline underline-offset-2"
                  >
                    Legend & meaning
                  </button>
                  {layer.enabled && (
                    <>
                      <label className="block text-[11px]">
                        <span className="flex justify-between">
                          <span>Opacity</span>
                          <span>{Math.round(layer.opacity * 100)}%</span>
                        </span>
                        <input
                          aria-label={`${group} Map ${layer.map.number} opacity`}
                          type="range"
                          min="0"
                          max="100"
                          step="1"
                          value={Math.round(layer.opacity * 100)}
                          onChange={(event) =>
                            state.setOpacity(
                              layer.map.id,
                              Number(event.target.value) / 100,
                            )
                          }
                          className="h-9 w-full accent-[#37594b]"
                        />
                      </label>
                      {layer.loading && (
                        <p role="status" className="text-xs">
                          Loading map…
                        </p>
                      )}
                      {layer.error && (
                        <div role="alert" className="text-xs text-amber-900">
                          This map could not load.{" "}
                          <button
                            type="button"
                            className="min-h-11 underline"
                            onClick={() => state.retry(layer.map.id)}
                          >
                            Retry
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </li>
              ))}
          </ul>
          {group === "CTP" && (
            <p className="border-t p-2 text-[10px] text-[#5c554d]">
              Map 4, the former regional transit plan, was removed from the
              published CTP.
            </p>
          )}
        </details>
      ))}
      <p className="text-[10px] leading-relaxed text-[#5c554d]">
        Geographically aligned plan maps. Use Top View to compare locations.
        Colours, lines and hatching retain the City’s published symbols; these
        city-wide maps are conceptual rather than parcel boundaries.
      </p>
      {count > 0 && (
        <button
          type="button"
          onClick={state.hideAll}
          className="min-h-11 w-full rounded-lg border border-[#151515]/20 text-xs font-semibold"
        >
          Hide all city-wide maps ({count})
        </button>
      )}
    </section>
  );
}
