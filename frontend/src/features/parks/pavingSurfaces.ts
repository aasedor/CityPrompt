import { Shape, ShapeGeometry } from "three";
import { parkOutlineProblem } from "@/features/pickPlace/parkOutline";
import {
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from "@/components/viewer/mapEngine/geoUtils";

export const PAVING_MATERIALS = {
  concrete: { label: "Light concrete", color: "#b9b5aa" },
  brick: { label: "Warm brick", color: "#aa7762" },
  asphalt: { label: "Asphalt", color: "#51575a" },
} as const;
export interface PavingSurface {
  id: string;
  material: keyof typeof PAVING_MATERIALS;
  coordinates: number[][];
}
export function pavingProblem(coordinates: number[][]): string | null {
  if (coordinates.length > 64) return "Use up to 64 corners per paved area.";
  if (
    coordinates.some(
      (p) =>
        p.length !== 2 ||
        !p.every(Number.isFinite) ||
        Math.abs(p[0]) > 180 ||
        Math.abs(p[1]) > 85,
    )
  )
    return "Use valid map coordinates.";
  const problem = parkOutlineProblem(coordinates);
  if (problem) return problem.replace(/park/g, "paved area");
  const local = pavingLocalPoints(coordinates);
  const area =
    Math.abs(
      local.reduce((sum, p, i) => {
        const q = local[(i + 1) % local.length];
        return sum + p[0] * q[1] - q[0] * p[1];
      }, 0),
    ) / 2;
  if (
    area > 250000 ||
    Math.max(...local.map((p) => p[0])) - Math.min(...local.map((p) => p[0])) >
      2000 ||
    Math.max(...local.map((p) => p[1])) - Math.min(...local.map((p) => p[1])) >
      2000
  )
    return "Split this into smaller paved areas (up to 250,000 m² and 2 km across).";
  return null;
}
export function pavingLocalPoints(coordinates: number[][]) {
  const [lng, lat] = coordinates[0];
  return coordinates.map((p) => [
    (p[0] - lng) * metersPerDegLon(lat),
    (p[1] - lat) * METERS_PER_DEG_LAT,
  ]);
}
/** Flat, lightweight surface. Geometry is rebuilt on edits, never during walking. */
export function pavingGeometry(coordinates: number[][], heights: number[]) {
  const local = pavingLocalPoints(coordinates);
  const shape = new Shape();
  shape.moveTo(local[0][0], local[0][1]);
  local.slice(1).forEach((p) => shape.lineTo(p[0], p[1]));
  shape.closePath();
  const geometry = new ShapeGeometry(shape);
  const positions = geometry.getAttribute("position");
  for (let i = 0; i < positions.count; i++) {
    const nearest = local.reduce(
      (best, p, j) =>
        Math.hypot(p[0] - positions.getX(i), p[1] - positions.getY(i)) <
        Math.hypot(
          local[best][0] - positions.getX(i),
          local[best][1] - positions.getY(i),
        )
          ? j
          : best,
      0,
    );
    positions.setZ(i, heights[nearest] - heights[0] + 0.025);
  }
  geometry.computeVertexNormals();
  return geometry;
}
