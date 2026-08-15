/**
 * legoGlobePlacement.ts — pure math + validation for seating a saved LEGO
 * assembly recipe (Building.specifications.legoAssembly) on the 3D tiles globe.
 *
 * Recipes are planned by the backend in Z-up metres with the origin at the
 * building's bottom-centre. Module GLBs are glTF Y-up, bottom-centre origin,
 * front facade on +Z. Rendering therefore happens in two spaces:
 *
 *   1. Stack space (glTF Y-up) — each instance's backend [x, y, z-up]
 *      position becomes three.js [x, z, y] and its [sx, sy, sz] scale becomes
 *      [sx, sz, sy], exactly mirroring legoShared.ModuleInstance (the
 *      composer preview). Instance scales already contain the planner's fit
 *      stretch — they are applied verbatim, never contain-fit again.
 *   2. Globe space (ENU Z-up inside an EastNorthUpFrame) — the whole stack is
 *      wrapped in the same Rx(+90°) Y-up -> Z-up group + yaw group that
 *      GlobeBuildingModelsLayer uses for whole Meshy models.
 */

import type { Building } from '@/types';
import type { LegoAssemblyInstance, LegoAssemblyRecipe } from '@/features/legoAssembly/legoAssemblyApi';

const DEG_TO_RAD = Math.PI / 180;

export interface PlannedMassingSpec {
  schema_version: 1;
  source: 'community_3d';
  source_zone_id: string;
  archetype_id: string | null;
  floor_count: number | null;
  height_meters: number;
}

function isFiniteTriple(value: unknown): value is [number, number, number] {
  return Array.isArray(value) && value.length === 3 && value.every((n) => Number.isFinite(n));
}

function isValidInstance(value: unknown): value is LegoAssemblyInstance {
  if (!value || typeof value !== 'object') return false;
  const instance = value as Partial<LegoAssemblyInstance>;
  return (
    typeof instance.model_url === 'string'
    && instance.model_url.length > 0
    && isFiniteTriple(instance.position)
    && isFiniteTriple(instance.scale)
    && (instance.rotation_degrees === undefined || Number.isFinite(instance.rotation_degrees))
  );
}

/**
 * Parse + validate the saved assembly recipe off a building's specifications.
 * Tolerates both snake_case (backend contract) and camelCase version keys.
 * Returns null for anything that is not a complete, renderable v1 recipe —
 * a malformed recipe must fall back to the Meshy model / zone prism, never
 * crash the globe.
 */
export function extractLegoRecipe(building: Building): LegoAssemblyRecipe | null {
  const raw = building.specifications?.legoAssembly;
  if (!raw || typeof raw !== 'object') return null;
  const recipe = raw as Partial<LegoAssemblyRecipe> & { schemaVersion?: number };
  const version = recipe.schema_version ?? recipe.schemaVersion;
  if (version !== 1) return null;
  if (!Array.isArray(recipe.instances) || recipe.instances.length === 0) return null;
  if (!recipe.instances.every(isValidInstance)) return null;
  const target = recipe.target;
  if (!target || !(Number(target.width_m) > 0) || !(Number(target.depth_m) > 0)) return null;
  return recipe as LegoAssemblyRecipe;
}

/** Parse the honest exact-footprint fallback used while an archetype family is
 * unavailable. It is deliberately distinct from a LEGO recipe: no unrelated
 * facade or module family is implied. */
export function extractPlannedMassing(building: Building): PlannedMassingSpec | null {
  const raw = building.specifications?.plannedMassing;
  if (!raw || typeof raw !== 'object') return null;
  const massing = raw as Partial<PlannedMassingSpec>;
  if (
    massing.schema_version !== 1
    || massing.source !== 'community_3d'
    || typeof massing.source_zone_id !== 'string'
    || massing.source_zone_id.length === 0
    || !(Number(massing.height_meters) > 0)
  ) return null;
  return massing as PlannedMassingSpec;
}

function validRing(ring: unknown): number[][] | null {
  if (!Array.isArray(ring)) return null;
  const pts = ring.filter(
    (c) => Array.isArray(c) && c.length >= 2 && Number.isFinite(c[0]) && Number.isFinite(c[1]),
  );
  return pts.length >= 3 ? (pts as number[][]) : null;
}

/** Footprint ring for LEGO placement. The owning zone's CURRENT ring wins when
 *  provided: rotating/moving/reshaping a zone edits only zone coordinates, and
 *  placement must follow live — the stored building footprint is the fallback
 *  compile-time truth (regenerate re-fits the modules to the new ring). */
export function legoFootprintRing(
  building: Building,
  owningZoneRing?: number[][] | null,
): number[][] | null {
  return validRing(owningZoneRing) ?? validRing(building.footprint_coordinates);
}

/** True when the building will actually render as a LEGO stack on the globe:
 *  a valid v1 recipe AND a usable footprint ring. */
export function recipeIsRenderable(building: Building): boolean {
  return extractLegoRecipe(building) !== null && legoFootprintRing(building) !== null;
}

