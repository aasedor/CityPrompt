import { envelopeFits, type ParkPoint } from './neighborhoodParkLayout';
import { MEADOW_VEGETATION_SPECS, type MeadowVegetationKind } from './meadowVegetationGeometry';

export const MEADOW_TREE_KINDS = ['shade_tree', 'grove_tree', 'ornamental_tree'] as const;

/** Keep the authored trunks and measured support; choose only crowns fitting
 * the whole park. A narrow candidate may use a grove tree, never shrink to fit. */
export function selectMeadowTrees<T extends ParkPoint & { scale: number }>(
  placements: readonly T[], boundary: readonly ParkPoint[],
  fixedObstacles: readonly (ParkPoint & { radius: number })[] = [],
): Array<{ kind: MeadowVegetationKind; placement: T }> {
  return placements.flatMap((p, index) => {
    if (!Number.isFinite(p.scale) || p.scale <= 0) return [];
    const preferred = MEADOW_TREE_KINDS[index % MEADOW_TREE_KINDS.length];
    const kind = [preferred, 'grove_tree' as const].find(candidate => {
      const radius = MEADOW_VEGETATION_SPECS[candidate].radiusM * p.scale;
      // Circumscribed polygon conservatively contains the complete crown disc.
      const r = radius / Math.cos(Math.PI / 24);
      const envelope = Array.from({ length: 24 }, (_, i) => ({
        x: p.x + Math.cos(i * Math.PI / 12) * r,
        y: p.y + Math.sin(i * Math.PI / 12) * r,
      }));
      return envelopeFits(envelope, boundary, .1)
        && fixedObstacles.every(o => Math.hypot(p.x - o.x, p.y - o.y) >= radius + o.radius);
    });
    return kind ? [{ kind, placement: p }] : [];
  });
}

/** A prototype replaces a whole clump within its existing reserved disc. */
export function meadowPlantScale(kind: MeadowVegetationKind, footprintRadiusM: number): number {
  return Math.max(0, footprintRadiusM) / MEADOW_VEGETATION_SPECS[kind].radiusM;
}
