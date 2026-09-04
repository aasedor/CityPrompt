import { api } from '@/services/api';
import type { SiteZoneProperties } from '@/types';

export type LegoModuleRole = 'podium' | 'floor' | 'setback' | 'crown' | 'roof' | 'attachment' | 'assembled';
export type LegoFootprintProfile = 'rectangle' | 'l_shape' | 'u_shape' | 'courtyard';

export interface LegoModule {
  id: string;
  name: string;
  model_url: string;
  family: string;
  role: LegoModuleRole;
  width_m: number;
  depth_m: number;
  height_m: number;
  archetype_ids: string[];
  reuse_keys: string[];
  min_floors?: number | null;
  max_floors?: number | null;
  repeatable_z: boolean;
  variant_key?: string;
  lod?: number;
  allowed_levels?: number[];
}

export interface LegoAssemblyInstance {
  asset_id: string;
  asset_name: string;
  model_url: string;
  family: string;
  role: LegoModuleRole;
  variant_key?: string;
  lod?: number;
  level: number;
  segment_id?: string;
  position: [number, number, number];
  rotation_degrees: number;
  scale: [number, number, number];
  native_dimensions_m: [number, number, number];
}

export interface LegoAssemblyPlan {
  version: number;
  family: string;
  /** Current executable inventory revision returned by project-scoped plans. */
  catalog_fingerprint?: string | null;
  archetype_id?: string | null;
  reuse_keys: string[];
  target: {
    width_m: number;
    depth_m: number;
    floors: number;
    footprint_profile?: LegoFootprintProfile;
    wing_depth_m?: number;
  };
  assembled_height_m: number;
  instances: LegoAssemblyInstance[];
  fit: {
    placement_mode?: 'detached_lots';
    dwelling_count?: number;
    scale_x: number;
    scale_y: number;
    /** Raw parcel-envelope ratios before archetype-preserving containment. */
    envelope_scale_x?: number;
    envelope_scale_y?: number;
    score: number;
    profile?: LegoFootprintProfile;
    segment_count?: number;
    assembly_mode?: 'fixed_landmark';
    compatibility_source?: string;
    /** The authored form is uniformly scaled and centred inside the polygon. */
    footprint_mode?: 'archetype_contain' | 'envelope_fill';
  };
  footprint_segments?: Array<{
    id: string;
    centre_x_m: number;
    centre_y_m: number;
    length_m: number;
    thickness_m: number;
    rotation_degrees: number;
  }>;
}

export interface LegoPlanRequest {
  target_width_m: number;
  target_depth_m: number;
  target_floors: number;
  footprint_local_m?: number[][];
  archetype_id?: string;
  reuse_keys?: string[];
  preferred_family?: string;
  /** Allow the planner to use setback modules (default true on the backend). */
  allow_setback?: boolean;
  /** Disable the legacy generic-family forced-fit escape hatch. Community 3D
   * and AI plans set this false so an out-of-contract family becomes honest
   * exact massing instead of distorted detail. */
  allow_forced_fit?: boolean;
  footprint_profile?: LegoFootprintProfile;
  wing_depth_m?: number;
  project_id?: string;
}

export type LegoPlanningFailureCode = 'family_not_found' | 'family_incompatible';

export interface LegoSupportedFamily {
  family: string;
  widths_m: number[];
  depths_m: number[];
  min_floors?: number | null;
  max_floors?: number | null;
}

export interface LegoPlanningFailure {
  code: LegoPlanningFailureCode;
  message: string;
  requested?: {
    width_m: number;
    depth_m: number;
    floors: number;
    footprint_profile?: LegoFootprintProfile;
  };
  supported_families?: LegoSupportedFamily[];
}

const LEGO_PLANNING_FAILURE_CODES = new Set<LegoPlanningFailureCode>([
  'family_not_found',
  'family_incompatible',
]);

/**
 * Decode the planner's semantic 422 payload. Legacy text/header recognition is
 * deliberately narrow so validation failures are never mislabeled as a
 * missing family during a rolling frontend/backend deployment.
 */
