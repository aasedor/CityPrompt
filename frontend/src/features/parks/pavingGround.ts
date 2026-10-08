import { authoredCameraGround } from "@/components/viewer/globe/authoredCameraGround";
import type { SiteZone } from "@/types";

/** The prepared site wins over roofs/vegetation still present in Google tiles. */
export function pavingGroundHeights(
  coordinates: number[][],
  zones: SiteZone[],
  measure: (point: number[]) => number,
) {
  return coordinates.map((p) =>
    authoredCameraGround(zones, p[0], p[1], measure(p)),
  );
}
