import type { SiteZone } from '@/types';
import type { SurveyGround } from './surveyGround';

export const surveyFixture: SurveyGround = {
  version: 1, dataset: 'USGS_CA_SanFrancisco_1_B23', verticalReference: 'WGS84_ellipsoid',
  grid: { west: -122.427, south: 37.759, columns: 3, rows: 3, stepLng: .0001, stepLat: .0001 },
  heights: [-4, -3, -2, -3, -2, -1, -2, -1, 0],
  provenance: { sourceVertical: 'NAVD88_GEOID18', classification: 2, method: 'ground-idw8', maximumSupportDistanceM: 1.5,
    geoidHeightM: -32.556, datumOperation: 'EPSG:9774', coordinateAccuracyM: 2, sourceSha256: 'a'.repeat(64) },
};
export const surveySite = (data: unknown = surveyFixture): SiteZone => ({ id: 'survey-site', project_id: 'survey-project', zone_type: 'site_boundary',
  coordinates: [[-122.427, 37.759], [-122.4268, 37.759], [-122.4268, 37.7592], [-122.427, 37.7592]],
  properties: { community_3d_mask_existing_tiles: false, survey_ground: data }, is_active_boundary: true,
  color: '#fff', created_at: 'before', updated_at: 'before', sort_order: 0 });
