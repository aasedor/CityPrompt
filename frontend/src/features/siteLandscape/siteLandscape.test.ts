import { describe, expect, it } from "vitest";
import { Group, Mesh, MeshBasicMaterial, Texture } from "three";
import {
  accessCorridor,
  siteLandscapeImagePath,
  siteLandscapeSurfaceRegions,
} from "./siteLandscape";
import type { SiteZone } from "@/types";
import {
  rasterizeResidualLandscapeRegions,
  residualLandscapeBounds,
  type ResidualLandscapeRecipe,
} from "@/components/viewer/globe/residualLandscape";
import { assertSiteLandscapeReady } from "./landscapeCapture";
describe("site landscape protection", () => {
  it("puts the full base below objects while retaining the parcel boundary and legacy holes", () => {
    const zone = {
      coordinates: [
        [0, 0],
        [10, 0],
        [0, 10],
        [0, 0],
      ],
    } as SiteZone;
    const region = {
      id: "remainder",
      kind: "lawn",
      area_sqm: 40,
      minimum_width_m: 0,
      geometry: {
        type: "Polygon",
        coordinates: [
          zone.coordinates,
          [
            [1, 1],
            [1, 3],
            [3, 3],
            [3, 1],
            [1, 1],
          ],
        ],
      },
    };
    const recipe = {
      regions: [region],
      area_sqm: 40,
      occupied_area_sqm: 4,
    } as ResidualLandscapeRecipe;
    const raster = (value: ResidualLandscapeRecipe) =>
      rasterizeResidualLandscapeRegions(
        siteLandscapeSurfaceRegions(zone, value),
        residualLandscapeBounds(zone.coordinates),
        10,
      );
    expect(raster(recipe)[22]).toBe(-1); // legacy object cutout
    const base = raster({ ...recipe, surface_mode: "site_base" });
    expect(base[22]).toBe(0); // ground beneath the object
    expect(base[88]).toBe(-1); // outside the irregular parcel
    expect(recipe.regions).toEqual([region]); // placement regions remain unchanged
  });
  it("buffers the whole access route with a margin and handles zero length", () => {
    const ring = accessCorridor([-114, 51], [-114, 51.0001], 2);
    expect(ring).toHaveLength(5);
    expect(ring[0]).toEqual(ring[4]);
    expect(Math.min(...ring.map((p) => p[0]))).toBeLessThan(-114);
    expect(Math.max(...ring.map((p) => p[0]))).toBeGreaterThan(-114);
    expect(Math.min(...ring.map((p) => p[1]))).toBeLessThan(51);
    expect(accessCorridor([-114, 51], [-114, 51], 2)).toEqual([]);
  });
  it("blocks incomplete custom textures instead of exporting the fallback", () => {
    const scene = new Group(),
      map = new Texture(),
      material = new MeshBasicMaterial({ map });
    scene.add(new Mesh(undefined, material));
    map.userData.siteLandscapeStatus = "loading";
    expect(() => assertSiteLandscapeReady(scene)).toThrow("loading");
    map.userData.siteLandscapeStatus = "failed";
    expect(() => assertSiteLandscapeReady(scene)).toThrow("could not load");
    map.userData.siteLandscapeStatus = "ready";
    expect(() => assertSiteLandscapeReady(scene)).not.toThrow();
  });
});

it("loads saved custom surfaces through the current authenticated API without stale tickets", () => {
  const path = "/api/v1/files/projects/project-a/landscape/1234-abcd.png";
  expect(
    siteLandscapeImagePath(path + "?asset_ticket=expired", "project-a"),
  ).toBe(path);
  expect(
    siteLandscapeImagePath(
      "https://backend.example" + path + "?asset_ticket=expired",
      "project-a",
    ),
  ).toBe(path);
  expect(siteLandscapeImagePath(path, "project-b")).toBeNull();
  expect(
    siteLandscapeImagePath(
      path.replace("1234-abcd.png", "../private.png"),
      "project-a",
    ),
  ).toBeNull();
});
