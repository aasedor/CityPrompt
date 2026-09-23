import type { SiteZone } from "@/types";
import { resolvePedestrianConnections } from "@/features/pickPlace/pedestrianConnections";
import { resolveManualParkAccess } from "@/components/viewer/globe/parkAccessConnections";
import {
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from "@/components/viewer/mapEngine/geoUtils";
import type {
  ResidualLandscapeRecipe,
  ResidualLandscapeRegion,
} from "@/components/viewer/globe/residualLandscape";

/** Surface coverage is independent of the tree/access keep-clear regions. */
export function siteLandscapeSurfaceRegions(
  zone: SiteZone,
  recipe: ResidualLandscapeRecipe,
): ResidualLandscapeRegion[] {
  if (recipe.surface_mode !== "site_base") return recipe.regions;
  return [
    {
      id: "continuous-site-base",
      kind: "lawn",
      area_sqm: recipe.area_sqm + recipe.occupied_area_sqm,
      minimum_width_m: 0,
      geometry: {
        type: "Polygon",
        coordinates: [zone.coordinates.map((p) => [p[0], p[1]])],
      },
    },
  ];
}

export type LandscapePreset = "gardens" | "natural" | "urban";
export interface LandscapePreview {
  preview: {
    boundary_id: string;
    project_id: string;
    context_hash: string;
    expires_at: number;
    recipe: ResidualLandscapeRecipe;
  };
  signature: string;
  image_base64: string;
}
export function accessCorridor(
  start: number[],
  end: number[],
  width: number,
): number[][] {
  const mx = metersPerDegLon(start[1]),
    my = METERS_PER_DEG_LAT;
  const dx = (end[0] - start[0]) * mx,
    dy = (end[1] - start[1]) * my,
    length = Math.hypot(dx, dy);
  if (length < 0.01) return [];
  const r = width / 2 + 0.75;
  const nx = ((-dy / length) * r) / mx,
    ny = ((dx / length) * r) / my;
  const tx = ((dx / length) * 0.75) / mx,
    ty = ((dy / length) * 0.75) / my;
  const a = [start[0] - tx + nx, start[1] - ty + ny];
  return [
    a,
    [end[0] + tx + nx, end[1] + ty + ny],
    [end[0] + tx - nx, end[1] + ty - ny],
    [start[0] - tx - nx, start[1] - ty - ny],
    a,
  ];
}
export function landscapeKeepClear(zones: SiteZone[]): number[][][] {
  const result: number[][][] = [];
  for (const plan of resolvePedestrianConnections(zones))
    for (const strip of plan.strips) {
      const ring = accessCorridor(strip.start, strip.end, strip.widthM);
      if (ring.length) result.push(ring);
    }
  for (const park of resolveManualParkAccess(zones).parks)
    for (const connection of park.connections) {
      for (let i = 1; i < connection.path.length; i++) {
        const ring = accessCorridor(
          connection.path[i - 1],
          connection.path[i],
          connection.widthM,
        );
        if (ring.length) result.push(ring);
      }
    }
  return result;
}

/** Read through the authenticated API, without persisting expiring asset tickets. */
export function siteLandscapeImagePath(
  value: string,
  projectId: string,
): string | null {
  try {
    const path = new URL(value, "https://site.invalid").pathname;
    const prefix = `/api/v1/files/projects/${projectId}/landscape/`;
    return path.startsWith(prefix) &&
      /^[a-f0-9-]+\.png$/i.test(path.slice(prefix.length))
      ? path
      : null;
  } catch {
    return null;
  }
}
