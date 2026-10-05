import { describe, expect, it, vi } from "vitest";
import * as THREE from "three";
import { WGS84_ELLIPSOID } from "3d-tiles-renderer";
import { cityPlanTileGeometry, opaqueMapPixel } from "./cityPlanGeometry";
import type { PlanTile } from "./citywidePlans";

describe("curved policy map tiles", () => {
  const tile: PlanTile = {
    id: "sample",
    rect: [0.25, 0.5, 0.5, 0.75],
    grid: [
      [-114.1, 51.1],
      [-114, 51.1],
      [-114.1, 51],
      [-114, 51],
    ],
  };
  it("uses geographic positions and north-at-top image UVs without stretching corners", () => {
    const origin = WGS84_ELLIPSOID.getCartographicToPosition(
      (51 * Math.PI) / 180,
      (-114 * Math.PI) / 180,
      1000,
      new THREE.Vector3(),
    );
    const geometry = cityPlanTileGeometry(tile, 1, 1000, origin, true);
    const first = new THREE.Vector3()
      .fromBufferAttribute(geometry.attributes.position, 0)
      .add(origin);
    const expected = WGS84_ELLIPSOID.getCartographicToPosition(
      (51.1 * Math.PI) / 180,
      (-114.1 * Math.PI) / 180,
      1000,
      new THREE.Vector3(),
    );
    expect(first.distanceTo(expected)).toBeLessThan(0.002);
    expect([...geometry.attributes.uv.array]).toEqual([
      0.25, 0.5, 0.5, 0.5, 0.25, 0.25, 0.5, 0.25,
    ]);
    expect(geometry.index?.count).toBe(6);
    expect(geometry.boundingSphere?.radius).toBeGreaterThan(6000);
    geometry.dispose();
  });
  it("does not intercept clicks on transparent paper and maps texture UVs to the correct image row", () => {
    const context = {
      clearRect: vi.fn(),
      drawImage: vi.fn(),
      getImageData: vi.fn(() => ({ data: [0, 0, 0, 0] })),
    };
    const image = { naturalWidth: 512, naturalHeight: 512 } as HTMLImageElement;
    expect(
      opaqueMapPixel(
        image,
        new THREE.Vector2(0.5, 0.75),
        context as unknown as CanvasRenderingContext2D,
      ),
    ).toBe(false);
    expect(context.drawImage).toHaveBeenCalledWith(
      image,
      256,
      128,
      1,
      1,
      0,
      0,
      1,
      1,
    );
    context.getImageData.mockReturnValue({ data: [12, 23, 45, 255] });
    expect(
      opaqueMapPixel(
        image,
        new THREE.Vector2(1, 0),
        context as unknown as CanvasRenderingContext2D,
      ),
    ).toBe(true);
    expect(context.drawImage).toHaveBeenLastCalledWith(
      image,
      511,
      511,
      1,
      1,
      0,
      0,
      1,
      1,
    );
  });
});
