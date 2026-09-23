import { useEffect, useMemo } from "react";
import {
  siteLandscapeImagePath,
  siteLandscapeSurfaceRegions,
} from "./siteLandscape";
import { api } from "@/services/api";
import type { SiteZone } from "@/types";
import {
  createResidualLandscapeTexture,
  rasterizeResidualLandscapeRegions,
  residualLandscapeBounds,
  type ResidualLandscapeRecipe,
} from "@/components/viewer/globe/residualLandscape";
import { createSitePreparationTexture } from "@/components/viewer/globe/sitePreparationSurface";

/** Compose into the boundary material; no overlay covers an archetype or its hit target. */
export function useSiteLandscapeTexture(
  zone: SiteZone,
  recipe: ResidualLandscapeRecipe | null,
  enabled: boolean,
) {
  const texture = useMemo(() => {
    if (!enabled) return null;
    const value = recipe
      ? createResidualLandscapeTexture(zone, recipe)
      : createSitePreparationTexture(zone.id, 256, "grass");
    if (recipe?.surface_image_url)
      value.userData.siteLandscapeStatus = "loading";
    return value;
  }, [enabled, recipe, zone]);
  useEffect(() => {
    if (!texture || !recipe?.surface_image_url) return;
    const imagePath = siteLandscapeImagePath(
      recipe.surface_image_url,
      zone.project_id,
    );
    if (!imagePath) {
      texture.userData.siteLandscapeStatus = "failed";
      return;
    }
    let active = true;
    const abort = new AbortController();
    void api
      .get<Blob>(imagePath, { responseType: "blob", signal: abort.signal })
      .then(async (response) => {
        const bitmap = await createImageBitmap(response.data);
        try {
          if (!active) return;
          const { width, height } = texture.image;
          const canvas = document.createElement("canvas");
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext("2d");
          if (!ctx) throw new Error("Landscape surface could not be decoded");
          ctx.drawImage(bitmap, 0, 0, width, height);
          const pixels = ctx.getImageData(0, 0, width, height).data;
          const target = texture.image.data;
          const labels = rasterizeResidualLandscapeRegions(
            siteLandscapeSurfaceRegions(zone, recipe),
            residualLandscapeBounds(zone.coordinates),
            width,
          );
          for (let y = 0; y < height; y++)
            for (let x = 0; x < width; x++) {
              if (labels[y * width + x] < 0) continue;
              const dst = (y * width + x) * 4,
                src = ((height - 1 - y) * width + x) * 4,
                alpha = pixels[src + 3] / 255;
              for (let c = 0; c < 3; c++)
                target[dst + c] = Math.round(
                  target[dst + c] * (1 - alpha) + pixels[src + c] * alpha,
                );
            }
          texture.needsUpdate = true;
          texture.userData.siteLandscapeStatus = "ready";
        } finally {
          bitmap.close();
        }
      })
      .catch((error) => {
        if (active && !abort.signal.aborted) {
          texture.userData.siteLandscapeStatus = "failed";
          console.warn(
            "Site surface unavailable; showing the saved landscape preset.",
            error,
          );
        }
      });
    return () => {
      active = false;
      abort.abort();
    };
  }, [texture, recipe, zone]);
  return texture;
}
