import { describe, expect, it } from "vitest";
import {
  buildParkTrio,
  PARK_TRIO,
  PARK_TRIO_REVISION,
  parkTrioKind,
  rect,
  type ParkTrioKind,
} from "./parkTrioLayout";
import {
  envelopeFits,
  envelopesOverlap,
  type ParkPoint,
} from "./neighborhoodParkLayout";
import { resolveManualParkAccess } from "./parkAccessConnections";
import {
  resolveParkGroundProfile,
  resolveParkSpecialtyStructureKind,
} from "./parkGroundProfiles";
import { METERS_PER_DEG_LAT, metersPerDegLon } from "../mapEngine/geoUtils";
import { bufferLineToPolygon } from "@/utils/roadGeometry";
import type { SiteZone } from "@/types";

const kinds = Object.keys(PARK_TRIO) as ParkTrioKind[];
const turn = (p: ParkPoint, a: number) => ({
  x: p.x * Math.cos(a) - p.y * Math.sin(a) + 120,
  y: p.x * Math.sin(a) + p.y * Math.cos(a) - 37,
});
describe("new park trio: whole metric objects in adaptive plots", () => {
  for (const kind of kinds)
    for (const scale of ["minimum", "standard", "large"] as const) {
      const info = PARK_TRIO[kind];
      const [w, d] =
        scale === "minimum"
          ? info.min
          : info.size.map((v) => v * (scale === "large" ? 1.3 : 1));
      it(`${kind} fits ${scale} and rotated plots without stretching or overlaps`, () => {
        const ring = rect(0, 0, w, d),
          layout = buildParkTrio(kind, ring),
          rotated = buildParkTrio(
            kind,
            ring.map((p) => turn(p, 0.44)),
          );
        expect(layout.status).not.toBe("constrained");
        expect(layout.modules.length).toBeGreaterThan(2);
        expect(rotated.modules.map((m) => m.id)).toEqual(
          layout.modules.map((m) => m.id),
        );
        expect(rotated.paths.length).toBe(layout.paths.length);
        for (let i = 0; i < layout.modules.length; i++) {
          const m = layout.modules[i],
            r = rotated.modules[i],
            expected = turn(m.center, 0.44);
          expect(r.width).toBe(m.width);
          expect(r.depth).toBe(m.depth);
          expect(r.center.x).toBeCloseTo(expected.x, 6);
          expect(r.center.y).toBeCloseTo(expected.y, 6);
          expect(envelopeFits(m.envelope, ring, 0.39)).toBe(true);
          for (const other of layout.modules)
            if (other !== m)
              expect(envelopesOverlap(m.envelope, other.envelope)).toBe(false);
        }
        expect(layout.trees.length).toBeGreaterThan(6);
        expect(layout.trees.length).toBeLessThanOrEqual(48);
        expect(buildParkTrio(kind, ring)).toEqual(layout);
        for (const path of layout.paths)
          for (let i = 0; i < path.points.length - (path.closed ? 0 : 1); i++) {
            const a = path.points[i],
              b = path.points[(i + 1) % path.points.length],
              len = Math.hypot(b.x - a.x, b.y - a.y);
            const nx = ((-(b.y - a.y) / len) * path.width) / 2,
              ny = (((b.x - a.x) / len) * path.width) / 2;
            expect(
              envelopeFits(
                [
                  { x: a.x + nx, y: a.y + ny },
                  { x: b.x + nx, y: b.y + ny },
                  { x: b.x - nx, y: b.y - ny },
                  { x: a.x - nx, y: a.y - ny },
                ],
                ring,
                0.04,
              ),
            ).toBe(true);
          }
      });
    }
  it.each(kinds)(
    "%s reports unsuitable plots without cropped structures",
    (kind) => {
      for (const ring of [
        rect(0, 0, 12, 100),
        [
          { x: 0, y: 0 },
          { x: 100, y: 0 },
          { x: 100, y: 30 },
          { x: 30, y: 30 },
          { x: 30, y: 100 },
          { x: 0, y: 100 },
        ],
        [],
      ]) {
        const layout = buildParkTrio(kind, ring);
        expect(layout.status).toBe("constrained");
        expect(layout.modules).toHaveLength(0);
        expect(layout.paths).toHaveLength(0);
      }
    },
  );
  it("only activates the exact parent, variant and explicit pilot revision", () => {
    for (const kind of kinds) {
      const info = PARK_TRIO[kind],
        zone = {
          zone_type: "green_space" as const,
          properties: {
            green_space_archetype_id: info.parent,
            green_space_selected_variant_id: info.variant,
            park_trio_layout: PARK_TRIO_REVISION,
          },
        };
      expect(parkTrioKind(zone)).toBe(kind);
      expect(
        parkTrioKind({
          ...zone,
          properties: { ...zone.properties, park_trio_layout: undefined },
        }),
      ).toBeNull();
      expect(
        parkTrioKind({
          ...zone,
          properties: {
            ...zone.properties,
            green_space_selected_variant_id: "different",
          },
        }),
      ).toBeNull();
    }
  });
  it("keeps garden labels, beds and a connected court at the minimum size", () => {
    const [w, d] = PARK_TRIO.garden.min,
      l = buildParkTrio("garden", rect(0, 0, w, d));
    expect(l.modules.filter((m) => m.asset === "garden/bed")).toHaveLength(6);
    expect(l.modules.filter((m) => m.asset === "garden/label")).toHaveLength(6);
    expect(envelopeFits(l.courtyard!, l.boundary)).toBe(true);
  });
  it.each(kinds)(
    "%s connects its real loop to an adjacent authored sidewalk",
    (kind) => {
      const info = PARK_TRIO[kind],
        [w, d] = info.size;
      const ll = (x: number, y: number): [number, number] => [
        -114 + x / metersPerDegLon(51),
        51 + y / METERS_PER_DEG_LAT,
      ];
      const park: SiteZone = {
        id: "park",
        project_id: "test",
        zone_type: "green_space",
        coordinates: rect(0, 0, w, d).map((p) => ll(p.x, p.y)),
        properties: {
          green_space_archetype_id: info.parent,
          green_space_selected_variant_id: info.variant,
          park_trio_layout: PARK_TRIO_REVISION,
        },
        color: "#789",
        sort_order: 0,
        created_at: "2026-09-06",
        updated_at: "2026-09-06",
      };
      const line = [ll(-w / 2 - 10, -d / 2 - 6), ll(w / 2 + 10, -d / 2 - 6)];
      const street: SiteZone = {
        ...park,
        id: "street",
        zone_type: "road",
        coordinates: bufferLineToPolygon(line, 10),
        properties: {
          road_archetype_id: "narrow_residential_street",
          width: 10,
          plan_centerline: line,
        },
      };
      expect(resolveParkSpecialtyStructureKind(park)).toBe(
        "park_trio_assembly",
      );
      expect(resolveParkGroundProfile(park).guides.some((g) => g.closed)).toBe(
        true,
      );
      const boundary: SiteZone = {
        ...park,
        id: "site",
        zone_type: "site_boundary",
        is_active_boundary: true,
        coordinates: rect(0, 0, w + 60, d + 60).map((p) => ll(p.x, p.y)),
        properties: { terrain_elevation_m: 1000 },
      };
      const access = resolveManualParkAccess([park, street, boundary]).parks[0];
      expect(access.status, access.reason).toBe("connected");
      expect(access.connections.length).toBeGreaterThan(0);
      expect(access.connections[0].streetBand).toBe("sidewalk");
    },
  );
});
