import type { SiteZone } from '@/types';
import { getApiErrorMessage } from '@/services/api';
import {
  getCommunity3DMeta,
  isCommunity3DCompiled,
  resolveCommunity3DKind,
  type Community3DKind,
} from '@/features/community3d/community3d';
import { allSettledWithConcurrency } from './allSettledWithConcurrency';
import { analyzeLegoFootprint } from './footprintProfiles';
import {
  legoArchetypeContextFromZone,
  legoAssemblyApi,
  type Community3DCompileResponse,
  type LegoAssemblyPlan,
  type LegoAssemblyRecipe,
  type LegoFootprintProfile,
} from './legoAssemblyApi';
import {
  deriveZoneTargets,
  findZoneCatalogOption,
  normalizeArchetypeId,
} from './legoShared';

const BUILDABLE_ZONE_TYPES = new Set<string>([
  'building',
  'residential',
  'development_area',
  'development',
]);
const METRES_PER_DEG_LAT = 110540;
const METRES_PER_DEG_LNG_EQUATOR = 111320;

export function isCommunityBuildingZone(zone: SiteZone): boolean {
  return resolveCommunity3DKind(zone) === 'building'
    && (
      BUILDABLE_ZONE_TYPES.has(zone.zone_type)
      || Boolean(zone.properties?.development_archetype_id)
    );
}

export interface GroundBuildItem {
  zone: SiteZone;
  kind: Extract<Community3DKind, 'park' | 'street'>;
  state: 'ready' | 'compiling' | 'compiled' | 'failed';
}

export function deriveGroundItems(zones: SiteZone[]): GroundBuildItem[] {
  return zones.flatMap((zone) => {
    const kind = resolveCommunity3DKind(zone);
    if (kind !== 'park' && kind !== 'street') return [];
    return [{ zone, kind, state: isCommunity3DCompiled(zone) ? 'compiled' : 'ready' }];
  });
}

function polygonCentroid(coordinates: number[][] | undefined): [number, number] | null {
  if (!coordinates || coordinates.length === 0) return null;
  let lng = 0;
  let lat = 0;
  let count = 0;
  for (const vertex of coordinates) {
    if (!Array.isArray(vertex) || vertex.length < 2) continue;
    const [vLng, vLat] = vertex;
    if (!Number.isFinite(vLng) || !Number.isFinite(vLat)) continue;
    lng += vLng;
    lat += vLat;
    count += 1;
  }
  if (count === 0) return null;
  return [lng / count, lat / count];
}

export interface ZoneBuildItem {
  zone: SiteZone;
  label: string;
  archetypeId?: string;
  targets: {
    width_m: number;
    depth_m: number;
    floors: number;
    footprint_profile: LegoFootprintProfile;
    wing_depth_m?: number;
    within_recommended_size: boolean;
  };
  offset: [number, number] | null;
  plan?: LegoAssemblyPlan;
  error?: string;
  familyMissing?: boolean;
  placeState?: 'placing' | 'placed' | 'failed';
  massingState?: 'compiling' | 'compiled' | 'failed';
}

export function recipeFromPlan(
  item: ZoneBuildItem & { plan: LegoAssemblyPlan },
): LegoAssemblyRecipe & { building_name: string } {
  const context = legoArchetypeContextFromZone(item.zone.properties);
  return {
    schema_version: 1,
    module_family: item.plan.family,
    archetype_id: item.plan.archetype_id ?? context.archetype_id ?? null,
    reuse_keys: item.plan.reuse_keys,
    target: item.plan.target,
    instances: item.plan.instances,
    assembled_height_m: item.plan.assembled_height_m,
    fit: item.plan.fit,
    assembled_preview_url: null,
    building_name: item.label,
  };
}

/** Shared zone-to-module derivation used by both LEGO Builder and the Render
 * panel's Generate Community 3D action. Keeping this in one module prevents
 * the two user entry points from drifting in footprint, floor, or family
 * selection behaviour. */
