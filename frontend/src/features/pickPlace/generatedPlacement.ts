import type { SiteZoneProperties } from '@/types';
import type { UserGeneratedBuilding } from '@/services/api';
import { placeAsset, placementProperties } from './catalogue';
import type { PlacementDraft } from './GlobePlacementPreview';

export function generatedPlacementDraft(model: UserGeneratedBuilding): PlacementDraft {
  return {
    assetId: `user-generated:${model.id}`,
    generatedModel: model,
    width: model.width_m,
    depth: model.depth_m,
    degrees: 0,
    faceStreet: true,
  };
}

export function placementDraftProperties(draft: PlacementDraft, elevation?: number, coordinates?: number[][]): SiteZoneProperties {
  const model = draft.generatedModel;
  if (!model) return placementProperties(placeAsset(draft.assetId), elevation, coordinates);
  const floors = model.floor_count ?? 2;
  return {
    user_generated_source_id: model.id,
    native_plot_axes: true,
    community_3d_mask_existing_tiles: true,
    height: model.height_meters,
    floor_count: floors,
    floors,
    ...(Number.isFinite(elevation) ? { terrain_elevation_m: elevation } : {}),
  };
}
