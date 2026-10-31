import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

/** Rotate in the same local metre frame used to fit and render native models. */
export function rotateCoordsAroundCentroid(coords: number[][], centroid: [number, number], deltaRad: number): number[][] {
  const cos = Math.cos(deltaRad);
  const sin = Math.sin(deltaRad);
  const [cx, cy] = centroid;
  const lonScale = metersPerDegLon(cy);
  return coords.map((c) => {
    const east = (c[0] - cx) * lonScale;
    const north = (c[1] - cy) * METERS_PER_DEG_LAT;
    return [cx + (east * cos - north * sin) / lonScale,
      cy + (east * sin + north * cos) / METERS_PER_DEG_LAT];
  });
}