export function deriveItems(zones: SiteZone[]): ZoneBuildItem[] {
  const buildable = zones.filter(isCommunityBuildingZone);
  const centroids = buildable.map((zone) => polygonCentroid(zone.coordinates));
  const anchors = centroids.filter((candidate): candidate is [number, number] => candidate !== null);

  let lng0 = 0;
  let lat0 = 0;
  for (const [lng, lat] of anchors) {
    lng0 += lng;
    lat0 += lat;
  }
  if (anchors.length > 0) {
    lng0 /= anchors.length;
    lat0 /= anchors.length;
  }
  const metresPerDegLng = METRES_PER_DEG_LNG_EQUATOR * Math.cos((lat0 * Math.PI) / 180);

  return buildable.map((zone, index) => {
    const context = legoArchetypeContextFromZone(zone.properties);
    const option = findZoneCatalogOption(context.archetype_id, zone.properties);
    const centroid = centroids[index];
    const archetypeLabel = zone.properties?.development_archetype_label;
    const defaults = deriveZoneTargets(option, zone.properties);
    // The drawn parcel is the source of truth for assembly dimensions even
    // when an older catalogue option has no footprintCompatibility metadata.
    // Falling back to the catalogue's nominal 25 x 20 m box made a 44 x 36 m
    // parcel render at roughly half size and broke the render-to-model loop.
    const footprint = analyzeLegoFootprint(
      zone.coordinates,
      option?.footprintCompatibility,
    );
    const communityMeta = getCommunity3DMeta(zone);
    return {
      zone,
      label:
        zone.name
        || option?.label
        || (typeof archetypeLabel === 'string' && archetypeLabel ? archetypeLabel : undefined)
        || normalizeArchetypeId(context.archetype_id)
        || zone.zone_type,
      archetypeId: normalizeArchetypeId(context.archetype_id),
      targets: {
        ...defaults,
        width_m: footprint?.width_m ?? defaults.width_m,
        depth_m: footprint?.depth_m ?? defaults.depth_m,
        footprint_profile: footprint?.profile ?? 'rectangle',
        wing_depth_m: footprint?.wing_depth_m,
        within_recommended_size: footprint?.within_recommended_size ?? true,
      },
      offset: centroid
        ? [
            (centroid[0] - lng0) * metresPerDegLng,
            -(centroid[1] - lat0) * METRES_PER_DEG_LAT,
          ] as [number, number]
        : null,
      // Deleting a generated Building leaves the planning polygon available
      // for another design.  A historical compile marker alone must not make
      // the builder think the now-unlinked model is still placed.
      placeState: communityMeta?.generator === 'lego_assembly' && Boolean(zone.building_id)
        ? 'placed' as const
        : undefined,
      massingState: communityMeta?.generator === 'planned_massing' ? 'compiled' as const : undefined,
    };
  });
}

export interface CommunityCompileProgress {
  completed: number;
  total: number;
}

export interface MixedCommunityCompileSummary {
  response: Community3DCompileResponse;
  detailedBuildings: number;
  plannedMasses: number;
  parks: number;
  streets: number;
}

function responseStatus(error: unknown): number | undefined {
  return (error as { response?: { status?: number } } | undefined)?.response?.status;
}

function isExplicitlyMissingFamily(error: unknown, archetypeId: string | undefined): boolean {
  if (!archetypeId || responseStatus(error) !== 422) return false;
  const response = (error as {
    response?: {
      data?: { detail?: unknown };
      headers?: Record<string, unknown>;
    };
  } | undefined)?.response;
  const errorCode = response?.headers?.['x-city-prompt-error-code'];
  if (errorCode === 'MODULE_FAMILY_MISSING') return true;
  const detail = response?.data?.detail;
  return typeof detail === 'string'
    && detail.includes(`No module family explicitly matches archetype '${archetypeId}'`);
}

function planRequestForItem(item: ZoneBuildItem) {
  return legoAssemblyApi.plan({
    target_width_m: item.targets.width_m,
    target_depth_m: item.targets.depth_m,
    target_floors: item.targets.floors,
    footprint_profile: item.targets.footprint_profile,
    wing_depth_m: item.targets.wing_depth_m,
    ...legoArchetypeContextFromZone(item.zone.properties),
  });
}

/** Plan every supported modular family and persist the entire mixed community
 * atomically. A missing family (422) is expected and compiles as honest exact-
 * footprint planned massing. Any other planning failure aborts before the
 * transaction, avoiding a partially downgraded or partially saved scene. */
