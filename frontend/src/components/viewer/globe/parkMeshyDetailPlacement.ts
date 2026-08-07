import { resolveContainedParkProgramAnchor } from './parkScatter';
import type { ParkMeshyArchetypeAsset } from './parkMeshyArchetypeAssets';

export interface ParkMeshyDetailPlacement {
  asset: ParkMeshyArchetypeAsset;
  x: number;
  y: number;
  yawRad: number;
}

function polygonAreaM2(ring: readonly (readonly [number, number])[]): number {
  return Math.abs(ring.reduce((area, point, index) => {
    const next = ring[(index + 1) % ring.length];
    return area + point[0] * next[1] - next[0] * point[1];
  }, 0)) / 2;
}

/** Place exact-variant Meshy details in the oriented park frame without ever
 * cropping or scaling them. Objects that do not fit are omitted; only objects
 * explicitly marked repeatOnOversize can gain a mirrored second instance. */
export function resolveParkMeshyDetailPlacements(
  assets: readonly ParkMeshyArchetypeAsset[],
  ring: readonly (readonly [number, number])[],
): ParkMeshyDetailPlacement[] {
  if (ring.length < 3) return [];
  const resolved: ParkMeshyDetailPlacement[] = [];
  const exclusions: Array<{ x: number; y: number; r: number }> = [];
  const areaM2 = polygonAreaM2(ring);

  for (const candidate of assets) {
    const rule = candidate.placement;
    if (!rule) continue;
    const clearanceM = Math.hypot(candidate.dimensionsM[0], candidate.dimensionsM[1]) / 2 + 0.3;
    const first = resolveContainedParkProgramAnchor(
      ring.map((point) => [point[0], point[1]]),
      [rule.u, rule.v],
      clearanceM,
      exclusions,
    );
    if (!first) continue;
    resolved.push({
      asset: candidate,
      x: first.x,
      y: first.y,
      yawRad: first.yawRad + rule.yawDeg * Math.PI / 180,
    });
    exclusions.push({ x: first.x, y: first.y, r: clearanceM });

    if (
      rule.repeatOnOversize
      && areaM2 >= Math.max(2500, candidate.dimensionsM[0] * candidate.dimensionsM[1] * 50)
    ) {
      const repeated = resolveContainedParkProgramAnchor(
        ring.map((point) => [point[0], point[1]]),
        [1 - rule.u, 1 - rule.v],
        clearanceM,
        exclusions,
      );
      if (repeated) {
        resolved.push({
          asset: candidate,
          x: repeated.x,
          y: repeated.y,
          yawRad: repeated.yawRad + rule.yawDeg * Math.PI / 180,
        });
        exclusions.push({ x: repeated.x, y: repeated.y, r: clearanceM });
      }
    }
  }
  return resolved;
}