export function getLegoPlanningFailure(error: unknown): LegoPlanningFailure | null {
  const response = (error as {
    response?: {
      status?: number;
      data?: { detail?: unknown };
      headers?: Record<string, unknown>;
    };
  })?.response;
  if (response?.status !== 422) return null;

  const detail = response.data?.detail;
  if (detail && typeof detail === 'object' && !Array.isArray(detail)) {
    const record = detail as Record<string, unknown>;
    const code = record.code;
    const message = record.message;
    if (
      typeof code === 'string'
      && LEGO_PLANNING_FAILURE_CODES.has(code as LegoPlanningFailureCode)
      && typeof message === 'string'
      && message.trim()
    ) {
      return {
        ...(record as unknown as LegoPlanningFailure),
        code: code as LegoPlanningFailureCode,
        message: message.trim(),
      };
    }
  }

  const legacyHeader = response.headers?.['x-city-prompt-error-code'];
  const legacyMessage = typeof detail === 'string' ? detail.trim() : '';
  if (
    legacyHeader === 'MODULE_FAMILY_MISSING'
    || /^No module family (?:explicitly matches|covers) archetype\b/i.test(legacyMessage)
  ) {
    return {
      code: 'family_not_found',
      message: legacyMessage || 'No module family covers this archetype.',
    };
  }
  if (/^No compatible module family\b/i.test(legacyMessage)) {
    return { code: 'family_incompatible', message: legacyMessage };
  }
  return null;
}

/**
 * Persisted assembly recipe attached to a generated building. Mirrors the
 * backend contract for /api/v1/lego-assembly/recipes/{building_id}.
 */
export interface LegoAssemblyRecipe {
  schema_version: 1;
  module_family: string;
  /** Executable catalogue revision stamped by the AI Master Planner. Manual
   * LEGO recipes intentionally omit it for backwards compatibility. */
  catalog_fingerprint?: string | null;
  archetype_id?: string | null;
  reuse_keys: string[];
  target: {
    width_m: number;
    depth_m: number;
    floors: number;
    footprint_profile?: LegoFootprintProfile;
    wing_depth_m?: number;
  };
  instances: LegoAssemblyInstance[];
  assembled_height_m?: number | null;
  fit?: LegoAssemblyPlan['fit'] | null;
  assembled_preview_url?: string | null;
}

export interface Community3DCompileResponse {
  status: 'compiled';
  compiled_at: string;
  counts: { building: number; park: number; street: number };
  /**
   * Additive compiler diagnostics for the optional site-boundary remainder.
   * Optional keeps older saved responses and test fixtures source-compatible.
   */
  residual_landscape?: {
    boundary_count: number;
    derived_boundary_count: number;
    area_sqm: number;
    placement_count: number;
  };
  items: Array<{
    zone_id: string;
    kind: 'building' | 'park' | 'street';
    building_id: string | null;
    building_created: boolean;
    generator: 'lego_assembly' | 'planned_massing' | 'meshy' | 'park_kit' | 'street_section';
  }>;
}

/**
 * Pull the exact archetype identity and reuse keys already produced by the
 * Urban Intelligence DNA / aesthetic-catalog workflow. This avoids creating a
 * second style taxonomy for modular buildings.
 */
export function legoArchetypeContextFromZone(
  properties: SiteZoneProperties | undefined,
): Pick<LegoPlanRequest, 'archetype_id' | 'reuse_keys' | 'allow_setback'> {
  if (!properties) return {};

  const generationInput = properties.generation_style_input as
    | {
        archetypeId?: string;
        generationTags?: string[];
        styleProfile?: { massing?: string };
        downstreamHints?: { reuseKeys?: string[]; allowSetback?: boolean };
      }
    | undefined;

  // A selected design variant is the most specific architectural identity.
  // The generation input can still contain the parent card's default visual
  // reference (for example `*_variant_0`), which must not replace a user's
  // explicit Contemporary Addition / Gothic / corner choice.
  const archetypeId = (properties.development_selected_variant_id as string | undefined)
    || (properties.development_archetype_id as string | undefined)
    || generationInput?.archetypeId
    || (properties.development_subcategory as string | undefined);

  const reuseKeys = generationInput?.downstreamHints?.reuseKeys;
  const massingText = String(generationInput?.styleProfile?.massing || '').toLowerCase();
  const generationTags = generationInput?.generationTags || [];
  const inferredSetback = generationTags.some((tag) => String(tag).toLowerCase().includes('setback'))
    || /\b(setback|stepped tower|tower on podium)\b/.test(massingText);
  // Setbacks are opt-in design grammar. Importing a setback module does not
  // authorize the planner to insert it into every five-storey family.
  const allowSetback = typeof generationInput?.downstreamHints?.allowSetback === 'boolean'
    ? generationInput.downstreamHints.allowSetback
    : inferredSetback;

  return {
    archetype_id: archetypeId,
    allow_setback: allowSetback,
    reuse_keys: Array.isArray(reuseKeys)
      ? reuseKeys.filter((value): value is string => typeof value === 'string' && value.length > 0)
      : [
      properties.development_subcategory,
      properties.development_aesthetic_category,
      properties.development_selected_variant_id,
      properties.development_archetype_id,
        ].filter((value): value is string => typeof value === 'string' && value.length > 0),
  };
}

