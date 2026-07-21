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
    scale_x: number;
    scale_y: number;
    score: number;
    profile?: LegoFootprintProfile;
    segment_count?: number;
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
  archetype_id?: string;
  reuse_keys?: string[];
  preferred_family?: string;
  /** Allow the planner to use setback modules (default true on the backend). */
  allow_setback?: boolean;
  footprint_profile?: LegoFootprintProfile;
  wing_depth_m?: number;
}

/**
 * Persisted assembly recipe attached to a generated building. Mirrors the
 * backend contract for /api/v1/lego-assembly/recipes/{building_id}.
 */
export interface LegoAssemblyRecipe {
  schema_version: 1;
  module_family: string;
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
   * Additive compiler diagnostics for the generated site-boundary remainder.
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
    || generationInput?.archetypeId
    || (properties.development_archetype_id as string | undefined)
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
    recipe: LegoAssemblyRecipe & { building_name?: string | null },
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
  async compileCommunity(items: Array<{
    zone_id: string;
    /** Revision of the zone snapshot used to plan this exact item. */
    source_updated_at: string;
    recipe?: LegoAssemblyRecipe & { building_name?: string | null };
  }>): Promise<Community3DCompileResponse> {
    const response = await api.post<Community3DCompileResponse>(
      '/api/v1/lego-assembly/place-community',
      { items },
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
