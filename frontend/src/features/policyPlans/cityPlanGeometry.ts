import * as THREE from "three";
import { WGS84_ELLIPSOID } from "3d-tiles-renderer";
import type { PlanTile } from "./citywidePlans";

export function cityPlanTileGeometry(
  tile: PlanTile,
  gridSize: number,
  height: number,
  origin: THREE.Vector3,
  overview: boolean,
) {
  const position: number[] = [],
    uv: number[] = [],
    indices: number[] = [];
  const point = new THREE.Vector3();
  for (let row = 0; row <= gridSize; row++)
    for (let col = 0; col <= gridSize; col++) {
      const [lon, lat] = tile.grid[row * (gridSize + 1) + col];
      WGS84_ELLIPSOID.getCartographicToPosition(
        (lat * Math.PI) / 180,
        (lon * Math.PI) / 180,
        height,
        point,
      );
      position.push(...point.sub(origin).toArray());
      const u = col / gridSize,
        v = row / gridSize;
      uv.push(
        overview ? tile.rect[0] + u * (tile.rect[2] - tile.rect[0]) : u,
        1 - (overview ? tile.rect[1] + v * (tile.rect[3] - tile.rect[1]) : v),
      );
      if (row < gridSize && col < gridSize) {
        const a = row * (gridSize + 1) + col,
          b = a + 1,
          c = a + gridSize + 1,
          d = c + 1;
        indices.push(a, c, b, b, c, d);
      }
    }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(position, 3),
  );
  geometry.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  geometry.setIndex(indices);
  geometry.computeBoundingSphere();
  return geometry;
}

/** Match a map pixel, ignoring transparent paper and off-map margins. */
export function opaqueMapPixel(
  image: HTMLImageElement,
  uv: THREE.Vector2,
  context: CanvasRenderingContext2D,
): boolean {
  if (!image.naturalWidth || !image.naturalHeight) return false;
  const x = Math.max(
    0,
    Math.min(image.naturalWidth - 1, Math.floor(uv.x * image.naturalWidth)),
  );
  const y = Math.max(
    0,
    Math.min(
      image.naturalHeight - 1,
      Math.floor((1 - uv.y) * image.naturalHeight),
    ),
  );
  context.clearRect(0, 0, 1, 1);
  context.drawImage(image, x, y, 1, 1, 0, 0, 1, 1);
  return context.getImageData(0, 0, 1, 1).data[3] > 24;
}
