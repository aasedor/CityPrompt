import { expect, it } from 'vitest';
import type { UserGeneratedBuilding } from '@/services/api';
import { generatedPlacementDraft, placementDraftProperties } from './generatedPlacement';
import { placeAsset, placementProperties } from './catalogue';

const model: UserGeneratedBuilding = {
  id: 'my-house', project_id: 'original', name: 'My house', preview_url: null,
  model_url: '/api/v1/files/projects/original/models/my-house.glb',
  floor_count: 2, height_meters: 7.5, width_m: 12, depth_m: 16, size_estimated: false,
};

it('starts a saved model in click-to-place mode at its original plot size', () => {
  const draft = generatedPlacementDraft(model);
  expect(draft).toMatchObject({ assetId: 'user-generated:my-house', generatedModel: model,
    width: 12, depth: 16, degrees: 0, faceStreet: true });
  expect(placementDraftProperties(draft, 1042)).toMatchObject({
    user_generated_source_id: 'my-house', native_plot_axes: true,
    height: 7.5, floor_count: 2, floors: 2, terrain_elevation_m: 1042,
  });
  expect(placementDraftProperties(draft)).not.toHaveProperty('model_url');
});

it('keeps catalogue placement properties unchanged', () => {
  const asset = placeAsset('infill_home');
  const draft = { assetId: asset.id, width: asset.width, depth: asset.depth, degrees: 0 };
  expect(placementDraftProperties(draft, 1042)).toEqual(placementProperties(asset, 1042));
});