/** Building ids whose persisted LEGO recipes are sufficient to replace the
 * editable planning prism. Suppression follows this durable render contract,
 * rather than a transient loader callback that can reset during hot reload or
 * a WebGL layer handoff while the authored model remains visible. */
export function renderableLegoBuildingIds(buildings: readonly Building[]): Set<string> {
  return new Set(
    buildings
      .filter(recipeIsRenderable)
      .map((building) => building.id),
  );
}

/** Any valid saved recipe, footprint or not — drives the layer mount so the
 *  layer itself can debug-count recipe-without-footprint skips. */
export function hasLegoRecipe(building: Building): boolean {
  return extractLegoRecipe(building) !== null;
}

export function hasPlannedMassing(building: Building): boolean {
  return extractPlannedMassing(building) !== null && legoFootprintRing(building) !== null;
}

/**
 * Coexistence filter: buildings whose recipe renders as a LEGO stack are
 * excluded from GlobeBuildingModelsLayer (the stack wins over the Meshy GLB).
 * A building with a recipe but no footprint keeps its Meshy model — the stack
 * can't place, so suppressing the model would leave nothing.
 */
export function excludeLegoStackBuildings(buildings: Building[]): Building[] {
  return buildings.filter((building) => (
    !recipeIsRenderable(building) && !hasPlannedMassing(building)
  ));
}

export interface LegoInstanceThreeTransform {
  /** three.js position in stack space (glTF Y-up, metres). */
  position: [number, number, number];
  /** Rotation about three.js Y (stack-space up). */
  rotationYRad: number;
  /** three.js scale in stack space. */
  scale: [number, number, number];
}

export interface LegoModuleVerticalExtent {
  /** Instance origin in stack-space Y (the eventual globe Up axis). */
  positionY: number;
  /** Instance scale on stack-space Y. Negative scales are supported. */
  scaleY: number;
  /** Authored GLB bounds before the instance transform. */
  boundsMinY: number;
  boundsMaxY: number;
}

/**
 * Translate a complete LEGO stack so its lowest transformed vertex is exactly
 * at the recipe ground datum. Family assets are intended to use a bottom-
 * centre origin, but older/high-detail GLBs can carry centred or offset origins.
 * Trusting the origin alone buries those families by one or more storeys.
 */
export function computeLegoStackBaseLift(
  extents: readonly LegoModuleVerticalExtent[],
): number {
  let stackMinY = Number.POSITIVE_INFINITY;
  for (const extent of extents) {
    const values = [
      extent.positionY,
      extent.scaleY,
      extent.boundsMinY,
      extent.boundsMaxY,
    ];
    if (!values.every(Number.isFinite)) continue;
    const scaledMin = Math.min(
      extent.boundsMinY * extent.scaleY,
      extent.boundsMaxY * extent.scaleY,
    );
    stackMinY = Math.min(stackMinY, extent.positionY + scaledMin);
  }
  if (!Number.isFinite(stackMinY) || Math.abs(stackMinY) < 1e-6) return 0;
  return -stackMinY;
}

/**
 * Backend Z-up instance placement -> three.js Y-up stack space. Mirrors
 * legoShared.ModuleInstance exactly: position [x, y, z-up] -> [x, z, y],
 * scale [sx, sy, sz] -> [sx, sz, sy], rotation negated about Y.
 */
export function legoInstanceTransform(instance: LegoAssemblyInstance): LegoInstanceThreeTransform {
  const [x, y, z] = instance.position;
  const [sx, sy, sz] = instance.scale;
  return {
    position: [x, z, y],
    scale: [sx, sz, sy],
    rotationYRad: -(instance.rotation_degrees ?? 0) * DEG_TO_RAD,
  };
}

/**
 * Yaw of the whole stack about ENU Up, mirroring computeModelPlacement's
 * modelAxisAngle logic. The recipe's plan orientation is known exactly (no
 * bbox guessing needed): target width_m spans stack-space X and target
 * depth_m spans stack-space Z, so the stack's long plan axis is X when
 * width_m >= depth_m and Z otherwise. Aligning that long axis with the
 * footprint's long axis (frame.bearingRad) makes the module front facade
 * (+Z in glTF space, ENU -North before yaw after the Rx(+90°) wrapper) face
 * the footprint's short-axis street side — same behavior as whole models.
 */
export function computeLegoStackYaw(
  bearingRad: number,
  target: Pick<LegoAssemblyRecipe['target'], 'width_m' | 'depth_m'>,
  rotationDegrees: number | null | undefined,
): number {
  const stackAxisAngle = target.width_m >= target.depth_m ? 0 : -Math.PI / 2;
  return bearingRad - stackAxisAngle + (rotationDegrees ?? 0) * DEG_TO_RAD;
}

/** Distinct module URLs in a recipe (repeated floors share one GLB — drei's
 *  useGLTF caches per URL, so clones are cheap). */
export function uniqueModuleUrls(recipe: LegoAssemblyRecipe): string[] {
  return Array.from(new Set(recipe.instances.map((instance) => instance.model_url)));
}
