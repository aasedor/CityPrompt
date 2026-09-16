import type { SiteZone } from '@/types';
import { sampleSharedSiteGround, sharedGroundSignature, sharedSiteGroundContains,
  validateSharedSiteGroundPass, type SharedSiteGroundSnapshot, type SharedSiteGroundGrid } from '@/components/viewer/globe/sharedSiteGround';
import type { SharedSiteGroundState } from '@/components/viewer/globe/SharedSiteGroundProvider';

/** Saved, versioned measurements, independent of the visible context provider.
 * This bounded pilot is not an upload/import API or a survey certification. */
export interface SurveyGround {
  version: 1;
  dataset: 'USGS_CA_SanFrancisco_1_B23';
  verticalReference: 'WGS84_ellipsoid';
  grid: SharedSiteGroundGrid;
  heights: number[];
  provenance: {
    sourceVertical: 'NAVD88_GEOID18'; classification: 2;
    method: 'ground-idw8'; maximumSupportDistanceM: number;
    geoidHeightM: number; datumOperation: 'EPSG:9774'; coordinateAccuracyM: 2;
    sourceSha256: string;
  };
}

export function readSurveyGround(value: unknown): SurveyGround | null {
  if (!value || typeof value !== 'object') return null;
  const v = value as SurveyGround, g = v.grid, p = v.provenance;
  if (v.version !== 1 || v.dataset !== 'USGS_CA_SanFrancisco_1_B23' || v.verticalReference !== 'WGS84_ellipsoid'
    || !g || !p || !Array.isArray(v.heights) || v.heights.length > 1200
    || !Number.isInteger(g.columns) || !Number.isInteger(g.rows) || g.columns < 2 || g.rows < 2
    || g.columns * g.rows !== v.heights.length || ![g.west, g.south, g.stepLng, g.stepLat].every(Number.isFinite)
    || g.stepLng <= 0 || g.stepLat <= 0 || g.stepLng > .001 || g.stepLat > .001
    || g.west < -122.52 || g.west + (g.columns - 1) * g.stepLng > -122.32
    || g.south < 37.69 || g.south + (g.rows - 1) * g.stepLat > 37.84
    || v.heights.some(h => !Number.isFinite(h) || h < -100 || h > 600)
    || p.sourceVertical !== 'NAVD88_GEOID18' || p.classification !== 2 || p.method !== 'ground-idw8'
    || !Number.isFinite(p.maximumSupportDistanceM) || p.maximumSupportDistanceM <= 0 || p.maximumSupportDistanceM > 3
    || !Number.isFinite(p.geoidHeightM) || p.geoidHeightM < -34 || p.geoidHeightM > -31
    || p.datumOperation !== 'EPSG:9774' || p.coordinateAccuracyM !== 2
    || typeof p.sourceSha256 !== 'string' || !/^[a-f0-9]{64}$/.test(p.sourceSha256)) return null;
  return v;
}

/** A missing/invalid saved survey must not silently re-ground to photogrammetry. */
export function surveyGroundState(boundary: SiteZone | null | undefined): SharedSiteGroundState | null {
  if (!boundary || boundary.properties?.survey_ground === undefined) return null;
  const ring = boundary.coordinates.map(([lng, lat]): [number, number] => [lng, lat]);
  const contains = (lng: number, lat: number) => sharedSiteGroundContains(ring, lng, lat);
  const unavailable: SharedSiteGroundState = { status: 'unavailable', snapshot: null, contains,
    heightAt: () => null, revision: 'survey-unavailable', failureReason: 'survey_invalid' };
  const data = readSurveyGround(boundary.properties.survey_ground);
  if (!data || ring.length < 3 || ring.length > 2048 || boundary.properties.community_3d_mask_existing_tiles !== false
    || boundary.properties.terrain_strategy === 'landscape') return unavailable;
  const g = data.grid;
  if (ring.some(([lng, lat]) => !Number.isFinite(lng) || !Number.isFinite(lat)
    || lng < g.west - 1e-10 || lng > g.west + (g.columns - 1) * g.stepLng + 1e-10
    || lat < g.south - 1e-10 || lat > g.south + (g.rows - 1) * g.stepLat + 1e-10)) return unavailable;
  const sourceSignature = sharedGroundSignature([boundary.id, ring, data]);
  const layout = { boundaryId: boundary.id, boundaryUpdatedAt: boundary.updated_at,
    boundaryCoordinates: ring, sourceSignature, grid: g };
  const quality = validateSharedSiteGroundPass(layout, data.heights);
  if (!quality.valid) return unavailable;
  const snapshot: SharedSiteGroundSnapshot = { ...layout, version: 1, source: 'classified_lidar',
    verticalReference: data.verticalReference, heights: data.heights, signature: sourceSignature,
    quality: { sampleCount: data.heights.length, stablePasses: 0, maxPassDeltaM: 0,
      maxSlope: quality.maxSlope, maxLocalResidualM: quality.maxLocalResidualM } };
  return { status: 'ready', snapshot, contains, heightAt: (lng, lat) => sampleSharedSiteGround(snapshot, lng, lat), revision: sourceSignature };
}
