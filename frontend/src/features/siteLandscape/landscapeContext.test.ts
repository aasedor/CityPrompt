import type { SiteZone } from "@/types";
import { describe, expect, it } from "vitest";
import { PerspectiveCamera, Vector3 } from "three";
import { WGS84_ELLIPSOID } from "3d-tiles-renderer";
import {
  frameLandscapeContext,
  landscapeContextImage,
} from "./landscapeContext";
import type { Direct3DCaptureBundle } from "@/components/viewer/globe/direct3dCapture";

describe("landscape neighbourhood reference", () => {
  it.each([0.65, 1.6])(
    "includes a margin around the full parcel at aspect %s and restores the camera",
    (aspect) => {
      const camera = new PerspectiveCamera(45, aspect, 1, 1e8);
      camera.position.set(10, 20, 30);
      camera.rotation.set(0.2, 0.3, 0.1);
      const saved = camera.clone();
      const controls = { enabled: true, pivotPoint: new Vector3(1, 2, 3) };
      const boundary = [
        [-114.14, 51.01],
        [-114.138, 51.01],
        [-114.1375, 51.013],
        [-114.14, 51.013],
      ];
      const restore = frameLandscapeContext(camera, boundary, 1100, controls);
      try {
        expect(controls.enabled).toBe(false);
        for (const [lng, lat] of boundary) {
          const point = new Vector3();
          WGS84_ELLIPSOID.getCartographicToPosition(
            (lat * Math.PI) / 180,
            (lng * Math.PI) / 180,
            1100,
            point,
          );
          point.project(camera);
          expect(Math.abs(point.x)).toBeLessThan(0.85);
          expect(Math.abs(point.y)).toBeLessThan(0.85);
        }
      } finally {
        restore();
      }
      expect(camera.position.toArray()).toEqual(saved.position.toArray());
      expect(camera.quaternion.toArray()).toEqual(saved.quaternion.toArray());
      expect(camera.up.toArray()).toEqual(saved.up.toArray());
      expect(controls).toEqual({
        enabled: true,
        pivotPoint: new Vector3(1, 2, 3),
      });
    },
  );
  it("rejects an absent neighbourhood rather than spending tokens without context", () => {
    const capture = {
      width: 100,
      height: 100,
      contextPixelCount: 500,
      proposalPixelCount: 9000,
      beautyImageBase64: "data:image/png;base64,scene-pixels",
    } as Direct3DCaptureBundle;
    expect(() => landscapeContextImage(capture)).toThrow("Google tiles");
    expect(landscapeContextImage({ ...capture, contextPixelCount: 3000 })).toBe(
      "scene-pixels",
    );
  });
});

it("requires the compiled development to be present and visible in its neighbourhood reference", () => {
  const zone = {
    id: "home",
    project_id: "project",
    coordinates: [
      [-114, 51],
      [-114, 51.001],
      [-114.001, 51],
    ],
    color: "#aaa",
    sort_order: 0,
    created_at: "now",
    updated_at: "now",
    zone_type: "building",
    properties: {
      community_3d: {
        schema_version: 1,
        state: "compiled",
        kind: "building",
        generator: "test",
        compiled_at: "now",
      },
    },
  } as SiteZone;
  const capture = {
    width: 100,
    height: 100,
    contextPixelCount: 3000,
    proposalPixelCount: 7000,
    beautyImageBase64: "scene",
    instanceIdManifest: {},
  } as Direct3DCaptureBundle;
  expect(() => landscapeContextImage(capture, [zone])).toThrow(
    "whole development",
  );
  capture.instanceIdManifest = {
    home: { instance_id: "home", zone_id: "home", semantic_class: "building" },
  };
  capture.instancePixelCounts = { home: 0 };
  expect(() => landscapeContextImage(capture, [zone])).toThrow(
    "whole development",
  );
  capture.instancePixelCounts = { home: 100 };
  expect(landscapeContextImage(capture, [zone])).toBe("scene");
});
