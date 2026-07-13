import { api } from '@/services/api';
import type { SiteZoneProperties } from '@/types';

export type LegoModuleRole = 'podium' | 'floor' | 'setback' | 'roof' | 'attachment';

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
}

export interface LegoAssemblyInstance {
  asset_id: string;
  asset_name: string;
  model_url: string;
  family: string;
  role: LegoModuleRole;
  level: number;
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
  };
  assembled_height_m: number;
  instances: LegoAssemblyInstance[];
  fit: {
    scale_x: number;
    scale_y: number;
    score: number;
  };
}

export interface LegoPlanRequest {
  target_width_m: number;
  target_depth_m: number;
  target_floors: number;
  archetype_id?: string;
  reuse_keys?: string[];
  preferred_family?: string;
}

/**
 * Pull the exact archetype identity and reuse keys already produced by the
 * Urban Intelligence DNA / aesthetic-catalog workflow. This avoids creating a
 * second style taxonomy for modular buildings.
 */
export function legoArchetypeContextFromZone(
  properties: SiteZoneProperties | undefined,
): Pick<LegoPlanRequest, 'archetype_id' | 'reuse_keys'> {
  if (!properties) return {};

  const generationInput = properties.generation_style_input as
    | {
        archetypeId?: string;
        downstreamHints?: { reuseKeys?: string[] };
      }
    | undefined;

  const archetypeId = generationInput?.archetypeId
    || (properties.development_archetype_id as string | undefined)
    || (properties.development_subcategory as string | undefined);

  const reuseKeys = generationInput?.downstreamHints?.reuseKeys;

  return {
    archetype_id: archetypeId,
    reuse_keys: Array.isArray(reuseKeys)
      ? reuseKeys.filter((value): value is string => typeof value === 'string' && value.length > 0)
      : [
          properties.development_subcategory,
          properties.development_aesthetic_category,
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
    },
  ): Promise<void> {
    await api.put(`/api/v1/lego-assembly/modules/${itemId}`, metadata);
  },
};
