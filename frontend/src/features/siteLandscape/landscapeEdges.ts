import { Matrix4, Vector3 } from "three";
import { WGS84_ELLIPSOID } from "3d-tiles-renderer";
import {
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from "@/components/viewer/mapEngine/geoUtils";
import type { Direct3DCaptureBundle } from "@/components/viewer/globe/direct3dCapture";
import type { SiteZone } from "@/types";

export interface LandscapeEdgeSample {
  lng: number;
  lat: number;
  color: [number, number, number];
}

/** Dense probes just outside the boundary; direction follows ring winding. */
export function landscapeEdgeProbes(boundary: number[][]) {
  const ring = boundary.filter(
    (p, i) => i === 0 || p[0] !== boundary[0][0] || p[1] !== boundary[0][1],
  );
  if (ring.length < 3) return [];
  const mx = metersPerDegLon(ring[0][1]),
    my = METERS_PER_DEG_LAT;
  const segments = ring.map((a, i) => {
    const b = ring[(i + 1) % ring.length];
    const dx = (b[0] - a[0]) * mx,
      dy = (b[1] - a[1]) * my;
    return { a, b, dx, dy, length: Math.hypot(dx, dy) };
  });
  const winding =
    Math.sign(
      segments.reduce((area, { a, b }) => area + a[0] * b[1] - b[0] * a[1], 0),
    ) || 1;
  const step = Math.max(
    3,
    segments.reduce((n, s) => n + s.length, 0) / Math.max(1, 256 - ring.length),
  );
  return segments
    .flatMap(({ a, b, dx, dy, length }) => {
      if (length < 0.01) return [];
      return Array.from({ length: Math.ceil(length / step) }, (_, i) => {
        const t = (i + 0.5) / Math.ceil(length / step);
        const lng = a[0] + (b[0] - a[0]) * t,
          lat = a[1] + (b[1] - a[1]) * t;
        return {
          lng,
          lat,
          outsideLng: lng + (((winding * dy) / length) * 4) / mx,
          outsideLat: lat - (((winding * dx) / length) * 4) / my,
        };
      });
    })
    .slice(0, 256);
}

/** Read colour only from visible context, never the proposal or an empty tile. */
export async function landscapeEdgeSamples(
  capture: Direct3DCaptureBundle,
  zone: SiteZone,
): Promise<LandscapeEdgeSample[]> {
  const decode = async (data: string) =>
    createImageBitmap(
      await (
        await fetch(
          data.startsWith("data:") ? data : `data:image/png;base64,${data}`,
        )
      ).blob(),
    );
  const [beauty, mask] = await Promise.all([
    decode(capture.beautyImageBase64),
    decode(capture.proposalMaskBase64),
  ]);
  try {
    const canvas = document.createElement("canvas");
    canvas.width = capture.width;
    canvas.height = capture.height;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    if (!ctx) throw new Error("Could not read the landscape edges.");
    ctx.drawImage(beauty, 0, 0, canvas.width, canvas.height);
    const rgb = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    ctx.drawImage(mask, 0, 0, canvas.width, canvas.height);
    const proposal = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    const projection = new Matrix4()
      .fromArray(capture.camera.projection_matrix)
      .multiply(new Matrix4().fromArray(capture.camera.matrix_world).invert());
    const height = Number(zone.properties?.terrain_elevation_m ?? 0);
    const samples: LandscapeEdgeSample[] = [];
    for (const probe of landscapeEdgeProbes(zone.coordinates)) {
      const point = new Vector3();
      WGS84_ELLIPSOID.getCartographicToPosition(
        (probe.outsideLat * Math.PI) / 180,
        (probe.outsideLng * Math.PI) / 180,
        height,
        point,
      );
      point.applyMatrix4(projection);
      const x = Math.round((point.x + 1) * 0.5 * canvas.width),
        y = Math.round((1 - point.y) * 0.5 * canvas.height);
      const values: number[][] = [];
      for (let dy = -2; dy <= 2; dy++)
        for (let dx = -2; dx <= 2; dx++) {
          const px = x + dx,
            py = y + dy;
          if (px < 0 || py < 0 || px >= canvas.width || py >= canvas.height)
            continue;
          const k = (py * canvas.width + px) * 4;
          if (proposal[k] > 127) continue;
          const color = [rgb[k], rgb[k + 1], rgb[k + 2]];
          const light = color.reduce((a, b) => a + b) / 3;
          if (light > 25 && light < 240) values.push(color);
        }
      if (values.length >= 4)
        samples.push({
          lng: probe.lng,
          lat: probe.lat,
          color: [0, 1, 2].map(
            (c) =>
              values.map((v) => v[c]).sort((a, b) => a - b)[
                Math.floor(values.length / 2)
              ],
          ) as [number, number, number],
        });
    }
    if (samples.length < 8)
      throw new Error(
        "Let the surrounding Google tiles load so the landscape edges can blend naturally.",
      );
    return samples;
  } finally {
    beauty.close();
    mask.close();
  }
}