export async function compileMixedCommunity3D(
  zones: SiteZone[],
  onProgress?: (progress: CommunityCompileProgress) => void,
): Promise<MixedCommunityCompileSummary> {
  const buildingItems = deriveItems(zones);
  const invalidBuildings = buildingItems.filter((item) => item.offset === null);
  if (invalidBuildings.length > 0) {
    throw new Error(
      `${invalidBuildings.length} building zone${invalidBuildings.length === 1 ? '' : 's'} `
      + 'have no usable map footprint. Repair the plan before generating 3D.',
    );
  }

  let completed = 0;
  onProgress?.({ completed, total: buildingItems.length });
  const markCompleted = (amount = 1) => {
    completed += amount;
    onProgress?.({ completed, total: buildingItems.length });
  };

  // Probe each exact archetype once before planning every footprint. A missing
  // imported family is independent of target dimensions, so one authoritative
  // 422 can safely classify the rest of that archetype as planned massing.
  // Fit-related 422s are deliberately NOT deduplicated: another footprint of
  // the same available family may still be compatible.
  const indicesByArchetype = new Map<string, number[]>();
  const ungroupedIndices: number[] = [];
  buildingItems.forEach((item, index) => {
    if (!item.archetypeId) {
      ungroupedIndices.push(index);
      return;
    }
    const indices = indicesByArchetype.get(item.archetypeId) ?? [];
    indices.push(index);
    indicesByArchetype.set(item.archetypeId, indices);
  });
  const probeIndices = [
    ...Array.from(indicesByArchetype.values(), (indices) => indices[0]),
    ...ungroupedIndices,
  ];
  const planResults = new Array<PromiseSettledResult<LegoAssemblyPlan>>(buildingItems.length);
  const probeResults = await allSettledWithConcurrency(
    probeIndices,
    async (itemIndex) => {
      try {
        return await planRequestForItem(buildingItems[itemIndex]);
      } finally {
        markCompleted();
      }
    },
    8,
  );
  probeIndices.forEach((itemIndex, resultIndex) => {
    planResults[itemIndex] = probeResults[resultIndex];
  });

  const remainingIndices: number[] = [];
  indicesByArchetype.forEach((indices, archetypeId) => {
    const [probeIndex, ...rest] = indices;
    const probe = planResults[probeIndex];
    if (
      probe?.status === 'rejected'
      && isExplicitlyMissingFamily(probe.reason, archetypeId)
    ) {
      rest.forEach((itemIndex) => {
        planResults[itemIndex] = { status: 'rejected', reason: probe.reason };
      });
      if (rest.length > 0) markCompleted(rest.length);
      return;
    }
    remainingIndices.push(...rest);
  });

  const remainingResults = await allSettledWithConcurrency(
    remainingIndices,
    async (itemIndex) => {
      try {
        return await planRequestForItem(buildingItems[itemIndex]);
      } finally {
        markCompleted();
      }
    },
    8,
  );
  remainingIndices.forEach((itemIndex, resultIndex) => {
    planResults[itemIndex] = remainingResults[resultIndex];
  });

  const unexpectedFailure = planResults.find(
    (result) => result.status === 'rejected' && responseStatus(result.reason) !== 422,
  );
  if (unexpectedFailure?.status === 'rejected') {
    throw new Error(getApiErrorMessage(
      unexpectedFailure.reason,
      'Could not prepare the modular community. Nothing was saved.',
    ));
  }

  const compileItems = buildingItems.map((item, index) => {
    const result = planResults[index];
    return result?.status === 'fulfilled'
      ? {
          zone_id: item.zone.id,
          source_updated_at: item.zone.updated_at,
          recipe: recipeFromPlan({ ...item, plan: result.value }),
        }
      : { zone_id: item.zone.id, source_updated_at: item.zone.updated_at };
  });
  const groundItems = deriveGroundItems(zones);
  compileItems.push(...groundItems.map((item) => ({
    zone_id: item.zone.id,
    source_updated_at: item.zone.updated_at,
  })));
  if (compileItems.length === 0) {
    throw new Error('This plan has no building, park, or street zones to generate.');
  }

  const response = await legoAssemblyApi.compileCommunity(compileItems);
  return {
    response,
    detailedBuildings: response.items.filter((item) => (
      item.generator === 'lego_assembly' || item.generator === 'meshy'
    )).length,
    plannedMasses: response.items.filter((item) => item.generator === 'planned_massing').length,
    parks: response.counts.park,
    streets: response.counts.street,
  };
}
