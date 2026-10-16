import { afterEach, describe, expect, it, vi } from "vitest";
import { PerspectiveCamera } from "three";
import type { Direct3DCaptureBundle } from "@/components/viewer/globe/direct3dCapture";
import type { SiteZone } from "@/types";
import { frameLandscapeContext } from "./landscapeContext";
import { landscapeEdgeProbes, landscapeEdgeSamples } from "./landscapeEdges";

afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); });

describe("landscape edge context sampling", () => {
  it.each([false, true])("samples local capture images without fetch under production CSP (data URL=%s)", async (dataUrl) => {
    const fetchMock = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));
    vi.stubGlobal("fetch", fetchMock);
    const beauty = { close: vi.fn() }, mask = { close: vi.fn() };
    const decode = vi.fn().mockResolvedValueOnce(beauty).mockResolvedValueOnce(mask);
    vi.stubGlobal("createImageBitmap", decode);
    let image: unknown;
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue({
      drawImage: (value: unknown) => { image = value; },
      getImageData: () => ({ data: new Uint8ClampedArray(64 * 64 * 4).fill(image === beauty ? 120 : 0) }),
    } as unknown as ReturnType<HTMLCanvasElement["getContext"]>);
    const zone = { coordinates: [[-114, 51], [-113.998, 51], [-113.998, 51.002], [-114, 51.002], [-114, 51]], properties: { terrain_elevation_m: 1100 } } as unknown as SiteZone;
    const camera = new PerspectiveCamera(45, 1, 1, 1e8);
    frameLandscapeContext(camera, zone.coordinates, 1100);
    const png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aV9sAAAAASUVORK5CYII=";
    const capture = { width: 64, height: 64, beautyImageBase64: dataUrl ? `data:image/png;base64,${png}` : png, proposalMaskBase64: `data:image/png;base64,${png}`, camera: { projection_matrix: camera.projectionMatrix.toArray(), matrix_world: camera.matrixWorld.toArray() } } as unknown as Direct3DCaptureBundle;
    const samples = await landscapeEdgeSamples(capture, zone);
    expect(samples.length).toBeGreaterThanOrEqual(8);
    expect(samples.every(s => s.color.join(",") === "120,120,120")).toBe(true);
    expect(fetchMock).not.toHaveBeenCalled();
    expect(decode).toHaveBeenCalledTimes(2);
    expect(decode.mock.calls[0][0]).toBeInstanceOf(Blob);
    expect(decode.mock.calls[0][0].type).toBe("image/png");
    expect(beauty.close).toHaveBeenCalledOnce();
    expect(mask.close).toHaveBeenCalledOnce();
  });
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