export const legoAssemblyApi = {
  async listModules(): Promise<LegoModule[]> {
    const response = await api.get<{ modules: LegoModule[] }>('/api/v1/lego-assembly/modules');
    return response.data.modules;
  },

  async plan(request: LegoPlanRequest): Promise<LegoAssemblyPlan> {
    const response = await api.post<LegoAssemblyPlan>('/api/v1/lego-assembly/plan', request);
    return response.data;
  },

  async saveRecipe(buildingId: string, recipe: LegoAssemblyRecipe): Promise<LegoAssemblyRecipe> {
    const response = await api.post<{ status: string; building_id: string; legoAssembly: LegoAssemblyRecipe }>(
      `/api/v1/lego-assembly/recipes/${buildingId}`,
      recipe,
    );
    return response.data.legoAssembly;
  },

  /**
   * Place a recipe on a zone: the backend ensures the zone has a linked
   * Building (creating one from the zone polygon when generate-all never ran),
   * saves the recipe on it, and the globe swaps the polygon for the stack once
   * the project query refetches.
   */
  async place(
    zoneId: string,
    recipe: LegoAssemblyRecipe & {
      building_name?: string | null;
      /** Optimistic-concurrency snapshot used to plan this placement. */
      source_updated_at?: string;
    },
  ): Promise<{ building_id: string; building_created: boolean }> {
    const response = await api.post<{
      status: string;
      zone_id: string;
      building_id: string;
      building_created: boolean;
      legoAssembly: LegoAssemblyRecipe;
    }>(`/api/v1/lego-assembly/place/${zoneId}`, recipe);
    return response.data;
  },

  /** Persist a mixed building/park/street build as one backend transaction. */
  async compileCommunity(
    items: Array<{
      zone_id: string;
      /** Revision of the zone snapshot used to plan this exact item. */
      source_updated_at: string;
      recipe?: LegoAssemblyRecipe & { building_name?: string | null };
    }>,
    scopeZoneIds?: string[],
    scopeBoundaryId?: string,
  ): Promise<Community3DCompileResponse> {
    const response = await api.post<Community3DCompileResponse>(
      '/api/v1/lego-assembly/place-community',
      {
        items,
        ...(scopeZoneIds !== undefined ? { scope_zone_ids: scopeZoneIds } : {}),
        ...(scopeBoundaryId !== undefined ? { scope_boundary_id: scopeBoundaryId } : {}),
      },
    );
    return response.data;
  },

  async getRecipe(buildingId: string): Promise<LegoAssemblyRecipe | null> {
    const response = await api.get<{ legoAssembly: LegoAssemblyRecipe | null }>(
      `/api/v1/lego-assembly/recipes/${buildingId}`,
    );
    return response.data.legoAssembly;
  },

  async clearRecipe(buildingId: string): Promise<void> {
    await api.delete(`/api/v1/lego-assembly/recipes/${buildingId}`);
  },

  async configureModule(
    itemId: string,
    metadata: {
      role: LegoModuleRole;
      family: string;
      width_m: number;
      depth_m: number;
      height_m: number;
      repeatable_z?: boolean;
      archetype_ids?: string[];
      reuse_keys?: string[];
      min_floors?: number;
      max_floors?: number;
      variant_key?: string;
      lod?: number;
      allowed_levels?: number[];
    },
  ): Promise<void> {
    await api.put(`/api/v1/lego-assembly/modules/${itemId}`, metadata);
  },
};
