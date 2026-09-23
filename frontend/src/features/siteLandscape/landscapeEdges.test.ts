import { describe, expect, it } from "vitest";
import { landscapeEdgeProbes } from "./landscapeEdges";

describe("landscape edge context sampling", () => {
  it.each([false, true])(
    "samples outside each side regardless of winding (reversed=%s)",
    (reversed) => {
      const ring = [
        [-114, 51],
        [-113.998, 51],
        [-113.998, 51.002],
        [-114, 51.002],
        [-114, 51],
      ];
      const probes = landscapeEdgeProbes(reversed ? [...ring].reverse() : ring);
      expect(probes.length).toBeGreaterThan(8);
      expect(probes.length).toBeLessThanOrEqual(256);
      for (const p of probes) {
        expect(
          p.outsideLng < -114 ||
            p.outsideLng > -113.998 ||
            p.outsideLat < 51 ||
            p.outsideLat > 51.002,
        ).toBe(true);
        expect(p.lng).toBeGreaterThanOrEqual(-114);
        expect(p.lng).toBeLessThanOrEqual(-113.998);
      }
    },
  );
});
