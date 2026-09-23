import {
  landscapeContextImage,
  type CaptureLandscapeContext,
} from "./landscapeContext";
import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Loader2, Trees, Sparkles } from "lucide-react";
import { api, authApi, getApiErrorMessage, siteZonesApi } from "@/services/api";
import { useAuthStore } from "@/store";
import {
  landscapeEdgeSamples,
  type LandscapeEdgeSample,
} from "./landscapeEdges";
import type { SiteZone, SiteZoneProperties } from "@/types";
import { runProjectWrite } from "@/utils/projectWriteQueue";
import { useUndoRedoStore } from "@/store/undoRedo";
import { createZoneUpdateAction } from "@/store/undoActions";
import {
  landscapeKeepClear,
  type LandscapePreset,
  type LandscapePreview,
} from "./siteLandscape";

const OPTIONS: Array<{
  id: LandscapePreset;
  name: string;
  description: string;
}> = [
  {
    id: "gardens",
    name: "Neighbourhood gardens",
    description: "Garden edges, tree groups and shared lawns",
  },
  {
    id: "natural",
    name: "Natural landscape",
    description: "Meadow ground and informal planting",
  },
  {
    id: "urban",
    name: "Urban landscape",
    description: "Paved edges and planted tree groups",
  },
];
export function SiteLandscapePanel({
  zone,
  onSaved,
  captureContext,
}: {
  zone: SiteZone;
  captureContext?: CaptureLandscapeContext;
  onSaved: (properties: SiteZoneProperties) => void;
}) {
  const client = useQueryClient();
  const [preset, setPreset] = useState<LandscapePreset>(
    () =>
      (
        zone.properties?.community_3d_landscape as
          { preset?: LandscapePreset } | undefined
      )?.preset ?? "gardens",
  );
  const [prompt, setPrompt] = useState("");
  const [custom, setCustom] = useState(false);
  const [preview, setPreview] = useState<LandscapePreview | null>(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [cost, setCost] = useState<number | null>(null);
  const generation = useRef(0);
  useEffect(() => {
    let active = true;
    const ref = generation;
    void api
      .get<{ tokens: number }>("/api/v1/site-landscape/options")
      .then((r) => {
        if (active) setCost(r.data.tokens);
      })
      .catch(() => {});
    return () => {
      active = false;
      ref.current++;
    };
  }, [zone.id]);
  const clear = () => {
    setPreview(null);
    setError("");
  };
  const record = async (before: SiteZone, saved: SiteZone) => {
    const keys = ["community_3d_landscape", "community_3d_landscape_mode"];
    const oldProps = { ...before.properties },
      newProps = { ...saved.properties };
    keys.forEach((key) => {
      if (!(key in oldProps)) oldProps[key] = null;
    });
    useUndoRedoStore
      .getState()
      .pushAction(
        createZoneUpdateAction(
          zone.project_id,
          zone.id,
          { properties: oldProps },
          { properties: newProps },
          client,
          saved.updated_at,
        ),
      );
    onSaved(newProps);
    await client.invalidateQueries({
      queryKey: ["site-zones", zone.project_id],
    });
  };
  const generate = async () => {
    const n = ++generation.current;
    setBusy("Generating preview…");
    clear();
    try {
      const zones = await runProjectWrite(client, zone.project_id, () =>
        siteZonesApi.list(zone.project_id),
      );
      const physical = zones.filter(
        (z) =>
          z.id === zone.id ||
          (z.zone_type !== "site_boundary" &&
            z.properties?._plan_role !== "framework_height"),
      );
      let contextImage: string | undefined;
      let edgeSamples: LandscapeEdgeSample[] | undefined;
      if (custom) {
        if (!captureContext)
          throw new Error(
            "Open the 3D globe to generate landscape that fits its surroundings.",
          );
        setBusy("Reading your site and neighbourhood…");
        const boundary = zones.find((z) => z.id === zone.id)!;
        const capture = await captureContext(boundary.coordinates);
        contextImage = landscapeContextImage(capture, physical);
        edgeSamples = await landscapeEdgeSamples(capture, boundary);
        if (n !== generation.current) return;
        setBusy("Generating preview…");
      }
      const result = (
        await api.post<LandscapePreview>(
          `/api/v1/site-landscape/${zone.id}/preview`,
          {
            preset,
            prompt: custom ? prompt : "",
            context_image_base64: contextImage,
            context_edge_samples: edgeSamples,
            corridors: landscapeKeepClear(zones),
            revisions: Object.fromEntries(
              physical.map((z) => [z.id, z.updated_at]),
            ),
          },
          { timeout: 420000 },
        )
      ).data;
      if (n === generation.current) setPreview(result);
    } catch (e) {
      if (n === generation.current)
        setError(getApiErrorMessage(e, "Could not generate this landscape."));
    } finally {
      if (n === generation.current) setBusy("");
      // Refresh after successful calls and refunded failures alike. Applying
      // or discarding a preview does not change the provider charge.
      if (custom) {
        void authApi
          .me()
          .then((user) => {
            if (useAuthStore.getState().user?.id === user.id)
              useAuthStore.getState().setUser(user);
          })
          .catch(() => {});
      }
    }
  };
  const apply = async () => {
    if (!preview) return;
    setBusy("Applying landscape…");
    setError("");
    try {
      await runProjectWrite(client, zone.project_id, async () => {
        const before = (await siteZonesApi.list(zone.project_id)).find(
          (z) => z.id === zone.id,
        )!;
        const saved = (
          await api.post<SiteZone>(`/api/v1/site-landscape/${zone.id}/apply`, {
            preview: preview.preview,
            signature: preview.signature,
          })
        ).data;
        await record(before, saved);
      });
      setPreview(null);
    } catch (e) {
      setError(getApiErrorMessage(e, "Could not apply the preview."));
    } finally {
      setBusy("");
    }
  };
  const remove = async () => {
    setBusy("Removing landscape…");
    setError("");
    try {
      await runProjectWrite(client, zone.project_id, async () => {
        const before = (await siteZonesApi.list(zone.project_id)).find(
          (z) => z.id === zone.id,
        )!;
        const saved = await siteZonesApi.update(zone.id, {
          expected_updated_at: before.updated_at,
          properties: {
            ...before.properties,
            community_3d_landscape: null,
            community_3d_landscape_mode: "placed_objects_only",
          },
        });
        await record(before, saved);
      });
      clear();
    } catch (e) {
      setError(getApiErrorMessage(e));
    } finally {
      setBusy("");
    }
  };
  const unavailable =
    zone.id.startsWith("temp-") ||
    zone.properties?.community_3d_mask_existing_tiles === false;
  const recipe = zone.properties?.community_3d_landscape as
    { state?: string } | undefined;
  return (
    <section
      className="space-y-3 rounded-xl border border-border bg-surface p-3"
      aria-label="Site landscape"
    >
      <h3 className="flex items-center gap-2 font-semibold">
        <Trees size={18} /> Finish your site
      </h3>
      <p className="text-xs text-text-muted">
        Fill the spaces around your buildings, streets and parks. Existing
        objects and access paths stay clear.
      </p>
      <fieldset disabled={!!busy} className="space-y-2">
        <legend className="sr-only">Landscape character</legend>
        {OPTIONS.map((option) => (
          <label
            key={option.id}
            className={`flex cursor-pointer gap-2 rounded-lg border p-2 ${preset === option.id ? "border-black bg-lime-100" : "border-border"}`}
          >
            <input
              type="radio"
              name={`landscape-${zone.id}`}
              checked={preset === option.id}
              onChange={() => {
                setPreset(option.id);
                clear();
              }}
            />
            <span>
              <span className="block text-sm font-medium">{option.name}</span>
              <span className="block text-xs text-text-muted">
                {option.description}
              </span>
            </span>
          </label>
        ))}
        <label className="flex items-center gap-2 pt-2 text-sm">
          <input
            type="checkbox"
            checked={custom}
            onChange={(e) => {
              setCustom(e.target.checked);
              clear();
            }}
          />{" "}
          Custom ground treatment
        </label>
        {custom && (
          <>
            <textarea
              aria-label="Describe your site landscape"
              value={prompt}
              maxLength={1600}
              rows={3}
              onChange={(e) => {
                setPrompt(e.target.value);
                clear();
              }}
              className="w-full rounded-lg border border-border bg-surface p-2 text-sm"
              placeholder="Terracotta paving, native planting beds and a marble pool surround…"
            />
            <p className="text-xs text-text-muted">
              GPT Image 2.5 uses your development and surrounding Google tiles
              to create a continuous landscape beneath your 3D objects. Preview
              · {cost === null ? "checking token cost…" : `${cost} tokens`}.
              Surface artwork is flat; pools and structures need a 3D archetype
              for depth.
            </p>
          </>
        )}
      </fieldset>
      {unavailable && (
        <p className="text-xs text-text-muted">
          To use landscape presets, choose Clear site for redevelopment under
          Site ground, then Save changes. This replaces the existing surface
          inside your boundary with a level site. Landscape presets are not
          available on terrain-following sites yet.
        </p>
      )}
      {recipe?.state === "stale" && (
        <p className="text-xs text-amber-700">
          Your design changed. Generate a fresh landscape to fit it.
        </p>
      )}
      <button
        type="button"
        onClick={() => void generate()}
        disabled={
          !!busy || unavailable || (custom && (!prompt.trim() || cost === null))
        }
        className="flex min-h-11 w-full items-center justify-center gap-2 rounded-lg border-2 border-black bg-[#c8ff31] p-2 text-sm font-semibold text-black disabled:opacity-50"
      >
        {busy ? (
          <Loader2 className="animate-spin" size={16} />
        ) : (
          <Sparkles size={16} />
        )}{" "}
        {busy || "Generate 3D Site Landscape"}
      </button>
      {!custom && (
        <p className="text-xs text-text-muted">
          No image-generation tokens · preview before applying
        </p>
      )}
      {preview && (
        <div className="space-y-2">
          <img
            src={`data:image/png;base64,${preview.image_base64}`}
            alt="Landscape preview viewed from above"
            className="w-full rounded-lg border border-border"
          />
          <p className="text-xs text-text-muted">
            {Math.round(preview.preview.recipe.area_sqm).toLocaleString()} m² ·{" "}
            {preview.preview.recipe.placements.length} trees. Apply to see the
            landscape in 3D.
          </p>
          <div className="flex gap-2">
            <button
              disabled={!!busy}
              onClick={() => void apply()}
              className="min-h-11 flex-1 rounded-lg border-2 border-black bg-[#c8ff31] p-2 font-semibold text-black"
            >
              Apply landscape
            </button>
            <button
              disabled={!!busy}
              onClick={clear}
              className="min-h-11 rounded-lg border border-border px-3"
            >
              Discard
            </button>
          </div>
        </div>
      )}
      {!!recipe && (
        <button
          disabled={!!busy}
          onClick={() => void remove()}
          className="min-h-11 text-sm underline"
        >
          Remove landscape
        </button>
      )}
      {error && (
        <p role="alert" className="text-sm text-red-700">
          {error}
        </p>
      )}
    </section>
  );
}
