import { describe, it, expect } from "vitest";
import { rectangleAt } from "@/features/pickPlace/geometry";
import type { SiteZone } from "@/types";
import { pavingGroundHeights } from "./pavingGround";
describe("paving ground", () => {
  it("uses the cleared site surface rather than the original building heights", () => {
    const boundary = {
      id: "site",
      project_id: "trial",
      color: "#777777",
      sort_order: 0,
      created_at: "2026-10-08",
      updated_at: "2026-10-08",
      zone_type: "site_boundary",
      is_active_boundary: true,
      coordinates: rectangleAt([-114, 51], 300, 300),
      properties: {
        terrain_elevation_m: 1103,
        community_3d_mask_existing_tiles: true,
      },
    } as SiteZone;
    const points = rectangleAt([-114, 51], 120, 28);
    expect(pavingGroundHeights(points, [boundary], () => 1125)).toEqual([
      1103, 1103, 1103, 1103,
    ]);
    expect(pavingGroundHeights(points, [], () => 1125)).toEqual([
      1125, 1125, 1125, 1125,
    ]);
  });
});
